# -*- coding: utf-8 -*-
"""R5 细节诊断：球从哪里停、被谁挡住、接触点在哪。"""
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

DP = ol.GEOM["D 球窝抬高6.8"][0]
ol.GEOM["R5"] = (DP, th2((350., 170.)))
ol.apply_geom("R5")
xml, ctrl = pv2.build_xml(1620.0, -1, 0.0, 145.0, pv2.tray_top_z(145.0) + pv2.BALL_R)
m = mujoco.MjModel.from_xml_string(xml)
d = mujoco.MjData(m)
d.ctrl[:] = ctrl
mujoco.mj_forward(m, d)
bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
bg = {g for g in range(m.ngeom) if m.geom_bodyid[g] == bid}
dt = m.opt.timestep
print("ball geom ids:", sorted(bg))
print("t      x       z       v      contacts(pos mm)")
for i in range(int(2.0 / dt)):
    mujoco.mj_step(m, d)
    if i % int(0.05 / dt) == 0:
        p = d.xpos[bid] * 1000.0
        v = float((d.cvel[bid][3:] ** 2).sum() ** 0.5)
        cs = []
        for c in range(d.ncon):
            con = d.contact[c]
            hit = [g for g in (con.geom1, con.geom2) if g in bg]
            if hit:
                o = con.geom2 if hit[0] == con.geom1 else con.geom1
                nm = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, o) or ("geom%d" % o)
                cs.append("%s@(%.0f,%.0f)" % (nm, con.pos[0] * 1000, con.pos[2] * 1000))
        print("%.2f  %7.2f %7.2f %6.2f  %s" % (i * dt, p[0], p[2], v, ",".join(cs)))

print()
print("--- paddle geom positions at home pose (world mm) ---")
names = [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, g) for g in range(m.ngeom)]
for g in sorted(bg):
    pass
for g in range(m.ngeom):
    nm = names[g] or ""
    if nm.startswith("paddle"):
        print("  %-18s pos=(%.1f, %.1f)  r=%.1f ang=%.1f" % (
            nm, m.geom_pos[g][0] * 1000, m.geom_pos[g][2] * 1000,
            math.hypot(m.geom_pos[g][0] * 1000 - pv2.PADDLE_CX, m.geom_pos[g][2] * 1000 - pv2.PADDLE_CZ),
            math.degrees(math.atan2(m.geom_pos[g][2] * 1000 - pv2.PADDLE_CZ, m.geom_pos[g][0] * 1000 - pv2.PADDLE_CX)) % 360))
print()
print("tray_top_z(145)=%.2f  tray_top_z(113.9)=%.2f  BALL_R=%.2f" % (
    pv2.tray_top_z(145.0), pv2.tray_top_z(113.9), pv2.BALL_R))
