# -*- coding: utf-8 -*-
import math, sys, importlib.util
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
for name in ("V0 现状", "R2"):
    r = ol.run(name, bx=145.0, fr=1.0, sec=14.0, rest=True, trace=True)
    tr = r["_trace"]
    print("== %s  最后采样:" % name, {k: tr[-1][k] for k in ("t","x","z","r","ang","v")})
    for s in tr[::700]:
        print("   t=%5.2f x=%8.2f z=%8.2f r=%6.1f ang=%6.1f v=%5.3f" % (s["t"], s["x"], s["z"], s["r"], s["ang"], s["v"]))
