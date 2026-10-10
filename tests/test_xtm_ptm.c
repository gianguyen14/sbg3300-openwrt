// SPDX-License-Identifier: GPL-2.0-only
#include <assert.h>
#include <stdio.h>
#include "../drivers/xtm/xtm_ptm_core.h"

int main(void)
{
	xtm_u32 length = 0;
	xtm_u16 status = XTM_DESC_SOP | XTM_DESC_EOP | 7;
	xtm_u16 tx;
	unsigned int i;

	assert(!xtm_ptm_rx_length(status, 70, 7, XTM_PTM_TRAILER_PRESENT, &length));
	assert(length == 64);
	assert(!xtm_ptm_rx_length(status, 64, 7, XTM_PTM_TRAILER_REMOVED, &length));
	assert(length == 64);
	for (i = 0; i < 20; i++)
		assert(xtm_ptm_rx_length(status, i, 7, XTM_PTM_TRAILER_PRESENT,
					 &length) == -EMSGSIZE);
	assert(!xtm_ptm_rx_length(status, 1528, 7, XTM_PTM_TRAILER_PRESENT, &length));
	assert(length == 1522);
	assert(xtm_ptm_rx_length(status, 1529, 7, XTM_PTM_TRAILER_PRESENT,
				 &length) == -EMSGSIZE);
	assert(xtm_ptm_rx_length(status | XTM_DESC_OWN, 70, 7,
				 XTM_PTM_TRAILER_PRESENT, &length) == -EAGAIN);
	assert(xtm_ptm_rx_length(status | XTM_DESC_RX_ERROR, 70, 7,
				 XTM_PTM_TRAILER_PRESENT, &length) == -EBADMSG);
	assert(xtm_ptm_rx_length(status & ~XTM_DESC_EOP, 70, 7,
				 XTM_PTM_TRAILER_PRESENT, &length) == -EMSGSIZE);
	assert(xtm_ptm_rx_length(status & ~XTM_DESC_SOP, 70, 7,
				 XTM_PTM_TRAILER_PRESENT, &length) == -EMSGSIZE);
	assert(xtm_ptm_rx_length(status | 0x400, 70, 7,
				 XTM_PTM_TRAILER_PRESENT, &length) == -EPROTONOSUPPORT);
	assert(xtm_ptm_rx_length(status, 70, 8, XTM_PTM_TRAILER_PRESENT,
				 &length) == -ENOENT);
	assert(xtm_ptm_rx_length(status, 70, 128, XTM_PTM_TRAILER_PRESENT,
				 &length) == -EINVAL);
	assert(xtm_ptm_rx_length(status, 70, 7, 99, &length) == -EINVAL);
	assert(xtm_ptm_rx_length(status, 70, 7, XTM_PTM_TRAILER_PRESENT, NULL) == -EINVAL);
	for (i = 0; i < 15; i++) {
		assert(!xtm_ptm_tx_status(i, &tx));
		assert(tx == (i | 0xf3));
	}
	assert(xtm_ptm_tx_status(15, &tx) == -EINVAL);
	assert(xtm_ptm_tx_status(16, &tx) == -EINVAL);
	assert(xtm_ptm_tx_status(0, NULL) == -EINVAL);
	puts("PTM policy: PASS (length/trailer/match/cell/error/VCID boundaries)");
	return 0;
}
