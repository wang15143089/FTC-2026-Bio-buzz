"""COTS-constrained single-motor, spring-deployed BIOBUZZ intake.

M3 packaging model focused on the transmission and flip-out load path.
Purchased parts are functional envelopes, not production drawings. Units: mm.
+X points out of the robot, +Y is left, and +Z is upward.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import cadquery as cq
from cadquery import exporters

OUT = Path(__file__).resolve().parent / "output"
OUT.mkdir(parents=True, exist_ok=True)

DESIGN_VERSION = "KEI16-FLIPOUT-COTS-0.2"
MOUNT_WIDTH = 380.0
CLEAR_CAPTURE_WIDTH = 330.0
POLLEN_D, NECTAR_D = 71.0, 91.0
EXPANDED_LIMIT_X, EXPANDED_LIMIT_Y, EXPANDED_LIMIT_Z = 610.0, 457.2, 736.6

ROLLER_OD, ROLLER_FACE, SHAFT_D = 60.0, 318.0, 8.0
MOTOR_RPM = 312.0
MITER_DRIVER_TEETH = MITER_DRIVEN_TEETH = 24
MITER_RATIO = MITER_DRIVER_TEETH / MITER_DRIVEN_TEETH
CHAIN_PITCH, CHAIN_SPROCKET_TEETH, CHAIN_LINKS = 8.0, 14, 38
ROLLER_CENTER = (CHAIN_LINKS - CHAIN_SPROCKET_TEETH) * CHAIN_PITCH / 2.0
ROLLER_DX = 88.0
ROLLER_DZ = math.sqrt(ROLLER_CENTER**2 - ROLLER_DX**2)
FIXED_ROLLERS = tuple((25.0 + i * ROLLER_DX, 67.0 + i * ROLLER_DZ) for i in range(3))
PIVOT = FIXED_ROLLERS[0]

FRONT_DRIVER_TEETH, FRONT_DRIVEN_TEETH = 16, 24
FRONT_BELT_LENGTH, ARM_LENGTH = 460.0, 179.8873504
FRONT_PULLEY_RATIO = FRONT_DRIVER_TEETH / FRONT_DRIVEN_TEETH
DEPLOYED_ANGLE, STOWED_ANGLE = 198.0, 103.0
FINGER_COUNT, FINGER_LENGTH, FINGER_WIDTH, FINGER_THICKNESS = 13, 73.0, 18.0, 3.0

C = {
    "structure": cq.Color(0.68, 0.73, 0.80), "roller": cq.Color(0.12, 0.12, 0.14),
    "shaft": cq.Color(0.50, 0.54, 0.60), "sprocket": cq.Color(0.75, 0.76, 0.78),
    "pulley": cq.Color(0.92, 0.60, 0.10), "belt": cq.Color(0.06, 0.06, 0.07),
    "motor": cq.Color(0.94, 0.73, 0.12), "gear": cq.Color(0.78, 0.80, 0.84),
    "finger": cq.Color(0.92, 0.94, 0.96), "spring": cq.Color(0.20, 0.62, 0.92),
    "latch": cq.Color(0.86, 0.24, 0.16), "guide": cq.Color(0.20, 0.55, 0.82, 0.34),
    "datum": cq.Color(0.25, 0.28, 0.32, 0.18),
}


def box(x, y, z, center):
    return cq.Workplane("XY").box(x, y, z, centered=(True, True, True)).translate(center).val()


def cyl_y(radius, length, center):
    x, y, z = center
    return cq.Solid.makeCylinder(radius, length, cq.Vector(x, y - length / 2, z), cq.Vector(0, 1, 0))


def cyl_z(radius, length, center):
    x, y, z = center
    return cq.Solid.makeCylinder(radius, length, cq.Vector(x, y, z - length / 2), cq.Vector(0, 0, 1))


def rod(a, b, radius):
    av, bv = cq.Vector(*a), cq.Vector(*b)
    delta = bv - av
    return cq.Solid.makeCylinder(radius, delta.Length, av, delta.normalized())


def roller(center, face=ROLLER_FACE, radius=ROLLER_OD / 2):
    x, z = center
    shell = cyl_y(radius, face, (x, 0, z)).cut(cyl_y(radius - 5, face + 2, (x, 0, z)))
    hubs = cyl_y(15, face, (x, 0, z)).cut(cyl_y(SHAFT_D / 2 + 0.2, face + 2, (x, 0, z)))
    return shell.fuse(hubs)


def arm_plate(pivot, tip, y):
    px, pz = pivot
    tx, tz = tip
    base = rod((px, y, pz), (tx, y, tz), 10.0)
    eyes = cyl_y(18, 6, (px, y, pz)).fuse(cyl_y(18, 6, (tx, y, tz)))
    holes = cyl_y(6.2, 12, (px, y, pz)).fuse(cyl_y(4.2, 12, (tx, y, tz)))
    return base.fuse(eyes).cut(holes)


def pulley(center, y, teeth, width=9.0):
    pitch_d = teeth * 5.0 / math.pi
    return cyl_y(pitch_d / 2, width, (center[0], y, center[1])).cut(
        cyl_y(SHAFT_D / 2 + 0.2, width + 2, (center[0], y, center[1])))


def sprocket(center, y, teeth=CHAIN_SPROCKET_TEETH, width=7.0):
    pitch_d = teeth * CHAIN_PITCH / math.pi
    return cyl_y(pitch_d / 2, width, (center[0], y, center[1])).cut(
        cyl_y(SHAFT_D / 2 + 0.2, width + 2, (center[0], y, center[1])))


def two_runs(a, b, y, width, thickness):
    return rod((a[0], y - width / 2, a[1]), (b[0], y - width / 2, b[1]), thickness / 2).fuse(
        rod((a[0], y + width / 2, a[1]), (b[0], y + width / 2, b[1]), thickness / 2))


def finger_bar(center):
    x, z = center
    parts = [cyl_y(SHAFT_D / 2, ROLLER_FACE + 28, (x, 0, z))]
    usable = CLEAR_CAPTURE_WIDTH - FINGER_WIDTH
    for i in range(FINGER_COUNT):
        y = -usable / 2 + usable * i / (FINGER_COUNT - 1)
        parts.append(box(FINGER_LENGTH, FINGER_WIDTH, FINGER_THICKNESS, (x - FINGER_LENGTH / 2, y, z)))
    return cq.Compound.makeCompound(parts)


def front_center(angle_deg):
    angle = math.radians(angle_deg)
    return PIVOT[0] + ARM_LENGTH * math.cos(angle), PIVOT[1] + ARM_LENGTH * math.sin(angle)


def add_common(assy, shapes):
    def add(name, shape, color, include=True):
        assy.add(shape, name=name, color=color)
        if include:
            shapes.append(shape)

    add("chassis_front_datum", box(12, MOUNT_WIDTH, 210, (0, 0, 110)), C["datum"], False)
    for y in (-MOUNT_WIDTH / 2, MOUNT_WIDTH / 2):
        add(f"mount_rail_{y:+.0f}", box(255, 16, 16, (105, y, 34)), C["structure"])

    for i, center in enumerate(FIXED_ROLLERS, 1):
        add(f"fixed_roller_{i}", roller(center), C["roller"])
        add(f"fixed_shaft_{i}", cyl_y(SHAFT_D / 2, MOUNT_WIDTH - 18, (center[0], 0, center[1])), C["shaft"])
        for y in (-170, 170):
            add(f"dual_bearing_block_{i}_{y:+.0f}", box(32, 14, 38, (center[0], y, center[1])), C["structure"])

    # Independent 38-link loops; two sprockets on the middle shaft isolate adjustment/failure.
    for n, (a, b, y) in enumerate(((FIXED_ROLLERS[0], FIXED_ROLLERS[1], -183.0),
                                    (FIXED_ROLLERS[1], FIXED_ROLLERS[2], -198.0)), 1):
        add(f"chain_sprocket_{n}_driver", sprocket(a, y), C["sprocket"])
        add(f"chain_sprocket_{n}_driven", sprocket(b, y), C["sprocket"])
        add(f"chain_loop_{n}", two_runs(a, b, y, 6, 4), C["belt"])
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - 13)
        add(f"chain_idler_3312_0006_0008_{n}", cyl_y(9, 10, (mid[0], y, mid[1])), C["sprocket"])
        add(f"arc_slot_tensioner_1524_0001_0001_{n}", box(42, 4, 18, (mid[0], y - 7, mid[1])), C["structure"])

    add("ball_guide_floor", box(235, CLEAR_CAPTURE_WIDTH + 8, 4, (105, 0, 42)).rotate(
        (105, 0, 42), (105, 1, 42), -24), C["guide"])

    # goBILDA 5203 19.2:1 motor and 24T:24T MOD1 miter pair.
    motor_x, motor_y, motor_z = PIVOT[0], -220.0, 119.0
    add("motor_5203_2402_0019_312rpm_envelope", cyl_z(19, 104, (motor_x, motor_y, motor_z)), C["motor"])
    add("motor_mount", box(58, 52, 5, (motor_x, motor_y, 68)), C["structure"])
    miter_motor = cq.Workplane("XY").workplane(offset=53).circle(7).workplane(offset=15).circle(14).loft(combine=True).val().translate((motor_x, motor_y, 0))
    add("miter_gear_24t_motor", miter_motor, C["gear"])
    miter_primary = cq.Workplane("XZ").circle(14).workplane(offset=16).circle(7).loft(combine=True).val().translate((PIVOT[0], -192, PIVOT[1]))
    add("miter_gear_24t_primary", miter_primary, C["gear"])
    add("primary_slip_clutch_0p8Nm_envelope", cyl_y(18, 14, (PIVOT[0], -207, PIVOT[1])), C["latch"])


def build(config, angle_deg):
    assy = cq.Assembly(name=f"single_motor_flipout_intake_{config}")
    shapes = []
    add_common(assy, shapes)

    def add(name, shape, color):
        assy.add(shape, name=name, color=color)
        shapes.append(shape)

    tip = front_center(angle_deg)
    for y in (-174.0, 174.0):
        add(f"pivot_arm_{y:+.0f}", arm_plate(PIVOT, tip, y), C["structure"])
    add("front_finger_bar", finger_bar(tip), C["finger"])
    add("front_pulley_24t_3417_4008_0024", pulley(tip, -181, FRONT_DRIVEN_TEETH), C["pulley"])
    add("pivot_pulley_16t_3417_4008_0016", pulley(PIVOT, -181, FRONT_DRIVER_TEETH), C["pulley"])
    add("front_belt_460mm_3412_0009_0460", two_runs(PIVOT, tip, -181, 9, 3), C["belt"])

    for y in (-170.0, 170.0):
        anchor = (PIVOT[0] - 45.0, y, PIVOT[1] - 47.0)
        angle = math.radians(angle_deg)
        arm_anchor = (PIVOT[0] + 90.0 * math.cos(angle), y, PIVOT[1] + 90.0 * math.sin(angle))
        add(f"deployment_spring_{y:+.0f}", rod(anchor, arm_anchor, 4.0), C["spring"])
        add(f"replaceable_hard_stop_{y:+.0f}", box(30, 16, 28, (-1, y, 50)), C["latch"])

    # Dual pawls take load. The synchronized servo link only releases them.
    add("latch_cross_shaft", cyl_y(4, 352, (-28, 0, 198)), C["shaft"])
    for y in (-174.0, 174.0):
        add(f"load_bearing_pawl_{y:+.0f}", box(34, 10, 12, (-34, y, 211)), C["latch"])
    add("rev_41_3334_balanced_servo_envelope", box(40.2, 20.0, 38.0, (-5, -150, 198)), cq.Color(0.48, 0.30, 0.70, 0.60))
    add("servo_release_crank_20mm", rod((-5, -160, 211), (-25, -160, 211), 3.0), C["latch"])
    add("servo_release_link", rod((-25, -160, 211), (-28, -174, 198), 2.0), C["latch"])
    return assy, shapes


def bbox(shapes):
    bb = cq.Compound.makeCompound(shapes).BoundingBox()
    return {
        "min_mm": [round(bb.xmin, 2), round(bb.ymin, 2), round(bb.zmin, 2)],
        "max_mm": [round(bb.xmax, 2), round(bb.ymax, 2), round(bb.zmax, 2)],
        "size_mm": [round(bb.xlen, 2), round(bb.ylen, 2), round(bb.zlen, 2)],
        "within_expanded_18x24x29_if_oriented_X24_Y18_Z29": bool(
            bb.xlen <= EXPANDED_LIMIT_X and bb.ylen <= EXPANDED_LIMIT_Y and bb.zlen <= EXPANDED_LIMIT_Z),
    }


def export_all():
    report = {
        "design_version": DESIGN_VERSION,
        "status": "M3_COTS_CONSTRAINED_PACKAGING_NOT_PRODUCTION_RELEASE",
        "model_purpose": "transmission and flip-out packaging; purchased-part envelopes require drawing verification",
        "source_video": "https://youtu.be/RIt5xxJ2Yxs",
        "authoritative_module_note": "KEI-16/T02 is imported reference provenance; current repository Intake is T04",
        "manual_stow_note": "one-shot spring deploy plus manual pre-match stow; no active in-match retraction",
        "game_piece_diameters_mm": {"pollen": POLLEN_D, "nectar": NECTAR_D},
        "clear_capture_width_mm": CLEAR_CAPTURE_WIDTH,
        "drive": {
            "dc_motor_count": 1,
            "motor": {"sku": "5203-2402-0019", "no_load_rpm": MOTOR_RPM},
            "miter_gears": {"sku": "2320-4008-0024", "quantity": 2, "ratio": MITER_RATIO},
            "fixed_chain": {"sprocket_sku": "3302-4008-0014", "sprocket_teeth": CHAIN_SPROCKET_TEETH,
                            "chain_sku": "3315-0008-0038", "chain_links_per_stage": CHAIN_LINKS,
                            "stage_count": 2, "center_distance_mm": ROLLER_CENTER},
            "front_belt": {"driver_sku": "3417-4008-0016", "driven_sku": "3417-4008-0024",
                           "belt_sku": "3412-0009-0460", "belt_pitch_length_mm": FRONT_BELT_LENGTH,
                           "center_distance_mm": ARM_LENGTH},
            "software_current_alert_a": 3.4, "overcurrent_duration_ms": 200,
            "target_primary_slip_torque_nm": 0.8,
        },
        "performance_calculated_no_load": {
            "fixed_roller_rpm": MOTOR_RPM * MITER_RATIO,
            "fixed_roller_surface_speed_mps": round(math.pi * (ROLLER_OD / 1000) * MOTOR_RPM / 60, 3),
            "front_bar_rpm": MOTOR_RPM * FRONT_PULLEY_RATIO,
            "front_finger_tip_speed_mps": round(2 * math.pi * (FINGER_LENGTH / 1000) * MOTOR_RPM * FRONT_PULLEY_RATIO / 60, 3),
        },
        "deployment": {"spring_count": 2, "target_force_each_n": {"stowed": 30.0, "deployed": 15.0},
                       "latch": "dual load-bearing pawls; REV-41-3334 only releases",
                       "hard_stop_target_n_each": 250.0},
        "pivot_center_mm": list(PIVOT), "arm_length_mm": ARM_LENGTH,
        "fixed_roller_centers_mm": [[round(x, 3), round(z, 3)] for x, z in FIXED_ROLLERS],
        "angles_deg": {"deployed": DEPLOYED_ANGLE, "stowed": STOWED_ANGLE}, "configurations": {},
    }
    for config, angle in (("deployed", DEPLOYED_ANGLE), ("stowed", STOWED_ANGLE)):
        assy, shapes = build(config, angle)
        stem = OUT / f"biobuzz_single_motor_flipout_intake_{config}"
        assy.export(str(stem.with_suffix(".step")), exportType="STEP")
        assy.export(str(stem.with_suffix(".glb")), exportType="GLTF", tolerance=0.25, angularTolerance=0.18)
        exporters.export(cq.Compound.makeCompound(shapes), str(stem.with_suffix(".stl")), tolerance=0.25, angularTolerance=0.18)
        report["configurations"][config] = {"front_bar_center_mm": [round(v, 2) for v in front_center(angle)],
                                               "bounding_box": bbox(shapes)}
    (OUT / "biobuzz_single_motor_flipout_intake_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    export_all()
