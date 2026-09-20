"""TS-S00-001 v0.2: evidence-anchored task-package screening.

The first four criteria are strategic and are anchored to BIOBUZZ TU01 point
values, RP routes, timing, and enabling effects. Engineering scores remain
explicit assumptions until calculations or prototypes replace them. Scores use
a 0..5 scale and may use 0.5 increments. Output is normalized to 0..100.
"""

from __future__ import annotations

import csv
import sys


CRITERIA = (
    "match_point_leverage",
    "ranking_point_leverage",
    "timing_and_enabling",
    "tactical_scope",
    "physical_feasibility",
    "reliability_recoverability",
    "integration_resource_burden",
    "operator_software_burden",
)

STRATEGIC_CRITERIA_COUNT = 4

# The default reflects the user's direction that strategic value dominate.
# The 60% and 80% cases test whether the recommendation is weight-sensitive.
SCENARIOS = {
    "strategy_70_default": (25, 25, 12, 8, 8, 8, 8, 6),
    "strategy_60_sensitivity": (22, 21, 10, 7, 11, 11, 10, 8),
    "strategy_80_sensitivity": (29, 29, 13, 9, 6, 5, 5, 4),
}

# Strategic scores are derived by the rubric in docs/task_package_trade_study.md.
# Engineering scores are ASSUMED evidence-anchored judgments, not measurements.
PACKAGES = {
    "P1": (1.5, 1.5, 3.0, 2.0, 5.0, 5.0, 5.0, 5.0),
    "P2": (3.0, 1.5, 3.0, 4.0, 3.5, 3.0, 3.5, 3.0),
    "P3": (5.0, 5.0, 5.0, 4.0, 2.5, 2.5, 3.0, 3.0),
    "P4": (5.0, 5.0, 5.0, 5.0, 1.5, 1.5, 1.0, 1.5),
}


def validate() -> None:
    assert len(set(CRITERIA)) == len(CRITERIA)
    for name, weights in SCENARIOS.items():
        assert len(weights) == len(CRITERIA), name
        assert sum(weights) == 100, name
        assert all(weight >= 0 for weight in weights), name
    assert sum(SCENARIOS["strategy_70_default"][:STRATEGIC_CRITERIA_COUNT]) == 70
    for name, scores in PACKAGES.items():
        assert len(scores) == len(CRITERIA), name
        assert all(0 <= score <= 5 for score in scores), name
        assert all(score * 2 == int(score * 2) for score in scores), name


def weighted_score(weights: tuple[int, ...], scores: tuple[float, ...]) -> float:
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
