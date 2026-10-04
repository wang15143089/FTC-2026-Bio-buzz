import sys, json, math
from pathlib import Path
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass
import cadquery as cq
p = Path("cad/output/paddle_launcher_motion_free_fingers_pollen.step")
s = cq.importers.importStep(str(p))
solids = s.solids().vals()
print("solids:", len(solids))
rows = []
for i, sol in enumerate(solids):
    bb = sol.BoundingBox()
    rows.append((i, round(bb.xmin,2), round(bb.xmax,2), round(bb.zmin,2), round(bb.zmax,2), sol.Volume()))
for r in rows:
    print(r)
