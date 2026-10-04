# -*- coding: utf-8 -*-
"""R5/R2 静置与低速诊断：球停在哪、靠什么支撑、多久被指片抓住。"""
import math, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import opt_lib as ol
import mujoco

pv2 = ol.pv2

def blades(angs, W=pv2.PADDLE_W):
    def f():
        parts = [("hub", (0., 0., 0.), (18., 17., 18.), 0., "cylY")]
        for i, a in enumerate(angs, 1):
            parts += [("arm_%d" % i, (30., 0, 0), (16., 9., 5.), a, "box"),
                      ("blade_%d" % i, (52., 0, 0), (6., W / 2., 15.), a, "box"),
                      ("flex_%d" % i, (58., 0, 0), (2., W / 2., 17.), a, "box")]
        return parts
    return f

def th2(ts):
    return blades([(360. - t) % 360. for t in ts])

FL = ol.GEOM["A 唇口喇叭"][0]
DP = ol.GEOM["D 球窝抬高6.8"][0]
ol.GEOM["R2"] = (FL, th2((350., 170.)))
ol.GEOM["R5"] = (DP, th2((350., 170.)))
ol.GEOM["V0"] = ol.GEOM["V0 现状"]
ol.GEOM["D"]  = ol.GEOM["D 球窝抬高6.8"]

def rest_contacts(name, bx=145.0, sec=6.0):
    ol.apply_geom(name)
    xml, ctrl = pv2.build_xml(1620.0, -1, 0.0, bx, pv2.tray_top_z(bx) + pv2.BALL_R)
    m = mujoco.MjModel.from_xml_string(xml)
    d = mujoco.MjData(m)
    d.ctrl[:] = ctrl
    mujoco.mj_forward(m, d)
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    bg = {g for g in range(m.ngeom) if m.geom_bodyid[g] == bid}
    dt = m.opt.timestep
    for _ in range(int(sec / dt)):
        mujoco.mj_step(m, d)
    p = d.xpos[bid] * 1000.0
    rx, rz = p[0] - pv2.PADDLE_CX, p[2] - pv2.PADDLE_CZ
    r = math.hypot(rx, rz)
    ang = math.degrees(math.atan2(rz, rx)) % 360.0
    cnt = {}
    for c in range(d.ncon):
        con = d.contact[c]
        for g in (con.geom1, con.geom2):
            if g in bg:
                o = con.geom2 if g == con.geom1 else con.geom1
                nm = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, o) or ("geom%d" % o)
                cnt[nm] = cnt.get(nm, 0) + 1
    print("[%s] rest x=%.2f z=%.2f  r=%.2f  ang=%.1f deg  contacts=%s"
          % (name, p[0], p[2], r, ang, cnt))
    return p, r, ang

def timings(name, rpm, bx=145.0, sec=12.0, fr=1.0):
    r = ol.run(name, bx=bx, rpm=rpm, fr=fr, sec=sec, trace=True, fw=1620.0)
    tr = r["_trace"]
    t_set = None
    for s in tr:
        if s["v"] < 0.05 and s["t"] > 0.3:
            t_set = s["t"]
            break
    t_grab = None
    base = t_set if t_set is not None else 0.0
    for s in tr:
        if s["t"] > base + 0.05 and s["v"] > 0.10:
            t_grab = s["t"]
            break
    lx = [s["lx"] for s in tr]
    print("[%s @%g rpm] settled=%.2fs  grabbed=%.2fs  creep=%s  launched=%s  peak=%.3f Nm  exit_v=%.2f"
          % (name, rpm, t_set if t_set else -1,
             t_grab if t_grab else -1,
             ("%.2f" % (t_grab - base)) if (t_grab and t_set) else "-",
             r["launched"], r["torque_peak_Nm"],
             r["exit_speed"] if "exit_speed" in r else float("nan")))
    return r

print("=== as-received rest positions (paddle static) ===")
for nm in ("V0", "D", "R2", "R5"):
    rest_contacts(nm)

print()
print("=== timings ===")
for nm in ("R5", "R2"):
    for rpm in (40, 70, 90, 145):
        timings(nm, rpm)
