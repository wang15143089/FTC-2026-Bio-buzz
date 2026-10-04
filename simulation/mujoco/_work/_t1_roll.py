# -*- coding: utf-8 -*-
"""T1: does a sphere roll down the 5-deg tray in THIS model's contact settings?"""
import math, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import opt_lib as ol
import mujoco, numpy as np
pv2 = ol.pv2
MM = 0.001
TILT = 5.0
PIVOT = (-0.806, 0.423)
R = 45.974

def scene(fr, solref, solimp, condim, slope, variant):
    ang = math.radians(-slope)
    q = (math.cos(ang/2), 0.0, math.sin(ang/2), 0.0)
    L, T = 300.0, 6.0
    xm = 0.0
    zt = PIVOT[1] + (xm - PIVOT[0]) * math.tan(math.radians(slope))
    nx, nz = math.sin(math.radians(slope)), math.cos(math.radians(slope))
    cx, cz = xm - nx*T/2, zt - nz*T/2
    bx = 100.0 - R*math.sin(math.radians(slope))
    bz = PIVOT[1] + (bx - PIVOT[0])*math.tan(math.radians(slope)) + R*math.cos(math.radians(slope))
    # ball contact with plane in the *unrotated* frame is at x = bx + R*sin
    s = []
    s.append('<mujoco model="t1">')
    s.append('<compiler angle="radian" autolimits="true"/>')
    s.append('<option timestep="0.0002" gravity="0 0 -9.81" integrator="implicitfast" cone="elliptic"/>')
    s.append('<default>')
    s.append('<geom friction="0.5 0.01 0.0001" solref="%s" solimp="%s"/>' % (solref, solimp))
    s.append('<default class="ball"><geom friction="%g 0.02 0.0001" solref="0.010 1" solimp="0.9 0.95 0.002" priority="1" condim="%d"/></default>' % (fr, condim))
    s.append('</default>')
    s.append('<worldbody>')
    s.append('<geom name="tray" type="box" size="%.6f 0.054 %.6f" pos="%.6f 0 %.6f" quat="%.6f 0 %.6f 0"/>' % (L/2*MM, T/2*MM, cx*MM, cz*MM, q[0], q[2]))
    s.append('<body name="ball" pos="%.6f 0 %.6f">' % (bx*MM, bz*MM))
    s.append('<freejoint name="bf"/>')
    s.append('<geom name="bg" class="ball" type="sphere" size="%.6f" mass="0.130"/>' % (R*MM))
    s.append('</body></worldbody></mujoco>')
    return "\n".join(s), bx, bz

def go(name, **kw):
    xml, bx, bz = scene(**kw)
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    mujoco.mj_forward(m, d)
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    dt = m.opt.timestep; n = int(2.0/dt)
    tr = []
    for i in range(n):
        mujoco.mj_step(m, d)
        if i % 500 == 0:
            p = d.xpos[bid]*1000.0
            tr.append((round(i*dt,2), round(float(p[0]),2), round(float(p[2]),2)))
    dx = tr[-1][1] - bx
    print("%-28s dx=%8.2f  z0=%.2f z1=%.2f  trace=%s" % (name, dx, bz, tr[-1][2], tr[:6]))
    return dx

print("start x=%.2f" % (100.0 - R*math.sin(math.radians(5))))
go("A default 5deg condim3", fr=1.0, solref="0.008 1", solimp="0.95 0.99 0.001", condim=3, slope=5.0, variant=0)
go("B ball solref 0.010-1", fr=1.0, solref="0.010 1", solimp="0.9 0.95 0.002", condim=3, slope=5.0, variant=0)
go("C condim1 (slide only)", fr=1.0, solref="0.010 1", solimp="0.9 0.95 0.002", condim=1, slope=5.0, variant=0)
go("D 5deg, mu_ball 0.4", fr=0.4, solref="0.010 1", solimp="0.9 0.95 0.002", condim=3, slope=5.0, variant=0)
go("E 20deg slope", fr=1.0, solref="0.010 1", solimp="0.9 0.95 0.002", condim=3, slope=20.0, variant=0)
