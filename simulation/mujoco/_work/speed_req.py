# -*- coding: utf-8 -*-
"""R5/R2 门槛随拨杆转速的变化（用于对比舵机线性扭矩-转速包络）"""
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
ol.GEOM.update({"R2": (FL, th2((350.0,170.0))), "R5": (DP, th2((350.0,170.0)))})
out = {}
for lab in ("R5","R2"):
    out[lab] = {}
    for rpm in (90.0, 120.0, 150.0, 200.0, 250.0, 290.0, 330.0):
        thr = ol.threshold(lab, rpm=rpm)[0]
        out[lab][str(int(rpm))] = thr
        print("%s @%3d rpm 门槛 = %s N·m   [%.0fs]" % (lab, rpm, thr, time.time()-T0), flush=True)
Path("simulation/mujoco/out/_r2r5_speed_req.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("done")
