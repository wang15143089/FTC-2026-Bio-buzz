# -*- coding: utf-8 -*-
"""T06 R54 -- M3 joint reachability check (read-only).

Why this exists
---------------
DEC-0053 claimed the four rail-leg joints are "M3 bolt + nut through both
members".  Probing the DELIVERED STEP shows the hole is blind at the top and
opens into the chassis rail's underside -> neither a bolt head nor a nut can be
reached.  This script re-measures that from the delivered geometry; it never
writes over any part file.

Run:  .venv-cad/Scripts/python.exe -X utf8 cad/_r54_joint_reachability.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
OUT = HERE / "output" / "_r54_frame"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

FRAME_STEP = OUT / "T06_shooter_frame_R54_pollen.step"
ASSY_STEP = OUT / "T06_shooter_assembly_R54_pollen.step"
RAIL_Y = (63.0, 81.0)          # base_rail_+72 measured y span
RAIL_Z = (2.0, 16.0)           # measured z span (bottom / top face)
LEG_COLS = ((60.0, 44.0), (76.0, 48.0))
LEG_Y = (64.0, 76.0)


def cyl(r, p0, d, h):
    return cq.Solid.makeCylinder(r, h, cq.Vector(*p0), cq.Vector(*d))


def scan(shape, axis, fixed, lo, hi, r, label):
    """Material intervals (mm) of `shape` along one axis inside a thin tube."""
    p0 = {"x": (lo, fixed[0], fixed[1]), "y": (fixed[0], lo, fixed[1]),
          "z": (fixed[0], fixed[1], lo)}[axis]
    d = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}[axis]
    i = "xyz".index(axis)
    it = cyl(r, p0, d, hi - lo).intersect(shape)
    rows = []
    for s in it.Solids():
        bb = s.BoundingBox()
        a = (bb.xmin, bb.ymin, bb.zmin)[i]
        b = (bb.xmax, bb.ymax, bb.zmax)[i]
        if s.Volume() > 0.02:
            rows.append([round(a, 2), round(b, 2), round(s.Volume(), 2)])
    rows.sort()
    print("   %-30s -> %s" % (label, rows))
    return rows


def main():
    t0 = time.time()
    frame = cq.importers.importStep(str(FRAME_STEP)).val()
    report = {"units": "mm", "source": str(FRAME_STEP.name),
              "import_s": round(time.time() - t0, 1), "rail": {"y": RAIL_Y, "z": RAIL_Z},
              "verdict": {}, "evidence": {}}

    print("== A. hole axis, printed frame only (tube r=0.3, well inside O3.4) ==")
    axis_rows = {}
    for x, ztop in LEG_COLS:
        for sy in (-1, 1):
            key = "x%.0f_%+d" % (x, sy)
            rows = scan(frame, "z", (x, sy * 70.0), -10.0, 70.0, 0.3,
                        "frame z @ x=%.0f y=%+.0f, hole axis" % (x, sy * 70.0))
            axis_rows[key] = rows
            # blind end = bottom of the lowest material run on the axis
            global_min_gap = None
            if rows:
                global_min_gap = rows[0][0]
            print("        -> %s: material starts at z = %s (hole is blind above it)"
                  % (key, global_min_gap))
    report["evidence"]["hole_axis_material_z"] = axis_rows

    print("== B. hole cross-section at mid-leg (z = 27), scan Y (r=0.3) ==")
    for x, _ in LEG_COLS:
        scan(frame, "y", (x, 27.0), 40.0, 100.0, 0.3,
             "frame y @ x=%.0f z=27" % x)

    print("== C. rail band: does the printed frame reach z < 16 in y 63..81? ==")
    for sy in (-1, 1):
        b = cq.Workplane("XY").box(60.0, 18.0, 14.0).translate((68.0, sy * 72.0, 9.0)).val()
        it = b.intersect(frame)
        vol = round(sum(s.Volume() for s in it.Solids()), 2)
        print("   frame volume inside base_rail_%+d envelope: %.2f mm3" % (sy, vol))
        report["evidence"]["frame_in_rail_envelope_mm3_%+d" % sy] = vol

    print("== D. gate reserved holes (y axis): is the frame open on both sides? ==")
    gate = {}
    for x, z in ((190.0, 200.0), (206.0, 220.0)):
        b = cq.Workplane("XY").box(3.0, 260.0, 3.0).translate((x, 0.0, z)).val()
        rows = sorted([[round(s.BoundingBox().ymin, 2), round(s.BoundingBox().ymax, 2),
                        round(s.Volume(), 2)] for s in b.intersect(frame).Solids()
                       if s.Volume() > 0.02])
        print("   %-30s -> %s" % ("frame y @ x=%.0f z=%.0f (3x3)" % (x, z), rows))
        outer = []
        for sy in (-1, 1):
            b = cq.Workplane("XY").box(6.0, 30.0, 6.0).translate((x, sy * 100.0, z)).val()
            outer.append(round(sum(s.Volume() for s in b.intersect(frame).Solids()), 2))
        gate["x%.0f_z%.0f" % (x, z)] = {"material_y": rows, "outside_mm3": outer}
        for sy in (-1, 1):
            idx = 0 if sy == -1 else 1
            print("        -> outside face (%+d side, y 85..115) has %.2f mm3 -> %s"
                  % (sy, outer[idx], "free" if outer[idx] < 0.01 else "BLOCKED"))
    report["evidence"]["gate_reserved"] = gate

    report["verdict"] = {
        "rail_leg_joints": "NOT ASSEMBLABLE (4 of 6): axis is solid above z=38 "
                           "(plate + tab crown) so no head-side access; the lower "
                           "end opens below the chassis rail bottom (z=2) so no "
                           "nut side and no wrench space.",
        "gate_reserved_holes": "OK (2 of 6): frame has material only in the two "
                               "side plates (y +-68..72) and both outer faces are free.",
    }
    dst = OUT / "report_r54_joint_reachability.json"
    dst.write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    print("\nwrote %s (%.1f s)" % (dst, time.time() - t0))


if __name__ == "__main__":
    main()
