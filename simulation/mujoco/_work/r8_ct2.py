# -*- coding: utf-8 -*-
"""R8: decompose every ball contact in the BALL frame (forward / outward / axial)."""
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


def run(bx=20.9, angs=(10., 190.), sec=6.0, rpm=N_FREE, t0=1.9, t1=2.3):
    pv2.static_geoms = BASE
    pv2.paddle_parts = blades(list(angs))
    xml, ctrl = pv2.build_xml(1620.0, -1, rpm * 2 * math.pi / 60.0, bx, pv2.tray_top_z(bx) + pv2.BALL_R)
    xml = xml.replace('kv="0.08"', 'kv="%.6f"' % KV)
    xml = xml.replace('forcerange="-1.5 1.5"', 'forcerange="-%g %g"' % (T_STALL, T_STALL))
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    bg = set(g for g in range(m.ngeom) if m.geom_bodyid[g] == bid)
    dt = m.opt.timestep
    nxt = t0
    MASS = 0.060
    print(" every 0.05 s: ball r/ang/v | per contact: geom Fn pen |d| pushF pushO pushY | offF offO")
    for i in range(int(sec / dt)):
        mujoco.mj_step(m, d)
        t = i * dt
        if t >= nxt and t <= t1:
            nxt += 0.05
            c = d.xpos[bid] * 1000.0
            rx, rz = c[0] - pv2.PADDLE_CX, c[2] - pv2.PADDLE_CZ
            rr = math.hypot(rx, rz); th = math.atan2(rz, rx)
            fwd = np.array([math.sin(th), 0.0, -math.cos(th)])
            out = np.array([math.cos(th), 0.0, math.sin(th)])
            yy = np.array([0.0, 1.0, 0.0])
            net = np.zeros(3); lines = []
            for k in range(d.ncon):
                con = d.contact[k]
                if (con.geom1 in bg) or (con.geom2 in bg):
                    o = con.geom2 if con.geom1 in bg else con.geom1
                    nm = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, o)
                    ff = np.zeros(6); mujoco.mj_contactForce(m, d, k, ff)
                    fn = abs(ff[0])
                    cp = con.pos * 1000.0
                    dv = c - cp
                    dist = float(np.linalg.norm(dv))
                    push = dv / max(dist, 1e-9)
                    net += push * fn
                    lines.append("%-16s Fn=%5.1f pen=%.2f |d|=%5.2f  F%+.2f O%+.2f Y%+.2f | ofF%+6.1f ofO%+6.1f"
                                 % (nm, fn, max(0.0, -con.dist * 1000), dist,
                                    float(push @ fwd), float(push @ out), float(push @ yy),
                                    float(dv @ fwd), float(dv @ out)))
            netF = net + np.array([0.0, 0.0, -9.81 * MASS])
            ma = MASS * d.cacc[bid][0:3]
            print("  t=%.2f ball r=%.2f ang=%.1f v=%.3f  netF(N)=%s  m*a(N)=%s"
                  % (t, rr, math.degrees(th) % 360.0,
                     float(np.linalg.norm(d.cvel[bid][3:])),
                     str([round(float(x), 3) for x in netF]),
                     str([round(float(x), 3) for x in ma])))
            for L in lines:
                print("        " + L)


if __name__ == "__main__":
    print("=== pocket start x0=20.9, blades polar(350,170), 25-4 @290 rpm ===")
    run(20.9)
