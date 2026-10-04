# -*- coding: utf-8 -*-
"""第二轮：A/D 参数加码与组合"""
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

def build(flare=0, step=0.0, tray_x0=None):
    def f():
        g = list(ORIG())
        if flare:
            g = [t for t in g if t[0] != "shell_lip_face"]
            for k in range(flare):
                g.append(seg(227.5 + 4.0*k, 95.5 + 4.0*k))
        if step > 0:
            ztop = pv2.tray_top_z(-2.0) + step
            g.append(("rest_pad", "shell", "box", (30.0, pv2.FEEDER_W, step+6.0),
                      (-2.0, 0.0, ztop-(step+6.0)/2.0), pv2.quat_y(0.0)))
        if tray_x0 is not None:
            out = []
            for t in g:
                if t[0] == "tray":
                    x0, x1 = tray_x0, pv2.TRAY_X1
                    nmx, nmz = pv2.normal(-pv2.TILT)
                    xm = 0.5*(x0+x1); zt = pv2.tray_top_z(xm)
                    L = (x1-x0)/math.cos(math.radians(pv2.TILT))
                    t = ("tray","shell","box",(L,pv2.FEEDER_W,pv2.TRAY_T),
                         (xm-nmx*pv2.TRAY_T/2.0,0.0,zt-nmz*pv2.TRAY_T/2.0), pv2.quat_y(-pv2.TILT))
                out.append(t)
            g = out
        return g
    return f

def run(bx, rpm, fr, sec=7.0, fw=1620.0):
    xml, ctrl = pv2.build_xml(fw, -1, rpm*2*math.pi/60.0, bx, pv2.tray_top_z(bx)+pv2.BALL_R)
    xml = xml.replace('-1.5 1.5"', '-%g %g"' % (fr, fr))
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    dt = m.opt.timestep; n = int(round(sec/dt)); tr = []
    for i in range(n):
        mujoco.mj_step(m, d)
        if i % max(1,int(round(0.002/dt))) == 0:
            p = d.xpos[bid]; lx, lz = pv2.to_shooter(float(p[0])*1000., float(p[2])*1000.)
            rx, rz = float(p[0])*1000.-pv2.PADDLE_CX, float(p[2])*1000.-pv2.PADDLE_CZ
            tr.append({"t":round(i*dt,4),"x":round(float(p[0])*1000.,3),"z":round(float(p[2])*1000.,3),
                       "v":round(float(np.linalg.norm(d.cvel[bid][3:])),4),"vx":round(float(d.cvel[bid][3]),4),
                       "vz":round(float(d.cvel[bid][5]),4),"r":round(math.hypot(rx,rz),3),
                       "ang":round(math.degrees(math.atan2(rz,rx))%360.,2),"lx":round(lx,3),"lz":round(lz,3)})
    return pv2.analyse(tr), tr

CASES = [
 ("A2 喇叭3段",            dict(flare=3)),
 ("A3 喇叭5段",            dict(flare=5)),
 ("D10 抬高10mm",          dict(step=10.0)),
 ("D13 抬高13mm",          dict(step=13.0)),
 ("A3+D10",               dict(flare=5, step=10.0)),
 ("A3+D13",               dict(flare=5, step=13.0)),
 ("A3+D10+托板缩进",        dict(flare=5, step=10.0, tray_x0=-12.0)),
]
FL = (0.3, 0.4, 0.5, 0.6, 0.8)
res = {}
print("%-20s %-9s %-8s %s" % ("方案", "停位r", "门槛", "各力矩限幅"))
print("-"*88)
for name, kw in CASES:
    pv2.static_geoms = build(**kw)
    r0, _ = run(145.0, 200.0, 5.0, sec=3.0)
    rp = r0["settled_position_mm"]; rr = math.hypot(rp[0]-pv2.PADDLE_CX, rp[1]-pv2.PADDLE_CZ)
    row, thr = {}, None
    for fr in FL:
        r, tr = run(145.0, 200.0, fr)
        row[fr] = bool(r["launched"])
        if r["launched"] and thr is None: thr = fr
    res[name] = {"rest_r": round(rr,2), "threshold": thr, "by_limit": row}
    print("%-20s %-9.1f %-8s %s" % (name, rr, thr if thr else ">0.8",
        "  ".join("%s@%.1f" % ("OK" if v else "--", k) for k, v in row.items())))
pv2.static_geoms = ORIG
Path("simulation/mujoco/out/summary_v2_geom_options2.json").write_text(
    json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
print("\n已写 out/summary_v2_geom_options2.json")
