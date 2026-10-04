# -*- coding: utf-8 -*-
"""mu=0.40 with a rear wall so the ball cannot escape off the tray end."""
import math, sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import r6_smooth as r6
import r9_tray as T
import opt_lib as ol

STAT_R5, PART_R5 = ol.GEOM["R5"]
wall = lambda: list(STAT_R5()) + [T.wall()]

out = {}
print("=== mu=0.40, R5 + rear wall at x=153 ===")
for bx in (145.0, 125.0):
    out["wall_bx%d" % bx] = T.run("bx=%.0f + wall" % bx, wall, PART_R5, bx, 0.40)
print("--- mu=1.00 + wall (control) ---")
out["wall_mu1"] = T.run("mu1.00 + wall", wall, PART_R5, 145.0, 1.00)
Path("simulation/mujoco/out/_r9_wall.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("  saved")
