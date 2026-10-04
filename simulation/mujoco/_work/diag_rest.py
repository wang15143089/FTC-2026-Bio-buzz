# -*- coding: utf-8 -*-
import sys, math, importlib.util
sys.stdout.reconfigure(encoding="utf-8")
import mujoco, numpy as np
spec = importlib.util.spec_from_file_location("pv2", r"simulation/mujoco/pollen_v2_sim.py")
pv2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(pv2)
bx = 145.0
xml, ctrl = pv2.build_xml(1620.0, -1, 1.0*2*math.pi/60.0, bx, pv2.tray_top_z(bx)+pv2.BALL_R)
m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
dt = m.opt.timestep
names = {i: mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, i) for i in range(m.ngeom)}
print("托盘顶面 z(x=145)=%.2f  球心初始 z=%.2f" % (pv2.tray_top_z(145), pv2.tray_top_z(145)+pv2.BALL_R))
n = int(round(4.0/dt))
for i in range(n):
    mujoco.mj_step(m, d)
    if i % int(round(0.25/dt)) == 0:
        p = d.xpos[bid]
        px, pz = float(p[0])*1000, float(p[2])*1000
        rr = math.hypot(px-pv2.PADDLE_CX, pz-pv2.PADDLE_CZ)
        print("t=%.2f  x=%8.2f z=%7.2f  v=%6.3f  r=%6.2f  θ=%6.1f°  托盘面高=%6.2f  离托盘=%5.2f"
              % (i*dt, px, pz, np.linalg.norm(d.cvel[bid][3:]), rr,
                 math.degrees(math.atan2(pz-pv2.PADDLE_CZ, px-pv2.PADDLE_CX)) % 360,
                 pv2.tray_top_z(px), pz-35.56-pv2.tray_top_z(px)))
# 最终接触
print("--- 最终接触 ---")
for c in range(d.ncon):
    g1, g2 = d.contact[c].geom1, d.contact[c].geom2
    print("  ", names[g1], "<->", names[g2])
