# -*- coding: utf-8 -*-
"""相位实验（修正版）：指片避让进料路径 -> 球能滚到唇口；顺带对比二指方案。"""
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

# θ(指片) = -ang  →  ang = (360 - θ) % 360
def by_theta(thetas): return blades([(360.0 - t) % 360.0 for t in thetas])

BASE = ol.GEOM["V0 现状"][0]
CASES = [
 ("P0 三指 原相位 θ=342/222/102",  ol.ORIG_PARTS),
 ("P1 三指 θ=240/120/0",           by_theta((240.0, 120.0, 0.0))),
 ("P2 三指 θ=154/34/274",          by_theta((154.0,  34.0, 274.0))),
 ("P3 二指 θ=350/170",             by_theta((350.0, 170.0))),
 ("P4 二指 θ=350/170 + A喇叭",      by_theta((350.0, 170.0))),
]
res = {}
for lab, parts in CASES:
    geom = "A 唇口喇叭" if "A喇叭" in lab else "V0 现状"
    ol.GEOM[lab] = (ol.GEOM[geom][0], parts)      # 注册为新方案，避免被 apply_geom 重置
    r = ol.run(lab, fr=1.0, sec=5.0, rest=True, trace=True)
    tr = r.pop("_trace"); tail = tr[-30:]
    x = sum(s["x"] for s in tail)/len(tail); z = sum(s["z"] for s in tail)/len(tail)
    rr = math.hypot(x-pv2.PADDLE_CX, z-pv2.PADDLE_CZ)
    ang = math.degrees(math.atan2(z-pv2.PADDLE_CZ, x-pv2.PADDLE_CX)) % 360
    drift = max(math.hypot(s["x"]-x, s["z"]-z) for s in tail)
    thr, _, rhi = ol.threshold(lab)
    res[lab] = {"rest_x": round(x,2), "rest_z": round(z,2), "rest_r": round(rr,2),
                "rest_ang": round(ang,1), "drift_mm": round(drift,3),
                "threshold_Nm": thr, "peak_torque_Nm": rhi["torque_peak_Nm"] if rhi else None}
    log("%-30s 停位 r=%5.2f θ=%5.1f° 漂移=%.3f  门槛=%s N·m"
        % (lab, rr, ang, drift, "%.2f"%thr if thr else ">1.60"))
    Path("simulation/mujoco/out/summary_v2_phase.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
log("完成 -> out/summary_v2_phase.json")
