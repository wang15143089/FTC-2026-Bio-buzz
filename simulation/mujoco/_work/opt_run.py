# -*- coding: utf-8 -*-
"""逐个方案跑一遍：门槛、静止位、轨迹；再做摩擦敏感性。"""
import json, math, sys, time, importlib.util
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
spec = importlib.util.spec_from_file_location("ol", r"simulation/mujoco/_work/opt_lib.py")
ol = importlib.util.module_from_spec(spec); spec.loader.exec_module(ol)
OUT = Path("simulation/mujoco/out")
T0 = time.time()
def log(*a):
    print("[%6.1fs]" % (time.time() - T0), *a, flush=True)

Geom = list(ol.GEOM.keys())
summary = {"geom": {}, "friction": {}, "meta": {"paddle_rpm": 200.0, "flywheel_rpm": 1620.0,
           "ball_start_x_mm": 145.0, "seconds": 7.0, "unit": "N*m (paddle forcerange)"}}

# ---------- 1. 静止位 ----------
log("=== 1/3 静止位（拨杆不动，球自由滚入停位）===")
for name in Geom:
    r = ol.run(name, rpm=200.0, fr=1.0, sec=4.0, rest=True, trace=True)
    tr = r.pop("_trace")
    tail = tr[-30:]
    x = sum(s["x"] for s in tail) / len(tail); z = sum(s["z"] for s in tail) / len(tail)
    rr = math.hypot(x - ol.pv2.PADDLE_CX, z - ol.pv2.PADDLE_CZ)
    ang = math.degrees(math.atan2(z - ol.pv2.PADDLE_CZ, x - ol.pv2.PADDLE_CX)) % 360.0
    spread = max(math.hypot(s["x"] - x, s["z"] - z) for s in tail)
    summary["geom"][name] = {"rest_x_mm": round(x, 2), "rest_z_mm": round(z, 2),
                             "rest_r_mm": round(rr, 2), "rest_ang_deg": round(ang, 2),
                             "rest_drift_mm": round(spread, 3)}
    log("  %-14s 停位 x=%.2f z=%.2f  r=%.2f  θ=%.1f°  残余漂移=%.3f mm"
        % (name, x, z, rr, ang, spread))

# ---------- 2. 门槛 ----------
log("=== 2/3 发射门槛（二分法）===")
for name in Geom:
    thr, _, rhi = ol.threshold(name)
    n_pass = 1
    if thr is not None:
        for bx in (138.0, 150.0):
            g, _ = ol.ok(name, bx, thr + 0.05)
            n_pass += int(g)
    summary["geom"][name].update({"threshold_Nm": thr, "approx": thr is None,
                                  "verify_pass_of3": n_pass})
    log("  %-14s 门槛 = %s N·m   （门槛+0.05 下 3 个进料位通过 %d/3）"
        % (name, "%.2f" % thr if thr else ">1.60 不发射", n_pass))
    OUT.joinpath("summary_v2_options_final.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

# ---------- 3. 轨迹（用于绘图）----------
log("=== 3/3 轨迹采样 ===")
SHOTS = [("V0 现状", 0.8), ("V0 现状", 1.0), ("A 唇口喇叭", 0.8), ("D 球窝抬高6.8", 0.8),
         ("A 唇口喇叭", 1.0), ("A+D", 1.0), ("C 叶尖卸载", 1.0)]
for name, fr in SHOTS:
    r = ol.run(name, fr=fr, trace=True)
    tr = r.pop("_trace")
    tag = "v2opt_%s_%s" % (name.split()[0], str(fr).replace(".", "p"))
    OUT.joinpath("trace_%s.json" % tag).write_text(json.dumps(tr), encoding="utf-8")
    r["tag"] = tag; r["forcerange_Nm"] = fr; r["option"] = name
    summary.setdefault("shots", {})[tag] = r
    log("  %-14s @%.1f N·m  launched=%-5s 出射=%s m/s 峰值扭矩=%.2f N·m"
        % (name, fr, r["launched"], r.get("exit", {}).get("speed_m_s", "-"), r["torque_peak_Nm"]))
    OUT.joinpath("summary_v2_options_final.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

# ---------- 4. 摩擦敏感性 ----------
log("=== 4/3 摩擦敏感性（现状几何 / 方案A）===")
cases = [("V0 u=1.0(现状)", "V0 现状", {}),
         ("V0 u_ball=0.7", "V0 现状", {"mu_ball": 0.7}),
         ("V0 u_ball=0.5", "V0 现状", {"mu_ball": 0.5}),
         ("V0 u_ball=0.35", "V0 现状", {"mu_ball": 0.35}),
         ("V0 u_shell=0.10", "V0 现状", {"mu_shell": 0.10}),
         ("A u_ball=0.7", "A 唇口喇叭", {"mu_ball": 0.7}),
         ("A u_ball=0.5", "A 唇口喇叭", {"mu_ball": 0.5}),
         ("A u_ball=0.35", "A 唇口喇叭", {"mu_ball": 0.35})]
for lab, name, kw in cases:
    thr, _, rhi = ol.threshold(name, **kw)
    summary["friction"][lab] = {"variant": name, "kw": kw, "threshold_Nm": thr,
                                "torque_peak_Nm": rhi["torque_peak_Nm"] if rhi else None}
    log("  %-18s 门槛 = %s N·m" % (lab, "%.2f" % thr if thr else ">1.60 不发射"))
    OUT.joinpath("summary_v2_options_final.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

ol.pv2.static_geoms, ol.pv2.paddle_parts = ol.ORIG_STATIC, ol.ORIG_PARTS
log("完成 -> out/summary_v2_options_final.json")
