# -*- coding: utf-8 -*-
"""转速门槛扫描 + 门槛稳健性（3 个进料位）"""
import json, math, sys, time, importlib.util
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
spec = importlib.util.spec_from_file_location("ol", r"simulation/mujoco/_work/opt_lib.py")
ol = importlib.util.module_from_spec(spec); spec.loader.exec_module(ol)
pv2 = ol.pv2; W = pv2.PADDLE_W
T0 = time.time()
def log(*a): print("[%5.1fs]" % (time.time()-T0), *a, flush=True)

def blades(angs):
    def f():
        parts = [("hub", (0.0,0.0,0.0), (18.0,17.0,18.0), 0.0, "cylY")]
        for i, a in enumerate(angs, 1):
            parts.append(("arm_%d"%i,   (30.0,0.0,0.0), (16.0, 9.0, 5.0), a, "box"))
            parts.append(("blade_%d"%i, (52.0,0.0,0.0), (6.0, W/2.0, 15.0), a, "box"))
            parts.append(("flex_%d"%i,  (58.0,0.0,0.0), (2.0, W/2.0, 17.0), a, "box"))
        return parts
    return f
def by_theta(ts): return blades([(360.0-t) % 360.0 for t in ts])

ol.GEOM["P4 二指350/170+A喇叭"] = (ol.GEOM["A 唇口喇叭"][0], by_theta((350.0,170.0)))
res = {}
log("=== 转速门槛（扭矩 1.5 N·m 不限）===")
for lab in ("V0 现状", "P4 二指350/170+A喇叭"):
    line = {}
    for rpm in (60.0, 90.0, 105.0, 120.0, 140.0, 200.0):
        g = {}
        for bx in (145.0, 138.0, 150.0):
            r = ol.run(lab, bx=bx, rpm=rpm, fr=1.5)
            g[bx] = bool(r["launched"])
        line[rpm] = g
        log("  %-22s %5.0f rpm -> %s" % (lab, rpm, "  ".join("x%.0f:%s" % (k, "OK" if v else "--") for k, v in g.items())))
    res[lab] = {"speed_by_rpm": {str(k): v for k, v in line.items()}}
log("=== 门槛稳健性（门槛+0.05，3 个进料位）===")
for lab in ("A 唇口喇叭", "D 球窝抬高6.8", "A+D", "P4 二指350/170+A喇叭"):
    thr = res.get(lab, {}).get("threshold_Nm")
    base = ol.threshold(lab)[0]
    n = sum(1 for bx in (145.0, 138.0, 150.0) if ol.run(lab, bx=bx, fr=base+0.05)["launched"])
    res[lab] = res.get(lab, {}); res[lab]["threshold_Nm"] = base
    res[lab]["pass_of3_at_thr+0.05"] = n
    log("  %-22s 门槛=%.2f  +0.05 下通过 %d/3" % (lab, base, n))
Path("simulation/mujoco/out/summary_v2_speed.json").write_text(
    json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
log("完成 -> out/summary_v2_speed.json")
