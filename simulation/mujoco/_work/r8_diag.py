# -*- coding: utf-8 -*-
"""R8: trace the pocket-start run (x0=20.9) in detail."""
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
BASE = ol.GEOM["D 球窝抬高6.8"][0]


def blades(angs, W=pv2.PADDLE_W):
    def f():
        parts = [("hub", (0., 0., 0.), (18., 17., 18.), 0., "cylY")]
        for i, a in enumerate(angs, 1):
            parts += [("arm_%d" % i, (30., 0, 0), (16., 9., 5.), a, "box"),
                      ("blade_%d" % i, (52., 0, 0), (6., W / 2., 15.), a, "box"),
                      ("flex_%d" % i, (58., 0, 0), (2., W / 2., 17.), a, "box")]
        return parts
    return f


def go(bx, sec=6.0, snaps=(0.6, 1.2, 2.0, 3.0, 4.0, 5.0)):
    pv2.static_geoms = BASE
    pv2.paddle_parts = blades([10.0, 190.0])
    xml, ctrl = pv2.build_xml(1620.0, -1, N_FREE * 2 * math.pi / 60.0, bx,
                              pv2.tray_top_z(bx) + pv2.BALL_R)
    xml = xml.replace('kv="0.08"', 'kv="%.6f"' % KV)
    xml = xml.replace('forcerange="-1.5 1.5"', 'forcerange="-%g %g"' % (T_STALL, T_STALL))
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
    pid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "paddle_joint")
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    aid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "paddle_vel")
    bg = {g for g in range(m.ngeom) if m.geom_bodyid[g] == bid}
    dt = m.opt.timestep
    nxt = 0; k = 0
    print("  x0=%.1f" % bx)
    for i in range(int(sec / dt)):
        mujoco.mj_step(m, d)
        t = i * dt
        if i % int(0.1 / dt) == 0:
            p = d.xpos[bid] * 1000.0
            qd = math.degrees(d.qpos[pid])
            rb = math.hypot(p[0] - pv2.PADDLE_CX, p[2] - pv2.PADDLE_CZ)
            ab = math.degrees(math.atan2(p[2] - pv2.PADDLE_CZ, p[0] - pv2.PADDLE_CX)) % 360.0
            print("    t=%.1f  x=%7.2f z=%7.2f  r=%6.2f ang=%6.1f v=%5.2f | pad=%7.1f rpm=%6.1f T=%.3f"
                  % (t, p[0], p[2], rb, ab, float(np.linalg.norm(d.cvel[bid][3:])),
                     qd, math.degrees(d.qvel[pid]) / 6.0, abs(float(d.actuator_force[aid]))))
        if nxt < len(snaps) and t >= snaps[nxt]:
            nxt += 1
            print("      -- contacts at t=%.1f --" % t)
            for c in range(d.ncon):
                con = d.contact[c]
                if not (con.geom1 in bg or con.geom2 in bg):
                    continue
                other = con.geom2 if con.geom1 in bg else con.geom1
                nm = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, other) or ("geom%d" % other)
                pt = con.pos * 1000.0
                f6 = np.zeros(6); mujoco.mj_contactForce(m, d, c, f6)
                print("         %-16s Fn=%7.3f  pt=(%7.2f,%7.2f) dist=%6.3f"
                      % (nm, abs(f6[0]), pt[0], pt[2], con.dist * 1000.0))


if __name__ == "__main__":
    go(20.9)
