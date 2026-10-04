# -*- coding: utf-8 -*-
"""最优组合收尾：二指 + A + D"""
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

# 组合：二指 + A 喇叭 + D 垫
ol.GEOM["P5 二指+A+D"] = (ol.GEOM["A+D"][0], by_theta((350.0,170.0)))
res = {}
for lab in ("P3 二指350/170", "P4 二指350/170+A喇叭", "P5 二指+A+D"):
    if lab not in ol.GEOM:
        ol.GEOM[lab] = (ol.GEOM["V0 现状"][0], by_theta((350.0,170.0)))
    thr = ol.threshold(lab)[0]
    n = sum(1 for bx in (145.0, 138.0) if ol.run(lab, bx=bx, fr=thr+0.05)["launched"])
    # 转速门槛
    sp = {}
    for rpm in (60.0, 75.0, 90.0, 105.0):
        sp[rpm] = all(ol.run(lab, bx=bx, rpm=rpm, fr=1.5)["launched"] for bx in (145.0, 138.0))
    res[lab] = {"threshold_Nm": thr, "pass_of2_at_thr+0.05": n,
                "speed_ok": {str(k): v for k, v in sp.items()}}
    log("%-22s 门槛=%.2f  稳健=%d/2   转速: %s" % (lab, thr, n,
        "  ".join("%.0f:%s" % (k, "OK" if v else "--") for k, v in sp.items())))
Path("simulation/mujoco/out/summary_v2_best.json").write_text(
    json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
log("完成 -> out/summary_v2_best.json")
