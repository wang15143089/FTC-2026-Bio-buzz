"""Integrated opposed-flywheel launcher with continuous servo paddle feeder.

X-Y is the chassis plane, +Z is upward, +X is the feed/launch projection.
No POLLEN or NECTAR geometry is included. Motors and servos are envelopes.
All other prototype components are modeled in assembly detail. Units: mm.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import cadquery as cq
from cadquery import exporters


OUT = Path(__file__).resolve().parent / "output"
OUT.mkdir(parents=True, exist_ok=True)

ANGLE = 52.0
WHEEL_OD = 96.0
WHEEL_W = 24.0
FLYWHEEL_HALF_SPACING = 89.0  # NECTAR/open position; links retain 9 mm inward travel.
SHOOTER_ORIGIN = (130.0, 0.0, 210.0)
PADDLE_CENTER = (-28.0, 0.0, 67.0)
PADDLE_RADIUS = 57.0
CHANNEL_WIDTH = 108.0
SERVO_ENV = (41.0, 21.0, 40.0)
MOTOR_D = 38.0
MOTOR_L = 104.0

C = {
    "plate": cq.Color(0.16, 0.21, 0.28, 0.34),
    "base": cq.Color(0.16, 0.21, 0.28),
    "structure": cq.Color(0.70, 0.76, 0.84),
    "wheel": cq.Color(0.055, 0.06, 0.07),
    "hub": cq.Color(0.72, 0.74, 0.78),
    "shaft": cq.Color(0.58, 0.62, 0.68),
    "paddle": cq.Color(0.92, 0.54, 0.12),
    "flex": cq.Color(0.92, 0.68, 0.16),
    "guide": cq.Color(0.20, 0.56, 0.84, 0.48),
    "servo": cq.Color(0.58, 0.30, 0.74, 0.55),
    "motor": cq.Color(0.82, 0.36, 0.12, 0.48),
    "reference": cq.Color(0.18, 0.58, 0.35, 0.18),
}


def box(l, w, h, center=(0.0, 0.0, 0.0)):
    return cq.Workplane("XY").box(l, w, h, centered=(True, True, True)).translate(center).val()


def cyl_y(r, length, center=(0.0, 0.0, 0.0)):
    x, y, z = center
    return cq.Solid.makeCylinder(r, length, cq.Vector(x, y - length / 2, z), cq.Vector(0, 1, 0))


def cyl_z(r, length, center=(0.0, 0.0, 0.0)):
    x, y, z = center
    return cq.Solid.makeCylinder(r, length, cq.Vector(x, y, z - length / 2), cq.Vector(0, 0, 1))


def rod(a, b, r):
    av, bv = cq.Vector(*a), cq.Vector(*b)
    d = bv - av
    return cq.Solid.makeCylinder(r, d.Length, av, d.normalized())


def to_world(shape):
    return shape.rotate((0, 0, 0), (0, 1, 0), -ANGLE).translate(SHOOTER_ORIGIN)


def gecko(center_n, y):
    outer = cyl_y(46, WHEEL_W, (0, y, center_n)).cut(cyl_y(39.5, WHEEL_W + 2, (0, y, center_n)))
    core = cyl_y(15, WHEEL_W, (0, y, center_n)).cut(cyl_y(7.1, WHEEL_W + 2, (0, y, center_n)))
    wheel = outer.fuse(core)
    for a in range(0, 360, 30):
        spoke = box(27, WHEEL_W - 3, 5.5, (27, y, center_n)).rotate((0, y, center_n), (0, y + 1, center_n), a)
        wheel = wheel.fuse(spoke)
    for a in range(0, 360, 15):
        pad = box(4, WHEEL_W - 2, 6.5, (46, y, center_n)).rotate((0, y, center_n), (0, y + 1, center_n), a)
        wheel = wheel.fuse(pad)
    return wheel


def sonic_hub(center_n, y, outward):
    """8 mm shaft to 14 mm Gecko core adapter with 16 mm square bolt pattern."""
    hub = cyl_y(16, 9, (0, y + outward * 7.5, center_n)).cut(cyl_y(4.1, 12, (0, y + outward * 7.5, center_n)))
    flange = cyl_y(22, 3, (0, y + outward * 2.0, center_n)).cut(cyl_y(7.1, 5, (0, y + outward * 2.0, center_n)))
    hub = hub.fuse(flange)
    for dx in (-8, 8):
        for dz in (-8, 8):
            hub = hub.cut(cyl_y(2.1, 14, (dx, y + outward * 2.0, center_n + dz)))
    return hub


def bearing_block(center_n, y):
    p = box(42, 10, 38, (0, y, center_n)).cut(cyl_y(7.1, 14, (0, y, center_n)))
    for x in (-14, 14):
        p = p.cut(cyl_y(2.2, 14, (x, y, center_n)))
    return p


def motor_mount(center_n, side):
    y = side * 76
    p = box(58, 6, 58, (0, y, center_n)).cut(cyl_y(19.2, 12, (0, y, center_n)))
    for x in (-8, 8):
        for z in (-8, 8):
            p = p.cut(cyl_y(2.2, 12, (x, y, center_n + z)))
    return p


def paddle_rotor():
    cx, cy, cz = PADDLE_CENTER
    rotor = cyl_y(18, 34, PADDLE_CENTER).cut(cyl_y(4.1, 38, PADDLE_CENTER))
    parts = [("paddle_hub", rotor, C["hub"])]
    phase = 20.0
    for i, a in enumerate((phase, phase + 120, phase + 240)):
        arm = box(48, 18, 10, (cx + 31, 0, cz)).rotate(PADDLE_CENTER, (cx, 1, cz), a)
        hinge_center = cq.Vector(cx + 55 * math.cos(math.radians(a)), 0, cz + 55 * math.sin(math.radians(a)))
        hinge = cyl_y(6, 100, (hinge_center.x, 0, hinge_center.z)).cut(cyl_y(2.1, 104, (hinge_center.x, 0, hinge_center.z)))
        # Cross-channel paddle with a replaceable compliant TPU leading strip.
        blade = box(20, 96, 30, (cx + 61, 0, cz)).rotate(PADDLE_CENTER, (cx, 1, cz), a)
        flex = box(5, 100, 34, (cx + 72, 0, cz)).rotate(PADDLE_CENTER, (cx, 1, cz), a)
        parts.extend([
            (f"paddle_arm_{i+1}", arm, C["paddle"]),
            (f"paddle_hinge_{i+1}", hinge, C["shaft"]),
            (f"paddle_blade_{i+1}", blade, C["paddle"]),
            (f"paddle_flex_tip_{i+1}", flex, C["flex"]),
        ])
    return parts


def build():
    assy = cq.Assembly(name="paddle_feeder_opposed_flywheel_launcher")
    mesh = []

    def add(name, shape, color, meshable=True):
        assy.add(shape, name=name, color=color)
        if meshable:
            mesh.append(shape)

    for y in (-72, 72):
        rail = box(430, 18, 14, (25, y, 9))
        for x in (-170, -122, -74, -26, 22, 70, 118, 166, 214):
            rail = rail.cut(cyl_z(2.3, 20, (x, y, 9)))
        add(f"base_rail_{y:+d}", rail, C["base"])

    # Horizontal receiving channel. Upstream intake supplies balls; this module indexes them.
    x0, x1 = -190, -72
    add("horizontal_floor", box(x1 - x0, CHANNEL_WIDTH + 6, 3, ((x0 + x1) / 2, 0, 16)), C["guide"])
    add("horizontal_roof", box(x1 - x0 - 28, CHANNEL_WIDTH + 6, 3, ((x0 + x1 - 28) / 2, 0, 120)), C["guide"])
    for side in (-1, 1):
        wall = box(x1 - x0, 3, 108, ((x0 + x1) / 2, side * 55.5, 68))
        add(f"horizontal_wall_{side:+d}", wall, C["guide"])

    # Paddle rotor support plates, bearings and continuous-rotation servo mount.
    for side in (-1, 1):
        y = side * 62
        cheek = box(118, 6, 152, (-28, y, 78))
        cheek = cheek.cut(cyl_y(7.1, 12, PADDLE_CENTER))
        cheek = cheek.cut(cyl_y(33, 12, (-28, y, 99)))
        for x, z in [(-76, 20), (18, 20), (-76, 138), (18, 138)]:
            cheek = cheek.cut(cyl_y(2.3, 12, (x, y, z)))
        add(f"paddle_support_cheek_{side:+d}", cheek, C["structure"])
    add("paddle_shaft", cyl_y(4, 154, PADDLE_CENTER), C["shaft"])
    for name, shape, color in paddle_rotor():
        add(name, shape, color)

    # Supported direct servo drive: ServoBlock takes radial load, hub clamps the 8 mm shaft.
    servo_center = (PADDLE_CENTER[0], 112, PADDLE_CENTER[2])
    add("paddle_cr_servo_envelope", box(*SERVO_ENV, servo_center), C["servo"], False)
    sb = box(58, 6, 60, (servo_center[0], 76, servo_center[2])).cut(cyl_y(8.2, 12, (servo_center[0], 76, servo_center[2])))
    for x in (-23, 23):
        for z in (-24, 24):
            sb = sb.cut(cyl_y(2.2, 12, (servo_center[0] + x, 76, servo_center[2] + z)))
    add("paddle_servo_block", sb, C["plate"])
    add("paddle_shaft_hub", cyl_y(12, 16, (PADDLE_CENTER[0], 70, PADDLE_CENTER[2])).cut(cyl_y(4.1, 18, (PADDLE_CENTER[0], 70, PADDLE_CENTER[2]))), C["hub"])

    # Curved/segmented guide carries each paddle stroke into the 52-degree throat.
    segments = [
        ((4, 0, 35), 72, 18),
        ((47, 0, 62), 66, 34),
        ((83, 0, 103), 68, 46),
    ]
    for i, (center, length, ang) in enumerate(segments):
        floor = box(length, 108, 3, center).rotate(center, (center[0], 1, center[2]), -ang)
        add(f"rising_guide_floor_{i+1}", floor, C["guide"])
        for side in (-1, 1):
            wall_center = (center[0], side * 55.5, center[2] + 48)
            wall = box(length, 3, 96, wall_center).rotate(wall_center, (wall_center[0], wall_center[1] + 1, wall_center[2]), -ang)
            add(f"rising_guide_wall_{i+1}_{side:+d}", wall, C["guide"])

    # Two compliant one-way fingers prevent the indexed object rolling back into the rotor.
    for side in (-1, 1):
        finger = box(42, 1.2, 48, (80, side * 38, 127)).rotate((80, side * 38, 127), (80, side * 38 + 1, 127), -52)
        add(f"one_way_finger_{side:+d}", finger, cq.Color(0.76, 0.88, 0.96))

    # Fixed shooter frame in local coordinates, transformed to 52 degrees.
    for side in (-1, 1):
        y = side * 70
        outline = [(-105, -132), (78, -132), (125, -102), (125, 102), (78, 132), (-105, 132)]
        plate = cq.Workplane("XZ").polyline(outline).close().extrude(2, both=True).translate((0, y, 0)).val()
        plate = plate.cut(cyl_y(26, 10, (-55, y, 0)))
        for sign in (-1, 1):
            plate = plate.cut(cyl_y(8, 10, (0, y, sign * 89)))
        add(f"shooter_side_plate_{side:+d}", to_world(plate), C["plate"])

    wheel_y = (-15.0, 15.0)
    for sign, label in ((1, "upper"), (-1, "lower")):
        n = sign * FLYWHEEL_HALF_SPACING
        add(f"flywheel_shaft_{label}", to_world(cyl_y(4, 194, (0, 0, n))), C["shaft"])
        for i, y in enumerate(wheel_y):
            add(f"gecko_flywheel_{label}_{i+1}", to_world(gecko(n, y)), C["wheel"])
            outward = -1 if y < 0 else 1
            add(f"sonic_hub_{label}_{i+1}", to_world(sonic_hub(n, y, outward)), C["hub"])
        for side in (-1, 1):
            add(f"bearing_block_{label}_{side:+d}", to_world(bearing_block(n, side * 63)), C["structure"])
        motor_side = 1 if sign > 0 else -1
        add(f"motor_mount_{label}", to_world(motor_mount(n, motor_side)), C["structure"])
        my = motor_side * (76 + MOTOR_L / 2 + 7)
        add(f"motor_envelope_{label}", to_world(cyl_y(MOTOR_D / 2, MOTOR_L, (0, my, n))), C["motor"], False)

    # Symmetric two-link gap adjustment retained from the opposed-wheel design.
    servo_u, servo_y = -76, 110
    add("gap_servo_envelope", to_world(box(*SERVO_ENV, (servo_u, servo_y, 0))), C["servo"], False)
    add("gap_double_horn", to_world(cyl_y(22, 5, (servo_u, 124, 0))), C["flex"])
    for sign, label in ((1, "upper"), (-1, "lower")):
        a = (servo_u, 124, sign * 18)
        b = (-18, 124, sign * FLYWHEEL_HALF_SPACING)
        add(f"gap_link_{label}", to_world(rod(a, b, 3)), C["flex"])

    # Final guide aligns the paddle-fed path to the flywheel centerline.
    for z in (-56.5, 56.5):
        add(f"shooter_throat_{z:+.0f}", to_world(box(125, 108, 3, (-45, 0, z))), C["guide"])

    return assy, mesh


def export_all():
    assy, mesh = build()
    step = OUT / "paddle_feeder_opposed_flywheel_launcher.step"
    stl = OUT / "paddle_feeder_opposed_flywheel_launcher.stl"
    glb = OUT / "paddle_feeder_opposed_flywheel_launcher.glb"
    assy.export(str(step), exportType="STEP")
    assy.export(str(glb), exportType="GLTF", tolerance=0.2, angularTolerance=0.15)
    exporters.export(cq.Compound.makeCompound(mesh), str(stl), tolerance=0.18, angularTolerance=0.14)
    summary = {
        "coordinate_system": "X-Y chassis plane; +Z upward",
        "game_piece_geometry_included": False,
        "launcher": "two opposed flywheel shafts; two 96 mm Gecko wheels per shaft",
        "feeder": "three flexible paddles directly driven by one continuous-rotation servo",
        "paddle_radius_mm": PADDLE_RADIUS,
        "paddles": 3,
        "recommended_servo_speed_rpm": [25, 40],
        "theoretical_feed_rate_objects_per_second": [1.25, 2.0],
        "channel_clear_width_mm": CHANNEL_WIDTH,
        "shooter_angle_deg": ANGLE,
        "outputs": {"step": str(step), "stl": str(stl), "glb": str(glb)},
    }
    (OUT / "paddle_feeder_launcher_parameters.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    export_all()
