import sys, json
import cadquery as cq
p = r"cad/output/paddle_launcher_motion_free_fingers_pollen.step"
s = cq.importers.importStep(p)
shapes = s.solids().vals()
print("SOLIDS", len(shapes))
rows = []
for i, sh in enumerate(shapes):
    bb = sh.BoundingBox()
    try:
        nm = sh.label
    except Exception:
        nm = ""
    rows.append((nm, i, round(sh.Volume()/1000.0, 3),
                 (round(bb.xmin,1), round(bb.xmax,1)),
                 (round(bb.ymin,1), round(bb.ymax,1)),
                 (round(bb.zmin,1), round(bb.zmax,1)),
                 round(bb.xlen,1), round(bb.ylen,1), round(bb.zlen,1)))
for r in sorted(rows, key=lambda r: -r[2]):
    print(json.dumps({"name": r[0], "i": r[1], "vol_cm3": r[2], "x": r[3], "y": r[4], "z": r[5], "len": r[6:]}))
