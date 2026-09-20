"""P3-LAUNCHER-CMP-0.2: analytic launcher and shared-intake comparison.

The contact model is an ideal local two-plane, no-slip model.  It proves
kinematic relationships, not real launcher efficiency or accuracy.  FLOWER
geometry is nominal and does not include field/gamepiece variation.
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path
from typing import TextIO

from p3_ballistics import load_inputs, solve_trajectory


MODEL_VERSION = "P3-LAUNCHER-CMP-0.2"
FIELDNAMES = (
    "claim_id",
    "category",
    "metric",
    "c06_a_single_flywheel_hood",
    "c06_b_opposed_dual_flywheel",
    "unit",
    "status",
    "derivation_or_boundary",
)


def required_baseline_speed(inputs: dict) -> float:
    solved = solve_trajectory(
        inputs["gravity_m_s2"],
        0.4,
        inputs["target"]["aim_height_m"],
        1.5,
        55.0,
    )
    assert solved is not None
    return solved["required_exit_speed_m_s"]


def rpm(surface_speed_m_s: float, wheel_diameter_m: float) -> float:
    return 60.0 * surface_speed_m_s / (math.pi * wheel_diameter_m)


def ideal_contact_state(
    surface_speed_1_m_s: float,
    surface_speed_2_m_s: float,
    ball_radius_m: float,
) -> tuple[float, float]:
    """Return ball-center speed and spin from two no-slip contact surfaces.

    The signed surface velocities are expressed in the desired launch
    direction.  v + omega*r = u1 and v - omega*r = u2.
    """

    center_speed = 0.5 * (surface_speed_1_m_s + surface_speed_2_m_s)
    spin_rad_s = (surface_speed_1_m_s - surface_speed_2_m_s) / (
        2.0 * ball_radius_m
    )
    return center_speed, spin_rad_s


def comparison_rows(inputs: dict) -> list[dict[str, str]]:
    speed = required_baseline_speed(inputs)
    wheel_diameter = 0.12
    pollen_d = inputs["gamepiece"]["pollen_nominal_diameter_m"]
    nectar_d = inputs["gamepiece"]["nectar_nominal_diameter_m"]
    diameter_delta = nectar_d - pollen_d
    motor = next(
        item for item in inputs["motor_candidates"] if item["sku"] == "5203-2402-0003"
    )

    # A: moving wheel at 2v, stationary hood at 0.  B: both contacts at v.
    a_surface = 2.0 * speed
    b_surface = speed
    a_ball_speed, a_spin = ideal_contact_state(a_surface, 0.0, pollen_d / 2.0)
    b_ball_speed, b_spin = ideal_contact_state(b_surface, b_surface, pollen_d / 2.0)
    assert math.isclose(a_ball_speed, speed)
    assert math.isclose(b_ball_speed, speed)

    rows = [
        ("CMP-001", "kinematics", "ideal required surface speed", a_surface, b_surface, "m/s", "CALCULATED_IDEAL", "A: u=2v; B: u1=u2=v"),
        ("CMP-002", "kinematics", "ideal 120 mm wheel speed", rpm(a_surface, wheel_diameter), rpm(b_surface, wheel_diameter), "rpm", "CALCULATED_IDEAL", "60u/(pi*d_wheel)"),
        ("CMP-003", "kinematics", "ideal POLLEN spin magnitude", abs(a_spin), abs(b_spin), "rad/s", "CALCULATED_IDEAL", "omega=(u1-u2)/(2r); excludes slip and deformation"),
        ("CMP-004", "diameter", "fixed-gap compression change from 71 to 91 mm", diameter_delta * 1000.0, diameter_delta * 1000.0, "mm", "CALCULATED_NOMINAL", "compression=D-gap; fixed gap changes compression by delta-D"),
        ("CMP-005", "diameter", "exit-center shift with one-sided/symmetric gap adjustment", diameter_delta * 500.0, 0.0, "mm", "CALCULATED_LOCAL_GEOMETRY", "A fixed-wheel/moving-hood center shifts delta-D/2; B symmetric surfaces preserve center"),
        ("CMP-006", "resources", "whole-robot motor count", 7.0, 8.0, "count", "CALCULATED_FROM_ASSUMED_ARCHITECTURE", "4 drive + 1 intake + 1 transfer + launcher motors"),
        ("CMP-007", "resources", "remaining legal motor ports", 1.0, 0.0, "count", "CALCULATED", "R503 limit 8 minus CMP-006"),
        ("CMP-008", "resources", "minimum launcher motor mass delta B minus A", 0.0, motor["mass_kg"], "kg", "KNOWN_VENDOR_LOWER_BOUND", "one additional 5203-2402-0003; excludes mounts/wheel/wiring"),
        ("CMP-009", "resources", "additional no-load current B minus A", 0.0, motor["no_load_current_a"], "A", "KNOWN_VENDOR_LOWER_BOUND", "one additional motor at 12 V; loaded current is TBD_MEASURE"),
        ("CMP-010", "fault", "additional single-motor stall-current exposure B minus A", 0.0, motor["stall_current_a"], "A", "KNOWN_VENDOR_FAULT_BOUND", "not an allowable operating point"),
    ]
    return [
        {
            "claim_id": claim,
            "category": category,
            "metric": metric,
            "c06_a_single_flywheel_hood": f"{a:.4f}",
            "c06_b_opposed_dual_flywheel": f"{b:.4f}",
            "unit": unit,
            "status": status,
            "derivation_or_boundary": derivation,
        }
        for claim, category, metric, a, b, unit, status, derivation in rows
    ]


def flower_rows(inputs: dict) -> list[dict[str, str]]:
    flower = inputs["flower"]
    pollen = inputs["gamepiece"]["pollen_nominal_diameter_m"]
    nectar = inputs["gamepiece"]["nectar_nominal_diameter_m"]
    operating_height = inputs["robot"]["operating_max_height_m"]
    starting_height = inputs["robot"]["starting_max_height_m"]
    backstop_top = flower["top_opening_height_m"] + flower["backstop_height_m"]
    metrics = [
        ("FLW-001", "top opening radial clearance for POLLEN", (flower["top_opening_diameter_m"] - pollen) / 2, "m", "nominal only"),
        ("FLW-002", "top opening radial clearance for NECTAR", (flower["top_opening_diameter_m"] - nectar) / 2, "m", "nominal only; variation makes centering mandatory"),
        ("FLW-003", "bottom retrieval vertical clearance for POLLEN", flower["retrieval_opening_height_m"] - pollen, "m", "nominal only"),
        ("FLW-004", "bottom retrieval depth minus POLLEN diameter", flower["retrieval_opening_depth_m"] - pollen, "m", "nominal only"),
        ("FLW-005", "operating-height headroom above top ring", operating_height - flower["top_opening_height_m"], "m", "proves nominal vertical reach is not excluded"),
        ("FLW-006", "operating-height headroom above backstop top", operating_height - backstop_top, "m", "structure/ball still must fit"),
        ("FLW-007", "minimum rise from starting-height plane to top ring", flower["top_opening_height_m"] - starting_height, "m", "top placement requires deployment"),
        ("FLW-008", "minimum rise from starting-height plane to NECTAR center above ring", flower["top_opening_height_m"] + nectar / 2 - starting_height, "m", "kinematic lower bound, not mechanism stroke"),
    ]
    return [
        {
            "claim_id": claim,
            "category": "flower_shared_intake",
            "metric": metric,
            "c06_a_single_flywheel_hood": f"{value:.4f}",
            "c06_b_opposed_dual_flywheel": f"{value:.4f}",
            "unit": unit,
            "status": "CALCULATED_NOMINAL",
            "derivation_or_boundary": note,
        }
        for claim, metric, value, unit, note in metrics
    ]


def rows(inputs: dict) -> list[dict[str, str]]:
    return comparison_rows(inputs) + flower_rows(inputs)


def write_csv(result: list[dict[str, str]], stream: TextIO) -> None:
    writer = csv.DictWriter(stream, fieldnames=FIELDNAMES, lineterminator="\n")
    writer.writeheader()
    writer.writerows(result)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = rows(load_inputs())
    if args.output:
        with args.output.open("w", encoding="utf-8", newline="") as stream:
            write_csv(result, stream)
    else:
        write_csv(result, sys.stdout)


if __name__ == "__main__":
    main()
