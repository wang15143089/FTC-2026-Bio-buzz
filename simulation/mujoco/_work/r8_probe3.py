# -*- coding: utf-8 -*-
"""R8 step 3: (a) paddle with no ball (control), (b) full contact dump incl. the blade."""
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


def build(name, bx=145.0, rpm=N_FREE, with_ball=True):
    ol.apply_geom(name)
    if with_ball:
        xml, ctrl = pv2.build_xml(1620.0, -1, rpm * 2 * math.pi / 60.0, bx,
                                  pv2.tray_top_z(bx) + pv2.BALL_R)
    else:
        xml, ctrl = pv2.build_xml(1620.0, -1, rpm * 2 * math.pi / 60.0, bx,
                                  pv2.tray_top_z(bx) + pv2.BALL_R)
        i = xml.index('<body name="ball"')
        j = xml.index("</body>", i) + len("</body>")
        xml = xml[:i] + xml[j:]
    xml = xml.replace('kv="0.08"', 'kv="%.6f"' % KV)
    xml = xml.replace('forcerange="-1.5 1.5"', 'forcerange="-%g %g"' % (T_STALL, T_STALL))
    return xml, ctrl


def control(name="R5", sec=2.0):
    xml, ctrl = build(name, with_ball=False)
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
    pid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "paddle_joint")
    aid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "paddle_vel")
    print("  [%s, NO BALL]  t     rpm    T_Nm" % name)
    for i in range(int(sec / m.opt.timestep)):
        mujoco.mj_step(m, d)
        if i % int(0.2 / m.opt.timestep) == 0:
            print("        %5.2f  %7.1f  %6.3f" % (i * m.opt.timestep,
                  math.degrees(d.qvel[pid]) / 6.0, abs(float(d.actuator_force[aid]))))


def full(name="R5", rpm=N_FREE, sec=6.0, bx=145.0, snaps=(0.45, 0.70, 1.40, 2.20, 2.90, 3.40, 4.50, 6.00)):
    xml, ctrl = build(name, bx=bx, rpm=rpm, with_ball=True)
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
    pid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "paddle_joint")
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    aid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "paddle_vel")
    bg = {g for g in range(m.ngeom) if m.geom_bodyid[g] == bid}
    dt = m.opt.timestep
    nxt = 0
    for i in range(int(sec / dt)):
        mujoco.mj_step(m, d)
        t = i * dt
        if nxt < len(snaps) and t >= snaps[nxt]:
            nxt += 1
            p = d.xpos[bid] * 1000.0
            qd = math.degrees(d.qpos[pid])
            rb = math.hypot(p[0] - pv2.PADDLE_CX, p[2] - pv2.PADDLE_CZ)
            ab = math.degrees(math.atan2(p[2] - pv2.PADDLE_CZ, p[0] - pv2.PADDLE_CX)) % 360.0
            print("--- t=%.2f ball r=%6.2f ang=%6.1f | paddle=%7.1f deg rpm=%6.1f T=%.3f"
                  % (t, rb, ab, qd, math.degrees(d.qvel[pid]) / 6.0,
                     abs(float(d.actuator_force[aid]))))
            for c in range(d.ncon):
                con = d.contact[c]
                if not (con.geom1 in bg or con.geom2 in bg):
                    continue
                other = con.geom2 if con.geom1 in bg else con.geom1
                nm = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, other) or ("geom%d" % other)
                pt = con.pos * 1000.0
                r_p = math.hypot(pt[0] - pv2.PADDLE_CX, pt[2] - pv2.PADDLE_CZ)
                a_p = math.degrees(math.atan2(pt[2] - pv2.PADDLE_CZ, pt[0] - pv2.PADDLE_CX)) % 360.0
                a_rel = (a_p - (-qd)) % 360.0
                nrm = con.frame[:3]
                print("      %-16s dist=%7.4f  pt=(%7.2f,%7.2f)  r_p=%6.2f  a_rel=%6.1f  n=(%6.3f,%6.3f)"
                      % (nm, con.dist * 1000.0, pt[0], pt[2], r_p, a_rel, nrm[0], nrm[2]))


if __name__ == "__main__":
    print("=== control: paddle alone, no ball ===")
    control("R5")
    print()
    print("=== R5 with ball: all contacts (a_rel = angle in the paddle frame) ===")
    full("R5", sec=6.0)
