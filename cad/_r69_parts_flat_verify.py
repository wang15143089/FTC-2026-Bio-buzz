import json, glob, os
from pathlib import Path
import cadquery as cq

PKG = Path(r"C:\FTC design\FTC 2026 biobuzz\deliverables\R69_print_package")
idx = json.loads((PKG/"parts_flat_index.json").read_text(encoding="utf-8"))
bad=[]
for r in idx["parts"]:
    p = PKG/"parts_flat"/r["file"]
    s = cq.importers.importStep(str(p)).val()
    sol = s.Solids()
    b = s.BoundingBox()
    ok = (len(sol)==1 and abs(b.zmin)<1e-3 and b.zlen<=325.0
          and b.xlen<=315.0 and b.ylen<=310.0
          and abs(sum(x.Volume() for x in sol)-r["volume_mm3"])<1.0)
    if not ok:
        bad.append((r["file"], len(sol), round(b.xmin,3), round(b.zmin,3), round(b.xlen,1), round(b.ylen,1), round(b.zlen,1)))
print("files", len(idx["parts"]), "bad", bad)
print("sum volume %.1f" % sum(r["volume_mm3"] for r in idx["parts"]))
