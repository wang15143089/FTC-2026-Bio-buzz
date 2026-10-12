# -*- coding: utf-8 -*-
"""R41: 用「减少接触面积 / 减小压力」降摩擦的实测 —— 外罩内弧由整面改筋条(rails)。

A  rib    : 外罩内弧 24 片满宽(108mm) -> 3 条 4mm 筋；mu 不变 0.60（与 R40 无内衬对照同口径）
B  ribmu  : 同上筋条，另把筋面 mu 覆盖 0.05，托板保持 0.60（检验"只在外罩降摩擦"够不够）

用法：
  _r41_ribs.py --mode diag --ribs 3            # 接触力分布诊断（快）
  _r41_ribs.py --ribs 3 --tag RIB              # A
  _r41_ribs.py --ribs 3 --rib-mu 0.05 --tag RIBMU   # B
"""
import sys, os, json, math, random, argparse
from pathlib import Path
import numpy as np
import mujoco

sys.path.insert(0, os.path.abspath("simulation/mujoco/_work"))
import r37_multiball as R
import r10_cradle as R10
import opt_lib as ol

PV2 = ol.pv2

ap = argparse.ArgumentParser()
ap.add_argument("--mode", default="run", choices=["run", "diag"])
ap.add_argument("--ribs", type=int, default=3)
ap.add_argument("--rib-w", type=float, default=4.0)
ap.add_argument("--rib-tray", action="store_true")
ap.add_argument("--rib-mu", type=float, default=-1.0)
ap.add_argument("--shell-mu", type=float, default=-1.0)
ap.add_argument("--noworst", action="store_true")
ap.add_argument("--tray-mu", type=float, default=-1.0)
ap.add_argument("--paddle-mu", type=float, default=-1.0)
ap.add_argument("--tray", type=float, default=285.0)
ap.add_argument("--qgap", type=float, default=0.6)
ap.add_argument("--mu-ball", type=float, default=0.60)
ap.add_argument("--hold", type=float, default=3.0)
ap.add_argument("--balls", type=int, default=4)
ap.add_argument("--cases", type=int, default=6)
ap.add_argument("--seed", type=int, default=20261011)
ap.add_argument("--extra", default="")
ap.add_argument("--grav", type=float, default=9.81)
ap.add_argument("--tag", default="RIB")
a = ap.parse_args()

R.TRAY_X1 = a.tray
R.SPILL_X = a.tray + 25.0
R.GAP = a.qgap
R._PROBE.clear()

FW = PV2.FEEDER_W
_orig_stat = R10.stat


def _split(entry):
    nm, cls, kind, size, pos, q = entry
    if a.ribs <= 1 or kind != "box":
        return [entry]
    w = a.rib_w
    half = FW / 2.0
    if a.ribs == 3:
        ys = [-(half - w / 2.0), 0.0, (half - w / 2.0)]
    else:
        ys = list(np.linspace(-(half - w / 2.0), half - w / 2.0, a.ribs))
    return [(nm + "_" + "abcdefgh"[i], cls, kind, (size[0], w, size[2]),
             (pos[0], ys[i], pos[2]), q) for i in range(len(ys))]


def stat_patch(*ar, **kw):
    out = []
    for e in _orig_stat(*ar, **kw):
        nm = e[0]
        if nm.startswith("r10_") or (a.rib_tray and nm == "tray"):
            out += _split(e)
        else:
            out.append(e)
    return out


R10.stat = stat_patch

_orig_build = R.build_multi


def build_patch(mix, ph0, nip, mu=None):
    m, d, aid, jid, meta, w, xml = _orig_build(mix, ph0, nip, a.mu_ball)
    for g in range(m.ngeom):
        nm = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, g) or ""
        if a.shell_mu >= 0.0 and (nm.startswith("r10_") or nm.startswith("shell_")):
            m.geom_friction[g][0] = a.shell_mu
            m.geom_priority[g] = 2
        elif a.rib_mu >= 0.0 and nm.startswith("r10_"):
            m.geom_friction[g][0] = a.rib_mu
            m.geom_priority[g] = 2
        elif a.tray_mu >= 0.0 and nm.startswith("tray"):
            m.geom_friction[g][0] = a.tray_mu
            m.geom_priority[g] = 2
        elif a.paddle_mu >= 0.0 and nm.startswith("paddle"):
            m.geom_friction[g][0] = a.paddle_mu
            m.geom_priority[g] = 2
    if abs(a.grav - 9.81) > 1e-9:
        m.opt.gravity[:] = [0.0, 0.0, -a.grav]
    return m, d, aid, jid, meta, w, xml


R.build_multi = build_patch

FAM = [("外罩内弧", ("r10_", "shell_")), ("托板", ("tray",)), ("拨杆", ("paddle_",)),
       ("导轨喉部", ("guide_",)), ("地面", ("catch_floor",)), ("后挡墙", ("rear_wall",))]


def fam(nm):
    for f, pre in FAM:
        if nm.startswith(pre):
            return f
    return "其他"


def diag():
    mix = ["NECTAR"]
    nip = R.SP["NECTAR"]["nip"]
    m, d, aid, jid, meta, w, xml = R.build_multi(mix, 0.0, nip, a.mu_ball)
    n_r10 = sum(1 for g in range(m.ngeom)
                if (mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, g) or "").startswith("r10_"))
    print("模型 geoms=%d  其中 r10_(外罩内弧)=%d 片" % (m.ngeom, n_r10), flush=True)
    centres, stacked, in_ch = R.place_queue(mix, 0.0)
    R.put(d, meta[0], *centres[0])
    dt = m.opt.timestep
    bg = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, "ball_geom_1")
    for i in range(int(1.5 / dt)):
        d.ctrl[aid] = 0.0
        mujoco.mj_step(m, d)
    acc = {}
    k = max(1, int(round(0.01 / dt)))
    n = int(1.2 / dt)
    f = np.zeros(6)
    for i in range(n):
        d.ctrl[aid] = w
        mujoco.mj_step(m, d)
        if i % k:
            continue
        for ci in range(d.ncon):
            c = d.contact[ci]
            if c.geom1 == bg:
                other = c.geom2
            elif c.geom2 == bg:
                other = c.geom1
            else:
                continue
            nm = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, other) or "?"
            mujoco.mj_contactForce(m, d, ci, f)
            e = acc.setdefault(nm, [0, 0.0, 0.0, 0.0])
            e[0] += 1
            e[1] += abs(f[0])
            e[2] += math.hypot(f[1], f[2])
            e[3] = max(e[3], abs(f[0]))
    print("\n=== 拨杆扫掠 1.2 s 内 球-环境 接触统计（NECTAR，外罩=%s）==="
          % ("整面 108mm" if a.ribs <= 1 else ("%d x %.1fmm 筋" % (a.ribs, a.rib_w))), flush=True)
    print("  %-10s %8s %12s %12s %12s" % ("接触对象", "采样数", "平均|N|(N)", "平均|Ff|(N)", "峰值|N|(N)"), flush=True)
    for kk in sorted(acc, key=lambda x: -acc[x][1]):
        e = acc[kk]
        print("  %-10s %8d %12.3f %12.3f %12.3f" % (kk, e[0], e[1] / e[0], e[2] / e[0], e[3]), flush=True)


rng = random.Random(a.seed)
cases = [] if a.noworst else [("NECTARx%d 最坏" % a.balls, 0.0, ["NECTAR"] * a.balls)]
for ph0 in R.PH0S[:a.cases]:
    cases.append(("mix%d随机" % a.balls, ph0,
                  [rng.choice(["POLLEN", "NECTAR"]) for _ in range(a.balls)]))
for spec in [s for s in a.extra.split("|") if s.strip()]:
    body, _, ph = spec.partition("@")
    cases.append(("固定", float(ph or 0.0), body.split(",")))

if a.mode == "diag":
    diag()
    raise SystemExit(0)

print("=== R41 筋条  g=%.2f  外罩=%s 筋面mu=%s 托板mu=%s  tray=%.0f  mu_ball=%.2f  hold=%.1f  轮数=%d ==="
      % (a.grav, "整面" if a.ribs <= 1 else ("%dx%.1fmm" % (a.ribs, a.rib_w)),
         "%.2f" % a.rib_mu if a.rib_mu >= 0 else "off",
         "%.2f" % a.tray_mu if a.tray_mu >= 0 else "off",
         a.tray, a.mu_ball, a.hold, len(cases)), flush=True)
print("    拨杆mu=%s  内衬范围: r10_/shell_/tray" % ("%.2f" % a.paddle_mu if a.paddle_mu >= 0 else "off"),
      flush=True)

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
        print("   球%d %-6s 静置(x=%7.1f z=%6.1f)  r=%5.1f 极角=%5.1f 扫掠可达=%s"
              % (k + 1, mix[k], x, z, rr, ang, "是" if reach else "否"), flush=True)
    for k, e in enumerate(res["exit"]):
        if e:
            fake = "  [假出膛: 轮内<0.05s]" if e["cyc_t"] <= 0.05 else ""
            print("   球%d %-6s 出膛 t=%6.2f 轮内%5.2f v=%5.2f m/s%s"
                  % (k + 1, mix[k], e["t"], e["cyc_t"], e["v"], fake), flush=True)
        else:
            sp = res["spill"][k]
            print("   球%d %-6s 未出膛%s" % (k + 1, mix[k],
                  ("  逸出t=%.1f@(%.0f,%.0f)" % (sp["t"], sp["x"], sp["z"])) if sp else ""), flush=True)
    print("   -> 出膛 %d/%d(真计数)  真出膛 %d  清空 %s s  扭矩峰 %.3f  卡滞 %.0f%%"
          % (sum(1 for e in res["exit"] if e and e["cyc_t"] > 0.05), len(mix),
             sum(1 for e in res["exit"] if e and e["v"] >= 3.0),
             res.get("t_total_s", "--"), res["tq_peak"], 100 * res["jam_frac"]), flush=True)

nb_tot = sum(len(r["mix"]) for r in rows)
ok = [e for r in rows for e in r["exit"] if e and e["cyc_t"] > 0.05]
real = [e for e in ok if e["v"] >= 3.0]
full = sum(1 for r in rows
           if sum(1 for e in r["exit"] if e and e["cyc_t"] > 0.05) == len(r["mix"]))
nfake = sum(1 for r in rows for e in r["exit"] if e and e["cyc_t"] <= 0.05)
print("  假出膛(轮内<0.05s) %d 个已剔除" % nfake, flush=True)
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

out = Path("simulation/mujoco/out/_r41_%s.json" % a.tag)
out.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
print("  saved", out, flush=True)
