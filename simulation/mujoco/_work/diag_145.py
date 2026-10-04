# -*- coding: utf-8 -*-
"""Diagnose R5 at 145 rpm (anomalous failure) and low-rpm requirement."""
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
FL = ol.GEOM["A 唇口喇叭"][0]; DP = ol.GEOM["D 球窝抬高6.8"][0]
ol.GEOM.update({"R2": (FL, th2((350.0,170.0))), "R5": (DP, th2((350.0,170.0)))})

print("=== R5 @145 rpm, varying torque limit ===", flush=True)
for fr in (0.6, 1.0, 1.6, 2.4):
    r = ol.run("R5", bx=145.0, rpm=145.0, fr=fr, trace=True)
    print("fr=%.1f launched=%s entered=%s nip=%s exit142=%s peak_v=%.2f max_lx=%.1f minang=%.1f final=%s"
          % (fr, r["launched"], r["entered_shell"], r["passed_nip"], r["reached_142deg_exit"],
             r["peak_speed_m_s"], r["max_lx_mm"], r["min_angle_deg"], r["final_mm"]), flush=True)
    tr = r["_trace"]
    sel = [s for s in tr if s["t"] <= 2.5][::40]
    for s in sel:
        print("    t=%5.2f r=%6.1f ang=%6.1f v=%5.2f lx=%7.1f" % (s["t"], s["r"], s["ang"], s["v"], s["lx"]), flush=True)
print("=== control R5 @200 rpm fr=1.0 ===", flush=True)
r = ol.run("R5", bx=145.0, rpm=200.0, fr=1.0, trace=True)
print("launched=%s entered=%s nip=%s exit142=%s peak_v=%.2f max_lx=%.1f" % (
    r["launched"], r["entered_shell"], r["passed_nip"], r["reached_142deg_exit"], r["peak_speed_m_s"], r["max_lx_mm"]), flush=True)
for s in [s for s in r["_trace"] if s["t"] <= 1.5][::30]:
    print("    t=%5.2f r=%6.1f ang=%6.1f v=%5.2f lx=%7.1f" % (s["t"], s["r"], s["ang"], s["v"], s["lx"]), flush=True)