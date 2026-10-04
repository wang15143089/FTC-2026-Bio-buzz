# -*- coding: utf-8 -*-
"""T2: in the R25 shell+tray scene, what stops the ball rolling down to the nest?"""
import math, sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import opt_lib as ol
import r10_cradle as R10
import r23
import mujoco, numpy as np

pv2 = ol.pv2
R_IN = 107.974; CUT_X = 38.901; A_LIP = 275.0; PIVOT = (-0.806, 0.423)
TRAY_X1 = 150.0; TILT = 5.0; WHEEL_R = 48.0
SIN_T = math.sin(math.radians(TILT)); COS_T = math.cos(math.radians(TILT))
HUB_ONLY = lambda: [("hub", (0.0,0.0,0.0), (12.0,17.0), 0.0, "cylY")]

def setup(ball_r, ball_m, nip, tray_x1=TRAY_X1):
    pv2.HALF_SPACING = nip/2.0 + WHEEL_R
    pv2.R_CARRY = R_IN - ball_r
    pv2.PIVOT_X, pv2.PIVOT_Z = PIVOT
    pv2.R_IN = R_IN; pv2.R_OUT = R_IN + pv2.SHELL_WALL
    R10.R_MID = R_IN + 3.5
    pv2.BALL_R = ball_r; pv2.BALL_MASS = ball_m
    pv2.static_geoms = (lambda: R10.stat(CUT_X, A_LIP, tray_x1=tray_x1))

def run(tag, ball_r, ball_m, nip, paddle, paddle_ctrl, sec=6.0, xc=None, mu=0.40):
    setup(ball_r, ball_m, nip)
    pv2.paddle_parts = paddle
    if xc is None:
        xc = min(120.0, TRAY_X1 - ball_r - 8.0)
    bx = xc - ball_r*SIN_T
    bz = pv2.tray_top_z(xc) + ball_r*COS_T
    w = 60.0*2*math.pi/60.0
    xml, ctrl = pv2.build_xml(1620.0, -1, paddle_ctrl*w, bx, bz)
    xml = xml.replace('class="ball"><geom friction="1.0 0.02 0.0001"',
                      'class="ball"><geom friction="%g 0.02 0.0001"' % mu)
    if paddle_ctrl == 0.0:
        xml = xml.replace('name="paddle_vel" joint="paddle_joint" kv="0.08"',
                          'name="paddle_vel" joint="paddle_joint" kv="2e4"')
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    bgeom = {g for g in range(m.ngeom) if m.geom_bodyid[g] == bid}
    dt = m.opt.timestep; n = int(sec/dt)
    tr = []
    for i in range(n):
        mujoco.mj_step(m, d)
        if i % 250 == 0:
            p = d.xpos[bid]*1000.0
            rx, rz = p[0]-pv2.PADDLE_CX, p[2]-pv2.PADDLE_CZ
            cnt = sorted({mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM,
                           int(cc.geom2 if cc.geom1 in bgeom else cc.geom1))
                          for cc in d.contact[:d.ncon] if (cc.geom1 in bgeom or cc.geom2 in bgeom)})
            tr.append({"t": round(i*dt,2), "x": round(float(p[0]),2), "z": round(float(p[2]),2),
                       "r": round(math.hypot(rx,rz),2),
                       "ang": round(math.degrees(math.atan2(rz,rx))%360.0,1),
                       "touch": ",".join(cnt) or "-"})
    print("%-26s r0=%6.2f rmin=%6.2f angmin=%6.1f touch0=%-18s touch_end=%-18s" %
          (tag, tr[0]["r"], min(s["r"] for s in tr), min(s["ang"] for s in tr),
           tr[0]["touch"][:18], tr[-1]["touch"][:18]))
    for s in tr[::max(1,len(tr)//8)]:
        print("     t=%5.2f x=%7.2f z=%7.2f r=%6.2f ang=%6.1f  %s" % (s["t"],s["x"],s["z"],s["r"],s["ang"],s["touch"]))
    return tr

N = dict(ball_r=45.974, ball_m=0.130, nip=82.0)
P = dict(ball_r=35.56, ball_m=0.060, nip=64.0)
print("=== NECTAR (r=45.974) ===")
run("N no-paddle(hub only)", **N, paddle=HUB_ONLY, paddle_ctrl=0.0)
print()
print("=== POLLEN (r=35.56) ===")
run("P no-paddle(hub only)", **P, paddle=HUB_ONLY, paddle_ctrl=0.0)
