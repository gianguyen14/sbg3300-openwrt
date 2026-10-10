/* SPDX-License-Identifier: GPL-2.0-only */
/* Original ring policy. Hardware format facts are traced in the contract report. */
#ifndef SBG3300_XTM_CORE_H
#define SBG3300_XTM_CORE_H

#ifdef __KERNEL__
#include <linux/types.h>
#include <linux/errno.h>
typedef u32 xtm_u32;
typedef u16 xtm_u16;
#else
#include <stdint.h>
#include <errno.h>
typedef uint32_t xtm_u32;
typedef uint16_t xtm_u16;
#endif

#define XTM_DESC_OWN  0x8000U
#define XTM_DESC_EOP  0x4000U
#define XTM_DESC_SOP  0x2000U
#define XTM_DESC_WRAP 0x1000U
#define XTM_DESC_FSTAT 0x0fffU
#define XTM_DESC_RX_ERROR 0x0800U
#define XTM_DESC_MAX_LENGTH 0x0fffU
#define XTM_RING_MAX_COUNT 8192U /* state_data descriptor index is 13 bits */

enum xtm_direction { XTM_RX, XTM_TX };

struct xtm_queue {
	xtm_u32 count;
	xtm_u32 head;
	xtm_u32 tail;
	xtm_u32 pending;
	enum xtm_direction direction;
};

struct xtm_completion {
	xtm_u32 index;
	xtm_u32 length;
	xtm_u16 status;
};

int xtm_queue_init(struct xtm_queue *q, xtm_u32 count,
		   enum xtm_direction direction);
/* Output word is CPU endian; the DMA adapter must encode it big endian. */
int xtm_queue_post(struct xtm_queue *q, xtm_u32 capacity, xtm_u16 fstat,
		   xtm_u32 *index, xtm_u32 *word);
/* OWN/empty returns EAGAIN without consuming. Malformed results are consumed. */
int xtm_queue_complete(struct xtm_queue *q, xtm_u32 word,
		       xtm_u32 capacity, struct xtm_completion *result);
/* Only valid after the DMA adapter has established hardware quiescence. */
int xtm_queue_cancel(struct xtm_queue *q, xtm_u32 *index);

#endif
