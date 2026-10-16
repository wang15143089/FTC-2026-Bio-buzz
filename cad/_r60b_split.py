# -*- coding: utf-8 -*-
"""R60B: split T06_print_set_R60_pollen.step into one STEP per printed part.

Reads ONLY the delivered print-set STEP (no regeneration), maps each solid back
to its part name by a unique (volume, bbox) match against report_r60_pollen.json,
and writes one named STEP per part into cad/output/_r60b_parts/.
"""
import json
from pathlib import Path
import cadquery as cq

SRC_DIR = Path("cad/output/_r60_frame")
DST = Path("cad/output/_r60b_parts")
rep = json.loads((SRC_DIR / "report_r60_pollen.json").read_text(encoding="utf-8"))
src = SRC_DIR / rep["print_set_step"]["file"]
printed = list(rep["print_set"]["printed"])
rows = {p["part"]: p for p in rep["parts"] if p["part"] in set(printed)}
assert len(rows) == len(printed), (len(rows), len(printed))

solids = list(cq.importers.importStep(str(src)).val().Solids())
assert len(solids) == len(printed), (len(solids), len(printed))


def key(v, bb):
    return (round(v, 1), round(bb.xmin, 2), round(bb.xmax, 2),
            round(bb.ymin, 2), round(bb.ymax, 2), round(bb.zmin, 2), round(bb.zmax, 2))


def rkey(vol, bb):
    return (round(vol, 1), round(bb["x"][0], 2), round(bb["x"][1], 2),
            round(bb["y"][0], 2), round(bb["y"][1], 2),
            round(bb["z"][0], 2), round(bb["z"][1], 2))


lookup = {}
for n in printed:
    k = rkey(rows[n]["volume_mm3"], rows[n]["bbox"])
    assert k not in lookup, "duplicate key %s" % (k,)
    lookup[k] = n

DST.mkdir(parents=True, exist_ok=True)
for f in DST.glob("*.step"):
    f.unlink()

index = []
for s in solids:
    k = key(s.Volume(), s.BoundingBox())
    assert k in lookup, "no name match for %s" % (k,)
    n = lookup.pop(k)
    a = cq.Assembly(name=n)
    a.add(s, name="body", color=cq.Color(0.72, 0.74, 0.78, 1.0))
    p = DST / (n + ".step")
    a.export(str(p), exportType="STEP")
    index.append({"part": n, "file": p.name, "volume_mm3": round(s.Volume(), 1),
                  "bbox": {"x": [round(s.BoundingBox().xmin, 2), round(s.BoundingBox().xmax, 2)],
                           "y": [round(s.BoundingBox().ymin, 2), round(s.BoundingBox().ymax, 2)],
                           "z": [round(s.BoundingBox().zmin, 2), round(s.BoundingBox().zmax, 2)]},
                  "kb": round(p.stat().st_size / 1e3, 1)})
assert not lookup, "unmatched names: %s" % (list(lookup),)

# read every file back: must be exactly 1 solid with the same volume
bad = []
for e in index:
    b = cq.importers.importStep(str(DST / e["file"])).val().Solids()
    if len(b) != 1 or abs(b[0].Volume() - e["volume_mm3"]) > 0.2:
        bad.append((e["file"], len(b), round(sum(x.Volume() for x in b), 1)))

(DST / "parts_index.json").write_text(json.dumps(
    {"units": "mm", "source": src.name, "n_parts": len(index),
     "sum_volume_mm3": round(sum(e["volume_mm3"] for e in index), 1),
     "parts": sorted(index, key=lambda e: e["part"])},
    ensure_ascii=False, indent=1), encoding="utf-8")

print("wrote %d STEP files -> %s" % (len(index), DST))
print("sum V = %.1f mm3 (print set = %.1f)"
      % (sum(e["volume_mm3"] for e in index), rep["print_set_step"]["mb"] * 0))
print("readback failures:", bad if bad else "none (all 1 solid, volume match)")
print("largest:", sorted(index, key=lambda e: -e["volume_mm3"])[0]["part"],
      sorted(index, key=lambda e: -e["volume_mm3"])[0]["volume_mm3"])
for e in sorted(index, key=lambda e: e["part"]):
    print("  %-52s %9.1f mm3  %6.1f KB" % (e["part"], e["volume_mm3"], e["kb"]))
