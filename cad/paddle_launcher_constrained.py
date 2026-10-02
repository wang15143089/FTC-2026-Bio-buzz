"""Dimension-constrained paddle feeder and opposed Gecko flywheel launcher.

The chassis plane is X-Y and +Z is upward.  Selected goBILDA components use
their downloaded official STEP geometry; custom prototype parts remain
parametric CadQuery solids.  Units are millimetres.
No POLLEN or NECTAR bodies are included in the exported assemblies.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import cadquery as cq
from cadquery import exporters

from t06_vendor_cad import (
    CAD_FILES,
    centered_y_axis_part,
    facts as vendor_facts,
    motor_with_output_tip,
    servo_with_output_face,
    sonic_hub as official_sonic_hub,
)


OUT = Path(__file__).resolve().parent / "output"
PARTS = OUT / "parts"
CONFIG = Path(__file__).resolve().parents[1] / "config" / "t06_launcher_cots.json"
OUT.mkdir(parents=True, exist_ok=True)
PARTS.mkdir(parents=True, exist_ok=True)
COTS = json.loads(CONFIG.read_text(encoding="utf-8"))

# Master dimensions
ANGLE = 52.0
WHEEL_OD = COTS["flywheel"]["diameter_mm"]
WHEEL_W = COTS["flywheel"]["width_mm"]
WHEEL_AXIAL_GAP = 6.0
WHEEL_Y = (-(WHEEL_W + WHEEL_AXIAL_GAP) / 2, (WHEEL_W + WHEEL_AXIAL_GAP) / 2)
CHANNEL_CLEAR_W = 108.0
CHANNEL_CLEAR_H = 110.0
PADDLE_CENTER = (-47.0, 0.0, 73.0)
PADDLE_SWEEP_R = 60.0
PADDLE_W = 96.0
PADDLE_SHAFT_L = COTS["feeder_shaft"]["length_mm"]
FLYWHEEL_SHAFT_L = COTS["flywheel_shaft"]["length_mm"]
BEARING_OD = COTS["shaft_bearing"]["outer_diameter_mm"]
BEARING_W = COTS["shaft_bearing"]["thickness_mm"]
COUPLER_L = COTS["shaft_coupler"]["length_envelope_mm"]
MOTOR_CLAMP_W = COTS["motor_clamp"]["width_mm"]
MOTOR_CLAMP_L = COTS["motor_clamp"]["axial_envelope_mm"]
MOTOR_FACE_Y = -112.0
MOTOR_OUTPUT_INNER_Y = MOTOR_FACE_Y + 24.0
FLYWHEEL_SHAFT_MOTOR_END_Y = -FLYWHEEL_SHAFT_L / 2
COUPLER_CENTER_Y = -87.0
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
    """Official 3613-0014-0096 geometry, centered on the launcher shaft."""
    return centered_y_axis_part(COTS["flywheel"]["sku"], (0, y, center_n))


def sonic_hub(center_n, y, outward):
    """Official 1309-0016-4008 assembly, rotated onto the Y shaft."""
    return official_sonic_hub((0, y + outward * 7.0, center_n))


def bearing_carriage(center_n, y):
    """External sliding carriage for goBILDA 1611-0514-4008 bearing."""
    p = box(46, 12, 38, (0, y, center_n)).cut(cyl_y(BEARING_OD / 2 + 0.1, 16, (0, y, center_n)))
    for x in (-16, 16):
        p = p.cut(cyl_y(2.2, 16, (x, y, center_n)))
    return p


def bearing_insert(center_n, y):
    return centered_y_axis_part(COTS["shaft_bearing"]["sku"], (0, y, center_n))


def link_with_eyes(a, b, body_r=3.2, eye_r=7.0, pin_r=2.1):
    """Round link with coplanar pivot eyes; a and b are in the same Y plane."""
    link = rod(a, b, body_r).fuse(cyl_y(eye_r, 6, a)).fuse(cyl_y(eye_r, 6, b))
    return link.cut(cyl_y(pin_r, 10, a)).cut(cyl_y(pin_r, 10, b))


def motor_clamp(center_n, y):
    """Official 1401-0043-0036 clamp assembly."""
    return centered_y_axis_part(COTS["motor_clamp"]["sku"], (0, y, center_n))


def shooter_plate(y):
    outline = [(-150, -136), (78, -136), (128, -105), (128, 105), (78, 136), (-150, 136)]
    plate = cq.Workplane("XZ").polyline(outline).close().extrude(2, both=True).translate((0, y, 0)).val()
    plate = plate.cut(cyl_y(26, 10, (-58, y, 0)))
    # One common 9 mm center-travel slot per axle. The bearing remains in the
    # external carriage, so only the 8 mm REX shaft passes through the plate.
    for sign in (-1, 1):
        zc = sign * 84.5
        slot = box(8.4, 12, 9, (0, y, zc))
        slot = slot.fuse(cyl_y(4.2, 12, (0, y, sign * 80))).fuse(cyl_y(4.2, 12, (0, y, sign * 89)))
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
        # Interference checking, the STL mesh and the geometry-inspection harness
        # all read the real derived solid now.  A low-detail stand-in here could
        # hide a collision, so every vendor part is checked as purchased.
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
        cheek = cheek.cut(cyl_y(7.1, 12, (PADDLE_CENTER[0], y, PADDLE_CENTER[2]))).cut(
            cyl_y(34, 12, (PADDLE_CENTER[0], y, 102))
        )
        for x in (-96, 2):
            for z in (18, 140):
                cheek = cheek.cut(cyl_y(2.3, 12, (x, y, z)))
        add(f"paddle_support_cheek_{side:+d}", cheek, C["structure"])
    add(
        f"paddle_shaft_{COTS['feeder_shaft']['sku']}",
        centered_y_axis_part(COTS["feeder_shaft"]["sku"], PADDLE_CENTER),
        C["shaft"],
    )
    for name, shape, color in paddle_parts():
        add(name, shape, color)
    servo_center = (PADDLE_CENTER[0], 112, PADDLE_CENTER[2])
    feeder_servo = servo_with_output_face(
        COTS["feeder_servo"]["sku"],
        (PADDLE_CENTER[0], PADDLE_CENTER[2]),
        101.5,
        -1,
    )
    add(
        f"paddle_cr_servo_{COTS['feeder_servo']['sku']}",
        feeder_servo,
        C["servo"],
    )
    block = box(58, 6, 60, (servo_center[0], 76, servo_center[2])).cut(cyl_y(8.2, 12, (servo_center[0], 76, servo_center[2])))
    for x in (-23, 23):
        for z in (-24, 24):
            block = block.cut(cyl_y(2.2, 12, (servo_center[0] + x, 76, servo_center[2] + z)))
    add("paddle_shaft_support_bridge", block, C["plate"])
    add(
        f"paddle_servo_frame_{COTS['servo_frame']['sku']}",
        centered_y_axis_part(COTS["servo_frame"]["sku"], (servo_center[0], 99, servo_center[2]), largest_solid_only=True),
        C["structure"],
    )
    add(
        f"paddle_servo_coupler_{COTS['feeder_servo_coupler']['sku']}",
        centered_y_axis_part(COTS["feeder_servo_coupler"]["sku"], (PADDLE_CENTER[0], 94, PADDLE_CENTER[2])),
        C["hub"],
    )

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
        add(
            f"flywheel_shaft_{label}_{COTS['flywheel_shaft']['sku']}",
            to_world(centered_y_axis_part(COTS["flywheel_shaft"]["sku"], (0, 0, n))),
            C["shaft"],
        )
        for i, y in enumerate(WHEEL_Y, 1):
            add(
                f"gecko_flywheel_{label}_{i}_{COTS['flywheel']['sku']}",
                to_world(gecko(n, y)),
                C["wheel"],
            )
            outward = -1 if y < 0 else 1
            hub_y = y + outward * 7.0
            add(
                f"sonic_hub_{label}_{i}_{COTS['flywheel_hub']['sku']}",
                to_world(sonic_hub(n, y, outward)),
                C["hub"],
            )
        # Both shaft ends run in sliding bearing carriages.  The plate slot sets
        # the path; paired guide rails prevent carriage rotation.
        for side in (-1, 1):
            cy = side * 70
            add(f"bearing_carriage_{label}_{side:+d}", to_world(bearing_carriage(n, cy)), C["structure"])
            add(
                f"bearing_insert_{label}_{side:+d}_{COTS['shaft_bearing']['sku']}",
                to_world(bearing_insert(n, cy)),
                C["hub"],
            )
            for rail_u in (-26.5, 26.5):
                add(f"carriage_guide_{label}_{side:+d}_{rail_u:+.1f}", to_world(box(5, 10, 52, (rail_u, cy, sign * 84.5))), C["plate"])
        # Put both motors on -Y, opposite the +Y adjustment linkage. The catalog
        # clamp is bridged to the moving carriage, so alignment follows the shaft.
        motor_side = -1
        clamp_y = MOTOR_FACE_Y - MOTOR_CLAMP_L / 2
        add(
            f"motor_clamp_{label}_{COTS['motor_clamp']['sku']}",
            to_world(motor_clamp(n, clamp_y)),
            C["structure"],
        )
        for u in (-17, 17):
            add(f"motor_bridge_{label}_{u:+d}", to_world(box(8, 42, 26, (u, -91, n))), C["structure"])
        add(
            f"motor_{label}_{COTS['flywheel_motor']['sku']}",
            to_world(motor_with_output_tip((0, n), MOTOR_OUTPUT_INNER_Y)),
            C["motor"],
        )
        # The coupler stops 0.5 mm short of the carriage outer face while
        # retaining 7.5 mm flywheel-shaft and 9.5 mm motor-shaft engagement.
        add(
            f"motor_coupler_{label}_{COTS['shaft_coupler']['sku']}",
            to_world(centered_y_axis_part(COTS["shaft_coupler"]["sku"], (0, COUPLER_CENTER_Y, n))),
            C["hub"],
        )

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
    servo_u = -120.0
    crank_r, drag_len = 12.0, 65.0
    d = crosshead_u - servo_u
    cos_theta = (d*d + crank_r*crank_r - drag_len*drag_len) / (2*d*crank_r)
    theta = math.acos(max(-1.0, min(1.0, cos_theta)))
    crank_end_x = servo_u + crank_r * math.cos(theta)
    crank_end_n = crank_r * math.sin(theta)
    add(
        f"gap_servo_frame_{COTS['servo_frame']['sku']}",
        to_world(centered_y_axis_part(COTS["servo_frame"]["sku"], (servo_u, 89, 0), largest_solid_only=True)),
        C["plate"],
    )
    for u in (servo_u - 23, servo_u + 23):
        for n in (-23, 23):
            add(f"gap_servo_standoff_{u:+.0f}_{n:+.0f}", to_world(cyl_y(3, 17, (u, 79.5, n))), C["structure"])
    add(
        f"gap_servo_{COTS['gap_servo']['sku']}",
        to_world(servo_with_output_face(COTS["gap_servo"]["sku"], (servo_u, 0), 122.0, 1)),
        C["servo"],
    )
    add(
        f"servo_spline_hub_{COTS['gap_servo_hub']['sku']}",
        to_world(centered_y_axis_part(COTS["gap_servo_hub"]["sku"], (servo_u, 125, 0))),
        C["hub"],
    )
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
    motors = {k: v for k, v in named.items() if k.startswith("motor_") and COTS["flywheel_motor"]["sku"] in k}
    motor_mounts = {k: v for k, v in named.items() if k.startswith("motor_clamp_")}
    motor_couplers = {k: v for k, v in named.items() if k.startswith("motor_coupler_")}
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
        ("motor_coupler_vs_bearing_carriage", motor_couplers, carriages),
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
    exporters.export(motor_clamp(0, 0), str(PARTS / "gobilda_1401_0043_0036_mount_official.step"))
    exporters.export(link_with_eyes((0, 0, 0), (0, 0, 110)), str(PARTS / "spacing_link_110mm.step"))
    cheek = box(124, 6, 154, (0, 0, 0)).cut(cyl_y(7.1, 12, (0, 0, -5)))
    exporters.export(cheek, str(PARTS / "feeder_support_cheek_reference.step"))


def vendor_component_bodies():
    """Measure the purchased part that actually enters the launcher, per SKU.

    A purchased part is one working *part*, not necessarily one B-rep solid: the
    whole official file is used, so a finished product whose sub-bodies the
    supplier separated by real air arrives with that same body count (see
    ``docs/decision_log.md`` DEC-0021).  The count is taken on the placed shape
    and not read back from the derivation record, so any reduced proxy
    substituted into this file would show up here as a mismatch.
    """
    samples = {
        COTS["flywheel"]["sku"]: centered_y_axis_part(COTS["flywheel"]["sku"], (0, 0, 0)),
        COTS["flywheel_hub"]["sku"]: official_sonic_hub((0, 0, 0)),
        COTS["flywheel_shaft"]["sku"]: centered_y_axis_part(COTS["flywheel_shaft"]["sku"], (0, 0, 0)),
        COTS["shaft_bearing"]["sku"]: centered_y_axis_part(COTS["shaft_bearing"]["sku"], (0, 0, 0)),
        COTS["flywheel_motor"]["sku"]: motor_with_output_tip((0, 0), 0),
        COTS["motor_clamp"]["sku"]: centered_y_axis_part(COTS["motor_clamp"]["sku"], (0, 0, 0)),
        COTS["shaft_coupler"]["sku"]: centered_y_axis_part(COTS["shaft_coupler"]["sku"], (0, 0, 0)),
        COTS["gap_servo"]["sku"]: servo_with_output_face(COTS["gap_servo"]["sku"], (0, 0), 0, 1),
        COTS["feeder_servo"]["sku"]: servo_with_output_face(COTS["feeder_servo"]["sku"], (0, 0), 0, 1),
        COTS["feeder_shaft"]["sku"]: centered_y_axis_part(COTS["feeder_shaft"]["sku"], (0, 0, 0)),
        COTS["servo_frame"]["sku"]: centered_y_axis_part(COTS["servo_frame"]["sku"], (0, 0, 0), largest_solid_only=True),
        COTS["gap_servo_hub"]["sku"]: centered_y_axis_part(COTS["gap_servo_hub"]["sku"], (0, 0, 0)),
        COTS["feeder_servo_coupler"]["sku"]: centered_y_axis_part(COTS["feeder_servo_coupler"]["sku"], (0, 0, 0)),
    }
    measured = {}
    for sku, shape in samples.items():
        record = vendor_facts(sku)
        measured[sku] = {
            "bodies": len(shape.Solids()),
            "derived_solid_count": record["derived_solid_count"],
            "single_solid": record["single_solid"],
            "keep": record["policy"].get("keep"),
            "source_step_solids": record["source_step_solids"],
            "dropped_solids": record["dropped_solids"],
            "boolean_union_attempted": record.get("boolean_union", {}).get("attempted"),
            "derivation_version": record["derivation_version"],
            "source_step_sha256": record["source_step_sha256"],
        }
    return measured


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
    coupler_inner_y = COUPLER_CENTER_Y + COUPLER_L / 2
    coupler_outer_y = COUPLER_CENTER_Y - COUPLER_L / 2
    carriage_outer_y = -70.0 - 12.0 / 2
    flywheel_shaft_engagement = coupler_inner_y - FLYWHEEL_SHAFT_MOTOR_END_Y
    motor_shaft_engagement = MOTOR_OUTPUT_INNER_Y - coupler_outer_y
    shaft_tip_gap = FLYWHEEL_SHAFT_MOTOR_END_Y - MOTOR_OUTPUT_INNER_Y
    coupler_carriage_clearance = carriage_outer_y - coupler_inner_y
    vendor_bodies = vendor_component_bodies()
    report = {
        "coordinate_system": "X-Y chassis plane; +Z upward",
        "game_piece_geometry_included": False,
        "flywheels": "four 96 x 24 mm Gecko wheels: two per opposed 8 mm shaft",
        "feeder": "three-paddle continuous-rotation-servo indexer; no conveyor belt",
        "gap_adjuster": "servo crank, 65 mm drag link, guided crosshead, two 110 mm links, and shaft-bearing carriages",
        "design_id": COTS["design_id"],
        "catalog_checked_date": COTS["catalog_checked_date"],
        "official_vendor_cad_manifest": COTS["official_cad_manifest"],
        "official_vendor_cad_imported_skus": sorted(CAD_FILES),
        "vendor_component_representation": COTS["assembly_representation"],
        "vendor_component_bodies": vendor_bodies,
        "vendor_whole_part_multi_body_skus": sorted(
            sku for sku, item in vendor_bodies.items() if item["bodies"] != 1
        ),
        "catalog_components": COTS,
        "drive_axial_stack_mm": {
            "flywheel_shaft_motor_end_y": FLYWHEEL_SHAFT_MOTOR_END_Y,
            "motor_output_inner_end_y": MOTOR_OUTPUT_INNER_Y,
            "shaft_tip_gap": shaft_tip_gap,
            "coupler_center_y": COUPLER_CENTER_Y,
            "flywheel_shaft_engagement": flywheel_shaft_engagement,
            "motor_shaft_engagement": motor_shaft_engagement,
            "coupler_to_carriage_clearance": coupler_carriage_clearance,
        },
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
        "shaft_clearance_slot_width_mm": 8.4,
        "shaft_clearance_slot_overall_length_mm": 17.4,
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
            "all_catalog_items_have_sku": all(
                item.get("sku") for key, item in COTS.items()
                if isinstance(item, dict) and key != "external_gears"
            ),
            "all_official_vendor_cad_files_present": all(path.is_file() for path in CAD_FILES.values()),
            "every_vendor_component_is_the_whole_derived_part": all(
                item["bodies"] == item["derived_solid_count"] for item in vendor_bodies.values()
            ),
            "multi_body_vendor_parts_keep_the_whole_official_file": all(
                # Every supplier body the keep rule retains must reach the launcher:
                # the placed count is the official file minus the loose fasteners the
                # part does not include, never a reduced proxy (DEC-0021).
                item["bodies"] == item["source_step_solids"] - item["dropped_solids"]
                for item in vendor_bodies.values()
            ),
            "no_boolean_union_is_run_on_a_vendor_part": all(
                # DEC-0021: a purchased part is kept whole.  Measured 2026-10-01, one
                # multi-argument fuse of 1309-0016-4008 needed over 3 min and still
                # lost 29.44 mm3 of its 4203.984 mm3, and 1401-0043-0036 invented
                # 3.7 mm3, so the Boolean chain is retired for vendor parts.
                item["boolean_union_attempted"] is False
                for item in vendor_bodies.values()
            ),
            "external_gear_count_is_zero": COTS["external_gears"]["quantity"] == 0,
            "coupler_engagement_at_least_7mm_each_end": min(flywheel_shaft_engagement, motor_shaft_engagement) >= 7.0,
            "coupler_clears_bearing_carriage": coupler_carriage_clearance >= 0.5,
            "shaft_tips_do_not_overlap": shaft_tip_gap >= 0.5,
        },
    }
    (OUT / "paddle_launcher_feasibility_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = [
        "# 对置飞轮连续拨杆发射机构：尺寸约束报告", "",
        "- 坐标：X–Y 为底盘平面，+Z 向上。", "- 模型不含 POLLEN / NECTAR 实体。",
        f"- 通道净截面：{CHANNEL_CLEAR_W:.0f} × {CHANNEL_CLEAR_H:.0f} mm；拨片宽 {PADDLE_W:.0f} mm，单侧余量 {(CHANNEL_CLEAR_W-PADDLE_W)/2:.1f} mm。",
        f"- 飞轮：4 个 96 × 24 mm Gecko；每根 8 mm 轴安装 2 个。",
        f"- COTS 版本：{COTS['design_id']}；目录核对日期 {COTS['catalog_checked_date']}。",
        f"- 官方 CAD：已导入 {len(CAD_FILES)} 个 goBILDA SKU；清单 `{COTS['official_cad_manifest']}`。",
        f"- 装配表示：{COTS['assembly_representation']}；供应商按真实间隙分开的子实体保持分开，不强行融合、不丢料。",
        f"- 飞轮直驱：2 × {COTS['flywheel_motor']['sku']}，无外置啮合齿轮。",
        f"- 电机夹具/联轴器：{COTS['motor_clamp']['sku']} / {COTS['shaft_coupler']['sku']}。",
        f"- 轴/轴承：{COTS['flywheel_shaft']['sku']}（{FLYWHEEL_SHAFT_L:.0f} mm）/ {COTS['shaft_bearing']['sku']}（Ø{BEARING_OD:.0f} × {BEARING_W:.0f} mm）。", "",
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
        "- 每根轴的槽中心行程 9 mm；轴承留在外置滑座内，侧板仅开 8.4 mm 轴槽，槽外形总长 17.4 mm；两轴相对中心距变化 18 mm。",
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
