# -*- coding: utf-8 -*-
"""Real 25-4 Super Speed model at several paddle speed setpoints; R5 vs R6."""
import json, math, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import r6_smooth as r6
import opt_lib as ol
import mujoco, numpy as np
pv2 = ol.pv2
OUT = Path("simulation/mujoco/out")
T_STALL, N_FREE = 0.530, 290.0
KV = T_STALL / (N_FREE * 2 * math.pi / 60.0)


def run(name, ctrl_rpm, sec=12.0, bx=145.0):
    ol.apply_geom(name)
    xml, ctrl = pv2.build_xml(1620.0, -1, ctrl_rpm * 2 * math.pi / 60.0, bx,
                              pv2.tray_top_z(bx) + pv2.BALL_R)
    xml = xml.replace('kv="0.08"', 'kv="%.6f"' % KV)
    xml = xml.replace('forcerange="-1.5 1.5"', 'forcerange="-%g %g"' % (T_STALL, T_STALL))
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
    pid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "paddle_joint")
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    aid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "paddle_vel")
    dt = m.opt.timestep
    tr = []
    for i in range(int(sec / dt)):
        mujoco.mj_step(m, d)
        if i % max(1, int(0.002 / dt)) == 0:
            p = d.xpos[bid]
            px, pz = float(p[0]) * 1000.0, float(p[2]) * 1000.0
            rx, rz = px - pv2.PADDLE_CX, pz - pv2.PADDLE_CZ
            lx, lz = pv2.to_shooter(px, pz)
            tr.append({"t": round(i * dt, 4), "x": round(px, 3), "z": round(pz, 3),
                       "v": round(float(np.linalg.norm(d.cvel[bid][3:])), 4),
                       "vx": round(float(d.cvel[bid][3]), 4),
                       "vz": round(float(d.cvel[bid][5]), 4),
                       "r": round(math.hypot(rx, rz), 3),
                       "ang": round(math.degrees(math.atan2(rz, rx)) % 360.0, 2),
                       "lx": round(lx, 3), "lz": round(lz, 3),
                       "pv": round(float(math.degrees(d.qvel[pid])), 2),
                       "pa": round(float(d.actuator_force[aid]), 4)})
    res = pv2.analyse(tr)
    win = [s for s in tr if 143.0 <= s["ang"] <= 232.0]
    if win:
        res["carry_rpm"] = round(float(np.mean([s["pv"] for s in win])) / 6.0, 2)
        res["carry_T"] = round(float(np.mean([abs(s["pa"]) for s in win])), 3)
    else:
        res["carry_rpm"] = None; res["carry_T"] = None
    return res


print("=== goBILDA 25-4 Super Speed model (kv=%.6f, forcerange +-0.530) ===" % KV)
print("geom  ctrl_rpm  launched  t_exit_s  carry_rpm  carry_T_Nm")
out = {}
for g in ("R5", "R6"):
    for cr in (90.0, 105.0, 145.0, 200.0, 290.0):
        r = run(g, cr)
        ex = r.get("exit", {})
        print("  %-4s %7.0f  %-8s %8s %10s %11s" % (g, cr, r["launched"],
              ("%.2f" % ex["t"]) if ex else "-", r["carry_rpm"], r["carry_T"]))
        out["%s_%g" % (g, cr)] = {"launched": r["launched"],
                                  "exit_t": ex.get("t") if ex else None,
                                  "exit_v": ex.get("speed_m_s") if ex else None,
                                  "carry_rpm": r["carry_rpm"], "carry_T": r["carry_T"]}
OUT.joinpath("_r7_motor_sweep.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("saved _r7_motor_sweep.json")
