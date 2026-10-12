# -*- coding: utf-8 -*-
"""R39：在低摩擦内衬（默认 0.05）下再比较拨杆改型 —— 判断叶片形状是否还有必要改。
用法: _r39_padd.py --liner 0.05 --ball NECTAR --ph0 150 --nip 86
"""
import sys, os, json, argparse
import numpy as np, mujoco
sys.path.insert(0, os.path.abspath("simulation/mujoco/_work"))
import r37_multiball as R
import _r39_t as T

LINER = [0.05]
_orig = R.build_multi

def build_patch(mix, ph0, nip, mu=0.60):
    m, d, aid, jid, meta, w, xml = _orig(mix, ph0, nip, mu)
    for g in range(m.ngeom):
        nm = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, g) or ""
        if nm.startswith("r10_") or nm.startswith("tray") or nm.startswith("shell_"):
            m.geom_friction[g][0] = LINER[0]
            m.geom_priority[g] = 2
    return m, d, aid, jid, meta, w, xml

ap = argparse.ArgumentParser()
ap.add_argument("--liner", type=float, default=0.05)
ap.add_argument("--ball", default="NECTAR")
ap.add_argument("--ph0", type=float, default=150.0)
ap.add_argument("--nip", type=float, default=86.0)
ap.add_argument("--tq", type=float, default=0.530)
ap.add_argument("--tmax", type=float, default=12.0)
ap.add_argument("--target", type=float, default=118.0)
ap.add_argument("--names", default="V0 原设计|X64 原+加高|R64 全高筋|R64n 圆头|R60 全高筋|R64A 带臂|R64t4 厚条|R50 半高筋")
a = ap.parse_args()
LINER[0] = a.liner
R.build_multi = build_patch
print("=== R39 内衬 mu=%.2f 下拨杆改型对比  ball=%s ph0=%.0f nip=%.0f 判据=累计转%.0f ==="
      % (a.liner, a.ball, a.ph0, a.nip, a.target), flush=True)
print("  %-14s %9s %9s %7s %7s %7s %7s  %s" %
      ("方案", "送达s", "扫完s", "tq均", "tq峰", "卡滞%", "转角", "碰撞"), flush=True)
rows = []
for nm in a.names.split("|"):
    r = T.measure(a.ball, T.VAR[nm], a.ph0, a.nip, 0.60, a.tq, tmax=a.tmax, target=a.target, tag=nm)
    r["name"] = nm
    rows.append(r)
    print("  %-14s %9s %9s %7.3f %7.3f %6.0f%% %7.1f  %s" %
          (nm, ("%.2f" % r["t_deliver"]) if r["t_deliver"] else "--",
           ("%.2f" % r["t_sweep"]) if r["t_sweep"] else "--",
           r["tq_mean"], r["tq_max"], 100 * r["jam"], r["travel"],
           ",".join("%s@%.2f" % (k, v) for k, v in r["hits"].items()) or "-"), flush=True)
json.dump(rows, open("simulation/mujoco/out/_r39_padd_liner.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
