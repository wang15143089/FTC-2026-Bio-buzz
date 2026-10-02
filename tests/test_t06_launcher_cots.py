import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config" / "t06_launcher_cots.json").read_text(encoding="utf-8"))
REPORT = json.loads((ROOT / "cad" / "output" / "paddle_launcher_feasibility_report.json").read_text(encoding="utf-8"))

#: SKUs whose official supplier file is not face-connected, with the body count
#: of the whole part.  Facts MEASURED_FROM_OFFICIAL_CAD 2026-10-01, recorded in
#: config/t06_vendor_derivation.json and cad/output/vendor_solids/<sku>.json.
#: The split is the supplier's own: the 5203-2402-0003 gearmotor separates its
#: housing shell by exactly 0.0450 mm, two plates by 0.028856 mm and the sensor
#: magnet by 0.0500 mm, and the 1611-0514-4008 bearing's two shield discs touch
#: the race at 0.0000 mm without ever merging.  DEC-0021 keeps each part whole,
#: so the count below is the official count and nothing has been dropped.
WHOLE_PART_MULTI_BODY_SKUS = {
    "1309-0016-4008": 3,
    "1401-0043-0036": 2,
    "1611-0514-4008": 3,
    "2000-0025-0002": 11,
    "2000-0025-0003": 11,
    "2106-4008-1680": 2,
    "2106-4008-1920": 2,
    "3613-0014-0096": 2,
    "5203-2402-0003": 66,
}

#: SKUs shipped by the supplier with loose fasteners that are not the purchased
#: part and are therefore dropped by the per-SKU keep rule.
SKUS_WITH_DROPPED_SUPPLIER_HARDWARE = {"1802-0043-0001", "4001-0025-4008", "4007-4008-4008"}


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

    def test_every_vendor_component_is_the_whole_official_part(self):
        # DEC-0021: a purchased part is one working *part*, not necessarily one
        # B-rep solid.  The whole official STEP is used, so a part the supplier
        # modelled with real internal air gaps keeps its own body split.
        bodies = REPORT["vendor_component_bodies"]
        self.assertEqual(set(bodies), set(REPORT["official_vendor_cad_imported_skus"]))
        self.assertEqual(
            REPORT["vendor_whole_part_multi_body_skus"], sorted(WHOLE_PART_MULTI_BODY_SKUS)
        )
        for sku, item in bodies.items():
            with self.subTest(sku=sku):
                # The launcher carries the derived part, not a reduced proxy.
                self.assertEqual(item["bodies"], item["derived_solid_count"])
                # Every supplier body the keep rule retains reaches the launcher.
                self.assertEqual(
                    item["bodies"], item["source_step_solids"] - item["dropped_solids"]
                )
                # DEC-0021: no Boolean union is ever run on a purchased part.
                self.assertFalse(item["boolean_union_attempted"])
                if sku in WHOLE_PART_MULTI_BODY_SKUS:
                    self.assertEqual(item["bodies"], WHOLE_PART_MULTI_BODY_SKUS[sku])
                    self.assertEqual(item["dropped_solids"], 0)
                    self.assertFalse(item["single_solid"])
                else:
                    self.assertEqual(item["bodies"], 1)
        for sku in SKUS_WITH_DROPPED_SUPPLIER_HARDWARE:
            with self.subTest(sku=sku):
                self.assertGreater(bodies[sku]["dropped_solids"], 0)
        self.assertTrue(REPORT["checks"]["every_vendor_component_is_the_whole_derived_part"])
        self.assertTrue(REPORT["checks"]["multi_body_vendor_parts_keep_the_whole_official_file"])
        self.assertTrue(REPORT["checks"]["no_boolean_union_is_run_on_a_vendor_part"])

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
