# -*- coding: utf-8 -*-
"""R32: R27 共用送球段全流程仿真（NECTAR + POLLEN，各自的正确飞轮夹口）。

几何口径 = R27（DEC-0031）：外罩/托盘/拨杆与 R26 相同，差异是 R27 在外罩球道
外侧（r > 107.974）做的 0.5 mm 让位。球实际接触的内弧面未变，所以本仿真的接触
几何与 R26 一致；让位不侵入球道由 CAD 的 19 点球道扫描独立证明为 0 mm3。

驱动 = 索引式：停 hold 秒 -> 一次连续扫掠 sw 度 -> 释放。
"""
import math, sys, json
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import opt_lib as ol
import r10_cradle as R10
import mujoco, numpy as np

pv2 = ol.pv2
OUT = Path("simulation/mujoco/out")
R_IN, CUT_X, A_LIP, TRAY_X1, TILT, WHEEL_R = 107.974, 38.901, 275.0, 150.0, 5.0, 48.0
PIVOT = (-0.806, 0.423)
T_STALL, RPM = 0.530, 290.0
MU = 0.40
SIN_T, COS_T = math.sin(math.radians(TILT)), math.cos(math.radians(TILT))
D = math.degrees


def parts(phases=(330.0, 150.0), hub_r=12.0):
    def f():
        out = [("hub", (0., 0., 0.), (hub_r, 17.), 0.0, "cylY")]
        for i, a in enumerate(phases, 1):
            out += [("arm_%d" % i, (28., 0., 0.), (18., 9., 5.), a, "box"),
                    ("blade_%d" % i, (52., 0., 0.), (6., pv2.PADDLE_W / 2., 15.), a, "box"),
                    ("flex_%d" % i, (58., 0., 0.), (2., pv2.PADDLE_W / 2., 17.), a, "box")]
        return out
    return f


def build(ball_r, ball_m, nip, xc, rpm=RPM, mu=MU):
    """按 R32 口径构造模型（与 run() 完全相同），供 run 与可视化脚本复用。
    返回 (m, d, aid, jid, bid, ctrl, w)。"""
    pv2.HALF_SPACING = nip / 2.0 + WHEEL_R
    pv2.R_CARRY = R_IN - ball_r
    pv2.PIVOT_X, pv2.PIVOT_Z = PIVOT
    pv2.R_IN = R_IN; pv2.R_OUT = R_IN + pv2.SHELL_WALL
    R10.R_MID = R_IN + 3.5
    pv2.BALL_R = ball_r; pv2.BALL_MASS = ball_m
    pv2.static_geoms = (lambda: R10.stat(CUT_X, A_LIP, tray_x1=TRAY_X1))
    pv2.paddle_parts = parts()
    bx = xc - ball_r * SIN_T
    bz = pv2.tray_top_z(xc) + ball_r * COS_T
    w = rpm * 2 * math.pi / 60.0
    xml, ctrl = pv2.build_xml(1620.0, -1, 0.0, bx, bz)
    xml = xml.replace('kv="0.08"', 'kv="%.6f"' % (T_STALL / w))
    xml = xml.replace('forcerange="-1.5 1.5"', 'forcerange="-%g %g"' % (T_STALL, T_STALL))
    xml = xml.replace('class="ball"><geom friction="1.0 0.02 0.0001"',
                      'class="ball"><geom friction="%g 0.02 0.0001"' % mu)
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    aid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "paddle_vel")
    jid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "paddle_joint")
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    d.ctrl[:] = [ctrl[0], ctrl[1], 0.0]
    mujoco.mj_forward(m, d)
    return m, d, aid, jid, bid, ctrl, w


def run(ball_r, ball_m, nip, xc, hold, sw, rpm=RPM, t_end=8.0, mu=MU):
    m, d, aid, jid, bid, ctrl, w = build(ball_r, ball_m, nip, xc, rpm, mu)
    bgeom = {g for g in range(m.ngeom) if m.geom_bodyid[g] == bid}
    dt = m.opt.timestep; n = int(t_end / dt)
    k = max(1, int(round(0.004 / dt))); kq = max(1, int(round(0.0005 / dt)))
    tr, tq, released, touched = [], [], False, set()
    t0 = sorted({mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM,
                 int(c.geom2 if c.geom1 in bgeom else c.geom1))
                 for c in d.contact[:d.ncon] if (c.geom1 in bgeom or c.geom2 in bgeom)})
    for i in range(n):
        t = i * dt; J = D(d.qpos[jid])
        if t < hold:
            d.ctrl[aid] = 0.0
        elif not released and J < sw:
            d.ctrl[aid] = w
        else:
            released = True; d.ctrl[aid] = 0.0
        mujoco.mj_step(m, d)
        if i % kq == 0:
            tq.append(abs(float(d.actuator_force[aid])))
        p = d.xpos[bid] * 1000.0
        rx, rz = p[0] - pv2.PADDLE_CX, p[2] - pv2.PADDLE_CZ
        r = math.hypot(rx, rz)
        if i % k == 0:
            names = {mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM,
                     int(cc.geom2 if cc.geom1 in bgeom else cc.geom1))
                     for cc in d.contact[:d.ncon] if (cc.geom1 in bgeom or cc.geom2 in bgeom)}
            touched |= names
            lx, lz = pv2.to_shooter(p[0], p[2])
            tr.append({"t": round(t, 3), "x": round(float(p[0]), 2), "z": round(float(p[2]), 2),
                       "v": round(float(np.linalg.norm(d.cvel[bid][3:])), 3),
                       "vx": round(float(d.cvel[bid][3]), 3), "vz": round(float(d.cvel[bid][5]), 3),
                       "r": round(r, 2), "ang": round(D(math.atan2(rz, rx)) % 360.0, 1),
                       "J": round(D(d.qpos[jid]) % 360.0, 1), "lx": round(lx, 2),
                       "lz": round(lz, 2), "touch": ",".join(sorted(x for x in names if x)) or "-"})
    res = pv2.analyse(tr)
    res["jam_frac"] = round(float(np.mean(np.array(tq) > 0.40)), 3)
    res["torque_peak_Nm"] = round(float(np.max(tq)), 3)
    res["min_r_mm"] = round(min(s["r"] for s in tr), 2)
    # 让位区从未被球触及的仿真侧证据：只取球还在外罩扇区（142..275 deg）内的采样，
    # 看球外缘半径有没有超过内弧面 107.974。
    sect = [s for s in tr if 142.0 <= s["ang"] <= 276.0]
    res["sector_samples"] = len(sect)
    res["sector_max_ball_outer_r_mm"] = round(max(s["r"] for s in sect) + ball_r, 3)
    res["sector_jaw_mm"] = round(R_IN - res["sector_max_ball_outer_r_mm"], 3)
    res["max_z_mm"] = round(max(s["z"] for s in tr), 2)
    res["contacts"] = sorted(x for x in touched if x)
    res["touched_at_t0"] = t0
    # 存盘的 trace 降采样到 20 ms（完整采样 4 ms 可用本脚本 17 s 重生），避免 JSON 过大
    res["_trace"] = tr[::5]
    return res


BALLS = {"NECTAR": dict(ball_r=45.974, ball_m=0.130, nip=82.0),
         "POLLEN": dict(ball_r=35.56, ball_m=0.060, nip=64.0)}
CASES = [("A 停1.2s/扫248", 1.2, 248.0),
         ("B 停3.0s/扫248", 3.0, 248.0),
         ("C 停3.0s/扫260", 3.0, 260.0)]
XC = 108.0


def main():
    rows = []
    print("=== R32  R27 共用送球段全流程（索引式驱动，mu=%.2f，飞轮 1620 rpm）===" % MU, flush=True)
    for bname, bprm in BALLS.items():
        print("\n[%s] 球 D=%.3f mm  r=%.3f mm  m=%.3f kg  夹口 %.0f mm" %
              (bname, 2 * bprm["ball_r"], bprm["ball_r"], bprm["ball_m"], bprm["nip"]), flush=True)
        print("  %-14s %-6s %-7s %-7s %-7s %-8s %-10s %s" %
              ("case", "t(s)", "v(m/s)", "角(deg)", "卡滞%", "min_r", "扇区球外缘r", "判定"), flush=True)
        for cname, hold, sw in CASES:
            r = run(xc=XC, hold=hold, sw=sw, **bprm)
            e = r.get("exit") or {}
            ok = bool(r["launched"])
            print("  %-14s %-6s %-7s %-7s %-7s %-8s %-10s %s" %
                  (cname, ("%.2f" % e["t"]) if ok else "-",
                   ("%.2f" % e["speed_m_s"]) if ok else "-",
                   ("%.1f" % e["angle_deg"]) if ok else "-",
                   "%.0f" % (100 * r["jam_frac"]), r["min_r_mm"],
                   r["sector_max_ball_outer_r_mm"], "OK" if ok else "FAIL"), flush=True)
            rows.append(dict(ball=bname, case=cname, hold=hold, sweep=sw, nip=bprm["nip"],
                             ok=ok, t=e.get("t"), v=e.get("speed_m_s"), ang=e.get("angle_deg"),
                             apex=e.get("apex_above_exit_mm"), rng=e.get("range_same_height_m"),
                             jam=r["jam_frac"], tq_peak=r["torque_peak_Nm"],
                             min_r=r["min_r_mm"], sector_n=r["sector_samples"],
                             sector_max_r=r["sector_max_ball_outer_r_mm"],
                             sector_jaw=r["sector_jaw_mm"], max_z=r["max_z_mm"],
                             reached142=r["reached_142deg_exit"], passed_nip=r["passed_nip"],
                             entered=r["entered_shell"], contacts=r["contacts"], t0=r["touched_at_t0"],
                             trace=r["_trace"]))
    OUT.joinpath("_r32_r27_full.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1),
                                                  encoding="utf-8")
    nok = sum(1 for r in rows if r["ok"])
    print("\n=== 汇总：%d/%d 通过 ===" % (nok, len(rows)), flush=True)
    print("saved", OUT / "_r32_r27_full.json", flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
