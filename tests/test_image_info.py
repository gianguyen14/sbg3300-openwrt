import importlib.util
from importlib.machinery import SourceFileLoader
import pathlib
import struct
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_loader(
    "sbg3300_image_info",
    SourceFileLoader("sbg3300_image_info", str(ROOT / "tools/sbg3300-image-info")),
)
image_info = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(image_info)


def valid_fixture():
    payload = b"fixture-payload" + bytes(300)
    trailer = bytearray(32)
    data = bytearray(image_info.TAG_SIZE + len(payload) + len(trailer))

    def put(off, size, value):
        encoded = str(value).encode("ascii")
        data[off:off + size] = encoded.ljust(size, b"\0")

    put(0x00, 4, "6")
    put(0x04, 4, "MSTC")
    put(0x0E, 4, "4506")
    put(0x26, 6, "63268")
    put(0x2C, 18, "963168MXH_17A")
    put(0x3E, 10, len(payload))
    put(0x48, 10, 0)
    put(0x54, 12, 0)
    put(0x5E, 12, 3217293312)
    put(0x6A, 12, len(payload))
    put(0x74, 12, 0)
    put(0x80, 12, 0)
    data[0xCE] = 1
    data[image_info.TAG_SIZE:image_info.TAG_SIZE + len(payload)] = payload
    trailer[:0x1C] = bytes(range(0x1C))
    data[-len(trailer):] = trailer
    struct.pack_into(">I", data, 0xD8, image_info.raw_crc32(payload))
    struct.pack_into(">I", data, 0xDC, image_info.raw_crc32(payload))
    struct.pack_into(">I", data, 0xEC, image_info.raw_crc32(data[:0xEC]))
    struct.pack_into(">I", data, image_info.TAG_SIZE + len(payload) + 0x1C,
                     image_info.raw_crc32(trailer[:0x1C]))
    return data


class ImageInfoTests(unittest.TestCase):
    def test_valid_image(self):
        result = image_info.parse_image(valid_fixture())
        self.assertTrue(result["structural_ok"])
        self.assertTrue(result["header_crc_ok"])
        self.assertTrue(result["payload_crc1_ok"])
        self.assertTrue(result["payload_crc2_ok"])
        self.assertTrue(result["trailer"]["crc_ok"])

    def test_payload_corruption(self):
        data = valid_fixture()
        data[image_info.TAG_SIZE] ^= 1
        result = image_info.parse_image(data)
        self.assertFalse(result["payload_crc1_ok"])

    def test_header_corruption(self):
        data = valid_fixture()
        data[0x2C] ^= 1
        result = image_info.parse_image(data)
        self.assertFalse(result["header_crc_ok"])
        self.assertFalse(result["structural_ok"])

    def test_truncated_payload_rejected(self):
        data = valid_fixture()[:image_info.TAG_SIZE + 3]
        with self.assertRaises(image_info.ImageError):
            image_info.parse_image(data)


if __name__ == "__main__":
    unittest.main()
