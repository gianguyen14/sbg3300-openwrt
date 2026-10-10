/* SPDX-License-Identifier: GPL-2.0-only */
#ifndef SBG3300_XTM_PTM_CORE_H
#define SBG3300_XTM_PTM_CORE_H
#include "xtm_core.h"
enum xtm_ptm_trailer { XTM_PTM_TRAILER_PRESENT, XTM_PTM_TRAILER_REMOVED };
int xtm_ptm_rx_length(xtm_u16 status, xtm_u32 length, xtm_u16 match_id,
		      enum xtm_ptm_trailer trailer, xtm_u32 *payload);
int xtm_ptm_tx_status(xtm_u16 vcid, xtm_u16 *status);
#endif
