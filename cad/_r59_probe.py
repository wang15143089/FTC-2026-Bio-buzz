# -*- coding: utf-8 -*-
import sys, json
from pathlib import Path
HERE = Path("cad").resolve()
sys.path.insert(0, str(HERE))
import cadquery as cq
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import paddle_launcher_constrained as K

f = cq.importers.importStep(str(HERE/"output"/"_r57_frame"/"T06_shooter_frame_R57_pollen.step")).val()
bb = f.BoundingBox()
print("frame bbox x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f V=%.1f solids=%d"
      % (bb.xmin,bb.xmax,bb.ymin,bb.ymax,bb.zmin,bb.zmax,f.Volume(),len(f.Solids())))

def probe(tag, dx,dy,dz, c):
    b = K.box(dx,dy,dz,c)
    v = f.intersect(b).Volume()
    print("%-28s V=%.4f mm3   box x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f"
          % (tag, v, c[0]-dx/2, c[0]+dx/2, c[1]-dy/2, c[1]+dy/2, c[2]-dz/2, c[2]+dz/2))
    return v

# candidate sole region under each rail (y +-72, x -170..210, z SOLE_ZB..2)
for y in (72.0, -72.0):
    probe("sole-region y=%+.0f" % y, 380.0, 18.0, 9.0, (20.0, y, -2.5))
# wider safety: whole new rail envelope z -8..2
for y in (72.0, -72.0):
    probe("envelope z-8..2 y=%+.0f" % y, 380.0, 18.0, 10.0, (20.0, y, -3.0))
# lower still, to find how much room we have
probe("all-z below -7 slab", 900.0, 900.0, 4.0, (30.0, 0.0, -9.0))
probe("all-z below -3.6 slab", 900.0, 900.0, 4.0, (30.0, 0.0, -5.6))
# where is the tray underside exactly
for x0 in (10.0, 20.0, 30.0, 40.0, 50.0):
    probe("tray under x=%.0f" % x0, 4.0, 120.0, 12.0, (x0, 0.0, -5.0))
