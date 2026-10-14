# ============================================================================
# SUPERSEDED by cad/paddle_launcher_shooter_lock_r53b.py  (2026-10-13, DEC-0051)
#
# * The wing-nut lock this file builds needs a HUMAN to loosen / tighten it, and
#   in a match nobody may touch the robot.  r53b replaces it with an always-on
#   compression-spring clamp that the EXISTING 25-2 gap servo can still slide.
# * BUG RETRACTED: the lock parts here are never passed through K.to_world(), so
#   they are compared against the world frame in their LOCAL coordinates.  Every
#   "clash" this file ever reported is therefore meaningless -- do not quote it.
#   r53b fixes the frame bug.
# * Kept only as the parent / lineage record.  Do not build a delivery from it.
# ============================================================================
# -*- coding: utf-8 -*-
"""T06 R53 -- the sliding window, redone: guided AND lockable.

R51/R52 opened a 59 x 56 mm window in each side plate and dropped two
5 x 10 x 52 mm "guide rails" into it.  Measuring the frozen R51 geometry
(and the R51 generator itself, rebuilt in the same process) shows those rails
touch nothing:

  * rail -> bearing carriage = 1.000 mm  (both settings, all four rails)
  * rail -> side plate       = 0.500 mm
  * the rail bbox is byte-identical for POLLEN and NECTAR => the rail never
    follows the carriage, it is a free block.

So the window guided nothing and clamped nothing.  R53 replaces the rails:

 1. the four free rails are deleted;
 2. the carriage grows two clamp ears (x 23 -> +-42, 3 mm thick) that straddle
    the side plate with 0.30 mm running clearance.  The ears riding the plate
    faces ARE the guide, and a face pair kills the carriage rotation the rails
    were supposed to kill;
 3. each side plate gets two 5.2 x 44 mm lock slots at x = +-36, spanning the
    whole POLLEN..NECTAR bolt travel (z 68 .. 103);
 4. two M4 studs per carriage per plate carry a washer and a wing nut: tighten
    to clamp both ears onto the plate (friction lock), back it off and gap
    adjustment is free again.  Nothing connects the two flywheel axles, so
    axle_isolation stays empty.

Run:  .venv-cad/Scripts/python.exe -X utf8 cad/paddle_launcher_shooter_lock_r53.py pollen --step
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

import paddle_launcher_constrained as K                      # noqa: E402
import paddle_launcher_shooter_drive_r51 as R51               # noqa: E402
import paddle_launcher_shooter_drive_r52 as R52               # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = HERE / "output" / "_r53_lock"
OUT.mkdir(parents=True, exist_ok=True)
DESKTOP = Path(os.path.expanduser("~")) / "OneDrive" / "Desktop"

SETTINGS = dict(R51.SETTINGS)

# Freeze the untouched R51/R52 definitions before monkey-patching: the R53
# replacements below must call the originals, not themselves.
_ORIG_CARRIAGE = K.bearing_carriage
_ORIG_PLATE = R52.r52_plate

# ------------------------------------------------------------- dimensions --
PLATE_Y = R51.PLATE_Y            # +-70, plate is 4 mm thick (68..72)
PLATE_HALF_T = R51.PLATE_T / 2.0  # 2.0
EAR_X = 42.0                     # ear half width; carriage is 23.0
EAR_T = 3.0                      # ear thickness
EAR_GAP = 0.30                   # running clearance ear face -> plate face
EAR_Z_HALF = R51.CARRIAGE_N_HALF  # 19.0, same as the carriage body
CLAMP_U = 36.0                   # lock bolt x
CLAMP_Z = 12.0                   # lock bolt z offset from the carriage centre
SLOT_W = 5.2                     # plate lock slot width
SLOT_Z0, SLOT_Z1 = 63.5, 107.5   # covers bolt z 68 (pollen) .. 103 (nectar)
STUD_R = 2.0                     # M4
STUD_HEAD_R = 3.5
STUD_HEAD_T = 3.0
WASHER_R = 5.0
WASHER_T = 1.2
NUT_R = 4.0
NUT_T = 3.2
WING_LEN = 12.0
WING_T = 2.6
WING_H = 7.0
BOLT_HOLE_R = 2.2                # M4 clearance in the ears
PLATE_CUT_T = 12.0               # cutting depth across the plate


def _ear_y(y, side):
    """(inner ear centre, outer ear centre) for a plate centred on y."""
    off = PLATE_HALF_T + EAR_GAP + EAR_T / 2.0
    return y - side * off, y + side * off


def r53_carriage(center_n, y):
    """R51 carriage + clamp ears + M4 clearance holes (DEC-0037 chain intact)."""
    side = 1 if y > 0 else -1
    body = _ORIG_CARRIAGE(center_n, y)
    for cy in _ear_y(y, side):
        body = body.fuse(K.box(2.0 * EAR_X, EAR_T, 2.0 * EAR_Z_HALF,
                               (0.0, cy, center_n)))
    for u in (-CLAMP_U, CLAMP_U):
        for dz in (-CLAMP_Z, CLAMP_Z):
            body = body.cut(K.cyl_y(BOLT_HOLE_R, 24.0, (u, y, center_n + dz)))
    return body


def r53_plate(y):
    """R52 plate (59 x 56 window + paddle bore) + two lock slots."""
    plate = _ORIG_PLATE(y)
    for u in (-CLAMP_U, CLAMP_U):
        plate = plate.cut(K.box(SLOT_W, PLATE_CUT_T, SLOT_Z1 - SLOT_Z0,
                                (u, y, 0.5 * (SLOT_Z0 + SLOT_Z1))))
    return plate


def lock_parts(half_spacing):
    """M4 stud + washer + wing nut for every ear pair of this setting."""
    out = {}
    for label, sign in (("upper", 1), ("lower", -1)):
        n = sign * half_spacing
        for side in (-1, 1):
            y = side * PLATE_Y
            for u in (-CLAMP_U, CLAMP_U):
                for dz in (-CLAMP_Z, CLAMP_Z):
                    z = n + dz
                    head_y = y - side * (PLATE_HALF_T + EAR_GAP + EAR_T
                                         + STUD_HEAD_T / 2.0)
                    stud_y = y + side * 1.05
                    wash_y = y + side * (PLATE_HALF_T + EAR_GAP + EAR_T
                                         + WASHER_T / 2.0)
                    nut_y = y + side * (PLATE_HALF_T + EAR_GAP + EAR_T
                                        + WASHER_T + NUT_T / 2.0)
                    piece = K.cyl_y(STUD_R, 18.7, (u, stud_y, z))
                    piece = piece.fuse(K.cyl_y(STUD_HEAD_R, STUD_HEAD_T,
                                               (u, head_y, z)))
                    piece = piece.fuse(K.cyl_y(WASHER_R, WASHER_T, (u, wash_y, z)))
                    piece = piece.fuse(K.cyl_y(NUT_R, NUT_T, (u, nut_y, z)))
                    for ws in (-1, 1):
                        piece = piece.fuse(K.box(WING_LEN, WING_T, WING_H,
                                                 (u + ws * (NUT_R + WING_LEN / 2.0 - 1.0),
                                                  nut_y, z)))
                    name = "carriage_lock_%s_%+d_%+.0f_%+.0f" % (label, side, u, dz)
                    out[name] = piece
    return out


def build(name, half):
    R52.r52_plate = r53_plate
    K.bearing_carriage = r53_carriage
    parts, kin, feeder, dropped, extra = R52.build(name, half)
    rails = sorted(n for n in parts if n.startswith("carriage_guide_"))
    for n in rails:
        parts.pop(n)
    locks = lock_parts(half)
    parts.update(locks)
    return parts, kin, feeder, dropped, rails, sorted(locks)


# ----------------------------------------------------------------- checks --
def screen(parts, names_a, names_b, thr=0.5):
    return R52.contacts(parts, names_a, names_b, thr)


def window_clearance(parts, half):
    """Ear-to-plate gap and carriage-to-window-wall gap, measured."""
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape
    rows = {}
    for side in (-1, 1):
        plate = parts["shooter_side_plate_%+d" % side]
        for label, sign in (("upper", 1), ("lower", -1)):
            car = parts["bearing_carriage_%s_%+d" % (label, side)]
            d = BRepExtrema_DistShapeShape(car.wrapped, plate.wrapped)
            d.Perform()
            rows["%s_%+d" % (label, side)] = round(d.Value(), 4)
    return rows


def lock_travel(half):
    """Do the plate slots really span the bolt travel of both settings?"""
    lo = 0.5 * (SLOT_Z0 + SLOT_Z1) - 0.5 * (SLOT_Z1 - SLOT_Z0)
    hi = 0.5 * (SLOT_Z0 + SLOT_Z1) + 0.5 * (SLOT_Z1 - SLOT_Z0)
    need = sorted({h + s * CLAMP_Z for h in SETTINGS.values() for s in (-1, 1)})
    return {
        "slot_z_mm": [lo, hi],
        "bolt_z_needed_mm": need,
        "covered": bool(lo <= min(need) and max(need) <= hi),
        "slack_mm": [round(min(need) - lo, 2), round(hi - max(need), 2)],
    }


def run(name, export=False, view=True):
    half = SETTINGS[name]
    t0 = time.time()
    parts, kin, feeder, dropped, rails, locks = build(name, half)
    print("[r53 %s] %d parts (dropped %d from R51 base, %d free rails removed, "
          "%d lock parts added)" % (name, len(parts), len(dropped), len(rails),
                                    len(locks)), flush=True)

    plates = sorted(n for n in parts if n.startswith("shooter_side_plate_"))
    carrs = sorted(n for n in parts if n.startswith("bearing_carriage_"))
    lock_rest = screen(parts, locks, sorted(set(parts) - set(locks) - set(carrs)))
    lock_carr = screen(parts, locks, carrs)
    plate_rest = screen(parts, plates, sorted(set(parts) - set(plates) - set(locks)))
    axles = R52.axle_isolation(parts)
    clear = window_clearance(parts, half)
    geom = R52.geometry(parts, R52._paddle_xz, feeder)

    meta = {
        "units": "mm",
        "caliber": "T06 R53 = R52 + sliding window redone (guided + lockable)",
        "variant": name,
        "half_spacing_mm": half,
        "nip_mm": round(2.0 * half - K.WHEEL_OD, 3),
        "changes_vs_r52": [
            "deleted %d free carriage guide rails" % len(rails),
            "carriage ears x 23 -> +-42, %g mm thick, %g mm running clearance"
            % (EAR_T, EAR_GAP),
            "side plate lock slots %g x %g at x = +-36" % (SLOT_W, SLOT_Z1 - SLOT_Z0),
            "%d M4 stud + washer + wing nut lock parts" % len(locks),
        ],
        "removed_rails": rails,
        "lock_parts": locks,
        "lock_travel": lock_travel(half),
        "ear_to_plate_min_gap_mm": clear,
        "axle_isolation_hits": axles,
        "lock_vs_rest_clashes": lock_rest,
        "lock_vs_carriage_clashes": lock_carr,
        "plate_vs_rest_clashes": plate_rest,
        "geometry": geom,
        "kinematics": kin,
        "n_parts": len(parts),
        "parts": R52.dump(parts),
    }
    (OUT / ("report_r53_%s.json" % name)).write_text(
        json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")

    print("[r53 %s] lock travel: %s" % (name, json.dumps(meta["lock_travel"])), flush=True)
    print("[r53 %s] ear-plate min gap: %s" % (name, json.dumps(clear)), flush=True)
    print("[r53 %s] axle-isolation hits (must be []): %s"
          % (name, json.dumps(axles, ensure_ascii=False)), flush=True)
    print("[r53 %s] lock vs everything else: %d" % (name, len(lock_rest)), flush=True)
    for h in lock_rest:
        print("   !", json.dumps(h, ensure_ascii=False), flush=True)
    print("[r53 %s] lock vs carriage (ears only expected): %d"
          % (name, len(lock_carr)), flush=True)
    for h in lock_carr:
        print("   ~", json.dumps(h, ensure_ascii=False), flush=True)
    print("[r53 %s] plate vs rest: %d" % (name, len(plate_rest)), flush=True)
    for h in plate_rest:
        print("   *", json.dumps(h, ensure_ascii=False), flush=True)

    if export:
        stem = "T06_shooter_assembly_R53_%s" % name
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
        print("[r53 %s] STEP -> %.1f MB" % (name, meta["step_mb"]), flush=True)
        (OUT / ("report_r53_%s.json" % name)).write_text(
            json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")

    print("[r53 %s] done in %.1f s" % (name, time.time() - t0), flush=True)
    return meta


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    names = [a for a in argv if not a.startswith("-")] or ["pollen"]
    for n in names:
        run(n, export="--step" in argv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
