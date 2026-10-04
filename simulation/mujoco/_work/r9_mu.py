# -*- coding: utf-8 -*-
"""R9: ball-friction ladder with peak-time, plus a 0.4 trace sanity dump."""
import math, sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import r9_nest as R
import opt_lib as ol
import numpy as np

base = ol.GEOM["D 球窝抬高6.8"][0]
out = {}
print("=== R9 ball-friction ladder (base nest, pocket start, 8 s, 25-4 @290 rpm) ===")
for mu in (1.0, 0.8, 0.7, 0.6, 0.55, 0.5, 0.45, 0.4, 0.35, 0.3):
    res = R.run("mu=%.2f" % mu, base, mu_ball=mu)
    vmax = max(s["v"] for s in res["_trace"])
    print("        peak_v=%.2f m/s at t=%.3f s   final_r=%.1f mm  max_lx=%.1f mm"
          % (vmax, res["peak_speed_t"], res["_trace"][-1]["r"], res["max_lx_mm"]), flush=True)
    out["mu%g" % mu] = {k: v for k, v in res.items() if k != "_trace"}

Path("simulation/mujoco/out/_r9_mu.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

print()
print("=== mu=0.4 trace around the speed peak (every 20 ms) ===")
res = out["mu0.4"]
tr = R.run("mu=0.4 redo", base, mu_ball=0.4, quiet=True)["_trace"]
pk = max(range(len(tr)), key=lambda i: tr[i]["v"])
for i in range(max(0, pk - 12), min(len(tr), pk + 8)):
    s = tr[i]
    print("   t=%.3f x=%8.2f z=%7.2f r=%6.2f ang=%7.2f v=%7.2f vx=%7.2f vz=%7.2f lx=%7.1f"
          % (s["t"], s["x"], s["z"], s["r"], s["ang"], s["v"], s["vx"], s["vz"], s["lx"]))
print("  saved simulation/mujoco/out/_r9_mu.json")
