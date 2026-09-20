import math
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "calculations"))

import p3_ballistics  # noqa: E402
import p3_motor_screen  # noqa: E402
import p3_concept_trade  # noqa: E402
import p3_launcher_comparison  # noqa: E402


class P3BallisticsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.inputs = p3_ballistics.load_inputs()

    def test_inputs_and_grid(self) -> None:
        p3_ballistics.validate_inputs(self.inputs)
        rows = p3_ballistics.generate_rows(self.inputs)
        self.assertEqual(len(rows), 3 * 4 * 3)

    def test_reference_case(self) -> None:
        result = p3_ballistics.solve_trajectory(
            self.inputs["gravity_m_s2"],
            0.55,
            self.inputs["target"]["aim_height_m"],
            1.5,
            55.0,
        )
        self.assertIsNotNone(result)
        assert result is not None
        self.assertTrue(
            math.isclose(result["required_exit_speed_m_s"], 5.2078, abs_tol=1e-4)
        )
        self.assertLess(result["entry_angle_deg"], 0)

    def test_max_ball_nominal_center_clearance(self) -> None:
        target = self.inputs["target"]
        diameter = self.inputs["gamepiece"]["nectar_nominal_diameter_m"]
        self.assertGreater((target["opening_width_m"] - diameter) / 2, 0.2)
        self.assertGreater(
            (target["rectangular_opening_height_m"] - diameter) / 2, 0.05
        )

    def test_motor_screen_rejects_drive_motor_direct_drive(self) -> None:
        rows = p3_motor_screen.generate_rows(self.inputs)
        drive_rows = [row for row in rows if row["sku"] == "5203-2402-0019"]
        self.assertEqual(len(drive_rows), 2)
        self.assertTrue(
            all(row["screen_result"] == "FAIL_DIRECT_DRIVE" for row in drive_rows)
        )

    def test_1620_rpm_with_120mm_wheel_passes_no_load_screen(self) -> None:
        rows = p3_motor_screen.generate_rows(self.inputs)
        candidate = next(
            row
            for row in rows
            if row["sku"] == "5203-2402-0003"
            and row["wheel_diameter_mm"] == 120.0
        )
        self.assertEqual(candidate["screen_result"], "PASS_PROTOTYPE_RANGE")

    def test_preliminary_concept_ranking(self) -> None:
        result = p3_concept_trade.rows()
        self.assertEqual(result[0]["concept"], "C06-B_opposed_dual_flywheel")
        self.assertEqual(result[0]["score_0_to_100"], "76.0")

    def test_ideal_contact_kinematics(self) -> None:
        radius = 0.071 / 2
        single = p3_launcher_comparison.ideal_contact_state(12.0, 0.0, radius)
        dual = p3_launcher_comparison.ideal_contact_state(6.0, 6.0, radius)
        self.assertTrue(math.isclose(single[0], 6.0))
        self.assertGreater(abs(single[1]), 0.0)
        self.assertTrue(math.isclose(dual[0], 6.0))
        self.assertTrue(math.isclose(dual[1], 0.0))

    def test_symmetric_gap_preserves_centerline(self) -> None:
        result = p3_launcher_comparison.comparison_rows(self.inputs)
        shift = next(row for row in result if row["claim_id"] == "CMP-005")
        self.assertEqual(shift["c06_a_single_flywheel_hood"], "10.0000")
        self.assertEqual(shift["c06_b_opposed_dual_flywheel"], "0.0000")

    def test_flower_nominal_clearances(self) -> None:
        result = p3_launcher_comparison.flower_rows(self.inputs)
        nectar = next(row for row in result if row["claim_id"] == "FLW-002")
        retrieval = next(row for row in result if row["claim_id"] == "FLW-003")
        self.assertTrue(math.isclose(float(nectar["c06_a_single_flywheel_hood"]), 0.0053, abs_tol=5e-5))
        self.assertEqual(retrieval["c06_a_single_flywheel_hood"], "0.0190")


if __name__ == "__main__":
    unittest.main()
