# -*- coding: utf-8 -*-
"""R9c: full-flow control run with mu=1.0 and trace dumps to find the entry failure."""
import math, sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import r9_nest as R
import opt_lib as ol
import mujoco, numpy as np

pv2 = ol.pv2
T_STALL, N_FREE = 0.530, 290.0
KV = T_STALL / (N_FREE * 2 * math.pi / 60.0)
BASE = ol.GEOM["D 球窝抬高6.8"][0]


def trace(tag, mu, bx=145.0, sec=12.0, rpm=N_FREE, every=0.1, dump=False):
    pv2.static_geoms = BASE
    pv2.paddle_parts = ol.ORIG_PARTS
    xml, ctrl = pv2.build_xml(1620.0, -1, rpm * 2 * math.pi / 60.0, bx,
                              pv2.tray_top_z(bx) + pv2.BALL_R)
    xml = xml.replace('kv="0.08"', 'kv="%.6f"' % KV)
    xml = xml.replace('forcerange="-1.5 1.5"', 'forcerange="-%g %g"' % (T_STALL, T_STALL))
    xml = xml.replace('class="ball"><geom friction="1.0 0.02 0.0001"',
                      'class="ball"><geom friction="%g 0.02 0.0001"' % mu)
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    aid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "paddle_vel")
    dt = m.opt.timestep; n = int(sec / dt); k = max(1, int(every / dt))
    tr = []
    for i in range(n):
        mujoco.mj_step(m, d)
        if i % k == 0:
            p = d.xpos[bid] * 1000.0
            rx, rz = p[0] - pv2.PADDLE_CX, p[2] - pv2.PADDLE_CZ
            tr.append((i * dt, p[0], p[2], math.hypot(rx, rz),
                       math.degrees(math.atan2(rz, rx)) % 360.0,
                       float(np.linalg.norm(d.cvel[bid][3:])), abs(float(d.actuator_force[aid]))))
    r = pv2.analyse([{"t": a, "x": b, "z": c, "v": f, "r": dd, "ang": e, "lx": pv2.to_shooter(b, c)[0],
                      "lz": pv2.to_shooter(b, c)[1], "vx": 0.0, "vz": 0.0}
                     for (a, b, c, dd, e, f, g) in [t[:6] + (0,) and t for t in tr]])
    print("  %-14s launched=%-5s exit_t=%-6s exit_v=%-6s jam=%.0f%%"
          % (tag, r["launched"], (r.get("exit") or {}).get("t", "--"),
             (r.get("exit") or {}).get("speed_m_s", "--"),
             100 * float((np.array([t[6] for t in tr]) > 0.40).mean())), flush=True)
    if dump:
        for t in tr:
            print("     t=%6.2f x=%9.2f z=%8.2f r=%7.2f ang=%7.2f v=%8.3f T=%.3f" % t)
    return r


print("=== R9c full flow control, tray entry x=145, 12 s ===")
trace("mu=1.00", 1.00)
trace("mu=0.70", 0.70)
trace("mu=0.60", 0.60)
trace("mu=0.50", 0.50)
trace("mu=0.40", 0.40, dump=True)
