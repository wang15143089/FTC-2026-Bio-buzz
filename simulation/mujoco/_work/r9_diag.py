# -*- coding: utf-8 -*-
"""Diagnose why low ball friction stops the ball on the R5 tray."""
import math, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import r6_smooth as r6
import opt_lib as ol
import mujoco, numpy as np

pv2 = ol.pv2
T_STALL, N_FREE = 0.530, 290.0
KV = T_STALL / (N_FREE * 2 * math.pi / 60.0)
STAT_R5, PART_R5 = ol.GEOM["R5"]
BID = None


def diag(mu, sec=2.0, bx=145.0, tag=""):
    pv2.static_geoms, pv2.paddle_parts = STAT_R5, PART_R5
    xml, ctrl = pv2.build_xml(1620.0, -1, N_FREE * 2 * math.pi / 60.0, bx,
                              pv2.tray_top_z(bx) + pv2.BALL_R)
    xml = xml.replace('kv="0.08"', 'kv="%.6f"' % KV)
    xml = xml.replace('forcerange="-1.5 1.5"', 'forcerange="-%g %g"' % (T_STALL, T_STALL))
    xml = xml.replace('class="ball"><geom friction="1.0 0.02 0.0001"',
                      'class="ball"><geom friction="%g 0.02 0.0001"' % mu)
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    bgeom = {g for g in range(m.ngeom) if m.geom_bodyid[g] == bid}
    fr = [round(float(x), 3) for x in m.geom_friction[list(bgeom)[0]]]
    print("### mu=%.2f  ball geom friction=%s  mass=%.4f kg" % (mu, fr, m.body_mass[bid]))
    d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
    dt = m.opt.timestep; n = int(sec / dt); k = max(1, int(0.1 / dt))
    for i in range(n):
        mujoco.mj_step(m, d)
        if i % k:
            continue
        p = d.xpos[bid] * 1000.0
        v = float(np.linalg.norm(d.cvel[bid][3:])) * 1000.0
        rx, rz = p[0] - pv2.PADDLE_CX, p[2] - pv2.PADDLE_CZ
        names = []
        for c in range(d.ncon):
            con = d.contact[c]
            if con.geom1 in bgeom or con.geom2 in bgeom:
                other = con.geom2 if con.geom1 in bgeom else con.geom1
                names.append(mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, int(other)) or "?")
        print("  t=%5.2f x=%8.2f z=%8.2f v=%7.2f r=%7.2f ang=%7.2f  contacts=%s"
              % (i * dt, p[0], p[2], v, math.hypot(rx, rz), math.degrees(math.atan2(rz, rx)) % 360.0,
                 ",".join(sorted(set(names))) or "-"), flush=True)


if __name__ == "__main__":
    for mu in (1.00, 0.40):
        diag(mu, sec=1.5)
        print()
