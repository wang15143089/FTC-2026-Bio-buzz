# -*- coding: utf-8 -*-
"""拆解扭矩峰值结构：冲击 or 持续负载"""
import json, math, sys, importlib.util
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
import mujoco, numpy as np
spec = importlib.util.spec_from_file_location("pv2", r"simulation/mujoco/pollen_v2_sim.py")
pv2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(pv2)

def run(bx, rpm_p, fr=5.0, sec=6.0, fw=1620.0):
    xml, ctrl = pv2.build_xml(fw, -1, rpm_p*2*math.pi/60.0, bx, pv2.tray_top_z(bx)+pv2.BALL_R)
    xml = xml.replace('name="paddle_vel" joint="paddle_joint" kv="0.08" ctrlrange="-100 100" forcerange="-1.5 1.5"',
                      'name="paddle_vel" joint="paddle_joint" kv="0.08" ctrlrange="-100 100" forcerange="-%g %g"' % (fr, fr))
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
    aid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "paddle_vel")
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    dt = m.opt.timestep
    n = int(round(sec/dt)); tq = np.zeros(n); ang = np.zeros(n); rr = np.zeros(n); sp = np.zeros(n)
    for i in range(n):
        mujoco.mj_step(m, d)
        tq[i] = abs(float(d.actuator_force[aid]))
        p = d.xpos[bid]; rx, rz = float(p[0])*1000.-pv2.PADDLE_CX, float(p[2])*1000.-pv2.PADDLE_CZ
        rr[i] = math.hypot(rx, rz); ang[i] = math.degrees(math.atan2(rz, rx)) % 360.
        sp[i] = float(np.linalg.norm(d.cvel[bid][3:]))
    return tq, rr, ang, sp, dt

def mav(a, w):
    if w <= 1: return a
    k = np.ones(w)/w
    return np.convolve(a, k, mode="same")

for rpm in (200.0, 140.0):
    tq, rr, ang, sp, dt = run(145.0, rpm)
    print("=== 拨杆 %.0f rpm ==="%rpm)
    print("  瞬时峰值            = %.3f N*m  (t=%.3f s)"%(tq.max(), np.argmax(tq)*dt))
    for ms in (2, 5, 10, 20, 50):
        w = int(round(ms/1000/dt))
        print("  %2d ms 滑动平均峰值 = %.3f N*m"%(ms, mav(tq, w).max()))
    for lab, v in (("0.61 (UltraSpeed堵转)",0.608),("1.64 (Balanced堵转)",1.638)):
        dur = float((tq > v).sum()*dt*1000.)
        print("  超过 %-22s 累计 %.2f ms"%(lab, dur))
    # 找出前 5 个扭矩尖峰
    thr = 0.5; above = tq > thr; idx = []
    i = 0
    while i < len(above):
        if above[i]:
            j = i
            while j+1 < len(above) and above[j+1]: j += 1
            idx.append((i, j)); i = j+1
        else: i += 1
    idx.sort(key=lambda p: -tq[p[0]:p[1]+1].max())
    print("  最大的几段接触（>0.5 N*m）：")
    for a, b in idx[:5]:
        print("     t=%6.3f-%6.3f s  时长%5.1f ms  峰值%5.3f  球 r=%5.1f→%5.1f  ang=%6.1f→%6.1f  v=%4.2f→%4.2f"%(
            a*dt, b*dt, (b-a+1)*dt*1000., tq[a:b+1].max(), rr[a], rr[b], ang[a], ang[b], sp[a], sp[b]))
    print()
