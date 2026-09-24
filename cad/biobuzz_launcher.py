"""Parametric preliminary CAD for a BIOBUZZ dual Gecko-wheel launcher.

Coordinate convention (required by the design brief):
    X-Y = chassis plane
    +Z  = upward
    +X  = nominal launch direction projected onto the chassis plane
    +Y  = launcher width / flywheel shaft direction

The shooter centerline is inclined by SHOOTER_ANGLE_DEG above the X-Y plane.
All dimensions are millimetres.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import cadquery as cq
from cadquery import exporters


OUT = Path(__file__).resolve().parent / "output"
OUT.mkdir(parents=True, exist_ok=True)

# --------------------------- Design parameters ---------------------------
SHOOTER_ANGLE_DEG = 52.0
WHEEL_OD = 96.0
WHEEL_WIDTH = 24.0
WHEEL_COUNT_PER_SHAFT = 2
WHEEL_AXIAL_GAP = 6.0
POLLEN_GAP = 64.0
NECTAR_GAP = 82.0
CHANNEL_CLEAR_WIDTH = 104.0
CHANNEL_CLEAR_HEIGHT = 110.0
SIDE_PLATE_OFFSET = 70.0
SIDE_PLATE_THICKNESS = 4.0
ORIGIN_WORLD = (210.0, 0.0, 220.0)

# Motor and servo are envelopes only.
MOTOR_ENVELOPE_DIAMETER = 38.0
MOTOR_ENVELOPE_LENGTH = 104.0
SERVO_ENVELOPE = (41.0, 21.0, 40.0)  # local U, Y, N

# Horizontal feeder prototype envelopes.
HORIZONTAL_FEED_CLEAR_WIDTH = 104.0
HORIZONTAL_FEED_CENTER_Z = 56.0
HORIZONTAL_FEED_X0 = -105.0
HORIZONTAL_FEED_X1 = 58.0
KICK_ROLLER_OD = 72.0
GUIDE_ROLLER_OD = 48.0


COLORS = {
    "structure": cq.Color(0.72, 0.76, 0.82),
    "plate": cq.Color(0.16, 0.21, 0.28),
    "channel": cq.Color(0.22, 0.55, 0.82),
    "wheel": cq.Color(0.08, 0.08, 0.09),
    "hub": cq.Color(0.78, 0.80, 0.84),
    "shaft": cq.Color(0.65, 0.68, 0.72),
    "motor_env": cq.Color(0.78, 0.42, 0.15, 0.55),
    "servo_env": cq.Color(0.58, 0.30, 0.74, 0.55),
    "linkage": cq.Color(0.92, 0.66, 0.12),
    "chassis": cq.Color(0.18, 0.58, 0.35, 0.22),
    "pollen": cq.Color(0.96, 0.80, 0.08, 0.55),
    "nectar": cq.Color(0.82, 0.12, 0.16, 0.50),
}


def box(l: float, w: float, h: float, center=(0.0, 0.0, 0.0)) -> cq.Shape:
    return (
        cq.Workplane("XY")
        .box(l, w, h, centered=(True, True, True))
        .translate(center)
        .val()
    )


def cyl_y(radius: float, length: float, center=(0.0, 0.0, 0.0)) -> cq.Shape:
    x, y, z = center
    return cq.Solid.makeCylinder(
        radius,
        length,
        cq.Vector(x, y - length / 2.0, z),
        cq.Vector(0, 1, 0),
    )


def cyl_z(radius: float, height: float, center=(0.0, 0.0, 0.0)) -> cq.Shape:
    x, y, z = center
    return cq.Solid.makeCylinder(
        radius,
        height,
        cq.Vector(x, y, z - height / 2.0),
        cq.Vector(0, 0, 1),
    )


def rod_between(a, b, radius: float) -> cq.Shape:
    va = cq.Vector(*a)
    vb = cq.Vector(*b)
    vec = vb - va
    return cq.Solid.makeCylinder(radius, vec.Length, va, vec.normalized())


def rounded_plate_local(center_u: float, center_n: float, size_u: float, size_n: float,
                        thickness_y: float, y: float, radius: float = 5.0) -> cq.Shape:
    # Edge fillets are intentionally limited to the four long edges so the
    # part remains robust across OpenCascade versions.
    p = box(size_u, thickness_y, size_n, (center_u, y, center_n))
    try:
        return cq.Workplane(obj=p).edges("|Y").fillet(min(radius, thickness_y * 0.45)).val()
    except Exception:
        return p


def world(shape: cq.Shape) -> cq.Shape:
    """Map local (U,Y,N) shooter coordinates into chassis (X,Y,Z)."""
    return (
        shape.rotate((0, 0, 0), (0, 1, 0), -SHOOTER_ANGLE_DEG)
        .translate(ORIGIN_WORLD)
    )


def local_side_plate(y: float) -> cq.Shape:
    outline = [
        (-176, -132),
        (82, -132),
        (142, -104),
        (142, 104),
        (82, 132),
        (-176, 132),
    ]
    plate = (
        cq.Workplane("XZ")
        .polyline(outline)
        .close()
        .extrude(SIDE_PLATE_THICKNESS / 2.0, both=True)
        .translate((0, y, 0))
        .val()
    )

    # Weight-reduction windows; material is retained around rails, bearings and mounts.
    windows = [
        cyl_y(34, 12, (-118, y, 0)),
        cyl_y(23, 12, (91, y, 0)),
        box(66, 12, 34, (-48, y, 0)),
    ]
    for cut in windows:
        plate = plate.cut(cut)

    # Elongated shaft slots: 80 mm -> 89 mm half center spacing plus bearing clearance.
    for sign in (-1, 1):
        slot = (
            cyl_y(8, 12, (0, y, sign * 79.0))
            .fuse(cyl_y(8, 12, (0, y, sign * 90.0)))
            .fuse(box(16, 12, 11, (0, y, sign * 84.5)))
        )
        plate = plate.cut(slot)

    # M4 clearance holes along the structural perimeter.
    for u, n in [(-155, -110), (-155, 110), (115, -82), (115, 82), (-75, -112), (-75, 112)]:
        plate = plate.cut(cyl_y(2.3, 12, (u, y, n)))
    return plate


def gecko_wheel_local(center_n: float, y: float) -> cq.Shape:
    """Detailed but non-manufacturer-exact Gecko wheel representation."""
    # Flexible outer ring and center hub.
    outer = cyl_y(46.0, WHEEL_WIDTH, (0, y, center_n)).cut(
        cyl_y(39.5, WHEEL_WIDTH + 2, (0, y, center_n))
    )
    hub = cyl_y(15.0, WHEEL_WIDTH, (0, y, center_n)).cut(
        cyl_y(7.1, WHEEL_WIDTH + 2, (0, y, center_n))
    )

    wheel = outer.fuse(hub)

    # Twelve flexible radial spokes.
    for angle in range(0, 360, 30):
        spoke = box(27.0, WHEEL_WIDTH - 3.0, 5.5, (27.0, y, center_n))
        spoke = spoke.rotate((0, y, center_n), (0, 1, 0), angle)
        wheel = wheel.fuse(spoke)

    # Twenty-four outer grip pads; their tips define the nominal 96 mm OD.
    for angle in range(0, 360, 15):
        pad = box(4.0, WHEEL_WIDTH - 2.0, 6.5, (46.0, y, center_n))
        pad = pad.rotate((0, y, center_n), (0, 1, 0), angle)
        wheel = wheel.fuse(pad)
    return wheel


def carriage_local(center_n: float, y: float) -> cq.Shape:
    block = rounded_plate_local(0, center_n, 42, 38, 10, y, radius=4)
    block = block.cut(cyl_y(7.1, 18, (0, y, center_n)))
    # Two M4 carriage/rail holes.
    for du in (-14, 14):
        block = block.cut(cyl_y(2.2, 18, (du, y, center_n)))
    return block


def motor_mount_local(center_n: float, side: int) -> cq.Shape:
    y = side * (SIDE_PLATE_OFFSET + 5.5)
    plate = rounded_plate_local(0, center_n, 58, 58, 6, y, radius=6)
    plate = plate.cut(cyl_y(19.2, 14, (0, y, center_n)))
    for du in (-8, 8):
        for dn in (-8, 8):
            plate = plate.cut(cyl_y(2.2, 14, (du, y, center_n + dn)))
    # Two triangular-ish rectangular braces tying the motor face to the carriage.
    brace_a = box(34, 16, 5, (-12, side * (SIDE_PLATE_OFFSET + 1), center_n + 25))
    brace_b = box(34, 16, 5, (-12, side * (SIDE_PLATE_OFFSET + 1), center_n - 25))
    return plate.fuse(brace_a).fuse(brace_b)


def channel_parts_local() -> list[tuple[str, cq.Shape, cq.Color]]:
    parts: list[tuple[str, cq.Shape, cq.Color]] = []

    # Short inclined receiver after the horizontal-to-inclined transition.
    u0, u1 = -145.0, -70.0
    length = u1 - u0
    wall_delta_y = (58.0 - 52.0)
    wall_angle = math.degrees(math.atan2(wall_delta_y, length))
    wall_len = math.hypot(length, wall_delta_y)
    for side in (-1, 1):
        wall = box(wall_len, 3.0, CHANNEL_CLEAR_HEIGHT + 8, ((u0 + u1) / 2, side * 55.0, 0))
        wall = wall.rotate(((u0 + u1) / 2, side * 55.0, 0),
                           ((u0 + u1) / 2, side * 55.0, 1),
                           -side * wall_angle)
        parts.append((f"input_sidewall_{side:+d}", wall, COLORS["channel"]))

    parts.append(("input_floor", box(length, 116, 3, ((u0 + u1) / 2, 0, -56.5)), COLORS["channel"]))
    parts.append(("input_roof", box(length, 116, 3, ((u0 + u1) / 2, 0, 56.5)), COLORS["channel"]))

    # Flexible centering leaves: relaxed for Pollen, deflect for Nectar.
    for side in (-1, 1):
        leaf = box(105, 1.2, 48, (-124, side * 39.0, 0))
        leaf = leaf.rotate((-176, side * 39.0, 0), (-176, side * 39.0, 1), side * 6.0)
        parts.append((f"centering_leaf_{side:+d}", leaf, cq.Color(0.75, 0.86, 0.95)))

    # Front output guide. It is kept wider than Nectar and establishes the launch vector.
    out_u0, out_u1 = 70.0, 220.0
    out_len = out_u1 - out_u0
    parts.append(("output_floor", box(out_len, 108, 3, ((out_u0 + out_u1) / 2, 0, -56.5)), COLORS["channel"]))
    parts.append(("output_roof", box(out_len, 108, 3, ((out_u0 + out_u1) / 2, 0, 56.5)), COLORS["channel"]))
    for side in (-1, 1):
        parts.append((
            f"output_sidewall_{side:+d}",
            box(out_len, 3, CHANNEL_CLEAR_HEIGHT + 8, ((out_u0 + out_u1) / 2, side * 52.5, 0)),
            COLORS["channel"],
        ))

    # Four replaceable UHMW wear strips near wheel exit.
    for n in (-50.0, 50.0):
        for y in (-47.0, 47.0):
            parts.append((
                f"wear_strip_{int(n)}_{int(y)}",
                box(74, 6, 5, (104, y, n)),
                cq.Color(0.90, 0.90, 0.86),
            ))
    return parts


def horizontal_feed_parts(mode: str) -> list[tuple[str, cq.Shape, cq.Color, bool]]:
    """Low horizontal conveyor and powered elbow feeding the inclined shooter.

    These are intentionally envelope-level components. The channel and rollers
    establish the ball path; detailed bearing, belt and motor hardware is left
    for the next packaging iteration.
    """
    parts: list[tuple[str, cq.Shape, cq.Color, bool]] = []
    x0, x1 = HORIZONTAL_FEED_X0, HORIZONTAL_FEED_X1
    ball_d = 71.0 if mode == "pollen" else 91.0
    # Each ball rests on the same belt; the larger ball therefore has a higher centerline.
    zc = 16.0 + ball_d / 2.0
    length = x1 - x0

    # Horizontal conveyor enclosure: 104 mm clear width, 100 mm clear height.
    parts.append(("horizontal_feed_floor", box(length, 112, 3, ((x0 + x1) / 2, 0, 5.0)), COLORS["channel"], True))
    # Leave the final 65 mm open for the swing-arm powered roller.
    roof_end = x1 - 65.0
    parts.append((
        "horizontal_feed_roof",
        box(roof_end - x0, 112, 3, ((x0 + roof_end) / 2, 0, 117.0)),
        COLORS["channel"], True,
    ))
    for side in (-1, 1):
        parts.append((
            f"horizontal_feed_side_{side:+d}",
            box(length, 3, 115, ((x0 + x1) / 2, side * 53.5, 61.0)),
            COLORS["channel"], True,
        ))

    # Belt/roller-bed envelope and its two pulleys.
    parts.append(("horizontal_belt_envelope", box(length - 18, 92, 8, ((x0 + x1) / 2, 0, 12)), cq.Color(0.12, 0.15, 0.18), True))
    for x in (x0 + 10, x1 - 10):
        parts.append((f"horizontal_belt_pulley_{int(x)}", cyl_y(16, 96, (x, 0, 16)), COLORS["shaft"], True))

    # Transition connects the horizontal path to the rear of the 52-deg chute.
    u_transition = -145.0
    local_end = world(cq.Vertex.makeVertex(u_transition, 0, 0))
    end_pt = local_end.Center()
    # The guide is one fixed part for both ball sizes. Different ball-center
    # heights are absorbed by its 110 mm clearance and the powered swing arm.
    start = (x1, 0.0, HORIZONTAL_FEED_CENTER_Z)
    end = (end_pt.x, 0.0, end_pt.z)
    dx, dz = end[0] - start[0], end[2] - start[2]
    beta = math.degrees(math.atan2(dz, dx))
    trans_len = math.hypot(dx, dz)
    cx, cz = (start[0] + end[0]) / 2, (start[2] + end[2]) / 2

    def inclined_box(size, center, angle_deg):
        s = box(*size, center)
        return s.rotate((center[0], center[1], center[2]), (center[0], center[1] + 1, center[2]), -angle_deg)

    # Top/bottom guide surfaces offset from the centerline normal.
    nx, nz = -math.sin(math.radians(beta)), math.cos(math.radians(beta))
    for sign in (-1, 1):
        c = (cx + sign * 56.0 * nx, 0.0, cz + sign * 56.0 * nz)
        parts.append((
            f"transition_guide_{sign:+d}",
            inclined_box((trans_len + 10, 108, 3), c, beta),
            COLORS["channel"], True,
        ))
    for side in (-1, 1):
        parts.append((
            f"transition_side_{side:+d}",
            inclined_box((trans_len + 10, 3, 112), (cx, side * 52.5, cz), beta),
            COLORS["channel"], True,
        ))

    # Spring-loaded powered roller contacts the upper-rear quadrant and drives
    # the ball forward/upward. Its swing-arm position changes with ball size.
    contact_dx = 25.0
    desired_centers = ball_d / 2.0 + KICK_ROLLER_OD / 2.0 - 7.0
    contact_dz = math.sqrt(max(desired_centers ** 2 - contact_dx ** 2, 1.0))
    kick_center = (x1 - contact_dx, 0.0, zc + contact_dz)
    # Lower passive roller supports the turn while the powered roller supplies traction.
    guide_center = (x1 + 19.0, 0.0, 24.0)
    parts.append(("kick_roller_envelope", cyl_y(KICK_ROLLER_OD / 2, 100, kick_center), COLORS["linkage"], True))
    parts.append(("upper_guide_roller_envelope", cyl_y(GUIDE_ROLLER_OD / 2, 100, guide_center), COLORS["shaft"], True))

    # Roller support cheeks, pivot arms and motor envelope.
    for side in (-1, 1):
        y = side * 58.0
        cheek = box(92, 6, 156, (x1 - 3, y, 78))
        cheek = cheek.cut(cyl_y(7.1, 12, (guide_center[0], y, guide_center[2])))
        parts.append((f"kick_support_cheek_{side:+d}", cheek, COLORS["structure"], True))
        arm = rod_between((x1 - 69, y, 151), (kick_center[0], y, kick_center[2]), 5.0)
        parts.append((f"spring_guide_arm_{side:+d}", arm, COLORS["structure"], True))

    feed_motor_y = 58.0 + MOTOR_ENVELOPE_LENGTH / 2 + 8.0
    parts.append((
        "feed_motor_envelope",
        cyl_y(MOTOR_ENVELOPE_DIAMETER / 2, MOTOR_ENVELOPE_LENGTH, (kick_center[0], feed_motor_y, kick_center[2])),
        COLORS["motor_env"], True,
    ))
    # Compact servo envelope for a future single-ball gate, placed outside the channel.
    parts.append((
        "feed_gate_servo_envelope",
        box(*SERVO_ENVELOPE, (x0 + 62, 70, 87)),
        COLORS["servo_env"], True,
    ))
    parts.append((
        "feed_gate_flap_envelope",
        box(4, 98, 50, (x0 + 79, 0, 82)),
        COLORS["linkage"], True,
    ))

    # Three translucent ball envelopes make the intended continuous path explicit.
    ball_color = COLORS["pollen"] if mode == "pollen" else COLORS["nectar"]
    path_points = [
        (x0 + 38, 0, zc),
        (x1 - 17, 0, zc),
        (cx, 0, cz),
    ]
    for i, p in enumerate(path_points):
        parts.append((f"horizontal_path_ball_{i+1}", cq.Solid.makeSphere(ball_d / 2, cq.Vector(*p)), ball_color, True))
    return parts


def base_and_gussets() -> list[tuple[str, cq.Shape, cq.Color]]:
    parts: list[tuple[str, cq.Shape, cq.Color]] = []

    chassis = box(620, 320, 4, (170, 0, -2))
    parts.append(("00_chassis_xy_reference", chassis, COLORS["chassis"]))

    for side in (-1, 1):
        rail = box(440, 20, 16, (110, side * 76, 10))
        for x in (-86, -38, 10, 58, 106, 154, 202, 250, 298):
            rail = rail.cut(cyl_z(2.3, 24, (x, side * 76, 10)))
        parts.append((f"base_rail_{side:+d}", rail, COLORS["structure"]))

        # World-coordinate triangular gusset, 4 mm sheet.
        gusset = (
            cq.Workplane("XZ")
            .polyline([(48, 18), (190, 18), (120, 128)])
            .close()
            .extrude(2, both=True)
            .translate((0, side * 72, 0))
            .val()
        )
        gusset = gusset.cut(cyl_y(18, 8, (120, side * 72, 63)))
        for x in (68, 164):
            gusset = gusset.cut(cyl_y(2.3, 8, (x, side * 72, 22)))
        parts.append((f"angle_gusset_{side:+d}", gusset, COLORS["plate"]))
    return parts


def build(mode: str) -> tuple[cq.Assembly, list[cq.Shape]]:
    if mode not in {"pollen", "nectar"}:
        raise ValueError("mode must be 'pollen' or 'nectar'")

    gap = POLLEN_GAP if mode == "pollen" else NECTAR_GAP
    half_axis = (WHEEL_OD + gap) / 2.0
    horn_angle = 60.0 if mode == "pollen" else 0.0
    assy = cq.Assembly(name=f"biobuzz_launcher_{mode}")
    export_shapes: list[cq.Shape] = []

    def add(name: str, shape: cq.Shape, color: cq.Color, local=True, include_mesh=True):
        final = world(shape) if local else shape
        assy.add(final, name=name, color=color)
        if include_mesh:
            export_shapes.append(final)

    # Fixed structure and base.
    for name, shape, color in base_and_gussets():
        add(name, shape, color, local=False, include_mesh=name != "00_chassis_xy_reference")
    for name, shape, color, include_mesh in horizontal_feed_parts(mode):
        add(name, shape, color, local=False, include_mesh=include_mesh)
    for side in (-1, 1):
        add(f"main_side_plate_{side:+d}", local_side_plate(side * SIDE_PLATE_OFFSET), COLORS["plate"])
    for u in (-162, 128):
        for n in (-118, 118):
            add(f"crossmember_{u}_{n}", box(20, 136, 16, (u, 0, n)), COLORS["structure"])

    # Guide rails and moving carriage blocks.
    for side in (-1, 1):
        y = side * (SIDE_PLATE_OFFSET - 7.0)
        for sign in (-1, 1):
            add(f"slide_rail_{side:+d}_{sign:+d}", box(30, 5, 58, (0, y, sign * 84.5)), COLORS["shaft"])
            add(f"carriage_{side:+d}_{sign:+d}", carriage_local(sign * half_axis, y), COLORS["structure"])

    # Wheels, shafts, bearing collars and motor brackets/envelopes.
    wheel_y_positions = (-(WHEEL_WIDTH + WHEEL_AXIAL_GAP) / 2.0,
                          (WHEEL_WIDTH + WHEEL_AXIAL_GAP) / 2.0)
    for sign, label in ((1, "upper"), (-1, "lower")):
        n = sign * half_axis
        add(f"shaft_{label}", cyl_y(4.0, 190, (0, 0, n)), COLORS["shaft"])
        for i, wy in enumerate(wheel_y_positions):
            add(f"gecko_{label}_{i+1}", gecko_wheel_local(n, wy), COLORS["wheel"])
        for side in (-1, 1):
            add(f"bearing_collar_{label}_{side:+d}",
                cyl_y(11, 8, (0, side * 62, n)).cut(cyl_y(7.1, 10, (0, side * 62, n))),
                COLORS["hub"])

        motor_side = 1 if sign > 0 else -1
        add(f"motor_mount_{label}", motor_mount_local(n, motor_side), COLORS["structure"])
        motor_y = motor_side * (SIDE_PLATE_OFFSET + MOTOR_ENVELOPE_LENGTH / 2.0 + 10.0)
        motor_env = cyl_y(MOTOR_ENVELOPE_DIAMETER / 2.0, MOTOR_ENVELOPE_LENGTH, (0, motor_y, n))
        add(f"motor_envelope_{label}", motor_env, COLORS["motor_env"], include_mesh=False)

    # Servo bracket, envelope, horn and two adjustable links.
    servo_u, servo_y, servo_n = -98.0, SIDE_PLATE_OFFSET + 40.0, 0.0
    bracket = box(70, 5, 72, (servo_u, SIDE_PLATE_OFFSET + 6.5, servo_n))
    bracket = bracket.cut(box(45, 12, 43, (servo_u, SIDE_PLATE_OFFSET + 6.5, servo_n)))
    for du in (-28, 28):
        for dn in (-29, 29):
            bracket = bracket.cut(cyl_y(2.2, 14, (servo_u + du, SIDE_PLATE_OFFSET + 6.5, servo_n + dn)))
    add("servo_bracket", bracket, COLORS["structure"])
    add("servo_envelope", box(*SERVO_ENVELOPE, (servo_u, servo_y, servo_n)), COLORS["servo_env"], include_mesh=False)

    horn_y = SIDE_PLATE_OFFSET + 54.0
    horn = cyl_y(22.0, 5.0, (servo_u, horn_y, 0)).cut(cyl_y(3.0, 8, (servo_u, horn_y, 0)))
    add("servo_double_horn", horn, COLORS["linkage"])

    phi = math.radians(horn_angle)
    top_pin = (servo_u + 18 * math.sin(phi), horn_y, 18 * math.cos(phi))
    bottom_pin = (servo_u - 18 * math.sin(phi), horn_y, -18 * math.cos(phi))
    top_carriage_pin = (-18.0, horn_y, half_axis)
    bottom_carriage_pin = (-18.0, horn_y, -half_axis)
    for label, a, b in (("upper", top_pin, top_carriage_pin), ("lower", bottom_pin, bottom_carriage_pin)):
        add(f"link_rod_{label}", rod_between(a, b, 3.0), COLORS["linkage"])
        add(f"link_ball_{label}_servo", cq.Solid.makeSphere(5.2, cq.Vector(*a)), COLORS["linkage"])
        add(f"link_ball_{label}_carriage", cq.Solid.makeSphere(5.2, cq.Vector(*b)), COLORS["linkage"])

    # Ball channels and a translucent reference ball at the launcher center.
    for name, shape, color in channel_parts_local():
        add(name, shape, color)
    ball_d = 71.0 if mode == "pollen" else 91.0
    ball_color = COLORS["pollen"] if mode == "pollen" else COLORS["nectar"]
    add(f"{mode}_reference_ball", cq.Solid.makeSphere(ball_d / 2.0, cq.Vector(0, 0, 0)), ball_color, include_mesh=False)

    return assy, export_shapes


def export_mode(mode: str) -> dict:
    assy, mesh_shapes = build(mode)
    step_path = OUT / f"biobuzz_launcher_horizontal_feed_{mode}.step"
    stl_path = OUT / f"biobuzz_launcher_horizontal_feed_{mode}.stl"
    glb_path = OUT / f"biobuzz_launcher_horizontal_feed_{mode}.glb"
    assy.export(str(step_path), exportType="STEP")
    assy.export(str(glb_path), exportType="GLTF", tolerance=0.22, angularTolerance=0.18)
    compound = cq.Compound.makeCompound(mesh_shapes)
    exporters.export(compound, str(stl_path), tolerance=0.18, angularTolerance=0.15)
    return {
        "mode": mode,
        "step": str(step_path),
        "stl": str(stl_path),
        "glb": str(glb_path),
        "gap_mm": POLLEN_GAP if mode == "pollen" else NECTAR_GAP,
        "axis_spacing_mm": WHEEL_OD + (POLLEN_GAP if mode == "pollen" else NECTAR_GAP),
    }


def ballistic_summary() -> dict:
    # Nominal geometry used to select the assembly angle.
    target_height = 1.15
    exit_height = 0.34
    horizontal_distance = 1.50
    dy = target_height - exit_height
    x = horizontal_distance
    g = 9.81
    energy_min_angle = math.degrees(math.atan2(dy + math.hypot(x, dy), x))

    def speed_for_angle(deg: float) -> float:
        a = math.radians(deg)
        denom = 2 * math.cos(a) ** 2 * (x * math.tan(a) - dy)
        return math.sqrt(g * x * x / denom)

    return {
        "coordinate_system": "X-Y chassis plane; +Z upward; +X launch projection",
        "modeled_angle_deg": SHOOTER_ANGLE_DEG,
        "nominal_target_height_m": target_height,
        "nominal_exit_height_m": exit_height,
        "nominal_horizontal_distance_m": horizontal_distance,
        "vacuum_energy_minimum_angle_deg": round(energy_min_angle, 2),
        "vacuum_speed_at_modeled_angle_mps": round(speed_for_angle(SHOOTER_ANGLE_DEG), 3),
        "design_reason": (
            "52 deg is lower than the ideal-vacuum minimum-energy angle to shorten flight time, "
            "reduce perforated-ball drag sensitivity, keep the assembly below the starting envelope, "
            "and preserve a useful 42-58 deg slotted adjustment range."
        ),
    }


if __name__ == "__main__":
    results = [export_mode("pollen"), export_mode("nectar")]
    summary = {
        "units": "mm unless noted",
        "parameters": {
            "wheel_od": WHEEL_OD,
            "wheel_width": WHEEL_WIDTH,
            "wheels_per_shaft": WHEEL_COUNT_PER_SHAFT,
            "pollen_gap": POLLEN_GAP,
            "nectar_gap": NECTAR_GAP,
            "channel_clear_width": CHANNEL_CLEAR_WIDTH,
            "channel_clear_height": CHANNEL_CLEAR_HEIGHT,
            "motor_envelope_diameter": MOTOR_ENVELOPE_DIAMETER,
            "motor_envelope_length": MOTOR_ENVELOPE_LENGTH,
            "servo_envelope": SERVO_ENVELOPE,
            "horizontal_feed_clear_width": HORIZONTAL_FEED_CLEAR_WIDTH,
            "horizontal_feed_center_height": HORIZONTAL_FEED_CENTER_Z,
            "horizontal_feed_length": HORIZONTAL_FEED_X1 - HORIZONTAL_FEED_X0,
            "kick_roller_od": KICK_ROLLER_OD,
            "guide_roller_od": GUIDE_ROLLER_OD,
        },
        "ballistics": ballistic_summary(),
        "exports": results,
    }
    (OUT / "design_parameters.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=True))
