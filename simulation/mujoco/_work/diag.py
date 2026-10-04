# -*- coding: utf-8 -*-
"""诊断：接球位置/时序对峰值扭矩的影响 + 载荷区间平均扭矩"""
import json, math, sys, importlib.util
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
import mujoco, numpy as np
spec = importlib.util.spec_from_file_location("pv2", r"simulation/mujoco/pollen_v2_sim.py")
pv2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(pv2)

def run(bx, rpm_p, fr=20.0, sec=8.0, fw=1620.0, phase=None):
    if phase is not None: pv2.PADDLE_PHASE = phase
    bz = pv2.tray_top_z(bx)+pv2.BALL_R if bx > -20 else None
    if bz is None:
        bz = pv2.tray_top_z(-2.30)+pv2.BALL_R
    xml, ctrl = pv2.build_xml(fw, -1, rpm_p*2*math.pi/60.0, bx, bz)
    xml = xml.replace('name="paddle_vel" joint="paddle_joint" kv="0.08" ctrlrange="-100 100" forcerange="-1.5 1.5"',
                      'name="paddle_vel" joint="paddle_joint" kv="0.08" ctrlrange="-100 100" forcerange="-%g %g"' % (fr, fr))
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
    aid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "paddle_vel")
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    dt = m.opt.timestep; n = int(round(sec/dt))
    tq = np.zeros(n); rr = np.zeros(n); ang = np.zeros(n); sp = np.zeros(n)
    tr = []
    for i in range(n):
        mujoco.mj_step(m, d)
        tq[i] = abs(float(d.actuator_force[aid]))
        p = d.xpos[bid]; rx, rz = float(p[0])*1000.-pv2.PADDLE_CX, float(p[2])*1000.-pv2.PADDLE_CZ
        rr[i] = math.hypot(rx, rz); ang[i] = math.degrees(math.atan2(rz, rx)) % 360.
        sp[i] = float(np.linalg.norm(d.cvel[bid][3:]))
        if i % max(1,int(round(0.002/dt))) == 0:
            lx, lz = pv2.to_shooter(float(p[0])*1000., float(p[2])*1000.)
            tr.append({"t":round(i*dt,4),"x":round(float(p[0])*1000.,3),"z":round(float(p[2])*1000.,3),
                       "v":round(float(np.linalg.norm(d.cvel[bid][3:])),4),"vx":round(float(d.cvel[bid][3]),4),
                       "vz":round(float(d.cvel[bid][5]),4),"r":round(rr[i],3),"ang":round(ang[i],2),
                       "lx":round(lx,3),"lz":round(lz,3)})
    return pv2.analyse(tr), tq, rr, ang, sp, dt, tr

print("=== 接球/进料时序对峰值扭矩的影响（拨杆 200 rpm，forcerange ±20）===")
for lab, bx in (("球从 x=145 滚入", 145.0), ("球从 x=90 滚入", 90.0), ("球从 x=40 滚入", 40.0), ("球已在唇口停位 x=-2.3", -2.30)):
    r, tq, rr, ang, sp, dt, tr = run(bx, 200.0)
    imax = int(np.argmax(tq))
    # 受载区间：球运动显著的时间
    mov = sp > 0.05
    seg = np.where(mov)[0]
    load = tq[seg] if len(seg) else tq
    print("  %-22s 峰值=%.3f (t=%.3f, r=%.1f ang=%.1f v=%.2f)  受载均值=%.3f  受载时长=%.0f ms  发射=%s"%(
        lab, tq.max(), imax*dt, rr[imax], ang[imax], sp[imax], load.mean(), len(seg)*dt*1000., r["launched"]))

print()
print("=== 拨杆初始相位影响（球从 x=145，200 rpm）===")
for ph in (18.0, 48.0, 78.0, 108.0):
    r, tq, rr, ang, sp, dt, tr = run(145.0, 200.0, phase=ph)
    imax = int(np.argmax(tq))
    print("  PADDLE_PHASE=%5.0f  峰值=%.3f N*m (t=%.3f, r=%.1f ang=%.1f v=%.2f)  发射=%s"%(
        ph, tq.max(), imax*dt, rr[imax], ang[imax], sp[imax], r["launched"]))
