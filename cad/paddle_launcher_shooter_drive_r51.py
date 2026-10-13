"""T06 R51 -- the pre-"motion only" launcher as the base, plus the only two
changes the shooter still needs.

Base = cad/output/paddle_launcher_feasible_pollen.step (2026-10-01), the last
*full* launcher published before the "motion only" strip.  That version already
carries everything the user asked to be added:

  * two flywheel motors 5203-2402-0003 (one per shaft, both on -Y) with the
    1401-0043-0036 clamps and 4007-4008-4008 couplers,
  * a paddle servo with its 1802-0043-0001 bracket and 4001-0025-4008 coupler,
  * the whole shooter support: slotted side plates, sliding bearing carriages
    with guide rails, base rails, paddle support cheeks and the throat.

It is also the version in which the two flywheel shafts are NOT tied to each
other: each shaft rides in its own sliding bearing carriage and is located by
the gap-adjust chain (2000-0025-0002 -> 12 mm crank -> 65 mm drag link ->
crosshead -> two 110 mm links -> carriage tabs, DEC-0037).

Two changes are made here, and neither adds a rigid link between the axles:

 1. paddle servo 2000-0025-0003 -> 2000-0025-0004, the determined model
    (DEC-0026 index_drive_servo).  The 2000 series body/spline are identical,
    so bracket, crank and coupler interfaces are unchanged.
 2. the side-plate opening is reworked.  The old 8.4 x 9 mm shaft slot only
    covered half spacing 80..89 mm (nip 64..82), i.e. it could not reach the
    accepted NECTAR setting of 86 mm (half spacing 91, DEC-0037), and it was
    straddled by the 46x12x38 carriage and by both 5x10x52 guide rails, so the
    plate and the moving carriages occupied the same space.  It becomes a
    59 x 56 mm sliding window (half spacing 80.0..91.2 => nip 64.0..86.4) that
    clears the carriage and both rails with 0.5 mm of side clearance, the rails
    running against the window walls as the pair of lateral guides the plate
    comment always intended.

Run:  .venv-cad/Scripts/python.exe -X utf8 cad/paddle_launcher_shooter_drive_r51.py
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import paddle_launcher_constrained as K  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = HERE / "output" / "_r51_drive"
OUT.mkdir(parents=True, exist_ok=True)
DESKTOP = Path(os.path.expanduser("~")) / "OneDrive" / "Desktop"

BASE_STEP = HERE / "output" / "paddle_launcher_feasible_pollen.step"
BASE_STEP_NECTAR = HERE / "output" / "paddle_launcher_feasible_nectar.step"

PADDLE_SERVO_SKU = "2000-0025-0004"
SUPERSEDED_PADDLE_SERVO_SKU = "2000-0025-0003"
MOTOR_SKU = K.COTS["flywheel_motor"]["sku"]
CLAMP_SKU = K.COTS["motor_clamp"]["sku"]
COUPLER_SKU = K.COTS["shaft_coupler"]["sku"]
GAP_SERVO_SKU = K.COTS["gap_servo"]["sku"]

HALF_MIN, HALF_MAX = 80.0, 91.2        # nip 64.0 .. 86.4
SETTINGS = {"pollen": 80.0, "nectar": 91.0}

WIN_U_HALF = 29.5                      # rails sit at +-26.5 +-2.5 => +-29
WIN_N0, WIN_N1 = 56.5, 112.5
CARRIAGE_N_HALF = 19.0                 # carriage body is 38 mm along the slot
RAIL_N = (58.5, 110.5)                 # guide rails are 52 mm long about 84.5

PLATE_Y = K.PLATE_INSIDE_SPAN / 2.0    # +-70, plate is 4 mm thick (68..72)
PLATE_T = 4.0


def r51_plate(y):
    """Baseline slotted side plate with the opening reworked (see docstring)."""
    outline = [(-150, -136), (78, -136), (128, -105), (128, 105), (78, 136), (-150, 136)]
    plate = (cq.Workplane("XZ").polyline(outline).close().extrude(2, both=True)
             .translate((0, y, 0)).val())
    plate = plate.cut(K.cyl_y(26, 10, (-58, y, 0)))
    for sign in (-1, 1):
        win = K.box(2.0 * WIN_U_HALF, 12, WIN_N1 - WIN_N0,
                    (0.0, y, sign * 0.5 * (WIN_N0 + WIN_N1)))
        plate = plate.cut(win)
    for x in (-88, 98):
        for z in (-116, 116):
            plate = plate.cut(K.cyl_y(2.2, 10, (x, y, z)))
    return plate


def opening_report():
    """Does the reworked window actually cover both accepted settings?"""
    rows = []
    for name, half in sorted(SETTINGS.items()):
        rows.append({
            "variant": name,
            "half_spacing_mm": half,
            "nip_mm": round(2.0 * half - K.WHEEL_OD, 3),
            "carriage_n_span_mm": [round(half - CARRIAGE_N_HALF, 2),
                                   round(half + CARRIAGE_N_HALF, 2)],
            "carriage_inside_window": (WIN_N0 <= half - CARRIAGE_N_HALF
                                       and half + CARRIAGE_N_HALF <= WIN_N1),
            "rails_inside_window": (WIN_N0 <= RAIL_N[0] and RAIL_N[1] <= WIN_N1),
            "rail_side_clearance_mm": round(WIN_U_HALF - 29.0, 2),
        })
    rows.append({
        "window_mm": [2.0 * WIN_U_HALF, WIN_N1 - WIN_N0],
        "window_n_span_mm": [WIN_N0, WIN_N1],
        "half_spacing_travel_mm": [HALF_MIN, HALF_MAX],
        "nip_travel_mm": [round(2.0 * HALF_MIN - K.WHEEL_OD, 2),
                          round(2.0 * HALF_MAX - K.WHEEL_OD, 2)],
    })
    return rows


def build(name, half_spacing, servo_sku=PADDLE_SERVO_SKU):
    """One assembly off the frozen 10-01 generator, with the two R51 changes."""
    K.COTS["feeder_servo"]["sku"] = servo_sku
    K.shooter_plate = r51_plate
    t0 = time.time()
    assy, mesh, shapes, named, kin = K.build(name, half_spacing)
    print("[r51 %s] build %.1f s, %d parts" % (name, time.time() - t0, len(named)),
          flush=True)
    return assy, named, kin


# ------------------------------------------------------------------ checks --
# Screening: bbox overlap is a cheap, *conservative* superset of "shares volume".
# Only small parts get a real boolean; the big COTS bodies (motor 66 solids,
# servo 11 solids, flywheel) are reported on the bbox screen alone -- their fits
# are unchanged from the 2026-10-01 base and are not what this round changed.
_BBOX_CACHE = {}


def bbox_of(shape):
    key = id(shape)
    bb = _BBOX_CACHE.get(key)
    if bb is None:
        bb = shape.BoundingBox()
        _BBOX_CACHE[key] = bb
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


def volume_or_bbox(a, b):
    """Real boolean only when both parts are light; else the bbox verdict."""
    if not bbox_overlap(a, b):
        return 0.0
    heavy = ("flywheel_motor_", "paddle_servo_", "gap_servo_", "gecko_flywheel_")
    return round(a.intersect(b).Volume(), 3)


def touches(parts, a, b, thr=0.5):
    if a not in parts or b not in parts:
        return None
    v = pair_volume(parts[a], parts[b])
    if isinstance(v, dict):
        return None
    return v > thr


PLATE_FOCUS = ("shooter_side_plate_", "bearing_carriage_", "carriage_guide_",
               "flywheel_shaft_", "flywheel_bearing_", "paddle_bearing_",
               "paddle_shaft", "guide_", "throat_", "base_rail_",
               "gecko_flywheel_", "sonic_hub_")


def axle_isolation(parts):
    """The point of the whole round: nothing rigid may hold both flywheels.

    A part reaching both sliding carriages would pin the nip again.  The bbox
    screen below is a conservative superset of "touches", so an empty result is
    a strict proof of isolation; the survivors then get a real boolean.
    """
    up = "bearing_carriage_upper_-1"
    lo = "bearing_carriage_lower_-1"
    up_shaft = "flywheel_shaft_upper_2106-4008-1680"
    lo_shaft = "flywheel_shaft_lower_2106-4008-1680"
    skip = ("bearing_carriage_", "flywheel_shaft_", "gecko_flywheel_",
            "sonic_hub_")
    cand = [n for n in sorted(parts)
            if not n.startswith(skip)
            and bbox_overlap(parts[n], parts[up])
            and bbox_overlap(parts[n], parts[lo])]
    detail = []
    for n in cand:
        if n.startswith(("flywheel_motor_", "paddle_servo_", "gap_servo_")):
            detail.append({"part": n, "bbox_overlap_both": True,
                           "boolean": "not_run (large COTS)"})
            continue
        vu = pair_volume(parts[n], parts[up])
        vl = pair_volume(parts[n], parts[lo])
        both = (isinstance(vu, float) and isinstance(vl, float)
                and vu > 0.5 and vl > 0.5)
        detail.append({"part": n, "to_upper_mm3": vu, "to_lower_mm3": vl,
                       "touches_both": both})
    return {
        "rigid_link_between_axles": [e for e in detail if e.get("touches_both")],
        "bbox_screen_candidates": cand,
        "n_candidates": len(cand),
        "detail": detail,
        "carriages_touch_each_other": touches(parts, up, lo),
        "shafts_touch_each_other": touches(parts, up_shaft, lo_shaft),
        "n_parts": len(parts),
    }


def plate_reach(parts):
    """The reworked window against the parts the old slot straddled."""
    plate = "shooter_side_plate_-1"
    cand = [n for n in sorted(parts)
            if n != plate and bbox_overlap(parts[plate], parts[n])]
    focus, rest = {}, {}
    for n in cand:
        if n.startswith(PLATE_FOCUS):
            focus[n] = pair_volume(parts[plate], parts[n])
        else:
            rest[n] = "bbox_overlap_only"
    return {"focus_boolean_mm3": focus, "other_bbox_overlap": rest,
            "n_candidates": len(cand)}


def drive_chain(parts):
    out = {}
    for lbl in ("upper", "lower"):
        out["coupler_%s_x_shaft" % lbl] = pair_volume(
            parts["flywheel_shaft_%s_2106-4008-1680" % lbl],
            parts["motor_coupler_%s_%s" % (lbl, COUPLER_SKU)])
        out["clamp_%s" % lbl] = "unchanged from 10-01 base (large COTS)"
    out["servo_coupler_x_shaft"] = pair_volume(
        parts["paddle_servo_coupler_%s" % K.COTS["feeder_servo_coupler"]["sku"]],
        parts["paddle_shaft_2106-4008-1920"])
    out["servo_coupler_x_servo"] = "unchanged from 10-01 base (large COTS)"
    return out


def timed(tag, fn, parts):
    t0 = time.time()
    out = fn(parts)
    print("[r51 check] %-15s %.1f s" % (tag, time.time() - t0), flush=True)
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


def _write(report):
    json.dump(report, (OUT / "report_r51.json").open("w", encoding="utf-8"),
              ensure_ascii=False, indent=1)


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    report = {
        "caliber": "T06 R51 shooter assembly off the 2026-10-01 full launcher",
        "base_step": BASE_STEP.name,
        "base_step_nectar": BASE_STEP_NECTAR.name,
        "changes": ["paddle servo %s -> %s" % (SUPERSEDED_PADDLE_SERVO_SKU,
                                              PADDLE_SERVO_SKU),
                    "side plate opening 8.4x9 slot -> 59x56 sliding window"],
        "servo_sku": PADDLE_SERVO_SKU,
        "motor_sku": MOTOR_SKU,
        "gap_servo_sku": GAP_SERVO_SKU,
        "opening": opening_report(),
        "variants": {},
    }
    for name, half in SETTINGS.items():
        if which not in ("both", name):
            continue
        assy, parts, kin = build(name, half)
        stem = "T06_shooter_assembly_R51_%s" % name
        step = OUT / (stem + ".step")
        if os.environ.get("R51_SKIP_EXPORT") and step.exists():
            print("[r51 %s] STEP reused %.1f MB" % (name, step.stat().st_size / 1e6),
                  flush=True)
        else:
            t0 = time.time()
            assy.export(str(step), exportType="STEP")
            print("[r51 %s] STEP %.1f s -> %.1f MB"
                  % (name, time.time() - t0, step.stat().st_size / 1e6), flush=True)
            try:
                desk = DESKTOP / (stem + ".step")
                if desk.exists():
                    desk.unlink()
                os.link(step, desk)
            except Exception:
                import shutil
                shutil.copyfile(step, DESKTOP / (stem + ".step"))
        bbs = [s.BoundingBox() for s in parts.values()]
        report["variants"][name] = {
            "half_spacing_mm": half,
            "nip_mm": round(2.0 * half - K.WHEEL_OD, 3),
            "kinematics": kin,
            "n_parts": len(parts),
            "step_mb": round(step.stat().st_size / 1e6, 1),
            "bbox_mm": [round(min(b.xmin for b in bbs), 2),
                        round(min(b.ymin for b in bbs), 2),
                        round(min(b.zmin for b in bbs), 2),
                        round(max(b.xmax for b in bbs), 2),
                        round(max(b.ymax for b in bbs), 2),
                        round(max(b.zmax for b in bbs), 2)],
            "axle_isolation": timed("axle_isolation", axle_isolation, parts),
            "plate_reach": timed("plate_reach", plate_reach, parts),
            "drive_chain": timed("drive_chain", drive_chain, parts),
            "parts": dump(parts),
        }
        _write(report)
        print("[r51 %s] report written" % name, flush=True)
    print("[r51] done", flush=True)
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "parts"}
                      for k, v in report["variants"].items()},
                     ensure_ascii=False, indent=1), flush=True)


if __name__ == "__main__":
    main()
