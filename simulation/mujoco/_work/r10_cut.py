# -*- coding: utf-8 -*-
"""R10b: remove the tray under the wedge zone so the ball can fall into the cradle."""
import math, sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import r6_smooth as r6
import opt_lib as ol
import r10_cradle as R10

res = {}
print("=== tray cut back (remove wedge support), lip=292, mu=0.40, 12 s ===")
for cx in (95.0, 110.0, 118.0, 126.0):
    g = R10.make_geom(cx, 292.0)
    res["cut%g" % cx] = R10.run("cut%g lip292" % cx, g, mu=0.40, sec=12.0)
    t = res["cut%g" % cx]["_trace"]
    key = [s for s in t if s["t"] >= 1.0]
    print("      after t=1s: r range %.1f..%.1f  ang range %.1f..%.1f  final=(%.0f,%.0f)  minz=%.1f"
          % (min(s["r"] for s in key), max(s["r"] for s in key),
             min(s["ang"] for s in key), max(s["ang"] for s in key),
             res["cut%g" % cx]["final_mm"][0], res["cut%g" % cx]["final_mm"][1],
             min(s["z"] for s in t)), flush=True)
Path("simulation/mujoco/out/_r10_cut.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
print("saved")
