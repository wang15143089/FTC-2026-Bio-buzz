# -*- coding: utf-8 -*-
"""T06 R55 -- regression: R55 vs R54 symmetric difference must be confined to the tabs."""
import json, sys, time
from pathlib import Path
import cadquery as cq
HERE = Path(__file__).resolve().parent
OUT55 = HERE / "output" / "_r55_frame"
OUT54 = HERE / "output" / "_r54_frame"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

t0 = time.time()
f55 = cq.importers.importStep(str(OUT55 / "T06_shooter_frame_R55_pollen.step")).val()
f54 = cq.importers.importStep(str(OUT54 / "T06_shooter_frame_R54_pollen.step")).val()
print("imported %.1fs   R55 V=%.0f  R54 V=%.0f" % (time.time()-t0, f55.Volume(), f54.Volume()))

def report(shape, label):
    rows = []
    for s in shape.Solids():
        if s.Volume() > 0.05:
            g = s.BoundingBox()
            rows.append({"x":[round(g.xmin,2),round(g.xmax,2)], "y":[round(g.ymin,2),round(g.ymax,2)],
                         "z":[round(g.zmin,2),round(g.zmax,2)], "mm3":round(s.Volume(),2)})
    rows.sort(key=lambda r:-r["mm3"])
    v = sum(r["mm3"] for r in rows)
    print("   %-12s solids(>0.05) = %2d   volume = %.2f mm3" % (label, len(rows), v))
    for r in rows[:12]:
        print("      %s" % r)
    return {"n": len(rows), "volume_mm3": round(v,2), "solids": rows}

rep = {"units":"mm","method":"symmetric difference of the exported R55 and R54 frame STEPs"}
print("== added material (R55 not in R54) ==")
rep["added"] = report(f55.cut(f54), "added")
print("== removed material (R54 not in R55) ==")
rep["removed"] = report(f54.cut(f55), "removed")
(OUT55 / "report_r55_vs_r54_diff.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
print("wrote report_r55_vs_r54_diff.json  (%.0fs)" % (time.time()-t0))
