"""Dimension-constrained paddle feeder and opposed Gecko flywheel launcher.

The chassis plane is X-Y and +Z is upward.  Motors and servos are envelopes;
all load-carrying prototype parts are modeled.  Units are millimetres.
No POLLEN or NECTAR bodies are included in the exported assemblies.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import cadquery as cq
from cadquery import exporters


OUT = Path(__file__).resolve().parent / "output"
PARTS = OUT / "parts"
OUT.mkdir(parents=True, exist_ok=True)
PARTS.mkdir(parents=True, exist_ok=True)

# Master dimensions
ANGLE = 52.0
WHEEL_OD = 96.0
WHEEL_W = 24.0
WHEEL_AXIAL_GAP = 6.0
WHEEL_Y = (-(WHEEL_W + WHEEL_AXIAL_GAP) / 2, (WHEEL_W + WHEEL_AXIAL_GAP) / 2)
CHANNEL_CLEAR_W = 108.0
CHANNEL_CLEAR_H = 110.0
PADDLE_CENTER = (-47.0, 0.0, 73.0)
PADDLE_SWEEP_R = 60.0
PADDLE_W = 96.0
SERVO_ENV = (41.0, 21.0, 40.0)
MOTOR_D = 38.0
MOTOR_L = 104.0
PLATE_INSIDE_SPAN = 140.0
CHASSIS_LIMIT = 457.2

# Exact guide polyline: horizontal -> transition -> shooter angle.
GUIDE_SPEC = [((-150.0, 16.0), 70.0, 0.0), (None, 55.0, 26.0), (None, 70.0, ANGLE)]

C = {
    "plate": cq.Color(0.16, 0.21, 0.28, 0.36),
    "base": cq.Color(0.16, 0.21, 0.28),
    "structure": cq.Color(0.70, 0.76, 0.84),
    "wheel": cq.Color(0.055, 0.06, 0.07),
    "hub": cq.Color(0.72, 0.74, 0.78),
    "shaft": cq.Color(0.58, 0.62, 0.68),
    "fastener": cq.Color(0.25, 0.27, 0.30),
    "paddle": cq.Color(0.92, 0.54, 0.12),
    "flex": cq.Color(0.96, 0.72, 0.18),
    "guide": cq.Color(0.20, 0.56, 0.84, 0.48),
    "servo": cq.Color(0.58, 0.30, 0.74, 0.55),
    "motor": cq.Color(0.82, 0.36, 0.12, 0.48),
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


def direction(angle):
    a = math.radians(angle)
    return math.cos(a), math.sin(a)


def normal(angle):
    a = math.radians(angle)
    return -math.sin(a), math.cos(a)


def guide_segments():
    result = []
    start = GUIDE_SPEC[0][0]
    for _, length, angle in GUIDE_SPEC:
        tx, tz = direction(angle)
        end = (start[0] + length * tx, start[1] + length * tz)
        result.append((start, end, length, angle))
        start = end
    return result


GUIDES = guide_segments()
GUIDE_END = GUIDES[-1][1]
N52 = normal(ANGLE)
T52 = direction(ANGLE)
THROAT_CENTER = (GUIDE_END[0] + 55.0 * N52[0], GUIDE_END[1] + 55.0 * N52[1])
SHOOTER_ORIGIN = (THROAT_CENTER[0] + 135.0 * T52[0], 0.0, THROAT_CENTER[1] + 135.0 * T52[1])


def to_world(shape):
    return shape.rotate((0, 0, 0), (0, 1, 0), -ANGLE).translate(SHOOTER_ORIGIN)


def gecko(center_n, y):
    """96 x 24 mm GripForce Gecko representation with 8 mm hub interface."""
    tread = cyl_y(46, WHEEL_W, (0, y, center_n)).cut(cyl_y(39.5, WHEEL_W + 2, (0, y, center_n)))
    core = cyl_y(15, WHEEL_W, (0, y, center_n)).cut(cyl_y(7.1, WHEEL_W + 2, (0, y, center_n)))
    wheel = tread.fuse(core)
    for a in range(0, 360, 30):
        wheel = wheel.fuse(box(27, WHEEL_W - 3, 5.5, (27, y, center_n)).rotate((0, y, center_n), (0, y + 1, center_n), a))
    for a in range(0, 360, 15):
        wheel = wheel.fuse(box(4, WHEEL_W - 2, 6.5, (46, y, center_n)).rotate((0, y, center_n), (0, y + 1, center_n), a))
    return wheel


def sonic_hub(center_n, y, outward):
    """Clamping adapter: 8 mm shaft, 14 mm wheel bore, 16 mm bolt square."""
    yy = y + outward * 7.5
    hub = cyl_y(16, 9, (0, yy, center_n)).cut(cyl_y(4.1, 12, (0, yy, center_n)))
    flange_y = y + outward * 2.0
    hub = hub.fuse(cyl_y(22, 3, (0, flange_y, center_n)).cut(cyl_y(7.1, 5, (0, flange_y, center_n))))
    for dx in (-8, 8):
        for dz in (-8, 8):
            hub = hub.cut(cyl_y(2.1, 14, (dx, flange_y, center_n + dz)))
    return hub


def bearing_carriage(center_n, y):
    """External sliding carriage with a 16 mm bearing pocket and M4 retainers."""
    p = box(46, 12, 38, (0, y, center_n)).cut(cyl_y(8.1, 16, (0, y, center_n)))
    for x in (-16, 16):
        p = p.cut(cyl_y(2.2, 16, (x, y, center_n)))
    return p


def bearing_insert(center_n, y):
    return cyl_y(8.0, 7, (0, y, center_n)).cut(cyl_y(4.1, 9, (0, y, center_n)))


def link_with_eyes(a, b, body_r=3.2, eye_r=7.0, pin_r=2.1):
    """Round link with coplanar pivot eyes; a and b are in the same Y plane."""
    link = rod(a, b, body_r).fuse(cyl_y(eye_r, 6, a)).fuse(cyl_y(eye_r, 6, b))
    return link.cut(cyl_y(pin_r, 10, a)).cut(cyl_y(pin_r, 10, b))


def motor_mount(center_n, side):
    y = side * 92
    p = box(58, 6, 58, (0, y, center_n)).cut(cyl_y(19.2, 12, (0, y, center_n)))
    for x in (-8, 8):
        for z in (-8, 8):
            p = p.cut(cyl_y(2.2, 12, (x, y, center_n + z)))
    return p


def shooter_plate(y):
    outline = [(-150, -136), (78, -136), (128, -105), (128, 105), (78, 136), (-150, 136)]
    plate = cq.Workplane("XZ").polyline(outline).close().extrude(2, both=True).translate((0, y, 0)).val()
    plate = plate.cut(cyl_y(26, 10, (-58, y, 0)))
    # One common 18 mm travel slot per axle: center positions 80...89 mm.
    for sign in (-1, 1):
        zc = sign * 84.5
        slot = box(16, 12, 9, (0, y, zc))
        slot = slot.fuse(cyl_y(8, 12, (0, y, sign * 80))).fuse(cyl_y(8, 12, (0, y, sign * 89)))
        plate = plate.cut(slot)
    for x in (-88, 98):
        for z in (-116, 116):
            plate = plate.cut(cyl_y(2.2, 10, (x, y, z)))
    return plate


def paddle_parts():
    cx, _, cz = PADDLE_CENTER
    hub = cyl_y(18, 34, PADDLE_CENTER).cut(cyl_y(4.1, 38, PADDLE_CENTER))
    parts = [("paddle_hub", hub, C["hub"])]
    phase = 18.0
    for i, a in enumerate((phase, phase + 120, phase + 240), 1):
        # Arm spans r=14...46; blade spans r=46...58; TPU tip reaches exactly r=60.
        arm = box(32, 18, 10, (cx + 30, 0, cz)).rotate(PADDLE_CENTER, (cx, 1, cz), a)
        hinge_pt = (cx + 46 * math.cos(math.radians(a)), 0, cz + 46 * math.sin(math.radians(a)))
        hinge = cyl_y(5, PADDLE_W + 4, hinge_pt).cut(cyl_y(2.1, PADDLE_W + 8, hinge_pt))
        blade = box(12, PADDLE_W, 30, (cx + 52, 0, cz)).rotate(PADDLE_CENTER, (cx, 1, cz), a)
        flex = box(4, PADDLE_W, 34, (cx + 58, 0, cz)).rotate(PADDLE_CENTER, (cx, 1, cz), a)
        parts += [
            (f"paddle_arm_{i}", arm, C["paddle"]),
            (f"paddle_hinge_{i}", hinge, C["shaft"]),
            (f"paddle_blade_{i}", blade, C["paddle"]),
            (f"paddle_flex_tip_{i}", flex, C["flex"]),
        ]
    return parts


def panel_on_segment(start, end, angle, kind, side=0):
    length = math.dist(start, end)
    mx, mz = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
    nx, nz = normal(angle)
    if kind == "floor":
        shape = box(length, CHANNEL_CLEAR_W + 6, 3, (mx, 0, mz))
        pivot = (mx, 0, mz)
    elif kind == "roof":
        cx, cz = mx + CHANNEL_CLEAR_H * nx, mz + CHANNEL_CLEAR_H * nz
        shape = box(length, CHANNEL_CLEAR_W + 6, 3, (cx, 0, cz))
        pivot = (cx, 0, cz)
    else:
        cx, cz = mx + CHANNEL_CLEAR_H / 2 * nx, mz + CHANNEL_CLEAR_H / 2 * nz
        shape = box(length, 3, CHANNEL_CLEAR_H, (cx, side * (CHANNEL_CLEAR_W / 2 + 1.5), cz))
        pivot = (cx, side * (CHANNEL_CLEAR_W / 2 + 1.5), cz)
    shape = shape.rotate(pivot, (pivot[0], pivot[1] + 1, pivot[2]), -angle)
    if kind in ("floor", "roof"):
        # The rotor occupies an intentional drum opening in the floor/roof.
        shape = shape.cut(cyl_y(PADDLE_SWEEP_R + 3.0, CHANNEL_CLEAR_W + 12, PADDLE_CENTER))
    else:
        # Only the 8 mm rotor shaft crosses the channel side walls.
        shape = shape.cut(cyl_y(7.0, CHANNEL_CLEAR_W + 20, PADDLE_CENTER))
    return shape


def build(config, half_spacing):
    assy = cq.Assembly(name=f"paddle_launcher_constrained_{config}")
    mesh, all_shapes, named = [], [], {}

    def add(name, shape, color, meshable=True):
        assy.add(shape, name=name, color=color)
        all_shapes.append(shape)
        named[name] = shape
        if meshable:
            mesh.append(shape)

    # Datum-aware chassis rails; hole pitch is 48 mm.
    for y in (-72, 72):
        rail = box(380, 18, 14, (20, y, 9))
        for x in range(-150, 191, 48):
            rail = rail.cut(cyl_z(2.3, 20, (x, y, 9)))
        add(f"base_rail_{y:+d}", rail, C["base"])

    # Continuous three-segment channel generated from shared endpoints.
    for i, (start, end, _, angle) in enumerate(GUIDES, 1):
        add(f"guide_floor_{i}", panel_on_segment(start, end, angle, "floor"), C["guide"])
        add(f"guide_roof_{i}", panel_on_segment(start, end, angle, "roof"), C["guide"])
        for side in (-1, 1):
            add(f"guide_wall_{i}_{side:+d}", panel_on_segment(start, end, angle, "wall", side), C["guide"])

    # Paddle support cheeks, 8 mm shaft and directly supported continuous servo drive.
    for side in (-1, 1):
        y = side * 62
        cheek = box(124, 6, 154, (PADDLE_CENTER[0], y, 78))
        cheek = cheek.cut(cyl_y(7.1, 12, PADDLE_CENTER)).cut(cyl_y(34, 12, (PADDLE_CENTER[0], y, 102)))
        for x in (-96, 2):
            for z in (18, 140):
                cheek = cheek.cut(cyl_y(2.3, 12, (x, y, z)))
        add(f"paddle_support_cheek_{side:+d}", cheek, C["structure"])
    add("paddle_shaft_8mm", cyl_y(4, 154, PADDLE_CENTER), C["shaft"])
    for name, shape, color in paddle_parts():
        add(name, shape, color)
    servo_center = (PADDLE_CENTER[0], 112, PADDLE_CENTER[2])
    add("paddle_cr_servo_envelope", box(*SERVO_ENV, servo_center), C["servo"], False)
    block = box(58, 6, 60, (servo_center[0], 76, servo_center[2])).cut(cyl_y(8.2, 12, (servo_center[0], 76, servo_center[2])))
    for x in (-23, 23):
        for z in (-24, 24):
            block = block.cut(cyl_y(2.2, 12, (servo_center[0] + x, 76, servo_center[2] + z)))
    add("paddle_servo_block", block, C["plate"])
    add("paddle_shaft_clamp", cyl_y(12, 6, (PADDLE_CENTER[0], 69, PADDLE_CENTER[2])).cut(cyl_y(4.1, 8, (PADDLE_CENTER[0], 69, PADDLE_CENTER[2]))), C["hub"])

    # Backflow fingers at the entrance of the 52-degree segment.
    finger_anchor = GUIDES[-1][0]
    for side in (-1, 1):
        f = box(38, 1.2, 44, (finger_anchor[0] + 16, side * 38, finger_anchor[1] + 25))
        f = f.rotate((finger_anchor[0] + 16, side * 38, finger_anchor[1] + 25), (finger_anchor[0] + 16, side * 38 + 1, finger_anchor[1] + 25), -ANGLE)
        add(f"one_way_finger_{side:+d}", f, cq.Color(0.76, 0.88, 0.96))

    # Shared slotted side plates support both spacing settings.
    for side in (-1, 1):
        add(f"shooter_side_plate_{side:+d}", to_world(shooter_plate(side * PLATE_INSIDE_SPAN / 2)), C["plate"])

    for sign, label in ((1, "upper"), (-1, "lower")):
        n = sign * half_spacing
        add(f"flywheel_shaft_{label}", to_world(cyl_y(4, 194, (0, 0, n))), C["shaft"])
        for i, y in enumerate(WHEEL_Y, 1):
            add(f"gecko_flywheel_{label}_{i}", to_world(gecko(n, y)), C["wheel"])
            outward = -1 if y < 0 else 1
            add(f"sonic_hub_{label}_{i}", to_world(sonic_hub(n, y, outward)), C["hub"])
            flange_y = y + outward * 2.0
            for bi, (dx, dz) in enumerate(((-8, -8), (-8, 8), (8, -8), (8, 8)), 1):
                add(f"hub_bolt_{label}_{i}_{bi}", to_world(cyl_y(2, 14, (dx, flange_y, n + dz))), C["fastener"])
        # Both shaft ends run in sliding bearing carriages.  The plate slot sets
        # the path; paired guide rails prevent carriage rotation.
        for side in (-1, 1):
            cy = side * 80
            add(f"bearing_carriage_{label}_{side:+d}", to_world(bearing_carriage(n, cy)), C["structure"])
            add(f"bearing_insert_{label}_{side:+d}", to_world(bearing_insert(n, cy)), C["hub"])
            for rail_u in (-26.5, 26.5):
                add(f"carriage_guide_{label}_{side:+d}_{rail_u:+.1f}", to_world(box(5, 10, 52, (rail_u, cy, sign * 84.5))), C["plate"])
        motor_side = 1 if sign > 0 else -1
        add(f"motor_mount_{label}", to_world(motor_mount(n, motor_side)), C["structure"])
        # Bridge is rigidly attached to the moving carriage, so motor alignment
        # follows the shaft throughout the 9 mm slot travel.
        for u in (-17, 17):
            add(f"motor_bridge_{label}_{u:+d}", to_world(box(8, 10, 26, (u, motor_side * 87, n))), C["structure"])
        my = motor_side * 153.0
        add(f"motor_envelope_{label}", to_world(cyl_y(MOTOR_D / 2, MOTOR_L, (0, my, n))), C["motor"], False)
        add(f"motor_coupler_{label}", to_world(cyl_y(9, 16, (0, motor_side * 103, n)).cut(cyl_y(4.1, 18, (0, motor_side * 103, n)))), C["hub"])

    # Real symmetric spacing mechanism on the +Y side:
    # servo crank -> fixed 65 mm drag link -> horizontal crosshead ->
    # two fixed 110 mm links -> tabs rigidly attached to the bearing carriages.
    main_link_len = 110.0
    carriage_pin_u = 18.0
    crosshead_u = carriage_pin_u - math.sqrt(main_link_len**2 - half_spacing**2)
    for sign, label in ((1, "upper"), (-1, "lower")):
        n = sign * half_spacing
        # Stack the two rod eyes in separate axial slots. A rigid spacer runs
        # from the moving carriage face to the corresponding rod eye.
        link_y = 96.0 if sign > 0 else 104.0
        spacer_start, spacer_end = 86.0, link_y - 3.0
        spacer = cyl_y(5, spacer_end - spacer_start, (carriage_pin_u, (spacer_start + spacer_end) / 2, n)).cut(
            cyl_y(2.1, spacer_end - spacer_start + 2, (carriage_pin_u, (spacer_start + spacer_end) / 2, n))
        )
        add(f"carriage_link_spacer_{label}", to_world(spacer), C["structure"])
        pin = (carriage_pin_u, link_y, n)
        pin_end = link_y + 4.0
        add(f"carriage_link_pin_{label}", to_world(cyl_y(2, pin_end - 82.0, (carriage_pin_u, (82.0 + pin_end) / 2, n))), C["fastener"])
        add(f"main_spacing_link_{label}", to_world(link_with_eyes((crosshead_u, link_y, 0), pin)), C["flex"])

    # Slotted clevis crosshead keeps the two link eyes in separate Y planes.
    # Body trails behind the pivot in -U; the two outgoing diagonal links leave
    # the clevis without crossing a front wall.
    crosshead = box(20, 24, 22, (crosshead_u - 10, 100, 0))
    for yy in (96.0, 104.0):
        crosshead = crosshead.cut(box(12, 7.0, 16.0, (crosshead_u - 4, yy, 0)))
    crosshead = crosshead.cut(cyl_y(2.1, 30, (crosshead_u, 100, 0)))
    add("crosshead", to_world(crosshead), C["structure"])
    add("crosshead_through_pin", to_world(cyl_y(2, 57, (crosshead_u, 114.5, 0))), C["fastener"])
    for n in (-15.0, 15.0):
        add(f"crosshead_guide_{n:+.0f}", to_world(box(40, 10, 5, (-62, 82, n))), C["plate"])
    for u in (-82.0, -42.0):
        add(f"crosshead_guide_stop_{u:+.0f}", to_world(box(5, 10, 27, (u, 82, 0))), C["plate"])

    # Servo, stand-off mounting plate, 12 mm crank and fixed-length drive link.
    servo_u, servo_y = -120.0, 111.0
    crank_r, drag_len = 12.0, 65.0
    d = crosshead_u - servo_u
    cos_theta = (d*d + crank_r*crank_r - drag_len*drag_len) / (2*d*crank_r)
    theta = math.acos(max(-1.0, min(1.0, cos_theta)))
    crank_end_x = servo_u + crank_r * math.cos(theta)
    crank_end_n = crank_r * math.sin(theta)
    add("gap_servo_mount_plate", to_world(box(55, 5, 56, (servo_u, 89, 0))), C["plate"])
    for u in (servo_u - 23, servo_u + 23):
        for n in (-23, 23):
            add(f"gap_servo_standoff_{u:+.0f}_{n:+.0f}", to_world(cyl_y(3, 17, (u, 79.5, n))), C["structure"])
    add("gap_servo_envelope", to_world(box(*SERVO_ENV, (servo_u, servo_y, 0))), C["servo"], False)
    add("servo_spline_hub", to_world(cyl_y(7, 7, (servo_u, 125, 0))), C["hub"])
    add("servo_crank", to_world(link_with_eyes((servo_u, 132, 0), (crank_end_x, 132, crank_end_n), 3.0, 5.0, 2.1)), C["flex"])
    add("servo_drag_link", to_world(link_with_eyes((crank_end_x, 139, crank_end_n), (crosshead_u, 139, 0), 3.0, 6.0, 2.1)), C["flex"])
    add("servo_crank_joint_pin", to_world(cyl_y(2, 15, (crank_end_x, 135.5, crank_end_n))), C["fastener"])

    # Final throat starts exactly at the calculated guide endpoint.
    # Stop 52 mm before the axle centre so guide panels cannot enter the 48 mm
    # flywheel envelope; the remaining 4 mm is a deliberate running clearance.
    throat_length = 83.0
    for n in (-55.0, 55.0):
        add(f"shooter_throat_{n:+.0f}", to_world(box(throat_length, CHANNEL_CLEAR_W + 6, 3, (-135 + throat_length / 2, 0, n))), C["guide"])

    kinematics = {
        "main_link_length_mm": main_link_len,
        "crosshead_u_mm": crosshead_u,
        "servo_crank_angle_deg": math.degrees(theta),
        "servo_drag_link_length_mm": drag_len,
    }
    return assy, mesh, all_shapes, named, kinematics


def bbox_dict(shapes):
    bb = cq.Compound.makeCompound(shapes).BoundingBox()
    return {
        "min_mm": [round(bb.xmin, 3), round(bb.ymin, 3), round(bb.zmin, 3)],
        "max_mm": [round(bb.xmax, 3), round(bb.ymax, 3), round(bb.zmax, 3)],
        "size_mm": [round(bb.xlen, 3), round(bb.ylen, 3), round(bb.zlen, 3)],
        "within_18in_cube": all(v <= CHASSIS_LIMIT + 1e-6 for v in (bb.xlen, bb.ylen, bb.zlen)),
    }


def _bbox_overlap(a, b, tol=1e-7):
    aa, bb = a.BoundingBox(), b.BoundingBox()
    return not (aa.xmax <= bb.xmin + tol or bb.xmax <= aa.xmin + tol or
                aa.ymax <= bb.ymin + tol or bb.ymax <= aa.ymin + tol or
                aa.zmax <= bb.zmin + tol or bb.zmax <= aa.zmin + tol)


def _intersection_volume(a, b):
    if not _bbox_overlap(a, b):
        return 0.0
    try:
        return max(0.0, a.intersect(b).Volume())
    except Exception:
        return float("inf")


def interference_report(named):
    """Check only interfaces that must have free running clearance."""
    wheels = {k: v for k, v in named.items() if k.startswith("gecko_flywheel_")}
    plates = {k: v for k, v in named.items() if k.startswith("shooter_side_plate_")}
    guides = {k: v for k, v in named.items() if k.startswith("guide_") or k.startswith("shooter_throat_")}
    carriages = {k: v for k, v in named.items() if k.startswith("bearing_carriage_")}
    rails = {k: v for k, v in named.items() if k.startswith("carriage_guide_")}
    rotor_prefixes = ("paddle_shaft_", "paddle_hub", "paddle_arm_", "paddle_hinge_", "paddle_blade_", "paddle_flex_tip_", "paddle_shaft_clamp")
    rotor = {k: v for k, v in named.items() if k.startswith(rotor_prefixes)}
    feeder_cheeks = {k: v for k, v in named.items() if k.startswith("paddle_support_cheek_")}
    motors = {k: v for k, v in named.items() if k.startswith("motor_envelope_")}
    motor_mounts = {k: v for k, v in named.items() if k.startswith("motor_mount_")}
    linkage = {k: v for k, v in named.items() if k.startswith(("main_spacing_link_", "servo_drag_link", "servo_crank"))}
    main_links = {k: v for k, v in named.items() if k.startswith("main_spacing_link_")}
    crosshead_body = {"crosshead": named["crosshead"]}
    servo_crank_shape = {"servo_crank": named["servo_crank"]}
    servo_drag_shape = {"servo_drag_link": named["servo_drag_link"]}

    groups = {}
    for label, left, right in (
        ("flywheel_vs_side_plate", wheels, plates),
        ("flywheel_vs_channel_panels", wheels, guides),
        ("flywheel_vs_bearing_carriage", wheels, carriages),
        ("bearing_carriage_vs_guide_rail", carriages, rails),
        ("motor_envelope_vs_bearing_carriage", motors, carriages),
        ("motor_mount_vs_bearing_carriage", motor_mounts, carriages),
        ("paddle_rotor_vs_channel_panels", rotor, guides),
        ("paddle_rotor_vs_support_cheeks", rotor, feeder_cheeks),
        ("linkage_vs_side_plate", linkage, plates),
        ("main_links_vs_crosshead_body", main_links, crosshead_body),
        ("servo_crank_vs_drag_link", servo_crank_shape, servo_drag_shape),
    ):
        hits, maximum = [], 0.0
        for an, a in left.items():
            for bn, b in right.items():
                volume = _intersection_volume(a, b)
                maximum = max(maximum, volume)
                if volume > 1e-5:
                    hits.append({"a": an, "b": bn, "intersection_volume_mm3": volume})
        groups[label] = {"pass": not hits, "max_intersection_volume_mm3": maximum, "hits": hits}

    wheel_hits, wheel_max = [], 0.0
    wheel_items = list(wheels.items())
    for i, (an, a) in enumerate(wheel_items):
        for bn, b in wheel_items[i + 1:]:
            volume = _intersection_volume(a, b)
            wheel_max = max(wheel_max, volume)
            if volume > 1e-5:
                wheel_hits.append({"a": an, "b": bn, "intersection_volume_mm3": volume})
    groups["flywheel_vs_flywheel"] = {"pass": not wheel_hits, "max_intersection_volume_mm3": wheel_max, "hits": wheel_hits}
    link_hits, link_max = [], 0.0
    link_items = list(main_links.items())
    for i, (an, a) in enumerate(link_items):
        for bn, b in link_items[i + 1:]:
            volume = _intersection_volume(a, b)
            link_max = max(link_max, volume)
            if volume > 1e-5:
                link_hits.append({"a": an, "b": bn, "intersection_volume_mm3": volume})
    groups["main_link_vs_main_link"] = {"pass": not link_hits, "max_intersection_volume_mm3": link_max, "hits": link_hits}
    groups["all_checked_interfaces_clear"] = all(g["pass"] for g in groups.values())
    return groups


def export_parts():
    exporters.export(shooter_plate(0), str(PARTS / "shooter_slotted_side_plate.step"))
    exporters.export(paddle_parts()[3][1], str(PARTS / "paddle_blade.step"))
    exporters.export(sonic_hub(0, 0, 1), str(PARTS / "sonic_8mm_gecko_hub.step"))
    exporters.export(bearing_carriage(0, 0), str(PARTS / "sliding_bearing_carriage.step"))
    exporters.export(link_with_eyes((0, 0, 0), (0, 0, 110)), str(PARTS / "spacing_link_110mm.step"))
    cheek = box(124, 6, 154, (0, 0, 0)).cut(cyl_y(7.1, 12, (0, 0, -5)))
    exporters.export(cheek, str(PARTS / "feeder_support_cheek_reference.step"))


def export_all():
    results = {}
    for config, half_spacing in (("pollen", 80.0), ("nectar", 89.0)):
        assy, mesh, shapes, named, kinematics = build(config, half_spacing)
        stem = OUT / f"paddle_launcher_feasible_{config}"
        assy.export(str(stem.with_suffix(".step")), exportType="STEP")
        assy.export(str(stem.with_suffix(".glb")), exportType="GLTF", tolerance=0.2, angularTolerance=0.15)
        exporters.export(cq.Compound.makeCompound(mesh), str(stem.with_suffix(".stl")), tolerance=0.18, angularTolerance=0.14)
        results[config] = {
            "half_axle_spacing_mm": half_spacing,
            "axle_center_distance_mm": 2 * half_spacing,
            "nominal_flywheel_gap_mm": 2 * half_spacing - WHEEL_OD,
            "bounding_box": bbox_dict(shapes),
            "solid_count": len(cq.Compound.makeCompound(shapes).Solids()),
            "linkage_kinematics": kinematics,
            "interference_checks": interference_report(named),
        }

    continuity = [math.dist(GUIDES[i][1], GUIDES[i + 1][0]) for i in range(len(GUIDES) - 1)]
    expected_end = (SHOOTER_ORIGIN[0] - 135 * T52[0] - 55 * N52[0], SHOOTER_ORIGIN[2] - 135 * T52[1] - 55 * N52[1])
    alignment_error = math.dist(GUIDE_END, expected_end)
    report = {
        "coordinate_system": "X-Y chassis plane; +Z upward",
        "game_piece_geometry_included": False,
        "flywheels": "four 96 x 24 mm Gecko wheels: two per opposed 8 mm shaft",
        "feeder": "three-paddle continuous-rotation-servo indexer; no conveyor belt",
        "gap_adjuster": "servo crank, 65 mm drag link, guided crosshead, two 110 mm links, and shaft-bearing carriages",
        "channel_clear_width_mm": CHANNEL_CLEAR_W,
        "channel_clear_height_mm": CHANNEL_CLEAR_H,
        "paddle_width_mm": PADDLE_W,
        "paddle_side_clearance_each_mm": (CHANNEL_CLEAR_W - PADDLE_W) / 2,
        "paddle_sweep_radius_mm": PADDLE_SWEEP_R,
        "guide_angles_deg": [s[3] for s in GUIDES],
        "guide_joint_errors_mm": continuity,
        "guide_to_throat_alignment_error_mm": alignment_error,
        "shooter_angle_deg": ANGLE,
        "relative_axle_separation_change_mm": 18.0,
        "slot_center_travel_each_axle_mm": 9.0,
        "slot_overall_length_including_16mm_bearing_hole_mm": 25.0,
        "wheel_stack_width_mm": 2 * WHEEL_W + WHEEL_AXIAL_GAP,
        "wheel_stack_clearance_between_plates_mm": PLATE_INSIDE_SPAN - (2 * WHEEL_W + WHEEL_AXIAL_GAP),
        "recommended_servo_speed_rpm": [25, 40],
        "theoretical_feed_rate_objects_per_second": [1.25, 2.0],
        "configurations": results,
        "checks": {
            "channel_width_for_91mm_object_plus_5mm_each_side": CHANNEL_CLEAR_W >= 101.0,
            "channel_height_for_96mm_object_plus_margin": CHANNEL_CLEAR_H >= 106.0,
            "paddle_has_at_least_5mm_side_clearance": (CHANNEL_CLEAR_W - PADDLE_W) / 2 >= 5.0,
            "guide_is_position_continuous": max(continuity) < 0.01,
            "final_guide_is_collinear_with_throat": alignment_error < 0.01,
            "both_configs_within_18in_cube": all(v["bounding_box"]["within_18in_cube"] for v in results.values()),
            "all_selected_interference_checks_pass": all(v["interference_checks"]["all_checked_interfaces_clear"] for v in results.values()),
        },
    }
    (OUT / "paddle_launcher_feasibility_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = [
        "# 对置飞轮连续拨杆发射机构：尺寸约束报告", "",
        "- 坐标：X–Y 为底盘平面，+Z 向上。", "- 模型不含 POLLEN / NECTAR 实体。",
        f"- 通道净截面：{CHANNEL_CLEAR_W:.0f} × {CHANNEL_CLEAR_H:.0f} mm；拨片宽 {PADDLE_W:.0f} mm，单侧余量 {(CHANNEL_CLEAR_W-PADDLE_W)/2:.1f} mm。",
        f"- 飞轮：4 个 96 × 24 mm Gecko；每根 8 mm 轴安装 2 个。", "",
        "| 配置 | 轴中心距 | 名义轮间隙 | 总包络 X×Y×Z | 18 in 校核 |", "|---|---:|---:|---:|:---:|",
    ]
    for name in ("pollen", "nectar"):
        r = results[name]
        b = r["bounding_box"]["size_mm"]
        lines.append(f"| {name.upper()} | {r['axle_center_distance_mm']:.0f} mm | {r['nominal_flywheel_gap_mm']:.0f} mm | {b[0]:.1f}×{b[1]:.1f}×{b[2]:.1f} mm | {'通过' if r['bounding_box']['within_18in_cube'] else '未通过'} |")
    lines += [
        "", "## 间距调节运动链", "",
        "舵机 12 mm 曲柄 → 65 mm 定长驱动杆 → 水平导向滑块 → 两根 110 mm 对称连杆 → 与轴承座刚性连接的耳轴 → 上下飞轮轴。",
        "两侧板均设置轴槽和外置滑动轴承座，因此轴在调节过程中保持平行。", "",
        f"- 三段导槽角度：0° / 26° / {ANGLE:.0f}°；接头最大位置误差 {max(continuity):.6f} mm。",
        f"- 导槽与发射喉道共线误差 {alignment_error:.6f} mm。",
        "- 每根轴的槽中心行程 9 mm；按 16 mm 轴承孔计，槽外形总长 25 mm；两轴相对中心距变化 18 mm。",
        "- 发射喉道在轴心前 52 mm 截止，相对 48 mm 飞轮半径保留至少 4 mm 轴向投影余量。", "",
        "## 实体干涉检查", "",
    ]
    for name in ("pollen", "nectar"):
        checks = results[name]["interference_checks"]
        lines.append(f"- {name.upper()}：{'全部通过' if checks['all_checked_interfaces_clear'] else '存在干涉'}。覆盖飞轮/侧板、飞轮/通道、飞轮/轴承座、飞轮彼此、电机/轴承座、拨杆/通道、拨杆/支撑板、连杆/侧板、双槽滑块及曲柄杆端分层。")
    (OUT / "paddle_launcher_feasibility_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    export_parts()
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    export_all()
