/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef SBG3300_ENETSW_CONTRACT_H
#define SBG3300_ENETSW_CONTRACT_H

#ifdef __KERNEL__
#include <linux/errno.h>
#include <linux/types.h>
typedef u32 enet_u32;
typedef u64 enet_u64;
#else
#include <errno.h>
#include <stdbool.h>
#include <stdint.h>
typedef uint32_t enet_u32;
typedef uint64_t enet_u64;
#endif

/* Optional TX IRQ absence selects the existing polling path; all other
 * lookup failures (including deferred probe) must reach the caller.
 */
static inline int enetsw_irq_config(int irq, bool required, int *effective)
{
	if (!effective)
		return -EINVAL;
	if (irq > 0) {
		*effective = irq;
		return 0;
	}
	if (!required && (irq == -ENXIO || irq == -ENOENT)) {
		*effective = -1;
		return 0;
	}
	return irq ? irq : -ENODEV;
}

/* The actual driver addresses channel and SRAM records with a 16-byte stride.
 * Derive bounds from its mapped resources; do not guess port/channel topology.
 */
static inline int enetsw_channel_check(enet_u32 rx, enet_u32 tx,
				       enet_u64 channel_bytes, enet_u64 state_bytes)
{
	if (rx == tx || rx >= channel_bytes / 16 || tx >= channel_bytes / 16 ||
	    rx >= state_bytes / 16 || tx >= state_bytes / 16)
		return -EINVAL;
	return 0;
}

#endif
