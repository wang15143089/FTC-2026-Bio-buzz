# -*- coding: utf-8 -*-
"""Read back the delivered R50 STEP and re-measure the key parts."""
import json
import sys
import time
from pathlib import Path

import cadquery as cq

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

path = Path.home() / "OneDrive" / "Desktop" / "T06_shooter_drive_R50_pollen.step"
if len(sys.argv) > 1:
    path = Path(sys.argv[1])

t0 = time.time()
assy = cq.Assembly.load(str(path))
print("loaded %s in %.1f s, %d children" % (path.name, time.time() - t0,
                                            len(assy.children)), flush=True)

rows = []
for ch in assy.children:
    name, shape = ch.name, ch.obj
    bb = shape.BoundingBox()
    rows.append({
        "part": name,
        "volume_mm3": round(float(shape.Volume()), 1),
        "bbox_mm": [round(v, 2) for v in (bb.xmin, bb.ymin, bb.zmin,
                                          bb.xmax, bb.ymax, bb.zmax)],
    })
    print("  %-52s %s" % (name, rows[-1]["bbox_mm"]), flush=True)

out = Path("cad/output/_r50_drive/delivery_readback.json")
out.write_text(json.dumps({"source": str(path), "n_parts": len(rows),
                           "parts": rows}, indent=2, ensure_ascii=False),
               encoding="utf-8")
print("readback -> %s (%.1f s)" % (out, time.time() - t0), flush=True)
