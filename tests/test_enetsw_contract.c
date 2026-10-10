// SPDX-License-Identifier: GPL-2.0-or-later
#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include "../drivers/ethernet/enetsw_contract.h"

int main(void)
{
	int value = 99;

	assert(!enetsw_irq_config(42, true, &value) && value == 42);
	assert(!enetsw_irq_config(42, false, &value) && value == 42);
	assert(!enetsw_irq_config(-ENXIO, false, &value) && value == -1);
	assert(!enetsw_irq_config(-ENOENT, false, &value) && value == -1);
	value = 99;
	assert(enetsw_irq_config(-ENXIO, true, &value) == -ENXIO && value == 99);
	assert(enetsw_irq_config(0, true, &value) == -ENODEV);
	assert(enetsw_irq_config(0, false, &value) == -ENODEV);
	assert(enetsw_irq_config(-517, false, &value) == -517); /* EPROBE_DEFER */
	assert(enetsw_irq_config(-EINVAL, false, &value) == -EINVAL);
	assert(enetsw_irq_config(-EPERM, false, &value) == -EPERM);
	assert(enetsw_irq_config(42, false, NULL) == -EINVAL);
	assert(!enetsw_channel_check(0, 1, 128, 128));
	assert(!enetsw_channel_check(6, 7, 128, 128));
	assert(enetsw_channel_check(7, 8, 128, 128) == -EINVAL);
	assert(enetsw_channel_check(0, 0, 128, 128) == -EINVAL);
	assert(enetsw_channel_check(0, 1, 128, 16) == -EINVAL);
	assert(enetsw_channel_check(0, 1, 15, 128) == -EINVAL);
	assert(enetsw_channel_check(UINT_MAX, 1, 128, 128) == -EINVAL);
	puts("Ethernet contracts: PASS (IRQ errors/defer/optional absence, DMA resource bounds)");
	return 0;
}
