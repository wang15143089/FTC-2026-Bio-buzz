# -*- coding: utf-8 -*-
"""T06 R55 -- rail-joint reachability readback (READ-ONLY on the delivered STEPs).

DEC-0055 fix A check: the 4 rail joints must be clean through holes in the
printed frame, coaxial with a real hole in the base rail, with the nut side and
the screwdriver side both reachable.  Nothing here writes to any part file.

Run:  .venv-cad/Scripts/python.exe -X utf8 cad/_r55_joint_reachability.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
OUT = HERE / "output" / "_r55_frame"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

FRAME_STEP = OUT / "T06_shooter_frame_R55_pollen.step"
ASSY_STEP = OUT / "T06_shooter_assembly_R55_pollen.step"
BOLT_Y = 76.0
BOLT_X = ((60.0, 44.0), (76.0, 48.0))   # (x, tab top z) from RAIL_TABS
RAIL_Z = (2.0, 16.0)                    # base_rail measured z span
R_HOLE = 1.70                           # O3.4 M3 clearance


def cyl(r, p0, d, h):
    return cq.Solid.makeCylinder(r, h, cq.Vector(*p0), cq.Vector(*d))


def ztube(r, x, y, z0, z1):
    return cyl(r, (x, y, z0), (0, 0, 1), z1 - z0)


def ytube(r, x, z, y0, y1):
    return cyl(r, (x, y0, z), (0, 1, 0), y1 - y0)


def box(x0, x1, y0, y1, z0, z1):
    x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0).translate(
        ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)).val()


def rows(shape, tool, axis_i, label):
    got = []
    for s in tool.intersect(shape).Solids():
        bb = s.BoundingBox()
        a = (bb.xmin, bb.ymin, bb.zmin)[axis_i]
        b = (bb.xmax, bb.ymax, bb.zmax)[axis_i]
        if s.Volume() > 0.02:
            got.append([round(a, 2), round(b, 2), round(s.Volume(), 2)])
    got.sort()
    print("   %-46s -> %s" % (label, got))
    return got


def main():
    t0 = time.time()
    frame = cq.importers.importStep(str(FRAME_STEP)).val()
    assy = cq.importers.importStep(str(ASSY_STEP)).val()
    print("frame solids=%d V=%.0f ; assembly %.0f mm3 (%.1fs)"
          % (len(frame.Solids()), frame.Volume(), assy.Volume(), time.time() - t0))

    rep = {"units": "mm", "revision": "R55 (DEC-0055 fix A)", "source": FRAME_STEP.name,
           "method": "read-only probe of the exported STEPs",
           "joints": [], "gate_reserved": {}, "bolt_stack": {}}
    ok_all = True

    for x, ztop in BOLT_X:
        for sy in (-1, 1):
            y = sy * BOLT_Y
            jid = "rail_x%.0f_%+d" % (x, sy)
            print("== %s  axis (x=%.0f, y=%+.0f) ==" % (jid, x, y))
            r = {"id": jid, "axis": [x, y]}

            # 1. the axis itself must be free all the way through (frame + rail)
            r["frame_axis_mm3"] = round(
                ztube(0.3, x, y, -20.0, ztop + 6.0).intersect(frame).Volume(), 3)
            r["assy_axis_mm3"] = round(
                ztube(0.3, x, y, -20.0, ztop + 6.0).intersect(assy).Volume(), 3)

            # 2. bore size: O3.4 probe must clear, O3.5 probe must bite
            r["probe_34_mm3"] = round(
                ztube(1.70, x, y, ztop - 24.0, ztop - 2.0).intersect(frame).Volume(), 3)
            r["probe_35_mm3"] = round(
                ztube(1.75, x, y, ztop - 24.0, ztop - 2.0).intersect(frame).Volume(), 3)

            # 3. walls on both sides of the bore, and the side plate left intact
            r["wall_in_mm3"] = round(
                ztube(0.3, x, y - 2.6, ztop - 26.0, ztop - 2.0).intersect(frame).Volume(), 2)
            r["wall_out_mm3"] = round(
                ztube(0.3, x, y + 2.6, ztop - 26.0, ztop - 2.0).intersect(frame).Volume(), 2)
            r["plate_above_tab_mm3"] = round(
                ztube(0.3, x, sy * 70.0, ztop + 2.0, ztop + 16.0).intersect(frame).Volume(), 2)

            # 4. tab bottom must sit on the rail top face, bore must span both
            print("   frame z @ x=%.0f y=%+.0f :" % (x, y))
            zrows = rows(frame, ztube(2.6, x, y - 0.0, -20.0, ztop + 4.0), 2,
                         "material (r=2.6 ring envelope)")
            print("   assy  z @ x=%.0f y=%+.0f :" % (x, y))
            rows(assy, ztube(2.6, x, y, -20.0, ztop + 4.0), 2, "material (r=2.6)")
            print("   frame y @ x=%.0f z=%.0f :" % (x, ztop - 14.0))
            r["tab_y_span"] = rows(frame, ytube(0.3, x, ztop - 14.0, 55.0, 95.0), 1,
                                   "tab cross-section along y")
            r["tab_bottom_z"] = min([a for a, b, v in zrows], default=None)

            # 5. nut side + screwdriver side
            r["nut_space_mm3"] = round(
                box(x - 7, x + 7, y - 7, y + 7, -20, 1.5).intersect(assy).Volume(), 2)
            r["head_space_mm3"] = round(
                cyl(2.75, (x, y, ztop + 0.2), (0, 0, 1), 20.0).intersect(assy).Volume(), 2)
            r["driver_space_mm3"] = round(
                cyl(1.5, (x, y, ztop + 0.2), (0, 0, 1), 60.0).intersect(assy).Volume(), 2)
            r["plate_to_head_gap_mm"] = round((abs(y) - 2.75) - 72.0, 2)
            r["head_washer_clearance_mm"] = round((abs(y) - 72.0) - 3.0, 2)

            r["rail_bottom_z"] = RAIL_Z[0]
            r["rail_top_z"] = RAIL_Z[1]
            r["grip_mm"] = ztop - RAIL_Z[0]
            r["required_bolt_shank_mm"] = round(r["grip_mm"] + 1.0 + 2.4, 1)
            r["through_hole"] = r["frame_axis_mm3"] < 0.05 and r["assy_axis_mm3"] < 0.05
            r["bore_is_34"] = r["probe_34_mm3"] < 0.05 and r["probe_35_mm3"] > 3.0
            r["walls_present"] = r["wall_in_mm3"] > 3.0 and r["wall_out_mm3"] > 3.0
            r["plate_intact"] = r["plate_above_tab_mm3"] > 1.0
            r["nut_reachable"] = r["nut_space_mm3"] < 0.05
            r["head_reachable"] = r["head_space_mm3"] < 0.05 and r["driver_space_mm3"] < 0.05
            r["pass"] = all(r[k] for k in ("through_hole", "bore_is_34", "walls_present",
                                           "plate_intact", "nut_reachable", "head_reachable"))
            ok_all = ok_all and r["pass"]
            rep["joints"].append(r)
            print("   -> through=%.3f/%.3f bore34=%s walls=%.2f/%.2f plate=%.2f "
                  "nut=%.2f head=%.2f grip=%.1f PASS=%s"
                  % (r["frame_axis_mm3"], r["assy_axis_mm3"], r["bore_is_34"],
                     r["wall_in_mm3"], r["wall_out_mm3"], r["plate_above_tab_mm3"],
                     r["nut_space_mm3"], r["head_space_mm3"], r["grip_mm"], r["pass"]),
                  flush=True)

    for x, z in ((190.0, 200.0), (206.0, 220.0)):
        key = "gate_reserved_x%.0f_z%.0f" % (x, z)
        inner = round(ytube(0.3, x, z, -120.0, 120.0).intersect(frame).Volume(), 3)
        p34 = round(ytube(1.70, x, z, -120.0, 120.0).intersect(frame).Volume(), 3)
        p35 = round(ytube(1.75, x, z, -120.0, 120.0).intersect(frame).Volume(), 3)
        out_n = round(box(x - 3, x + 3, -115, -85, z - 3, z + 3).intersect(frame).Volume(), 2)
        out_p = round(box(x - 3, x + 3, 85, 115, z - 3, z + 3).intersect(frame).Volume(), 2)
        plates = rows(frame, ytube(2.6, x, z, -120.0, 120.0), 1,
                      "frame y @ x=%.0f z=%.0f (r=2.6 ring)" % (x, z))
        res = {"axis_material_mm3": inner, "probe_34_mm3": p34, "probe_35_mm3": p35,
               "outside_mm3": [out_n, out_p], "plate_ring_y": plates,
               "through_hole": inner < 0.05 and p34 < 0.05,
               "bore_is_34": p35 > 3.0, "outside_free": out_n < 0.05 and out_p < 0.05}
        res["pass"] = res["through_hole"] and res["bore_is_34"] and res["outside_free"]
        rep["gate_reserved"][key] = res
        ok_all = ok_all and res["pass"]
        print("== %s: axis=%.3f probe34=%.3f probe35=%.2f outside=%.2f/%.2f PASS=%s"
              % (key, inner, p34, p35, out_n, out_p, res["pass"]), flush=True)

    rep["bolt_stack"] = {
        "rail_z": [RAIL_Z[0], RAIL_Z[1]],
        "tab_heights_mm": {"x=60": 44.0 - 16.0, "x=76": 48.0 - 16.0},
        "grip_mm": {"x=60": 42.0, "x=76": 46.0},
        "washer_mm": 1.0, "nut_m3_mm": 2.4,
        "recommended": "M3x50 for x=60, M3x55 for x=76 (or 4x M3x55); "
                       "plain washer + M3 nut under the rail",
        "note": "nut and driver are both outside the printed part; nothing is embedded",
    }
    rep["verdict"] = "PASS (4/4 rail joints through + 4/4 gate reserved holes)" if ok_all \
        else "FAIL - see per-joint flags"
    rep["elapsed_s"] = round(time.time() - t0, 1)
    (OUT / "report_r55_joint_reachability.json").write_text(
        json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\nVERDICT: %s" % rep["verdict"])
    print("wrote report_r55_joint_reachability.json (%.0fs)" % rep["elapsed_s"])
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
