import math
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "calculations"))

import t04_flower_sweep  # noqa: E402


class T04FlowerSweepAnalyticalTests(unittest.TestCase):
    def test_pure_lateral_ray_conflicts_with_left_support(self) -> None:
        clearance = t04_flower_sweep.ray_circle_clearance_mm(
            0.0, -31.841, 46.316, 16.2525, 35.5
        )
        self.assertLess(clearance, 0.0)

    def test_25_degree_diagonal_ray_has_nominal_clearance(self) -> None:
        clearance = t04_flower_sweep.ray_circle_clearance_mm(
            25.0, -31.841, 46.316, 16.2525, 35.5
        )
        self.assertTrue(math.isclose(clearance, 3.67, abs_tol=0.05))

    def test_official_cad_hash_is_registered(self) -> None:
        inputs = t04_flower_sweep.load_inputs()
        self.assertEqual(len(inputs["official_flower_cad"]["sha256"]), 64)
        self.assertEqual(inputs["side_sweep_path"]["ball_heading_from_negative_x_deg"], 25.0)


if __name__ == "__main__":
    unittest.main()
