# -*- coding: utf-8 -*-
"""拨杆头部几何参数化扫描：峰值扭矩 + 发射成败"""
import json, math, sys, importlib.util
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
import mujoco, numpy as np
spec = importlib.util.spec_from_file_location("pv2", r"simulation/mujoco/pollen_v2_sim.py")
pv2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(pv2)
W = pv2.PADDLE_W

def mk(blade_r, blade_hx, blade_hz, flex_r, flex_hz, flex_hx=2.0, arm_r=30.0, arm_hx=16.0):
    def f():
        parts = [("hub", (0.0, 0.0, 0.0), (18.0, 17.0, 18.0), 0.0, "cylY")]
        for i, a in enumerate((pv2.PADDLE_PHASE, pv2.PADDLE_PHASE+120.0, pv2.PADDLE_PHASE+240.0), 1):
            parts.append((f"arm_{i}", (arm_r, 0.0, 0.0), (arm_hx, 9.0, 5.0), a, "box"))
            parts.append((f"blade_{i}", (blade_r, 0.0, 0.0), (blade_hx, W/2.0, blade_hz), a, "box"))
            if flex_hz > 0:
                parts.append((f"flex_{i}", (flex_r, 0.0, 0.0), (flex_hx, W/2.0, flex_hz), a, "box"))
        return parts
    return f

VARIANTS = {
 "V0 现状":        mk(52.0, 6.0, 15.0, 58.0, 17.0),
 "A 叶尖收短":     mk(52.0, 6.0, 15.0, 56.0, 13.0),
 "B 叶尖收到58.4": mk(50.0, 6.0, 13.0, 56.4, 13.0),
 "C 切向减薄":     mk(52.0, 6.0, 15.0, 58.0,  9.0),
 "D 楔形头":       mk(52.0, 6.0, 15.0, 57.0,  7.0, flex_hx=3.0),
}

def run(bx, rpm_p, fr=5.0, sec=6.0, fw=1620.0):
    xml, ctrl = pv2.build_xml(fw, -1, rpm_p*2*math.pi/60.0, bx, pv2.tray_top_z(bx)+pv2.BALL_R)
    xml = xml.replace('name="paddle_vel" joint="paddle_joint" kv="0.08" ctrlrange="-100 100" forcerange="-1.5 1.5"',
                      'name="paddle_vel" joint="paddle_joint" kv="0.08" ctrlrange="-100 100" forcerange="-%g %g"' % (fr, fr))
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
    aid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "paddle_vel")
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    dt = m.opt.timestep; every = max(1, int(round(0.002/dt)))
    tr, tq, bstat = [], [], []
    for i in range(int(round(sec/dt))):
        mujoco.mj_step(m, d)
        f = abs(float(d.actuator_force[aid])); tq.append(f)
        if i % every == 0:
            p = d.xpos[bid]; v = d.cvel[bid][3:]
            px, pz = float(p[0])*1000., float(p[2])*1000.
            lx, lz = pv2.to_shooter(px, pz)
            rx, rz = px-pv2.PADDLE_CX, pz-pv2.PADDLE_CZ
            tr.append({"t":round(i*dt,4),"x":round(px,3),"z":round(pz,3),"v":round(float(np.linalg.norm(v)),4),
                       "vx":round(float(v[0]),4),"vz":round(float(v[2]),4),"r":round(math.hypot(rx,rz),3),
                       "ang":round(math.degrees(math.atan2(rz,rx))%360.,2),"lx":round(lx,3),"lz":round(lz,3)})
            bstat.append((i*dt, px, pz, math.hypot(rx,rz), math.degrees(math.atan2(rz,rx))%360., float(np.linalg.norm(v))))
    return pv2.analyse(tr), np.array(tq), tr, bstat

res = {}
print("=== 拨杆头部几何扫描（200 rpm，球 x=145，6 s，forcerange ±5 N*m）===")
for name, fn in VARIANTS.items():
    pv2.paddle_parts = fn
    r, t, tr, bs = run(145.0, 200.0)
    res[name] = {"peak": float(t.max()), "mean": float(t.mean()), "launched": bool(r["launched"]),
                 "minAng": float(r["min_angle_deg"]), "peak_t": float(np.argmax(t)*2e-4)}
    # 峰值时刻球的半径/角度
    tp = float(np.argmax(t)*2e-4)
    near = min(bs, key=lambda s: abs(s[0]-tp))
    res[name]["ball_at_peak"] = [round(near[0],3), round(near[1],2), round(near[2],2), round(near[3],2), round(near[4],2), round(near[5],3)]
    print("  %-14s 峰值=%.3f N*m (t=%.3f s, 球 r=%.1f ang=%.1f v=%.2f)  平均=%.3f  发射=%-5s  minAng=%7.2f"%(
        name, t.max(), tp, near[3], near[4], near[5], t.mean(), r["launched"], r["min_angle_deg"]))

# 门槛：对最优方案重新扫 forcerange
print()
print("=== 各方案在 ±1.2 / ±1.5 N*m 硬限幅下能否发射 ===")
for name, fn in VARIANTS.items():
    pv2.paddle_parts = fn
    row = []
    for fr in (1.2, 1.5):
        r2, t2, _, _ = run(145.0, 200.0, fr=fr)
        row.append("%s(%.2f)" % ("OK" if r2["launched"] else "--", t2.max()))
    print("  %-14s  ±1.2: %-12s  ±1.5: %s" % (name, row[0], row[1]))

Path("simulation/mujoco/out/summary_v2_blade_variants.json").write_text(
    json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
print()
print("已写 out/summary_v2_blade_variants.json")
