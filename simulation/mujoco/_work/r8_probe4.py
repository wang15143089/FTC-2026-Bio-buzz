# -*- coding: utf-8 -*-
"""R8 step 4: measure the actual contact FORCE (N) on the ball while jammed."""
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


def go(name="R5", rpm=N_FREE, sec=6.0, bx=145.0,
       snaps=(0.45, 0.70, 1.40, 2.20, 2.90, 3.40, 4.50)):
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
    bg = {g for g in range(m.ngeom) if m.geom_bodyid[g] == bid}
    res = np.zeros(6)
    dt = m.opt.timestep
    nxt = 0
    print("  ball weight = %.3f N   (m=%.3f kg)" % (pv2.BALL_MASS * 9.81, pv2.BALL_MASS))
    for i in range(int(sec / dt)):
        mujoco.mj_step(m, d)
        t = i * dt
        if nxt < len(snaps) and t >= snaps[nxt]:
            nxt += 1
            p = d.xpos[bid] * 1000.0
            rb = math.hypot(p[0] - pv2.PADDLE_CX, p[2] - pv2.PADDLE_CZ)
            ab = math.degrees(math.atan2(p[2] - pv2.PADDLE_CZ, p[0] - pv2.PADDLE_CX)) % 360.0
            T = abs(float(d.actuator_force[aid]))
            print("--- t=%.2f ball r=%6.2f ang=%6.1f  paddle rpm=%6.1f  joint torque=%.3f Nm"
                  % (t, rb, ab, math.degrees(d.qvel[pid]) / 6.0, T))
            for c in range(d.ncon):
                con = d.contact[c]
                if not (con.geom1 in bg or con.geom2 in bg):
                    continue
                other = con.geom2 if con.geom1 in bg else con.geom1
                nm = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, other) or ("geom%d" % other)
                mujoco.mj_contactForce(m, d, c, res)
                fN = res[0]
                ft = math.hypot(res[1], res[2])
                print("      %-16s pen=%6.3f mm   F_normal=%7.3f N   F_shear=%7.3f N"
                      % (nm, con.dist * 1000.0, fN, ft))
            fat = d.xfrc_applied[bid].copy()
            print("      ball |v|=%.4f m/s" % float(np.linalg.norm(d.cvel[bid][3:])))


if __name__ == "__main__":
    go("R5", sec=6.0)
