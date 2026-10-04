# -*- coding: utf-8 -*-
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
DP = ol.GEOM["D 球窝抬高6.8"][0]
ol.GEOM.update({"R5": (DP, th2((350.0,170.0)))})
SEC = 12.0
def dual_ok(rpm, fr):
    return all(bool(ol.run("R5", bx=bx, rpm=rpm, fr=fr, sec=SEC)["launched"]) for bx in (145.0, 138.0))
def thr(rpm, lo=0.24, hi=1.30, tol=0.03):
    if not dual_ok(rpm, hi): return None
    if dual_ok(rpm, lo): return lo
    while hi-lo > tol:
        mid = round(0.5*(lo+hi), 3)
        if dual_ok(rpm, mid): hi = mid
        else: lo = mid
    return hi
JP = Path("simulation/mujoco/out/_r2r5_speed_req12.json")
out = json.loads(JP.read_text(encoding="utf-8"))
for rpm in (50.0, 120.0, 130.0, 160.0):
    k = str(int(rpm))
    if k in out["R5"] and out["R5"][k] is not None:
        print("skip", rpm, flush=True); continue
    t = thr(rpm)
    out["R5"][k] = t
    JP.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("R5 @%3d rpm threshold(12s) = %s N.m [%.0fs]" % (rpm, t, time.time()-T0), flush=True)
print("done")