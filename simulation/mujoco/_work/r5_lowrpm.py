# -*- coding: utf-8 -*-
"""R5 low-rpm requirement upper bound (30-75 rpm), dual entry."""
import json, sys, time, importlib.util
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
spec = importlib.util.spec_from_file_location("ol", r"simulation/mujoco/_work/opt_lib.py")
ol = importlib.util.module_from_spec(spec); spec.loader.exec_module(ol)
pv2 = ol.pv2; W = pv2.PADDLE_W
T0 = time.time()
def blades(angs):
    def f():
        parts = [("hub", (0.0,0.0,0.0), (18.0,17.0,18.0), 0.0, "cylY")]
        for i, a in enumerate(angs, 1):
            parts.append(("arm_%d"%i,   (30.0,0.0,0.0), (16.0, 9.0, 5.0), a, "box"))
            parts.append(("blade_%d"%i, (52.0,0.0,0.0), (6.0, W/2.0, 15.0), a, "box"))
            parts.append(("flex_%d"%i,  (58.0,0.0,0.0), (2.0, W/2.0, 17.0), a, "box"))
        return parts
    return f
def th2(ts): return blades([(360.0-t) % 360.0 for t in ts])
FL = ol.GEOM["A 唇口喇叭"][0]; DP = ol.GEOM["D 球窝抬高6.8"][0]
ol.GEOM.update({"R5": (DP, th2((350.0,170.0))), "R2": (FL, th2((350.0,170.0)))})
def d(lab, rpm, fr):
    return [bool(ol.run(lab, bx=bx, rpm=rpm, fr=fr)["launched"]) for bx in (145.0, 138.0)]
res = {}
for rpm in (30.0, 40.0, 50.0, 60.0, 70.0):
    res[str(int(rpm))] = {}
    for fr in (0.95, 1.30, 1.70, 2.20, 3.00):
        st = d("R5", rpm, fr)
        res[str(int(rpm))][str(fr)] = st
        print("R5 @%3d rpm fr=%.2f -> %s  [%.0fs]" % (rpm, fr, st, time.time()-T0), flush=True)
    Path("simulation/mujoco/out/_r5_lowrpm.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
print("done %.0fs" % (time.time()-T0))