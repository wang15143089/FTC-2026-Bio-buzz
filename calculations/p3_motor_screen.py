"""P3-MOT-0.1: no-load surface-speed screen for launcher motors.

This is not a motor selection. It rejects obviously slow direct-drive options
and identifies candidates for an instrumented prototype. Loaded speed, current,
thermal behavior, slip, and recovery remain to be measured.
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path
from typing import TextIO

import p3_ballistics


FIELDNAMES = (
    "sku",
    "no_load_rpm",
    "wheel_diameter_mm",
    "no_load_surface_speed_m_s",
    "estimated_ball_speed_m_s_at_nominal_ratio",
    "ideal_linear_curve_max_power_w",
    "stall_current_a",
    "screen_result",
    "status",
)


def generate_rows(inputs: dict) -> list[dict[str, str | float | int]]:
    ratio = inputs["study"]["nominal_ball_to_wheel_speed_ratio"]
    rows: list[dict[str, str | float | int]] = []
    for motor in inputs["motor_candidates"]:
        for diameter in inputs["study"]["wheel_diameters_m"]:
            surface_speed = math.pi * diameter * motor["no_load_rpm"] / 60
            ball_speed = ratio * surface_speed
            stall_torque_nm = motor["stall_torque_kg_cm"] * 0.0980665
            no_load_speed_rad_s = motor["no_load_rpm"] * 2 * math.pi / 60
            ideal_max_power = stall_torque_nm * no_load_speed_rad_s / 4
            if ball_speed < 5.2:
                screen_result = "FAIL_DIRECT_DRIVE"
            elif ball_speed < 5.6:
                screen_result = "MARGINAL_SHOT_DEPENDENT"
            elif ball_speed <= 7.0:
                screen_result = "PASS_PROTOTYPE_RANGE"
            else:
                screen_result = "OVERSPEED_REDUCTION_REQUIRED"
            rows.append(
                {
                    "sku": motor["sku"],
                    "no_load_rpm": motor["no_load_rpm"],
                    "wheel_diameter_mm": round(diameter * 1000, 1),
                    "no_load_surface_speed_m_s": round(surface_speed, 3),
                    "estimated_ball_speed_m_s_at_nominal_ratio": round(ball_speed, 3),
                    "ideal_linear_curve_max_power_w": round(ideal_max_power, 2),
                    "stall_current_a": motor["stall_current_a"],
                    "screen_result": screen_result,
                    "status": "CALCULATED_WITH_ASSUMED_SPEED_RATIO",
                }
            )
    return rows


def write_csv(rows: list[dict[str, str | float | int]], stream: TextIO) -> None:
    writer = csv.DictWriter(stream, fieldnames=FIELDNAMES, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    inputs = p3_ballistics.load_inputs()
    p3_ballistics.validate_inputs(inputs)
    rows = generate_rows(inputs)
    if args.output:
        with args.output.open("w", encoding="utf-8", newline="") as stream:
            write_csv(rows, stream)
    else:
        write_csv(rows, sys.stdout)


if __name__ == "__main__":
    main()
