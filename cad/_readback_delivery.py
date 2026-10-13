# -*- coding: utf-8 -*-
"""Read back the delivered desktop STEP files (n_solids / volume / bbox)."""
from __future__ import annotations
import json, sys
from pathlib import Path
import cadquery as cq

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

rows = []
for p in sys.argv[1:]:
    w = cq.importers.importStep(p)
    shape = w.val()
    solids = shape.Solids()
    vol = 0.0
    for s in solids:
        vol += s.Volume()
    bb = shape.BoundingBox()
    rows.append({
        "file": Path(p).name,
        "n_solids": len(solids),
        "total_volume_mm3": round(vol, 3),
        "bbox_min_mm": [round(bb.xmin, 3), round(bb.ymin, 3), round(bb.zmin, 3)],
        "bbox_max_mm": [round(bb.xmax, 3), round(bb.ymax, 3), round(bb.zmax, 3)],
    })
    print(json.dumps(rows[-1], ensure_ascii=False), flush=True)

Path("cad/output/_motion_check/delivery_readback.json").write_text(
    json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")