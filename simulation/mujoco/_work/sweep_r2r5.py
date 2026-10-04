# -*- coding: utf-8 -*-
"""R2 vs R5 离散扭矩扫描 + 关键指标"""
import json, math, sys, time, importlib.util
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
out = {}
for lab in ("R2","R5"):
    rows = []
    for fr in (0.38,0.40,0.42,0.44,0.46,0.48,0.50,0.55):
        st = [ol.run(lab, bx=bx, rpm=200.0, fr=fr)["launched"] for bx in (145.0,138.0)]
        rows.append({"fr": fr, "pass": st})
        print("%s fr=%.2f  bx145/%s  bx138/%s" % (lab, fr, st[0], st[1]), flush=True)
    # 90 rpm 检查
    sp = {}
    for fr in (0.42,0.46,0.50):
        sp[fr] = [ol.run(lab, bx=bx, rpm=90.0, fr=fr)["launched"] for bx in (145.0,138.0)]
        print("   %s @90rpm fr=%.2f -> %s" % (lab, fr, sp[fr]), flush=True)
    r = ol.run(lab, bx=145.0, rpm=200.0, fr=0.50)
    out[lab] = {"sweep": rows, "at90": {str(k): v for k,v in sp.items()},
                "metrics": {k: r[k] for k in ("rest_position_mm","settled_position_mm","release_speed_m_s",
                            "peak_speed_m_s","max_z_mm","entered_shell","passed_nip","reached_142deg_exit",
                            "torque_peak_Nm","torque_load_mean_Nm","torque_load_p95_Nm","final_mm")}}
    print("   %s 指标: %s" % (lab, json.dumps(out[lab]["metrics"], ensure_ascii=False)), flush=True)
Path("simulation/mujoco/out/_r2r5_sweep.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("完成 %.1fs" % (time.time()-T0))
