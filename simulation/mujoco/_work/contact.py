# -*- coding: utf-8 -*-
"""接触对诊断：找出峰值时刻到底是谁在夹球"""
import json, math, sys, importlib.util
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
import mujoco, numpy as np
spec = importlib.util.spec_from_file_location("pv2", r"simulation/mujoco/pollen_v2_sim.py")
pv2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(pv2)

bx, rpm_p, fr, sec = 145.0, 200.0, 20.0, 2.0
xml, ctrl = pv2.build_xml(1620.0, -1, rpm_p*2*math.pi/60.0, bx, pv2.tray_top_z(bx)+pv2.BALL_R)
xml = xml.replace('-1.5 1.5"', '-%g %g"' % (fr, fr))
m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
aid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "paddle_vel")
bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
bg = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, "ball_geom")
dt = m.opt.timestep; n = int(round(sec/dt))
rows = []
for i in range(n):
    mujoco.mj_step(m, d)
    f = abs(float(d.actuator_force[aid]))
    if f > 1.0:
        names = []
        for c in range(d.ncon):
            con = d.contact[c]
            if con.geom1 == bg or con.geom2 == bg:
                other = con.geom2 if con.geom1 == bg else con.geom1
                names.append(mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, other))
        p = d.xpos[bid]; rx, rz = float(p[0])*1000.-pv2.PADDLE_CX, float(p[2])*1000.-pv2.PADDLE_CZ
        rows.append((i*dt, f, math.hypot(rx,rz), math.degrees(math.atan2(rz,rx))%360.,
                     float(np.linalg.norm(d.cvel[bid][3:])), float(d.qvel[mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_JOINT,"paddle_joint")]), tuple(sorted(set(names)))))
print("峰值附近（|torque|>1.0 N*m）接触对统计：")
from collections import Counter
cnt = Counter(r[6] for r in rows)
for k, v in cnt.most_common():
    print("  %4d 帧  %s" % (v, k))
print()
print("最早 15 帧细节： t, 扭矩, 球r, 球ang, 球速, 拨杆角速度(rad/s), 接触对")
for r in rows[:15]:
    print("  t=%.3f  τ=%.3f  r=%5.1f ang=%6.1f v=%5.2f  ωp=%7.2f  %s" % r)
print()
print("球与各几何接触的帧数（全程 %d 帧，扭矩>1.0 的 %d 帧）：" % ((n), len(rows)))
print()
print("--- 全程接触统计 ---")
cnt2 = Counter()
for i in range(n):
    mujoco.mj_step(m, d) if False else None
