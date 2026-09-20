"""TS-S00-001: deterministic task-package screening calculation.

Inputs are engineering judgments, not measured robot performance. Scores use a
1..5 ordinal scale where 5 is favorable. The script validates the model and
prints CSV so results can be reproduced without third-party packages.
"""

from __future__ import annotations

import csv
import sys


CRITERIA = (
    "strategic_value",
    "reliability",
    "development_risk",
    "integration_simplicity",
    "mass_volume_efficiency",
    "power_actuator_efficiency",
    "operator_software_simplicity",
    "growth_modularity",
)

SCENARIOS = {
    "neutral": (25, 20, 15, 10, 10, 5, 10, 5),
    "score_first": (40, 15, 10, 5, 5, 5, 10, 10),
    "reliability_first": (15, 35, 15, 10, 10, 5, 5, 5),
    "resource_limited": (15, 20, 25, 15, 10, 5, 5, 5),
}

# ASSUMED v0.1 scores. For risk/complexity criteria, a higher score means the
# package is less risky, simpler, or more efficient.
PACKAGES = {
    "P1": (2, 5, 5, 5, 5, 5, 5, 3),
    "P2": (3, 4, 3, 4, 4, 4, 3, 4),
    "P3": (5, 3, 3, 3, 4, 3, 3, 4),
    "P4": (5, 2, 1, 1, 1, 1, 1, 5),
}


def validate() -> None:
    assert len(set(CRITERIA)) == len(CRITERIA)
    for name, weights in SCENARIOS.items():
        assert len(weights) == len(CRITERIA), name
        assert sum(weights) == 100, name
        assert all(weight >= 0 for weight in weights), name
    for name, scores in PACKAGES.items():
        assert len(scores) == len(CRITERIA), name
        assert all(1 <= score <= 5 for score in scores), name


def weighted_score(weights: tuple[int, ...], scores: tuple[int, ...]) -> float:
    """Return normalized score on a 0..100 scale."""
    return sum(weight * score for weight, score in zip(weights, scores)) / 5


def results() -> list[tuple[str, str, float, int]]:
    rows = []
    for scenario, weights in SCENARIOS.items():
        ranked = sorted(
            (
                (package, weighted_score(weights, scores))
                for package, scores in PACKAGES.items()
            ),
            key=lambda item: (-item[1], item[0]),
        )
        rows.extend(
            (scenario, package, score, rank)
            for rank, (package, score) in enumerate(ranked, start=1)
        )
    return rows


def main() -> None:
    validate()
    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(("scenario", "package", "score_0_to_100", "rank"))
    for scenario, package, score, rank in results():
        writer.writerow((scenario, package, f"{score:.1f}", rank))


if __name__ == "__main__":
    main()
