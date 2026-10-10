// SPDX-License-Identifier: GPL-2.0-only
#include "xtm_ptm_core.h"

int xtm_ptm_rx_length(xtm_u16 status, xtm_u32 length, xtm_u16 match_id,
		      enum xtm_ptm_trailer trailer, xtm_u32 *payload)
{
	if (!payload || match_id > 127 ||
	    (trailer != XTM_PTM_TRAILER_PRESENT && trailer != XTM_PTM_TRAILER_REMOVED))
		return -EINVAL;
	if (status & XTM_DESC_OWN)
		return -EAGAIN;
	if (status & XTM_DESC_RX_ERROR)
		return -EBADMSG;
	if ((status & (XTM_DESC_SOP | XTM_DESC_EOP)) != (XTM_DESC_SOP | XTM_DESC_EOP))
		return -EMSGSIZE;
	if (status & 0x0400) /* SAR cell dispatch requires a separate ATM/control path. */
		return -EPROTONOSUPPORT;
	if ((status & 0x007f) != match_id)
		return -ENOENT;
	if (trailer == XTM_PTM_TRAILER_PRESENT) {
		if (length < 20) /* Ethernet header plus 4-byte FCS and 2-byte PTM CRC */
			return -EMSGSIZE;
		length -= 6;
	}
	if (length < 14 || length > 1522)
		return -EMSGSIZE;
	*payload = length;
	return 0;
}

int xtm_ptm_tx_status(xtm_u16 vcid, xtm_u16 *status)
{
	/* Slot 15 is the family's diagnostic TEQ VCID; do not use it as data. */
	if (!status || vcid >= 15)
		return -EINVAL;
	*status = vcid | 0x00f0 | 0x0003; /* PTM content type, Ethernet FCS, PTM CRC */
	return 0;
}
