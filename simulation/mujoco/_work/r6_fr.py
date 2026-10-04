# -*- coding: utf-8 -*-
"""What does the paddle really do when the torque clamp is tightened?"""
import math, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import r6_smooth as r6
import opt_lib as ol
import mujoco

pv2 = ol.pv2


def probe(name, rpm, fr, bx=145.0, sec=12.0):
    ol.apply_geom(name)
    xml, ctrl = pv2.build_xml(1620.0, -1, rpm * 2 * math.pi / 60.0, bx,
                              pv2.tray_top_z(bx) + pv2.BALL_R)
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
        if i % int(0.002 / dt) == 0:
            p = d.xpos[bid] * 1000.0
            tr.append({"t": i * dt, "x": p[0], "z": p[2],
                       "v": float((d.cvel[bid][3:] ** 2).sum() ** 0.5),
                       "w": float(d.qvel[pid]),
                       "a": float(d.actuator_force[aid]),
                       "ang": math.degrees(math.atan2(p[2] - pv2.PADDLE_CZ, p[0] - pv2.PADDLE_CX)) % 360.0})
    res = pv2.analyse([{"t": round(s["t"], 4), "x": round(s["x"], 3), "z": round(s["z"], 3),
                        "v": round(s["v"], 4), "vx": 0.0, "vz": 0.0,
                        "r": round(math.hypot(s["x"] - pv2.PADDLE_CX, s["z"] - pv2.PADDLE_CZ), 3),
                        "ang": round(s["ang"], 2), "lx": round(pv2.to_shooter(s["x"], s["z"])[0], 3),
                        "lz": round(pv2.to_shooter(s["x"], s["z"])[1], 3)} for s in tr])
    # window: while the ball is inside the drum band 45<r<70 and 143<ang<232
    win = [s for s in tr if 143.0 <= s["ang"] <= 232.0]
    import numpy as np
    if win:
        w = np.array([s["w"] for s in win]); a = np.array([abs(s["a"]) for s in win])
        v = np.array([s["v"] for s in win])
        info = "carry rpm=%.1f  torque=%.3f Nm  vball=%.3f m/s  t=%.2f..%.2f" % (
            np.mean(w) * 60 / 2 / math.pi, np.mean(a), np.mean(v), win[0]["t"], win[-1]["t"])
    else:
        info = "never entered drum band"
    print("  %s @%3g rpm fr=%.2f : launched=%-5s exit=%-5s %s"
          % (name, rpm, fr, res["launched"], res.get("reached_142deg_exit"), info))
    return tr


R = {}
for fr in (0.24, 0.40, 0.75, 1.00):
    R[fr] = probe("R5", 90.0, fr)
print()
for fr in (0.24, 0.40, 0.75, 1.00):
    probe("R6", 90.0, fr)
print()
for fr in (0.24, 0.40, 0.60):
    probe("R6", 105.0, fr)
print()
tr = R[0.24]
print("R5 fr=0.24 fine trace (0.2 s):")
print("   t      x       z      r     ang     v     w_deg/s  act")
for s in tr:
    if abs(s["t"] * 5 - round(s["t"] * 5)) < 1e-6 and s["t"] <= 6.0:
        r = math.hypot(s["x"] - pv2.PADDLE_CX, s["z"] - pv2.PADDLE_CZ)
        print("  %5.2f %7.2f %7.2f %6.2f %7.1f %6.3f %9.1f %6.3f"
              % (s["t"], s["x"], s["z"], r, s["ang"], s["v"], math.degrees(s["w"]), s["a"]))
