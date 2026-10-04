# -*- coding: utf-8 -*-
"""相位实验：球能否滚到唇口？拨杆指片数量/初始相位的影响"""
import json, math, sys, time, importlib.util
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
spec = importlib.util.spec_from_file_location("ol", r"simulation/mujoco/_work/opt_lib.py")
ol = importlib.util.module_from_spec(spec); spec.loader.exec_module(ol)
pv2 = ol.pv2; W = pv2.PADDLE_W
T0 = time.time()
def log(*a): print("[%5.1fs]" % (time.time()-T0), *a, flush=True)

def blades(angs, tip=58.0, name="blade", n_arm=True):
    def f():
        parts = [("hub", (0.0,0.0,0.0), (18.0,17.0,18.0), 0.0, "cylY")]
        for i, a in enumerate(angs, 1):
            parts.append(("arm_%d"%i,      (30.0,0.0,0.0), (16.0, 9.0, 5.0), a, "box"))
            parts.append(("blade_%d"%i,    (52.0,0.0,0.0), (6.0, W/2.0, 15.0), a, "box"))
            parts.append(("flex_%d"%i,     (58.0,0.0,0.0), (2.0, W/2.0, 17.0), a, "box"))
        return parts
    return f

# θ(指片) = -ang  →  ang = -θ
CASES = {
 "V0 三指 原相位 θ=342/222/102": None,
 "三指 Δ=102 θ=240/120/0":      blades((120.0, 240.0, 360.0)),
 "三指 Δ=188 θ=154/34/274":      blades((206.0, 326.0, 86.0)),
 "二指 θ=350/170":               blades((10.0, 190.0)),
 "二指 θ=350/170 + A喇叭":       blades((10.0, 190.0)),
}
res = {}
for lab, patch in CASES.items():
    ol.apply_geom("V0 现状")
    if patch is not None: pv2.paddle_parts = patch
    # 静止位
    r = ol.run("V0 现状", fr=1.0, sec=5.0, rest=True, trace=True)
    tr = r.pop("_trace"); tail = tr[-30:]
    x = sum(s["x"] for s in tail)/len(tail); z = sum(s["z"] for s in tail)/len(tail)
    rr = math.hypot(x-pv2.PADDLE_CX, z-pv2.PADDLE_CZ)
    ang = math.degrees(math.atan2(z-pv2.PADDLE_CZ, x-pv2.PADDLE_CX)) % 360
    drift = max(math.hypot(s["x"]-x, s["z"]-z) for s in tail)
    # 门槛
    thr, _, rhi = ol.threshold("V0 现状")
    res[lab] = {"rest_x": round(x,2), "rest_z": round(z,2), "rest_r": round(rr,2),
                "rest_ang": round(ang,1), "drift": round(drift,3), "threshold_Nm": thr,
                "peak_torque": rhi["torque_peak_Nm"] if rhi else None}
    log("%-28s 停位 x=%7.2f z=%6.2f r=%5.2f θ=%5.1f° 漂移=%.3f  门槛=%s N·m"
        % (lab, x, z, rr, ang, drift, "%.2f"%thr if thr else ">1.60"))
    Path("simulation/mujoco/out/summary_v2_phase.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
log("完成 -> out/summary_v2_phase.json")
