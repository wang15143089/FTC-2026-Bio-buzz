# -*- coding: utf-8 -*-
"""R8: where on the ball does the blade push? normal orientation vs radial dir."""
import math, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import r6_smooth as r6
import opt_lib as ol
import mujoco, numpy as np

pv2 = ol.pv2
T_STALL, N_FREE = 0.530, 290.0
KV = T_STALL / (N_FREE * 2 * math.pi / 60.0)
BASE = ol.GEOM["D 球窝抬高6.8"][0]


def blades(angs, W=pv2.PADDLE_W):
    def f():
        parts = [("hub", (0., 0., 0.), (18., 17., 18.), 0., "cylY")]
        for i, a in enumerate(angs, 1):
            parts += [("arm_%d" % i, (30., 0, 0), (16., 9., 5.), a, "box"),
                      ("blade_%d" % i, (52., 0, 0), (6., W / 2., 15.), a, "box"),
                      ("flex_%d" % i, (58., 0, 0), (2., W / 2., 17.), a, "box")]
        return parts
    return f


def ang_of(x, z):
    return math.degrees(math.atan2(z - pv2.PADDLE_CZ, x - pv2.PADDLE_CX)) % 360.0


def run(bx=20.9, angs=(10., 190.), sec=6.0, rpm=N_FREE):
    pv2.static_geoms = BASE
    pv2.paddle_parts = blades(list(angs))
    xml, ctrl = pv2.build_xml(1620.0, -1, rpm * 2 * math.pi / 60.0, bx, pv2.tray_top_z(bx) + pv2.BALL_R)
    xml = xml.replace('kv="0.08"', 'kv="%.6f"' % KV)
    xml = xml.replace('forcerange="-1.5 1.5"', 'forcerange="-%g %g"' % (T_STALL, T_STALL))
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
    pid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "paddle_joint")
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    bg = set(g for g in range(m.ngeom) if m.geom_bodyid[g] == bid)
    pad = set()
    for g in range(m.ngeom):
        nm = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, g)
        if nm and nm.startswith("paddle_"):
            pad.add(g)
    dt = m.opt.timestep
    nxt = 0.0
    print("   t   q(deg)  ball r / ang      blade1 r/ang   flex1 r/ang    lag  | contact(paddle): geom r ang nRad nTan Fn pen")
    for i in range(int(sec / dt)):
        mujoco.mj_step(m, d)
        t = i * dt
        if t >= nxt:
            nxt += (0.1 if t < 1.2 else 0.5)
            p = d.xpos[bid] * 1000.0
            ba = ang_of(p[0], p[2]); br = math.hypot(p[0] - pv2.PADDLE_CX, p[2] - pv2.PADDLE_CZ)
            def ga(nm):
                g = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, nm)
                gp = d.geom_xpos[g] * 1000.0
                return math.hypot(gp[0] - pv2.PADDLE_CX, gp[2] - pv2.PADDLE_CZ), ang_of(gp[0], gp[2])
            b1r, b1a = ga("paddle_blade_1"); f1r, f1a = ga("paddle_flex_1")
            txt = []
            for c in range(d.ncon):
                con = d.contact[c]
                i1, i2 = con.geom1, con.geom2
                if (i1 in bg and i2 in pad) or (i2 in bg and i1 in pad):
                    ff = np.zeros(6); mujoco.mj_contactForce(m, d, c, ff)
                    cp = con.pos * 1000.0
                    ca = ang_of(cp[0], cp[2]); cr = math.hypot(cp[0] - pv2.PADDLE_CX, cp[2] - pv2.PADDLE_CZ)
                    ur = np.array([math.cos(math.radians(ca)), 0.0, math.sin(math.radians(ca))])
                    ut = np.array([-math.sin(math.radians(ca)), 0.0, math.cos(math.radians(ca))])
                    nrm = np.array(con.frame[0:3])
                    nm = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, i1 if i1 in pad else i2)
                    txt.append("%s r=%.1f a=%.0f nR=%+.2f nT=%+.2f Fn=%.1f pen=%.2f"
                               % (nm, cr, ca, float(nrm @ ur), float(nrm @ ut), abs(ff[0]), max(0.0, -con.dist * 1000)))
            print("  %5.2f %7.1f  %6.2f /%6.1f   %5.1f/%6.1f  %5.1f/%6.1f %6.1f | %s"
                  % (t, math.degrees(d.qpos[pid]) % 360.0, br, ba, b1r, b1a, f1r, f1a,
                     (b1a - ba + 540.0) % 360.0 - 180.0, " ; ".join(txt)))


if __name__ == "__main__":
    print("=== pocket start x0=20.9, blades polar(350,170), 25-4 @290 rpm, 6 s ===")
    run(20.9)
