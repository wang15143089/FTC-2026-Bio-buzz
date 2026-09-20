import math
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "calculations"))

import t01_drive_trade  # noqa: E402


class T01DriveTradeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.inputs = t01_drive_trade.load_inputs()
        self.motor = self.inputs["drive_motor"]
        self.radius = self.inputs["current_chassis"]["mecanum_wheel_diameter_m"] / 2

    def test_two_motors_halves_peak_power_and_force(self) -> None:
        p4 = t01_drive_trade.peak_metrics(self.motor, 4, self.radius)
        p2 = t01_drive_trade.peak_metrics(self.motor, 2, self.radius)
        self.assertTrue(math.isclose(p2["stall_force_n"] / p4["stall_force_n"], 0.5))
        self.assertTrue(math.isclose(p2["max_mechanical_power_w"] / p4["max_mechanical_power_w"], 0.5))

    def test_two_motors_release_two_ports_and_874_grams(self) -> None:
        result = t01_drive_trade.rows(self.inputs)
        ports = next(row for row in result if row["row_id"] == "DRV-002")
        mass = next(row for row in result if row["row_id"] == "DRV-009")
        self.assertEqual(ports["differential_2_motor"], "2.0000")
        self.assertEqual(mass["differential_2_motor"], "0.8740")

    def test_equal_force_speed_can_exceed_two_motor_voltage(self) -> None:
        op4 = t01_drive_trade.operating_point(self.motor, 4, self.radius, 40.0, 1.0)
        op2 = t01_drive_trade.operating_point(self.motor, 2, self.radius, 40.0, 1.0)
        self.assertTrue(op4["feasible_at_12v"])
        self.assertFalse(op2["feasible_at_12v"])

    def test_lateral_break_even(self) -> None:
        threshold = t01_drive_trade.preserved_heading_break_even_strafe_fraction(0.5, 0.375)
        self.assertTrue(math.isclose(threshold, 0.459116, abs_tol=1e-6))


if __name__ == "__main__":
    unittest.main()
