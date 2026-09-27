import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "calculations"))

from kei16_flipout_drive import calculate  # noqa: E402


class Kei16FlipoutDriveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = json.loads((ROOT / "calculations" / "kei16_flipout_drive_inputs.json").read_text(encoding="utf-8"))
        cls.result = calculate(cls.inputs)

    def test_every_registered_design_check_passes(self):
        self.assertTrue(self.result["all_checks_pass"], self.result["checks"])

    def test_only_one_dc_motor_is_registered(self):
        self.assertEqual(self.inputs["motor"]["sku"], "5203-2402-0019")

    def test_two_equal_38_link_chain_stages_are_96mm_center(self):
        fixed = self.result["fixed_drive"]
        self.assertAlmostEqual(fixed["chain_center_distance_mm"], 96.0, places=3)

    def test_stock_460mm_belt_sets_arm_near_180mm(self):
        front = self.result["front_bar_drive"]
        self.assertAlmostEqual(front["calculated_center_distance_mm"], 179.887, places=3)
        self.assertGreaterEqual(front["small_pulley_teeth_in_mesh"], 6.0)

    def test_latch_servo_is_not_a_structural_stop(self):
        deployment = self.result["deployment"]
        self.assertLessEqual(deployment["servo_stall_fraction_for_static_release"], 0.25)

    def test_current_alert_and_slip_target_precede_motor_stall(self):
        self.assertLess(self.inputs["motor"]["software_current_alert_a"], self.inputs["motor"]["stall_current_a"])
        self.assertLessEqual(self.inputs["protection"]["target_primary_slip_torque_nm"], 0.9)


if __name__ == "__main__":
    unittest.main()
