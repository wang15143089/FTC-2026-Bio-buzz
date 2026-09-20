"""P3-TS-001 v0.1: preliminary launcher concept comparison.

All scores are ASSUMED engineering judgments anchored to the evidence and
failure modes in docs/p3_hive_concept.md. They select prototypes, not hardware.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


CRITERIA = (
    "dual_size_tolerance",
    "shot_repeatability_potential",
    "adjustability",
    "cycle_and_recovery",
    "packaging",
    "motor_efficiency",
    "safety_serviceability",
    "precedent_maturity",
)
WEIGHTS = (30, 20, 15, 10, 5, 5, 10, 5)
CONCEPTS = {
    "C06-A_single_flywheel_hood": (2, 4, 4, 4, 5, 5, 3, 5),
    "C06-B_opposed_dual_flywheel": (4, 4, 4, 4, 3, 3, 3, 4),
    "C06-C_adjustable_catapult": (4, 3, 4, 2, 3, 4, 2, 3),
}


def validate() -> None:
    assert len(CRITERIA) == len(set(CRITERIA)) == len(WEIGHTS)
    assert sum(WEIGHTS) == 100
    for scores in CONCEPTS.values():
        assert len(scores) == len(CRITERIA)
        assert all(1 <= score <= 5 for score in scores)


def rows() -> list[dict[str, str | float | int]]:
    validate()
    ranked = sorted(
        (
            (name, sum(w * s for w, s in zip(WEIGHTS, scores)) / 5)
            for name, scores in CONCEPTS.items()
        ),
        key=lambda item: (-item[1], item[0]),
    )
    return [
        {
            "concept": name,
            "score_0_to_100": f"{score:.1f}",
            "rank": rank,
            "status": "ASSUMED_M1_PROTOTYPE_SCREEN",
        }
        for rank, (name, score) in enumerate(ranked, start=1)
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    fieldnames = ("concept", "score_0_to_100", "rank", "status")
    if args.output:
        stream = args.output.open("w", encoding="utf-8", newline="")
    else:
        stream = sys.stdout
    try:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows())
    finally:
        if args.output:
            stream.close()


if __name__ == "__main__":
    main()
