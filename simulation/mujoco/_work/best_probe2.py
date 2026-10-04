# -*- coding: utf-8 -*-
"""干净复核：二指 / 二指+A / 二指+A+D / A+D 的门槛与转速门槛（显式注册，避免命名串台）"""
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
def th2(ts): return blades([(360.0-t) % 360.0 for t in ts])
V0S = ol.GEOM["V0 现状"][0]; FL = ol.GEOM["A 唇口喇叭"][0]; AD = ol.GEOM["A+D"][0]
REG = {
 "R1 二指350/170":          (V0S, th2((350.0, 170.0))),
 "R2 二指350/170 + A":      (FL,  th2((350.0, 170.0))),
 "R3 二指350/170 + A + D":  (AD,  th2((350.0, 170.0))),
 "R4 三指原相位 + A + D":    (AD,  ol.ORIG_PARTS),
 "R5 二指350/170 + D":      (ol.GEOM["D 球窝抬高6.8"][0], th2((350.0, 170.0))),
}
ol.GEOM.update(REG)
res = {}
for lab in REG:
    thr = ol.threshold(lab)[0]
    rob = sum(1 for bx in (145.0, 138.0) if ol.run(lab, bx=bx, fr=thr+0.05)["launched"])
    sp = {}
    for rpm in (75.0, 90.0, 105.0, 120.0):
        sp[rpm] = all(ol.run(lab, bx=bx, rpm=rpm, fr=1.5)["launched"] for bx in (145.0, 138.0))
    res[lab] = {"threshold_Nm": thr, "robust_of2": rob, "speed_ok": {str(k): v for k, v in sp.items()}}
    log("%-24s 门槛=%.2f 稳健=%d/2 转速门槛≈%s rpm" % (lab, thr, rob,
        next((int(k) for k, v in sp.items() if v), ">120")))
Path("simulation/mujoco/out/summary_v2_best.json").write_text(
    json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
log("完成 -> out/summary_v2_best.json")
