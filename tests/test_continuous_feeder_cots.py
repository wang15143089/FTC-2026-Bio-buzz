import math
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cad"))

import continuous_servo_feeder_cots as model


class ContinuousServoFeederCotsTests(unittest.TestCase):
    def test_all_motion_hardware_has_vendor_sku_and_url(self):
        for item in model.CATALOG.values():
            self.assertTrue(item["sku"])
            self.assertEqual(item["status"], "KNOWN_VENDOR_VERIFIED")
            self.assertTrue(item["url"].startswith("https://www.gobilda.com/"))

    def test_equal_pulley_belt_centres(self):
        self.assertAlmostEqual(model.HORIZONTAL_CENTER, 140.0, places=6)
        self.assertAlmostEqual(model.INCLINE_CENTER, 120.0, places=6)

    def test_pinch_reduction_is_catalog_16_to_48(self):
        self.assertEqual(model.SMALL_TEETH, 16)
        self.assertEqual(model.LARGE_TEETH, 48)
        self.assertEqual(model.LARGE_TEETH / model.SMALL_TEETH, 3.0)
        self.assertGreater(model.PINCH_CENTER, 50.0)
        self.assertLess(model.PINCH_CENTER, 52.0)

    def test_incline_angle_is_preserved(self):
        dx = model.UPPER_SHAFT[0] - model.JUNCTION_X
        dz = model.UPPER_SHAFT[2] - model.LOWER_SHAFT_Z
        self.assertAlmostEqual(math.hypot(dx, dz), 120.0, places=6)
        self.assertAlmostEqual(math.degrees(math.atan2(dz, dx)), 38.0, places=6)


if __name__ == "__main__":
    unittest.main()
