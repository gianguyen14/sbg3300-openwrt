// SPDX-License-Identifier: GPL-2.0-only
#include "xtm_core.h"

static xtm_u32 xtm_next(const struct xtm_queue *q, xtm_u32 index)
{
	return index + 1 == q->count ? 0 : index + 1;
}

int xtm_queue_init(struct xtm_queue *q, xtm_u32 count,
		   enum xtm_direction direction)
{
	if (!q || !count || count > XTM_RING_MAX_COUNT ||
	    (direction != XTM_RX && direction != XTM_TX))
		return -EINVAL;
	q->count = count;
	q->head = 0;
	q->tail = 0;
	q->pending = 0;
	q->direction = direction;
	return 0;
}

int xtm_queue_post(struct xtm_queue *q, xtm_u32 capacity, xtm_u16 fstat,
		   xtm_u32 *index, xtm_u32 *word)
{
	xtm_u32 status;

	if (!q || !index || !word || !q->count || !capacity ||
	    capacity > XTM_DESC_MAX_LENGTH || (fstat & ~XTM_DESC_FSTAT) ||
	    (q->direction == XTM_RX && fstat))
		return -EINVAL;
	if (q->pending == q->count)
		return -ENOSPC;
	status = XTM_DESC_OWN;
	if (q->direction == XTM_TX)
		status |= XTM_DESC_SOP | XTM_DESC_EOP | fstat;
	if (q->tail == q->count - 1)
		status |= XTM_DESC_WRAP;
	*index = q->tail;
	*word = (capacity << 16) | status;
	q->tail = xtm_next(q, q->tail);
	q->pending++;
	return 0;
}

int xtm_queue_complete(struct xtm_queue *q, xtm_u32 word,
		       xtm_u32 capacity, struct xtm_completion *result)
{
	int ret = 0;

	if (!q || !result || !q->count)
		return -EINVAL;
	if (!q->pending || (word & XTM_DESC_OWN))
		return -EAGAIN;
	result->index = q->head;
	result->length = word >> 16;
	result->status = word & 0xffff;
	/* Consume even a bad completion so an error cannot wedge the ring. */
	q->head = xtm_next(q, q->head);
	q->pending--;
	if (!result->length || result->length > capacity ||
	    result->length > XTM_DESC_MAX_LENGTH)
		ret = -EMSGSIZE;
	else if (q->direction == XTM_RX && (word & XTM_DESC_RX_ERROR))
		ret = -EBADMSG;
	return ret;
}

int xtm_queue_cancel(struct xtm_queue *q, xtm_u32 *index)
{
	if (!q || !index || !q->count)
		return -EINVAL;
	if (!q->pending)
		return -EAGAIN;
	*index = q->head;
	q->head = xtm_next(q, q->head);
	q->pending--;
	return 0;
}
