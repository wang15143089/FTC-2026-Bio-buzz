# -*- coding: utf-8 -*-
"""R5 feed torque threshold vs paddle rpm (dual-entry criterion x=145/138)."""
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
ENTRIES = (145.0, 138.0)
def dual_ok(lab, rpm, fr):
    return all(bool(ol.run(lab, bx=bx, rpm=rpm, fr=fr)["launched"]) for bx in ENTRIES)
def thr(lab, rpm, lo=0.24, hi=0.95, tol=0.05):
    if not dual_ok(lab, rpm, hi): return None
    if dual_ok(lab, rpm, lo): return lo
    while hi-lo > tol:
        mid = round(0.5*(lo+hi), 3)
        if dual_ok(lab, rpm, mid): hi = mid
        else: lo = mid
    return hi
JP = Path("simulation/mujoco/out/_r2r5_speed_req.json")
out = {}
if JP.exists():
    try: out = json.loads(JP.read_text(encoding="utf-8"))
    except Exception: out = {}
JOBS = [("R5", 60.0), ("R5", 90.0), ("R5", 105.0), ("R5", 145.0), ("R5", 200.0),
        ("R5", 290.0), ("R5", 45.0), ("R5", 75.0), ("R5", 120.0), ("R5", 250.0),
        ("R2", 60.0), ("R2", 90.0), ("R2", 200.0)]
for lab, rpm in JOBS:
    if lab in out and str(int(rpm)) in out[lab] and out[lab][str(int(rpm))] is not None:
        print("skip %s @%d (cached)" % (lab, rpm), flush=True); continue
    out.setdefault(lab, {})
    t = thr(lab, rpm)
    out[lab][str(int(rpm))] = t
    JP.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("%s @%3d rpm dual-entry threshold = %s N.m  [%.0fs]" % (lab, rpm, t, time.time()-T0), flush=True)
print("done %.0fs" % (time.time()-T0))