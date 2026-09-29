import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config" / "t06_launcher_cots.json").read_text(encoding="utf-8"))
REPORT = json.loads((ROOT / "cad" / "output" / "paddle_launcher_feasibility_report.json").read_text(encoding="utf-8"))


class T06LauncherCotsTests(unittest.TestCase):
    def test_catalog_skus_are_fixed(self):
        expected = {
            "flywheel": "3613-0014-0096",
            "flywheel_hub": "1309-0016-4008",
            "flywheel_shaft": "2106-4008-1680",
            "shaft_bearing": "1611-0514-4008",
            "flywheel_motor": "5203-2402-0003",
            "motor_clamp": "1401-0043-0036",
            "shaft_coupler": "4007-4008-4008",
            "gap_servo": "2000-0025-0002",
            "feeder_servo": "2000-0025-0003",
            "feeder_shaft": "2106-4008-1920",
            "servo_frame": "1802-0043-0001",
            "gap_servo_hub": "1908-0025-0032",
            "feeder_servo_coupler": "4001-0025-4008",
        }
        self.assertEqual({key: CONFIG[key]["sku"] for key in expected}, expected)

    def test_launcher_has_no_external_gear_mesh(self):
        self.assertEqual(CONFIG["external_gears"]["quantity"], 0)
        self.assertTrue(REPORT["checks"]["external_gear_count_is_zero"])

    def test_catalog_bearing_and_shaft_dimensions_reach_report(self):
        self.assertEqual(CONFIG["shaft_bearing"]["outer_diameter_mm"], 14.0)
        self.assertEqual(CONFIG["shaft_bearing"]["thickness_mm"], 5.0)
        self.assertEqual(CONFIG["flywheel_shaft"]["length_mm"], 168.0)
        self.assertEqual(REPORT["shaft_clearance_slot_width_mm"], 8.4)
        self.assertEqual(REPORT["shaft_clearance_slot_overall_length_mm"], 17.4)

    def test_drive_stack_has_engagement_and_clearance(self):
        stack = REPORT["drive_axial_stack_mm"]
        self.assertGreaterEqual(stack["flywheel_shaft_engagement"], 7.0)
        self.assertGreaterEqual(stack["motor_shaft_engagement"], 7.0)
        self.assertGreaterEqual(stack["coupler_to_carriage_clearance"], 0.5)
        self.assertGreaterEqual(stack["shaft_tip_gap"], 0.5)

    def test_both_gap_endpoints_pass_selected_interference_checks(self):
        for name in ("pollen", "nectar"):
            config = REPORT["configurations"][name]
            self.assertTrue(config["bounding_box"]["within_18in_cube"])
            self.assertTrue(config["interference_checks"]["all_checked_interfaces_clear"])
        self.assertTrue(all(REPORT["checks"].values()))


if __name__ == "__main__":
    unittest.main()
