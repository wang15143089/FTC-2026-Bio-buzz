# -*- coding: utf-8 -*-
"""R34: 按“热态外径”配轮轴间距后的膨胀工况全流程复核（R27 共用送球段）。

物理：硅胶飞轮在 1620 rpm 下离心长大 dr。
  * 热态外半径 R_hot = 48 + dr
  * 发射时飞轮已在转速上，球看到的是运行夹口；按工程惯例把轮轴间距按热态
    外径装：half_spacing = nip/2 + R_hot，于是运行夹口仍是设计值 82 / 64。
  * 若按冷态（未补偿）装：运行夹口变成 nip - 2*dr，R33 已证明把 POLLEN 送球
    相位打乱（球掉进轮毂-叶片夹角）—— 那是装配误差而不是设计意图。

用法: --mode hot | cold
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
DR_LIST = (0.5, 1.0, 1.5, 2.0, 2.7)


def geom_ids(m, body_name):
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, body_name)
    return [g for g in range(m.ngeom) if m.geom_bodyid[g] == bid], bid


def run_case(ball_name, bprm, hold, sw, dr, mode):
    Rw = BASE_R + dr
    R.WHEEL_R = Rw                       # 决定安装间距（hot）或仅冷态尺寸（cold）
    pv2.WHEEL_R = Rw                     # 碰撞圆柱半径
    if mode == "cold":
        # 冷态装配：安装间距按冷态 96 mm 外径定，运行夹口自动缩小 2*dr
        pv2.HALF_SPACING = bprm["nip"] / 2.0 + BASE_R
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
    e = res.get("exit") or {}
    row = dict(mode=mode, ball=ball_name, dr=dr, R=Rw, half_spacing=round(pv2.HALF_SPACING, 2),
               nip=round(2 * pv2.HALF_SPACING - 2 * Rw, 2), case=None, ok=bool(res["launched"]),
               t=e.get("t"), v=e.get("speed_m_s"), ang=e.get("angle_deg"),
               jam=round(float(np.mean(np.array(tq) > 0.40)), 3),
               tq_peak=round(float(np.max(tq)), 3),
               gap=None if min_gap > 1e8 else round(min_gap * 1000.0, 3),
               contacts=contact_steps, rng=e.get("range_same_height_m"),
               apex=e.get("apex_above_exit_mm"))
    return row


def main():
    mode = "hot"
    for a in sys.argv[1:]:
        if a.startswith("--mode="):
            mode = a.split("=", 1)[1]
    rows = []
    print("=== R34 膨胀工况（%s 装配） 1620 rpm  mu=%.2f ==="
          % ("热态配间距" if mode == "hot" else "冷态装配", R.MU), flush=True)
    print("%-8s %5s %7s %11s %8s %6s %7s %8s %8s %7s %10s %6s"
          % ("ball", "dr", "R_hot", "half_space", "run.nip", "判定", "t(s)", "v(m/s)",
             "角(deg)", "卡滞%", "拨杆-轮间隙", "接触"), flush=True)
    for dr in DR_LIST:
        for bname, bprm in R.BALLS.items():
            for cname, hold, sw in R.CASES:
                r = run_case(bname, bprm, hold, sw, dr, mode)
                r["case"] = cname
                print("%-8s %5.1f %7.2f %11.2f %8.2f %6s %7s %8s %8s %7.0f %10s %6d"
                      % (r["ball"], r["dr"], r["R"], r["half_spacing"], r["nip"],
                         "OK" if r["ok"] else "FAIL",
                         ("%.2f" % r["t"]) if r["ok"] else "-",
                         ("%.2f" % r["v"]) if r["ok"] else "-",
                         ("%.1f" % r["ang"]) if r["ok"] else "-", 100 * r["jam"],
                         ("%.3f" % r["gap"]) if r["gap"] is not None else "-", r["contacts"]),
                      flush=True)
                rows.append(r)
    OUT.joinpath("_r34_expansion_%s.json" % mode).write_text(
        json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    bad = [r for r in rows if not r["ok"]]
    touch = [r for r in rows if r["contacts"]]
    print("\n=== %d/%d 通过；飞轮-拨杆接触 %d 例；最小间隙 %.3f mm ==="
          % (len(rows) - len(bad), len(rows), len(touch),
             min(r["gap"] for r in rows if r["gap"] is not None)), flush=True)
    for r in bad:
        print("  FAIL %s dr=%.1f %s" % (r["ball"], r["dr"], r["case"]), flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
