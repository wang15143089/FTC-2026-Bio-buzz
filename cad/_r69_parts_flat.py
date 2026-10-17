# -*- coding: utf-8 -*-
"""R69: re-export every printable part as its own single-solid, bed-flat STEP.

Source of truth: the finished plate STEPs (already baked, verified in R69).
Bambu Studio imports a multi-solid STEP as one object and then complains about
the group bounding box, so we also hand out one file per part, min-Z = 0,
centred on the origin.
"""
import json, shutil
from pathlib import Path
import cadquery as cq

ROOT = Path(r"C:\FTC design\FTC 2026 biobuzz")
PKG = ROOT / "deliverables" / "R69_print_package"
PLATES = PKG / "plates"
OUT = PKG / "parts_flat"
OUT.mkdir(parents=True, exist_ok=True)

idx = json.loads((PKG / "plates_index.json").read_text(encoding="utf-8"))

def dims(b):
    return sorted([b.xlen, b.ylen, b.zlen])

rows = []
missing = []
for plate in idx["plates"]:
    step = PLATES / plate["step"]
    shape = cq.importers.importStep(str(step)).val()
    solids = list(shape.Solids())
    pool = []
    for s in solids:
        b = s.BoundingBox()
        pool.append({"s": s, "v": s.Volume(), "d": dims(b), "b": b})

    for obj in plate["objects"]:
        v = obj["volume_mm3"]
        fd = sorted([obj["footprint_mm"][0], obj["footprint_mm"][1], obj["height_mm"]])
        best, bestscore = None, 1e18
        for e in pool:
            score = abs(e["v"] - v) * 20.0 + sum(abs(e["d"][i] - fd[i]) for i in range(3))
            if score < bestscore:
                best, bestscore = e, score
        if best is None or abs(best["v"] - v) > 1.0:
            missing.append((plate["plate"], obj["object"], v))
            continue
        pool.remove(best)

        b = best["b"]
        cx, cy = (b.xmin + b.xmax) / 2.0, (b.ymin + b.ymax) / 2.0
        flat = best["s"].translate((-cx, -cy, -b.zmin))
        fb = flat.BoundingBox()
        path = OUT / (obj["object"] + ".step")
        cq.exporters.export(flat, str(path))

        rows.append({"object": obj["object"], "group": obj["group"],
                     "plate": plate["plate"], "file": path.name,
                     "volume_mm3": round(flat.Volume(), 1),
                     "bbox_mm": [round(fb.xlen, 2), round(fb.ylen, 2), round(fb.zlen, 2)],
                     "zmin_mm": round(fb.zmin, 4)})

print("exported", len(rows), "parts; missing", missing)
print("max height", max(r["bbox_mm"][2] for r in rows))
print("max footprint", max(max(r["bbox_mm"][0], r["bbox_mm"][1]) for r in rows))
bad = [r for r in rows if r["zmin_mm"] < -1e-3 or r["bbox_mm"][2] > 325.0
       or r["bbox_mm"][0] > 315.0 or r["bbox_mm"][1] > 310.0]
print("out of bed:", bad)
(PKG / "parts_flat_index.json").write_text(json.dumps(
    {"units": "mm", "what": "R69 printable parts, one single solid per file, laid flat, min-Z = 0, centred on XY origin",
     "source": "deliverables/R69_print_package/plates (finished R69 plate STEPs)",
     "bed_limit_mm": [315.0, 310.0, 325.0], "n_parts": len(rows), "parts": rows},
    ensure_ascii=False, indent=1), encoding="utf-8")
