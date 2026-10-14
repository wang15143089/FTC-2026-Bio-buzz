# -*- coding: utf-8 -*-
"""R53f delivery readback: re-open the STEP this round wrote and re-measure it.

Only reads; never writes over anything.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
OUT = HERE / "output" / "_r53f_lock"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

rows = {}
for name in ("pollen", "nectar"):
    rep = json.loads((OUT / ("report_r53f_%s.json" % name)).read_text(encoding="utf-8"))
    step = OUT / ("T06_shooter_assembly_R53f_%s.step" % name)
    t0 = time.time()
    shp = cq.importers.importStep(str(step)).val()
    sol = shp.Solids()
    bb = shp.BoundingBox()
    vols = [s.Volume() for s in sol]
    want_bbox = [round(min(p["bbox_mm"][i] for p in rep["parts"]), 2) for i in range(3)] + \
                [round(max(p["bbox_mm"][i + 3] for p in rep["parts"]), 2) for i in range(3)]
    want_vol = round(sum(p["volume_mm3"] for p in rep["parts"]), 1)
    got_bbox = [round(v, 2) for v in (bb.xmin, bb.ymin, bb.zmin,
                                      bb.xmax, bb.ymax, bb.zmax)]
    seats = [p for p in rep["parts"] if "clamp_seat" in p["part"]]
    rows[name] = {
        "step_mb": round(step.stat().st_size / 1e6, 1),
        "import_s": round(time.time() - t0, 1),
        "n_solids": len(sol),
        "n_parts_expected": rep["n_parts"],
        "volume_mm3_readback": round(sum(vols), 1),
        "volume_mm3_expected": want_vol,
        "volume_delta_pct": round(100.0 * (sum(vols) - want_vol) / want_vol, 4),
        "bbox_readback_mm": got_bbox,
        "bbox_expected_mm": want_bbox,
        "bbox_delta_mm": [round(a - b, 2) for a, b in zip(got_bbox, want_bbox)],
        "ring": {"count": len(seats), "od_mm": rep["seat"]["od_mm"],
                 "bore_mm": rep["seat"]["bore_mm"], "length_mm": rep["seat"]["length_mm"],
                 "volume_mm3_each": sorted(set(round(p["volume_mm3"], 2) for p in seats)),
                 "axial_mm": sorted(set(round(p["bbox_mm"][1], 2) for p in seats) |
                                    set(round(p["bbox_mm"][4], 2) for p in seats)),
                 "preload_n_per_stud": rep["seat"]["preload_n_per_stud_geometric"]},
        "nip_mm": rep["geometry"]["nip_mm"],
        "axle_isolation_hits": len(rep["axle_isolation_hits"]),
        "lock_vs_rest": len(rep["lock_vs_rest_clashes"]),
        "lock_vs_carriage": len(rep["lock_vs_carriage_clashes"]),
        "paddle_axis_mm": rep["geometry"]["paddle_axis_measured_mm"],
        "paddle_tip_to_lower_wheel_mm": rep["geometry"]["paddle_tip_to_lower_wheel_face_mm"],
    }
    print(name, json.dumps(rows[name], ensure_ascii=False), flush=True)

(OUT / "readback_r53f.json").write_text(
    json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
print("wrote", OUT / "readback_r53f.json")
