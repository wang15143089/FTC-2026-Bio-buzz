"""Reproducible checks for the KEI-16 COTS single-motor flip-out intake.

The motor/vendor values are KNOWN from linked official product pages.  Losses,
spring loads, current alert, and clutch setting are ASSUMED prototype limits.
The output is therefore CALCULATED_FROM_VENDOR_SPEC_AND_ASSUMPTIONS, not a
physical performance claim.
"""

from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
INPUT_PATH = ROOT / "kei16_flipout_drive_inputs.json"
OUTPUT_PATH = ROOT / "kei16_flipout_drive_results.json"
KG_CM_TO_NM = 0.0980665


def belt_length(center_mm: float, pitch_d1_mm: float, pitch_d2_mm: float) -> float:
    return (
        2.0 * center_mm
        + math.pi * (pitch_d1_mm + pitch_d2_mm) / 2.0
        + (pitch_d2_mm - pitch_d1_mm) ** 2 / (4.0 * center_mm)
    )


def solve_belt_center(length_mm: float, pitch_d1_mm: float, pitch_d2_mm: float) -> float:
    low = max(pitch_d1_mm, pitch_d2_mm) / 2.0
    high = length_mm / 2.0
    for _ in range(100):
        mid = (low + high) / 2.0
        if belt_length(mid, pitch_d1_mm, pitch_d2_mm) < length_mm:
            low = mid
        else:
            high = mid
    return (low + high) / 2.0


def spring_moment_arm_m(angle_deg: float, attach_radius_mm: float, anchor_mm: tuple[float, float]) -> tuple[float, float]:
    angle = math.radians(angle_deg)
    arm = (attach_radius_mm * math.cos(angle), attach_radius_mm * math.sin(angle))
    spring = (anchor_mm[0] - arm[0], anchor_mm[1] - arm[1])
    length = math.hypot(*spring)
    unit = (spring[0] / length, spring[1] / length)
    moment_arm_mm = arm[0] * unit[1] - arm[1] * unit[0]
    return moment_arm_mm / 1000.0, length


def calculate(data: dict) -> dict:
    motor = data["motor"]
    miter = data["miter_stage"]
    chain = data["fixed_roller_chain"]
    belt = data["front_bar_belt"]
    geo = data["geometry"]
    servo = data["latch_servo"]
    protection = data["protection"]

    miter_ratio = miter["driver_teeth"] / miter["driven_teeth"]
    roller_rpm = motor["no_load_speed_rpm"] * miter_ratio
    roller_surface_speed = math.pi * (geo["fixed_roller_diameter_mm"] / 1000.0) * roller_rpm / 60.0

    motor_stall_torque = motor["stall_torque_kg_cm"] * KG_CM_TO_NM
    current_fraction = (
        motor["software_current_alert_a"] - motor["no_load_current_a"]
    ) / (motor["stall_current_a"] - motor["no_load_current_a"])
    estimated_motor_torque_at_alert = motor_stall_torque * current_fraction
    primary_torque_at_alert = estimated_motor_torque_at_alert * miter_ratio * miter["assumed_efficiency"]

    sprocket_pitch_radius_m = chain["sprocket_teeth"] * chain["pitch_mm"] / (2.0 * math.pi * 1000.0)
    chain_center = (chain["chain_links_per_stage"] - chain["sprocket_teeth"]) * chain["pitch_mm"] / 2.0
    chain_tension_at_alert = primary_torque_at_alert / sprocket_pitch_radius_m

    d1 = belt["driver_teeth"] * belt["pitch_mm"] / math.pi
    d2 = belt["driven_teeth"] * belt["pitch_mm"] / math.pi
    belt_center = solve_belt_center(belt["belt_pitch_length_mm"], d1, d2)
    wrap_small_rad = math.pi - 2.0 * math.asin((d2 - d1) / (2.0 * belt_center))
    teeth_in_mesh = belt["driver_teeth"] * wrap_small_rad / (2.0 * math.pi)
    front_ratio = belt["driver_teeth"] / belt["driven_teeth"]
    front_rpm = roller_rpm * front_ratio
    front_tip_speed = 2.0 * math.pi * (geo["finger_tip_radius_mm"] / 1000.0) * front_rpm / 60.0
    front_torque_at_alert = primary_torque_at_alert * (belt["driven_teeth"] / belt["driver_teeth"]) * belt["assumed_efficiency"]
    front_tip_force_at_alert = front_torque_at_alert / (geo["finger_tip_radius_mm"] / 1000.0)

    anchor = tuple(geo["spring_chassis_anchor_relative_mm"])
    stowed_arm, stowed_length = spring_moment_arm_m(
        geo["stowed_angle_deg"], geo["spring_arm_attachment_radius_mm"], anchor
    )
    deployed_arm, deployed_length = spring_moment_arm_m(
        geo["deployed_angle_deg"], geo["spring_arm_attachment_radius_mm"], anchor
    )
    stowed_deploy_torque = stowed_arm * geo["stowed_spring_force_each_n"] * geo["spring_count"]
    deployed_hold_torque = deployed_arm * geo["deployed_spring_force_each_n"] * geo["spring_count"]
    deployed_tip_downforce = deployed_hold_torque / (belt_center / 1000.0)

    latch_force_total = stowed_deploy_torque / (geo["latch_catch_radius_mm"] / 1000.0)
    latch_release_torque = (
        latch_force_total * (geo["latch_contact_offset_mm"] / 1000.0) + geo["latch_return_torque_nm"]
    )
    latch_link_force = latch_release_torque / (geo["servo_crank_radius_mm"] / 1000.0)
    servo_stall_torque = servo["stall_torque_kg_cm_at_6v"] * KG_CM_TO_NM
    servo_stall_fraction = latch_release_torque / servo_stall_torque

    checks = {
        "fixed_chain_center_matches_96mm": abs(chain_center - 96.0) <= 0.1,
        "front_belt_center_is_near_180mm": abs(belt_center - 180.0) <= 0.5,
        "small_pulley_has_minimum_teeth_in_mesh": teeth_in_mesh >= protection["minimum_small_pulley_teeth_in_mesh"],
        "spring_torque_deploys_at_both_endpoints": stowed_deploy_torque > 0 and deployed_hold_torque > 0,
        "servo_static_release_below_target_stall_fraction": servo_stall_fraction <= protection["maximum_servo_stall_fraction_for_static_release"],
        "software_alert_precedes_motor_stall": motor["software_current_alert_a"] < motor["stall_current_a"],
        "mechanical_slip_target_not_above_calculated_alert_torque_plus_tolerance": protection["target_primary_slip_torque_nm"] <= primary_torque_at_alert + protection["target_primary_slip_tolerance_nm"]
    }

    return {
        "design_version": data["design_version"],
        "result_status": "CALCULATED_FROM_VENDOR_SPEC_AND_ASSUMPTIONS",
        "fixed_drive": {
            "roller_rpm_no_load": round(roller_rpm, 3),
            "roller_surface_speed_mps_no_load": round(roller_surface_speed, 3),
            "motor_stall_torque_nm": round(motor_stall_torque, 3),
            "estimated_motor_torque_at_current_alert_nm": round(estimated_motor_torque_at_alert, 3),
            "estimated_primary_torque_at_current_alert_nm": round(primary_torque_at_alert, 3),
            "chain_center_distance_mm": round(chain_center, 3),
            "chain_tension_at_current_alert_n": round(chain_tension_at_alert, 1)
        },
        "front_bar_drive": {
            "pulley_pitch_diameters_mm": [round(d1, 3), round(d2, 3)],
            "calculated_center_distance_mm": round(belt_center, 3),
            "small_pulley_wrap_deg": round(math.degrees(wrap_small_rad), 2),
            "small_pulley_teeth_in_mesh": round(teeth_in_mesh, 2),
            "front_bar_rpm_no_load": round(front_rpm, 3),
            "finger_tip_speed_mps_no_load": round(front_tip_speed, 3),
            "front_torque_at_current_alert_nm_if_full_primary_torque_routes_to_front": round(front_torque_at_alert, 3),
            "finger_tip_force_at_current_alert_n_if_full_primary_torque_routes_to_front": round(front_tip_force_at_alert, 1)
        },
        "deployment": {
            "spring_lengths_mm": {"stowed": round(stowed_length, 2), "deployed": round(deployed_length, 2)},
            "spring_moment_arms_mm": {"stowed": round(stowed_arm * 1000.0, 2), "deployed": round(deployed_arm * 1000.0, 2)},
            "deploy_torque_stowed_nm": round(stowed_deploy_torque, 3),
            "hold_torque_deployed_nm": round(deployed_hold_torque, 3),
            "estimated_deployed_tip_downforce_n": round(deployed_tip_downforce, 1),
            "estimated_total_latch_force_n": round(latch_force_total, 1),
            "estimated_latch_release_torque_nm": round(latch_release_torque, 3),
            "estimated_servo_link_force_n": round(latch_link_force, 1),
            "servo_stall_torque_nm_at_6v": round(servo_stall_torque, 3),
            "servo_stall_fraction_for_static_release": round(servo_stall_fraction, 3)
        },
        "protection": {
            "software_current_alert_a": motor["software_current_alert_a"],
            "overcurrent_duration_ms": protection["overcurrent_duration_ms"],
            "mechanical_primary_slip_torque_nm": protection["target_primary_slip_torque_nm"],
            "mechanical_primary_slip_tolerance_nm": protection["target_primary_slip_tolerance_nm"]
        },
        "checks": checks,
        "all_checks_pass": all(checks.values())
    }


def main() -> None:
    data = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    result = calculate(data)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
