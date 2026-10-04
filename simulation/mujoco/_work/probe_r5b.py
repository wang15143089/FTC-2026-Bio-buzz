# -*- coding: utf-8 -*-
"""R2 vs R5：紧凑事件探针（稀疏轨迹 + 关键事件）"""
import json, math, sys, importlib.util
from pathlib import Path
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
SAVE = {}
for lab, thr in (("R2",0.46),("R5",0.42)):
    r = ol.run(lab, bx=145.0, rpm=200.0, fr=thr+0.05, sec=7.0, trace=True)
    tr = r["_trace"]
    # 关键事件
    ev = {}
    ev["launched"] = r["launched"]
    # 球第一次到达 x<0（进入停位区）
    for t in tr:
        if t["x"] < 0.0: ev["enter_x0"] = (t["t"], round(t["x"],2), round(t["z"],2), round(t["r"],2), round(t["ang"],1)); break
    # r 最小值（滚进球道的标志）
    mn = min(tr, key=lambda t: t["r"]); ev["min_r"] = (mn["t"], round(mn["r"],2), round(mn["ang"],1), round(mn["x"],2), round(mn["z"],2))
    # 球第一次越过唇口角 225°（进入外罩扇形区，θ 从 330 降到 <225）
    for t in tr:
        if t["ang"] < 225.0: ev["cross_225"] = (t["t"], round(t["ang"],1), round(t["r"],2), round(t["x"],2), round(t["z"],2)); break
    # 最大速度
    mx = max(tr, key=lambda t: t["v"]); ev["v_max"] = (mx["t"], round(mx["v"],2), round(mx["ang"],1), round(mx["r"],2))
    ev["torque_peak"] = r["torque_peak_Nm"]; ev["torque_load_mean"] = r["torque_load_mean_Nm"]
    ev["exit_speed"] = r.get("exit_speed"); ev["exit_angle"] = r.get("exit_angle")
    ev["keys"] = sorted(r.keys())
    SAVE[lab] = {"ev": ev, "path": [[round(t["t"],3), round(t["x"],2), round(t["z"],2), round(t["r"],2), round(t["ang"],2), round(t["v"],3)] for t in tr if t["t"] <= 4.0]}
    print("==", lab, "==")
    for k, v in ev.items():
        if k != "keys": print("   %-14s %s" % (k, v))
    print("   res keys:", ev["keys"])
Path("simulation/mujoco/out/_r2r5_paths.json").write_text(json.dumps(SAVE, ensure_ascii=False), encoding="utf-8")
print("saved out/_r2r5_paths.json")
