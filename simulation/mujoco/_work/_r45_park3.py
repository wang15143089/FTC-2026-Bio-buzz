# -*- coding: utf-8 -*-
"""P 试验：拨杆用速度伺服(真实舵机行为)保持在 J_PARK，看托板滚下的 NECTAR 能否到球窝。
   对比对象：r38 相位机在 settle 段 ctrl=0 -> 自由下垂到 ~53.3 deg -> 弹性指楔住球。"""
import sys, os, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mujoco, r37_multiball as R
MM = R.MM
D = math.degrees
R.TRAY_X1 = 460.0
nm = lambda m, g: (mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, g) or "?")
KP = 40.0

def run(P, x0, z0, t_end=5.0):
    m, d, aid, jid, meta, w, xml = R.build_multi(["NECTAR"], 0.0, 82)
    b = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball_1")
    qb = m.jnt_qposadr[m.body_jntadr[b]]
    qp = m.jnt_qposadr[jid]
    d.qpos[qp] = math.radians(P)
    d.qpos[qb:qb + 3] = (x0 * MM, 0.0, z0 * MM)
    d.qpos[qb + 3:qb + 7] = (1, 0, 0, 0)
    mujoco.mj_forward(m, d)
    for i in range(int(t_end / m.opt.timestep)):
        err = math.remainder(math.radians(P) - float(d.qpos[qp]), 2 * math.pi)
        d.ctrl[aid] = max(-100.0, min(100.0, KP * err))
        mujoco.mj_step(m, d)
    p = d.xpos[b] * 1000
    J = D(float(d.qpos[qp])) % 360.0
    cs = sorted({nm(m, c.geom2) if c.geom1 == m.body_geomadr[b] else nm(m, c.geom1)
                 for c in d.contact[:d.ncon]})
    ok = "球窝 OK" if p[0] < 45 else ("楔住CH" if 110 < p[0] < 140 else "中间/被挡")
    print("P=%6.1f x0=%6.1f -> x=%6.1f z=%5.1f | J=%6.1f | %-8s %s"
          % (P, x0, p[0], p[2], J, ok, cs), flush=True)

for P in (53.3, 70.0, 85.0, 95.0, 105.0, 115.0, 125.0, 140.0, 150.0, 165.0, 185.0, 205.0, 230.0):
    run(P, 200.0, 66.7)
