/* SPDX-License-Identifier: GPL-2.0-only */
#ifndef SBG3300_XTM_DMA_H
#define SBG3300_XTM_DMA_H
#include <linux/device.h>
#include <linux/gfp_types.h>
#include <linux/io.h>
#include "xtm_core.h"

struct xtm_dma_ring;
struct xtm_dma_packet {
	void *data;
	u32 length;
	u16 status;
	int error;
};
struct xtm_dma_stats {
	u64 packets;
	u64 bytes;
	u64 completion_errors;
	u64 mapping_errors;
	u64 allocation_errors;
	u64 ring_full;
	u64 cancelled;
	u64 stop_timeouts;
};

/* Caller must configure a verified DMA mask/window no wider than 32 bits.
 * One descriptor per linear packet. No FAP, FPM, bonding or scatter/gather.
 * The caller owns the device and mapped SAR channel/state resources exclusively.
 * Serialize ring lifetime: stop IRQ/NAPI/users before destroying the object.
 */
struct xtm_dma_ring *xtm_dma_alloc(struct device *dev, enum xtm_direction dir,
				 unsigned int count, gfp_t gfp);
/* Only an inactive exact-SoC IUDMA channel may be attached. No resource guessing. */
int xtm_dma_bind(struct xtm_dma_ring *r, void __iomem *channel,
		 void __iomem *state);
int xtm_dma_start(struct xtm_dma_ring *r);
/* Terminal, sleepable stop; timeout keeps mappings alive. Allocate a new ring
 * for a new session after destruction; this API does not implement suspend.
 */
int xtm_dma_stop(struct xtm_dma_ring *r);
int xtm_dma_destroy(struct xtm_dma_ring *r, struct xtm_dma_stats *final_stats);
int xtm_dma_tx_submit(struct xtm_dma_ring *r, const void *data, unsigned int len,
		      u16 fstat, gfp_t gfp);
int xtm_dma_rx_post(struct xtm_dma_ring *r, unsigned int capacity, gfp_t gfp);
/* 1: returned packet (including error), 0: no completion, negative: API error.
 * Data is CPU-owned/unmapped on return; caller must free it even on error.
 */
int xtm_dma_poll(struct xtm_dma_ring *r, struct xtm_dma_packet *packet);
void xtm_dma_packet_free(struct xtm_dma_packet *packet);
void xtm_dma_get_stats(struct xtm_dma_ring *r, struct xtm_dma_stats *stats);
#endif
