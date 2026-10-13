# -*- coding: utf-8 -*-
"""T06 R50 -- R37 staging + R49 gate (both read-only) + launcher drive & frame.

User instruction (2026-10-13):
  "give the flywheels their motors, give the paddle its servo -- both SKUs are
   already fixed, look them up -- and give the whole shooter a support
   structure.  Do not lose focus; be reasonably careful; use the shortest
   workable route."

Nothing is overwritten: R37/R47/R49 keep their own files and are imported
read-only.

Fixed SKUs (KNOWN -- config/t06_launcher_cots.json)
--------------------------------------------------
  flywheel motor  x2   5203-2402-0003   goBILDA 3.7:1 1620 rpm, 8 mm REX out
  motor clamp     x2   1401-0043-0036   axial envelope 8.0 (MEASURED)
  shaft coupler   x2   4007-4008-4008   8 mm REX -> 8 mm REX
  paddle servo    x1   2000-0025-0004   goBILDA 25-4 Super Speed
        = config/parameters.yaml index_drive_servo, fixed by the user in
        DEC-0026 and used for the feeder in DEC-0043.  Its supplier STEP was
        missing from the repo and was downloaded on 2026-10-13 -- see
        references/vendor/gobilda/t06/manifest.json.
  servo frame     x1   1802-0043-0001
  servo coupler   x1   4001-0025-4008   25T spline -> 8 mm REX
  shaft bearing   x6   1611-0514-4008   (4 -> 6: the R50 frame also seats the
        paddle shaft in bearings, so the COTS quantity grows by two)

Axle positions are measured off the final R37 solids, never typed in:
  A upper flywheel   (-11.368, 285.260)
  B lower flywheel   (115.975, 185.769)
  C paddle           (F.PADDLE_CX, F.PADDLE_CZ) = (29.490, 111.460)

Y stacking -- the R37 machine lives inside |y| <= 57 (shell / guides) and the
rotor inside |y| <= 48, so the frame sits outside it and only the shafts cross:

  motor body        -219.17 .. -112.00    output-shaft tip at -88.0
  motor clamp       -120.00 .. -112.00    catalogue clamp on the body
  motor bridges     -112.00 ..  -68.00    printed, bolt the clamp to the plate
  shaft coupler      -96.50 ..  -75.50    flywheel shaft 8.5 mm + motor 8.5 mm
  flywheel shaft     -84.00 ..   84.00    kept R37 part
  frame plate -Y     -71.00 ..  -65.00    printed, 6 mm
  paddle shaft       -96.00 ..   96.00    kept R37 part
  paddle bridge       73.00 ..   79.00    kept R37 part (superseded by the R50
                                          +Y plate, kept as an extra web)
  frame plate +Y      79.00 ..   85.00    flush with that bridge
  servo coupler       88.00 ..  105.00    REX bore 88.0..96.0, 25T pocket
                                          102.1..105.0, 0.6 mm to the case face
  servo frame         96.00 ..  102.00
  servo case         101.50 ..  145.60    spline face at 101.5 pointing -Y

The two plates are drawn as a boss/bar/leg outline rather than a slab: every
outline piece is inside |y| >= 65, where nothing else lives, so the only bores
that matter are the three axle bores (O14.1 for the 1611-0514-4008 bearing).

Usage: python cad/paddle_launcher_shooter_drive_r50.py [pollen] [--step] [--no-view]
Output: cad/output/_r50_drive/
"""
from __future__ import annotations

import json
import math
import os
import pickle
import sys
import time
from pathlib import Path

import cadquery as cq

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import paddle_launcher_feeder_a_prime_shared as SH          # noqa: E402
import paddle_launcher_feeder_a_prime_shared_staging as ST  # noqa: E402
import paddle_launcher_gate_drive_r49 as G49                # noqa: E402
import t06_vendor_cad as TC                                 # noqa: E402

F, pl = SH.F, SH.pl

MOTOR_SKU = "5203-2402-0003"
CLAMP_SKU = "1401-0043-0036"
COUPLER_SKU = "4007-4008-4008"
SERVO_SKU = "2000-0025-0004"
SERVO_FRAME_SKU = "1802-0043-0001"
SERVO_COUPLER_SKU = "4001-0025-4008"
BEARING_SKU = "1611-0514-4008"

MOTOR_OUTPUT_TIP_Y = -88.0          # accepted R35/R37 drive stack
CLAMP_Y = -116.0
COUPLER_Y = -86.0                   # web centred on the -88..-84 shaft gap
SERVO_FACE_Y = 101.5                # accepted R35/R37 drive stack
SERVO_FRAME_Y = 99.0
SERVO_COUPLER_Y = 96.5              # spline pocket full depth, case 0.6 clear

PLATE_Y = {-1: (-71.0, -65.0), 1: (79.0, 85.0)}
BEARING_Y = {-1: -68.0, 1: 82.0}
RAIL_Y0, RAIL_Y1 = -71.0, 85.0

BOSS_R, BAR_W, PLATE_T = 34.0, 44.0, 6.0
BORE_R = 7.05                       # O14.1 pocket for the 1611 bearing

PLATE_RECTS = (                     # x0, x1, z0, z1 -- must hold the rails
    (40.0, 92.0, -18.0, 95.0),      # front leg / foot
    (10.0, 92.0, 300.0, 332.0),     # top arm
    (96.0, 132.0, 104.0, 200.0),    # rear arm (carries boss B)
)
RAILS = (                           # x0, x1, z0, z1 -- clear of the machine
    (38.0, 92.0, 314.0, 332.0),
    (96.0, 132.0, 104.0, 128.0),
    (40.0, 92.0, -18.0, -5.0),
)
FOOT_HOLES = ((52.0, -50.0), (80.0, -50.0), (52.0, 50.0), (80.0, 50.0))
MOTOR_BRIDGE_U = (-17.0, 17.0)
SERVO_BRIDGE_U = (-28.0, 28.0)

DESKTOP = Path(os.path.expanduser("~")) / "OneDrive" / "Desktop"
OUT = HERE / "output" / "_r50_drive"
OUT.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------------ basics --
def _box(dx, dy, dz, c):
    return cq.Solid.makeBox(dx, dy, dz,
                            cq.Vector(-dx / 2.0, -dy / 2.0, -dz / 2.0)).translate(
        cq.Vector(*c))


def _cyl_y(r, y0, y1, x, z):
    return cq.Solid.makeCylinder(r, y1 - y0, cq.Vector(x, y0, z),
                                 cq.Vector(0.0, 1.0, 0.0))


def _bar(p0, p1, w, y0, y1):
    """Flat bar in the XZ plane, centre line p0 -> p1, w wide, y0..y1 thick."""
    dx, dz = p1[0] - p0[0], p1[1] - p0[1]
    length = math.hypot(dx, dz)
    ang = math.degrees(math.atan2(dz, dx))
    bar = cq.Solid.makeBox(length, y1 - y0, w,
                           cq.Vector(-0.5 * length, -0.5 * (y1 - y0), -0.5 * w))
    bar = bar.rotate(cq.Vector(0.0, 0.0, 0.0), cq.Vector(0.0, 1.0, 0.0), -ang)
    return bar.translate(cq.Vector(0.5 * (p0[0] + p1[0]), 0.5 * (y0 + y1),
                                   0.5 * (p0[1] + p1[1])))


def _fuse(shapes):
    out = shapes[0]
    for s in shapes[1:]:
        out = out.fuse(s)
    return out.clean()


def _xz_centre(shapes):
    bbs = [s.BoundingBox() for s in shapes]
    x0 = min(b.xmin for b in bbs)
    x1 = max(b.xmax for b in bbs)
    z0 = min(b.zmin for b in bbs)
    z1 = max(b.zmax for b in bbs)
    return (0.5 * (x0 + x1), 0.5 * (z0 + z1))


def _pick(kept, prefix):
    """All kept parts whose name starts with ``prefix`` (ordering by name)."""
    out = [kept[k] for k in sorted(kept) if k.startswith(prefix)]
    if not out:
        raise KeyError("no kept part starts with %r (have %s)"
                       % (prefix, sorted(kept)))
    return out


def axle_centres(kept):
    """Measure the three axle centres off the final R37 solids."""
    up = _xz_centre(_pick(kept, "gecko_flywheel_upper_"))
    lo = _xz_centre(_pick(kept, "gecko_flywheel_lower_"))
    return {"upper": up, "lower": lo, "paddle": (F.PADDLE_CX, F.PADDLE_CZ)}


# ------------------------------------------------------------- the frame ----
def frame_plate(side, ax):
    y0, y1 = PLATE_Y[side]
    pieces = [_cyl_y(BOSS_R, y0, y1, ax[k][0], ax[k][1])
              for k in ("upper", "lower", "paddle")]
    pieces += [_bar(ax["upper"], ax["lower"], BAR_W, y0, y1),
               _bar(ax["upper"], ax["paddle"], BAR_W, y0, y1),
               _bar(ax["lower"], ax["paddle"], BAR_W, y0, y1)]
    pieces += [_box(x1 - x0, y1 - y0, z1 - z0,
                    (0.5 * (x0 + x1), 0.5 * (y0 + y1), 0.5 * (z0 + z1)))
               for (x0, x1, z0, z1) in PLATE_RECTS]
    plate = _fuse(pieces)
    for k in ("upper", "lower", "paddle"):
        plate = plate.cut(_cyl_y(BORE_R, y0 - 2.0, y1 + 2.0, ax[k][0], ax[k][1]))
    return plate


def cross_rail(x0, x1, z0, z1):
    rail = _box(x1 - x0, RAIL_Y1 - RAIL_Y0, z1 - z0,
                (0.5 * (x0 + x1), 0.5 * (RAIL_Y0 + RAIL_Y1), 0.5 * (z0 + z1)))
    if z1 < 0.0:                    # the bottom rail is the chassis interface
        for (hx, hy) in FOOT_HOLES:
            rail = rail.cut(cq.Solid.makeCylinder(
                2.3, z1 - z0 + 4.0, cq.Vector(hx, hy, z0 - 2.0),
                cq.Vector(0.0, 0.0, 1.0)))
    return rail


def motor_drive(axle, label, parts):
    """One motor: case, clamp, coupler, bracket bridges."""
    parts["flywheel_motor_%s_%s" % (label, MOTOR_SKU)] = \
        TC.motor_with_output_tip(axle, MOTOR_OUTPUT_TIP_Y)
    parts["motor_clamp_%s_%s" % (label, CLAMP_SKU)] = \
        TC.centered_y_axis_part(CLAMP_SKU, (axle[0], CLAMP_Y, axle[1]))
    parts["motor_coupler_%s_%s" % (label, COUPLER_SKU)] = \
        TC.centered_y_axis_part(COUPLER_SKU, (axle[0], COUPLER_Y, axle[1]))
    for u in MOTOR_BRIDGE_U:
        parts["motor_bridge_%s_%+d" % (label, int(u))] = _box(
            8.0, 44.0, 26.0, (axle[0] + u, -90.0, axle[1]))    # -112 .. -68
    for side in (-1, 1):
        parts["flywheel_bearing_%s_%+d_%s" % (label, side, BEARING_SKU)] = \
            TC.centered_y_axis_part(BEARING_SKU,
                                    (axle[0], BEARING_Y[side], axle[1]))


def paddle_drive(ax, parts):
    c = ax["paddle"]
    parts["paddle_servo_%s" % SERVO_SKU] = TC.servo_with_output_face(
        SERVO_SKU, c, SERVO_FACE_Y, -1)
    parts["paddle_servo_frame_%s" % SERVO_FRAME_SKU] = TC.centered_y_axis_part(
        SERVO_FRAME_SKU, (c[0], SERVO_FRAME_Y, c[1]), largest_solid_only=True)
    # 4001-0025-4008 carries its 25T spline pocket on the -Y end and the 8 mm REX
    # bore on the +Y end (measured on the official STEP: pocket 2.9 deep at
    # local -8.5..-5.6, 8 mm bore 8.0 deep at local +0.5..+8.5).  The servo
    # drives toward -Y and the paddle shaft arrives from -Y, so the purchased
    # part is fitted end for end.  It is turned 180 deg about a diameter
    # through its own placement centre, which puts the spline pocket on +Y
    # (102.1..105.0, over the 101.5..105.6 spline) and the REX bore on -Y
    # (88.0..96.0, over the 96.0 shaft end).  Shape.mirror("XZ") must NOT be
    # used here: it mirrors about the world XZ plane and would relocate the
    # part to -96.5 instead of flipping it in place.
    # The turn is done at the origin: cadquery's Shape.rotate treats its two
    # vectors as a point and a *direction*, so passing the placement centre as
    # the start and (1, 0, 0) as the end would spin the part about a nearly-Y
    # axis instead of about its own X diameter.
    _servo_coupler = TC.centered_y_axis_part(SERVO_COUPLER_SKU,
                                             (c[0], SERVO_COUPLER_Y, c[1]))
    _servo_coupler = _servo_coupler.translate(
        cq.Vector(-c[0], -SERVO_COUPLER_Y, -c[1]))
    _servo_coupler = _servo_coupler.rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0),
                                           180.0)
    parts["paddle_servo_coupler_%s" % SERVO_COUPLER_SKU] = \
        _servo_coupler.translate(cq.Vector(c[0], SERVO_COUPLER_Y, c[1]))
    for u in SERVO_BRIDGE_U:
        parts["servo_bridge_%+d" % int(u)] = _box(
            8.0, 21.0, 26.0, (c[0] + u, 89.5, c[1]))           # 79 .. 100
    for side in (-1, 1):
        parts["paddle_bearing_%+d_%s" % (side, BEARING_SKU)] = \
            TC.centered_y_axis_part(BEARING_SKU, (c[0], BEARING_Y[side], c[1]))


def drive_parts(kept):
    ax = axle_centres(kept)
    parts = {"shooter_frame_neg": frame_plate(-1, ax),
             "shooter_frame_pos": frame_plate(1, ax)}
    for i, (x0, x1, z0, z1) in enumerate(RAILS, 1):
        parts["shooter_rail_%d" % i] = cross_rail(x0, x1, z0, z1)
    motor_drive(ax["upper"], "upper", parts)
    motor_drive(ax["lower"], "lower", parts)
    paddle_drive(ax, parts)
    return parts, ax


# --------------------------------------------------------------- assembly ---
_kept_cache = {}


def kept_parts(name):
    """R37 kept parts, in-process cache only.

    Pickling OCC shapes is not safe here: the BRep binary stream does not
    round-trip (BRep_PointRepresentation comes back mis-aligned), so a
    pickled cache reads back as garbage.  The staging module has its own
    disk cache and re-runs in ~50 s, which is good enough.
    """
    if name in _kept_cache:
        return _kept_cache[name]
    t0 = time.time()
    kept, *_ = ST.build_variant_stage(name)
    _kept_cache[name] = kept
    print("[r50 %s] R37 staging %.1f s, %d parts"
          % (name, time.time() - t0, len(kept)), flush=True)
    return _kept_cache[name]


KEPT_NAMES = ("feeder_shell_tray", "guide_wall_3_-1", "guide_wall_3_+1",
              "guide_roof_3", "shooter_throat_+55", "paddle_rotor",
              "paddle_flex_tip_1", "paddle_flex_tip_2",
              "paddle_shaft_2106-4008-1920", "paddle_shaft_support_bridge")


_parts_cache = {}


def all_parts_cached(name):
    """In-process wrapper -- OCC shapes do not survive a pickle round trip."""
    if name not in _parts_cache:
        _parts_cache[name] = all_parts(name)
    return _parts_cache[name]


def all_parts(name):
    kept = dict(kept_parts(name))
    gate = dict(G49.drive_parts(G49.PHI_DN, 0))
    frame, ax = drive_parts(kept)
    parts = {}
    parts.update(kept)
    parts.update(gate)
    parts.update(frame)
    return parts, ax, kept


def dump(parts):
    rows = []
    for n, s in parts.items():
        bb = s.BoundingBox()
        rows.append({
            "part": n,
            "n_solids": len(s.Solids()),
            "volume_mm3": round(s.Volume(), 2),
            "bbox_mm": [round(v, 3) for v in (bb.xmin, bb.ymin, bb.zmin,
                                              bb.xmax, bb.ymax, bb.zmax)],
        })
    return rows


def clashes(parts, names_a, names_b):
    """Volume intersection between two part groups, bbox filtered."""
    hits = []
    bs = {n: parts[n].BoundingBox() for n in names_a + names_b}
    for a in names_a:
        ba = bs[a]
        for b in names_b:
            if a == b:
                continue
            bb = bs[b]
            if (ba.xmax <= bb.xmin or bb.xmax <= ba.xmin
                    or ba.ymax <= bb.ymin or bb.ymax <= ba.ymin
                    or ba.zmax <= bb.zmin or bb.zmax <= ba.zmin):
                continue
            try:
                vol = parts[a].intersect(parts[b]).Volume()
            except Exception as exc:                       # pragma: no cover
                hits.append({"a": a, "b": b, "error": str(exc)[:80]})
                continue
            if vol > 0.5:
                hits.append({"a": a, "b": b, "volume_mm3": round(vol, 3)})
    return hits


def pair_overlap(parts, name_a, name_b):
    """Volume intersection of two named parts -- used inside the new group,
    which ``clashes`` (new versus existing) cannot see."""
    try:
        vol = parts[name_a].intersect(parts[name_b]).Volume()
    except Exception as exc:                                   # pragma: no cover
        return {"a": name_a, "b": name_b, "error": str(exc)[:80]}
    return {"a": name_a, "b": name_b, "volume_mm3": round(vol, 3)}


def drive_stack_overlaps(parts):
    """Every purchased part of the drive stack against its neighbours."""
    out = []
    for lbl in ("upper", "lower"):
        out.append(pair_overlap(parts, "flywheel_motor_%s_%s" % (lbl, MOTOR_SKU),
                                "motor_coupler_%s_%s" % (lbl, COUPLER_SKU)))
    out.append(pair_overlap(parts, "paddle_servo_%s" % SERVO_SKU,
                            "paddle_servo_coupler_%s" % SERVO_COUPLER_SKU))
    out.append(pair_overlap(parts, "paddle_servo_frame_%s" % SERVO_FRAME_SKU,
                            "paddle_servo_coupler_%s" % SERVO_COUPLER_SKU))
    out.append(pair_overlap(parts, "paddle_servo_coupler_%s" % SERVO_COUPLER_SKU,
                            "paddle_shaft_2106-4008-1920"))
    for u in SERVO_BRIDGE_U:
        out.append(pair_overlap(parts, "paddle_servo_coupler_%s" % SERVO_COUPLER_SKU,
                                "servo_bridge_%+d" % int(u)))
    for side in (-1, 1):
        out.append(pair_overlap(parts, "paddle_servo_coupler_%s" % SERVO_COUPLER_SKU,
                                "shooter_frame_%s" % ("pos" if side > 0 else "neg")))
    return out


def run(name="pollen", export=False, view=True):
    t0 = time.time()
    parts, ax, kept = all_parts_cached(name)
    frame_names = [n for n in parts if n.startswith(("shooter_frame",
                                                     "shooter_rail",
                                                     "motor_bridge",
                                                     "servo_bridge"))]
    cots_names = [n for n in parts if any(k in n for k in
                                          (MOTOR_SKU, CLAMP_SKU, COUPLER_SKU,
                                           SERVO_SKU, SERVO_FRAME_SKU,
                                           SERVO_COUPLER_SKU, BEARING_SKU))]
    new_names = frame_names + cots_names
    old_names = [n for n in parts if n not in new_names]
    rows = dump(parts)
    hits = clashes(parts, new_names, old_names)
    stack = drive_stack_overlaps(parts)

    n_motor = len([n for n in parts if n.startswith("flywheel_motor_")])
    n_bearing = len([n for n in parts if "bearing" in n])
    meta = {
        "variant": name,
        "units": "mm",
        "caliber": "T06 R50 shooter drive + support frame",
        "axles_xz_mm": {k: [round(v, 3) for v in ax[k]] for k in ax},
        "plate_y_mm": {"-1": list(PLATE_Y[-1]), "+1": list(PLATE_Y[1])},
        "plate_thickness_mm": PLATE_T,
        "rail_y_mm": [RAIL_Y0, RAIL_Y1],
        "rails_xz_mm": [list(r) for r in RAILS],
        "foot_holes_mm": [list(h) for h in FOOT_HOLES],
        "motor_sku": MOTOR_SKU,
        "motor_count": n_motor,
        "motor_output_tip_y_mm": MOTOR_OUTPUT_TIP_Y,
        "clamp_sku": CLAMP_SKU,
        "clamp_y_mm": CLAMP_Y,
        "coupler_sku": COUPLER_SKU,
        "coupler_y_mm": COUPLER_Y,
        "servo_sku": SERVO_SKU,
        "servo_face_y_mm": SERVO_FACE_Y,
        "servo_frame_sku": SERVO_FRAME_SKU,
        "servo_coupler_sku": SERVO_COUPLER_SKU,
        "servo_coupler_y_mm": SERVO_COUPLER_Y,
        "bearing_sku": BEARING_SKU,
        "bearing_count": n_bearing,
        "bearing_y_mm": {str(k): v for k, v in BEARING_Y.items()},
        "gate_included": True,
        "clashes_new_vs_old": hits,
        "drive_stack_overlaps": stack,
        "build_s": round(time.time() - t0, 1),
        "parts": rows,
    }
    (OUT / ("parts_%s.json" % name)).write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    if view:
        import paddle_launcher_shooter_drive_r50_view as V
        meta["view_png"] = V.render_doc(name, parts, OUT)

    if export:
        stem = "T06_shooter_drive_R50_%s" % name
        assy = cq.Assembly(name=stem)
        for n, s in parts.items():
            assy.add(s, name=n, color=cq.Color(0.7, 0.72, 0.76, 1.0))
        dst = DESKTOP / (stem + ".step")
        assy.export(str(dst), exportType="STEP")
        assy.export(str(OUT / (stem + ".step")), exportType="STEP")
        meta["delivered_step"] = str(dst)
        print("[r50 %s] export -> %s" % (name, dst), flush=True)

    for r in rows:
        print("  %-46s solids=%d vol=%9.1f y %.1f..%.1f"
              % (r["part"], r["n_solids"], r["volume_mm3"],
                 r["bbox_mm"][1], r["bbox_mm"][4]), flush=True)
    print("[r50] new-vs-existing clashes: %d" % len(hits), flush=True)
    for h in hits:
        print("   !", h, flush=True)
    print("[r50] drive-stack overlaps:", flush=True)
    for s in meta["drive_stack_overlaps"]:
        print("   ~", s, flush=True)
    print("[r50 %s] done in %.1f s" % (name, time.time() - t0), flush=True)
    return meta


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    names = [a for a in argv if not a.startswith("-")] or ["pollen"]
    for n in names:
        run(n, export="--step" in argv, view="--no-view" not in argv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
