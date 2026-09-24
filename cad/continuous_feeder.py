"""Detailed continuous-servo feeder for the BIOBUZZ launcher.

Coordinate convention:
    X-Y = chassis plane
    +Z  = upward
    +X  = feed direction toward the launcher

No game-piece geometry is included. Servos are packaging envelopes; frame,
shafts, pulleys, belts, bearings, swing arms, guides and fastener holes are
modeled as preliminary manufacturable geometry. Units are millimetres.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import cadquery as cq
from cadquery import exporters


OUT = Path(__file__).resolve().parent / "output"
OUT.mkdir(parents=True, exist_ok=True)

FRAME_INNER_WIDTH = 108.0
SIDE_PLATE_Y = 58.0
SIDE_PLATE_T = 4.0
SHAFT_D = 8.0
BEARING_OD = 14.0
BELT_WIDTH = 18.0
BELT_THICKNESS = 3.0
PULLEY_OD = 28.0
PULLEY_WIDTH = 20.0
HORIZONTAL_X0 = -112.0
JUNCTION_X = 28.0
LOWER_SHAFT_Z = 26.0
INCLINE_ANGLE_DEG = 38.0
UPPER_SHAFT = (126.0, 0.0, 103.0)
PINCH_ROLLER_OD = 72.0
PINCH_NEUTRAL = (46.0, 0.0, 157.0)
PINCH_TRAVEL = 22.0
PINCH_REDUCTION = 2.4
SERVO_ENV = (41.0, 21.0, 40.0)


C = {
    "frame": cq.Color(0.18, 0.23, 0.30),
    "plate": cq.Color(0.70, 0.76, 0.84),
    "shaft": cq.Color(0.62, 0.66, 0.72),
    "bearing": cq.Color(0.32, 0.35, 0.40),
    "pulley": cq.Color(0.84, 0.52, 0.16),
    "belt": cq.Color(0.08, 0.09, 0.11),
    "guide": cq.Color(0.20, 0.57, 0.84, 0.55),
    "servo": cq.Color(0.60, 0.31, 0.76, 0.55),
    "spring": cq.Color(0.90, 0.66, 0.12),
    "reference": cq.Color(0.18, 0.60, 0.35, 0.18),
}


def box(l, w, h, center=(0.0, 0.0, 0.0)) -> cq.Shape:
    return cq.Workplane("XY").box(l, w, h, centered=(True, True, True)).translate(center).val()


def cyl_y(radius, length, center=(0.0, 0.0, 0.0)) -> cq.Shape:
    x, y, z = center
    return cq.Solid.makeCylinder(radius, length, cq.Vector(x, y - length / 2, z), cq.Vector(0, 1, 0))


def cyl_z(radius, height, center=(0.0, 0.0, 0.0)) -> cq.Shape:
    x, y, z = center
    return cq.Solid.makeCylinder(radius, height, cq.Vector(x, y, z - height / 2), cq.Vector(0, 0, 1))


def rod_between(a, b, radius) -> cq.Shape:
    va, vb = cq.Vector(*a), cq.Vector(*b)
    d = vb - va
    return cq.Solid.makeCylinder(radius, d.Length, va, d.normalized())


def inclined(shape: cq.Shape, center, angle_deg: float) -> cq.Shape:
    return shape.rotate(center, (center[0], center[1] + 1, center[2]), -angle_deg)


def timing_pulley(center, width=PULLEY_WIDTH, od=PULLEY_OD, teeth=20) -> cq.Shape:
    """Envelope-accurate pulley with visible preliminary teeth and 8 mm bore."""
    x, y, z = center
    pulley = cyl_y(od / 2 - 1.4, width, center).cut(cyl_y(SHAFT_D / 2 + 0.15, width + 2, center))
    for i in range(teeth):
        angle = i * 360.0 / teeth
        tooth = box(3.0, width - 2, 2.8, (x + od / 2 - 0.9, y, z))
        tooth = tooth.rotate((x, y, z), (x, y + 1, z), angle)
        pulley = pulley.fuse(tooth)
    # Flanges retain the narrow belts.
    for dy in (-(width / 2 - 0.8), width / 2 - 0.8):
        flange = cyl_y(od / 2 + 1.5, 1.6, (x, y + dy, z)).cut(cyl_y(SHAFT_D / 2 + 0.15, 3, (x, y + dy, z)))
        pulley = pulley.fuse(flange)
    return pulley


def bearing_block(center, y) -> cq.Shape:
    x, _, z = center
    block = box(34, 10, 34, (x, y, z))
    block = block.cut(cyl_y(BEARING_OD / 2 + 0.1, 14, (x, y, z)))
    for dx in (-12, 12):
        block = block.cut(cyl_y(2.2, 14, (x + dx, y, z)))
    return block


def mini_servo_block(center, side=1) -> list[tuple[str, cq.Shape, cq.Color]]:
    """Compact ServoBlock envelope and supported output hub."""
    x, y, z = center
    sy = side * abs(y)
    parts = []
    body = box(*SERVO_ENV, (x, sy, z))
    parts.append(("servo_envelope", body, C["servo"]))
    plate_y = sy - side * 16
    plate = box(57, 6, 58, (x, plate_y, z))
    plate = plate.cut(cyl_y(8.2, 12, (x, plate_y, z)))
    for dx in (-23, 23):
        for dz in (-23, 23):
            plate = plate.cut(cyl_y(2.2, 12, (x + dx, plate_y, z + dz)))
    parts.append(("servo_block_plate", plate, C["frame"]))
    parts.append(("servo_output_hub", cyl_y(11, 12, (x, plate_y - side * 8, z)).cut(cyl_y(4.1, 14, (x, plate_y - side * 8, z))), C["shaft"]))
    return parts


def compliant_pinch_roller(center) -> cq.Shape:
    """72 mm flexible roller approximation with hub, ring and twelve spokes."""
    x, y, z = center
    outer = cyl_y(36, 44, center).cut(cyl_y(30, 46, center))
    hub = cyl_y(13, 48, center).cut(cyl_y(4.1, 50, center))
    roller = outer.fuse(hub)
    for a in range(0, 360, 30):
        spoke = box(24, 40, 5, (x + 23, y, z)).rotate((x, y, z), (x, y + 1, z), a)
        roller = roller.fuse(spoke)
    return roller


def build() -> tuple[cq.Assembly, list[cq.Shape]]:
    assy = cq.Assembly(name="continuous_servo_feeder")
    mesh: list[cq.Shape] = []

    def add(name, shape, color, meshable=True):
        assy.add(shape, name=name, color=color)
        if meshable:
            mesh.append(shape)

    # Chassis reference only; X-Y is the chassis plane.
    add("00_xy_chassis_reference", box(340, 240, 4, (10, 0, -2)), C["reference"], False)

    # Side frames: laser-cut 4 mm plates with lightening windows and mounting holes.
    outline = [(-128, 4), (54, 4), (145, 78), (151, 145), (72, 188), (-42, 178), (-128, 126)]
    for side in (-1, 1):
        y = side * SIDE_PLATE_Y
        plate = cq.Workplane("XZ").polyline(outline).close().extrude(SIDE_PLATE_T / 2, both=True).translate((0, y, 0)).val()
        for x, z, r in [(-88, 79, 28), (-22, 90, 23), (62, 112, 24), (116, 139, 18)]:
            plate = plate.cut(cyl_y(r, 10, (x, y, z)))
        for x in (-112, -64, -16, 32, 80, 128):
            plate = plate.cut(cyl_y(2.3, 10, (x, y, 14)))
        # Bearing holes and the pinch-arm pivot.
        for x, z in [(HORIZONTAL_X0, LOWER_SHAFT_Z), (JUNCTION_X, LOWER_SHAFT_Z), (UPPER_SHAFT[0], UPPER_SHAFT[2]), (-20, 166)]:
            plate = plate.cut(cyl_y(BEARING_OD / 2 + 0.15, 10, (x, y, z)))
        add(f"side_frame_{side:+d}", plate, C["plate"])

    # Cross members and chassis feet.
    for x, z in [(-118, 16), (18, 16), (136, 86), (-30, 169)]:
        add(f"crossmember_{x}_{z}", box(18, 112, 16, (x, 0, z)), C["frame"])
    for y in (-66, 66):
        rail = box(290, 18, 14, (5, y, 9))
        for x in (-112, -64, -16, 32, 80, 128):
            rail = rail.cut(cyl_z(2.3, 20, (x, y, 9)))
        add(f"chassis_rail_{y:+d}", rail, C["frame"])

    # Three main shafts: horizontal return, common junction drive, incline return.
    shafts = [
        ("horizontal_return", (HORIZONTAL_X0, 0, LOWER_SHAFT_Z)),
        ("junction_drive", (JUNCTION_X, 0, LOWER_SHAFT_Z)),
        ("incline_return", UPPER_SHAFT),
    ]
    for label, p in shafts:
        add(f"shaft_{label}", cyl_y(SHAFT_D / 2, 146, p), C["shaft"])
        for side in (-1, 1):
            add(f"bearing_block_{label}_{side:+d}", bearing_block(p, side * 52), C["frame"])
            add(f"bearing_{label}_{side:+d}",
                cyl_y(BEARING_OD / 2, 5, (p[0], side * 52, p[2])).cut(cyl_y(SHAFT_D / 2 + 0.05, 7, (p[0], side * 52, p[2]))),
                C["bearing"])

    # Four-groove junction shaft: the wide horizontal lanes transition to
    # narrower incline lanes without any pulleys occupying the same space.
    horizontal_lanes = (-36.0, 36.0)
    incline_lanes = (-12.0, 12.0)
    for lane in horizontal_lanes:
        add(f"pulley_horizontal_return_{int(lane)}", timing_pulley((HORIZONTAL_X0, lane, LOWER_SHAFT_Z)), C["pulley"])
        add(f"pulley_horizontal_drive_{int(lane)}", timing_pulley((JUNCTION_X, lane, LOWER_SHAFT_Z)), C["pulley"])
        h_len = JUNCTION_X - HORIZONTAL_X0
        add(f"belt_horizontal_top_{int(lane)}", box(h_len, BELT_WIDTH, BELT_THICKNESS, ((HORIZONTAL_X0 + JUNCTION_X) / 2, lane, LOWER_SHAFT_Z + PULLEY_OD / 2)), C["belt"])
        add(f"belt_horizontal_return_{int(lane)}", box(h_len, BELT_WIDTH, BELT_THICKNESS, ((HORIZONTAL_X0 + JUNCTION_X) / 2, lane, LOWER_SHAFT_Z - PULLEY_OD / 2)), C["belt"])

    for lane in incline_lanes:
        add(f"pulley_incline_drive_{int(lane)}", timing_pulley((JUNCTION_X, lane, LOWER_SHAFT_Z)), C["pulley"])
        add(f"pulley_incline_return_{int(lane)}", timing_pulley((UPPER_SHAFT[0], lane, UPPER_SHAFT[2])), C["pulley"])
        dx, dz = UPPER_SHAFT[0] - JUNCTION_X, UPPER_SHAFT[2] - LOWER_SHAFT_Z
        inc_len = math.hypot(dx, dz)
        inc_angle = math.degrees(math.atan2(dz, dx))
        cx, cz = (JUNCTION_X + UPPER_SHAFT[0]) / 2, (LOWER_SHAFT_Z + UPPER_SHAFT[2]) / 2
        nx, nz = -math.sin(math.radians(inc_angle)), math.cos(math.radians(inc_angle))
        for sign, suffix in ((1, "top"), (-1, "return")):
            center = (cx + sign * (PULLEY_OD / 2) * nx, lane, cz + sign * (PULLEY_OD / 2) * nz)
            strand = inclined(box(inc_len, BELT_WIDTH, BELT_THICKNESS, center), center, inc_angle)
            add(f"belt_incline_{suffix}_{int(lane)}", strand, C["belt"])

    # The common drive shaft receives a continuous-rotation servo through a supported hub.
    for i, (name, part, color) in enumerate(mini_servo_block((JUNCTION_X, 100, LOWER_SHAFT_Z), side=1)):
        add(f"belt_drive_{name}_{i}", part, color, meshable=name != "servo_envelope")
    add("junction_shaft_coupler", cyl_y(11, 18, (JUNCTION_X, 72, LOWER_SHAFT_Z)).cut(cyl_y(4.1, 20, (JUNCTION_X, 72, LOWER_SHAFT_Z))), C["shaft"])

    # Fixed 38-degree guide shell surrounding the incline belts.
    dx, dz = UPPER_SHAFT[0] - JUNCTION_X, UPPER_SHAFT[2] - LOWER_SHAFT_Z
    guide_len = math.hypot(dx, dz) + 32
    guide_angle = math.degrees(math.atan2(dz, dx))
    gc = ((JUNCTION_X + UPPER_SHAFT[0]) / 2, 0, (LOWER_SHAFT_Z + UPPER_SHAFT[2]) / 2 + 39)
    for side in (-1, 1):
        wall = inclined(box(guide_len, 3, 112, (gc[0], side * 55.5, gc[2])), (gc[0], side * 55.5, gc[2]), guide_angle)
        add(f"incline_guide_wall_{side:+d}", wall, C["guide"])
    roof_center = (gc[0] - 48 * math.sin(math.radians(guide_angle)), 0, gc[2] + 48 * math.cos(math.radians(guide_angle)))
    roof = inclined(box(guide_len, 108, 3, roof_center), roof_center, guide_angle)
    add("incline_guide_roof", roof, C["guide"])

    # Servo-driven floating pinch roller. Both side arms pivot on supported bearings.
    pivot = (-20.0, 0.0, 166.0)
    for side in (-1, 1):
        y = side * 62.0
        arm = rod_between((pivot[0], y, pivot[2]), (PINCH_NEUTRAL[0], y, PINCH_NEUTRAL[2]), 7.0)
        arm = arm.fuse(cyl_y(13, 8, (pivot[0], y, pivot[2])).cut(cyl_y(4.1, 10, (pivot[0], y, pivot[2]))))
        arm = arm.fuse(cyl_y(13, 8, (PINCH_NEUTRAL[0], y, PINCH_NEUTRAL[2])).cut(cyl_y(4.1, 10, (PINCH_NEUTRAL[0], y, PINCH_NEUTRAL[2]))))
        add(f"pinch_swing_arm_{side:+d}", arm, C["frame"])
        # Adjustable spring/damper link envelope sets preload without fixing ball diameter.
        spring_a = (-2, y, 112)
        spring_b = (24, y, 151)
        add(f"pinch_preload_link_{side:+d}", rod_between(spring_a, spring_b, 4.0), C["spring"])
        add(f"pinch_preload_eye_a_{side:+d}", cq.Solid.makeSphere(7, cq.Vector(*spring_a)), C["spring"])
        add(f"pinch_preload_eye_b_{side:+d}", cq.Solid.makeSphere(7, cq.Vector(*spring_b)), C["spring"])

    add("pinch_shaft", cyl_y(SHAFT_D / 2, 154, PINCH_NEUTRAL), C["shaft"])
    add("pinch_compliant_roller", compliant_pinch_roller(PINCH_NEUTRAL), C["belt"])
    # The pinch servo rides on the swing arm. A 20T:48T reduction matches the
    # 72 mm roller surface speed to the 28 mm conveyor pulley surface speed.
    pinch_drive_center = (PINCH_NEUTRAL[0] - 52.0, 105.0, PINCH_NEUTRAL[2] + 8.0)
    for i, (name, part, color) in enumerate(mini_servo_block(pinch_drive_center, side=1)):
        add(f"pinch_drive_{name}_{i}", part, color, meshable=name != "servo_envelope")
    pulley_y = 73.0
    small_pulley_center = (pinch_drive_center[0], pulley_y, pinch_drive_center[2])
    large_pulley_center = (PINCH_NEUTRAL[0], pulley_y, PINCH_NEUTRAL[2])
    add("pinch_servo_20t_pulley", timing_pulley(small_pulley_center, width=14, od=16, teeth=20), C["pulley"])
    add("pinch_roller_48t_pulley", timing_pulley(large_pulley_center, width=14, od=38.4, teeth=48), C["pulley"])
    pdx = large_pulley_center[0] - small_pulley_center[0]
    pdz = large_pulley_center[2] - small_pulley_center[2]
    p_len = math.hypot(pdx, pdz)
    p_ang = math.degrees(math.atan2(pdz, pdx))
    pcx = (small_pulley_center[0] + large_pulley_center[0]) / 2
    pcz = (small_pulley_center[2] + large_pulley_center[2]) / 2
    pnx, pnz = -math.sin(math.radians(p_ang)), math.cos(math.radians(p_ang))
    for sign, suffix in ((1, "upper"), (-1, "lower")):
        center = (pcx + sign * 12.0 * pnx, pulley_y, pcz + sign * 12.0 * pnz)
        strand = inclined(box(p_len, 12, 3, center), center, p_ang)
        add(f"pinch_reduction_belt_{suffix}", strand, C["belt"])

    # 52-degree launcher-inlet flange and compliant side funnels.
    outlet_angle = 52.0
    outlet_center = (151, 0, 132)
    for side in (-1, 1):
        wall = inclined(box(72, 3, 116, (outlet_center[0], side * 55.5, outlet_center[2])), (outlet_center[0], side * 55.5, outlet_center[2]), outlet_angle)
        add(f"launcher_inlet_wall_{side:+d}", wall, C["guide"])
    for side in (-1, 1):
        leaf = inclined(box(62, 1.2, 46, (145, side * 40, 128)), (145, side * 40, 128), outlet_angle)
        add(f"flex_centering_leaf_{side:+d}", leaf, cq.Color(0.75, 0.87, 0.95))

    # Belt guards protect the exposed timing pulleys on both sides.
    for side in (-1, 1):
        y = side * 74
        guard = box(178, 3, 54, (-42, y, 30))
        for x in (-95, -45, 5):
            guard = guard.cut(cyl_y(13, 7, (x, y, 30)))
        add(f"horizontal_belt_guard_{side:+d}", guard, C["guide"])

    return assy, mesh


def export_all():
    assy, mesh = build()
    step = OUT / "continuous_servo_feeder.step"
    stl = OUT / "continuous_servo_feeder.stl"
    glb = OUT / "continuous_servo_feeder.glb"
    assy.export(str(step), exportType="STEP")
    assy.export(str(glb), exportType="GLTF", tolerance=0.18, angularTolerance=0.14)
    exporters.export(cq.Compound.makeCompound(mesh), str(stl), tolerance=0.16, angularTolerance=0.12)
    summary = {
        "coordinate_system": "X-Y chassis plane; +Z upward; +X feed direction",
        "game_piece_geometry_included": False,
        "horizontal_belt_length_mm": JUNCTION_X - HORIZONTAL_X0,
        "incline_angle_deg": INCLINE_ANGLE_DEG,
        "clear_width_mm": FRAME_INNER_WIDTH,
        "horizontal_belt_lanes_y_mm": [-36, 36],
        "incline_belt_lanes_y_mm": [-12, 12],
        "belt_width_mm": BELT_WIDTH,
        "pinch_roller_od_mm": PINCH_ROLLER_OD,
        "pinch_travel_mm": PINCH_TRAVEL,
        "pinch_reduction_ratio": PINCH_REDUCTION,
        "nominal_conveyor_speed_at_100rpm_mps": round(math.pi * (PULLEY_OD / 1000) * 100 / 60, 3),
        "nominal_pinch_surface_speed_at_100rpm_mps": round(math.pi * (PINCH_ROLLER_OD / 1000) * (100 / PINCH_REDUCTION) / 60, 3),
        "continuous_rotation_servos": 2,
        "outputs": {"step": str(step), "stl": str(stl), "glb": str(glb)},
    }
    (OUT / "continuous_servo_feeder_parameters.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    export_all()
