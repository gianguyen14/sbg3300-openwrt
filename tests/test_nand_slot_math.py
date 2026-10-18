import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "sbg3300_slot_map", ROOT / "tools/sbg3300-slot-map.py")
slot_map = importlib.util.module_from_spec(spec)
spec.loader.exec_module(slot_map)


class StockSlotMathTests(unittest.TestCase):
    def test_stock_tag_maps_to_first_slot(self):
        tag = slot_map.read_stock_tag(Path("/home/hermes/sbg3300-build/reference-stock-aady9.bin"))
        self.assertEqual(tag.rootfs_address, 0xBFC40000)
        self.assertEqual(tag.rootfs_length, 0x16A0000)
        self.assertEqual(slot_map.vendor_rootfs_offset(tag.rootfs_address), 0x40000)

    def test_stock_slot1_tag_and_live_slot2_translation(self):
        tag = slot_map.read_stock_tag(Path("/home/hermes/sbg3300-build/reference-stock-aady9.bin"))
        slot1 = slot_map.vendor_rootfs_offset(tag.rootfs_address)
        slot2 = slot_map.vendor_slot2_write_offset(0x08000000)
        slot2_tag_addr = slot_map.vendor_slot2_rootfs_address(0x08000000)
        self.assertEqual(slot1, 0x00040000)
        self.assertEqual(slot2, 0x04020000)
        self.assertEqual(slot2_tag_addr, 0xC3C20000)
        self.assertEqual(slot_map.vendor_rootfs_offset(slot2_tag_addr), 0x04020000)
        self.assertEqual(slot_map.live_rootfs_extent(slot2, tag.rootfs_length),
                         (0x04020000, 0x056c0000))

    def test_slot1_tag_block_and_rootfs_offsets_are_distinct(self):
        tag = slot_map.read_stock_tag(Path("/home/hermes/sbg3300-build/reference-stock-aady9.bin"))
        rootfs_offset = slot_map.vendor_rootfs_offset(tag.rootfs_address)
        tag_block_offset = rootfs_offset - slot_map.TAG_BLOCK_LEN
        self.assertEqual(tag_block_offset, 0x20000)
        self.assertNotEqual(tag_block_offset, rootfs_offset)


if __name__ == "__main__":
    unittest.main()