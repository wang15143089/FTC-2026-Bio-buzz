"""r38 v8: 夹口 = 真实调隙舵机两档刚性定位（无弹性件）

- 删除 r38_v3/v4/v6 中自加的扎带 spring_patch 假设（已 superseded）。
- 夹口只由几何给出：半间距 = nip/2 + WHEEL_R(48)；
  NECTAR 82 -> 89，POLLEN 64 -> 80（与 config/parameters.yaml 的冷/热态一致）。
- 档位切换按真实机构「位置指令」实现：换球保持段内换到对应档模型，
  并把 qpos/qvel/ctrl 整段搬运（两模型 body/joint 顺序相同，nq/nv 相等）。
  真实舵机只需转约 54 deg（曲柄 42.41 -> 96.68 deg），切换代价可忽略。
- 只在本文件内实现，不触碰 r37_* / pollen_v2_sim.py。
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
ap.add_argument("--sweep-net", type=float, default=0.0)
ap.add_argument("--sweep-pol", type=float, default=0.0)
ap.add_argument("--qgap", type=float, default=0.6)
ap.add_argument("--nip-net", type=float, default=0.0)   # 覆盖 NECTAR 运行夹口
ap.add_argument("--nip-pol", type=float, default=0.0)   # 覆盖 POLLEN 运行夹口
ap.add_argument("--budget", type=float, default=30.0)  # 每颗球允许的仿真秒数上限
ap.add_argument("--tmax", type=float, default=0.0)     # >0 时直接给定仿真总秒数
ap.add_argument("--mu", type=float, default=0.6)          # 塑料光球 / 0.4mm 层高 PET
ap.add_argument("--hold-map", default="")
ap.add_argument("--spd-map", default="")
ap.add_argument("--tag", default="v8")
ap.add_argument("--sw-delay", type=float, default=0.25)  # 上一颗出膛后等球飞离夹口再换档
ap.add_argument("--dbg", action="store_true")
a = ap.parse_args()

pv2 = R.pv2
R.TRAY_X1 = a.tray; R.SPILL_X = a.tray + 25.0; R.GAP = a.qgap; R._PROBE.clear()
mix = a.mix.split(",")
nb = len(mix)
if a.nip_net > 0:
    R.SP["NECTAR"]["nip"] = a.nip_net
if a.nip_pol > 0:
    R.SP["POLLEN"]["nip"] = a.nip_pol
TMAP = {"NECTAR": a.sweep_net or a.sweep, "POLLEN": a.sweep_pol or a.sweep}

NIP = {nm: R.SP[nm]["nip"] for nm in ("POLLEN", "NECTAR")}
HS = {nm: NIP[nm] / 2.0 + R.WHEEL_R for nm in NIP}
SEQ = [NIP[nm] for nm in mix]


def _pmap(s, dflt):
    out = {}
    for it in (s or "").split(","):
        if ":" in it:
            k, v = it.split(":")
            out[k.strip().upper()] = float(v)
    if not out:
        out = {"POLLEN": dflt, "NECTAR": dflt}
    out.setdefault("POLLEN", dflt)
    out.setdefault("NECTAR", dflt)
    return out


HOLD = _pmap(a.hold_map, a.hold)
SPD = _pmap(a.spd_map, 1.0)


def build_models(ph0):
    out = {}
    for nip in sorted(set(SEQ)):
        out[nip] = R.build_multi(list(mix), ph0, nip, a.mu)
    return out


def xfer(src, dst, nip):
    ms, ds = src[0], src[1]
    md, dd = dst[0], dst[1]
    assert md.nq == ms.nq and md.nv == ms.nv, "档位模型结构不一致，不可搬运状态"
    dd.qpos[:] = ds.qpos[:]
    dd.qvel[:] = ds.qvel[:]
    if md.na:
        dd.act[:] = ds.act[:]
    dd.ctrl[:] = ds.ctrl[:]
    mujoco.mj_forward(md, dd)
    return nip


def run_case(ph0, hold):
    MOD = build_models(ph0)
    cur_nip = SEQ[0]
    m, d, aid, jid, meta, w, xml = MOD[cur_nip]
    centres, stacked, in_ch = R.place_queue(list(mix), ph0)
    FW, ball_of = set(), {}
    for lab in ("upper", "lower"):
        for nm in ("fw_shaft_%s" % lab, "fw_%s_1" % lab, "fw_%s_2" % lab):
            gi = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, nm)
            if gi >= 0:
                FW.add(gi)
    for k, mt in enumerate(meta):
        for gi in range(m.ngeom):
            if int(m.geom_bodyid[gi]) == mt["bid"]:
                ball_of[gi] = k
    dt = m.opt.timestep
    t0 = R.SETTLE
    n = int((t0 + (nb + 2) * max(R.T_ROT + hold, a.budget) + 6.0) / dt)
    if a.tmax > 0:
        n = int(a.tmax / dt)
    kt = max(1, int(round(0.002 / dt)))
    kq = max(1, int(round(0.05 / dt)))
    tq, tr = [], [[] for _ in range(nb)]
    exits = [None] * nb; spilled = [None] * nb
    inside = [False] * nb
    cf = [0.0] * nb; cf_at = [None] * nb; cf_sum = [0.0] * nb
    minln = [999.0] * nb; n_drive = 0
    gap_log = [(0.0, cur_nip)]
    phase, t_ph, kk = "settle", 0.0, 0
    pend, pend_t = SEQ[0], None
    J0 = None; sweep_end = reindex_end = None
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
        if phase == "settle_tail":
            d.ctrl[aid] = 0.0
            if t - t_ph >= (HOLD[mix[kk]] if kk < nb else hold):
                phase = "sweep"
                if J0 is None:
                    J0 = J
                sw = TMAP[mix[kk]] if kk < nb else a.sweep
                sweep_end = J0 + 360.0 * kk + sw
                reindex_end = J0 + 360.0 * (kk + 1)
        elif phase in ("sweep", "reindex"):
            d.ctrl[aid] = w * (SPD[mix[kk]] if kk < nb else 1.0)
            if phase == "sweep" and J >= sweep_end:
                phase = "reindex"
            if J >= reindex_end:
                phase, t_ph, kk = "settle_tail", t, kk + 1
        else:
            d.ctrl[aid] = 0.0
        mujoco.mj_step(m, d)
        if d.ncon:
            for ci in range(d.ncon):
                c = d.contact[ci]
                if c.geom1 in FW:
                    k = ball_of.get(c.geom2)
                elif c.geom2 in FW:
                    k = ball_of.get(c.geom1)
                else:
                    continue
                if k is None:
                    continue
                f6 = np.zeros(6); mujoco.mj_contactForce(m, d, ci, f6)
                fm = float(np.linalg.norm(f6[:3]))
                cf_sum[k] += fm * dt
                if fm > cf[k]:
                    p = d.xpos[meta[k]["bid"]] * 1000.0
                    lx, ln = pv2.to_shooter(p[0], p[2])
                    cf[k] = fm
                    cf_at[k] = (round(t, 2), round(lx, 1), round(ln, 1),
                                round(float(np.linalg.norm(d.cvel[meta[k]["bid"]][3:])), 2))
        if i % kt == 0:
            if phase != "settle" and n_drive == 0:
                n_drive = len(tq)
            tq.append(abs(float(d.actuator_force[aid])))
            for k, mt in enumerate(meta):
                p = d.xpos[mt["bid"]] * 1000.0
                lx, ln = pv2.to_shooter(p[0], p[2])
                if abs(lx) < 15.0:
                    minln[k] = min(minln[k], abs(ln))
                if abs(lx) < 15.0 and abs(ln) < 70.0:
                    inside[k] = True
                if exits[k] is None and inside[k] and lx > R.XLIM and abs(ln) < 80.0:
                    exits[k] = dict(t=round(t, 3),
                                    v=round(float(np.linalg.norm(d.cvel[mt["bid"]][3:])), 3),
                                    cyc=kk, cyc_t=round(max(t - t_ph, 0.0), 3),
                                    x=round(p[0], 1), z=round(p[2], 1), ln=round(ln, 1),
                                    minln=round(minln[k], 1) if minln[k] < 999 else None)
                if spilled[k] is None and exits[k] is None and t > 1.0:
                    if p[0] > R.SPILL_X or p[2] < -20.0:
                        spilled[k] = dict(t=round(t, 2), x=round(p[0], 1), z=round(p[2], 1))
        if i % kt == 0:
            nxt = None
            for k in range(nb):
                if exits[k] is None and spilled[k] is None:
                    nxt = SEQ[k]
                    break
            if nxt is not None and nxt != pend:
                pend, pend_t = nxt, t
            if pend is not None and pend != cur_nip and pend_t is not None \
               and t - pend_t >= a.sw_delay:
                cur_nip = xfer(MOD[cur_nip], MOD[pend], pend)
                m, d, aid, jid, meta, w, xml = MOD[cur_nip]
                FW.clear(); ball_of.clear()
                for lab in ("upper", "lower"):
                    for nm in ("fw_shaft_%s" % lab, "fw_%s_1" % lab, "fw_%s_2" % lab):
                        gi = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, nm)
                        if gi >= 0:
                            FW.add(gi)
                for k2, mt2 in enumerate(meta):
                    for gi in range(m.ngeom):
                        if int(m.geom_bodyid[gi]) == mt2["bid"]:
                            ball_of[gi] = k2
                gap_log.append((round(t, 2), cur_nip))
                print("   [换档] t=%6.2f -> 夹口%.0f（伺服行程约 54 deg）" % (t, cur_nip), flush=True)
        if kk > nb and all((exits[k] is not None) or (spilled[k] is not None)
                           for k in range(nb)):
            break
        if a.dbg and i % kt == 0 and (i // kt) % 60 == 0:
            print("   DBG t=%6.2f phase=%-11s kk=%d nip=%.0f J=%7.1f" % (t, phase, kk, cur_nip, J), flush=True)
        if i % kq == 0:
            for k, mt in enumerate(meta):
                p = d.xpos[mt["bid"]] * 1000.0
                lx, ln = pv2.to_shooter(p[0], p[2])
                rx, rz = p[0] - pv2.PADDLE_CX, p[2] - pv2.PADDLE_CZ
                tr[k].append(dict(t=round(t, 2), x=round(p[0], 1), z=round(p[2], 1),
                                  v=round(float(np.linalg.norm(d.cvel[mt["bid"]][3:])), 2),
                                  ang=round(R.D(math.atan2(rz, rx)) % 360.0, 1),
                                  lx=round(lx, 1), ln=round(ln, 1),
                                  J=round(R.D(d.qpos[jid]) % 360.0, 1)))
    tqa = np.array(tq[n_drive:]) if n_drive else np.array(tq)
    res = dict(mix=list(mix), ph0=ph0, nip_seq=SEQ, hs_seq=[HS[nm] for nm in mix],
               gap_switch=gap_log, mu=a.mu, hold_map=dict(HOLD), spd_map=dict(SPD),
               tray=R.TRAY_X1, hold=hold,
               start=[(round(c[0], 1), round(c[1], 1)) for c in centres],
               stacked=stacked, in_channel=in_ch,
               n_launched=sum(1 for e in exits if e), exit=exits, spill=spilled,
               wheel_peak=[round(x, 1) for x in cf],
               wheel_imp=[round(x, 3) for x in cf_sum],
               wheel_peak_at=cf_at, minln=[(round(x, 1) if x < 999 else None) for x in minln],
               jam_frac=round(float(np.mean(tqa > 0.40)), 3),
               tq_peak=round(float(np.max(tqa)), 3), trace=tr)
    ok = [e for e in exits if e]
    res["n_real"] = sum(1 for e in ok if e["v"] >= 3.0)
    if ok:
        res["t_total_s"] = round(max(e["t"] for e in ok) - t0, 2)
        res["cyc_mean_s"] = round(float(np.mean([e["cyc_t"] for e in ok])), 2)
    return res


print("=== r38v8(舵机两档) mix=%s tray=%.0f ph0=%s 夹口P=%.0f/N=%.0f mu=%.2f 保持P%.2f/N%.2f 转速P%.2f/N%.2f ==="
      % (">".join(mix), R.TRAY_X1, a.phases, NIP["POLLEN"], NIP["NECTAR"], a.mu,
         HOLD["POLLEN"], HOLD["NECTAR"], SPD["POLLEN"], SPD["NECTAR"]), flush=True)
rows = []
for ph0 in [float(x) for x in a.phases.split(",")]:
    res = run_case(ph0, a.hold)
    rows.append(res)
    print("\n[ph0=%3.0f 叠放%d 档位切换%s]" % (ph0, res["stacked"], res["gap_switch"]), flush=True)
    for k, e in enumerate(res["exit"]):
        tag = ("夹口%.0f 飞轮峰%6.1fN 冲量%.3fNs 最近ln=%s"
               % (SEQ[k], res["wheel_peak"][k], res["wheel_imp"][k], res["minln"][k]))
        if e:
            print("   球%d %-6s t=%6.2f 轮内%5.2f v=%5.2f %s  %s"
                  % (k + 1, mix[k], e["t"], e["cyc_t"], e["v"],
                     "真出膛" if e["v"] >= 3.0 else "速度不足", tag), flush=True)
        else:
            sp = res["spill"][k]
            print("   球%d %-6s 未出膛%s  %s"
                  % (k + 1, mix[k], ("  逸出t=%.1f@(%.0f,%.0f)" % (sp["t"], sp["x"], sp["z"])) if sp else "", tag), flush=True)
    print("   -> 出膛 %d/%d 真出膛 %d  清空%s s 扭矩峰%.3f 卡滞%.0f%%"
          % (res["n_launched"], len(mix), res["n_real"], res.get("t_total_s", "--"),
             res["tq_peak"], 100 * res["jam_frac"]), flush=True)
n = sum(len(r["mix"]) for r in rows)
ok = [e for r in rows for e in r["exit"] if e]
real = [e for r in rows for e in r["exit"] if e and e["v"] >= 3.0]
full = sum(1 for r in rows if r["n_launched"] == len(r["mix"]))
print("\n=== 汇总 %d 轮 %d 颗：出膛 %d/%d  真出膛(v>=3.0) %d/%d  全清轮 %d/%d ==="
      % (len(rows), n, len(ok), n, len(real), n, full, len(rows)), flush=True)
from pathlib import Path
Path("simulation/mujoco/out").joinpath("_r38_%s.json" % a.tag).write_text(
    json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
print("  saved _r38_%s.json" % a.tag, flush=True)
