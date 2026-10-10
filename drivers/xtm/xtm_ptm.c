// SPDX-License-Identifier: GPL-2.0-only
#include <linux/etherdevice.h>
#include <linux/interrupt.h>
#include <linux/rtnetlink.h>
#include <linux/workqueue.h>
#include "xtm_ptm.h"

#define XTM_PTM_RING_SIZE 64
#define XTM_PTM_RX_CAPACITY 2048

struct xtm_ptm {
	struct net_device *ndev;
	struct device *dev;
	struct xtm_ptm_config cfg;
	struct xtm_dma_ring *rx, *tx;
	struct napi_struct napi;
	struct delayed_work refill;
	spinlock_t irq_lock, tx_lock, stats_lock;
	struct rtnl_link_stats64 stats;
	u16 tx_status;
	u64 line_rate;
	bool opened, link_up, irqs_requested, napi_enabled;
};

static void xtm_ptm_masks(struct xtm_ptm *p, bool enable)
{
	if (p->rx)
		xtm_dma_irq_mask(p->rx, enable &&
				 xtm_dma_available(p->rx) < XTM_PTM_RING_SIZE);
	if (p->tx)
		xtm_dma_irq_mask(p->tx, enable);
}

static void xtm_ptm_refill_work(struct work_struct *work)
{
	struct xtm_ptm *p = container_of(to_delayed_work(work), struct xtm_ptm, refill);
	unsigned long flags;
	bool posted = false;

	if (!READ_ONCE(p->opened))
		return;
	while (xtm_dma_available(p->rx)) {
		if (xtm_dma_rx_post(p->rx, XTM_PTM_RX_CAPACITY, GFP_KERNEL)) {
			schedule_delayed_work(&p->refill, msecs_to_jiffies(20));
			break;
		}
		posted = true;
	}
	if (posted) {
		/* NAPI restores RX interrupts after recovering from an empty ring. */
		spin_lock_irqsave(&p->irq_lock, flags);
		if (p->opened && napi_schedule_prep(&p->napi)) {
			xtm_ptm_masks(p, false);
			__napi_schedule(&p->napi);
		}
		spin_unlock_irqrestore(&p->irq_lock, flags);
	}
}

static irqreturn_t xtm_ptm_irq(int irq, void *data)
{
	struct xtm_ptm *p = data;
	unsigned long flags;
	u32 status;

	spin_lock_irqsave(&p->irq_lock, flags);
	status = xtm_dma_irq_status(irq == p->cfg.rx_irq ? p->rx : p->tx);
	if (status && p->opened) {
		xtm_ptm_masks(p, false);
		if (napi_schedule_prep(&p->napi))
			__napi_schedule(&p->napi);
	}
	spin_unlock_irqrestore(&p->irq_lock, flags);
	return status ? IRQ_HANDLED : IRQ_NONE;
}

static int xtm_ptm_poll(struct napi_struct *napi, int budget)
{
	struct xtm_ptm *p = container_of(napi, struct xtm_ptm, napi);
	struct xtm_dma_packet packet;
	unsigned long flags;
	unsigned int packets = 0, bytes = 0, tx_work = 0;
	int work = 0;

	/* Acknowledge before consuming. Late events remain pending on unmask;
	 * an in-flight ISR must not clear a completion behind this poll.
	 */
	xtm_dma_irq_ack(p->tx);
	if (budget)
		xtm_dma_irq_ack(p->rx);
	spin_lock_irqsave(&p->tx_lock, flags);
	while (tx_work++ < XTM_PTM_RING_SIZE && xtm_dma_poll(p->tx, &packet) == 1) {
		packets++;
		bytes += packet.capacity; /* BQL matches submitted bytes even on error. */
		spin_lock(&p->stats_lock);
		if (packet.error) {
			p->stats.tx_errors++;
		} else {
			p->stats.tx_packets++;
			p->stats.tx_bytes += packet.length;
		}
		spin_unlock(&p->stats_lock);
		xtm_dma_packet_free(&packet);
	}
	if (packets) {
		netdev_completed_queue(p->ndev, packets, bytes);
		if (READ_ONCE(p->link_up) && xtm_dma_available(p->tx))
			netif_wake_queue(p->ndev);
	}
	spin_unlock_irqrestore(&p->tx_lock, flags);
	if (!budget)
		return 0;
	while (work < budget && xtm_dma_poll(p->rx, &packet) == 1) {
		struct sk_buff *skb = NULL;
		u32 length = 0;
		int ret = packet.error;

		work++;
		if (!ret)
			ret = xtm_ptm_rx_length(packet.status, packet.length,
						p->cfg.match_id, p->cfg.trailer, &length);
		if (!ret && READ_ONCE(p->link_up))
			skb = napi_alloc_skb(napi, length);
		spin_lock_irqsave(&p->stats_lock, flags);
		if (!skb) {
			p->stats.rx_dropped++;
			if (ret)
				p->stats.rx_errors++;
		} else {
			p->stats.rx_packets++;
			p->stats.rx_bytes += length;
		}
		spin_unlock_irqrestore(&p->stats_lock, flags);
		if (skb) {
			skb_put_data(skb, packet.data, length);
			skb->protocol = eth_type_trans(skb, p->ndev);
			napi_gro_receive(napi, skb);
		}
		xtm_dma_packet_free(&packet);
		if (xtm_dma_rx_post(p->rx, XTM_PTM_RX_CAPACITY, GFP_ATOMIC))
			schedule_delayed_work(&p->refill, msecs_to_jiffies(20));
	}
	if (work < budget && napi_complete_done(napi, work)) {
		spin_lock_irqsave(&p->irq_lock, flags);
		if (p->opened)
			xtm_ptm_masks(p, true);
		spin_unlock_irqrestore(&p->irq_lock, flags);
	}
	return work;
}

static netdev_tx_t xtm_ptm_xmit(struct sk_buff *skb, struct net_device *ndev)
{
	struct xtm_ptm *p = netdev_priv(ndev);
	unsigned long flags;
	int ret;

	if (skb->len > 1522 || skb_linearize(skb))
		goto drop;
	if (skb_put_padto(skb, ETH_ZLEN)) {
		skb = NULL; /* skb_put_padto frees the buffer on failure. */
		goto drop;
	}
	spin_lock_irqsave(&p->tx_lock, flags);
	if (!READ_ONCE(p->link_up) || !xtm_dma_available(p->tx)) {
		netif_stop_queue(ndev);
		spin_unlock_irqrestore(&p->tx_lock, flags);
		return NETDEV_TX_BUSY;
	}
	ret = xtm_dma_tx_submit(p->tx, skb->data, skb->len, p->tx_status, GFP_ATOMIC);
	if (!ret) {
		netdev_sent_queue(ndev, skb->len);
		if (!xtm_dma_available(p->tx))
			netif_stop_queue(ndev);
	}
	spin_unlock_irqrestore(&p->tx_lock, flags);
	if (ret)
		goto drop;
	dev_consume_skb_any(skb);
	return NETDEV_TX_OK;
drop:
	spin_lock_irqsave(&p->stats_lock, flags);
	p->stats.tx_dropped++;
	spin_unlock_irqrestore(&p->stats_lock, flags);
	dev_kfree_skb_any(skb);
	return NETDEV_TX_OK;
}

/* Retain any ring that fails to halt. Its DMA mappings/resources remain live. */
static int xtm_ptm_release_rings(struct xtm_ptm *p)
{
	struct xtm_dma_ring **rings[] = { &p->rx, &p->tx };
	int ret = 0;
	unsigned int i;

	for (i = 0; i < ARRAY_SIZE(rings); i++) {
		int err;

		if (!*rings[i])
			continue;
		err = xtm_dma_stop(*rings[i]);
		if (!err)
			err = xtm_dma_destroy(*rings[i], NULL);
		if (err)
			ret = err;
		else
			*rings[i] = NULL;
	}
	return ret;
}

static int xtm_ptm_stop(struct net_device *ndev)
{
	struct xtm_ptm *p = netdev_priv(ndev);
	unsigned long flags;
	int ret;

	netif_tx_disable(ndev);
	spin_lock_irqsave(&p->irq_lock, flags);
	p->opened = false;
	xtm_ptm_masks(p, false);
	spin_unlock_irqrestore(&p->irq_lock, flags);
	if (p->irqs_requested) {
		synchronize_irq(p->cfg.rx_irq);
		synchronize_irq(p->cfg.tx_irq);
	}
	if (p->napi_enabled) {
		napi_disable(&p->napi);
		p->napi_enabled = false;
	}
	cancel_delayed_work_sync(&p->refill);
	if (p->irqs_requested) {
		free_irq(p->cfg.rx_irq, p);
		free_irq(p->cfg.tx_irq, p);
		p->irqs_requested = false;
	}
	ret = xtm_ptm_release_rings(p);
	netdev_reset_queue(ndev);
	return ret;
}

static int xtm_ptm_open(struct net_device *ndev)
{
	struct xtm_ptm *p = netdev_priv(ndev);
	unsigned long flags;
	int ret;
	unsigned int i;

	if (p->rx || p->tx)
		return -EBUSY; /* A prior failed stop is quarantined until halt succeeds. */
	p->rx = xtm_dma_alloc(p->dev, XTM_RX, XTM_PTM_RING_SIZE, GFP_KERNEL);
	if (IS_ERR(p->rx)) {
		ret = PTR_ERR(p->rx);
		p->rx = NULL;
		return ret;
	}
	p->tx = xtm_dma_alloc(p->dev, XTM_TX, XTM_PTM_RING_SIZE, GFP_KERNEL);
	if (IS_ERR(p->tx)) {
		ret = PTR_ERR(p->tx);
		p->tx = NULL;
		goto fail;
	}
	ret = xtm_dma_bind(p->rx, p->cfg.rx_channel, p->cfg.rx_state);
	if (!ret)
		ret = xtm_dma_bind(p->tx, p->cfg.tx_channel, p->cfg.tx_state);
	if (ret)
		goto fail;
	for (i = 0; i < XTM_PTM_RING_SIZE; i++) {
		ret = xtm_dma_rx_post(p->rx, XTM_PTM_RX_CAPACITY, GFP_KERNEL);
		if (ret)
			goto fail;
	}
	ret = request_irq(p->cfg.rx_irq, xtm_ptm_irq, 0, ndev->name, p);
	if (ret)
		goto fail;
	ret = request_irq(p->cfg.tx_irq, xtm_ptm_irq, 0, ndev->name, p);
	if (ret) {
		free_irq(p->cfg.rx_irq, p);
		goto fail;
	}
	p->irqs_requested = true;
	napi_enable(&p->napi);
	p->napi_enabled = true;
	ret = xtm_dma_start(p->rx);
	if (!ret)
		ret = xtm_dma_start(p->tx);
	if (ret)
		goto fail;
	spin_lock_irqsave(&p->irq_lock, flags);
	p->opened = true;
	xtm_ptm_masks(p, true);
	spin_unlock_irqrestore(&p->irq_lock, flags);
	if (p->link_up)
		netif_start_queue(ndev);
	else
		netif_stop_queue(ndev);
	return 0;
fail:
	xtm_ptm_stop(ndev);
	return ret;
}

static void xtm_ptm_stats(struct net_device *ndev, struct rtnl_link_stats64 *stats)
{
	struct xtm_ptm *p = netdev_priv(ndev);
	unsigned long flags;

	spin_lock_irqsave(&p->stats_lock, flags);
	*stats = p->stats;
	spin_unlock_irqrestore(&p->stats_lock, flags);
}

static const struct net_device_ops xtm_ptm_ops = {
	.ndo_open = xtm_ptm_open,
	.ndo_stop = xtm_ptm_stop,
	.ndo_start_xmit = xtm_ptm_xmit,
	.ndo_get_stats64 = xtm_ptm_stats,
	.ndo_validate_addr = eth_validate_addr,
};

struct net_device *xtm_ptm_register(struct device *dev, const struct xtm_ptm_config *cfg)
{
	struct net_device *ndev;
	struct xtm_ptm *p;
	u32 ignored;
	u16 status;
	int ret;

	if (!dev || !cfg || !cfg->rx_channel || !cfg->rx_state || !cfg->tx_channel ||
	    !cfg->tx_state || cfg->rx_irq <= 0 || cfg->tx_irq <= 0 ||
	    cfg->rx_irq == cfg->tx_irq ||
	    xtm_ptm_tx_status(cfg->tx_vcid, &status) ||
	    xtm_ptm_rx_length(XTM_DESC_SOP | XTM_DESC_EOP | cfg->match_id,
			      64, cfg->match_id, cfg->trailer, &ignored))
		return ERR_PTR(-EINVAL);
	ndev = alloc_etherdev(sizeof(*p));
	if (!ndev)
		return ERR_PTR(-ENOMEM);
	SET_NETDEV_DEV(ndev, dev);
	ret = device_get_ethdev_address(dev, ndev);
	if (ret || !is_valid_ether_addr(ndev->dev_addr)) {
		free_netdev(ndev);
		return ERR_PTR(ret ? ret : -EADDRNOTAVAIL);
	}
	p = netdev_priv(ndev);
	p->dev = dev;
	p->ndev = ndev;
	p->cfg = *cfg;
	p->tx_status = status;
	spin_lock_init(&p->irq_lock);
	spin_lock_init(&p->tx_lock);
	spin_lock_init(&p->stats_lock);
	INIT_DELAYED_WORK(&p->refill, xtm_ptm_refill_work);
	netif_napi_add(ndev, &p->napi, xtm_ptm_poll);
	ndev->netdev_ops = &xtm_ptm_ops;
	ndev->min_mtu = 68;
	ndev->max_mtu = 1500;
	strscpy(ndev->name, "ptm%d", IFNAMSIZ);
	netif_carrier_off(ndev);
	ret = register_netdev(ndev);
	if (ret) {
		netif_napi_del(&p->napi);
		free_netdev(ndev);
		return ERR_PTR(ret);
	}
	return ndev;
}
EXPORT_SYMBOL_GPL(xtm_ptm_register);

int xtm_ptm_link_update(struct net_device *ndev, bool up, u64 rate)
{
	struct xtm_ptm *p = netdev_priv(ndev);
	unsigned long flags;

	if (up && !rate)
		return -EINVAL;
	rtnl_lock();
	spin_lock_irqsave(&p->tx_lock, flags);
	WRITE_ONCE(p->link_up, up);
	p->line_rate = up ? rate : 0;
	if (up) {
		netif_carrier_on(ndev);
		if (p->opened && xtm_dma_available(p->tx))
			netif_wake_queue(ndev);
	} else {
		netif_stop_queue(ndev);
		netif_carrier_off(ndev);
	}
	spin_unlock_irqrestore(&p->tx_lock, flags);
	rtnl_unlock();
	return 0;
}
EXPORT_SYMBOL_GPL(xtm_ptm_link_update);

int xtm_ptm_unregister(struct net_device *ndev)
{
	struct xtm_ptm *p = netdev_priv(ndev);
	int ret;

	rtnl_lock();
	dev_close(ndev);
	ret = xtm_ptm_release_rings(p);
	if (!ret)
		unregister_netdevice(ndev);
	rtnl_unlock();
	if (ret)
		return ret; /* Parent must keep the netdev and resources alive. */
	netif_napi_del(&p->napi);
	free_netdev(ndev);
	return 0;
}
EXPORT_SYMBOL_GPL(xtm_ptm_unregister);
