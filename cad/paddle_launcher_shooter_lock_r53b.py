# -*- coding: utf-8 -*-
"""T06 R53b -- the sliding window: guided AND self-clamping (no hands).

R53 asked the operator to loosen / tighten a wing nut to clamp the carriage onto
the side plate.  That is illegal -- during a match nobody may touch the robot.
R53b keeps every R53 dimension and replaces only the fastener stack:

  * the butterfly (wing) nut is deleted;
  * every M4 stud now carries a compression spring between the outer ear and
    the washer, closed by a nyloc nut that is set ONCE when the robot is built;
  * the spring is always compressed => both ears are always pressed onto the
    side plate => the carriage is friction-locked even with the robot powerless
    (fail-safe, nothing to remember before a match);
  * the preload (PRELOAD_N per stud) is deliberately small, so the EXISTING
    25-2 gap servo still wins and can slide the carriage between POLLEN and
    NECTAR.  That is the whole "adjust it with the servo we already have" story:
    no new servo, no spare channel, no human in the loop.

Axle isolation is untouched: nothing here bridges the two flywheel axles.

Run:  .venv-cad/Scripts/python.exe -X utf8 cad/paddle_launcher_shooter_lock_r53b.py pollen --step
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

OUT = HERE / "output" / "_r53b_auto"
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
NUT_AF = 6.93                    # M4 nyloc nut across flats
SPRING_COIL_R = 2.5              # mean coil radius -> OD 5.5 / ID 4.5 on a M4 stud
SPRING_WIRE_R = 0.25
SPRING_TURNS = 4
SPRING_INSTALLED = 6.0           # installed (compressed) length, mm
SPRING_FREE = 8.4                # free length, mm
SPRING_RATE = 1.24               # N/mm  CALCULATED  k = G d^4 / (8 D^3 n)
PRELOAD_N = 3.0                  # N per stud  CALCULATED = rate * (free - installed)
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
    """R52 plate (59 x 56 window + paddle bore) + four lock slots.

    There are TWO carriages, at local n = +/-half_spacing, so the slot has to
    exist on BOTH sides of the launcher axis.  The first R53b pass only cut the
    +n side, which drove the lower carriage's 8 studs straight through 4.0 mm of
    solid plate (pi*2^2*4.0 = 50.265 mm3 each, exactly what the checker saw).
    """
    plate = _ORIG_PLATE(y)
    for u in (-CLAMP_U, CLAMP_U):
        for sgn in (1, -1):
            zc = sgn * 0.5 * (SLOT_Z0 + SLOT_Z1)
            plate = plate.cut(K.box(SLOT_W, PLATE_CUT_T, SLOT_Z1 - SLOT_Z0,
                                    (u, y, zc)))
    return plate


def _spring(y0, sgn, u, z):
    """Compression spring as SPRING_TURNS stacked rings (low-detail proxy).

    y0 is the outer ear face; the coil grows away from the plate along sgn.
    """
    pitch = (SPRING_INSTALLED - 2.0 * SPRING_WIRE_R) / (SPRING_TURNS - 1)
    out = None
    for i in range(SPRING_TURNS):
        t = cq.Solid.makeTorus(SPRING_COIL_R, SPRING_WIRE_R)
        t = t.rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), -90.0)
        t = t.translate(cq.Vector(u, y0 + sgn * (SPRING_WIRE_R + i * pitch), z))
        out = t if out is None else out.fuse(t)
    return out


def clamp_parts(half_spacing):
    """M4 stud + washer + nyloc nut AND a preload spring, per ear pair.

    Everything is built in the shooter-local frame and then pushed through
    K.to_world(), exactly like the R51/R52 generators: ``parts`` is in world
    coordinates, so a local-frame clamp would be compared against the wrong
    place.  (R53 shipped that bug: its lock parts were never transformed, which
    is why its "clashes" were meaningless.  It is fixed here.)

    Stack along y, offsets from the plate centre (side = +1):
        head  -8.3..-5.3 | ear -5.3..-2.3 | plate | ear +2.3..+5.3 | spring | washer | nut
    R53 tightened a wing nut by hand; here the spring does the clamping and the
    nyloc nut is only the reaction seat, set once when the robot is built.
    """
    out = {}
    ear_outer = PLATE_HALF_T + EAR_GAP + EAR_T          # 5.3
    for label, sign in (("upper", 1), ("lower", -1)):
        n = sign * half_spacing
        for side in (-1, 1):
            y = side * PLATE_Y
            head_y = y - side * (ear_outer + STUD_HEAD_T / 2.0)
            wash_y = y + side * (ear_outer + SPRING_INSTALLED + WASHER_T / 2.0)
            nut_y = y + side * (ear_outer + SPRING_INSTALLED + WASHER_T + NUT_T / 2.0)
            bottom = head_y - side * STUD_HEAD_T / 2.0
            top = y + side * (ear_outer + SPRING_INSTALLED + WASHER_T + NUT_T + 0.5)
            stud_len = abs(top - bottom)
            stud_y = 0.5 * (top + bottom)
            for u in (-CLAMP_U, CLAMP_U):
                for dz in (-CLAMP_Z, CLAMP_Z):
                    z = n + dz
                    piece = K.cyl_y(STUD_R, stud_len, (u, stud_y, z))
                    piece = piece.fuse(K.cyl_y(STUD_HEAD_R, STUD_HEAD_T, (u, head_y, z)))
                    piece = piece.fuse(K.cyl_y(WASHER_R, WASHER_T, (u, wash_y, z)))
                    nut = (cq.Workplane("XY").polygon(6, 2.0 * NUT_R).extrude(NUT_T)
                           .rotate((0, 0, 0), (1, 0, 0), -90.0)
                           .translate((u, nut_y - NUT_T / 2.0, z)))
                    piece = piece.fuse(nut.val())
                    out["carriage_clamp_stud_%s_%+d_%+.0f_%+.0f" % (label, side, u, dz)] = \
                        K.to_world(piece)
                    out["carriage_clamp_spring_%s_%+d_%+.0f_%+.0f" % (label, side, u, dz)] = \
                        K.to_world(_spring(y + side * ear_outer, side, u, z))
    return out


def build(name, half):
    R52.r52_plate = r53_plate
    K.bearing_carriage = r53_carriage
    parts, kin, feeder, dropped, extra = R52.build(name, half)
    rails = sorted(n for n in parts if n.startswith("carriage_guide_"))
    for n in rails:
        parts.pop(n)
    clamps = clamp_parts(half)
    parts.update(clamps)
    return parts, kin, feeder, dropped, rails, sorted(clamps)


def clamp_calc():
    """What does the spring buy, and can the existing 25-2 servo still slide it?"""
    n_stud = 4 * 2                     # u x dz per carriage per side plate
    faces = 2.0                        # each stud loads two ear/plate faces
    out = {"studs_per_carriage": n_stud, "preload_n_per_stud": PRELOAD_N,
           "spring_rate_n_per_mm": SPRING_RATE,
           "spring_installed_mm": SPRING_INSTALLED, "spring_free_mm": SPRING_FREE}
    for mu in (0.30, 0.60):
        f_car = mu * faces * n_stud * PRELOAD_N
        out["mu_%.2f" % mu] = {
            "friction_per_carriage_n": round(f_car, 1),
            "friction_total_n": round(2.0 * f_car, 1),
            "servo_can_still_slide_it": bool(2.0 * f_car < 0.6 * 112.0),
        }
    out["note"] = ("CALCULATED. mu=0.30 = PET-on-PET as printed; mu=0.60 = if a "
                   "1 mm elastic high-friction pad is taped onto the ear faces "
                   "(NOT modelled). Servo push budget ~112 N, see the R53b sheet: "
                   "the clamp must stay well under it or the servo cannot change "
                   "the gap any more.")
    return out


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
    parts, kin, feeder, dropped, rails, clamps = build(name, half)
    print("[r53b %s] %d parts (dropped %d from R51 base, %d free rails removed, "
          "%d clamp parts added)" % (name, len(parts), len(dropped), len(rails),
                                     len(clamps)), flush=True)

    plates = sorted(n for n in parts if n.startswith("shooter_side_plate_"))
    carrs = sorted(n for n in parts if n.startswith("bearing_carriage_"))
    lock_rest = screen(parts, clamps, sorted(set(parts) - set(clamps) - set(carrs)))
    lock_carr = screen(parts, clamps, carrs)
    plate_rest = screen(parts, plates, sorted(set(parts) - set(plates) - set(clamps)))
    axles = R52.axle_isolation(parts)
    clear = window_clearance(parts, half)
    geom = R52.geometry(parts, R52._paddle_xz, feeder)

    meta = {
        "units": "mm",
        "caliber": "T06 R53b = R52 + guided window + always-on elastic clamp",
        "variant": name,
        "half_spacing_mm": half,
        "nip_mm": round(2.0 * half - K.WHEEL_OD, 3),
        "changes_vs_r52": [
            "deleted %d free carriage guide rails" % len(rails),
            "carriage ears x 23 -> +-42, %g mm thick, %g mm running clearance"
            % (EAR_T, EAR_GAP),
            "side plate lock slots %g x %g at x = +-36" % (SLOT_W, SLOT_Z1 - SLOT_Z0),
            "%d M4 stud + washer + nyloc nut + preload spring clamp parts"
            % len(clamps),
            "wing nut deleted: clamping is by spring, set once at build time",
        ],
        "removed_rails": rails,
        "clamp_parts": clamps,
        "clamp_calc": clamp_calc(),
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
    (OUT / ("report_r53b_%s.json" % name)).write_text(
        json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")

    print("[r53b %s] clamp slot travel: %s" % (name, json.dumps(meta["lock_travel"])), flush=True)
    print("[r53b %s] ear-plate min gap: %s" % (name, json.dumps(clear)), flush=True)
    print("[r53b %s] axle-isolation hits (must be []): %s"
          % (name, json.dumps(axles, ensure_ascii=False)), flush=True)
    print("[r53b %s] clamp vs everything else: %d" % (name, len(lock_rest)), flush=True)
    for h in lock_rest:
        print("   !", json.dumps(h, ensure_ascii=False), flush=True)
    print("[r53b %s] clamp vs carriage (ears only expected): %d"
          % (name, len(lock_carr)), flush=True)
    for h in lock_carr:
        print("   ~", json.dumps(h, ensure_ascii=False), flush=True)
    print("[r53b %s] plate vs rest: %d" % (name, len(plate_rest)), flush=True)
    for h in plate_rest:
        print("   *", json.dumps(h, ensure_ascii=False), flush=True)

    if export:
        stem = "T06_shooter_assembly_R53b_%s" % name
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
        print("[r53b %s] STEP -> %.1f MB" % (name, meta["step_mb"]), flush=True)
        (OUT / ("report_r53_%s.json" % name)).write_text(
            json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")

    print("[r53b %s] done in %.1f s" % (name, time.time() - t0), flush=True)
    return meta


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    names = [a for a in argv if not a.startswith("-")] or ["pollen"]
    for n in names:
        run(n, export="--step" in argv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
