# -*- coding: utf-8 -*-
"""T06 R55 -- printability probe (read-only): overhang area by z band + bottom slab layout."""
import json, sys, time
from pathlib import Path
import cadquery as cq

HERE = Path(__file__).resolve().parent
OUT = HERE / "output" / "_r55_frame"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
FRAME = OUT / "T06_shooter_frame_R55_pollen.step"

t0 = time.time()
f = cq.importers.importStep(str(FRAME)).val()
print("imported %.1fs  solids=%d  V=%.0f" % (time.time()-t0, len(f.Solids()), f.Volume()))
rep = {"units":"mm","source":FRAME.name,"note":"as-drawn orientation assumed = print with +z up"}

print("== 1. downward-facing face area (normal.z < -0.7) by z band ==")
bands = {}
tot = 0.0
nface = 0
for fc in f.Faces():
    try:
        a = fc.Area()
        c = fc.Center()
        n = fc.normalAt(c)
    except Exception:
        continue
    nface += 1
    if n.z < -0.7:
        tot += a
        k = int(c.z // 5) * 5
        bands[k] = bands.get(k, 0.0) + a
print("   faces=%d  total downward area = %.0f mm2" % (nface, tot))
for k in sorted(bands, key=lambda k: -bands[k])[:10]:
    print("   z %+4d..%+4d : %8.0f mm2" % (k, k+5, bands[k]))
rep["downward_face_area_mm2"] = round(tot,1)
rep["downward_area_by_z_band"] = {str(k): round(v,1) for k,v in sorted(bands.items())}

print("== 2. bottom region: what material exists below z = 6, and is it one piece? ==")
def slab(z0, z1):
    b = cq.Workplane("XY").box(400, 300, z1-z0).translate((0, 0, (z0+z1)/2)).val()
    it = b.intersect(f)
    rows = []
    for s in it.Solids():
        if s.Volume() > 0.5:
            g = s.BoundingBox()
            rows.append([round(g.xmin,1), round(g.xmax,1), round(g.ymin,1), round(g.ymax,1),
                         round(g.zmin,2), round(g.zmax,2), round(s.Volume(),1)])
    return rows
slabs = {}
for z0, z1 in ((-4.0, 0.0), (0.0, 1.0), (1.0, 2.0), (2.0, 3.0), (3.0, 4.0), (4.0, 6.0)):
    rows = slab(z0, z1)
    slabs["z %.1f..%.1f" % (z0, z1)] = rows
    print("   z %5.1f..%4.1f  regions=%d  %s" % (z0, z1, len(rows), rows[:6]))
rep["bottom_slabs"] = slabs

t1 = time.time()
assy = cq.importers.importStep(str(OUT / "T06_shooter_assembly_R55_pollen.step")).val()
print("== 3. is the front skirt free of any other part at z < 3? (assembly) ==")
b = cq.Workplane("XY").box(400, 300, 9.0).translate((0, 0, -4.5+4.5-4.5+4.5)).val()
b = cq.Workplane("XY").box(400, 300, 7.0).translate((0, 0, -0.5)).val()
it = b.intersect(assy)
rows = []
for s in it.Solids():
    if s.Volume() > 0.5:
        g = s.BoundingBox()
        rows.append([round(g.xmin,1), round(g.xmax,1), round(g.ymin,1), round(g.ymax,1),
                     round(g.zmin,2), round(g.zmax,2), round(s.Volume(),1)])
print("   assembly z -4..3: %s" % rows)
rep["assembly_below_z3"] = rows
(OUT / "report_r55_print_probe.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
print("wrote report_r55_print_probe.json (%.0fs)" % (time.time()-t0))
