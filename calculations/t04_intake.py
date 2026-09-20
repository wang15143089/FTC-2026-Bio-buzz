"""T04-INTAKE-0.1 nominal geometry, speed, load, and resource checks."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from typing import TextIO


INPUT_PATH = Path(__file__).with_name("t04_intake_inputs.json")
FIELDNAMES = ("claim_id", "metric", "value", "unit", "status", "boundary")


def load_inputs(path: Path = INPUT_PATH) -> dict:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def surface_speed(roller_diameter_m: float, rpm: float) -> float:
    return math.pi * roller_diameter_m * rpm / 60.0


def rows(inputs: dict) -> list[dict[str, str]]:
    pollen = inputs["gamepiece"]["pollen_nominal_diameter_m"]
    nectar = inputs["gamepiece"]["nectar_nominal_diameter_m"]
    opening = inputs["flower"]["retrieval_opening_height_m"]
    m = inputs["mechanism"]
    motor = inputs["motor"]
    stall_torque_nm = motor["stall_torque_kg_cm"] * 0.0980665
    roller_radius = m["roller_diameter_m"] / 2.0
    roller_torque = m["design_extraction_force_n"] * roller_radius
    torque_fraction = roller_torque / stall_torque_nm
    estimated_current = motor["no_load_current_a"] + torque_fraction * (
        motor["stall_current_a"] - motor["no_load_current_a"]
    )
    required_servo_torque = (
        m["design_extraction_force_n"]
        * m["effective_force_lever_arm_m"]
        * m["structural_safety_factor"]
    )
    spring_force_limit = (
        m["series_spring_rate_n_m"] * m["series_spring_max_compression_m"]
    )
    resource = inputs["resource_architecture"]
    total_motors = (
        resource["drive_motors"]
        + resource["shared_intake_and_prefeed_motors"]
        + resource["dual_flywheel_motors"]
    )

    values = [
        ("INT-001", "POLLEN total vertical opening clearance", opening - pollen, "m", "CALCULATED_NOMINAL", "Does not include ball/field variation"),
        ("INT-002", "clearance remaining with rake above POLLEN", opening - pollen - m["rake_blade_thickness_m"], "m", "CALCULATED_NOMINAL", "Rake crosses above nominal ball before hook drop"),
        ("INT-003", "NECTAR nominal vertical interference", opening - nectar, "m", "CALCULATED_NOMINAL", "Negative value reinforces that bottom removal is POLLEN-only"),
        ("INT-004", "rake extension nominal versus opening depth", m["rake_extension_nominal_m"] - inputs["flower"]["retrieval_opening_depth_m"], "m", "CALCULATED_NOMINAL", "Near-equal nominal values require adjustable stop and CAD/field verification"),
        ("INT-005", "roller surface speed lower FLOWER setting", surface_speed(m["roller_diameter_m"], m["flower_mode_rpm"][0]), "m/s", "CALCULATED", "Commanded speed, not measured under load"),
        ("INT-006", "roller surface speed upper FLOWER setting", surface_speed(m["roller_diameter_m"], m["flower_mode_rpm"][1]), "m/s", "CALCULATED", "Commanded speed, not measured under load"),
        ("INT-007", "roller surface speed upper floor setting", surface_speed(m["roller_diameter_m"], m["floor_mode_rpm"][1]), "m/s", "CALCULATED", "312 rpm motor candidate at no load"),
        ("INT-008", "roller torque at assumed extraction force", roller_torque, "N.m", "CALCULATED_FROM_ASSUMED_LOAD", "10 N force limit at 30 mm radius"),
        ("INT-009", "estimated motor current at assumed extraction force", estimated_current, "A", "CALCULATED_LINEAR_MODEL", "Excludes losses; use only to seed current-limit testing"),
        ("INT-010", "minimum servo/linkage torque with safety factor", required_servo_torque, "N.m", "CALCULATED_FROM_ASSUMED_LOAD", "Actuator rating must be checked at actual servo voltage"),
        ("INT-011", "series spring force limit", spring_force_limit, "N", "CALCULATED", "0.5 N/mm over 20 mm; prevents rigid field loading"),
        ("INT-012", "whole-robot motor count", total_motors, "count", "CALCULATED_FROM_PROPOSED_ARCHITECTURE", "4 drive + 1 shared intake/prefeed + 2 shooter"),
        ("INT-013", "remaining legal motor ports", 8 - total_motors, "count", "CALCULATED", "R503 maximum 8 motors"),
    ]
    return [
        {
            "claim_id": claim,
            "metric": metric,
            "value": f"{value:.4f}",
            "unit": unit,
            "status": status,
            "boundary": boundary,
        }
        for claim, metric, value, unit, status, boundary in values
    ]


def validate(inputs: dict) -> None:
    m = inputs["mechanism"]
    assert m["powered_motor_count"] == 1
    assert m["servo_count"] == 2
    assert m["rake_blade_thickness_m"] > 0
    assert m["roller_vertical_compliance_m"] >= (
        inputs["gamepiece"]["nectar_nominal_diameter_m"]
        - inputs["gamepiece"]["pollen_nominal_diameter_m"]
    )
    assert m["series_spring_rate_n_m"] * m["series_spring_max_compression_m"] <= m["design_extraction_force_n"]
    resource = inputs["resource_architecture"]
    assert resource["drive_motors"] + resource["shared_intake_and_prefeed_motors"] + resource["dual_flywheel_motors"] <= 8


def write_csv(result: list[dict[str, str]], stream: TextIO) -> None:
    writer = csv.DictWriter(stream, fieldnames=FIELDNAMES, lineterminator="\n")
    writer.writeheader()
    writer.writerows(result)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    inputs = load_inputs()
    validate(inputs)
    result = rows(inputs)
    if args.output:
        with args.output.open("w", encoding="utf-8", newline="") as stream:
            write_csv(result, stream)
    else:
        write_csv(result, sys.stdout)


if __name__ == "__main__":
    main()
