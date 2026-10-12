# -*- coding: utf-8 -*-
"""R40：低摩擦内衬下复核多球工况 —— 停靠位置 + 索引送出成功率。

口径对齐 r38_v8（R38/R39 现行几何）：托板 TRAY_X1 默认 285、球-球/球-拨杆 mu 默认 0.60。
内衬只用 monkeypatch 加到 外罩内弧(r10_*/shell_*) 与 托板(tray*) 上（priority=2 覆盖）。

用法: _r40_liner_mix.py --liner 0.05 --tag LIN05
      _r40_liner_mix.py --liner -1 --tag B60        (--liner -1 = 不贴内衬的同期对照)
"""
import sys, os, json, math, random, argparse
from pathlib import Path
import numpy as np, mujoco
sys.path.insert(0, os.path.abspath("simulation/mujoco/_work"))
import r37_multiball as R

ap = argparse.ArgumentParser()
ap.add_argument("--liner", type=float, default=0.05)
ap.add_argument("--liner-shell", type=float, default=-2.0)
ap.add_argument("--liner-tray", type=float, default=-2.0)
ap.add_argument("--tray", type=float, default=285.0)
ap.add_argument("--mu-ball", type=float, default=0.60)
ap.add_argument("--qgap", type=float, default=0.6)
ap.add_argument("--hold", type=float, default=3.0)
ap.add_argument("--balls", type=int, default=4)
ap.add_argument("--cases", type=int, default=6)
ap.add_argument("--seed", type=int, default=20261011)
ap.add_argument("--extra", default="")
ap.add_argument("--tag", default="LIN05")
a = ap.parse_args()

SHELL = a.liner if a.liner_shell == -2.0 else a.liner_shell
TRAY = a.liner if a.liner_tray == -2.0 else a.liner_tray
shell_on, tray_on = SHELL >= 0.0, TRAY >= 0.0

R.TRAY_X1 = a.tray
R.SPILL_X = a.tray + 25.0
R.GAP = a.qgap
R._PROBE.clear()

_orig = R.build_multi
def build_patch(mix, ph0, nip, mu=None):
    m, d, aid, jid, meta, w, xml = _orig(mix, ph0, nip, a.mu_ball)
    for g in range(m.ngeom):
        nm = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, g) or ""
        if nm.startswith("r10_") or nm.startswith("shell_"):
            if shell_on:
                m.geom_friction[g][0] = SHELL; m.geom_priority[g] = 2
        elif nm.startswith("tray"):
            if tray_on:
                m.geom_friction[g][0] = TRAY; m.geom_priority[g] = 2
    return m, d, aid, jid, meta, w, xml
R.build_multi = build_patch

rng = random.Random(a.seed)
cases = [("NECTARx%d 最坏" % a.balls, 0.0, ["NECTAR"] * a.balls)]
for ph0 in R.PH0S[:a.cases]:
    cases.append(("mix%d随机" % a.balls, ph0,
                  [rng.choice(["POLLEN", "NECTAR"]) for _ in range(a.balls)]))
for spec in [s for s in a.extra.split("|") if s.strip()]:
    body, _, ph = spec.partition("@")
    cases.append(("固定", float(ph or 0.0), body.split(",")))

print("=== R40 复核  内衬:外罩=%s 托板=%s  tray=%.0f  mu_ball=%.2f  hold=%.1f  seed=%d  轮数=%d ==="
      % ("%.2f" % SHELL if shell_on else "off", "%.2f" % TRAY if tray_on else "off",
         a.tray, a.mu_ball, a.hold, a.seed, len(cases)), flush=True)

rows = []
for tag, ph0, mix in cases:
    nip = max(R.SP[x]["nip"] for x in mix)
    res, xml = R.run_case(mix, ph0, nip, a.hold)
    res["tag"] = tag
    rows.append(res)
    cx, cz = R.pv2.PADDLE_CX, R.pv2.PADDLE_CZ
    print("\n[%s ph0=%3.0f  %s  夹口%.0f  叠放%d  通道内%d]"
          % (tag, ph0, ">".join(mix), nip, res["stacked"], res["in_channel"]), flush=True)
    for k, (x, z, ang) in enumerate(res["settled"]):
        rr = math.hypot(x - cx, z - cz)
        reach = (142.0 <= ang <= 275.0) and (rr <= 61.0 + R.SP[mix[k]]["r"])
        print("   球%d %-6s 静置(x=%7.1f z=%6.1f)  r=%5.1f 极角=%5.1f 扫掠可达=%s  起点%s"
              % (k + 1, mix[k], x, z, rr, ang, "是" if reach else "否", res["start"][k]),
              flush=True)
    for k, e in enumerate(res["exit"]):
        if e:
            print("   球%d %-6s 出膛 t=%6.2f 轮内%5.2f v=%5.2f m/s"
                  % (k + 1, mix[k], e["t"], e["cyc_t"], e["v"]), flush=True)
        else:
            sp = res["spill"][k]
            print("   球%d %-6s 未出膛%s" % (k + 1, mix[k],
                  ("  逸出t=%.1f@(%.0f,%.0f)" % (sp["t"], sp["x"], sp["z"])) if sp else ""),
                  flush=True)
    print("   -> 出膛 %d/%d  真出膛 %d  清空 %s s  扭矩峰 %.3f  卡滞 %.0f%%"
          % (res["n_launched"], len(mix),
             sum(1 for e in res["exit"] if e and e["v"] >= 3.0),
             res.get("t_total_s", "--"), res["tq_peak"], 100 * res["jam_frac"]), flush=True)

nb_tot = sum(len(r["mix"]) for r in rows)
ok = [e for r in rows for e in r["exit"] if e]
real = [e for e in ok if e["v"] >= 3.0]
full = sum(1 for r in rows if r["n_launched"] == len(r["mix"]))
print("\n=== 汇总 %d 轮 / %d 颗 ===" % (len(rows), nb_tot), flush=True)
print("  出膛 %d/%d = %.0f%%   真出膛(v>=3.0) %d/%d = %.0f%%   全清轮 %d/%d"
      % (len(ok), nb_tot, 100.0 * len(ok) / nb_tot, len(real), nb_tot,
         100.0 * len(real) / nb_tot, full, len(rows)), flush=True)
if ok:
    print("  出膛速度 均%.2f 最小%.2f 最大%.2f m/s   轮内耗时 均%.2f s"
          % (float(np.mean([e["v"] for e in ok])), min(e["v"] for e in ok),
             max(e["v"] for e in ok), float(np.mean([e["cyc_t"] for e in ok]))), flush=True)
tt = [r["t_total_s"] for r in rows if r.get("t_total_s")]
if tt:
    print("  清空耗时 均%.2f s 最小%.2f 最大%.2f" % (float(np.mean(tt)), min(tt), max(tt)), flush=True)
print("  最大卡滞 %.0f%%  逸出 %d 颗"
      % (100 * max(r["jam_frac"] for r in rows),
         sum(1 for r in rows for s in r["spill"] if s)), flush=True)

out = Path("simulation/mujoco/out/_r40_%s.json" % a.tag)
out.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
print("  saved", out, flush=True)

