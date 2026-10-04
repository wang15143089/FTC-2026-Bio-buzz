# -*- coding: utf-8 -*-
"""90 rpm 下 R2/R5 的真实扭矩需求"""
import json, sys, time, importlib.util
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
spec = importlib.util.spec_from_file_location("ol", r"simulation/mujoco/_work/opt_lib.py")
ol = importlib.util.module_from_spec(spec); spec.loader.exec_module(ol)
pv2 = ol.pv2; W = pv2.PADDLE_W
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
for lab, frs in (("R5", (0.40,0.42,0.44,0.46,0.48)), ("R2", (0.50,0.60,0.70,0.85,1.00))):
    rows = {}
    for fr in frs:
        st = [ol.run(lab, bx=bx, rpm=90.0, fr=fr)["launched"] for bx in (145.0,138.0)]
        rows[str(fr)] = st
        print("%s @90rpm fr=%.2f -> %s" % (lab, fr, st), flush=True)
    out[lab] = rows
Path("simulation/mujoco/out/_r2r5_at90.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("ok")
