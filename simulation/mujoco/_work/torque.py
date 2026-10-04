# -*- coding: utf-8 -*-
"""测量 V2 拨杆实际需要的扭矩：峰值 + 门槛扫描"""
import json, math, sys, importlib.util
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
import mujoco, numpy as np
spec = importlib.util.spec_from_file_location("pv2", r"simulation/mujoco/pollen_v2_sim.py")
pv2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(pv2)

def run(bx, rpm_p, fr, sec=6.0, fw=1620.0):
    xml, ctrl = pv2.build_xml(fw, -1, rpm_p*2*math.pi/60.0, bx, pv2.tray_top_z(bx)+pv2.BALL_R)
    xml = xml.replace('name="paddle_vel" joint="paddle_joint" kv="0.08" ctrlrange="-100 100" forcerange="-1.5 1.5"',
                      'name="paddle_vel" joint="paddle_joint" kv="0.08" ctrlrange="-100 100" forcerange="-%g %g"' % (fr, fr))
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
    aid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "paddle_vel")
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    dt = m.opt.timestep; every = max(1, int(round(0.002/dt)))
    tr = []; tq = []
    for i in range(int(round(sec/dt))):
        mujoco.mj_step(m, d)
        tq.append(abs(float(d.actuator_force[aid])))
        if i % every == 0:
            p = d.xpos[bid]; v = d.cvel[bid][3:]
            px, pz = float(p[0])*1000., float(p[2])*1000.
            lx, lz = pv2.to_shooter(px, pz)
            rx, rz = px-pv2.PADDLE_CX, pz-pv2.PADDLE_CZ
            tr.append({"t":round(i*dt,4),"x":round(px,3),"z":round(pz,3),"v":round(float(np.linalg.norm(v)),4),
                       "vx":round(float(v[0]),4),"vz":round(float(v[2]),4),"r":round(math.hypot(rx,rz),3),
                       "ang":round(math.degrees(math.atan2(rz,rx))%360.,2),"lx":round(lx,3),"lz":round(lz,3)})
    res = pv2.analyse(tr)
    return res, np.array(tq)

# 1) 大扭矩下量峰值
res, tq = run(145.0, 200.0, 5.0)
print("自由跑（forcerange 5 N*m）：launched=%s  峰值 |扭矩| = %.3f N*m  平均 %.3f N*m"%(
    res["launched"], tq.max(), tq.mean()))
print("   峰值出现在 t=%.3f s"%float(np.argmax(tq)*2e-4))

# 2) 门槛扫描
print()
print("forcrange 门槛扫描（拨杆 200 rpm，球从 x=145 进料，6 s）：")
for fr in (0.05, 0.10, 0.15, 0.20, 0.30, 0.50, 0.80, 1.50):
    r, t = run(145.0, 200.0, fr)
    print("   forcerange ±%.2f N*m  peak_used=%.3f  发射=%-5s  minAng=%7.2f"%(fr, t.max(), r["launched"], r["min_angle_deg"]))
