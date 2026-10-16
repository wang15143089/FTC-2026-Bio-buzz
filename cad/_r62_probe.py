# -*- coding: utf-8 -*-
"""R62 probe: where can a connector between the two rails live for x > -40 ?

The rails sit at y = +-72 (y 63..81). Everything between them (|y| < 63) for
x >= -40 is suspected to be taken by the merged frame's bottom web.  Slice the
frame in z inside that gap and report the free bands.
"""
import json
from pathlib import Path
import cadquery as cq

OUT = Path("cad/output/_r61_frame")
fr = cq.importers.importStep(str(OUT / "T06_shooter_frame_R61_pollen.step")).val()
bb = fr.BoundingBox()
print("frame bbox x[%.2f,%.2f] y[%.2f,%.2f] z[%.2f,%.2f] V=%.0f"
      % (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax, fr.Volume()))


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0).translate(
        ((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0)).val()


res = {"units": "mm", "gap_z_slices": [], "rib_candidates": []}

# 1. z slices inside the between-rails gap, x -40..286, |y| <= 62
z = -10.0
while z < 20.0:
    v = box(-40.0, 286.0, -62.0, 62.0, z, z + 0.5).intersect(fr).Volume()
    if v > 0.5:
        # x extent of that material
        sub = box(-40.0, 286.0, -62.0, 62.0, z, z + 0.5).intersect(fr)
        sb = sub.BoundingBox()
        res["gap_z_slices"].append({"z": [z, z + 0.5], "mm3": round(v, 1),
                                    "x": [round(sb.xmin, 1), round(sb.xmax, 1)],
                                    "y": [round(sb.ymin, 1), round(sb.ymax, 1)]})
        print("  z %6.1f..%6.1f  V=%9.1f  x[%.1f,%.1f] y[%.1f,%.1f]"
              % (z, z + 0.5, v, sb.xmin, sb.xmax, sb.ymin, sb.ymax))
    z += 0.5

print()
# 2. candidate top-rib boxes (10 wide in x, y +-66, z band) vs the frame
for x in (-40.0, -20.0, 0.0, 20.0, 40.0, 60.0, 80.0, 100.0, 120.0, 140.0,
          160.0, 180.0, 200.0):
    for z0, z1 in ((2.0, 16.0), (3.0, 16.0), (2.5, 15.0), (-10.0, 16.0)):
        v = box(x - 5.0, x + 5.0, -66.0, 66.0, z0, z1).intersect(fr).Volume()
        row = {"x": x, "z": [z0, z1], "mm3": round(v, 3),
               "free": v < 0.5}
        res["rib_candidates"].append(row)
        print("  rib x=%6.1f z %6.1f..%5.1f  frame=%9.3f mm3  %s"
              % (x, z0, z1, v, "FREE" if v < 0.5 else "clash"))

Path("cad/output/_r62_probe.json").write_text(
    json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
print("\nwritten cad/output/_r62_probe.json")
