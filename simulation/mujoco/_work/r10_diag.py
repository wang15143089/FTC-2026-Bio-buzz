# -*- coding: utf-8 -*-
"""R10 diagnosis: where does the ball actually settle with a STATIC paddle?"""
import math, sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import r6_smooth as r6
import opt_lib as ol
import r10_cradle as R10
import mujoco, numpy as np

pv2 = ol.pv2


def settle(tag, geom, bx=145.0, sec=10.0, mu=0.40, rpm=0.0):
    st, pt = geom
    pv2.static_geoms, pv2.paddle_parts = st, pt
    xml, ctrl = pv2.build_xml(10.0, -1, rpm * 2 * math.pi / 60.0, bx,
                              pv2.tray_top_z(bx) + pv2.BALL_R)
    xml = xml.replace('class="ball"><geom friction="1.0 0.02 0.0001"',
                      'class="ball"><geom friction="%g 0.02 0.0001"' % mu)
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    bg = {g for g in range(m.ngeom) if m.geom_bodyid[g] == bid}
    n = int(sec / m.opt.timestep)
    hist = []
    for i in range(n):
        mujoco.mj_step(m, d)
        if i % 500 == 0:
            p = d.xpos[bid] * 1000.0
            rx, rz = p[0] - pv2.PADDLE_CX, p[2] - pv2.PADDLE_CZ
            hist.append((round(i*m.opt.timestep,2), round(p[0],1), round(p[2],1),
                         round(math.hypot(rx,rz),1), round(math.degrees(math.atan2(rz,rx))%360.0,1)))
    p = d.xpos[bid] * 1000.0
    rx, rz = p[0] - pv2.PADDLE_CX, p[2] - pv2.PADDLE_CZ
    cnt = {}
    for c in range(d.ncon):
        con = d.contact[c]
        for g in (con.geom1, con.geom2):
            if g in bg:
                o = con.geom2 if g == con.geom1 else con.geom1
                nm = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, o) or ("geom%d" % o)
                cnt[nm] = cnt.get(nm, 0) + 1
    print("  %-18s rest=(%.1f, %.1f)  r=%.1f  ang=%.1f  contacts=%s" % (tag, p[0], p[2], math.hypot(rx,rz), math.degrees(math.atan2(rz,rx))%360.0, cnt))
    print("      hist:", hist[::4])
    return p


print("=== static paddle (rpm=0), mu=0.40, load at x=145 ===")
settle("R10 cut56 lip292", R10.make_geom(56.0, 292.0))
settle("R10 cut56 lip300", R10.make_geom(56.0, 300.0))
settle("R10 cut70 lip292", R10.make_geom(70.0, 292.0))
settle("R5 (DPB)", (lambda: r6.DPB(), r6.th2((350.0, 170.0))))
print()
print("=== targets ===")
print("  cradle bottom 270deg: (%.2f, %.2f)  r=58.40" % (pv2.PADDLE_CX, pv2.PADDLE_CZ - pv2.R_CARRY))
print("  arc R_IN=%.2f  tray foot x=%.1f  R_CARRY=%.2f" % (pv2.R_IN, 56.2, pv2.R_CARRY))
