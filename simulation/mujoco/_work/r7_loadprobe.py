# -*- coding: utf-8 -*-
"""Decisive check: is the carry load really ~0.52 N.m, or is the 25-4 model run anomalous?
Same R5 geometry under three actuator settings; log paddle rpm / torque in the
ball-angle window 143..232 deg."""
import json, math, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import r6_smooth as r6
import opt_lib as ol
import mujoco, numpy as np
pv2 = ol.pv2


def run(name, kv, ctrl_rpm, fr, sec=12.0, bx=145.0, tag=""):
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
            p = d.xpos[bid] * 1000.0
            px, pz = float(p[0]) * 1000.0, float(p[2]) * 1000.0
            rx, rz = px - pv2.PADDLE_CX, pz - pv2.PADDLE_CZ
            lx, lz = pv2.to_shooter(px, pz)
            ang = math.degrees(math.atan2(rz, rx)) % 360.0
            tr.append({"t": round(i * dt, 4), "ang": round(ang, 2),
                       "x": round(px, 3), "z": round(pz, 3),
                       "v": round(float(np.linalg.norm(d.cvel[bid][3:])), 4),
                       "vx": round(float(d.cvel[bid][3]), 4),
                       "vz": round(float(d.cvel[bid][5]), 4),
                       "r": round(math.hypot(rx, rz), 3),
                       "lx": round(lx, 3), "lz": round(lz, 3),
                       "pv": round(float(math.degrees(d.qvel[pid])), 2),
                       "pa": round(float(d.actuator_force[aid]), 4)})
    res = pv2.analyse(tr)
    win = [s for s in tr if 143.0 <= s["ang"] <= 232.0]
    rpm_mean = float(np.mean([s["pv"] for s in win])) / 6.0 if win else float("nan")
    tq_mean = float(np.mean([abs(s["pa"]) for s in win])) if win else float("nan")
    tq_max = max(abs(s["pa"]) for s in tr)
    print("  %-26s kv=%.6f ctrl=%6.1f rpm fr=%.3f -> launched=%-5s carry_rpm=%8.2f "
          "carry_T=%7.3f N.m peak_T=%.3f"
          % (tag, kv, ctrl_rpm, fr, res["launched"], rpm_mean, tq_mean, tq_max))
    return res, tr, rpm_mean, tq_mean


print("=== same R5 geometry, three actuator settings ===")
run("R5", 0.017452, 290.0, 0.530, tag="25-4 Super Speed model")
run("R5", 0.08, 145.0, 5.000, tag="stiff vel source @145rpm")
run("R5", 0.08, 145.0, 0.240, tag="DEC-0026 style @145rpm")

_, tr, _, _ = run("R5", 0.08, 145.0, 5.0, tag="trace for load curve")
print()
print("    t     ang   paddle_rpm   torque_Nm")
for s in tr:
    if abs(s["t"] * 20 - round(s["t"] * 20)) < 1e-6 and s["t"] <= 8.0:
        print("  %5.2f  %6.1f  %9.2f  %10.3f" % (s["t"], s["ang"], s["pv"] / 6.0, s["pa"]))
