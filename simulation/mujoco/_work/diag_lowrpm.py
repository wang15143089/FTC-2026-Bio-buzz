# -*- coding: utf-8 -*-
"""Long-run diagnosis: why do 30/40/60/70 rpm fail while 50 rpm passes?"""
import sys, importlib.util
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
DP = ol.GEOM["D 球窝抬高6.8"][0]
ol.GEOM.update({"R5": (DP, th2((350.0,170.0)))})
for rpm in (50.0, 60.0, 70.0, 40.0):
    for bx in (145.0,):
        r = ol.run("R5", bx=bx, rpm=rpm, fr=2.0, sec=12.0, trace=True)
        tr = r["_trace"]
        deep = [s for s in tr if s["r"] < 100.0]
        print("=== rpm=%.0f bx=%.0f fr=2.0 sec=12 ===" % (rpm, bx), flush=True)
        print("  launched=%s nip=%s exit142=%s peak_v=%.2f minang=%.0f" % (
            r["launched"], r["passed_nip"], r["reached_142deg_exit"], r["peak_speed_m_s"], r["min_angle_deg"]), flush=True)
        print("  n_deep=%d  t_first_deep=%.2f  final=%s" % (
            len(deep), deep[0]["t"] if deep else -1, r["final_mm"]), flush=True)
        sel = [s for s in tr if s["t"] < 6.0][::150]
        for s in sel:
            print("    t=%5.2f r=%6.1f ang=%6.1f v=%5.2f" % (s["t"], s["r"], s["ang"], s["v"]), flush=True)