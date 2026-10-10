// SPDX-License-Identifier: GPL-2.0-only
/* CPU-only test doubles for the real callback body, not a kernel/DMA backend. */
#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <errno.h>

typedef int netdev_tx_t;
#define NETDEV_TX_OK 0
#define NETDEV_TX_BUSY 1
#define ETH_ZLEN 60
#define GFP_ATOMIC 0
#define READ_ONCE(v) (v)
struct sk_buff { unsigned int len; void *data; };
struct xtm_ptm {
	int tx_lock, stats_lock;
	bool link_up;
	void *tx;
	unsigned short tx_status;
	struct { unsigned int tx_dropped; } stats;
};
struct net_device { struct xtm_ptm *priv; };
static unsigned int available, touched, stopped, consumed, freed, submitted, sent;
static int linear_error, padding_error, submit_error;
#define spin_lock_irqsave(lock, flags) do { (flags) = 0; assert(!*(lock)); *(lock) = 1; } while (0)
#define spin_unlock_irqrestore(lock, flags) do { (void)(flags); assert(*(lock)); *(lock) = 0; } while (0)
static struct xtm_ptm *netdev_priv(struct net_device *n) { return n->priv; }
static unsigned int xtm_dma_available(void *ring) { (void)ring; return available; }
static void netif_stop_queue(struct net_device *n) { (void)n; stopped++; }
static int skb_linearize(struct sk_buff *s) { (void)s; touched++; return linear_error; }
static int skb_put_padto(struct sk_buff *s, unsigned int length)
{
	touched++;
	if (padding_error) { freed++; return padding_error; }
	if (s->len < length) s->len = length;
	return 0;
}
static int xtm_dma_tx_submit(void *r, void *data, unsigned int len, unsigned short status, int gfp)
{
	(void)r; (void)data; (void)len; (void)status; (void)gfp;
	submitted++;
	if (!submit_error) { assert(available); available--; }
	return submit_error;
}
static void netdev_sent_queue(struct net_device *n, unsigned int len) { (void)n; sent += len; }
static void dev_consume_skb_any(struct sk_buff *s) { assert(s); consumed++; }
static void dev_kfree_skb_any(struct sk_buff *s) { if (s) freed++; }

#include "xtm-xmit-under-test.inc"

int main(void)
{
	unsigned int scenario;
	for (scenario = 0; scenario < 8; scenario++) {
		struct xtm_ptm p = { .link_up = true };
		struct net_device n = { .priv = &p };
		struct sk_buff skb = { .len = 42 };
		netdev_tx_t ret;
		available = 2;
		touched = stopped = consumed = freed = submitted = sent = 0;
		linear_error = padding_error = submit_error = 0;
		if (scenario == 0) available = 0;
		if (scenario == 1) p.link_up = false;
		if (scenario == 2) skb.len = 1523;
		if (scenario == 3) linear_error = -ENOMEM;
		if (scenario == 4) padding_error = -ENOMEM;
		if (scenario == 5) submit_error = -EIO;
		if (scenario == 7) available = 1;
		ret = xtm_ptm_xmit(&skb, &n);
		assert(!p.tx_lock && !p.stats_lock);
		if (scenario < 2) {
			assert(ret == NETDEV_TX_BUSY && skb.len == 42);
			assert(!touched && !consumed && !freed && !submitted && !sent);
			assert(stopped == 1 && !p.stats.tx_dropped);
		} else if (scenario < 6) {
			assert(ret == NETDEV_TX_OK && freed == 1 && !consumed && !sent);
			assert(p.stats.tx_dropped == 1);
		} else {
			assert(ret == NETDEV_TX_OK && consumed == 1 && !freed);
			assert(submitted == 1 && sent == 60 && !p.stats.tx_dropped);
			assert(stopped == (scenario == 7));
		}
	}
	puts("Actual TX callback/API doubles: PASS (BUSY ownership, drops, padding, BQL/backpressure)");
	return 0;
}
