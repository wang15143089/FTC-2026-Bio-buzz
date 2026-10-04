# -*- coding: utf-8 -*-
"""细化扭矩门槛 + 转速-扭矩耦合扫描"""
import json, math, sys, importlib.util
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
    return res, np.array(tq), tr

print("=== 1) 细化门槛扫描（拨杆 200 rpm，球 x=145，6 s）===")
out = {}
for fr in (0.80, 0.90, 1.00, 1.10, 1.20, 1.30, 1.40, 1.50):
    r, t, tr = run(145.0, 200.0, fr)
    out["%.2f"%fr] = {"launched": bool(r["launched"]), "minAng": float(r["min_angle_deg"]),
                      "peak_used": float(t.max()), "exit_v": float(r.get("exit_speed", 0.0))}
    print("  ±%.2f N*m  peak=%.3f  发射=%-5s  minAng=%7.2f  出射=%.2f m/s"%(
        fr, t.max(), r["launched"], r["min_angle_deg"], r.get("exit_speed", 0.0)))

print()
print("=== 2) 转速-峰值扭矩耦合（forcerange 5 N*m 自由跑）===")
spd = {}
for rpm in (105.0, 140.0, 160.0, 200.0, 260.0):
    r, t, tr = run(145.0, rpm, 5.0)
    spd["%.0f"%rpm] = {"launched": bool(r["launched"]), "peak": float(t.max()), "mean": float(t.mean()),
                       "t_peak": float(np.argmax(t)*2e-4), "exit_v": float(r.get("exit_speed", 0.0)),
                       "minAng": float(r["min_angle_deg"])}
    print("  拨杆 %5.0f rpm  峰值=%.3f  平均=%.3f N*m  峰值时刻=%.3f s  发射=%-5s  出射=%.2f m/s"%(
        rpm, t.max(), t.mean(), float(np.argmax(t)*2e-4), r["launched"], r.get("exit_speed", 0.0)))

Path = __import__("pathlib").Path
Path("simulation/mujoco/out/summary_v2_torque_detail.json").write_text(
    json.dumps({"threshold_scan": out, "speed_sweep": spd}, ensure_ascii=False, indent=2), encoding="utf-8")
print()
print("已写 out/summary_v2_torque_detail.json")
