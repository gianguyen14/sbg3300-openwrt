/* SPDX-License-Identifier: GPL-2.0-or-later */
/* Tests execute extracted kernel callbacks. API doubles are CPU-only. */
#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef uint32_t u32;
struct list_head { int unused; };
struct device { int unused; };
struct platform_device { struct device dev; };
struct sk_buff {
	unsigned int len, protocol;
	unsigned char *data, *allocation;
	struct list_head list;
};
struct net_device_stats {
	unsigned int rx_errors, rx_length_errors, rx_dropped, rx_packets;
	unsigned int rx_bytes, tx_errors;
};
struct napi_struct { int unused; };
struct bcm6368_enetsw_desc;
struct bcm6368_enetsw {
	struct platform_device *pdev;
	struct net_device *net_dev;
	struct napi_struct napi;
	struct bcm6368_enetsw_desc *rx_desc_cpu, *tx_desc_cpu;
	unsigned char **rx_buf;
	struct sk_buff **tx_skb;
	int rx_desc_count, rx_curr_desc, rx_ring_size, rx_lock, rx_chan;
	int tx_desc_count, tx_dirty_desc, tx_ring_size, tx_lock, tx_chan;
	unsigned int copybreak, rx_buf_size, rx_frag_size;
};
struct net_device {
	struct bcm6368_enetsw *priv;
	struct net_device_stats stats;
};
#define NET_SKB_PAD 32
#define ETH_HLEN 14
#define ETH_FCS_LEN 4
#define ENETSW_FRAG_SIZE(n) (NET_SKB_PAD + (n) + 64)
#define DMA_FROM_DEVICE 0
#define DMA_TO_DEVICE 1
#define DMAC_IR_REG 4
#define DMAC_IRMASK_REG 8
#define DMAC_IR_PKTDONE_MASK 2
#define DMAC_CHANCFG_REG 0
#define DMAC_CHANCFG_EN_MASK 1
#define unlikely(x) (x)
#define netdev_priv(n) ((n)->priv)
#define container_of(p, type, member) ((type *)((char *)(p) - offsetof(type, member)))
#define READ_ONCE(x) (x)
#define INIT_LIST_HEAD(p) ((void)(p))

static struct sk_buff *pending[8];
static unsigned int queued, delivered, sync_cpu, sync_device, unmapped;
static unsigned int barriers, refills, completed, irq_enables, tx_completed;
static bool alloc_fails, build_fails, completion_allowed, overwrite_tx;
static struct bcm6368_enetsw *active;
#define list_for_each_entry(skb, head, member) \
	for (unsigned int at = 0; at < queued && (((skb) = pending[at]), 1); at++)
static void list_add_tail(struct list_head *item, struct list_head *head)
{
	(void)head;
	assert(queued < 8);
	pending[queued++] = container_of(item, struct sk_buff, list);
}
static void dma_rmb(void) { barriers++; }
#define rmb() dma_rmb()
static void spin_lock(int *lock) { (void)lock; }
static void spin_unlock(int *lock);
static unsigned char *napi_alloc_frag(unsigned int size)
{
	return alloc_fails ? NULL : calloc(1, size);
}
static void skb_free_frag(void *p) { free(p); }
static struct sk_buff *napi_build_skb(void *buf, unsigned int size)
{
	struct sk_buff *skb;
	(void)size;
	if (build_fails)
		return NULL;
	skb = calloc(1, sizeof(*skb));
	assert(skb);
	skb->data = skb->allocation = buf;
	return skb;
}
static void skb_reserve(struct sk_buff *skb, unsigned int size) { skb->data += size; }
static void skb_put(struct sk_buff *skb, unsigned int size)
{
	assert(size <= active->rx_buf_size - ETH_FCS_LEN);
	skb->len += size;
}
static unsigned int eth_type_trans(struct sk_buff *skb, struct net_device *ndev)
{
	(void)skb; (void)ndev;
	return 0;
}
static void netif_receive_skb_list(struct list_head *head)
{
	(void)head;
	for (unsigned int i = 0; i < queued; i++) {
		delivered++;
		free(pending[i]->allocation);
		free(pending[i]);
	}
	queued = 0;
}
static void dma_sync_single_for_cpu(struct device *dev, u32 addr, unsigned int len, int direction)
{
	(void)dev; (void)addr; (void)direction;
	assert(len <= active->rx_buf_size);
	sync_cpu++;
}
static void dma_sync_single_for_device(struct device *dev, u32 addr, unsigned int len, int direction)
{
	(void)dev; (void)addr; (void)direction;
	assert(len <= active->rx_buf_size);
	sync_device++;
}
static void dma_unmap_single(struct device *dev, u32 addr, unsigned int len, int direction)
{
	(void)dev; (void)addr; (void)len; (void)direction;
	unmapped++;
}
static int bcm6368_enetsw_refill_rx(struct net_device *ndev, bool napi_mode)
{
	(void)ndev; (void)napi_mode;
	refills++;
	return 0;
}
static void dmac_writel(struct bcm6368_enetsw *priv, u32 value, u32 reg, int chan)
{
	(void)priv; (void)chan;
	if (reg == DMAC_IRMASK_REG && value)
		irq_enables++;
}
static void netdev_completed_queue(struct net_device *ndev, unsigned int packets, unsigned int bytes)
{
	(void)ndev; (void)bytes;
	tx_completed += packets;
}
static void napi_consume_skb(struct sk_buff *skb, int budget)
{
	(void)budget;
	free(skb->allocation);
	free(skb);
}
static bool netif_queue_stopped(struct net_device *ndev) { (void)ndev; return false; }
static void netif_wake_queue(struct net_device *ndev) { (void)ndev; }
static bool napi_complete_done(struct napi_struct *napi, int work)
{
	(void)napi; (void)work;
	completed++;
	return completion_allowed;
}
#include "enetsw-rx-poll-under-test.inc"

static void spin_unlock(int *lock)
{
	if (overwrite_tx && lock == &active->tx_lock) {
		active->tx_desc_cpu[0].len_stat = 0;
		overwrite_tx = false;
	}
}

struct fixture {
	struct platform_device pdev;
	struct net_device ndev;
	struct bcm6368_enetsw priv;
	struct bcm6368_enetsw_desc rx[2], tx[1];
	unsigned char *buf[2];
	struct sk_buff *skb[1];
};
static void setup(struct fixture *f, unsigned int len)
{
	memset(f, 0, sizeof(*f));
	queued = delivered = sync_cpu = sync_device = unmapped = barriers = refills = 0;
	completed = irq_enables = tx_completed = 0;
	alloc_fails = build_fails = overwrite_tx = false;
	completion_allowed = true;
	active = &f->priv;
	f->ndev.priv = active;
	active->pdev = &f->pdev;
	active->net_dev = &f->ndev;
	active->rx_desc_cpu = f->rx;
	active->tx_desc_cpu = f->tx;
	active->rx_buf = f->buf;
	active->tx_skb = f->skb;
	active->rx_ring_size = 2;
	active->rx_desc_count = 1;
	active->tx_ring_size = active->tx_desc_count = 1;
	active->rx_buf_size = 1600;
	active->rx_frag_size = ENETSW_FRAG_SIZE(1600);
	active->copybreak = 128;
	f->buf[0] = calloc(1, active->rx_frag_size);
	assert(f->buf[0]);
	f->rx[0].len_stat = (len << DMADESC_LENGTH_SHIFT) | DMADESC_ESOP_MASK;
}
static void teardown(struct fixture *f)
{
	free(f->buf[0]);
	free(f->buf[1]);
}
int main(void)
{
	struct fixture f;
	/* Invalid lengths must not reach DMA synchronization or skb_put. */
	for (unsigned int len = 0; len < ETH_HLEN + ETH_FCS_LEN; len++) {
		setup(&f, len);
		assert(bcm6368_enetsw_receive_queue(&f.ndev, 1) == 1);
		assert(f.ndev.stats.rx_length_errors == 1 && f.ndev.stats.rx_errors == 1);
		assert(delivered == 0 && sync_cpu == 0 && unmapped == 0);
		teardown(&f);
	}
	for (unsigned int len = 1601; len <= 4095; len += 2494) {
		setup(&f, len);
		assert(bcm6368_enetsw_receive_queue(&f.ndev, 1) == 1);
		assert(f.ndev.stats.rx_length_errors == 1 && delivered == 0);
		teardown(&f);
	}
	setup(&f, 64);
	f.rx[0].len_stat |= DMADESC_CRC_MASK;
	assert(bcm6368_enetsw_receive_queue(&f.ndev, 1) == 1);
	assert(f.ndev.stats.rx_errors == 1 && delivered == 0);
	teardown(&f);
	/* Valid copybreak and zero-copy lifetimes. */
	for (unsigned int len = 18; len <= 1500; len += 1482) {
		setup(&f, len);
		assert(bcm6368_enetsw_receive_queue(&f.ndev, 1) == 1);
		assert(delivered == 1 && f.ndev.stats.rx_bytes == len - ETH_FCS_LEN);
		assert(barriers == 1 && f.priv.rx_curr_desc == 1);
		assert(unmapped == (len == 1500));
		teardown(&f);
	}
	setup(&f, 64);
	f.rx[0].len_stat |= DMADESC_OWNER_MASK;
	assert(bcm6368_enetsw_receive_queue(&f.ndev, 1) == 0 && barriers == 0);
	teardown(&f);
	setup(&f, 64);
	f.priv.rx_curr_desc = 1;
	f.buf[1] = f.buf[0]; f.buf[0] = NULL; f.rx[1] = f.rx[0];
	assert(bcm6368_enetsw_receive_queue(&f.ndev, 1) == 1);
	assert(f.priv.rx_curr_desc == 0);
	teardown(&f);
	setup(&f, 64);
	alloc_fails = true;
	assert(bcm6368_enetsw_receive_queue(&f.ndev, 1) == 1);
	assert(f.ndev.stats.rx_dropped == 1 && sync_cpu == 0 && f.buf[0]);
	teardown(&f);
	for (unsigned int len = 64; len <= 1500; len += 1436) {
		setup(&f, len); build_fails = true;
		assert(bcm6368_enetsw_receive_queue(&f.ndev, 1) == 1);
		assert(f.ndev.stats.rx_dropped == 1 && delivered == 0);
		assert((f.buf[0] == NULL) == (len == 1500));
		teardown(&f);
	}
	/* Empty RX ring must never dereference an unarmed descriptor. */
	setup(&f, 64);
	f.priv.rx_desc_count = 0; f.priv.rx_desc_cpu = NULL;
	assert(bcm6368_enetsw_receive_queue(&f.ndev, 64) == 0 && refills == 1);
	teardown(&f);
	/* budget=0 can reclaim TX but must not consume RX or complete NAPI. */
	setup(&f, 64);
	f.priv.tx_desc_count = 0;
	f.skb[0] = napi_build_skb(calloc(1, 64), 64); f.skb[0]->len = 64;
	assert(bcm6368_enetsw_poll(&f.priv.napi, 0) == 0);
	assert(tx_completed == 1 && delivered == 0 && completed == 0 && irq_enables == 0);
	teardown(&f);
	for (unsigned int allow = 0; allow < 2; allow++) {
		setup(&f, 64); f.rx[0].len_stat |= DMADESC_OWNER_MASK;
		completion_allowed = allow;
		assert(bcm6368_enetsw_poll(&f.priv.napi, 64) == 0);
		assert(completed == 1 && irq_enables == (allow ? 2U : 0U));
		teardown(&f);
	}
	setup(&f, 64);
	assert(bcm6368_enetsw_poll(&f.priv.napi, 1) == 1);
	assert(completed == 0 && irq_enables == 0);
	teardown(&f);
	/* Simulate xmit reusing status immediately after reclaim unlocks. */
	setup(&f, 64);
	f.priv.tx_desc_count = 0;
	f.tx[0].len_stat = DMADESC_UNDER_MASK;
	f.skb[0] = napi_build_skb(calloc(1, 64), 64); f.skb[0]->len = 64;
	overwrite_tx = true;
	assert(bcm6368_enetsw_tx_reclaim(&f.ndev, 0, 64) == 1);
	assert(f.ndev.stats.tx_errors == 1 && tx_completed == 1);
	teardown(&f);
	puts("enetsw actual callbacks: RX bounds/errors/ownership/lifetime/wrap; TX-only budget; NAPI completion; TX status reuse PASS");
	return 0;
}
