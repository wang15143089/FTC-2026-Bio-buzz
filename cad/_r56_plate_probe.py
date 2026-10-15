# -*- coding: utf-8 -*-
import json, cadquery as cq
REP = "cad/output/_r56_frame/report_r56_pollen.json"
rep = json.load(open(REP, encoding="utf-8"))

print("=== parts whose bbox zmin < 8 (candidate ground contact) ===")
rows = []
for p in rep["parts"]:
    b = p["bbox"]
    rows.append((b["z"][0], p["part"], p["role"], b))
rows.sort()
for zmin, name, role, b in rows[:14]:
    print("zmin=%7.2f  %-34s %-8s x[%7.1f,%7.1f] y[%6.1f,%6.1f] z[%6.1f,%6.1f]"
          % (zmin, name, role, b["x"][0], b["x"][1], b["y"][0], b["y"][1], b["z"][0], b["z"][1]))

print()
print("=== rail tabs (frame members that bolt to base_rail) ===")
for m in rep["merged_into_frame"]["rail_tabs"]:
    print("  ", m)
for p in rep["parts"]:
    if "rail_tab" in p["part"]:
        b = p["bbox"]
        print("  %-30s x[%7.2f,%7.2f] y[%6.2f,%6.2f] z[%6.2f,%6.2f] V=%.1f"
              % (p["part"], b["x"][0], b["x"][1], b["y"][0], b["y"][1],
                 b["z"][0], b["z"][1], p["volume_mm3"]))
