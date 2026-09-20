"""T04-INTAKE-0.3 nominal checks for C04-A and the C04-B1 side-sweep."""

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


def circle_step_horizontal_run(radius_m: float, step_height_m: float) -> float:
    """Horizontal run while a circle centre rises by an ideal step height."""
    if not 0 < step_height_m < 2 * radius_m:
        raise ValueError("step height must be between zero and the diameter")
    return math.sqrt(2 * radius_m * step_height_m - step_height_m**2)


def horizontal_push_force_ratio(radius_m: float, step_height_m: float) -> float:
    """Quasi-static horizontal force / weight at initial step climb."""
    run = circle_step_horizontal_run(radius_m, step_height_m)
    vertical_lever = radius_m - step_height_m
    if vertical_lever <= 0:
        raise ValueError("model requires step height below the radius")
    return run / vertical_lever


def ramp_path_for_lift(lift_m: float, face_angle_deg: float) -> float:
    if not 0 < face_angle_deg < 90:
        raise ValueError("face angle must be between zero and 90 degrees")
    return lift_m / math.sin(math.radians(face_angle_deg))


def weighted_trade_score(inputs: dict, candidate: str) -> float:
    return sum(
        criterion["weight"] * criterion[candidate]
        for criterion in inputs["trade_study"]["criteria"].values()
    )


def kg_cm_to_nm(torque_kg_cm: float) -> float:
    return torque_kg_cm * 0.0980665


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
    side = inputs["side_sweep_mechanism"]
    pollen_radius = pollen / 2.0
    ring_step = inputs["flower"]["bottom_ring_thickness_m"]
    step_run = circle_step_horizontal_run(pollen_radius, ring_step)
    push_ratio = horizontal_push_force_ratio(pollen_radius, ring_step)
    side_required_servo_torque = (
        side["design_contact_force_n"]
        * side["effective_force_lever_arm_m"]
        * side["structural_safety_factor"]
    )
    side_sweep_speed = side["paddle_sweep_stroke_m_range"][0] / side["nominal_sweep_time_s"]
    servo = inputs["side_sweep_servo"]
    servo_6v = servo["six_volt"]
    servo_74v = servo["seven_point_four_volt"]
    torque_6v_nm = kg_cm_to_nm(servo_6v["stall_torque_kg_cm"])
    torque_74v_nm = kg_cm_to_nm(servo_74v["stall_torque_kg_cm"])
    transmission_efficiency = servo["assumed_transmission_efficiency"]
    moving_fraction = servo["assumed_max_moving_fraction_of_stall"]
    required_output_torque_without_structural_sf = (
        side["design_contact_force_n"] * servo["nominal_output_arm_m"]
    )
    min_ratio_6v_moving = required_output_torque_without_structural_sf / (
        torque_6v_nm * transmission_efficiency * moving_fraction
    )
    min_ratio_6v_structural = side_required_servo_torque / (
        torque_6v_nm * transmission_efficiency
    )
    min_ratio_74v_moving = required_output_torque_without_structural_sf / (
        torque_74v_nm * transmission_efficiency * moving_fraction
    )
    ratio = servo["proposed_reduction_ratio"]
    nominal_output_angle_rad = servo["nominal_sweep_stroke_m"] / servo["nominal_output_arm_m"]
    nominal_servo_angle_deg = math.degrees(nominal_output_angle_rad) * ratio
    no_load_sweep_time_6v = servo_6v["speed_s_per_60_deg"] * nominal_servo_angle_deg / 60.0
    output_torque_at_moving_limit_6v = torque_6v_nm * transmission_efficiency * moving_fraction * ratio
    output_force_at_moving_limit_6v = output_torque_at_moving_limit_6v / servo["nominal_output_arm_m"]
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
        ("INT-014", "nominal POLLEN-to-ring diametric clearance", inputs["flower"]["bottom_ring_inner_diameter_m"] - pollen, "m", "CALCULATED_NOMINAL", "Zero nominal clearance means C04-B1 must lift or deform the ball before lateral translation"),
        ("INT-015", "ideal-step horizontal run to raise centre by ring thickness", step_run, "m", "CALCULATED_IDEAL_STEP", "Sphere/rigid-step proxy; not official contact geometry"),
        ("INT-016", "horizontal push force divided by ball weight at initial climb", push_ratio, "ratio", "CALCULATED_IDEAL_STEP", "Excludes friction, deformation, other balls and guide contact"),
        ("INT-017", "20 degree ramp path to lift by ring thickness", ramp_path_for_lift(ring_step, 20.0), "m", "CALCULATED_KINEMATIC", "Lower face-angle bound; must fit official bottom-opening sweep"),
        ("INT-018", "30 degree ramp path to lift by ring thickness", ramp_path_for_lift(ring_step, 30.0), "m", "CALCULATED_KINEMATIC", "Upper face-angle bound; must fit official bottom-opening sweep"),
        ("INT-019", "C04-B1 paddle torque check with safety factor", side_required_servo_torque, "N.m", "CALCULATED_FROM_ASSUMED_LOAD", "10 N contact force and 70 mm lever; actual linkage torque remains TBD"),
        ("INT-020", "C04-B1 minimum-stroke average paddle speed", side_sweep_speed, "m/s", "CALCULATED_FROM_ASSUMED_MOTION", "40 mm in 0.35 s; not a measured cycle time"),
        ("INT-021", "C04-B1 additional DC motors", side["powered_motor_count"], "count", "CALCULATED_FROM_PROPOSED_ARCHITECTURE", "Standard roller retains the existing shared T04/T05 motor"),
        ("INT-022", "C04-B1 nominal dedicated servos", side["servo_count_nominal"], "count", "PROPOSED", "One-DOF cam/arc sweep; use two only if deploy and sweep cannot be safely combined"),
        ("INT-023", "C04-A weighted evidence rating", weighted_trade_score(inputs, "C04-A"), "score/5", "ASSUMED_EVIDENCE_RATING", "Prototype-order aid only; rule gate cannot be offset by score"),
        ("INT-024", "C04-B1 weighted evidence rating", weighted_trade_score(inputs, "C04-B1"), "score/5", "ASSUMED_EVIDENCE_RATING", "Prototype-order aid only; nominal STEP passed, physical gate remains open"),
        ("INT-025", "servo 6 V stall torque", torque_6v_nm, "N.m", "CALCULATED_FROM_USER_SPEC", "Stall is not a continuous operating point; model ID/datasheet remain TBD"),
        ("INT-026", "servo 7.4 V stall torque", torque_74v_nm, "N.m", "CALCULATED_FROM_USER_SPEC", "7.4 V supply compatibility is not assumed"),
        ("INT-027", "minimum 6 V ratio for 10 N moving load", min_ratio_6v_moving, "ratio", "CALCULATED_FROM_ASSUMPTIONS", "Uses 50% stall and 80% transmission efficiency"),
        ("INT-028", "minimum 6 V ratio for 1.4 N.m structural check", min_ratio_6v_structural, "ratio", "CALCULATED_FROM_ASSUMPTIONS", "Uses full stall only as a short-duration strength boundary"),
        ("INT-029", "minimum 7.4 V ratio for 10 N moving load", min_ratio_74v_moving, "ratio", "CALCULATED_FROM_ASSUMPTIONS", "Comparison only; 7.4 V integration remains TBD"),
        ("INT-030", "proposed 3.2 ratio 6 V moving-limit output force", output_force_at_moving_limit_6v, "N", "CALCULATED_FROM_ASSUMPTIONS", "50% stall and 80% transmission efficiency"),
        ("INT-031", "nominal 55 mm sweep required servo rotation", nominal_servo_angle_deg, "deg", "CALCULATED_SMALL_ANGLE_ARC", "70 mm output arm and 3.2 ratio; linkage geometry remains preliminary"),
        ("INT-032", "nominal 55 mm sweep ideal no-load time at 6 V", no_load_sweep_time_6v, "s", "CALCULATED_FROM_USER_SPEC", "No-load lower bound; commanded prototype motion remains 0.25-0.40 s"),
        ("INT-033", "servo 6 V stall current", servo_6v["stall_current_a"], "A", "KNOWN_USER_PROVIDED", "Power rail transient capability and wiring remain TBD"),
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
    side = inputs["side_sweep_mechanism"]
    assert side["powered_motor_count"] == 0
    assert side["servo_count_nominal"] == 1
    assert side["paddle_sweep_stroke_m_range"][0] >= circle_step_horizontal_run(
        inputs["gamepiece"]["pollen_nominal_diameter_m"] / 2.0,
        inputs["flower"]["bottom_ring_thickness_m"],
    )
    criteria = inputs["trade_study"]["criteria"].values()
    assert math.isclose(sum(item["weight"] for item in criteria), 1.0)
    assert all(1.0 <= item[candidate] <= 5.0 for item in criteria for candidate in ("C04-A", "C04-B1"))
    servo = inputs["side_sweep_servo"]
    torque_6v_nm = kg_cm_to_nm(servo["six_volt"]["stall_torque_kg_cm"])
    efficiency = servo["assumed_transmission_efficiency"]
    moving_fraction = servo["assumed_max_moving_fraction_of_stall"]
    required_moving_torque = side["design_contact_force_n"] * servo["nominal_output_arm_m"]
    required_structural_torque = (
        required_moving_torque * side["structural_safety_factor"]
    )
    min_ratio_6v_moving = required_moving_torque / (
        torque_6v_nm * efficiency * moving_fraction
    )
    min_ratio_6v_structural = required_structural_torque / (
        torque_6v_nm * efficiency
    )
    assert servo["default_design_voltage_v"] == 6.0
    assert servo["proposed_reduction_ratio"] >= min_ratio_6v_moving
    assert servo["proposed_reduction_ratio"] >= min_ratio_6v_structural
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
