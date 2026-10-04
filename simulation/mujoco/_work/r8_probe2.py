# -*- coding: utf-8 -*-
"""R8 step 2: dump the exact contact set while the ball is jammed."""
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
SNAP = (0.60, 0.95, 1.60, 2.85, 3.60, 5.00)


def profile(name, rpm=N_FREE, sec=5.2, bx=145.0):
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
    dt = m.opt.timestep
    nxt = 0
    for i in range(int(sec / dt)):
        mujoco.mj_step(m, d)
        t = i * dt
        if nxt < len(SNAP) and t >= SNAP[nxt]:
            nxt += 1
            p = d.xpos[bid] * 1000.0
            q = math.degrees(d.qpos[pid])
            print("--- t=%.2f  ball x=%7.2f z=%7.2f  r=%6.2f ang=%6.1f  v=%5.3f  "
                  "paddle=%7.1f deg  rpm=%6.1f  T=%.3f"
                  % (t, p[0], p[2],
                     math.hypot(p[0] - pv2.PADDLE_CX, p[2] - pv2.PADDLE_CZ),
                     math.degrees(math.atan2(p[2] - pv2.PADDLE_CZ, p[0] - pv2.PADDLE_CX)) % 360.0,
                     float(np.linalg.norm(d.cvel[bid][3:])), q,
                     math.degrees(d.qvel[pid]) / 6.0, abs(float(d.actuator_force[aid]))))
            for c in range(d.ncon):
                con = d.contact[c]
                if con.geom1 in bg or con.geom2 in bg:
                    other = con.geom2 if con.geom1 in bg else con.geom1
                    nm = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, other) or ("geom%d" % other)
                    if nm.startswith("paddle"):
                        continue
                    pt = con.pos * 1000.0
                    nrm = con.frame[:3]
                    brush = [con.geom1, con.geom2][0] if con.geom1 in bg else con.geom2
                    print("      vs %-18s dist=%7.4f  pt=(%7.2f,%7.2f)  n=(%6.3f,%6.3f)"
                          % (nm, con.dist * 1000.0, pt[0], pt[2], nrm[0], nrm[2]))
    print()
    print("--- paddle-side contacts at selected times (blade tip corners) ---")
    return d


def blade_geom_names(m):
    return [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, g) for g in range(m.ngeom)
            if (mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, g) or "").startswith("paddle")]


def blade_probe(name, rpm=0.0, sec=0.5, bx=145.0, at=0.35):
    """Freeze the paddle at a given joint angle and find which blade part can reach the ball."""
    ol.apply_geom(name)
    xml, ctrl = pv2.build_xml(1620.0, -1, rpm * 2 * math.pi / 60.0, bx,
                              pv2.tray_top_z(bx) + pv2.BALL_R)
    xml = xml.replace('kv="0.08"', 'kv="%.6f"' % KV)
    xml = xml.replace('forcerange="-1.5 1.5"', 'forcerange="-%g %g"' % (T_STALL, T_STALL))
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    bg = {g for g in range(m.ngeom) if m.geom_bodyid[g] == bid}
    for i in range(int(sec / m.opt.timestep)):
        mujoco.mj_step(m, d)
    p = d.xpos[bid] * 1000.0
    rb = math.hypot(p[0] - pv2.PADDLE_CX, p[2] - pv2.PADDLE_CZ)
    ab = math.degrees(math.atan2(p[2] - pv2.PADDLE_CZ, p[0] - pv2.PADDLE_CX)) % 360.0
    print("  rest ball r=%.2f ang=%.2f   (blade tip radius=%g)" % (rb, ab, pv2.PADDLE_SWEEP_R))
    pid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "paddle_joint")
    q0 = d.qpos[pid]
    best = []
    for qd in range(0, 360, 5):
        d.qpos[pid] = math.radians(qd); d.qvel[:] = 0
        mujoco.mj_forward(m, d)
        for c in range(d.ncon):
            con = d.contact[c]
            if con.geom1 in bg or con.geom2 in bg:
                other = con.geom2 if con.geom1 in bg else con.geom1
                nm = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, other) or ("geom%d" % other)
                if nm.startswith("paddle"):
                    best.append((qd, nm, con.dist * 1000.0))
    if best:
        for qd, nm, dd in best[:14]:
            print("     paddle rot %5d deg -> contact %-16s dist=%7.4f mm" % (qd + math.degrees(q0) % 360, nm, dd))
    else:
        print("     no paddle contact at any rotation")
    d.qpos[pid] = q0


if __name__ == "__main__":
    print("=== R5: contact set at key times (only non-paddle geoms shown) ===")
    profile("R5", sec=5.2)
    print()
    print("=== R5: which blade part can reach the resting ball, vs paddle angle ===")
    blade_probe("R5", sec=0.30)
