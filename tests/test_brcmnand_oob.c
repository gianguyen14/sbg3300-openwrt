/* SPDX-License-Identifier: GPL-2.0-only */
/* Actual kernel callback test, not a flash operation or hardware probe. */
#include <assert.h>
#include <errno.h>
#include <stdint.h>
#include <stdio.h>

typedef uint32_t u32;
struct brcmnand_cfg { int spare_area_size, sector_size_1k, page_size; };
struct brcmnand_host { struct brcmnand_cfg hwcfg; };
struct nand_chip { struct brcmnand_host *host; };
struct mtd_info { struct nand_chip *chip; };
struct mtd_oob_region { unsigned int offset, length; };
static struct nand_chip *mtd_to_nand(struct mtd_info *mtd) { return mtd->chip; }
static struct brcmnand_host *nand_get_controller_data(struct nand_chip *chip) { return chip->host; }
#include "brcmnand-oob-under-test.inc"

int main(void)
{
	struct brcmnand_host host = { {16, 0, 2048} };
	struct nand_chip chip = { &host };
	struct mtd_info mtd = { &chip };
	struct mtd_oob_region region;
	/* Public legacy header values are facts, not vendor implementation. */
	const unsigned int ecc_offsets[4] = {6, 22, 38, 54};
	const unsigned int free_offsets[5] = {2, 9, 25, 41, 57};
	const unsigned int free_lengths[5] = {4, 13, 13, 13, 7};
	unsigned int owned[64] = {0}, ecc_bytes = 0, free_bytes = 0;
	owned[0] = owned[1] = 1;
	for (int section = 0; section < 4; section++) {
		assert(brcmnand_hamming_ooblayout_ecc(&mtd, section, &region) == 0);
		assert(region.offset == ecc_offsets[section] && region.length == 3);
		assert(region.offset + region.length <= 64);
		for (unsigned int i = region.offset; i < region.offset + region.length; i++)
			assert(owned[i]++ == 0);
		ecc_bytes += region.length;
	}
	assert(brcmnand_hamming_ooblayout_ecc(&mtd, 4, &region) == -ERANGE);
	for (int section = 0; section < 5; section++) {
		assert(brcmnand_hamming_ooblayout_free(&mtd, section, &region) == 0);
		assert(region.offset == free_offsets[section] && region.length == free_lengths[section]);
		assert(region.offset + region.length <= 64);
		for (unsigned int i = region.offset; i < region.offset + region.length; i++)
			assert(owned[i]++ == 0);
		free_bytes += region.length;
	}
	assert(brcmnand_hamming_ooblayout_free(&mtd, 5, &region) == -ERANGE);
	assert(ecc_bytes == 12 && free_bytes == 50);
	for (unsigned int i = 0; i < 64; i++)
		assert(owned[i] == 1);
	puts("Actual Linux Hamming OOB callbacks: legacy 2KiB/64-byte layout, 12 ECC/50 free bytes and bounds PASS; physical media NOT-TESTED");
	return 0;
}
