"""BIOBUZZ single-motor, spring-deployed roller intake baseline.

This is a dimensioned packaging model, not a production drawing.  It models
the load path, roller axes, belt side, pivot geometry, hard stops, spring and
latch envelopes.  Units are millimetres.  X points out of the robot, Y runs
left-to-right across the intake, and +Z is upward.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import cadquery as cq
from cadquery import exporters


OUT = Path(__file__).resolve().parent / "output"
OUT.mkdir(parents=True, exist_ok=True)

# Interface and game-piece assumptions.
CHASSIS_FRONT_X = 0.0
MOUNT_WIDTH = 380.0
CLEAR_CAPTURE_WIDTH = 330.0
POLLEN_D = 71.0
NECTAR_D = 91.0
EXPANDED_LIMIT_X = 610.0  # 24 in.
EXPANDED_LIMIT_Y = 457.2  # 18 in.
EXPANDED_LIMIT_Z = 736.6  # 29 in.

# Roller system.
ROLLER_OD = 60.0
ROLLER_FACE = 318.0
SHAFT_D = 8.0
MOTOR_RPM = 435.0
BEVEL_RATIO = 20.0 / 28.0
FIXED_ROLLERS = ((25.0, 67.0), (103.0, 111.0), (181.0, 155.0))
PIVOT = FIXED_ROLLERS[0]
ARM_LENGTH = 178.0
DEPLOYED_ANGLE = 198.0
STOWED_ANGLE = 103.0
FRONT_PULLEY_RATIO = 24.0 / 36.0

# Flexible finger bar.
FINGER_COUNT = 13
FINGER_LENGTH = 73.0
FINGER_WIDTH = 18.0
FINGER_THICKNESS = 3.0

C = {
    "structure": cq.Color(0.68, 0.73, 0.80),
    "roller": cq.Color(0.12, 0.12, 0.14),
    "shaft": cq.Color(0.50, 0.54, 0.60),
    "pulley": cq.Color(0.92, 0.60, 0.10),
    "belt": cq.Color(0.06, 0.06, 0.07),
    "motor": cq.Color(0.94, 0.73, 0.12),
    "gear": cq.Color(0.78, 0.80, 0.84),
    "finger": cq.Color(0.92, 0.94, 0.96),
    "spring": cq.Color(0.20, 0.62, 0.92),
    "latch": cq.Color(0.86, 0.24, 0.16),
    "guide": cq.Color(0.20, 0.55, 0.82, 0.34),
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
    d = bv - av
    return cq.Solid.makeCylinder(radius, d.Length, av, d.normalized())


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


def pulley(center, y, teeth, width=12.0):
    pitch_d = teeth * 5.0 / math.pi
    body = cyl_y(pitch_d / 2, width, (center[0], y, center[1]))
    return body.cut(cyl_y(SHAFT_D / 2 + 0.2, width + 2, (center[0], y, center[1])))


def belt_segment(a, b, y, width=10.0, thickness=3.0):
    return rod((a[0], y, a[1]), (b[0], y, b[1]), thickness / 2).fuse(
        rod((a[0], y + width, a[1]), (b[0], y + width, b[1]), thickness / 2)
    )


def finger_bar(center):
    x, z = center
    parts = [cyl_y(SHAFT_D / 2, ROLLER_FACE + 28, (x, 0, z))]
    usable = CLEAR_CAPTURE_WIDTH - FINGER_WIDTH
    for i in range(FINGER_COUNT):
        y = -usable / 2 + usable * i / (FINGER_COUNT - 1)
        finger = box(FINGER_LENGTH, FINGER_WIDTH, FINGER_THICKNESS, (x - FINGER_LENGTH / 2, y, z))
        parts.append(finger)
    return cq.Compound.makeCompound(parts)


def front_center(angle_deg):
    a = math.radians(angle_deg)
    return (PIVOT[0] + ARM_LENGTH * math.cos(a), PIVOT[1] + ARM_LENGTH * math.sin(a))


def guide_panel():
    # 4 mm polycarbonate floor tangent to the three fixed roller crowns.
    return box(235, CLEAR_CAPTURE_WIDTH + 8, 4, (105, 0, 42)).rotate((105, 0, 42), (105, 1, 42), -27)


def add_common(assy, shapes):
    def add(name, shape, color, include_in_mesh=True):
        assy.add(shape, name=name, color=color)
        if include_in_mesh:
            shapes.append(shape)

    # Mounting/datums.
    add("chassis_front_datum", box(12, MOUNT_WIDTH, 210, (0, 0, 110)), C["datum"], False)
    for y in (-MOUNT_WIDTH / 2, MOUNT_WIDTH / 2):
        add(f"mount_rail_{y:+.0f}", box(255, 16, 16, (105, y, 34)), C["structure"])

    # Fixed roller train and supports.
    for i, center in enumerate(FIXED_ROLLERS, 1):
        add(f"fixed_roller_{i}", roller(center), C["roller"])
        add(f"fixed_shaft_{i}", cyl_y(SHAFT_D / 2, MOUNT_WIDTH - 18, (center[0], 0, center[1])), C["shaft"])
        for y in (-170, 170):
            add(f"bearing_block_{i}_{y:+.0f}", box(30, 14, 38, (center[0], y, center[1])), C["structure"])
        add(f"drive_pulley_{i}", pulley(center, -181, 24), C["pulley"])
    add("roller_belt_1_2", belt_segment(FIXED_ROLLERS[0], FIXED_ROLLERS[1], -186), C["belt"])
    add("roller_belt_2_3", belt_segment(FIXED_ROLLERS[1], FIXED_ROLLERS[2], -186), C["belt"])
    add("ball_guide_floor", guide_panel(), C["guide"])

    # Vertical motor and bevel stage copied from the visible video architecture.
    motor_x, motor_y, motor_z = PIVOT[0], -211.0, 119.0
    add("motor_435rpm_envelope", cyl_z(19, 104, (motor_x, motor_y, motor_z)), C["motor"])
    add("motor_mount", box(58, 52, 5, (motor_x, motor_y, 68)), C["structure"])
    pinion = cq.Workplane("XY").workplane(offset=53).circle(7).workplane(offset=15).circle(19).loft(combine=True).val()
    pinion = pinion.translate((motor_x, motor_y, 0))
    add("bevel_pinion_20t", pinion, C["gear"])
    bevel = cq.Workplane("XZ").circle(26).workplane(offset=18).circle(9).loft(combine=True).val().translate((PIVOT[0], -183, PIVOT[1]))
    add("bevel_gear_28t", bevel, C["gear"])


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
    add("front_36t_pulley", pulley(tip, -181, 36), C["pulley"])
    add("pivot_24t_pulley", pulley(PIVOT, -181, 24), C["pulley"])
    add("constant_center_arm_belt", belt_segment(PIVOT, tip, -186), C["belt"])

    # Spring deployment: energy storage and a positive deployed hard stop.
    spring_anchor = (64.0, -170.0, 177.0)
    arm_anchor = ((PIVOT[0] + tip[0]) / 2, -170.0, (PIVOT[1] + tip[1]) / 2)
    add("deployment_spring_envelope", rod(spring_anchor, arm_anchor, 5.0), C["spring"])
    add("deployed_hard_stop", box(32, 22, 28, (-1, -174, 50)), C["latch"])

    # Recommended latch: spring-loaded hook, released by a micro-servo.
    add("stow_latch_hook", box(34, 12, 12, (-34, -174, 221)), C["latch"])
    add("micro_servo_latch_envelope", box(24, 13, 29, (-10, -174, 204)), cq.Color(0.48, 0.30, 0.70, 0.50))
    # Strict one-actuator option: reverse-direction cam on the pivot shaft.
    cam = cyl_y(23, 8, (PIVOT[0], 185, PIVOT[1])).cut(box(30, 12, 14, (PIVOT[0] + 15, 185, PIVOT[1] + 15)))
    add("optional_reverse_unlatch_cam", cam, C["latch"])

    return assy, shapes


def bbox(shapes):
    bb = cq.Compound.makeCompound(shapes).BoundingBox()
    size = (bb.xlen, bb.ylen, bb.zlen)
    return {
        "min_mm": [round(bb.xmin, 2), round(bb.ymin, 2), round(bb.zmin, 2)],
        "max_mm": [round(bb.xmax, 2), round(bb.ymax, 2), round(bb.zmax, 2)],
        "size_mm": [round(v, 2) for v in size],
        "within_expanded_18x24x29_if_oriented_X24_Y18_Z29": bool(
            bb.xlen <= EXPANDED_LIMIT_X and bb.ylen <= EXPANDED_LIMIT_Y and bb.zlen <= EXPANDED_LIMIT_Z
        ),
    }


def export_all():
    report = {
        "model_purpose": "packaging and kinematic baseline; verify purchased parts and chassis interfaces before fabrication",
        "source_video": "https://youtu.be/RIt5xxJ2Yxs",
        "visible_video_features_reused": [
            "one vertically mounted geared motor",
            "90-degree bevel gear turn into a transverse roller shaft",
            "one-side belt distribution to multiple horizontal rollers",
            "front flexible-finger pickup bar",
        ],
        "adaptations_not_proven_by_video": [
            "finger bar carried on constant-center pivot arms",
            "torsion/extension spring deployment",
            "servo latch or optional reverse-cam unlatch",
        ],
        "game_piece_diameters_mm": {"pollen": POLLEN_D, "nectar": NECTAR_D},
        "clear_capture_width_mm": CLEAR_CAPTURE_WIDTH,
        "motor_nominal_rpm": MOTOR_RPM,
        "bevel_ratio": BEVEL_RATIO,
        "fixed_roller_rpm": round(MOTOR_RPM * BEVEL_RATIO, 1),
        "fixed_roller_surface_speed_mps": round(math.pi * (ROLLER_OD / 1000) * MOTOR_RPM * BEVEL_RATIO / 60, 3),
        "front_bar_rpm": round(MOTOR_RPM * BEVEL_RATIO * FRONT_PULLEY_RATIO, 1),
        "front_finger_tip_speed_mps": round(2 * math.pi * (FINGER_LENGTH / 1000) * MOTOR_RPM * BEVEL_RATIO * FRONT_PULLEY_RATIO / 60, 3),
        "pivot_center_mm": list(PIVOT),
        "arm_length_mm": ARM_LENGTH,
        "angles_deg": {"deployed": DEPLOYED_ANGLE, "stowed": STOWED_ANGLE},
        "configurations": {},
    }
    for config, angle in (("deployed", DEPLOYED_ANGLE), ("stowed", STOWED_ANGLE)):
        assy, shapes = build(config, angle)
        stem = OUT / f"biobuzz_single_motor_flipout_intake_{config}"
        assy.export(str(stem.with_suffix(".step")), exportType="STEP")
        assy.export(str(stem.with_suffix(".glb")), exportType="GLTF", tolerance=0.25, angularTolerance=0.18)
        exporters.export(cq.Compound.makeCompound(shapes), str(stem.with_suffix(".stl")), tolerance=0.25, angularTolerance=0.18)
        report["configurations"][config] = {"front_bar_center_mm": [round(v, 2) for v in front_center(angle)], "bounding_box": bbox(shapes)}

    (OUT / "biobuzz_single_motor_flipout_intake_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    export_all()
