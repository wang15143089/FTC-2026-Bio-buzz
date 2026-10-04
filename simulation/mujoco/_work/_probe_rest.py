# -*- coding: utf-8 -*-
"""Probe: why does the ball sit still on a 5 deg tray?"""
import math, sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import opt_lib as ol
import r10_cradle as R10
import mujoco, numpy as np

pv2 = ol.pv2
R_IN = 107.974
CUT_X = 38.901
A_LIP = 275.0
PIVOT = (-0.806, 0.423)
TRAY_X1 = 150.0
TILT, SIN_T, COS_T = 5.0, math.sin(math.radians(5.0)), math.cos(math.radians(5.0))


def rotor(kind, hub_r=12.0):
    def f():
        out = [("hub", (0.0, 0.0, 0.0), (hub_r, 17.0), 0.0, "cylY")]
        for i, a in enumerate((18.0, 138.0, 258.0), 1):
            out.append(("arm_%d" % i, (28.0, 0.0, 0.0), (36.0, 18.0, 10.0), a, "box"))
            out.append(("hinge_%d" % i, (46.0, 0.0, 0.0), (5.0, 50.0), a, "cylY"))
            out.append(("blade_%d" % i, (52.0, 0.0, 0.0), (12.0, 96.0, 30.0), a, "box"))
            out.append(("flex_%d" % i, (58.0, 0.0, 0.0), (4.0, 96.0, 34.0), a, "box"))
        return out
    return f


def probe(ball_r, ball_m, nip, mu, xc, sec=3.0):
    pv2.HALF_SPACING = nip / 2.0 + 48.0
    pv2.R_CARRY = R_IN - ball_r
    pv2.PIVOT_X, pv2.PIVOT_Z = PIVOT
    pv2.R_IN = R_IN
    pv2.R_OUT = R_IN + pv2.SHELL_WALL
    R10.R_MID = R_IN + 3.5
    pv2.BALL_R = ball_r
    pv2.BALL_MASS = ball_m
    pv2.static_geoms = (lambda: R10.stat(CUT_X, A_LIP, tray_x1=TRAY_X1))
    pv2.paddle_parts = rotor("cad")
    bx, bz = xc - ball_r * SIN_T, pv2.tray_top_z(xc) + ball_r * COS_T
    xml, ctrl = pv2.build_xml(1620.0, -1, 0.0, bx, bz)
    xml = xml.replace('kv="0.08"', 'kv="40.0"')
    xml = xml.replace('forcerange="-1.5 1.5"', 'forcerange="0 0"')
    xml = xml.replace('class="ball"><geom friction="1.0 0.02 0.0001"',
                      'class="ball"><geom friction="%g 0.02 0.0001"' % mu)
    m = mujoco.MjModel.from_xml_string(xml)
    d = mujoco.MjData(m)
    d.ctrl[:] = ctrl
    mujoco.mj_forward(m, d)
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    bgeom = {g for g in range(m.ngeom) if m.geom_bodyid[g] == bid}
    dt = m.opt.timestep
    print("   start=(%.2f, %.2f)  mu=%.2f  r=%.3f" % (bx, bz, mu, ball_r), flush=True)
    t = 0.0
    for i in range(int(sec / dt)):
        mujoco.mj_step(m, d)
        if i % int(0.25 / dt) == 0:
            p = d.xpos[bid] * 1000.0
            rx, rz = p[0] - pv2.PADDLE_CX, p[2] - pv2.PADDLE_CZ
            cnt = sorted({mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM,
                           int(cc.geom2 if cc.geom1 in bgeom else cc.geom1))
                          for cc in d.contact[:d.ncon] if (cc.geom1 in bgeom or cc.geom2 in bgeom)})
            print("      t=%4.2f x=%7.2f z=%7.2f r=%7.2f ang=%6.1f  touch=%s"
                  % (i * dt, p[0], p[2], math.hypot(rx, rz),
                     math.degrees(math.atan2(rz, rx)) % 360.0, ",".join(cnt) or "-"), flush=True)
    return 0


if __name__ == "__main__":
    print("=== NECTAR mu sweep, tray_x1=150, foot at xc=102 ===", flush=True)
    for mu in (0.05, 0.20, 0.40):
        probe(45.974, 0.130, 82.0, mu, 102.0)
    print("=== POLLEN mu sweep, xc=110 ===", flush=True)
    probe(35.56, 0.060, 64.0, 0.40, 110.0)
    raise SystemExit(0)
