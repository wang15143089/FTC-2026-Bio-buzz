"""r38 v2: 在 r37 基础上做 4 项改进（不改 r37 原文件）
  1) 出膛判据修正：必须先进入发射段(lx<20)再 lx>XLIM，否则托盘后段会误判
  2) 托板长度 TRAY_X1 / 停位相位 ph0 可调
  3) 逐球舵机曲线：每颗球可按球种给 SWEEP/hold/速度
  4) 可选弹性浮动夹口：按"即将进入夹口的球"设夹口（弹簧平衡态模型）
"""
import sys, os, math, json, argparse
import numpy as np
import mujoco
sys.path.insert(0, os.path.abspath("simulation/mujoco/_work"))
import r37_multiball as R

ap = argparse.ArgumentParser()
ap.add_argument("--tray", type=float, default=285.0)
ap.add_argument("--phases", default="150")
ap.add_argument("--mix", default="POLLEN,NECTAR,POLLEN,NECTAR")
ap.add_argument("--hold", type=float, default=3.0)
ap.add_argument("--sweep", type=float, default=248.0)
ap.add_argument("--sweep-net", type=float, default=0.0)   # NECTAR 专用扫掠，0=同 sweep
ap.add_argument("--sweep-pol", type=float, default=0.0)
ap.add_argument("--compliant", action="store_true")        # 弹性浮动夹口
ap.add_argument("--tag", default="v2")
a = ap.parse_args()

pv2 = R.pv2
R.TRAY_X1 = a.tray; R.SPILL_X = a.tray + 25.0
R._PROBE.clear()
mix = a.mix.split(",")
TMAP = {"NECTAR": a.sweep_net or a.sweep, "POLLEN": a.sweep_pol or a.sweep}


def build(mix, ph0, nip, mu=R.MU):
    m, d, aid, jid, meta, w, xml = R.build_multi(mix, ph0, nip, mu)
    return m, d, aid, jid, meta, w


def run_case(mix, ph0, nip, hold, compliant=False):
    m, d, aid, jid, meta, w = build(mix, ph0, nip)
    nb = len(mix)
    centres, stacked, in_ch = R.place_queue(mix, ph0)
    dt = m.opt.timestep
    t0 = R.SETTLE
    n = int((t0 + (nb + 2) * (R.T_ROT + hold) + 6.0) / dt)
    kt = max(1, int(round(0.002 / dt)))
    kq = max(1, int(round(0.05 / dt)))
    # 夹口几何：找到两个飞轮 body
    def set_nip(nip_mm):
        half = (nip_mm / 2.0 + R.WHEEL_R) * R.MM
        for lab, sg in (("upper", 1.0), ("lower", -1.0)):
            bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "flywheel_%s" % lab)
            assert bid >= 0, "flywheel body not found"
            wp = pv2.to_world(0.0, 0.0, sg * (nip_mm / 2.0 + R.WHEEL_R))
            m.body_pos[bid] = np.array(wp)
    set_nip(nip)
    tq, tr = [], [[] for _ in range(nb)]
    exits = [None] * nb
    spilled = [None] * nb
    inside = [False] * nb
    n_drive = 0
    done = [False] * nb
    phase, t_ph, kk = "settle", 0.0, 0
    J0 = None
    sweep_end = reindex_end = None
    for i in range(n):
        t = i * dt
        if phase == "settle":
            d.ctrl[aid] = 0.0
            if i == 0:
                for k, mt in enumerate(meta):
                    R.put(d, mt, *centres[k])
            if t + 0.5 * dt >= t0:
                phase, t_ph, kk = "settle_tail", t, 0
        J = R.D(d.qpos[jid])
        if compliant and phase != "settle":
            # 找最靠近夹口的球，按其球径设夹口（无球在夹口内时才允许改动）
            best = None
            for k, mt in enumerate(meta):
                if exits[k] or spilled[k]:
                    continue
                p = d.xpos[mt["bid"]] * 1000.0
                lx, ln = pv2.to_shooter(p[0], p[2])
                if -80.0 < lx < 60.0 and abs(ln) < 60.0:
                    if best is None or abs(lx) < best[0]:
                        best = (abs(lx), k)
            if best is not None:
                set_nip(R.SP[mix[best[1]]]["nip"])
        if phase == "settle_tail":
            d.ctrl[aid] = 0.0
            if t - t_ph >= hold:
                phase = "sweep"
                if J0 is None:
                    J0 = J
                sw = TMAP[mix[min(kk, nb - 1)]] if kk < nb else a.sweep
                sweep_end = J0 + 360.0 * kk + sw
                reindex_end = J0 + 360.0 * (kk + 1)
        elif phase in ("sweep", "reindex"):
            d.ctrl[aid] = w
            if phase == "sweep" and J >= sweep_end:
                phase = "reindex"
            if J >= reindex_end:
                phase, t_ph, kk = "settle_tail", t, kk + 1
        else:
            d.ctrl[aid] = 0.0
        mujoco.mj_step(m, d)
        if i % kt == 0:
            if phase != "settle" and n_drive == 0:
                n_drive = len(tq)
            tq.append(abs(float(d.actuator_force[aid])))
            for k, mt in enumerate(meta):
                p = d.xpos[mt["bid"]] * 1000.0
                lx, _ = pv2.to_shooter(p[0], p[2])
                if lx < 20.0:
                    inside[k] = True
                if exits[k] is None and inside[k] and lx > R.XLIM:
                    exits[k] = dict(t=round(t, 3),
                                    v=round(float(np.linalg.norm(d.cvel[mt["bid"]][3:])), 3),
                                    cyc=kk, cyc_t=round(max(t - t_ph, 0.0), 3),
                                    x=round(p[0], 1), z=round(p[2], 1))
                if spilled[k] is None and exits[k] is None and t > 1.0:
                    if p[0] > R.SPILL_X or p[2] < -20.0:
                        spilled[k] = dict(t=round(t, 2), x=round(p[0], 1), z=round(p[2], 1))
        if i % kq == 0:
            for k, mt in enumerate(meta):
                p = d.xpos[mt["bid"]] * 1000.0
                lx, _ = pv2.to_shooter(p[0], p[2])
                rx, rz = p[0] - pv2.PADDLE_CX, p[2] - pv2.PADDLE_CZ
                tr[k].append(dict(t=round(t, 2), x=round(p[0], 1), z=round(p[2], 1),
                                  v=round(float(np.linalg.norm(d.cvel[mt["bid"]][3:])), 2),
                                  ang=round(R.D(math.atan2(rz, rx)) % 360.0, 1),
                                  lx=round(lx, 1), J=round(R.D(d.qpos[jid]) % 360.0, 1)))
    tqa = np.array(tq[n_drive:]) if n_drive else np.array(tq)
    res = dict(mix=list(mix), ph0=ph0, nip=nip, tray=R.TRAY_X1, hold=hold,
               compliant=compliant,
               start=[(round(c[0], 1), round(c[1], 1)) for c in centres],
               stacked=stacked, in_channel=in_ch,
               n_launched=sum(1 for e in exits if e), exit=exits, spill=spilled,
               jam_frac=round(float(np.mean(tqa > 0.40)), 3),
               tq_peak=round(float(np.max(tqa)), 3), trace=tr)
    ok = [e for e in exits if e]
    if ok:
        res["t_total_s"] = round(max(e["t"] for e in ok) - t0, 2)
        res["cyc_mean_s"] = round(float(np.mean([e["cyc_t"] for e in ok])), 2)
    settled = []
    for tk in tr:
        ss = [q for q in tk if abs(q["t"] - t0) < 0.03]
        if ss:
            settled.append((round(ss[0]["x"], 1), round(ss[0]["z"], 1), ss[0]["ang"]))
    res["settled"] = settled
    return res


print("=== r38v2 mix=%s tray=%.0f ph0=%s hold=%.1f sweep=%.0f 弹性=%s ==="
      % (">".join(mix), R.TRAY_X1, a.phases, a.hold, a.sweep, a.compliant), flush=True)
rows = []
for ph0 in [float(x) for x in a.phases.split(",")]:
    nip = max(R.SP[x]["nip"] for x in mix)
    res = run_case(mix, ph0, nip, a.hold, a.compliant)
    rows.append(res)
    print("\n[ph0=%3.0f 叠放%d]" % (ph0, res["stacked"]), flush=True)
    for k, e in enumerate(res["exit"]):
        if e:
            print("   球%d %-6s 真出膛 t=%6.2f 轮内%5.2f v=%5.2f" % (k+1, mix[k], e["t"], e["cyc_t"], e["v"]), flush=True)
        else:
            sp = res["spill"][k]
            print("   球%d %-6s 未出膛%s" % (k+1, mix[k], ("  逸出t=%.1f@(%.0f,%.0f)" % (sp["t"], sp["x"], sp["z"])) if sp else ""), flush=True)
    print("   -> %d/%d  清空%s s  扭矩峰%.3f 卡滞%.0f%%" % (res["n_launched"], len(mix),
          res.get("t_total_s", "--"), res["tq_peak"], 100*res["jam_frac"]), flush=True)
n = sum(len(r["mix"]) for r in rows)
ok = [e for r in rows for e in r["exit"] if e]
real = [e for e in ok if e["v"] >= 3.0]
print("\n=== 汇总 %d 轮 %d 颗：出膛 %d/%d  其中 v>=3.0 的 %d 颗 ===" % (len(rows), n, len(ok), n, len(real)), flush=True)
tt = [r["t_total_s"] for r in rows if r.get("t_total_s")]
if tt: print("  平均清空 %.2f s 最慢 %.2f s" % (sum(tt)/len(tt), max(tt)), flush=True)
print("  全清轮 %d/%d" % (sum(1 for r in rows if r["n_launched"] == len(mix)), len(rows)), flush=True)
from pathlib import Path
Path("simulation/mujoco/out").joinpath("_r38_%s.json" % a.tag).write_text(
    json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
print("  saved _r38_%s.json" % a.tag, flush=True)
