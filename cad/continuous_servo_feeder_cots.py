"""COTS-constrained revision of the imported continuous-servo feeder.

This keeps the custom PETG frame, guides, swing arms and compliant roller, but
replaces the placeholder motion hardware with currently catalogued goBILDA
parts.  X-Y is the chassis plane, +Z is up and +X is the feed direction.

Status tags used by the generated report:
    KNOWN_VENDOR_VERIFIED: official goBILDA product page checked 2026-09-28.
    CALCULATED: belt centres calculated from pitch length and pitch diameters.
    ASSUMED: simplified CAD envelope used instead of downloaded vendor STEP.
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
HTD_PITCH = 5.0
BELT_WIDTH = 9.0
BELT_THICKNESS = 2.2
SMALL_TEETH = 16
LARGE_TEETH = 48
SMALL_PD = SMALL_TEETH * HTD_PITCH / math.pi
LARGE_PD = LARGE_TEETH * HTD_PITCH / math.pi
HORIZONTAL_X0 = -112.0
JUNCTION_X = 28.0
LOWER_SHAFT_Z = 26.0
INCLINE_ANGLE_DEG = 38.0
HORIZONTAL_BELT_PITCH_LENGTH = 360.0
INCLINE_BELT_PITCH_LENGTH = 320.0
PINCH_BELT_PITCH_LENGTH = 275.0
HORIZONTAL_CENTER = (HORIZONTAL_BELT_PITCH_LENGTH - math.pi * SMALL_PD) / 2.0
INCLINE_CENTER = (INCLINE_BELT_PITCH_LENGTH - math.pi * SMALL_PD) / 2.0
UPPER_SHAFT = (
    JUNCTION_X + INCLINE_CENTER * math.cos(math.radians(INCLINE_ANGLE_DEG)),
    0.0,
    LOWER_SHAFT_Z + INCLINE_CENTER * math.sin(math.radians(INCLINE_ANGLE_DEG)),
)
PINCH_ROLLER_OD = 72.0
PINCH_NEUTRAL = (46.0, 0.0, 157.0)
SERVO_ENV = (43.5, 20.5, 40.0)


CATALOG = {
    "servo": {
        "sku": "2000-0025-0003",
        "name": "2000 Series Dual Mode Servo (25-3, Speed)",
        "qty": 2,
        "status": "KNOWN_VENDOR_VERIFIED",
        "url": "https://www.gobilda.com/2000-series-dual-mode-servo-25-3-speed/",
    },
    "servo_frame": {
        "sku": "1802-0043-0001",
        "name": "1802 Series Servo Frame (43mm Width)",
        "qty": 2,
        "status": "KNOWN_VENDOR_VERIFIED",
        "url": "https://www.gobilda.com/1802-series-servo-frame-43mm-width-for-standard-size-servos/",
    },
    "servo_shaft_coupler": {
        "sku": "4001-0025-4008",
        "name": "Clamping Servo-to-Shaft Coupler, H25T to 8mm REX",
        "qty": 2,
        "status": "KNOWN_VENDOR_VERIFIED",
        "url": "https://www.gobilda.com/4001-series-clamping-servo-to-shaft-coupler-25-tooth-spline-to-8mm-rex-bore/",
    },
    "small_pulley": {
        "sku": "3417-4008-0016",
        "name": "5mm HTD Set-Screw Pinion Pulley, 8mm REX, 16T",
        "qty": 9,
        "status": "KNOWN_VENDOR_VERIFIED",
        "url": "https://www.gobilda.com/5mm-htd-timing-pulleys/",
    },
    "large_pulley": {
        "sku": "3415-0014-0048",
        "name": "5mm HTD Hub-Mount Pulley, 14mm Bore, 48T",
        "qty": 1,
        "status": "KNOWN_VENDOR_VERIFIED",
        "url": "https://www.gobilda.com/5mm-htd-timing-pulleys/",
    },
    "sonic_hub": {
        "sku": "1309-0016-4008",
        "name": "1309 Series Sonic Hub, 8mm REX Bore",
        "qty": 1,
        "status": "KNOWN_VENDOR_VERIFIED",
        "url": "https://www.gobilda.com/1309-series-sonic-hub-8mm-rex-bore/",
    },
    "belt_360": {
        "sku": "3412-0009-0360",
        "name": "5mm HTD Belt, 9mm Width, 360mm Pitch Length",
        "qty": 2,
        "status": "KNOWN_VENDOR_VERIFIED",
        "url": "https://www.gobilda.com/5mm-pitch-htd-timing-belt-9mm-width-360mm-pitch-length-72-tooth/",
    },
    "belt_320": {
        "sku": "3412-0009-0320",
        "name": "5mm HTD Belt, 9mm Width, 320mm Pitch Length",
        "qty": 2,
        "status": "KNOWN_VENDOR_VERIFIED",
        "url": "https://www.gobilda.com/3412-series-5mm-htd-pitch-timing-belt-9mm-width-320mm-pitch-length-64-tooth/",
    },
    "belt_275": {
        "sku": "3412-0009-0275",
        "name": "5mm HTD Belt, 9mm Width, 275mm Pitch Length",
        "qty": 1,
        "status": "KNOWN_VENDOR_VERIFIED",
        "url": "https://www.gobilda.com/3412-series-5mm-htd-pitch-timing-belt-9mm-width-275mm-pitch-length-55-tooth/",
    },
    "shaft_144": {
        "sku": "2106-4008-1440",
        "name": "8mm REX Shaft with E-Clip, 144mm",
        "qty": 3,
        "status": "KNOWN_VENDOR_VERIFIED",
        "url": "https://www.gobilda.com/8mm-rex-shaft-with-e-clip-stainless-steel-144mm-length/",
    },
    "shaft_192": {
        "sku": "2106-4008-1920",
        "name": "8mm REX Shaft with E-Clip, 192mm",
        "qty": 1,
        "status": "KNOWN_VENDOR_VERIFIED",
        "url": "https://www.gobilda.com/stainless-steel-rex-shafting/",
    },
    "bearing": {
        "sku": "1611-0514-4008",
        "name": "Flanged Bearing, 8mm REX ID x 14mm OD x 5mm",
        "qty": 8,
        "status": "KNOWN_VENDOR_VERIFIED",
        "url": "https://www.gobilda.com/1611-series-flanged-ball-bearing-8mm-rex-id-x-14mm-od-5mm-thickness-2-pack/",
    },
}


C = {
    "frame": cq.Color(0.18, 0.23, 0.30),
    "cots": cq.Color(0.78, 0.80, 0.84),
    "shaft": cq.Color(0.58, 0.62, 0.68),
    "pulley": cq.Color(0.86, 0.52, 0.16),
    "belt": cq.Color(0.06, 0.07, 0.08),
    "guide": cq.Color(0.20, 0.57, 0.84, 0.52),
    "servo": cq.Color(0.60, 0.31, 0.76, 0.75),
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


def solve_open_belt_center(length, d_small, d_large):
    def estimate(c):
        return 2 * c + math.pi * (d_small + d_large) / 2 + (d_large - d_small) ** 2 / (4 * c)
    lo, hi = abs(d_large - d_small) / 2 + 0.1, length / 2
    for _ in range(80):
        mid = (lo + hi) / 2
        if estimate(mid) < length:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


PINCH_CENTER = solve_open_belt_center(PINCH_BELT_PITCH_LENGTH, SMALL_PD, LARGE_PD)


def pulley_16(center, width=BELT_WIDTH) -> cq.Shape:
    x, y, z = center
    body = cyl_y(SMALL_PD / 2, width, center).cut(cyl_y(SHAFT_D / 2 + 0.10, width + 2, center))
    for dy in (-(width / 2 + 0.7), width / 2 + 0.7):
        body = body.fuse(cyl_y(SMALL_PD / 2 + 1.5, 1.4, (x, y + dy, z)).cut(cyl_y(4.1, 3, (x, y + dy, z))))
    return body


def pulley_48_with_hub(center) -> cq.Shape:
    x, y, z = center
    wheel = cyl_y(LARGE_PD / 2, BELT_WIDTH, center).cut(cyl_y(7.1, BELT_WIDTH + 2, center))
    hub = cyl_y(16, 8, (x, y + 9, z)).cut(cyl_y(4.1, 10, (x, y + 9, z)))
    flange = cyl_y(22, 3, (x, y + 4.5, z)).cut(cyl_y(7.1, 5, (x, y + 4.5, z)))
    return wheel.fuse(hub).fuse(flange)


def flanged_bearing(center) -> cq.Shape:
    x, y, z = center
    ring = cyl_y(7, 5, center).cut(cyl_y(4.05, 7, center))
    return ring.fuse(cyl_y(8, 1, (x, y, z)).cut(cyl_y(4.05, 3, (x, y, z))))


def servo_drive(center, axis_y, label):
    x, y, z = center
    side = 1 if axis_y < y else -1
    frame_y = (y + axis_y) / 2
    frame = box(58, 6, 58, (x, frame_y, z)).cut(cyl_y(8.2, 12, (x, frame_y, z)))
    for dx in (-23, 23):
        for dz in (-23, 23):
            frame = frame.cut(cyl_y(2.2, 12, (x + dx, frame_y, z + dz)))
    coupler_y = axis_y + side * 8
    coupler = cyl_y(10, 16, (x, coupler_y, z)).cut(cyl_y(4.1, 18, (x, coupler_y, z)))
    return [
        (f"{label}_2000-0025-0003_servo", box(*SERVO_ENV, center), C["servo"], False),
        (f"{label}_1802-0043-0001_servo_frame", frame, C["cots"], True),
        (f"{label}_4001-0025-4008_coupler", coupler, C["shaft"], True),
    ]


def belt_strands_equal(a, b, lane, pitch_d):
    ax, _, az = a
    bx, _, bz = b
    dx, dz = bx - ax, bz - az
    length = math.hypot(dx, dz)
    angle = math.degrees(math.atan2(dz, dx))
    nx, nz = -dz / length, dx / length
    parts = []
    for sign, suffix in ((1, "upper"), (-1, "lower")):
        center = ((ax + bx) / 2 + sign * pitch_d / 2 * nx, lane, (az + bz) / 2 + sign * pitch_d / 2 * nz)
        parts.append((suffix, inclined(box(length, BELT_WIDTH, BELT_THICKNESS, center), center, angle)))
    return parts


def compliant_pinch_roller(center) -> cq.Shape:
    x, y, z = center
    outer = cyl_y(PINCH_ROLLER_OD / 2, 44, center).cut(cyl_y(30, 46, center))
    hub = cyl_y(13, 48, center).cut(cyl_y(4.1, 50, center))
    roller = outer.fuse(hub)
    for angle in range(0, 360, 30):
        roller = roller.fuse(box(24, 40, 5, (x + 23, y, z)).rotate((x, y, z), (x, y + 1, z), angle))
    return roller


def build():
    assy = cq.Assembly(name="continuous_servo_feeder_cots")
    mesh = []

    def add(name, shape, color, meshable=True):
        assy.add(shape, name=name, color=color)
        if meshable:
            mesh.append(shape)

    add("00_xy_chassis_reference", box(340, 240, 4, (10, 0, -2)), C["reference"], False)

    outline = [(-128, 4), (54, 4), (142, 75), (148, 145), (72, 188), (-42, 178), (-128, 126)]
    shafts = [
        ("horizontal_return", (HORIZONTAL_X0, 0, LOWER_SHAFT_Z)),
        ("junction_drive", (JUNCTION_X, 0, LOWER_SHAFT_Z)),
        ("incline_return", UPPER_SHAFT),
    ]
    for side in (-1, 1):
        y = side * SIDE_PLATE_Y
        plate = cq.Workplane("XZ").polyline(outline).close().extrude(SIDE_PLATE_T / 2, both=True).translate((0, y, 0)).val()
        for _, (sx, _, sz) in shafts:
            plate = plate.cut(cyl_y(7.1, 10, (sx, y, sz)))
            for dx in (-16, 16):
                plate = plate.cut(cyl_y(2.2, 10, (sx + dx, y, sz)))
        add(f"custom_PETG_side_frame_{side:+d}", plate, C["frame"])

    for name, center in shafts:
        length = 144
        add(f"{name}_2106-4008-1440_rex_shaft", cyl_y(4, length, center), C["shaft"])
        for side in (-1, 1):
            by = side * SIDE_PLATE_Y
            add(f"{name}_1611-0514-4008_bearing_{side:+d}", flanged_bearing((center[0], by, center[2])), C["cots"])

    for lane in (-36.0, 36.0):
        a = (HORIZONTAL_X0, lane, LOWER_SHAFT_Z)
        b = (JUNCTION_X, lane, LOWER_SHAFT_Z)
        add(f"horizontal_return_3417-4008-0016_{int(lane)}", pulley_16(a), C["pulley"])
        add(f"horizontal_drive_3417-4008-0016_{int(lane)}", pulley_16(b), C["pulley"])
        for suffix, strand in belt_strands_equal(a, b, lane, SMALL_PD):
            add(f"horizontal_3412-0009-0360_{suffix}_{int(lane)}", strand, C["belt"])

    for lane in (-12.0, 12.0):
        a = (JUNCTION_X, lane, LOWER_SHAFT_Z)
        b = (UPPER_SHAFT[0], lane, UPPER_SHAFT[2])
        add(f"incline_drive_3417-4008-0016_{int(lane)}", pulley_16(a), C["pulley"])
        add(f"incline_return_3417-4008-0016_{int(lane)}", pulley_16(b), C["pulley"])
        for suffix, strand in belt_strands_equal(a, b, lane, SMALL_PD):
            add(f"incline_3412-0009-0320_{suffix}_{int(lane)}", strand, C["belt"])

    for name, shape, color, meshable in servo_drive((JUNCTION_X, 102, LOWER_SHAFT_Z), 72, "conveyor_drive"):
        add(name, shape, color, meshable)

    guide_center = ((JUNCTION_X + UPPER_SHAFT[0]) / 2, 0, (LOWER_SHAFT_Z + UPPER_SHAFT[2]) / 2 + 39)
    for side in (-1, 1):
        wall = inclined(box(INCLINE_CENTER + 32, 3, 112, (guide_center[0], side * 55.5, guide_center[2])), (guide_center[0], side * 55.5, guide_center[2]), INCLINE_ANGLE_DEG)
        add(f"custom_PETG_incline_guide_wall_{side:+d}", wall, C["guide"])

    pivot = (-20.0, 0.0, 166.0)
    for side in (-1, 1):
        y = side * 62.0
        arm = rod_between((pivot[0], y, pivot[2]), (PINCH_NEUTRAL[0], y, PINCH_NEUTRAL[2]), 7.0)
        arm = arm.fuse(cyl_y(13, 8, (pivot[0], y, pivot[2])).cut(cyl_y(4.1, 10, (pivot[0], y, pivot[2]))))
        arm = arm.fuse(cyl_y(13, 8, (PINCH_NEUTRAL[0], y, PINCH_NEUTRAL[2])).cut(cyl_y(7.1, 10, (PINCH_NEUTRAL[0], y, PINCH_NEUTRAL[2]))))
        add(f"custom_PETG_pinch_swing_arm_{side:+d}", arm, C["frame"])
        add(f"pinch_1611-0514-4008_bearing_{side:+d}", flanged_bearing((PINCH_NEUTRAL[0], y, PINCH_NEUTRAL[2])), C["cots"])
        add(f"custom_preload_link_{side:+d}", rod_between((-2, y, 112), (24, y, 151), 4), C["spring"])

    add("pinch_2106-4008-1920_rex_shaft", cyl_y(4, 192, PINCH_NEUTRAL), C["shaft"])
    add("custom_72mm_compliant_pinch_roller", compliant_pinch_roller(PINCH_NEUTRAL), C["belt"])

    # The 75 mm belt plane leaves 1.5 mm between the 9 mm pulley and the
    # nearest swing-arm face (arm centre y=62 mm, half-thickness 7 mm).
    pinch_belt_y = 75.0
    pinch_small = (PINCH_NEUTRAL[0] - PINCH_CENTER, pinch_belt_y, PINCH_NEUTRAL[2])
    pinch_large = (PINCH_NEUTRAL[0], pinch_belt_y, PINCH_NEUTRAL[2])
    add("pinch_drive_3417-4008-0016_16T", pulley_16(pinch_small), C["pulley"])
    add("pinch_3415-0014-0048_48T_with_1309_hub", pulley_48_with_hub(pinch_large), C["pulley"])
    for sign, suffix in ((1, "upper"), (-1, "lower")):
        z = PINCH_NEUTRAL[2] + sign * (SMALL_PD + LARGE_PD) / 4
        add(f"pinch_3412-0009-0275_{suffix}", box(PINCH_CENTER, BELT_WIDTH, BELT_THICKNESS, ((pinch_small[0] + pinch_large[0]) / 2, pinch_belt_y, z)), C["belt"])
    for name, shape, color, meshable in servo_drive((pinch_small[0], 103, pinch_small[2]), 81, "pinch_drive"):
        add(name, shape, color, meshable)

    for side in (-1, 1):
        wall = inclined(box(72, 3, 116, (148, side * 55.5, 132)), (148, side * 55.5, 132), 52.0)
        add(f"custom_PETG_launcher_inlet_wall_{side:+d}", wall, C["guide"])

    return assy, mesh


def export_all():
    assy, mesh = build()
    step = OUT / "continuous_servo_feeder_cots.step"
    stl = OUT / "continuous_servo_feeder_cots.stl"
    glb = OUT / "continuous_servo_feeder_cots.glb"
    assy.export(str(step), exportType="STEP")
    assy.export(str(glb), exportType="GLTF", tolerance=0.18, angularTolerance=0.14)
    exporters.export(cq.Compound.makeCompound(mesh), str(stl), tolerance=0.16, angularTolerance=0.12)
    summary = {
        "version": "CONTINUOUS-FEEDER-COTS-0.1",
        "supersedes": "continuous_servo_feeder.glb",
        "coordinate_system": "X-Y chassis plane; +Z upward; +X feed direction",
        "fact_status": "VALIDATED_GEOMETRY; COTS availability vendor-verified 2026-09-28; physical fit TBD",
        "calculated": {
            "horizontal_center_mm": round(HORIZONTAL_CENTER, 3),
            "incline_center_mm": round(INCLINE_CENTER, 3),
            "pinch_center_mm": round(PINCH_CENTER, 3),
            "pinch_ratio": LARGE_TEETH / SMALL_TEETH,
            "belt_width_mm": BELT_WIDTH,
        },
        "custom_parts": ["PETG side frames", "PETG guide walls", "PETG swing arms", "72mm compliant roller", "preload links/springs"],
        "catalog_bom": list(CATALOG.values()),
        "outputs": {"step": str(step), "stl": str(stl), "glb": str(glb)},
    }
    (OUT / "continuous_servo_feeder_cots_report.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    export_all()
