import json, math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pollen_launcher_sim as P
import feeder_fair_test as F
import mujoco

bx, bz = -95.0, 17.5 + P.BALL_R
omega = 120.0 * 2 * math.pi / 60.0
xml, ctrl = P.build_xml(1620.0, omega, -1, bx, bz)
xml = F.strip(xml)
m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m); d.ctrl[:] = ctrl
mujoco.mj_forward(m, d)
bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
pj = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "paddle_joint")
dt = m.opt.timestep
for i in range(int(3.0 / dt)):
    mujoco.mj_step(m, d)
    if i % 5000 == 0:
        names = []
        for c in d.contact[:d.ncon]:
            b1 = m.geom_bodyid[c.geom1]; b2 = m.geom_bodyid[c.geom2]
            if b1 == bid or b2 == bid:
                g = c.geom1 if b2 == bid else c.geom2
                names.append(mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, g))
        print(f"t={i*dt:.2f} ball=({d.xpos[bid][0]*1000:.1f}, {d.xpos[bid][2]*1000:.1f}) "
              f"qpos={d.qpos[m.jnt_qposadr[pj]]:.2f} qvel={d.qvel[m.jnt_dofadr[pj]]:.3f} "
              f"contacts={names}", flush=True)
