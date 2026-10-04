# -*- coding: utf-8 -*-
import math, sys, json, importlib.util
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
ol.GEOM["R2"] = (ol.GEOM["A 唇口喇叭"][0], blades([10.0, 190.0]))
r = ol.run("R2", bx=145.0, rpm=200.0, fr=1.5, sec=7.0, trace=True)
tr = r["_trace"]
print("launched:", r["launched"], " exit:", r.get("exit"))
print("路径采样（球心，世界坐标；θ 为相对拨杆轴心的极角）：")
for s in tr[::150]:
    print("  t=%5.2f x=%8.2f z=%8.2f r=%6.1f ang=%6.1f v=%5.2f" % (s["t"], s["x"], s["z"], s["r"], s["ang"], s["v"]))
json.dump(tr, open(r"simulation/mujoco/out/trace_section_R2_1p5.json","w",encoding="utf-8"))
