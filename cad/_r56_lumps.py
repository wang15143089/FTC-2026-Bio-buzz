# -*- coding: utf-8 -*-
"""R56 frame cut at x=100 / z=300 -> list EVERY printable lump with its bbox."""
import time
from pathlib import Path
import cadquery as cq

FRAME = Path("cad/output/_r56_frame/T06_shooter_frame_R56_pollen.step")
CUT_X, CUT_Z = 100.0, 300.0
BIG = 2000.0

t0 = time.time()
frame = cq.importers.importStep(str(FRAME)).val()
b = frame.BoundingBox()
print("R56 frame x[%.2f,%.2f] y[%.2f,%.2f] z[%.2f,%.2f] V=%.0f solids=%d"
      % (b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax, frame.Volume(), len(frame.Solids())), flush=True)

def half(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1-x0, y1-y0, z1-z0, centered=False).translate((x0, y0, z0)).val()

pieces = {
    "P1_rear_lower":  frame.intersect(half(CUT_X-BIG, CUT_X, -BIG/2, BIG/2, -BIG/2, CUT_Z)),
    "P2_front_lower": frame.intersect(half(CUT_X, CUT_X+BIG, -BIG/2, BIG/2, -BIG/2, CUT_Z)),
    "P3_top":         frame.intersect(half(CUT_X-BIG, CUT_X+BIG, -BIG/2, BIG/2, CUT_Z, CUT_Z+BIG)),
}
for n, p in pieces.items():
    pb = p.BoundingBox()
    print("\n== %s  dims %.1f x %.1f x %.1f  V=%.0f  lumps=%d"
          % (n, pb.xmax-pb.xmin, pb.ymax-pb.ymin, pb.zmax-pb.zmin, p.Volume(), len(p.Solids())), flush=True)
    for i, s in enumerate(p.Solids()):
        q = s.BoundingBox()
        print("   lump %d V=%9.1f  x[%7.1f,%7.1f] y[%6.1f,%6.1f] z[%7.1f,%7.1f]  (%.1f x %.1f x %.1f)"
              % (i, s.Volume(), q.xmin, q.xmax, q.ymin, q.ymax, q.zmin, q.zmax,
                 q.xmax-q.xmin, q.ymax-q.ymin, q.zmax-q.zmin), flush=True)
print("\nelapsed %.1fs" % (time.time()-t0), flush=True)
