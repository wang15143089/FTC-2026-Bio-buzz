"""T01-DRIVE-TRADE-0.1: motor, resource, and lateral-task trade study.

This model separates facts that follow from motor count and ideal kinematics
from unknown wheel/floor and transmission efficiencies.  It does not assign an
unsupported efficiency percentage to mecanum or differential wheels.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from typing import TextIO


INPUT_PATH = Path(__file__).with_name("t01_drive_trade_inputs.json")
G0 = 9.80665
FIELDNAMES = (
    "row_id",
    "category",
    "metric",
    "case",
    "mecanum_4_motor",
    "differential_4_motor",
    "differential_2_motor",
    "unit",
    "status",
    "boundary",
)


def load_inputs(path: Path = INPUT_PATH) -> dict:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def motor_constants(motor: dict) -> dict[str, float]:
    voltage = motor["nominal_voltage_v"]
    no_load_current = motor["no_load_current_a"]
    stall_current = motor["stall_current_a"]
    stall_torque = motor["stall_torque_kg_cm"] * 0.0980665
    omega_free = motor["no_load_speed_rpm"] * 2.0 * math.pi / 60.0
    resistance = voltage / stall_current
    torque_constant = stall_torque / (stall_current - no_load_current)
    back_emf_constant = (voltage - no_load_current * resistance) / omega_free
    return {
        "stall_torque_nm": stall_torque,
        "omega_free_rad_s": omega_free,
        "resistance_ohm": resistance,
        "torque_constant_nm_a": torque_constant,
        "back_emf_constant_v_s_rad": back_emf_constant,
    }


def operating_point(
    motor: dict,
    motor_count: int,
    wheel_radius_m: float,
    ground_force_n: float,
    vehicle_speed_m_s: float,
) -> dict[str, float | bool]:
    c = motor_constants(motor)
    torque_each = ground_force_n * wheel_radius_m / motor_count
    torque_current = torque_each / c["torque_constant_nm_a"]
    current_each = motor["no_load_current_a"] + torque_current
    omega = vehicle_speed_m_s / wheel_radius_m
    required_voltage = (
        c["back_emf_constant_v_s_rad"] * omega
        + current_each * c["resistance_ohm"]
    )
    electrical_power = motor_count * required_voltage * current_each
    mechanical_power = ground_force_n * vehicle_speed_m_s
    return {
        "current_each_a": current_each,
        "total_current_a": motor_count * current_each,
        "required_voltage_v": required_voltage,
        "electrical_power_w": electrical_power,
        "mechanical_power_w": mechanical_power,
        "model_efficiency": mechanical_power / electrical_power,
        "feasible_at_12v": required_voltage <= motor["nominal_voltage_v"]
        and current_each <= motor["stall_current_a"],
    }


def peak_metrics(motor: dict, motor_count: int, wheel_radius_m: float) -> dict[str, float]:
    c = motor_constants(motor)
    no_load_speed = c["omega_free_rad_s"] * wheel_radius_m
    stall_force = motor_count * c["stall_torque_nm"] / wheel_radius_m
    max_mechanical_power = (
        motor_count * c["stall_torque_nm"] * c["omega_free_rad_s"] / 4.0
    )
    return {
        "no_load_speed_m_s": no_load_speed,
        "stall_force_n": stall_force,
        "force_at_max_power_n": stall_force / 2.0,
        "max_mechanical_power_w": max_mechanical_power,
        "no_load_current_a": motor_count * motor["no_load_current_a"],
        "motor_mass_kg": motor_count * motor["mass_kg"],
    }


def preserved_heading_break_even_strafe_fraction(
    lateral_displacement_m: float, track_width_m: float
) -> float:
    """Mecanum strafe-speed fraction that ties rotate-drive-rotate time.

    Both candidates use the same forward/no-load wheel speed. Differential
    drive turns 90 deg, drives laterally, then restores its original heading.
    Acceleration and scrub are omitted.
    """

    return lateral_displacement_m / (
        lateral_displacement_m + math.pi * track_width_m / 2.0
    )


def ideal_one_meter_time(
    mass_kg: float, motor_count: int, wheel_radius_m: float, motor: dict
) -> float:
    """Solve an ideal 1 m straight sprint under a linear force-speed curve."""

    peak = peak_metrics(motor, motor_count, wheel_radius_m)
    v_free = peak["no_load_speed_m_s"]
    tau = mass_kg * v_free / peak["stall_force_n"]

    def distance(time_s: float) -> float:
        return v_free * (time_s - tau * (1.0 - math.exp(-time_s / tau)))

    lo, hi = 0.0, 5.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if distance(mid) < 1.0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def make_row(
    row_id: str,
    category: str,
    metric: str,
    case: str,
    mecanum: str | float,
    differential_4: str | float,
    differential_2: str | float,
    unit: str,
    status: str,
    boundary: str,
) -> dict[str, str]:
    def fmt(value: str | float) -> str:
        return value if isinstance(value, str) else f"{value:.4f}"

    return {
        "row_id": row_id,
        "category": category,
        "metric": metric,
        "case": case,
        "mecanum_4_motor": fmt(mecanum),
        "differential_4_motor": fmt(differential_4),
        "differential_2_motor": fmt(differential_2),
        "unit": unit,
        "status": status,
        "boundary": boundary,
    }


def rows(inputs: dict) -> list[dict[str, str]]:
    motor = inputs["drive_motor"]
    chassis = inputs["current_chassis"]
    conversion = inputs["representative_differential_conversion"]
    r_current = chassis["mecanum_wheel_diameter_m"] / 2.0
    r_diff = conversion["wheel_diameter_m"] / 2.0
    p4 = peak_metrics(motor, 4, r_current)
    p2_same_wheel = peak_metrics(motor, 2, r_current)
    p2_conversion = peak_metrics(motor, 2, r_diff)

    result = [
        make_row("DRV-001", "resources", "drive motor ports", "architecture", 4, 4, 2, "count", "CALCULATED", "Only the 2-motor differential architecture releases ports"),
        make_row("DRV-002", "resources", "ports released versus baseline", "architecture", 0, 0, 2, "count", "CALCULATED", "R503 whole-robot limit remains 8"),
        make_row("DRV-003", "resources", "drive-motor mass", "motors only", p4["motor_mass_kg"], p4["motor_mass_kg"], p2_same_wheel["motor_mass_kg"], "kg", "CALCULATED_FROM_KNOWN_VENDOR", "Excludes chain/belt, sprockets, tensioners, guards, and wheel change"),
        make_row("DRV-004", "motor", "ideal maximum mechanical power", "motor shafts", p4["max_mechanical_power_w"], p4["max_mechanical_power_w"], p2_same_wheel["max_mechanical_power_w"], "W", "CALCULATED_LINEAR_MOTOR_MODEL", "Before wheel/transmission losses and thermal limits"),
        make_row("DRV-005", "motor", "ideal stall force", "104 mm direct wheel", p4["stall_force_n"], p4["stall_force_n"], p2_same_wheel["stall_force_n"], "N", "CALCULATED_LINEAR_MOTOR_MODEL", "Not a permitted continuous operating point; tire traction may cap lower"),
        make_row("DRV-006", "motor", "force at ideal maximum-power point", "104 mm direct wheel", p4["force_at_max_power_n"], p4["force_at_max_power_n"], p2_same_wheel["force_at_max_power_n"], "N", "CALCULATED_LINEAR_MOTOR_MODEL", "At one-half no-load wheel speed"),
        make_row("DRV-007", "motor", "no-load vehicle speed", "104 mm direct wheel", p4["no_load_speed_m_s"], p4["no_load_speed_m_s"], p2_same_wheel["no_load_speed_m_s"], "m/s", "CALCULATED", "Real speed lower"),
        make_row("DRV-008", "electrical", "aggregate no-load current", "12 V", p4["no_load_current_a"], p4["no_load_current_a"], p2_same_wheel["no_load_current_a"], "A", "CALCULATED_FROM_KNOWN_VENDOR", "Two motors save 0.5 A only near no load"),
        make_row("DRV-009", "mass", "gross mass reduction", "2 motors removed", 0, 0, 2 * motor["mass_kg"], "kg", "CALCULATED_LOWER_BOUND", "Before adding a cross-drive transmission"),
        make_row("DRV-010", "mass", "gross mass reduction", "2 motors removed + four reference 96 mm traction wheels", 0, 4 * (chassis["mecanum_wheel_mass_kg_each"] - conversion["wheel_mass_kg_each"]), 2 * motor["mass_kg"] + 4 * (chassis["mecanum_wheel_mass_kg_each"] - conversion["wheel_mass_kg_each"]), "kg", "CALCULATED_REFERENCE_ONLY", "Not net savings; 96 mm wheel and transmission are not selected"),
        make_row("DRV-011", "speed", "no-load speed with reference 96 mm wheel", "312 rpm direct wheel", p4["no_load_speed_m_s"], peak_metrics(motor, 4, r_diff)["no_load_speed_m_s"], p2_conversion["no_load_speed_m_s"], "m/s", "CALCULATED_REFERENCE_ONLY", "Wheel swap reduces nominal speed 7.69 percent"),
    ]

    row_number = 12
    for force in inputs["study"]["ground_force_cases_n"]:
        v = inputs["study"]["vehicle_speed_case_m_s"]
        op4 = operating_point(motor, 4, r_current, force, v)
        op2 = operating_point(motor, 2, r_current, force, v)
        result.append(
            make_row(
                f"DRV-{row_number:03d}",
                "operating_point",
                "electrical power at equal force and speed",
                f"{force:.0f} N at {v:.1f} m/s, ideal 104 mm wheel",
                op4["electrical_power_w"],
                op4["electrical_power_w"],
                op2["electrical_power_w"] if op2["feasible_at_12v"] else f"INFEASIBLE_{op2['required_voltage_v']:.2f}V",
                "W",
                "CALCULATED_LINEAR_MOTOR_MODEL",
                "Excludes external drivetrain losses; required voltage must not exceed 12 V",
            )
        )
        row_number += 1

    for mass in inputs["study"]["robot_mass_sweep_kg"]:
        t4 = ideal_one_meter_time(mass, 4, r_current, motor)
        t2 = ideal_one_meter_time(mass, 2, r_current, motor)
        result.append(
            make_row(
                f"DRV-{row_number:03d}",
                "transient",
                "ideal 1 m straight sprint",
                f"{mass:.0f} kg robot",
                t4,
                t4,
                t2,
                "s",
                "CALCULATED_IDEAL_SENSITIVITY",
                "No traction cap, losses, battery sag, or current limiting",
            )
        )
        row_number += 1

    for track in inputs["study"]["track_width_sweep_m"]:
        for lateral in inputs["study"]["lateral_displacement_sweep_m"]:
            threshold = preserved_heading_break_even_strafe_fraction(lateral, track)
            result.append(
                make_row(
                    f"DRV-{row_number:03d}",
                    "maneuver",
                    "mecanum strafe-speed fraction needed to beat differential rotate-drive-rotate",
                    f"track {track:.3f} m, lateral {lateral:.2f} m",
                    threshold,
                    "N/A_NO_STRAFE",
                    "N/A_NO_STRAFE",
                    "fraction_of_forward_speed",
                    "CALCULATED_IDEAL_KINEMATICS",
                    "Same forward speed; final heading preserved; excludes acceleration and turn scrub",
                )
            )
            row_number += 1
    return result


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
