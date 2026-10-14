# -*- coding: utf-8 -*-
"""R54: can the 4 bolt axes be moved outboard (y = +-74.5) clear of the side plate?"""
import sys
from pathlib import Path
import cadquery as cq
HERE = Path(__file__).resolve().parent
OUT = HERE / "output" / "_r54_frame"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
frame = cq.importers.importStep(str(OUT / "T06_shooter_frame_R54_pollen.step")).val()
assy = cq.importers.importStep(str(OUT / "T06_shooter_assembly_R54_pollen.step")).val()

def cyl(r, p0, d, h):
    return cq.Solid.makeCylinder(r, h, cq.Vector(*p0), cq.Vector(*d))

def scan(shape, axis, fixed, lo, hi, r, label):
    p0 = {"x": (lo, fixed[0], fixed[1]), "y": (fixed[0], lo, fixed[1]),
          "z": (fixed[0], fixed[1], lo)}[axis]
    d = {"x": (1,0,0), "y": (0,1,0), "z": (0,0,1)}[axis]
    i = "xyz".index(axis)
    rows = []
    for s in cyl(r, p0, d, hi-lo).intersect(shape).Solids():
        bb = s.BoundingBox()
        a = (bb.xmin, bb.ymin, bb.zmin)[i]; b = (bb.xmax, bb.ymax, bb.zmax)[i]
        if s.Volume() > 0.02:
            rows.append([round(a,2), round(b,2), round(s.Volume(),2)])
    rows.sort()
    print("  %-46s -> %s" % (label, rows))
    return rows

print("== vertical probe on candidate axis y=+-74.5 ==")
for x in (60.0, 76.0):
    for y in (74.5, -74.5):
        scan(frame, "z", (x, y), -6.0, 80.0, 0.3, "frame z @ x=%.0f y=%+.1f" % (x, y))
        scan(assy,  "z", (x, y), -20.0, 60.0, 0.3, "assy  z @ x=%.0f y=%+.1f" % (x, y))
print("== leg footprint at y=74.5 (x scan) ==")
for z in (20.0, 27.0, 40.0, 44.0, 47.0):
    scan(frame, "x", (74.5, z), 40.0, 100.0, 0.3, "frame x @ y=74.5 z=%.0f" % z)
print("== how far outboard is the free channel? y scan at x=60/76 ==")
for x, z in ((60.0, 40.0), (60.0, 27.0), (76.0, 40.0), (76.0, 20.0)):
    scan(frame, "y", (x, z), 40.0, 110.0, 0.3, "frame y @ x=%.0f z=%.0f" % (x, z))
print("== plate lower edge (V) near the legs: y=70 axis, x scan ==")
for z in (36.0, 38.0, 40.0):
    scan(frame, "x", (70.0, z), 40.0, 100.0, 0.3, "frame x @ y=70 z=%.0f" % z)
