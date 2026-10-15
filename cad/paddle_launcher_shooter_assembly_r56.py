# -*- coding: utf-8 -*-
"""T06 R56 -- R55 assembly-friendly frame with the intake tray lengthened.

Targets, straight from the 2026-10-14 brief:
  1. fewest possible printed parts -> feeder_shell_tray (shroud+tray) and both
     shooter_side_plate members are fused into ONE frame solid, tied together by
     printed gussets in the 54..68 mm y gap;
  2. real M3 joints -> plain O3.4 through-hole in BOTH members, bolt head one
     side, nut the other.  No self-tapping, no heat-set inserts, no nut pockets;
  3. 3D-print friendly -> everything stays in the printed frame's own planes;
  4. vendor-supplied COTS bodies are excluded from this version;
  5. the R49 gate solid is NOT modelled, its mounting holes are reserved;
  6. durability / fatigue is explicitly out of scope (prototype).

Run:
  .venv-cad/Scripts/python.exe -X utf8 cad/paddle_launcher_shooter_assembly_r55.py pollen --step
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
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import paddle_launcher_constrained as K                      # noqa: E402
import paddle_launcher_shooter_drive_r51 as R51               # noqa: E402
import paddle_launcher_shooter_lock_r53b as B                 # noqa: E402
import paddle_launcher_shooter_lock_r53f as F                 # noqa: E402   (patches B)

OUT = HERE / "output" / "_r56_frame"
OUT.mkdir(parents=True, exist_ok=True)
SECT = OUT / "sections"
SECT.mkdir(parents=True, exist_ok=True)

HALF = {"pollen": 80.0, "nectar": 91.0}

# --- R56: lengthen the intake tray (single-parameter change) ---------------
# Per the 2026-10-14 brief the tray is made longer so more balls queue behind
# the paddle; everything else is R55.  Capacity (cad/_r56_tray_pick.py):
#   TRAY_X1 = 215 -> pollen 3 / nectar 2      (R55)
#   TRAY_X1 = 285 -> pollen 4 / nectar 3      (R56, chosen)
STAGE_X1_R56 = 285.0
import paddle_launcher_feeder_a_prime_shared as SH             # noqa: E402
import paddle_launcher_feeder_a_prime_shared_staging as ST     # noqa: E402
ST.STAGE_X1 = STAGE_X1_R56
SH.F.TRAY_X1 = STAGE_X1_R56


# --- M3 bolted joints -------------------------------------------------------
M3_CLR_R = 1.70            # O3.4 clearance, drilled right through both members
M3_HEAD_R = 5.6            # head/ washer seat radius, cosmetic only
DRILLABLE = ("base_rail_+72", "base_rail_-72")   # joint bolts pierce these too
# (x, tab top z).  MEASURED side-plate lower edge: x=60 -> z 38, x=76 -> z 42
RAIL_TABS = ((60.0, 44.0), (76.0, 48.0))
# DEC-0055 fix A (MEASURED): the y = +-70 axis sat exactly on the side plate's
# (y 68..72) V lower edge, so the hole was blind.  Move the axis outboard to
# y = +-76 and widen the tab in y so the O3.4 hole keeps >2 mm walls.
BOLT_Y = 76.0              # rail-joint bolt axis, |y| (was 70.0)
TAB_WY = 16.0              # rail-tab width in y  ->  y 68..84
DRILL_LEN = 60.0           # z 26 +- 30 = -4..56: through tab + rail, exits free
DRILL_ZC = 26.0
GUSSET_T = 6.0             # printed rib thickness in x
F_VERBOSE = True           # print why each candidate rib was rejected

# --- what gets excluded from this version ----------------------------------
VENDOR_SKU = ("3613-0014-0096", "1309-0016-4008", "2106-4008-1680",
              "2106-4008-1920", "4007-4008-4008", "1401-0043-0036",
              "5203-2402-0003", "2000-0025-0002", "2000-0025-0004",
              "1802-0043-0001", "4001-0025-4008", "1908-0025-0032",
              "1611-0514-4008")
GATE_PREFIX = "gate_"

# --- what gets fused into the single printed frame --------------------------
MERGE = ("feeder_shell_tray",
         "shooter_side_plate_+1", "shooter_side_plate_-1",
         "feeder_mount_+1", "feeder_mount_-1",
         "guide_roof_3", "guide_wall_3_+1", "guide_wall_3_-1",
         "shooter_throat_+55",
         "paddle_shaft_support_bridge",
         "servo_bridge_+26", "servo_bridge_-26")

# --- tie pads: close the measured 1 mm gap plate(y68-72) -> bracket(y73-99) ---
TIE_PADS = ((8.0, 11.0, 20.0, (54.5, 76.5, 111.0)),
            (8.0, 11.0, 20.0, (4.5, 76.5, 111.0)))

FRAME_NAME = "shooter_frame_R56_merged"


# ----------------------------------------------------------------- helpers --
def bbox(shape):
    bb = shape.BoundingBox()
    return {"x": [round(bb.xmin, 2), round(bb.xmax, 2)],
            "y": [round(bb.ymin, 2), round(bb.ymax, 2)],
            "z": [round(bb.zmin, 2), round(bb.zmax, 2)]}


def is_vendor(name):
    return any(name.endswith("_" + sku) for sku in VENDOR_SKU) or \
        name.startswith(("gap_servo_", "paddle_servo_"))


CACHE = OUT / "cache"
CACHE.mkdir(parents=True, exist_ok=True)


def build_parts(name, fresh=False):
    """R53f chain, pollen/nectar.  F.CAPTURED holds every final solid.

    The chain takes ~165 s, so every solid is mirrored to BREP on first build and
    read back afterwards; delete cad/output/_r55_frame/cache to rebuild.
    """
    mark = CACHE / ("%s.done" % name)
    if mark.exists() and not fresh:
        parts = {}
        for f in sorted(CACHE.glob("%s__*.brep" % name)):
            parts[f.name[len(name) + 2:-5].replace("~", "/")] = \
                cq.Shape.importBrep(str(f))
        print("[r55 %s] cache hit, %d parts" % (name, len(parts)), flush=True)
        return parts
    t0 = time.time()
    B.build(name, HALF[name])
    parts = dict(F.CAPTURED["parts"])
    for n, sh in parts.items():
        sh.exportBrep(str(CACHE / ("%s__%s.brep" % (name, n.replace("/", "~")))))
    mark.write_text("ok", encoding="utf-8")
    print("[r55 %s] R53f chain %.1f s, %d parts" % (name, time.time() - t0, len(parts)),
          flush=True)
    return parts


def split_parts(parts):
    """(structural keep, vendor, gate) -- the wire the user asked for."""
    gate = {n: s for n, s in parts.items() if n.startswith(GATE_PREFIX)}
    vendor = {n: s for n, s in parts.items()
              if n not in gate and is_vendor(n)}
    keep = {n: s for n, s in parts.items()
            if n not in gate and n not in vendor}
    return keep, vendor, gate


def merge_members(keep):
    """Everything the brief wants as ONE printed part, plus the tie gussets."""
    members = {n: keep[n] for n in MERGE if n in keep}
    missing = [n for n in MERGE if n not in keep]
    if missing:
        print("[r55] merge members absent from the build: %s" % missing, flush=True)
    return members


def cyl(axis, r, length, center):
    if axis == "y":
        return K.cyl_y(r, length, center)
    if axis == "z":
        return K.cyl_z(r, length, center)
    return K.box(length, 2 * r, 2 * r, center)


def prebbox(parts):
    return {n: s.BoundingBox() for n, s in parts.items()}


def clash(shape, others, bbs, floor=0.5):
    """(name, mm3) for every part sharing more than `floor` mm3 with `shape`."""
    out = []
    b2 = shape.BoundingBox()
    for n, s in others.items():
        bb = bbs[n]
        if (b2.xmax <= bb.xmin or bb.xmax <= b2.xmin
                or b2.ymax <= bb.ymin or bb.ymax <= b2.ymin
                or b2.zmax <= bb.zmin or bb.zmax <= b2.zmin):
            continue
        try:
            v = shape.intersect(s).Volume()
        except Exception:
            continue
        if v > floor:
            out.append((n, round(v, 2)))
    return out


def find_gussets(members, others, bbs):
    """Ribs in the 54..68 mm y gap that really bite BOTH the tray and the plates.

    Measured fact: feeder_shell_tray is a thin XZ chute profile extruded across
    |y| <= 54, so a rib has to land ON the wall, not merely inside the bbox.
    Each candidate is therefore probed as a small 2 mm Y-slab on the wall
    (y = 52) and on the plate inner face (y = 70) before any boolean is spent.
    """
    tray = members["feeder_shell_tray"]
    plates = [members["shooter_side_plate_%+d" % x] for x in (-1, 1)]
    on_tray, found = [], []
    for x in range(-84, 216, 6):
        for z in range(6, 200, 6):
            c = K.box(2.0, 2.0, 2.0, (float(x), 52.0, float(z)))
            if c.intersect(tray).Volume() < 0.5:
                continue
            on_tray.append((x, z))
            g = K.box(10.0, 20.0, 16.0, (float(x), 60.0, float(z)))
            bite = [g.intersect(plates[1]).Volume()]
            g = K.box(10.0, 20.0, 16.0, (float(x), -60.0, float(z)))
            bite.append(g.intersect(plates[0]).Volume())
            g = K.box(10.0, 20.0, 16.0, (float(x), 60.0, float(z)))
            tvol = g.intersect(tray).Volume()
            if min(bite) < 20.0:
                if F_VERBOSE:
                    print("[r55] cand x=%-5d z=%-5d tray=%.2f plates=%s (plate bite too small)"
                          % (x, z, tvol, [round(v, 1) for v in bite]), flush=True)
                continue
            hits = clash(g, others, bbs)
            if F_VERBOSE and hits:
                print("[r55] cand x=%-5d z=%-5d tray=%.2f plates=%s hits=%s"
                      % (x, z, tvol, [round(v, 1) for v in bite], [h[0] for h in hits][:3]),
                      flush=True)
            if hits:
                continue
            found.append({"x": float(x), "z": float(z),
                          "tray_mm3": round(g.intersect(tray).Volume(), 2),
                          "plate_mm3": [round(v, 2) for v in bite]})
    print("[r55] %d wall samples, %d usable rib slots" % (len(on_tray), len(found)),
          flush=True)
    if on_tray:
        xs = [p[0] for p in on_tray]
        zs = [p[1] for p in on_tray]
        print("[r55] wall footprint x[%d,%d] z[%d,%d]" % (min(xs), max(xs), min(zs), max(zs)),
              flush=True)
    return found


def make_gussets(found):
    out = {}
    for i, f in enumerate(found):
        for side in (-1, 1):
            out["frame_gusset_%d_%+d" % (i, side)] = K.box(
                10.0, 20.0, 16.0, (f["x"], side * 60.0, f["z"]))
    return out


def make_tie_pads(others, bbs):
    """Two pads that fuse plate + shaft-support bridge + servo bridge in one go."""
    out = {}
    for i, (sx, sy, sz, c) in enumerate(TIE_PADS):
        b = K.box(sx, sy, sz, c)
        hits = clash(b, others, bbs)
        if hits:
            print("[r55] tie pad %d blocked by %s" % (i, [h[0] for h in hits][:3]),
                  flush=True)
            continue
        out["frame_tie_pad_%d" % i] = b
    return out


def make_rail_tabs(others, bbs):
    """Short brackets that land the frame on the base rail top face (z = 16).

    MEASURED: side plate bottom z = 33.6, rail top z = 16 -> 17.6 mm of air.
    Tab spans z 16..36, so it overlaps the plate by 2.4 mm and sits exactly on
    the rail; one M3 bolt + nut then pierces tab AND rail.
    """
    out = {}
    for x, ztop in RAIL_TABS:
        for side in (-1, 1):
            hh = ztop - 16.0
            b = K.box(12.0, TAB_WY, hh, (x, side * BOLT_Y, 16.0 + hh / 2.0))
            hits = clash(b, others, bbs)
            if hits:
                print("[r55] rail tab x=%.0f %+d blocked by %s"
                      % (x, side, [h[0] for h in hits][:3]), flush=True)
                continue
            out["frame_rail_tab_x%.0f_%+d" % (x, side)] = b
    return out


def drill_holes(frame, specs, keep_others):
    """Cut only the holes that are provably a clean through-joint."""
    done, skipped = [], []
    for sp in specs:
        h = cyl(sp["axis"], M3_CLR_R, sp["len"], tuple(sp["center"]))
        hit = [(n, round(h.intersect(s).Volume(), 2))
               for n, s in keep_others.items() if h.intersect(s).Volume() > 1.0]
        blocked = [x for x in hit if x[0] not in DRILLABLE]
        if blocked:
            skipped.append(dict(sp, blocked_by=blocked))
            continue
        inner = h.intersect(frame)
        if sp.get("need", 1.0) > inner.Volume():
            skipped.append(dict(sp, not_in_material_mm3=round(inner.Volume(), 2)))
            continue
        done.append(dict(sp, material_mm3=round(inner.Volume(), 2),
                         also_drilled=[x[0] for x in hit]))
    return done, skipped


def verify_joints(frame, done, others, tabs):
    """DEC-0055 fix A: prove each rail joint is a clean through hole."""
    out = []
    for h in done:
        if not h["id"].startswith("rail_"):
            continue
        x, y = float(h["center"][0]), float(h["center"][1])
        ztop = dict(((x0, zt) for x0, zt in RAIL_TABS))[x]
        axis = round(cyl("z", 0.3, 70.0, (x, y, 20.0)).intersect(frame).Volume(), 3)
        wall_in = round(cyl("z", 0.3, 24.0, (x, y - 2.6, 30.0)).intersect(frame).Volume(), 2)
        wall_out = round(cyl("z", 0.3, 24.0, (x, y + 2.6, 30.0)).intersect(frame).Volume(), 2)
        plate = round(cyl("z", 0.3, 14.0, (x, 70.0, ztop + 8.0)).intersect(frame).Volume(), 2)
        below = [(n, round(cyl("z", 2.6, 9.0, (x, y, -3.5)).intersect(s).Volume(), 2))
                 for n, s in others.items()
                 if cyl("z", 2.6, 9.0, (x, y, -3.5)).intersect(s).Volume() > 0.5]
        row = {"id": h["id"], "axis_y": y, "tab_top_z": ztop,
               "axis_material_mm3": axis, "wall_in_mm3": wall_in,
               "wall_out_mm3": wall_out, "side_plate_probe_mm3": plate,
               "nut_side_blockers": below,
               "through_hole": axis < 0.05 and wall_in > 1.0 and wall_out > 1.0,
               "plate_intact": plate > 1.0, "nut_space_clear": not below}
        out.append(row)
        print("[r55] joint %-14s axis_empty=%.3f walls in/out=%.2f/%.2f "
              "plate=%.2f nut_clear=%s pass=%s"
              % (row["id"], axis, wall_in, wall_out, plate, not below,
                 row["through_hole"] and row["plate_intact"] and row["nut_space_clear"]),
              flush=True)
    return out


def fuse_all(shapes):
    out = None
    for s in shapes:
        out = s if out is None else out.fuse(s)
    return out.clean()


def n_solids(shape):
    try:
        return len(shape.Solids())
    except Exception:
        return 1


def section_png(shapes, yplane, path, title):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection
    fig, ax = plt.subplots(figsize=(10, 10))
    slab = K.box(900.0, 0.8, 900.0, (30.0, yplane, 200.0))
    for name, s in shapes.items():
        try:
            sec = s.intersect(slab)
        except Exception:
            continue
        segs = []
        for f in sec.Faces():
            n = f.normalAt()
            if abs(n.y) < 0.99:
                continue
            for e in f.Edges():
                segs.append([(e.positionAt(i / 16.0).x, e.positionAt(i / 16.0).z)
                             for i in range(17)])
        if segs:
            ax.add_collection(LineCollection(segs, linewidths=0.9))
    ax.set_aspect("equal")
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Z (mm)")
    ax.set_title(title)
    ax.grid(True, linewidth=0.2, alpha=0.4)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def run(name, export=False):
    t0 = time.time()
    parts = build_parts(name, fresh=True)
    keep, vendor, gate = split_parts(parts)
    print("[r55 %s] keep %d / vendor %d / gate %d"
          % (name, len(keep), len(vendor), len(gate)), flush=True)

    members = merge_members(keep)
    others = {n: s for n, s in keep.items() if n not in members}
    bbs = prebbox(others)
    gussets = make_gussets(find_gussets(members, others, bbs))
    ties = make_tie_pads(others, bbs)
    tabs = make_rail_tabs(others, bbs)
    frame = fuse_all(list(members.values()) + list(gussets.values())
                     + list(ties.values()) + list(tabs.values()))
    print("[r55 %s] frame fused: %d solids, V=%.0f mm3 "
          "(members %d + gussets %d + ties %d + rail tabs %d)"
          % (name, n_solids(frame), frame.Volume(), len(members), len(gussets),
             len(ties), len(tabs)), flush=True)
    try:
        for _i, _sd in enumerate(frame.Solids()):
            _b = _sd.BoundingBox()
            print("[r55 %s]   solid %d V=%.0f x[%.1f,%.1f] y[%.1f,%.1f] z[%.1f,%.1f]"
                  % (name, _i, _sd.Volume(), _b.xmin, _b.xmax, _b.ymin, _b.ymax,
                     _b.zmin, _b.zmax), flush=True)
    except Exception as _e:
        print("[r55] solid diag failed: %r" % (_e,), flush=True)

    gb = None
    for n in ("gate_frame", "gate_bracket"):
        if n in gate:
            b = gate[n].BoundingBox()
            if gb is None:
                gb = {"x": (b.xmin, b.xmax), "y": (b.ymin, b.ymax), "z": (b.zmin, b.zmax)}
            else:
                gb = {k: (min(gb[k][0], v[0]), max(gb[k][1], v[1]))
                      for k, v in (("x", (b.xmin, b.xmax)), ("y", (b.ymin, b.ymax)),
                                   ("z", (b.zmin, b.zmax)))}
    specs = []
    for x in (RAIL_TABS[0][0], RAIL_TABS[1][0]):
        for sy in (-1, 1):
            specs.append({"axis": "z", "len": DRILL_LEN,
                          "center": (x, sy * BOLT_Y, DRILL_ZC),
                          "need": 20.0,
                          "joint": "rail tab -> base rail (M3 bolt + nut, through both)",
                          "id": "rail_x%.0f_%+d" % (x, sy)})
    if gb is not None:
        print("[r55 %s] gate envelope %s" % (name, gb), flush=True)
        for x, z in ((190.0, 200.0), (206.0, 220.0)):
            if True:
                specs.append({"axis": "y", "len": 160.0, "center": (x, 0.0, z),
                              "need": 4.0, "joint": "reserved: R49 gate (not modelled)",
                              "id": "gate_reserved_x%.0f_z%.0f" % (x, z)})
    done, skipped = drill_holes(frame, specs, others)
    joint_check = verify_joints(frame, done, others, tabs)
    for h in done:
        c = cyl(h["axis"], M3_CLR_R, h["len"], tuple(h["center"]))
        frame = frame.cut(c)
        for n in h.get("also_drilled", ()):
            others[n] = others[n].cut(c)
    for s in skipped:
        print("[r55 %s] hole SKIPPED %s: %s"
              % (name, s["id"], {k: v for k, v in s.items() if k not in ("axis", "len", "center", "need", "joint", "id")}),
              flush=True)

    final = dict(others)
    final[FRAME_NAME] = frame
    rows = [{"part": n, "volume_mm3": round(s.Volume(), 1), "bbox": bbox(s),
             "role": ("printed frame (merged)" if n == FRAME_NAME else "kept")}
            for n, s in sorted(final.items())]

    meta = {
        "units": "mm",
        "caliber": "T06 R55 prototype: merged printed frame + plain M3 through-joints",
        "variant": name,
        "half_spacing_mm": HALF[name],
        "excluded_from_this_version": {
            "vendor_cots_bodies": sorted(vendor),
            "gate_solids": sorted(gate),
            "note": "gate geometry not modelled; its mounting holes are reserved instead",
        },
        "merged_into_frame": {
            "members": sorted(members),
            "gussets": sorted(gussets),
            "tie_pads": sorted(ties),
            "rail_tabs": sorted(tabs),
            "solids_after_fuse": n_solids(frame),
            "volume_mm3": round(frame.Volume(), 1),
            "bbox": bbox(frame),
        },
        "m3_joints": done,
        "joint_verification": joint_check,
        "m3_skipped": skipped,
        "parts": rows,
        "n_parts": len(final),
    }

    if export:
        stem = "T06_shooter_frame_R56_%s" % name
        cq.exporters.export(cq.Workplane(obj=frame), str(OUT / (stem + ".step")))
        astem = "T06_shooter_assembly_R56_%s" % name
        assy = cq.Assembly(name=astem)
        for n, s in final.items():
            col = cq.Color(0.20, 0.56, 0.84, 1.0) if n == FRAME_NAME \
                else cq.Color(0.72, 0.74, 0.78, 1.0)
            assy.add(s, name=n, color=col)
        dst = OUT / (astem + ".step")
        assy.export(str(dst), exportType="STEP")
        meta["assembly_step_mb"] = round(dst.stat().st_size / 1e6, 1)
        meta["frame_step_mb"] = round((OUT / (stem + ".step")).stat().st_size / 1e6, 2)
        print("[r55 %s] STEP frame %.2f MB / assembly %.1f MB"
              % (name, meta["frame_step_mb"], meta["assembly_step_mb"]), flush=True)

        rd = cq.importers.importStep(str(OUT / (stem + ".step")))
        rb = rd.val().BoundingBox()
        meta["frame_readback"] = {"solids": len(rd.val().Solids()),
                                  "volume_mm3": round(rd.val().Volume(), 1),
                                  "bbox": {"x": [round(rb.xmin, 2), round(rb.xmax, 2)],
                                           "y": [round(rb.ymin, 2), round(rb.ymax, 2)],
                                           "z": [round(rb.zmin, 2), round(rb.zmax, 2)]}}

        section_png({FRAME_NAME: frame}, 0.0,
                    SECT / ("r56_%s_section_y0.png" % name),
                    "R56 %s section y=0 (frame + kept parts)" % name)
        section_png({FRAME_NAME: frame, "shooter_frame_xsec": frame}, 64.0,
                    SECT / ("r56_%s_section_y64.png" % name),
                    "R56 %s section y=64 (plate-to-tray gusset zone)" % name)
        section_png(final, 0.0, SECT / ("r56_%s_assembly_y0.png" % name),
                    "R56 %s full kept assembly, y=0" % name)

    (OUT / ("report_r56_%s.json" % name)).write_text(
        json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")
    print("[r55 %s] done in %.1f s" % (name, time.time() - t0), flush=True)
    return meta


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    names = [a for a in argv if not a.startswith("-")] or ["pollen"]
    for n in names:
        run(n, export="--step" in argv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
