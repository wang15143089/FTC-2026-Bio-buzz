# -*- coding: utf-8 -*-
"""T06 R56 print split for the Bambu Lab H2D (325 x 320 x 325, single nozzle).

The R56 frame is ONE fused printed solid of 432.5 x 183.0 x 404.5 mm, so it cannot
be printed in one go.  Two planes turn it into 8 printable lumps:

    P1 = frame & x <= 100 & z <= 300   rear chassis   247.2 x 183.0 x 303.5   1 lump
    P2 = frame & x >= 100 & z <= 300   front tray kit 185.3 x 144.0 x 296.8   5 lumps
    P3 = frame & z >= 300              upper plates   247.6 x 144.0 x 101.0   2 lumps

Largest lump = 247.6 mm, so every lump has > 75 mm of margin on the 325 mm axis.

Joints (agreed 2026-10-14: no self-tapping, every bolt goes through BOTH members,
head one side / nut the other):

  * S1 seam x=100  -- one lap tab per side plate (x 75..115, z 95..133),
                     2 x M3 through y, both holes on the x > 100 side
  * S1 seam x=100  -- tray lap (interlocking, no bolt: a bolt head or nut on the tray
                      top would sit in the ball path; the tray is only a ball support,
                      the side-plate laps carry the frame)
  * S1 seam x=100  -- feeder-mount tongues (2 x M3 tongue-and-pocket, no bolt)
  * S2 seam z=300  -- one lap tab per side plate, 2 x M3 through y

A tab is fused onto its OWNER piece and the same solid is relieved from the mating
pieces, so the halves never interfere; the O3.4 holes are then drilled through both.

Units: mm.  Chassis X-Y plane, +Z up, flywheel / paddle axes along Y.
"""
from __future__ import annotations

import json
import math
import time
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
OUT = HERE / "output" / "_r56_frame"
SPL = OUT / "split"
CACHE = OUT / "cache"

LIMITS = (325.0, 320.0, 325.0)      # H2D single nozzle build volume
CUT_X, CUT_Z = 100.0, 300.0
PLATE_Y = (68.0, 72.0)
TAB_T = 2.5                         # lap tab thickness proud of the plate
TAB_BITE = 1.0                      # how deep the tab bites into the plate
M3_R = 1.70                         # O3.4 clearance
BOLT_LEN = 20.0
BOLT_YC = 72.25                     # tab centre in |y| (plate 68..72 + 1 bite + 2.5/2)
BITE_MIN_MM3 = 300.0
CLASH_MM3 = 0.5
PIECE_CLASH_MM3 = 1.0
HOLE_LEFTOVER_MM3 = 0.05

# Tray floor (MEASURED 2026-10-14 from the R56 frame / feeder_shell_tray cache
# brep): the ball-side floor of the intake tray is the plane
#     z_floor(x) = TRAY_FLOOR_Z0 + x * tan(5 deg)
# Probe: 1 mm x-columns at y = 0, x = 40..280 -> floor top z matches that line
# within 0.02 mm and the tray plate is 6.11 mm thick.  The old ztop(x) line
# (PIVOT_Z + ...) is the PRE-SHIFT R37 pivot: it sits 17.15 mm above the
# as-built floor, so a lap placed on it floated in mid air (bite = 0).
TRAY_T = 6.11
PIV_X, PIV_Z, TILT = -2.30, 17.50, 5.0
TRAY_FLOOR_Z0 = 0.55            # MEASURED: floor top z at x = 0
TRAY_LAP = dict(x0=80.0, x1=130.0, half_y=50.0, bite=1.0, t=3.0)
FEEDER_TONGUES = dict(x0=88.0, x1=115.0, y_in=54.0, y_out=62.5, z0=17.0, z1=25.0)

# (seam, x0, x1, z0, z1, bolts (x, z) -- 2 bolts per tab, both inside the tab)
# S1 z window is set by the LOWER bearing carriage, which slides in the 52 deg
# window: measured pollen corner (113.2, 134.7); the nectar setting sweeps it
# 11 mm along the slot, so the lowest reach is z = 134.6 over the whole
# 80.0..91.2 travel.  Everything above z = 133 at x 75..115 is carriage
# territory, so the tab stops at 133.  Both M3 holes sit on the P2 side
# (x = 108 > 100) so the lap really bolts the two pieces together; a hole at
# x < 100 would only clamp the tab to its own plate.
PLATE_TABS = (
    ("S1", 75.0, 115.0, 95.0, 133.0, ((108.0, 105.0), (108.0, 124.0))),
    ("S2", 55.0, 125.0, 265.0, 320.0, ((75.0, 282.0), (110.0, 282.0))),
)
SEAM_OWNER = {"S1": "frameP_1_rear_lower", "S2": "frameP_3_top"}
SEAM_OTHER = {"S1": ("frameP_2_front_lower",),
              "S2": ("frameP_1_rear_lower", "frameP_2_front_lower")}
PIECES = ("frameP_1_rear_lower", "frameP_2_front_lower", "frameP_3_top")


# ------------------------------------------------------------------ primitives
def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False
                                  ).translate((x0, y0, z0)).val()


def cyl(axis, r, center, length):
    wp = cq.Workplane("XZ") if axis == "y" else cq.Workplane("XY")
    return wp.circle(r).extrude(length / 2.0, both=True).translate(center).val()


def ztop(x):
    """Ball-side tray floor, MEASURED as-built (see TRAY_FLOOR_Z0).

    The R37 pivot line (PIV_Z + (x - PIV_X) * tan 5) is the PRE-shift pivot
    and is 17.15 mm above the real floor, so it must not be used to place
    anything on the tray.
    """
    return TRAY_FLOOR_Z0 + x * math.tan(math.radians(TILT))


def plate_tab(side, x0, x1, z0, z1):
    if side > 0:
        y0, y1 = PLATE_Y[1] - TAB_BITE, PLATE_Y[1] - TAB_BITE + TAB_T
    else:
        y1, y0 = -(PLATE_Y[1] - TAB_BITE), -PLATE_Y[1] + TAB_BITE - TAB_T
    return box(x0, x1, y0, y1, z0, z1)


def tray_lap():
    x0, x1 = TRAY_LAP["x0"], TRAY_LAP["x1"]
    # Slab straddles the tray UNDERSIDE: TRAY_LAP['bite'] into the tray, the
    # rest hangs clear below it.  The tray underside is free air (the tray is
    # the lowest material in P2 there), so the lap never touches the ball path.
    top0 = ztop(x0) + TRAY_LAP["bite"]
    top1 = ztop(x1) + TRAY_LAP["bite"]
    return (cq.Workplane("XZ")
            .moveTo(x0, top0 - TRAY_LAP["t"]).lineTo(x1, top1 - TRAY_LAP["t"])
            .lineTo(x1, top1).lineTo(x0, top0).close()
            .extrude(TRAY_LAP["half_y"], both=True)).val()


def feeder_tongue(side):
    y0, y1 = sorted((side * FEEDER_TONGUES["y_in"], side * FEEDER_TONGUES["y_out"]))
    return box(FEEDER_TONGUES["x0"], FEEDER_TONGUES["x1"], y0, y1,
               FEEDER_TONGUES["z0"], FEEDER_TONGUES["z1"])


# ------------------------------------------------------------------- reporting
def bbox_row(shape):
    b = shape.BoundingBox()
    return {"x": [round(b.xmin, 2), round(b.xmax, 2)],
            "y": [round(b.ymin, 2), round(b.ymax, 2)],
            "z": [round(b.zmin, 2), round(b.zmax, 2)],
            "dims_mm": [round(b.xmax - b.xmin, 1), round(b.ymax - b.ymin, 1),
                        round(b.zmax - b.zmin, 1)],
            "volume_mm3": round(shape.Volume(), 1),
            "solids": len(shape.Solids())}


def fits(row, limits=LIMITS):
    d = sorted(row["dims_mm"], reverse=True)
    lim = sorted(limits, reverse=True)
    return bool(d[0] <= lim[0] and d[1] <= lim[1] and d[2] <= lim[2])


def lump_rows(shape):
    out = []
    for s in shape.Solids():
        r = bbox_row(s)
        r["fits"] = fits(r)
        out.append(r)
    out.sort(key=lambda r: -max(r["dims_mm"]))
    return out


def load_cache():
    parts = {}
    for f in sorted(CACHE.glob("pollen__*.brep")):
        parts[f.name[8:-5].replace("~", "/")] = cq.Shape.importBrep(str(f))
    return parts


def clashes(b, others):
    out = []
    bb = b.BoundingBox()
    for n, s in others.items():
        cb = s.BoundingBox()
        if (bb.xmax < cb.xmin or cb.xmax < bb.xmin or bb.ymax < cb.ymin or
                cb.ymax < bb.ymin or bb.zmax < cb.zmin or cb.zmax < bb.zmin):
            continue
        v = s.intersect(b).Volume()
        if v > CLASH_MM3:
            out.append((n, round(v, 2)))
    return out


# ------------------------------------------------------------------------ main
def main():
    SPL.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    src = OUT / "T06_shooter_frame_R56_pollen.step"
    frame = cq.importers.importStep(str(src)).val()
    others = load_cache()
    print("frame %.0f mm3 %d solids + %d cached parts  %.1fs"
          % (frame.Volume(), len(frame.Solids()), len(others), time.time() - t0), flush=True)

    big = 3000.0
    parts = {
        PIECES[0]: frame.intersect(box(CUT_X - big, CUT_X, -big, big, -big, CUT_Z)),
        PIECES[1]: frame.intersect(box(CUT_X, CUT_X + big, -big, big, -big, CUT_Z)),
        PIECES[2]: frame.intersect(box(CUT_X - big, CUT_X + big, -big, big, CUT_Z, CUT_Z + big)),
    }
    print("plane cut done %.1fs" % (time.time() - t0), flush=True)

    report = {"units": "mm", "source": src.name, "limits_mm": list(LIMITS),
              "cut_x": CUT_X, "cut_z": CUT_Z, "tabs": [], "tongues": [], "tray_lap": {}}

    # ---- side-plate lap tabs, both sides, both seams ------------------------
    for seam, x0, x1, z0, z1, bolts in PLATE_TABS:
        owner, others_l = SEAM_OWNER[seam], SEAM_OTHER[seam]
        for side in (+1, -1):
            t = plate_tab(side, x0, x1, z0, z1)
            bite = t.intersect(parts[owner]).Volume()
            third = clashes(t, others)
            parts[owner] = parts[owner].fuse(t).clean()
            for o in others_l:
                parts[o] = parts[o].cut(t)
            holes = []
            for bx, bz in bolts:
                h = cyl("y", M3_R, (bx, side * BOLT_YC, bz), BOLT_LEN)
                parts[owner] = parts[owner].cut(h)
                for o in others_l:
                    parts[o] = parts[o].cut(h)
                holes.append({"x": bx, "z": bz})
            row = {"seam": seam, "side": side, "x": [x0, x1], "z": [z0, z1],
                   "owner": owner, "relieved": list(others_l), "bolts": holes,
                   "bite_mm3": round(bite, 1), "third_party_clash": third,
                   "bite_ok": bite >= BITE_MIN_MM3, "clean_ok": not third}
            report["tabs"].append(row)
            print("tab %s %+d x%.0f..%.0f z%.0f..%.0f bite=%.0f third=%s  %.1fs"
                  % (seam, side, x0, x1, z0, z1, bite, third or "-", time.time() - t0),
                  flush=True)

    # ---- feeder-mount tongue and pocket ------------------------------------
    for side in (+1, -1):
        t = feeder_tongue(side)
        bite = t.intersect(parts[PIECES[1]]).Volume()
        parts[PIECES[0]] = parts[PIECES[0]].fuse(t).clean()
        parts[PIECES[1]] = parts[PIECES[1]].cut(t)
        row = {"side": side, "owner": PIECES[0], "relieved": PIECES[1],
               "tongue": [FEEDER_TONGUES["x0"], FEEDER_TONGUES["x1"]],
               "pocket_mm3": round(bite, 1), "pocket_ok": bite >= 100.0}
        report["tongues"].append(row)
        print("tongue %+d pocket=%.1f  %.1fs" % (side, bite, time.time() - t0), flush=True)

    # ---- tray lap (interlocking, no bolt) ----------------------------------
    t = tray_lap()
    bite = t.intersect(parts[PIECES[0]]).Volume()
    third = clashes(t, others)
    parts[PIECES[0]] = parts[PIECES[0]].fuse(t).clean()
    parts[PIECES[1]] = parts[PIECES[1]].cut(t)
    report["tray_lap"] = {"x": [TRAY_LAP["x0"], TRAY_LAP["x1"]],
                          "half_y": TRAY_LAP["half_y"], "bite_mm3": round(bite, 1),
                          "third_party_clash": third, "bite_ok": bite >= BITE_MIN_MM3,
                          "clean_ok": not third}
    print("tray lap bite=%.0f third=%s  %.1fs" % (bite, third or "-", time.time() - t0), flush=True)

    # ---- verification -------------------------------------------------------
    lumps = {}
    for n in PIECES:
        rows = lump_rows(parts[n])
        lumps[n] = rows
        r = bbox_row(parts[n])
        print("%s  %s  V=%.0f  lumps=%d  fits_all=%s"
              % (n, r["dims_mm"], r["volume_mm3"], r["solids"],
                 all(x["fits"] for x in rows)), flush=True)

    pair = {}
    for i in range(len(PIECES)):
        for j in range(i + 1, len(PIECES)):
            a, b = PIECES[i], PIECES[j]
            v = parts[a].intersect(parts[b]).Volume()
            pair["%s^%s" % (a, b)] = round(v, 3)
    holes = []
    for row in report["tabs"]:
        for h in row["bolts"]:
            p = cyl("y", 0.40, (h["x"], row["side"] * BOLT_YC, h["z"]), BOLT_LEN - 4.0)
            left = []
            for n in [row["owner"]] + list(row["relieved"]):
                v = p.intersect(parts[n]).Volume()
                if v > HOLE_LEFTOVER_MM3:
                    left.append([n, round(v, 3)])
            holes.append({"seam": row["seam"], "side": row["side"], "x": h["x"],
                          "z": h["z"], "material_left": left, "ok": not left})
    report["piece_overlap_mm3"] = pair
    report["piece_overlap_ok"] = all(v < PIECE_CLASH_MM3 for v in pair.values())
    report["bolt_holes"] = holes
    report["bolt_holes_ok"] = all(h["ok"] for h in holes)
    report["lumps"] = lumps
    report["all_lumps_fit"] = all(x["fits"] for rows in lumps.values() for x in rows)
    report["n_lumps"] = sum(len(rows) for rows in lumps.values())
    report["elapsed_s"] = round(time.time() - t0, 1)

    print("piece overlap %s ok=%s | holes ok=%s | all lumps fit=%s"
          % (pair, report["piece_overlap_ok"], report["bolt_holes_ok"],
             report["all_lumps_fit"]), flush=True)

    # ---- export + read back -------------------------------------------------
    for n in PIECES:
        cq.exporters.export(cq.Workplane(obj=parts[n]), str(SPL / ("%s.step" % n)))
    assy = cq.Assembly(name="T06_shooter_frame_R56_split")
    for n in PIECES:
        assy.add(parts[n], name=n)
    assy.export(str(SPL / "T06_shooter_frame_R56_split.step"), exportType="STEP")
    rb = {}
    for n in PIECES:
        s = cq.importers.importStep(str(SPL / ("%s.step" % n))).val()
        b = s.BoundingBox()
        rb[n] = {"dims_mm": [round(b.xmax - b.xmin, 1), round(b.ymax - b.ymin, 1),
                             round(b.zmax - b.zmin, 1)],
                 "volume_mm3": round(s.Volume(), 1), "solids": len(s.Solids())}
        rb[n]["fits"] = fits(rb[n])
    report["readback"] = rb
    report["readback_volume_delta_mm3"] = {
        n: round(rb[n]["volume_mm3"] - parts[n].Volume(), 2) for n in PIECES}

    (SPL / "report_r56_split.json").write_text(
        json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    print("exported to %s  %.1fs" % (SPL, time.time() - t0), flush=True)
    return report


if __name__ == "__main__":
    main()
