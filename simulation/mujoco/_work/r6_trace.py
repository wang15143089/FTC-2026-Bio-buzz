# -*- coding: utf-8 -*-
"""R5 @90 rpm 运载段轨迹：球在什么半径上被带走。"""
import math, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import opt_lib as ol

pv2 = ol.pv2
def blades(angs, W=pv2.PADDLE_W):
    def f():
        parts = [("hub", (0., 0., 0.), (18., 17., 18.), 0., "cylY")]
        for i, a in enumerate(angs, 1):
            parts += [("arm_%d" % i, (30., 0, 0), (16., 9., 5.), a, "box"),
                      ("blade_%d" % i, (52., 0, 0), (6., W / 2., 15.), a, "box"),
                      ("flex_%d" % i, (58., 0, 0), (2., W / 2., 17.), a, "box")]
        return parts
    return f
def th2(ts):
    return blades([(360. - t) % 360. for t in ts])

ol.GEOM["R5"] = (ol.GEOM["D 球窝抬高6.8"][0], th2((350., 170.)))
r = ol.run("R5", bx=145.0, rpm=90.0, fr=1.0, sec=8.0, trace=True, fw=1620.0)
print("launched=%s peak=%.3f Nm" % (r["launched"], r["torque_peak_Nm"]))
print("t      x       z       r      ang    lx      lz     v")
for s in r["_trace"]:
    if abs(s["t"] * 10 - round(s["t"] * 10)) < 1e-6 and s["t"] <= 3.0:
        print("%.2f %7.2f %7.2f %6.2f %6.1f %7.1f %7.1f %5.2f" % (
            s["t"], s["x"], s["z"], s["r"], s["ang"], s["lx"], s["lz"], s["v"]))
print()
print("PADDLE_C=(%.2f,%.2f) R_CARRY=%.2f BALL_R=%.2f R_IN=%.2f R_OUT=%.2f" % (
    pv2.PADDLE_CX, pv2.PADDLE_CZ, pv2.R_CARRY, pv2.BALL_R, pv2.R_IN, pv2.R_OUT))
