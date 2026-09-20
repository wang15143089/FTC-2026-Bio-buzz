import math
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "calculations"))

import t04_intake  # noqa: E402


class T04IntakeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.inputs = t04_intake.load_inputs()

    def test_parameters_and_resource_limit(self) -> None:
        t04_intake.validate(self.inputs)
        rows = t04_intake.rows(self.inputs)
        motors = next(row for row in rows if row["claim_id"] == "INT-012")
        reserve = next(row for row in rows if row["claim_id"] == "INT-013")
        self.assertEqual(motors["value"], "7.0000")
        self.assertEqual(reserve["value"], "1.0000")

    def test_rake_nominal_clearance(self) -> None:
        rows = t04_intake.rows(self.inputs)
        clearance = next(row for row in rows if row["claim_id"] == "INT-002")
        self.assertTrue(math.isclose(float(clearance["value"]), 0.015, abs_tol=1e-9))

    def test_nectar_does_not_nominally_fit_retrieval_height(self) -> None:
        rows = t04_intake.rows(self.inputs)
        interference = next(row for row in rows if row["claim_id"] == "INT-003")
        self.assertLess(float(interference["value"]), 0.0)

    def test_flower_roller_speed_range(self) -> None:
        diameter = self.inputs["mechanism"]["roller_diameter_m"]
        self.assertTrue(math.isclose(t04_intake.surface_speed(diameter, 80), 0.251327, abs_tol=1e-6))
        self.assertTrue(math.isclose(t04_intake.surface_speed(diameter, 160), 0.502655, abs_tol=1e-6))

    def test_side_sweep_ideal_step_bound(self) -> None:
        rows = t04_intake.rows(self.inputs)
        run = next(row for row in rows if row["claim_id"] == "INT-015")
        force_ratio = next(row for row in rows if row["claim_id"] == "INT-016")
        self.assertTrue(math.isclose(float(run["value"]), 0.0275, abs_tol=5e-5))
        self.assertTrue(math.isclose(float(force_ratio["value"]), 1.2206, abs_tol=5e-4))

    def test_side_sweep_stroke_exceeds_ideal_step_run(self) -> None:
        radius = self.inputs["gamepiece"]["pollen_nominal_diameter_m"] / 2.0
        step = self.inputs["flower"]["bottom_ring_thickness_m"]
        run = t04_intake.circle_step_horizontal_run(radius, step)
        minimum_stroke = self.inputs["side_sweep_mechanism"]["paddle_sweep_stroke_m_range"][0]
        self.assertGreater(minimum_stroke, run)

    def test_true_side_exit_is_not_modelled_as_legal_candidate(self) -> None:
        constraint = self.inputs["side_sweep_mechanism"]["exit_path_constraint"]
        self.assertEqual(
            constraint,
            "ball_must_remain_in_bottom_retrieval_opening_until_clear_of_flower",
        )

    def test_trade_scores_are_reproducible_but_not_rule_gates(self) -> None:
        self.assertTrue(math.isclose(t04_intake.weighted_trade_score(self.inputs, "C04-A"), 3.05))
        self.assertTrue(math.isclose(t04_intake.weighted_trade_score(self.inputs, "C04-B1"), 3.45))
        self.assertIn("G418", self.inputs["trade_study"]["hard_gate"])


if __name__ == "__main__":
    unittest.main()
