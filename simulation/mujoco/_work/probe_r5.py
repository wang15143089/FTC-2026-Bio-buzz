# -*- coding: utf-8 -*-
"""R2 vs R5 送球段轨迹/停位对比探针"""
import json, math, sys, time, importlib.util
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
V0S = ol.GEOM["V0 现状"][0]; FL = ol.GEOM["A 唇口喇叭"][0]; DP = ol.GEOM["D 球窝抬高6.8"][0]
ol.GEOM.update({
 "R2": (FL, th2((350.0,170.0))),
 "R5": (DP, th2((350.0,170.0))),
})
print("== 静止停位（拨杆不动，球从 x=145 滚入，采样末 20 点均值） ==")
for lab in ("V0 现状","R2","R5"):
    r = ol.run(lab, bx=145.0, fr=1.0, sec=5.0, rest=True, trace=True)
    tr = r["_trace"][-20:]
    x = sum(t["x"] for t in tr)/len(tr); z = sum(t["z"] for t in tr)/len(tr)
    rr = sum(t["r"] for t in tr)/len(tr); an = sum(t["ang"] for t in tr)/len(tr)
    print("  %-8s 球心(%.2f, %.2f)  r=%.2f  theta=%.2f  launched=%s" % (lab, x, z, rr, an, r["launched"]))
print()
print("== pad 台面 ==")
print("  tray_top_z(-2) = %.2f  pad top = %.2f  (x -17..13)" % (pv2.tray_top_z(-2.0), pv2.tray_top_z(-2.0)+6.8))
for lab, thr in (("R2",0.46),("R5",0.42)):
    r = ol.run(lab, bx=145.0, rpm=200.0, fr=thr+0.05, sec=7.0, trace=True)
    print()
    print("== %s @%.2f Nm 200rpm  launched=%s 出口 v=%.2f 角=%.1f ==" % (lab, thr+0.05, r["launched"], r.get("exit_speed",0), r.get("exit_angle",0)))
    for t in r["_trace"]:
        if t["t"] <= 2.2:
            print("   t=%.3f x=%8.2f z=%7.2f r=%7.2f th=%6.1f lx=%7.2f lz=%7.2f v=%.3f" % (
                t["t"], t["x"], t["z"], t["r"], t["ang"], t["lx"], t["lz"], t["v"]))
