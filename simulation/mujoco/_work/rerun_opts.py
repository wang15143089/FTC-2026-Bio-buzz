# -*- coding: utf-8 -*-
"""逐个复跑：接触几何方案 A/B/C/D 的发射门槛（现场打印，逐个确认）"""
import json, math, sys, time, importlib.util
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
spec = importlib.util.spec_from_file_location("ol", r"simulation/mujoco/_work/opt_lib.py")
ol = importlib.util.module_from_spec(spec); spec.loader.exec_module(ol)
T0 = time.time()
def log(*a): print("[%6.1fs]" % (time.time()-T0), *a, flush=True)

ORDER = ["V0 现状", "A 唇口喇叭", "B 托板缩进", "C 叶尖卸载", "D 球窝抬高6.8", "A+B", "A+D"]
log("开始：200 rpm，球从托板 x=145 滚入，二分法分辨率 0.05 N·m")
out = {}
for name in ORDER:
    t1 = time.time()
    r = ol.run(name, bx=145.0, fr=1.0, sec=3.0, rest=True, trace=True)
    tr = r["_trace"][-20:]
    rx = sum(p["x"] for p in tr)/len(tr) - ol.pv2.PADDLE_CX
    rz = sum(p["z"] for p in tr)/len(tr) - ol.pv2.PADDLE_CZ
    rest_r = math.hypot(rx, rz); rest_a = math.degrees(math.atan2(rz, rx)) % 360.0
    thr, _, rhi = ol.threshold(name)
    n_ok = sum(1 for bx in (145.0, 138.0) if ol.run(name, bx=bx, fr=thr+0.05)["launched"])
    out[name] = {"rest_r_mm": round(rest_r,2), "rest_ang_deg": round(rest_a,1),
                 "threshold_Nm": thr, "robust_of2": n_ok}
    log("%-16s 停位 r=%.1f mm (θ=%.1f°)  门槛=%.2f N·m  稳健=%d/2   用时 %.0fs"
        % (name, rest_r, rest_a, thr if thr else -1, n_ok, time.time()-t1))
Path("simulation/mujoco/out/summary_v2_rerun_opts.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
log("逐个复跑完成 -> out/summary_v2_rerun_opts.json")
