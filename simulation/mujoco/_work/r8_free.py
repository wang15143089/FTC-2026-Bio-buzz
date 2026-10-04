# -*- coding: utf-8 -*-
"""R8: where does the ball go with NO blades at all (natural nest + rho(t) curve)?"""
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


def roll(angs, bx=145.0, sec=3.0, rpm=0.0, static=None, every=0.05, quiet=False):
    pv2.static_geoms = static or BASE
    pv2.paddle_parts = blades(angs)
    xml, ctrl = pv2.build_xml(1620.0, -1, rpm * 2 * math.pi / 60.0, bx,
                              pv2.tray_top_z(bx) + pv2.BALL_R)
    xml = xml.replace('kv="0.08"', 'kv="%.6f"' % KV)
    xml = xml.replace('forcerange="-1.5 1.5"', 'forcerange="-%g %g"' % (T_STALL, T_STALL))
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    dt = m.opt.timestep
    out = []
    for i in range(int(sec / dt)):
        mujoco.mj_step(m, d)
        if i % int(every / dt) == 0:
            p = d.xpos[bid] * 1000.0
            rx, rz = p[0] - pv2.PADDLE_CX, p[2] - pv2.PADDLE_CZ
            s = {"t": round(i * dt, 3), "x": round(p[0], 2), "z": round(p[2], 2),
                 "r": round(math.hypot(rx, rz), 2),
                 "ang": round(math.degrees(math.atan2(rz, rx)) % 360.0, 1),
                 "v": round(float(np.linalg.norm(d.cvel[bid][3:])), 3)}
            out.append(s)
            if not quiet:
                print("   t=%.2f  x=%8.2f z=%8.2f  r=%7.2f  ang=%6.1f  v=%.3f" %
                      (s["t"], s["x"], s["z"], s["r"], s["ang"], s["v"]))
    return out


if __name__ == "__main__":
    print("=== A. no blades, paddle stopped: natural roll-in ===")
    a = roll([], rpm=0.0, sec=3.0)
    print("   settled: x=%.2f z=%.2f r=%.2f ang=%.1f" % (a[-1]["x"], a[-1]["z"], a[-1]["r"], a[-1]["ang"]))
    print()
    print("=== B. no blades, paddle at 290 rpm (pure geometry, no interference) ===")
    b = roll([], rpm=N_FREE, sec=3.0, quiet=True)
    for s in b:
        if abs(s["t"] * 10 - round(s["t"] * 10)) < 1e-6:
            print("   t=%.1f  x=%8.2f  r=%7.2f  ang=%6.1f  v=%.3f" % (s["t"], s["x"], s["r"], s["ang"], s["v"]))
    print("   final: x=%.2f r=%.2f ang=%.1f" % (b[-1]["x"], b[-1]["r"], b[-1]["ang"]))
