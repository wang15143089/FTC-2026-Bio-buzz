# -*- coding: utf-8 -*-
"""R8 step 1: where does the ball actually rest, and what happens during the creep?"""
import json, math, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import r6_smooth as r6
import opt_lib as ol
import mujoco, numpy as np

pv2 = ol.pv2
T_STALL, N_FREE = 0.530, 290.0
KV = T_STALL / (N_FREE * 2 * math.pi / 60.0)


def rest(name, sec=8.0, bx=145.0):
    ol.apply_geom(name)
    xml, ctrl = pv2.build_xml(1620.0, -1, 0.0, bx, pv2.tray_top_z(bx) + pv2.BALL_R)
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    bg = {g for g in range(m.ngeom) if m.geom_bodyid[g] == bid}
    for _ in range(int(sec / m.opt.timestep)):
        mujoco.mj_step(m, d)
    p = d.xpos[bid] * 1000.0
    cont = {}
    for c in range(d.ncon):
        con = d.contact[c]
        for g in (con.geom1, con.geom2):
            if g in bg:
                o = con.geom2 if g == con.geom1 else con.geom1
                nm = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, o) or ("geom%d" % o)
                cont[nm] = round(float(np.linalg.norm(con.frame[:3])), 3) if False else cont.get(nm, 0) + 1
    rx, rz = p[0] - pv2.PADDLE_CX, p[2] - pv2.PADDLE_CZ
    print("  [%s] rest x=%8.3f z=%8.3f  r=%7.3f ang=%6.2f  |  tray_top_z(x)=%7.3f"
          % (name, p[0], p[2], math.hypot(rx, rz),
             math.degrees(math.atan2(rz, rx)) % 360.0, pv2.tray_top_z(p[0])))
    print("        contacts: %s" % cont)
    return p


def creep(name, rpm=N_FREE, sec=5.0, bx=145.0, step=0.05):
    ol.apply_geom(name)
    xml, ctrl = pv2.build_xml(1620.0, -1, rpm * 2 * math.pi / 60.0, bx,
                              pv2.tray_top_z(bx) + pv2.BALL_R)
    xml = xml.replace('kv="0.08"', 'kv="%.6f"' % KV)
    xml = xml.replace('forcerange="-1.5 1.5"', 'forcerange="-%g %g"' % (T_STALL, T_STALL))
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
    pid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "paddle_joint")
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    aid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "paddle_vel")
    dt = m.opt.timestep
    print("  [%s @%g rpm] t     ballx    ballz      r    ang    v     paddle_deg  rpm     T_Nm"
          % (name, rpm))
    n = int(sec / dt); k = max(1, int(step / dt))
    for i in range(n):
        mujoco.mj_step(m, d)
        if i % k == 0 and i * dt >= 0.15:
            p = d.xpos[bid] * 1000.0
            rx, rz = p[0] - pv2.PADDLE_CX, p[2] - pv2.PADDLE_CZ
            print("        %5.2f %8.2f %8.2f %6.2f %6.1f %6.3f  %9.1f %7.1f %7.3f"
                  % (i * dt, p[0], p[2], math.hypot(rx, rz),
                     math.degrees(math.atan2(rz, rx)) % 360.0,
                     float(np.linalg.norm(d.cvel[bid][3:])),
                     math.degrees(d.qpos[pid]), math.degrees(d.qvel[pid]) / 6.0,
                     abs(float(d.actuator_force[aid]))))
    return d


if __name__ == "__main__":
    print("=== rest position, paddle held still ===")
    for nm in ("R5", "R6"):
        rest(nm)
    print()
    print("=== R5 with the real 25-4 motor at full speed ===")
    creep("R5", sec=4.2)
    print()
    print("=== R6 with the real 25-4 motor at full speed ===")
    creep("R6", sec=4.2)
