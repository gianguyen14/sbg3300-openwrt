/* SPDX-License-Identifier: GPL-2.0-only */
#ifndef SBG3300_XTM_PTM_H
#define SBG3300_XTM_PTM_H
#include <linux/netdevice.h>
#include "xtm_dma.h"
#include "xtm_ptm_core.h"
struct xtm_ptm_config {
	void __iomem *rx_channel, *rx_state, *tx_channel, *tx_state;
	int rx_irq, tx_irq; /* Linux virtual IRQs from verified platform resources */
	u16 match_id, tx_vcid; /* Established by the real DSL/XTM configuration provider */
	enum xtm_ptm_trailer trailer;
};

/* Sleepable APIs. Parent must own and initialize global SAR/clock/reset/FAP
 * state, configure the device DMA window and keep all resources alive until
 * unregister succeeds. This library has no automatic platform binding.
 */
struct net_device *xtm_ptm_register(struct device *dev, const struct xtm_ptm_config *cfg);
int xtm_ptm_link_update(struct net_device *ndev, bool up, u64 rate);
int xtm_ptm_unregister(struct net_device *ndev);
#endif
