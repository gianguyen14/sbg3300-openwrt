// SPDX-License-Identifier: GPL-2.0-only
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "../drivers/xtm/xtm_core.h"

static void test_contract(void)
{
	struct xtm_queue q;
	xtm_u32 i, word;
	struct xtm_completion c;

	assert(xtm_queue_init(&q, 0, XTM_TX) == -EINVAL);
	assert(xtm_queue_init(&q, XTM_RING_MAX_COUNT + 1, XTM_TX) == -EINVAL);
	assert(xtm_queue_init(&q, 1, (enum xtm_direction)2) == -EINVAL);
	assert(!xtm_queue_init(&q, 1, XTM_TX));
	assert(xtm_queue_complete(&q, 0, 64, &c) == -EAGAIN);
	assert(xtm_queue_post(&q, 0, 0, &i, &word) == -EINVAL);
	assert(xtm_queue_post(&q, 4096, 0, &i, &word) == -EINVAL);
	assert(xtm_queue_post(&q, 64, XTM_DESC_OWN, &i, &word) == -EINVAL);
	assert(!q.pending);
	assert(!xtm_queue_post(&q, 64, 0x31, &i, &word));
	assert(i == 0 && word == 0x0040f031);
	assert(q.head == q.tail && q.pending == 1);
	assert(xtm_queue_post(&q, 64, 0, &i, &word) == -ENOSPC);
	assert(xtm_queue_complete(&q, word, 64, &c) == -EAGAIN);
	assert(q.pending == 1); /* DMA retains ownership */
	assert(!xtm_queue_complete(&q, word & ~XTM_DESC_OWN, 64, &c));
	assert(c.length == 64 && !q.pending);
	assert(!xtm_queue_post(&q, XTM_DESC_MAX_LENGTH, XTM_DESC_FSTAT, &i, &word));
	assert(word == 0x0fffffff);
	assert(!xtm_queue_complete(&q, word & ~XTM_DESC_OWN, 4095, &c));
}

static void test_wrap_and_fifo(void)
{
	struct xtm_queue q;
	struct xtm_completion c;
	xtm_u32 words[7] = {0}, ids[7] = {0}, index, word;
	unsigned int produced = 0, consumed = 0, step;

	assert(!xtm_queue_init(&q, 7, XTM_TX));
	/* Non power-of-two capacity; repeatedly wrap a completely full ring. */
	for (step = 0; step < 10000; step++) {
		if (q.pending < q.count && (step % 3 || !q.pending)) {
			assert(!xtm_queue_post(&q, 100, 0, &index, &word));
			words[index] = word;
			ids[index] = produced++;
			assert(!!(word & XTM_DESC_WRAP) == (index == 6));
		} else {
			assert(xtm_queue_complete(&q, words[q.head], 100, &c) == -EAGAIN);
			words[q.head] &= ~XTM_DESC_OWN; /* simulated hardware only */
			assert(!xtm_queue_complete(&q, words[q.head], 100, &c));
			assert(ids[c.index] == consumed++);
		}
		assert(q.pending == produced - consumed);
		assert(q.pending <= q.count && q.head < 7 && q.tail < 7);
	}
	while (q.pending) {
		words[q.head] &= ~XTM_DESC_OWN;
		assert(!xtm_queue_complete(&q, words[q.head], 100, &c));
		assert(ids[c.index] == consumed++);
	}
	assert(produced == consumed && q.head == q.tail);
}

static void test_rx_errors_and_cancel(void)
{
	struct xtm_queue q, before;
	struct xtm_completion c;
	xtm_u32 index, word;

	assert(!xtm_queue_init(&q, 3, XTM_RX));
	assert(xtm_queue_post(&q, 2048, 1, &index, &word) == -EINVAL);
	assert(!xtm_queue_post(&q, 2048, 0, &index, &word));
	assert(word == 0x08008000); /* RX does not fabricate SOP/EOP */
	before = q;
	assert(xtm_queue_complete(&q, word, 2048, &c) == -EAGAIN);
	assert(before.head == q.head && before.tail == q.tail &&
	       before.pending == q.pending && before.count == q.count);
	assert(xtm_queue_complete(&q, (100 << 16) | XTM_DESC_RX_ERROR, 2048, &c) == -EBADMSG);
	assert(c.index == 0 && c.length == 100 && !q.pending);
	assert(!xtm_queue_post(&q, 100, 0, &index, &word));
	assert(xtm_queue_complete(&q, 101 << 16, 100, &c) == -EMSGSIZE);
	assert(!q.pending);
	assert(!xtm_queue_post(&q, 100, 0, &index, &word));
	assert(xtm_queue_complete(&q, 0, 100, &c) == -EMSGSIZE);
	assert(!q.pending);
	/* Preserve raw SAR cell/match status; do not apply Ethernet error masks. */
	assert(!xtm_queue_post(&q, 100, 0, &index, &word));
	assert(!xtm_queue_complete(&q, (53U << 16) | 0x401, 100, &c));
	assert(c.length == 53 && c.status == 0x401);
	assert(!xtm_queue_post(&q, 100, 0, &index, &word));
	assert(!xtm_queue_cancel(&q, &index) && index == 1);
	assert(xtm_queue_cancel(&q, &index) == -EAGAIN);
	/* Cancel an entire OWN ring only after simulated controller quiescence. */
	for (unsigned int j = 0; j < 3; j++)
		assert(!xtm_queue_post(&q, 100, 0, &index, &word));
	for (unsigned int j = 0; j < 3; j++) {
		assert(!xtm_queue_cancel(&q, &index));
		assert(index == (j + 2) % 3);
	}
	assert(!q.pending && q.head == q.tail);
}

int main(void)
{
	test_contract();
	test_wrap_and_fifo();
	test_rx_errors_and_cancel();
	puts("XTM core: descriptor, ownership, FIFO, wrap, error and cancel tests passed");
	return 0;
}
