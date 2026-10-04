# -*- coding: utf-8 -*-
"""摩擦敏感性：门槛到底由什么决定"""
import json, math, sys, importlib.util
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
import mujoco, numpy as np
spec = importlib.util.spec_from_file_location("pv2", r"simulation/mujoco/pollen_v2_sim.py")
pv2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(pv2)
ORIG = pv2.static_geoms

def seg(am, r_in, da=4.0, thick=7.0):
    r_mid = r_in + thick/2.0
    half = 0.5*r_mid*math.radians(da)*1.35
    cx, cz = pv2.polar(r_mid, am)
    return (f"flare_{int(round(am*10))}", "shell", "box", (2*half, pv2.FEEDER_W, thick),
            (cx, 0.0, cz), pv2.quat_y(-(am+90.0)))
def flare():
    g = [t for t in ORIG() if t[0] != "shell_lip_face"]
    g += [seg(227.5+4.0*k, 95.5+4.0*k) for k in range(3)]
    return g

def run(bx, rpm, fr, sec=7.0, mu_ball=None, mu_shell=None, fw=1620.0):
    xml, ctrl = pv2.build_xml(fw, -1, rpm*2*math.pi/60.0, bx, pv2.tray_top_z(bx)+pv2.BALL_R)
    xml = xml.replace('-1.5 1.5"', '-%g %g"' % (fr, fr))
    if mu_ball is not None:
        xml = xml.replace('<default class="ball"><geom friction="1.0 0.02 0.0001"',
                          '<default class="ball"><geom friction="%g 0.02 0.0001"' % mu_ball)
    if mu_shell is not None:
        xml = xml.replace('<default class="shell"><geom friction="0.25 0.005 0.0001"',
                          '<default class="shell"><geom friction="%g 0.005 0.0001"' % mu_shell)
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
    aid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "paddle_vel")
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    dt = m.opt.timestep; n = int(round(sec/dt)); tr = []; tq = np.zeros(n)
    for i in range(n):
        mujoco.mj_step(m, d); tq[i] = abs(float(d.actuator_force[aid]))
        if i % max(1,int(round(0.002/dt))) == 0:
            p = d.xpos[bid]; lx, lz = pv2.to_shooter(float(p[0])*1000., float(p[2])*1000.)
            rx, rz = float(p[0])*1000.-pv2.PADDLE_CX, float(p[2])*1000.-pv2.PADDLE_CZ
            tr.append({"t":round(i*dt,4),"x":round(float(p[0])*1000.,3),"z":round(float(p[2])*1000.,3),
                       "v":round(float(np.linalg.norm(d.cvel[bid][3:])),4),"vx":round(float(d.cvel[bid][3]),4),
                       "vz":round(float(d.cvel[bid][5]),4),"r":round(math.hypot(rx,rz),3),
                       "ang":round(math.degrees(math.atan2(rz,rx))%360.,2),"lx":round(lx,3),"lz":round(lz,3)})
    return pv2.analyse(tr), tr, tq, dt

FL = (0.3, 0.4, 0.5, 0.6, 0.8)
print("=== 摩擦敏感性（球-外罩/托板有效摩擦，现状几何，200 rpm）===")
print("%-24s %-8s %-9s %s" % ("条件", "门槛", "受载均值", "各力矩限幅"))
print("-"*92)
res = {}
for lab, kb, ks in (("现状 μ_ball=1.0/μ_shell=0.25", None, None),
                    ("μ_ball=0.6", 0.6, None), ("μ_ball=0.3", 0.3, None),
                    ("μ_ball=0.15", 0.15, None), ("μ_ball=0.3 + μ_shell=0.10", 0.3, 0.10)):
    pv2.static_geoms = ORIG
    row, thr = {}, None
    for fr in FL:
        r, tr, tq, dt = run(145.0, 200.0, fr, mu_ball=kb, mu_shell=ks)
        row[fr] = bool(r["launched"])
        if r["launched"] and thr is None: thr = fr
    r5, tr5, tq5, dt5 = run(145.0, 200.0, 20.0, mu_ball=kb, mu_shell=ks)
    sp = np.array([s["v"] for s in tr5]); load = tq5[sp > 0.05] if (sp > 0.05).any() else tq5
    res[lab] = {"threshold": thr, "load_mean": round(float(load.mean()),3), "by_limit": row}
    print("%-24s %-8s %-9.3f %s" % (lab, thr if thr else ">0.8", load.mean(),
        "  ".join("%s@%.1f" % ("OK" if v else "--", k) for k, v in row.items())))

print()
print("=== 摩擦 + 方案A 唇口喇叭（200 rpm）===")
for lab, kb in (("A + μ_ball=0.6", 0.6), ("A + μ_ball=0.3", 0.3)):
    pv2.static_geoms = flare
    row, thr = {}, None
    for fr in FL:
        r, tr, tq, dt = run(145.0, 200.0, fr, mu_ball=kb)
        row[fr] = bool(r["launched"])
        if r["launched"] and thr is None: thr = fr
    res[lab] = {"threshold": thr, "by_limit": row}
    print("%-24s 门槛=%-6s %s" % (lab, thr if thr else ">0.8",
        "  ".join("%s@%.1f" % ("OK" if v else "--", k) for k, v in row.items())))
pv2.static_geoms = ORIG
Path("simulation/mujoco/out/summary_v2_friction.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
print("\n已写 out/summary_v2_friction.json")
