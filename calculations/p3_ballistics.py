"""P3-BAL-0.1: lightweight ballistic and wheel-speed screening model.

This is a Level-2 numerical model. It does not model drag, spin, ball
deformation, or HIVE motion. Inputs are centralized in p3_launcher_inputs.json.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from typing import TextIO


INPUT_PATH = Path(__file__).with_name("p3_launcher_inputs.json")
FIELDNAMES = (
    "model_version",
    "launch_height_m",
    "requires_deployment",
    "horizontal_distance_m",
    "launch_angle_deg",
    "status",
    "required_exit_speed_m_s",
    "flight_time_s",
    "entry_angle_deg",
    "apex_height_m",
    "specific_kinetic_energy_j_kg",
    "wheel_rpm_96mm_at_nominal_ratio",
    "wheel_rpm_120mm_at_nominal_ratio",
)


def load_inputs(path: Path = INPUT_PATH) -> dict:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def solve_trajectory(
    gravity: float,
    launch_height: float,
    target_height: float,
    distance: float,
    launch_angle_deg: float,
) -> dict[str, float] | None:
    angle = math.radians(launch_angle_deg)
    height_delta = target_height - launch_height
    denominator = 2 * math.cos(angle) ** 2 * (
        distance * math.tan(angle) - height_delta
    )
    if denominator <= 0:
        return None
    speed = math.sqrt(gravity * distance**2 / denominator)
    horizontal_speed = speed * math.cos(angle)
    flight_time = distance / horizontal_speed
    vertical_speed_at_target = speed * math.sin(angle) - gravity * flight_time
    entry_angle = math.degrees(
        math.atan2(vertical_speed_at_target, horizontal_speed)
    )
    apex_height = launch_height + (speed * math.sin(angle)) ** 2 / (2 * gravity)
    return {
        "required_exit_speed_m_s": speed,
        "flight_time_s": flight_time,
        "entry_angle_deg": entry_angle,
        "apex_height_m": apex_height,
        "specific_kinetic_energy_j_kg": 0.5 * speed**2,
    }


def wheel_rpm(ball_speed: float, wheel_diameter: float, speed_ratio: float) -> float:
    surface_speed = ball_speed / speed_ratio
    return 60 * surface_speed / (math.pi * wheel_diameter)


def generate_rows(inputs: dict) -> list[dict[str, str | float]]:
    study = inputs["study"]
    target_height = inputs["target"]["aim_height_m"]
    gravity = inputs["gravity_m_s2"]
    speed_ratio = study["nominal_ball_to_wheel_speed_ratio"]
    starting_height = inputs["robot"]["starting_max_height_m"]
    wheel_diameters = study["wheel_diameters_m"]
    assert wheel_diameters == [0.096, 0.12]

    rows: list[dict[str, str | float]] = []
    for launch_height in study["launch_heights_m"]:
        for distance in study["horizontal_distances_m"]:
            for angle in study["launch_angles_deg"]:
                solved = solve_trajectory(
                    gravity, launch_height, target_height, distance, angle
                )
                row: dict[str, str | float] = {
                    "model_version": inputs["model_version"],
                    "launch_height_m": launch_height,
                    "requires_deployment": str(launch_height > starting_height).lower(),
                    "horizontal_distance_m": distance,
                    "launch_angle_deg": angle,
                }
                if solved is None:
                    row.update(
                        {
                            "status": "INFEASIBLE_AT_THIS_ANGLE",
                            **{field: "" for field in FIELDNAMES[6:]},
                        }
                    )
                else:
                    speed = solved["required_exit_speed_m_s"]
                    row.update(
                        {
                            "status": "CALCULATED_VACUUM_MODEL",
                            **{key: round(value, 4) for key, value in solved.items()},
                            "wheel_rpm_96mm_at_nominal_ratio": round(
                                wheel_rpm(speed, wheel_diameters[0], speed_ratio), 1
                            ),
                            "wheel_rpm_120mm_at_nominal_ratio": round(
                                wheel_rpm(speed, wheel_diameters[1], speed_ratio), 1
                            ),
                        }
                    )
                rows.append(row)
    return rows


def write_csv(rows: list[dict[str, str | float]], stream: TextIO) -> None:
    writer = csv.DictWriter(stream, fieldnames=FIELDNAMES, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)


def validate_inputs(inputs: dict) -> None:
    assert inputs["gravity_m_s2"] > 0
    target = inputs["target"]
    max_ball = inputs["gamepiece"]["nectar_nominal_diameter_m"]
    assert target["opening_width_m"] > max_ball
    assert target["rectangular_opening_height_m"] > max_ball
    expected_aim = target["bottom_edge_height_m"] + 0.5 * target[
        "rectangular_opening_height_m"
    ]
    assert math.isclose(target["aim_height_m"], expected_aim, abs_tol=1e-9)
    for height in inputs["study"]["launch_heights_m"]:
        assert 0 < height <= inputs["robot"]["operating_max_height_m"]
    ratio = inputs["study"]["nominal_ball_to_wheel_speed_ratio"]
    assert 0 < ratio <= 1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    inputs = load_inputs()
    validate_inputs(inputs)
    rows = generate_rows(inputs)
    if args.output:
        with args.output.open("w", encoding="utf-8", newline="") as stream:
            write_csv(rows, stream)
    else:
        write_csv(rows, sys.stdout)


if __name__ == "__main__":
    main()
