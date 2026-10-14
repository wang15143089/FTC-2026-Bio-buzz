# -*- coding: utf-8 -*-
"""R53f vs R53b, part by part: prove that only the 16 clamp seats were added.

Baseline : cad/output/_r53b_auto/report_r53b_<variant>.json    (the real R53b run)
New      : cad/output/_r53f_lock/report_r53f_<variant>.json   (R53f, rings added)

Careful: cad/output/_r53f_lock/report_r53f_deps_r53b_module_<variant>.json is a
by-product that the R53b module writes while R53f runs. It is NOT the baseline
(it already carries the 16 rings). It was renamed this round so that nobody
reads it as a baseline again.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "output" / "_r53f_lock"
BASE = HERE / "output" / "_r53b_auto"

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def index(rep):
    return {p["part"]: p for p in rep["parts"]}


def box(parts):
    return [round(min(p["bbox_mm"][i] for p in parts.values()), 2) for i in range(3)] + \
           [round(max(p["bbox_mm"][i + 3] for p in parts.values()), 2) for i in range(3)]


res = {}
for name in ("pollen", "nectar"):
    b = json.loads((BASE / ("report_r53b_%s.json" % name)).read_text(encoding="utf-8"))
    f = json.loads((OUT / ("report_r53f_%s.json" % name)).read_text(encoding="utf-8"))
    bi, fi = index(b), index(f)

    added_names = sorted(set(fi) - set(bi))
    removed_names = sorted(set(bi) - set(fi))
    moved = []
    for k in sorted(set(bi) & set(fi)):
        dv = round(fi[k]["volume_mm3"] - bi[k]["volume_mm3"], 4)
        db = [round(fi[k]["bbox_mm"][i] - bi[k]["bbox_mm"][i], 4) for i in range(6)]
        if abs(dv) > 1e-3 or max(abs(x) for x in db) > 1e-3:
            moved.append({"part": k, "d_volume_mm3": dv, "d_bbox_mm": db})

    bb, bf = box(bi), box(fi)
    rings = [fi[k] for k in added_names if "clamp_seat" in k]
    res[name] = {
        "baseline": "cad/output/_r53b_auto/report_r53b_%s.json" % name,
        "new": "cad/output/_r53f_lock/report_r53f_%s.json" % name,
        "n_parts_base": b["n_parts"],
        "n_parts_new": f["n_parts"],
        "added": added_names,
        "added_count": len(added_names),
        "added_all_are_seats": bool(added_names) and len(rings) == len(added_names),
        "added_volume_mm3": sorted({round(r["volume_mm3"], 2) for r in rings}),
        "removed": removed_names,
        "moved": moved,
        "moved_count": len(moved),
        "bbox_base_mm": bb,
        "bbox_new_mm": bf,
        "bbox_delta_max_mm": round(max(abs(bf[i] - bb[i]) for i in range(6)), 4),
        "seat_count": len(rings),
        "verdict": ("除 16 件限位环外，R53b 的每一件几何与位置完全未变"
                    if not removed_names and not moved and len(rings) == len(added_names) == 16
                    else "存在未预期的差异，需要人工核查"),
    }
    print("[%s] +%d / -%d / moved %d  bbox delta %.4f  %s"
          % (name, res[name]["added_count"], len(removed_names), len(moved),
             res[name]["bbox_delta_max_mm"], res[name]["verdict"]))

doc = {
    "note": "R53f 逐件对比：基线取自 _r53b_auto（真 R53b），不是 _r53f_lock 里的同名副产物。",
    "tool": "cad/_r53f_compare_base.py",
    "variants": res,
}
p = OUT / "compare_r53f_vs_r53b.json"
p.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
print("wrote", p)
