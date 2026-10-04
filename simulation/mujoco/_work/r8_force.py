# -*- coding: utf-8 -*-
"""R8: which contact actually resists the paddle? (pocket start, real 25-4 motor)"""
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


def go(bx, angs=(10.0, 190.0), sec=6.0, rpm=N_FREE, every=0.25):
    pv2.static_geoms = BASE
    pv2.paddle_parts = blades(list(angs))
    xml, ctrl = pv2.build_xml(1620.0, -1, rpm * 2 * math.pi / 60.0, bx,
                              pv2.tray_top_z(bx) + pv2.BALL_R)
    xml = xml.replace('kv="0.08"', 'kv="%.6f"' % KV)
    xml = xml.replace('forcerange="-1.5 1.5"', 'forcerange="-%g %g"' % (T_STALL, T_STALL))
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
    pid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "paddle_joint")
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    aid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "paddle_vel")
    bg = set(g for g in range(m.ngeom) if m.geom_bodyid[g] == bid)
    dt = m.opt.timestep
    agg = {}
    nxt = 0.0
    print("  t     ballx  ballz    r     ang     v     rpm    |F|   | contacts")
    for i in range(int(sec / dt)):
        mujoco.mj_step(m, d)
        t = i * dt
        for c in range(d.ncon):
            con = d.contact[c]
            if (con.geom1 in bg) or (con.geom2 in bg):
                o = con.geom2 if con.geom1 in bg else con.geom1
                nm = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, o) or ("g%d" % o)
                ff = np.zeros(6); mujoco.mj_contactForce(m, d, c, ff)
                a = agg.setdefault(nm, [0, 0.0, 0.0, 0.0, 0.0])
                a[0] += 1; a[1] += abs(ff[0])
                a[2] = max(a[2], abs(ff[0])); a[3] = max(a[3], max(0.0, -con.dist * 1000.0))
                a[4] = max(a[4], abs(ff[1]))
        if t >= nxt:
            nxt += every
            p = d.xpos[bid] * 1000.0
            rx, rz = p[0] - pv2.PADDLE_CX, p[2] - pv2.PADDLE_CZ
            txt = []
            for c in range(d.ncon):
                con = d.contact[c]
                if (con.geom1 in bg) or (con.geom2 in bg):
                    o = con.geom2 if con.geom1 in bg else con.geom1
                    nm = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, o) or ("g%d" % o)
                    ff = np.zeros(6); mujoco.mj_contactForce(m, d, c, ff)
                    txt.append("%s Fn=%.1f Ft=%.1f pen=%.2f" % (nm, abs(ff[0]), abs(ff[1]), max(0.0, -con.dist * 1000.0)))
            print("  %5.2f %7.2f %7.2f %6.2f %6.1f %6.3f %7.1f %6.3f | %s"
                  % (t, p[0], p[2], math.hypot(rx, rz),
                     math.degrees(math.atan2(rz, rx)) % 360.0,
                     float(np.linalg.norm(d.cvel[bid][3:])),
                     math.degrees(d.qvel[pid]) / 6.0, abs(float(d.actuator_force[aid])),
                     " ; ".join(txt)))

    print("  --- contact summary (geom: samples, mean Fn, max Fn, max pen mm, max Ft) ---")
    for nm, a in sorted(agg.items(), key=lambda kv: -kv[1][1]):
        print("    %-22s n=%5d  meanFn=%6.2f  maxFn=%7.2f  maxPen=%.2f  maxFt=%.2f"
              % (nm, a[0], a[1] / max(1, a[0]), a[2], a[3], a[4]))


if __name__ == "__main__":
    print("=== pocket start x0=20.9, blades (10,190), 25-4 @290 rpm, 6 s ===")
    go(20.9)
