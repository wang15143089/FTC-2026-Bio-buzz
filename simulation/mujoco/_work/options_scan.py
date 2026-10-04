# -*- coding: utf-8 -*-
"""接触几何改善方案 A/B/C/D 逐个仿真对比：发射门槛扭矩"""
import json, math, sys, importlib.util
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
import mujoco, numpy as np
spec = importlib.util.spec_from_file_location("pv2", r"simulation/mujoco/pollen_v2_sim.py")
pv2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(pv2)

ORIG_STATIC = pv2.static_geoms
ORIG_PARTS  = pv2.paddle_parts
R_IN, R_OUT, W = pv2.R_IN, pv2.R_OUT, pv2.PADDLE_W

def seg(am, r_in, da=4.0, thick=7.0, name="flare"):
    r_mid = r_in + thick/2.0
    half = 0.5*r_mid*math.radians(da)*1.35
    cx, cz = pv2.polar(r_mid, am)
    return (f"{name}_{int(round(am*10))}", "shell", "box", (2*half, pv2.FEEDER_W, thick),
            (cx, 0.0, cz), pv2.quat_y(-(am+90.0)))

def A_flare():
    def f():
        g = [t for t in ORIG_STATIC() if t[0] != "shell_lip_face"]
        g += [seg(227.5, 95.5), seg(231.5, 99.5), seg(235.5, 103.5)]
        return g
    return f

def B_tray():
    def f():
        g = []
        for t in ORIG_STATIC():
            if t[0] == "tray":
                x0, x1 = -12.0, pv2.TRAY_X1
                nmx, nmz = pv2.normal(-pv2.TILT)
                x_mid = 0.5*(x0+x1); zt = pv2.tray_top_z(x_mid)
                L = (x1-x0)/math.cos(math.radians(pv2.TILT))
                t = ("tray", "shell", "box", (L, pv2.FEEDER_W, pv2.TRAY_T),
                     (x_mid-nmx*pv2.TRAY_T/2.0, 0.0, zt-nmz*pv2.TRAY_T/2.0), pv2.quat_y(-pv2.TILT))
            g.append(t)
        return g
    return f

def D_pad(step=6.8):
    def f():
        g = list(ORIG_STATIC())
        ztop = pv2.tray_top_z(-2.0) + step
        g.append(("rest_pad", "shell", "box", (30.0, pv2.FEEDER_W, step+6.0),
                  (-2.0, 0.0, ztop-(step+6.0)/2.0), pv2.quat_y(0.0)))
        return g
    return f

def C_blade(tip=56.0):
    def f():
        parts = [("hub", (0.0,0.0,0.0), (18.0,17.0,18.0), 0.0, "cylY")]
        for i, a in enumerate((pv2.PADDLE_PHASE, pv2.PADDLE_PHASE+120.0, pv2.PADDLE_PHASE+240.0), 1):
            parts.append((f"arm_{i}", (30.0,0.0,0.0), (16.0,9.0,5.0), a, "box"))
            parts.append((f"blade_{i}", (tip-8.0,0.0,0.0), (6.0, W/2.0, 15.0), a, "box"))
            parts.append((f"flex_{i}", (tip-2.0,0.0,0.0), (2.0, W/2.0, 17.0), a, "box"))
        return parts
    return f

VAR = {
 "V0 现状":        (None, None),
 "A 唇口喇叭导入":  (None, A_flare()),
 "B 托板末端缩进":  (None, B_tray()),
 "C 叶片外缘卸载":  (lambda: setattr(pv2, "paddle_parts", C_blade(56.0)), None),
 "D 球窝抬高6.8mm": (None, D_pad(6.8)),
 "A+B":            (None, (lambda: (lambda g: g)(A_flare()()))),
}

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

FL = (0.4, 0.5, 0.6, 0.8, 1.0, 1.2)
res = {}
print("%-16s %-9s %-7s  %s" % ("方案", "停位球心r", "门槛", "各力矩限幅结果"))
print("-"*96)
for name, (ppatch, spatch) in VAR.items():
    pv2.paddle_parts = ORIG_PARTS if ppatch is None else ORIG_PARTS
    if name == "C 叶片外缘卸载": pv2.paddle_parts = C_blade(56.0)
    else: pv2.paddle_parts = ORIG_PARTS
    if name == "A 唇口喇叭导入": pv2.static_geoms = A_flare()
    elif name == "B 托板末端缩进": pv2.static_geoms = B_tray()
    elif name == "D 球窝抬高6.8mm": pv2.static_geoms = D_pad(6.8)
    elif name == "A+B":
        def AB():
            g = [t for t in ORIG_STATIC() if t[0] != "shell_lip_face"]
            g += [seg(227.5,95.5), seg(231.5,99.5), seg(235.5,103.5)]
            x0, x1 = -12.0, pv2.TRAY_X1
            nmx, nmz = pv2.normal(-pv2.TILT)
            x_mid = 0.5*(x0+x1); zt = pv2.tray_top_z(x_mid)
            L = (x1-x0)/math.cos(math.radians(pv2.TILT))
            g = [("tray","shell","box",(L,pv2.FEEDER_W,pv2.TRAY_T),
                  (x_mid-nmx*pv2.TRAY_T/2.0,0.0,zt-nmz*pv2.TRAY_T/2.0), pv2.quat_y(-pv2.TILT))
                 if t[0]=="tray" else t for t in g]
            return g
        pv2.static_geoms = AB
    else: pv2.static_geoms = ORIG_STATIC

    r0, tr0 = run(145.0, 200.0, 5.0, sec=3.0)
    rest = r0["settled_position_mm"]; rr = math.hypot(rest[0]-pv2.PADDLE_CX, rest[1]-pv2.PADDLE_CZ)
    row, thr = {}, None
    for fr in FL:
        r, tr = run(145.0, 200.0, fr)
        row[fr] = bool(r["launched"])
        if r["launched"] and thr is None: thr = fr
    res[name] = {"rest_r_mm": round(rr,2), "threshold": thr, "by_limit": row}
    print("%-16s %-9.1f %-7s  %s" % (name, rr, thr if thr else ">1.2",
        "  ".join("%s@%.1f" % ("OK" if v else "--", k) for k, v in row.items())))
pv2.static_geoms = ORIG_STATIC; pv2.paddle_parts = ORIG_PARTS
Path("simulation/mujoco/out/summary_v2_geom_options.json").write_text(
    json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
print("\n已写 out/summary_v2_geom_options.json")
