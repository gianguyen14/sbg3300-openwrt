// SPDX-License-Identifier: GPL-2.0-only
/* Original Linux DMA adapter; no vendor compatibility headers or NBuff shims. */
#include <linux/dma-mapping.h>
#include <linux/err.h>
#include <linux/iopoll.h>
#include <linux/module.h>
#include <linux/mutex.h>
#include <linux/slab.h>
#include <linux/spinlock.h>
#include "xtm_dma.h"

/* Exact-family register interface, not absolute register addresses. */
#define XTM_CH_CFG 0x00
#define XTM_CH_IRQ_STATUS 0x04
#define XTM_CH_IRQ_MASK 0x08
#define XTM_CH_BURST 0x0c
#define XTM_CH_ENABLE 0x01
#define XTM_CH_PACKET_HALT 0x02
#define XTM_CH_DONE_MASK 0x07
#define XTM_CH_MAX_BURST 8
#define XTM_STATE_BASE 0x00

struct xtm_hw_desc {
	__be32 control;
	__be32 address;
};

struct xtm_slot {
	void *buffer;
	dma_addr_t dma;
	u32 capacity;
};

struct xtm_dma_ring {
	struct device *dev;
	struct xtm_hw_desc *descs;
	dma_addr_t desc_dma;
	struct xtm_slot *slots;
	struct xtm_queue queue;
	struct xtm_dma_stats stats;
	spinlock_t lock;
	struct mutex lifecycle;
	void __iomem *channel;
	void __iomem *state;
	bool running;
	bool stopping;
};

static enum dma_data_direction xtm_dma_direction(const struct xtm_dma_ring *r)
{
	return r->queue.direction == XTM_RX ? DMA_FROM_DEVICE : DMA_TO_DEVICE;
}

struct xtm_dma_ring *xtm_dma_alloc(struct device *dev, enum xtm_direction dir,
				 unsigned int count, gfp_t gfp)
{
	struct xtm_dma_ring *r;
	int ret;

	static_assert(sizeof(struct xtm_hw_desc) == 8);
	static_assert(offsetof(struct xtm_hw_desc, address) == 4);
	if (!dev || !dev->dma_mask || !*dev->dma_mask ||
	    dma_get_mask(dev) > DMA_BIT_MASK(32) ||
	    !dev->coherent_dma_mask || dev->coherent_dma_mask > DMA_BIT_MASK(32))
		return ERR_PTR(-EINVAL);
	r = kzalloc(sizeof(*r), gfp);
	if (!r)
		return ERR_PTR(-ENOMEM);
	ret = xtm_queue_init(&r->queue, count, dir);
	if (ret)
		goto free_ring;
	r->slots = kcalloc(count, sizeof(*r->slots), gfp);
	if (!r->slots) {
		ret = -ENOMEM;
		goto free_ring;
	}
	r->descs = dma_alloc_coherent(dev, count * sizeof(*r->descs),
				     &r->desc_dma, gfp);
	if (!r->descs) {
		ret = -ENOMEM;
		goto free_slots;
	}
	/* A 32-bit descriptor cannot represent a wider DMA address. */
	if (upper_32_bits(r->desc_dma) || !IS_ALIGNED(r->desc_dma, 16) ||
	    (u64)r->desc_dma + count * sizeof(*r->descs) - 1 > U32_MAX) {
		ret = -ERANGE;
		goto free_descs;
	}
	memset(r->descs, 0, count * sizeof(*r->descs));
	r->dev = get_device(dev);
	spin_lock_init(&r->lock);
	mutex_init(&r->lifecycle);
	return r;
free_descs:
	dma_free_coherent(dev, count * sizeof(*r->descs), r->descs, r->desc_dma);
free_slots:
	kfree(r->slots);
free_ring:
	kfree(r);
	return ERR_PTR(ret);
}
EXPORT_SYMBOL_GPL(xtm_dma_alloc);

int xtm_dma_bind(struct xtm_dma_ring *r, void __iomem *channel,
		 void __iomem *state)
{
	int ret = 0;

	if (!r || !channel || !state)
		return -EINVAL;
	mutex_lock(&r->lifecycle);
	if (r->channel || (ioread32be(channel + XTM_CH_CFG) & XTM_CH_ENABLE)) {
		ret = -EBUSY;
		goto out;
	}
	/* No IRQ is enabled here. The future platform driver must own IRQ/NAPI. */
	iowrite32be(0, channel + XTM_CH_CFG);
	iowrite32be(0, channel + XTM_CH_IRQ_MASK);
	iowrite32be(XTM_CH_DONE_MASK, channel + XTM_CH_IRQ_STATUS);
	iowrite32be(XTM_CH_MAX_BURST, channel + XTM_CH_BURST);
	iowrite32be(0, state + 4);
	iowrite32be(0, state + 8);
	iowrite32be(0, state + 12);
	iowrite32be(lower_32_bits(r->desc_dma), state + XTM_STATE_BASE);
	ioread32be(state + XTM_STATE_BASE); /* flush posted register writes */
	r->channel = channel;
	r->state = state;
out:
	mutex_unlock(&r->lifecycle);
	return ret;
}
EXPORT_SYMBOL_GPL(xtm_dma_bind);

int xtm_dma_start(struct xtm_dma_ring *r)
{
	unsigned long flags;
	int ret = 0;

	if (!r)
		return -EINVAL;
	mutex_lock(&r->lifecycle);
	spin_lock_irqsave(&r->lock, flags);
	if (!r->channel)
		ret = -ENODEV;
	else if (r->stopping)
		ret = -ESHUTDOWN;
	else if (r->running || (ioread32be(r->channel) & XTM_CH_ENABLE))
		ret = -EBUSY;
	else if (!r->queue.pending)
		ret = -ENODATA;
	else {
		dma_wmb();
		iowrite32be(XTM_CH_ENABLE, r->channel + XTM_CH_CFG);
		ioread32be(r->channel + XTM_CH_CFG);
		r->running = true;
	}
	spin_unlock_irqrestore(&r->lock, flags);
	mutex_unlock(&r->lifecycle);
	return ret;
}
EXPORT_SYMBOL_GPL(xtm_dma_start);

int xtm_dma_stop(struct xtm_dma_ring *r)
{
	u32 cfg;
	unsigned long flags;
	int ret = 0;

	if (!r)
		return -EINVAL;
	mutex_lock(&r->lifecycle);
	spin_lock_irqsave(&r->lock, flags);
	r->stopping = true;
	spin_unlock_irqrestore(&r->lock, flags);
	if (r->channel) {
		/* TX halts at a packet boundary; RX asks the channel to disable. */
		iowrite32be(r->queue.direction == XTM_TX ? XTM_CH_PACKET_HALT : 0,
			    r->channel + XTM_CH_CFG);
		ret = read_poll_timeout(ioread32be, cfg, !(cfg & XTM_CH_ENABLE),
					20, 200000, false, r->channel + XTM_CH_CFG);
	}
	spin_lock_irqsave(&r->lock, flags);
	if (ret)
		r->stats.stop_timeouts++;
	else
		r->running = false;
	spin_unlock_irqrestore(&r->lock, flags);
	mutex_unlock(&r->lifecycle);
	return ret;
}
EXPORT_SYMBOL_GPL(xtm_dma_stop);

static int xtm_dma_post(struct xtm_dma_ring *r, const void *data,
			unsigned int capacity, u16 fstat, gfp_t gfp)
{
	struct xtm_slot slot;
	unsigned long flags;
	u32 index, word;
	int ret;

	if (!capacity || capacity > XTM_DESC_MAX_LENGTH ||
	    (fstat & ~XTM_DESC_FSTAT))
		return -EINVAL;
	/* Keep the complete streaming buffer on private cache lines. */
	slot.buffer = kmalloc(ALIGN(capacity, dma_get_cache_alignment()), gfp);
	if (!slot.buffer) {
		spin_lock_irqsave(&r->lock, flags);
		r->stats.allocation_errors++;
		spin_unlock_irqrestore(&r->lock, flags);
		return -ENOMEM;
	}
	if (data)
		memcpy(slot.buffer, data, capacity);
	slot.capacity = capacity;
	slot.dma = dma_map_single(r->dev, slot.buffer, capacity,
				  xtm_dma_direction(r));
	if (dma_mapping_error(r->dev, slot.dma)) {
		ret = -EIO;
		goto mapping_error;
	}
	if (upper_32_bits(slot.dma) || (u64)slot.dma + capacity - 1 > U32_MAX) {
		ret = -ERANGE;
		goto unmap_error;
	}
	spin_lock_irqsave(&r->lock, flags);
	if (r->stopping)
		ret = -ESHUTDOWN;
	else
		ret = xtm_queue_post(&r->queue, capacity, fstat, &index, &word);
	if (ret) {
		if (ret == -ENOSPC)
			r->stats.ring_full++;
		spin_unlock_irqrestore(&r->lock, flags);
		goto unmap;
	}
	r->slots[index] = slot;
	WRITE_ONCE(r->descs[index].address, cpu_to_be32(lower_32_bits(slot.dma)));
	/* Packet map/cache maintenance and address precede publishing OWN. */
	dma_wmb();
	WRITE_ONCE(r->descs[index].control, cpu_to_be32(word));
	/* Hardware may idle on an unowned descriptor: restart only if active. */
	if (r->running) {
		dma_wmb();
		iowrite32be(XTM_CH_ENABLE, r->channel + XTM_CH_CFG);
	}
	spin_unlock_irqrestore(&r->lock, flags);
	return 0;
unmap_error:
	dma_unmap_single(r->dev, slot.dma, capacity, xtm_dma_direction(r));
mapping_error:
	spin_lock_irqsave(&r->lock, flags);
	r->stats.mapping_errors++;
	spin_unlock_irqrestore(&r->lock, flags);
	kfree(slot.buffer);
	return ret;
unmap:
	dma_unmap_single(r->dev, slot.dma, capacity, xtm_dma_direction(r));
	kfree(slot.buffer);
	return ret;
}

int xtm_dma_tx_submit(struct xtm_dma_ring *r, const void *data, unsigned int len,
		      u16 fstat, gfp_t gfp)
{
	if (!r || !data || r->queue.direction != XTM_TX)
		return -EINVAL;
	return xtm_dma_post(r, data, len, fstat, gfp);
}
EXPORT_SYMBOL_GPL(xtm_dma_tx_submit);

int xtm_dma_rx_post(struct xtm_dma_ring *r, unsigned int capacity, gfp_t gfp)
{
	if (!r || r->queue.direction != XTM_RX)
		return -EINVAL;
	return xtm_dma_post(r, NULL, capacity, 0, gfp);
}
EXPORT_SYMBOL_GPL(xtm_dma_rx_post);

int xtm_dma_poll(struct xtm_dma_ring *r, struct xtm_dma_packet *packet)
{
	struct xtm_completion completion;
	struct xtm_slot slot;
	unsigned long flags;
	u32 index, word;
	int ret;

	if (!r || !packet)
		return -EINVAL;
	memset(packet, 0, sizeof(*packet));
	spin_lock_irqsave(&r->lock, flags);
	if (!r->queue.pending) {
		spin_unlock_irqrestore(&r->lock, flags);
		return 0;
	}
	index = r->queue.head;
	word = be32_to_cpu(READ_ONCE(r->descs[index].control));
	if (word & XTM_DESC_OWN) {
		spin_unlock_irqrestore(&r->lock, flags);
		return 0;
	}
	/* Observe device completion before reading its other writes. */
	dma_rmb();
	slot = r->slots[index];
	ret = xtm_queue_complete(&r->queue, word, slot.capacity, &completion);
	memset(&r->slots[index], 0, sizeof(r->slots[index]));
	WRITE_ONCE(r->descs[index].control, cpu_to_be32(0));
	dma_unmap_single(r->dev, slot.dma, slot.capacity, xtm_dma_direction(r));
	packet->data = slot.buffer;
	packet->length = ret ? 0 : completion.length;
	packet->status = completion.status;
	packet->error = ret;
	if (ret)
		r->stats.completion_errors++;
	else {
		r->stats.packets++;
		r->stats.bytes += completion.length;
	}
	spin_unlock_irqrestore(&r->lock, flags);
	return 1;
}
EXPORT_SYMBOL_GPL(xtm_dma_poll);

void xtm_dma_packet_free(struct xtm_dma_packet *packet)
{
	if (packet) {
		kfree(packet->data);
		memset(packet, 0, sizeof(*packet));
	}
}
EXPORT_SYMBOL_GPL(xtm_dma_packet_free);

void xtm_dma_get_stats(struct xtm_dma_ring *r, struct xtm_dma_stats *stats)
{
	unsigned long flags;

	if (!r || !stats)
		return;
	spin_lock_irqsave(&r->lock, flags);
	*stats = r->stats;
	spin_unlock_irqrestore(&r->lock, flags);
}
EXPORT_SYMBOL_GPL(xtm_dma_get_stats);

int xtm_dma_destroy(struct xtm_dma_ring *r, struct xtm_dma_stats *final_stats)
{
	u32 index;

	if (!r)
		return -EINVAL;
	/* Caller has already synchronized users/IRQ/NAPI; lifetime is exclusive. */
	mutex_lock(&r->lifecycle);
	if (r->running || (r->channel &&
	    (ioread32be(r->channel + XTM_CH_CFG) & XTM_CH_ENABLE))) {
		mutex_unlock(&r->lifecycle);
		return -EBUSY;
	}
	if (r->channel) {
		iowrite32be(0, r->channel + XTM_CH_IRQ_MASK);
		iowrite32be(0, r->state + XTM_STATE_BASE);
		ioread32be(r->state + XTM_STATE_BASE);
	}
	while (!xtm_queue_cancel(&r->queue, &index)) {
		struct xtm_slot *s = &r->slots[index];

		dma_unmap_single(r->dev, s->dma, s->capacity, xtm_dma_direction(r));
		kfree(s->buffer);
		r->stats.cancelled++;
	}
	if (final_stats)
		*final_stats = r->stats;
	dma_free_coherent(r->dev, r->queue.count * sizeof(*r->descs),
			  r->descs, r->desc_dma);
	kfree(r->slots);
	put_device(r->dev);
	mutex_unlock(&r->lifecycle);
	kfree(r);
	return 0;
}
EXPORT_SYMBOL_GPL(xtm_dma_destroy);

MODULE_LICENSE("GPL");
/* OpenWrt CONFIG_MODULE_STRIPPED removes MODULE_DESCRIPTION; retain metadata
 * explicitly so the external-module modpost check can verify it.
 */
MODULE_INFO(description, "SBG3300 BCM63168 XTM descriptor and DMA ring component");
