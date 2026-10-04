# -*- coding: utf-8 -*-
"""确认球停位支撑 + 低转速门槛"""
import json, math, sys, importlib.util
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
import mujoco, numpy as np
spec = importlib.util.spec_from_file_location("pv2", r"simulation/mujoco/pollen_v2_sim.py")
pv2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(pv2)

def mk(bx, rpm_p, fr, sec=7.0, fw=1620.0):
    bz = pv2.tray_top_z(bx)+pv2.BALL_R
    xml, ctrl = pv2.build_xml(fw, -1, rpm_p*2*math.pi/60.0, bx, bz)
    xml = xml.replace('-1.5 1.5"', '-%g %g"' % (fr, fr))
    return xml, ctrl

def go(xml, ctrl, sec=7.0, contacts_at=None):
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
    aid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "paddle_vel")
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    bg = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, "ball_geom")
    dt = m.opt.timestep; n = int(round(sec/dt)); tr = []
    for i in range(n):
        mujoco.mj_step(m, d)
        if i % max(1,int(round(0.002/dt))) == 0:
            p = d.xpos[bid]
            lx, lz = pv2.to_shooter(float(p[0])*1000., float(p[2])*1000.)
            rx, rz = float(p[0])*1000.-pv2.PADDLE_CX, float(p[2])*1000.-pv2.PADDLE_CZ
            tr.append({"t":round(i*dt,4),"x":round(float(p[0])*1000.,3),"z":round(float(p[2])*1000.,3),
                       "v":round(float(np.linalg.norm(d.cvel[bid][3:])),4),"vx":round(float(d.cvel[bid][3]),4),
                       "vz":round(float(d.cvel[bid][5]),4),"r":round(math.hypot(rx,rz),3),
                       "ang":round(math.degrees(math.atan2(rz,rx))%360.,2),"lx":round(lx,3),"lz":round(lz,3)})
    return pv2.analyse(tr), tr

# (1) 静止球（不转拨杆）的接触对
xml, ctrl = mk(-2.30, 0.0001, 0.02, sec=1.5)
m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
for _ in range(2000): mujoco.mj_step(m, d)
bg = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, "ball_geom")
names = set()
for c in range(d.ncon):
    con = d.contact[c]
    if con.geom1 == bg or con.geom2 == bg:
        o = con.geom2 if con.geom1 == bg else con.geom1
        names.add(mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, o))
print("球在停位静止时的接触对：", sorted(names))
p = d.xpos[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY,"ball")]
rz = float(p[2])*1000.-pv2.PADDLE_CZ; rx = float(p[0])*1000.-pv2.PADDLE_CX
print("  停位球心: x=%.2f z=%.2f  (r=%.1f  ang=%.1f)"%(float(p[0])*1000., float(p[2])*1000., math.hypot(rx,rz), math.degrees(math.atan2(rz,rx))%360.))
print("  该处托板顶面 z=%.2f  -> 球底距托板 %.2f mm"%(pv2.tray_top_z(float(p[0])*1000.), (float(p[2])*1000.-pv2.BALL_R)-pv2.tray_top_z(float(p[0])*1000.)))

# (2) 各转速下的扭矩门槛
print()
print("=== 发射所需拨杆力矩门槛 vs 转速（球从 x=145 滚入，7 s）===")
res = {}
for rpm in (105.0, 140.0, 200.0):
    row = {}
    ok = None
    for fr in (0.4, 0.6, 0.8, 1.0, 1.2, 1.5):
        xml, ctrl = mk(145.0, rpm, fr)
        r, tr = go(xml, ctrl)
        row["%.1f"%fr] = bool(r["launched"])
        if r["launched"] and ok is None: ok = fr
    res["%.0f"%rpm] = {"launched": row, "threshold": ok}
    print("  %5.0f rpm: %s   门槛=%.1f N*m"%(rpm,
        "  ".join("%s@%.1f" % ("OK" if v else "--", float(k)) for k, v in row.items()), ok if ok else -1))

Path("simulation/mujoco/out/summary_v2_servo_req.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
print()
print("已写 out/summary_v2_servo_req.json")
