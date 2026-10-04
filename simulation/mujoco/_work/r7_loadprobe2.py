# -*- coding: utf-8 -*-
"""Correct-angle load probe: same R5 geometry, stiff velocity source, log ball r/ang + paddle torque."""
import math, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import r6_smooth as r6
import opt_lib as ol
import mujoco, numpy as np
pv2 = ol.pv2


def run(name, kv, ctrl_rpm, fr, sec=12.0, bx=145.0):
    ol.apply_geom(name)
    xml, ctrl = pv2.build_xml(1620.0, -1, ctrl_rpm * 2 * math.pi / 60.0, bx,
                              pv2.tray_top_z(bx) + pv2.BALL_R)
    xml = xml.replace('kv="0.08"', 'kv="%.6f"' % kv)
    xml = xml.replace('forcerange="-1.5 1.5"', 'forcerange="-%g %g"' % (fr, fr))
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
    return pv2.analyse(tr), tr


for tag, kv, rpm_c, fr in (("stiff@145   fr=5.0", 0.08, 145.0, 5.0),
                           ("25-4 model  fr=.53", 0.017452, 290.0, 0.530)):
    res, tr = run("R5", kv, rpm_c, fr)
    win = [s for s in tr if 143.0 <= s["ang"] <= 232.0]
    print("=== %s  launched=%s ===" % (tag, res["launched"]))
    if win:
        print("  carry window: t=%.2f..%.2f s  paddle=%.2f rpm  torque=%.3f N.m  r=%.1f..%.1f mm"
              % (win[0]["t"], win[-1]["t"], np.mean([s["pv"] for s in win]) / 6.0,
                 np.mean([abs(s["pa"]) for s in win]),
                 min(s["r"] for s in win), max(s["r"] for s in win)))
    else:
        print("  no sample with ball ang in 143..232")
    print("     t      x       z       r      ang   paddle_rpm  torque_Nm   ball_v")
    for s in tr:
        if abs(s["t"] * 10 - round(s["t"] * 10)) < 1e-6 and s["t"] <= 6.0:
            print("  %5.2f %7.1f %7.1f %7.1f %7.1f %9.2f %10.3f %8.3f"
                  % (s["t"], s["x"], s["z"], s["r"], s["ang"], s["pv"] / 6.0, s["pa"], s["v"]))
    print()
