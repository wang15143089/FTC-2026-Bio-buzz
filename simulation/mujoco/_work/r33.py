# -*- coding: utf-8 -*-
"""R33: 硅胶飞轮离心膨胀下的全流程复算（R27 共用送球段）。

与 R32 完全相同的几何/驱动，唯一区别：飞轮碰撞半径由 48.0 变为 48.0+dr。
安装的轮轴位置（half_spacing = nip/2 + 48）不变 —— 因为膨胀是轮子自己
长大，不是重新装配。于是夹口自动变成 nip - 2*dr。

额外做两件 R32 没做的事：
  1. 每一步检测“拨杆体 vs 飞轮体”的接触（MuJoCo 里两者都在 worldbody，
     真重叠就会报接触）。任何时刻出现接触即为设计失败。
  2. 采样两者之间的最小 geom 距离（mj_geomDistance），给出实际间隙。
"""
import math, sys, json
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import numpy as np
import mujoco
import r32 as R

pv2 = R.pv2
OUT = Path("simulation/mujoco/out")
BASE_R = 48.0
DR_LIST = (0.0, 1.0, 1.5, 2.0, 2.7, 3.7)


def geom_ids(m, body_name):
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, body_name)
    return [g for g in range(m.ngeom) if m.geom_bodyid[g] == bid], bid


def run_case(ball_name, bprm, hold, sw, dr):
    pv2.WHEEL_R = BASE_R + dr
    m, d, aid, jid, bid, ctrl, w = R.build(xc=R.XC, **bprm)
    pad_geoms, pad_bid = geom_ids(m, "paddle")
    fw_bid = {mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "flywheel_%s" % s)
              for s in ("upper", "lower")}
    fw_geoms = [g for g in range(m.ngeom) if m.geom_bodyid[g] in fw_bid]

    bgeom = {g for g in range(m.ngeom) if m.geom_bodyid[g] == bid}
    dt = m.opt.timestep
    n = int(8.0 / dt)
    k = max(1, int(round(0.004 / dt)))
    kq = max(1, int(round(0.0005 / dt)))
    ft = np.zeros(6)
    contact_steps, min_gap, min_gap_at = 0, 1e9, None
    tr, tq, released = [], [], False
    for i in range(n):
        t = i * dt
        J = R.D(d.qpos[jid])
        if t < hold:
            d.ctrl[aid] = 0.0
        elif not released and J < sw:
            d.ctrl[aid] = w
        else:
            released = True
            d.ctrl[aid] = 0.0
        mujoco.mj_step(m, d)
        if i % kq == 0:
            tq.append(abs(float(d.actuator_force[aid])))
        for c in d.contact[:d.ncon]:
            b1, b2 = m.geom_bodyid[c.geom1], m.geom_bodyid[c.geom2]
            if (b1 == pad_bid and b2 in fw_bid) or (b2 == pad_bid and b1 in fw_bid):
                contact_steps += 1
                break
        p = d.xpos[bid] * 1000.0
        rx, rz = p[0] - pv2.PADDLE_CX, p[2] - pv2.PADDLE_CZ
        if i % k == 0:
            lx, lz = pv2.to_shooter(p[0], p[2])
            tr.append({"t": round(t, 3), "x": round(float(p[0]), 2), "z": round(float(p[2]), 2),
                       "v": round(float(np.linalg.norm(d.cvel[bid][3:])), 3),
                       "vx": round(float(d.cvel[bid][3]), 3), "vz": round(float(d.cvel[bid][5]), 3),
                       "r": round(math.hypot(rx, rz), 2),
                       "ang": round(R.D(math.atan2(rz, rx)) % 360.0, 1),
                       "lx": round(lx, 2), "lz": round(lz, 2)})
            for gp in pad_geoms:
                for gf in fw_geoms:
                    try:
                        dist = mujoco.mj_geomDistance(m, d, gp, gf, 0.5, ft)
                    except Exception:
                        dist = -1.0
                    if 0.0 <= dist < min_gap:
                        min_gap, min_gap_at = dist, round(t, 3)
    res = pv2.analyse(tr)
    res["dr_mm"] = dr
    res["wheel_r_mm"] = round(BASE_R + dr, 2)
    res["nip_effective_mm"] = round(2 * pv2.HALF_SPACING - 2 * (BASE_R + dr), 2)
    res["pad_fw_contact_steps"] = contact_steps
    res["pad_fw_min_gap_mm"] = round(min_gap * 1000.0, 3) if min_gap < 1e8 else None
    res["pad_fw_min_gap_at_s"] = min_gap_at
    res["jam_frac"] = round(float(np.mean(np.array(tq) > 0.40)), 3)
    res["torque_peak_Nm"] = round(float(np.max(tq)), 3)
    res["min_r_mm"] = round(min(s["r"] for s in tr), 2)
    e = res.get("exit") or {}
    res["_row"] = (ball_name, dr, BASE_R + dr, res["nip_effective_mm"],
                   bool(res["launched"]), e.get("t"), e.get("speed_m_s"),
                   e.get("angle_deg"), res["jam_frac"], res["torque_peak_Nm"],
                   res["pad_fw_min_gap_mm"], contact_steps)
    res.pop("_trace", None)
    return res


def main():
    rows = []
    print("=== R33 硅胶飞轮离心膨胀 × R27 共用送球段（1620 rpm, mu=%.2f）===" % R.MU, flush=True)
    print("%-8s %5s %7s %8s %6s %7s %8s %8s %7s %8s %10s %6s"
          % ("ball", "dr", "R", "eff.nip", "判定", "t(s)", "v(m/s)", "角(deg)", "卡滞%", "峰值Nm",
             "拨杆-轮间隙", "接触"), flush=True)
    for dr in DR_LIST:
        for bname, bprm in R.BALLS.items():
            for cname, hold, sw in R.CASES:
                r = run_case(bname, bprm, hold, sw, dr)
                (b, dr_, Rw, nip, ok, tt, v, ang, jam, tqp, gap, cs) = r["_row"]
                print("%-8s %5.1f %7.2f %8.2f %6s %7s %8s %8s %7.0f %8.3f %10s %6d"
                      % (b, dr_, Rw, nip, "OK" if ok else "FAIL",
                         ("%.2f" % tt) if ok else "-", ("%.2f" % v) if ok else "-",
                         ("%.1f" % ang) if ok else "-", 100 * jam, tqp,
                         ("%.3f" % gap) if gap is not None else "-", cs), flush=True)
                rows.append(dict(ball=b, case=cname, dr=dr_, R=Rw, nip=nip, ok=ok, t=tt, v=v,
                                 ang=ang, jam=jam, tq_peak=tqp, gap=gap, contacts=cs,
                                 rng=r.get("range_same_height_m"), apex=r.get("apex_above_exit_mm")))
    OUT.joinpath("_r33_expansion.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1),
                                                   encoding="utf-8")
    bad = [r for r in rows if not r["ok"]]
    touch = [r for r in rows if r["contacts"]]
    print("\n=== %d/%d 通过；接触案例 %d ===" % (len(rows) - len(bad), len(rows), len(touch)), flush=True)
    for r in bad:
        print("  FAIL: %s dr=%.1f %s" % (r["ball"], r["dr"], r["case"]), flush=True)


if __name__ == "__main__":
    raise SystemExit(main())

