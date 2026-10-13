# -*- coding: utf-8 -*-
"""T06 R52 -- the R37 + R49 feeding hardware grafted onto the R51 independent
axle shooter base.

User instruction (2026-10-13):  "把 R37+R49 那套送球件搬到这个独立轴底座上"

base   = paddle_launcher_shooter_drive_r51.py (read-only import): the 2026-10-01
         full launcher + the accepted 59 x 56 mm sliding side-plate window + the
         2000-0025-0004 paddle servo.  Two flywheel motors, the whole gap-adjust
         chain, sliding bearing carriages, base rails, both side plates.
feeder = paddle_launcher_feeder_a_prime_shared_staging.py (read-only import),
         kept at its OWN world coordinates -- measured, never retyped:
             feeder_shell_tray           x -85.48..215.26  |y|<=54  z -3.51..180.04
             paddle_rotor                axis (29.490, 111.460)
             paddle_flex_tip_1 / _2
             paddle_shaft_2106-4008-1920 y -96..+96
             paddle_shaft_support_bridge y 73..79
         guide_roof_3 / guide_wall_3_+/-1 / shooter_throat_+55 are NOT duplicated:
         they are measured identical inside the R51 base, so the base copy stays.
gate   = paddle_launcher_gate_drive_r49.py at PHI_DN (read-only import).
new    = the only geometry this round adds:
           * a bearing seat in each side plate at the R37 paddle axis, so the
             R37 shaft (y -96..+96) may cross the R51 plate (y +/-68..72),
           * two servo brackets from the R37 +Y shaft bridge to the servo frame,
           * two chassis rails tying the R37 shell/tray to the base rails.
Nothing is overwritten: R37/R47/R49/R50/R51 keep their own files and are only
imported.  No rigid part is added between the two flywheel axles.

Run:  .venv-cad/Scripts/python.exe -X utf8 cad/paddle_launcher_shooter_drive_r52.py [pollen] [--step] [--no-view]
Out:  cad/output/_r52_drive/
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path

import cadquery as cq

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import paddle_launcher_constrained as K                      # noqa: E402
import paddle_launcher_feeder_a_prime_shared as SH           # noqa: E402
import paddle_launcher_feeder_a_prime_shared_staging as ST   # noqa: E402
import paddle_launcher_gate_drive_r49 as G49                 # noqa: E402
import paddle_launcher_shooter_drive_r51 as R51              # noqa: E402
import t06_vendor_cad as TC                                  # noqa: E402

OUT = HERE / "output" / "_r52_drive"
OUT.mkdir(parents=True, exist_ok=True)
DESKTOP = Path(os.path.expanduser("~")) / "OneDrive" / "Desktop"

SERVO_SKU = "2000-0025-0004"
SERVO_FRAME_SKU = "1802-0043-0001"
SERVO_COUPLER_SKU = "4001-0025-4008"
BEARING_SKU = "1611-0514-4008"

SERVO_FACE_Y = 101.5           # same verified Y stack as R50
SERVO_FRAME_Y = 99.0
SERVO_COUPLER_Y = 96.5
SERVO_BRIDGE_Y = (79.0, 99.0)  # R37 bridge outer face -> servo frame
SERVO_BRIDGE_U = (-26.0, 26.0)
SERVO_BRIDGE_Z_H = 43.0
BEARING_Y = {-1: -70.0, 1: 76.0}
PLATE_BORE_R = 7.05            # O14.1 pocket for the 1611-0514-4008 bearing

# Tie the R37 shell/tray to the base rail WITHOUT entering the base rail body
# (and without touching either sliding carriage): the strip sits in the y gap
# between the tray wall (|y| = 54) and the base-rail inner face (|y| = 63) and
# rests on the base-rail top face (z = 16), i.e. it touches, never penetrates.
FEEDER_RAIL_X = (-80.0, 168.0)   # stops 7 mm short of the R49 gate frame (x>=175)
FEEDER_RAIL_Y = (53.5, 63.0)     # 0.5 mm bite into the tray wall = the joint allowance
FEEDER_RAIL_Z = (16.0, 30.0)

SETTINGS = dict(R51.SETTINGS)

DROP_EXACT = (
    "guide_floor_1", "guide_floor_2", "guide_floor_3",
    "guide_roof_1", "guide_roof_2",
    "guide_wall_1_-1", "guide_wall_1_+1", "guide_wall_2_-1", "guide_wall_2_+1",
    "one_way_finger_-1", "one_way_finger_+1",
    "paddle_hub",
    "paddle_arm_1", "paddle_arm_2", "paddle_arm_3",
    "paddle_hinge_1", "paddle_hinge_2", "paddle_hinge_3",
    "paddle_blade_1", "paddle_blade_2", "paddle_blade_3",
    "paddle_flex_tip_1", "paddle_flex_tip_2", "paddle_flex_tip_3",
    "paddle_shaft_2106-4008-1920",
    "paddle_shaft_support_bridge",
    "shooter_throat_-55",
)
DROP_PREFIX = ("paddle_cr_servo_", "paddle_servo_frame_",
               "paddle_servo_coupler_", "paddle_support_cheek_")

R37_FEEDER_NAMES = ("feeder_shell_tray", "paddle_rotor", "paddle_flex_tip_1",
                    "paddle_flex_tip_2", "paddle_shaft_2106-4008-1920",
                    "paddle_shaft_support_bridge")


# ------------------------------------------------------------- geometry ----
def _box(dx, dy, dz, c):
    return cq.Solid.makeBox(dx, dy, dz,
                            cq.Vector(-dx / 2.0, -dy / 2.0, -dz / 2.0)).translate(
        cq.Vector(*c))


_BBX = {}


def bbox_of(shape):
    bb = _BBX.get(id(shape))
    if bb is None:
        bb = shape.BoundingBox()
        _BBX[id(shape)] = bb
    return bb


def bbox_overlap(a, b, eps=1e-6):
    ba, bb = bbox_of(a), bbox_of(b)
    return (ba.xmax > bb.xmin + eps and bb.xmax > ba.xmin + eps
            and ba.ymax > bb.ymin + eps and bb.ymax > ba.ymin + eps
            and ba.zmax > bb.zmin + eps and bb.zmax > ba.zmin + eps)


def pair_volume(a, b):
    if not bbox_overlap(a, b):
        return 0.0
    try:
        return round(a.intersect(b).Volume(), 3)
    except Exception as exc:                                   # pragma: no cover
        return {"error": str(exc)[:90]}


def pick(parts, prefix):
    """Part names carry their SKU suffix; never retype them."""
    for n in sorted(parts):
        if n.startswith(prefix):
            return n
    raise KeyError(prefix)


def centre_xz(shape):
    bb = shape.BoundingBox()
    return (0.5 * (bb.xmin + bb.xmax), 0.5 * (bb.zmin + bb.zmax))


def world_xz_to_local(x, z):
    """Inverse of K.to_world for a point in the XZ plane (side plates are drawn
    in the local frame and only then rotated into the machine)."""
    ox, _, oz = K.SHOOTER_ORIGIN
    rx, rz = x - ox, z - oz
    a = math.radians(K.ANGLE)
    return (rx * math.cos(a) + rz * math.sin(a),
            -rx * math.sin(a) + rz * math.cos(a))


# ------------------------------------------------------------ the feeder ---
_kept_cache = {}
_paddle_xz = None
_variant = "pollen"


def feeder_kept(name):
    """R37 staging kept parts (it has its own disk cache, ~40 s cold)."""
    if name not in _kept_cache:
        t0 = time.time()
        kept, *_ = ST.build_variant_stage(name)
        _kept_cache[name] = kept
        print("[r52 %s] R37 staging %.1f s, %d parts"
              % (name, time.time() - t0, len(kept)), flush=True)
    return _kept_cache[name]


def paddle_axis(kept):
    """Measured off the final R37 rotor solid, not typed in."""
    return centre_xz(kept["paddle_rotor"])


def r52_plate(y):
    """R51 sliding-window plate + a bearing seat at the R37 paddle axis."""
    plate = R51.r51_plate(y)
    lx, lz = _paddle_local
    return plate.cut(K.cyl_y(PLATE_BORE_R, 14.0, (lx, y, lz)))


def new_support(paddle_xz):
    xp, zp = paddle_xz
    out = {}
    for u in SERVO_BRIDGE_U:
        out["servo_bridge_%+d" % int(u)] = _box(
            10.0, SERVO_BRIDGE_Y[1] - SERVO_BRIDGE_Y[0], SERVO_BRIDGE_Z_H,
            (xp + u, 0.5 * sum(SERVO_BRIDGE_Y), zp))
    for side in (-1, 1):
        out["feeder_mount_%+d" % side] = _box(
            FEEDER_RAIL_X[1] - FEEDER_RAIL_X[0],
            FEEDER_RAIL_Y[1] - FEEDER_RAIL_Y[0],
            FEEDER_RAIL_Z[1] - FEEDER_RAIL_Z[0],
            (0.5 * sum(FEEDER_RAIL_X), side * 0.5 * sum(FEEDER_RAIL_Y),
             0.5 * sum(FEEDER_RAIL_Z)))
    out["paddle_servo_%s" % SERVO_SKU] = TC.servo_with_output_face(
        SERVO_SKU, (xp, zp), SERVO_FACE_Y, -1)
    out["paddle_servo_frame_%s" % SERVO_FRAME_SKU] = TC.centered_y_axis_part(
        SERVO_FRAME_SKU, (xp, SERVO_FRAME_Y, zp), largest_solid_only=True)
    cpl = TC.centered_y_axis_part(SERVO_COUPLER_SKU, (xp, SERVO_COUPLER_Y, zp))
    cpl = cpl.translate(cq.Vector(-xp, -SERVO_COUPLER_Y, -zp))
    cpl = cpl.rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 180.0)
    out["paddle_servo_coupler_%s" % SERVO_COUPLER_SKU] = cpl.translate(
        cq.Vector(xp, SERVO_COUPLER_Y, zp))
    for side in (-1, 1):
        out["paddle_bearing_%+d_%s" % (side, BEARING_SKU)] = \
            TC.centered_y_axis_part(BEARING_SKU, (xp, BEARING_Y[side], zp))
    return out


def build(name, half):
    global _paddle_xz, _paddle_local
    feeder = feeder_kept(name)
    _paddle_xz = paddle_axis(feeder)
    _paddle_local = world_xz_to_local(*_paddle_xz)
    K.COTS["feeder_servo"]["sku"] = SERVO_SKU
    K.shooter_plate = r52_plate
    t0 = time.time()
    assy, mesh, shapes, named, kin = K.build(name, half)
    print("[r52 %s] R51 base %.1f s, %d parts"
          % (name, time.time() - t0, len(named)), flush=True)
    missing = [n for n in DROP_EXACT if n not in named]
    if missing:
        print("[r52 %s] R51 base has no %s (already gone, nothing to drop)"
              % (name, missing), flush=True)
    dropped = sorted(n for n in named
                     if n in DROP_EXACT or n.startswith(DROP_PREFIX))
    parts = {n: s for n, s in named.items() if n not in dropped}
    for n in R37_FEEDER_NAMES:
        parts[n] = feeder[n]
    gate = G49.drive_parts(G49.PHI_DN, 0)
    relief = 0.0
    if "gate_frame" in gate:
        try:
            inter = gate["gate_frame"].intersect(feeder["feeder_shell_tray"])
            relief = round(inter.Volume(), 3)
            if relief > 1.0:
                gate["gate_frame"] = gate["gate_frame"].cut(inter)
        except Exception as exc:
            print("[r52 %s] gate_frame relief skipped: %s" % (name, exc), flush=True)
        print("[r52 %s] gate frame relieved against the R37 tray by %.1f mm3"
              % (name, relief), flush=True)
    parts.update(gate)
    parts.update(new_support(_paddle_xz))
    return parts, kin, feeder, dropped, {"gate_frame_relief_mm3": relief}


# ----------------------------------------------------------------- checks --
def axle_isolation(parts):
    """No new part may reach both sliding carriages: that would pin the nip."""
    up = pick(parts, "bearing_carriage_upper_")
    lo = pick(parts, "bearing_carriage_lower_")
    skip = ("bearing_carriage_", "flywheel_shaft_", "gecko_flywheel_",
            "sonic_hub_", "shooter_side_plate_")
    hits = []
    for n, s in sorted(parts.items()):
        if n.startswith(skip):
            continue
        if bbox_overlap(s, parts[up]) and bbox_overlap(s, parts[lo]):
            hits.append({"part": n,
                         "vol_upper_mm3": pair_volume(s, parts[up]),
                         "vol_lower_mm3": pair_volume(s, parts[lo])})
    return hits


def contacts(parts, names_a, names_b, thr=0.5):
    hits = []
    for a in names_a:
        for b in names_b:
            if a == b or a not in parts or b not in parts:
                continue
            v = pair_volume(parts[a], parts[b])
            if isinstance(v, dict) or (v or 0.0) > thr:
                hits.append({"a": a, "b": b, "volume_mm3": v})
    return hits


def tip_radius(shape, axis):
    xp, zp = axis
    r = 0.0
    for v in shape.Vertices():
        r = max(r, math.hypot(v.X - xp, v.Z - zp))
    return round(r, 3)


def geometry(parts, paddle_xz, feeder):
    up = centre_xz(parts[pick(parts, "gecko_flywheel_upper_1")])
    lo = centre_xz(parts[pick(parts, "gecko_flywheel_lower_1")])
    rotor_tip = tip_radius(feeder["paddle_rotor"], paddle_xz)
    wheel_r = K.WHEEL_OD / 2.0
    sep = math.dist(up, lo)
    out = {
        "paddle_axis_measured_mm": [round(v, 3) for v in paddle_xz],
        "paddle_axis_generator_mm": [round(SH.F.PADDLE_CX, 3),
                                     round(SH.F.PADDLE_CZ, 3)],
        "upper_axle_measured_mm": [round(v, 3) for v in up],
        "lower_axle_measured_mm": [round(v, 3) for v in lo],
        "wheel_od_mm": K.WHEEL_OD,
        "wheel_r_mm": wheel_r,
        "rotor_tip_r_mm": rotor_tip,
        "axle_separation_mm": round(sep, 3),
        "nip_mm": round(sep - K.WHEEL_OD, 3),
        "nip_from_settings_mm": round(2.0 * SETTINGS[_variant] - K.WHEEL_OD, 3),
    }
    for lbl, c in (("upper", up), ("lower", lo)):
        d = math.dist(paddle_xz, c)
        out["paddle_to_%s_axle_mm" % lbl] = round(d, 3)
        out["paddle_tip_to_%s_wheel_face_mm" % lbl] = round(
            d - wheel_r - rotor_tip, 3)
    return out


def dump(parts):
    rows = []
    for n, s in sorted(parts.items()):
        bb = s.BoundingBox()
        rows.append({
            "part": n,
            "n_solids": len(s.Solids()),
            "volume_mm3": round(s.Volume(), 2),
            "bbox_mm": [round(v, 3) for v in (bb.xmin, bb.ymin, bb.zmin,
                                              bb.xmax, bb.ymax, bb.zmax)],
        })
    return rows


# -------------------------------------------------------------------- run --
def run(name="pollen", export=False, view=True):
    global _variant
    _variant = name
    half = SETTINGS[name]
    t0 = time.time()
    parts, kin, feeder, dropped, extra = build(name, half)
    print("[r52 %s] assembly %d parts (dropped %d from R51 base)"
          % (name, len(parts), len(dropped)), flush=True)

    r37_names = list(R37_FEEDER_NAMES)
    gate_names = sorted(n for n in parts if n.startswith("gate_"))
    new_names = sorted(n for n in parts
                       if n.startswith(("servo_bridge_", "feeder_mount_",
                                        "paddle_servo_", "paddle_bearing_")))
    moved = set(r37_names + gate_names + new_names)
    base_names = sorted(n for n in parts if n not in moved)

    rows = dump(parts)
    gl = geometry(parts, _paddle_xz, feeder)
    imported_vs_base = contacts(parts, r37_names + gate_names, base_names)
    new_vs_rest = contacts(parts, new_names, sorted(moved - set(new_names)) + base_names)
    inside_feeder = contacts(parts, gate_names, r37_names)
    axles = axle_isolation(parts)

    meta = {
        "units": "mm",
        "caliber": "T06 R52 = R51 independent-axle shooter base + R37/R49 feeder",
        "variant": name,
        "half_spacing_mm": half,
        "plate_window_mm": [2.0 * R51.WIN_U_HALF, R51.WIN_N1 - R51.WIN_N0],
        "plate_bore_local_xz_mm": [round(v, 3) for v in _paddle_local],
        "plate_bore_r_mm": PLATE_BORE_R,
        "servo_sku": SERVO_SKU,
        "servo_face_y_mm": SERVO_FACE_Y,
        "servo_frame_sku": SERVO_FRAME_SKU,
        "servo_coupler_sku": SERVO_COUPLER_SKU,
        "servo_coupler_y_mm": SERVO_COUPLER_Y,
        "bearing_sku": BEARING_SKU,
        "bearing_y_mm": {str(k): v for k, v in BEARING_Y.items()},
        "geometry": gl,
        "kinematics": kin,
        "r37_frozen_coordinates": True,
        "dropped_from_r51_base": dropped,
        "gate_frame_relief_mm3": extra["gate_frame_relief_mm3"],
        "drop_list_not_in_base": [n for n in DROP_EXACT if n not in parts],
        "r37_parts_moved_in": r37_names,
        "gate_parts_moved_in": gate_names,
        "new_support_parts": new_names,
        "axle_isolation_hits": axles,
        "imported_vs_base": imported_vs_base,
        "new_vs_rest": new_vs_rest,
        "gate_vs_feeder": inside_feeder,
        "n_parts": len(parts),
        "parts": rows,
    }

    # Report first: a failure in the renderer or the STEP writer must never
    # cost another full rebuild.
    (OUT / ("report_r52_%s.json" % name)).write_text(
        json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")

    if view:
        import paddle_launcher_shooter_drive_r52_view as V
        from PIL import Image
        up = centre_xz(parts[pick(parts, "gecko_flywheel_upper_1")])
        lo = centre_xz(parts[pick(parts, "gecko_flywheel_lower_1")])
        frames = [
            V.render(parts, "xy", (-180.0, 270.0, -245.0, 175.0),
                     "A  俯视：R51 底座 + R37 送球件 + R49 闸门",
                     "两台飞轮马达 5203-2402-0003 在 -Y；拨杆舵机 2000-0025-0004 在 +Y；"
                     "R37 送球件保持自身坐标不动"),
            V.render(parts, "xz", (-180.0, 270.0, -40.0, 405.0),
                     "B  侧视（沿 -Y 看）：整机",
                     "两侧 59x56 滑窗侧板 + 底盘纵梁 = 支撑；两根飞轮轴各自独立，"
                     "调隙链只驱动滑座"),
            V.render(parts, "xz", (-150.0, 260.0, -40.0, 260.0),
                     "C  侧视放大：R37 外罩/托板 -> 拨杆 -> 夹口 -> 喉道",
                     "实测：拨杆轴 %s，下轴 %s，叶尖 %s mm，到轮面 %s mm"
                     % (["%.2f" % v for v in gl["paddle_axis_measured_mm"]],
                        ["%.2f" % v for v in gl["lower_axle_measured_mm"]],
                        gl["rotor_tip_r_mm"],
                        gl["paddle_tip_to_lower_wheel_face_mm"]),
                     marks=[{"dot": up, "color": (232, 60, 60, 255)},
                            {"dot": lo, "color": (232, 60, 60, 255)},
                            {"dot": _paddle_xz, "color": (40, 90, 232, 255)},
                            {"circle": (_paddle_xz[0], _paddle_xz[1],
                                        gl["rotor_tip_r_mm"]),
                             "color": (40, 90, 232, 200)}]),
        ]
        W, H = V.W, V.H
        sheet = Image.new("RGB", (2 * W + 46, 2 * H + 46), (250, 250, 252))
        for f, pos in zip(frames, [(0, 0), (W + 46, 0), (0, H + 46)]):
            sheet.paste(f, pos)
        png = OUT / ("r52_assembly_sheet_%s.png" % name)
        sheet.save(png)
        meta["view_png"] = str(png)
        print("[r52 %s] view -> %s" % (name, png), flush=True)

    if export:
        stem = "T06_shooter_assembly_R52_%s" % name
        assy = cq.Assembly(name=stem)
        for n, s in parts.items():
            assy.add(s, name=n, color=cq.Color(0.72, 0.74, 0.78, 1.0))
        dst = OUT / (stem + ".step")
        assy.export(str(dst), exportType="STEP")
        meta["step_mb"] = round(dst.stat().st_size / 1e6, 1)
        try:
            desk = DESKTOP / (stem + ".step")
            if desk.exists():
                desk.unlink()
            os.link(dst, desk)
        except Exception:
            import shutil
            shutil.copyfile(dst, DESKTOP / (stem + ".step"))
        print("[r52 %s] STEP -> %.1f MB" % (name, meta["step_mb"]), flush=True)

    (OUT / ("report_r52_%s.json" % name)).write_text(
        json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")

    print("[r52 %s] geometry %s"
          % (name, json.dumps(gl, ensure_ascii=False)), flush=True)
    print("[r52 %s] axle-isolation hits (must be []): %s"
          % (name, json.dumps(axles, ensure_ascii=False)), flush=True)
    print("[r52 %s] R37/R49 vs R51 base clashes: %d" % (name, len(imported_vs_base)),
          flush=True)
    for h in imported_vs_base:
        print("   !", h, flush=True)
    print("[r52 %s] new support vs everything: %d" % (name, len(new_vs_rest)),
          flush=True)
    for h in new_vs_rest:
        print("   ~", h, flush=True)
    print("[r52 %s] gate vs feeder: %d" % (name, len(inside_feeder)), flush=True)
    for h in inside_feeder:
        print("   *", h, flush=True)
    print("[r52 %s] done in %.1f s" % (name, time.time() - t0), flush=True)
    return meta


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    names = [a for a in argv if not a.startswith("-")] or ["pollen"]
    for n in names:
        run(n, export="--step" in argv, view="--no-view" not in argv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
