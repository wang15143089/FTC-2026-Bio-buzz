# -*- coding: utf-8 -*-
"""R60 probe: how far DOWN can the base-rail sole go before it hits the frame?

Reads the R59 (final) frame STEP and intersects slabs of the region the new
sole will occupy.  Anything > 0.0000 mm3 in x -170..210, y +-63..81 means the
sole would have to be relieved there.
"""
import sys
from pathlib import Path
HERE = Path("cad").resolve()
sys.path.insert(0, str(HERE))
import cadquery as cq
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import paddle_launcher_constrained as K

f = cq.importers.importStep(
    str(HERE / "output" / "_r59_frame" / "T06_shooter_frame_R59_pollen.step")).val()
bb = f.BoundingBox()
print("frame bbox x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f V=%.1f solids=%d"
      % (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax,
         f.Volume(), len(f.Solids())))


def slab(tag, dx, dy, dz, c):
    b = K.box(dx, dy, dz, c)
    v = f.intersect(b).Volume()
    print("%-32s V=%.4f mm3   x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f"
          % (tag, v, c[0] - dx / 2, c[0] + dx / 2, c[1] - dy / 2, c[1] + dy / 2,
             c[2] - dz / 2, c[2] + dz / 2))
    return v


print("--- 2 mm slabs under each rail, z = -14 .. +2 ---")
tot = 0.0
for y in (72.0, -72.0):
    for zb in range(-14, 2, 2):
        tot += slab("y=%+.0f z[%d..%d]" % (y, zb, zb + 2), 380.0, 18.0, 2.0,
                    (20.0, y, zb + 1.0))
print("TOTAL rail-envelope interference = %.4f mm3" % tot)

print("--- 1 mm slabs, whole machine footprint below z=-3 ---")
for zb in range(-14, -2):
    slab("all x/y z[%d..%d]" % (zb, zb + 1), 900.0, 900.0, 1.0, (30.0, 0.0, zb + 0.5))
