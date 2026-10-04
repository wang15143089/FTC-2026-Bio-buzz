# -*- coding: utf-8 -*-
"""R8: correct signed contact wrench on the ball; verify sumF = m*a; per-contact dirs."""
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


def run(bx=20.9, angs=(10., 190.), sec=3.0, rpm=N_FREE, t0=1.0, t1=2.2):
    pv2.static_geoms = BASE
    pv2.paddle_parts = blades(list(angs))
    xml, ctrl = pv2.build_xml(1620.0, -1, rpm * 2 * math.pi / 60.0, bx, pv2.tray_top_z(bx) + pv2.BALL_R)
    xml = xml.replace('kv="0.08"', 'kv="%.6f"' % KV)
    xml = xml.replace('forcerange="-1.5 1.5"', 'forcerange="-%g %g"' % (T_STALL, T_STALL))
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    jid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "ball_free")
    dadr = m.jnt_dofadr[jid]
    bg = set(g for g in range(m.ngeom) if m.geom_bodyid[g] == bid)
    dt = m.opt.timestep
    nxt = t0
    for i in range(int(sec / dt)):
        mujoco.mj_step(m, d)
        t = i * dt
        if t >= nxt and t <= t1:
            nxt += 0.3
            c = d.xpos[bid] * 1000.0
            rx, rz = c[0] - pv2.PADDLE_CX, c[2] - pv2.PADDLE_CZ
            th = math.atan2(rz, rx)
            out = np.array([math.cos(th), 0.0, math.sin(th)])
            fwd = np.array([math.sin(th), 0.0, -math.cos(th)])
            fball = np.zeros(3)
            print("  t=%.2f  r=%.2f ang=%.1f" % (t, math.hypot(rx, rz), math.degrees(th) % 360.0))
            for k in range(d.ncon):
                con = d.contact[k]
                if (con.geom1 in bg) or (con.geom2 in bg):
                    o = con.geom2 if con.geom1 in bg else con.geom1
                    nm = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, o)
                    ff = np.zeros(6); mujoco.mj_contactForce(m, d, k, ff)
                    n = np.array(con.frame[0:3])
                    tv = ff[1] * np.array(con.frame[3:6]) + ff[2] * np.array(con.frame[6:9])
                    f = ff[0] * n
                    sgn = -1.0 if con.geom1 in bg else 1.0
                    fball += sgn * (f + tv)
                    print("     %-16s Fn=%5.2f Ft=%5.2f  onBall: O%+6.2f F%+6.2f  |n|check=%.3f"
                          % (nm, ff[0], math.hypot(ff[1], ff[2]),
                             float(sgn * (f + tv) @ out), float(sgn * (f + tv) @ fwd),
                             float(np.linalg.norm(n))))
            ma = 0.060 * np.array(d.cacc[bid][0:3])
            grav = np.array([0.0, 0.0, -0.5886])
            print("     SUM_contact=%s  +gravity=%s   m*a=%s"
                  % (str([round(float(x), 3) for x in fball]),
                     str([round(float(x), 3) for x in (fball + grav)]),
                     str([round(float(x), 3) for x in ma])))


if __name__ == "__main__":
    print("=== signed wrench on ball; O=outward radial, F=forward ===")
    run(20.9)
