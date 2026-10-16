# -*- coding: utf-8 -*-
"""R61 probe: where can the left/right base rails be tied together by ribs?

Envelope of a candidate rib: y -66..66 (bites 3 mm into each 18 mm rail),
z -10..16 (full rail+sole section).  Nothing else may occupy it.
"""
import json, io, sys
from pathlib import Path
import cadquery as cq

OUT = Path("cad/output/_r60_frame")
idx = json.load(io.open("cad/output/_r60b_parts/parts_index.json", encoding="utf-8"))
low = [(p["part"], p["bbox"]["z"][0], p["bbox"]["z"][1]) for p in idx["parts"]
       if p["bbox"]["z"][0] < 16.0]
print("printed bodies whose zmin < 16:")
for n, z0, z1 in sorted(low, key=lambda r: r[1]):
    print("   %-34s z %.2f..%.2f" % (n, z0, z1))

rep = json.load(io.open(OUT / "report_r60_pollen.json", encoding="utf-8"))
print("other bodies (COTS incl.) whose zmin < 16:")
for r in rep["parts"]:
    if r["bbox"]["z"][0] < 16.0 and not r["part"].startswith("base_rail"):
        print("   %-34s z %.2f..%.2f  %s" % (r["part"], r["bbox"]["z"][0],
                                             r["bbox"]["z"][1], r["role"]))

frame = cq.importers.importStep(str(OUT / "T06_shooter_frame_R60_pollen.step")).val()
print("frame V=%.1f" % frame.Volume(), flush=True)

def box(x0, x1):
    b = cq.Workplane("XY").box(x1 - x0, 132.0, 26.0, centered=False)
    return b.translate((x0, -66.0, -10.0)).val()

rows = []
for x in range(-170, 210, 10):
    v = box(float(x), float(x + 10.0)).intersect(frame).Volume()
    rows.append((x, round(v, 2)))
print("frame volume in rib envelope, 10 mm x-slices (x0, mm3):")
for i in range(0, len(rows), 6):
    print("   " + "  ".join("%5d:%-7.2f" % r for r in rows[i:i + 6]))
clear = [r for r in rows if r[1] < 0.01]
print("slices with 0 mm3: %d of %d" % (len(clear), len(rows)))
# contiguous clear runs
runs, cur = [], []
for x, v in rows:
    if v < 0.01:
        cur.append(x)
    else:
        if len(cur) >= 2:
            runs.append((cur[0], cur[-1] + 10.0))
        cur = []
if len(cur) >= 2:
    runs.append((cur[0], cur[-1] + 10.0))
print("clear x runs (>=20 mm):", runs)
json.dump({"rows": rows, "runs": runs},
          io.open("cad/output/_r61_rib_probe.json", "w", encoding="utf-8"), indent=1)
