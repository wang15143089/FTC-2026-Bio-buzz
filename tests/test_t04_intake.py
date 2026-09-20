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


if __name__ == "__main__":
    unittest.main()
