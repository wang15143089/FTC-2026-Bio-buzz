# -*- coding: utf-8 -*-
"""R8: put the ball at different entry x and see where the jam comes from."""
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


def run(bx, angs=(10.0, 190.0), sec=10.0, rpm=N_FREE, static=None, quiet=False):
    pv2.static_geoms = static or BASE
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
    pbody = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "paddle")
    bg = {g for g in range(m.ngeom) if m.geom_bodyid[g] == bid}
    dt = m.opt.timestep
    tr = []
    first = None
    t_first_paddle = None
    for i in range(int(sec / dt)):
        mujoco.mj_step(m, d)
        t = i * dt
        hit = False
        if d.ncon:
            for c in range(d.ncon):
                con = d.contact[c]
                if (con.geom1 in bg) != (con.geom2 in bg):
                    o = con.geom2 if con.geom1 in bg else con.geom1
                    if m.geom_bodyid[o] == pbody:
                        hit = True
                        if first is None:
                            p = d.xpos[bid] * 1000.0
                            first = (round(t, 3), round(math.hypot(p[0] - pv2.PADDLE_CX,
                                                                   p[2] - pv2.PADDLE_CZ), 2))
                        break
        if i % int(0.002 / dt) == 0:
            p = d.xpos[bid] * 1000.0
            rx, rz = p[0] - pv2.PADDLE_CX, p[2] - pv2.PADDLE_CZ
            lx, lz = pv2.to_shooter(p[0], p[2])
            tr.append({"t": round(t, 4), "x": round(p[0], 3), "z": round(p[2], 3),
                       "v": round(float(np.linalg.norm(d.cvel[bid][3:])), 4),
                       "vx": round(float(d.cvel[bid][3]), 4), "vz": round(float(d.cvel[bid][5]), 4),
                       "r": round(math.hypot(rx, rz), 3),
                       "ang": round(math.degrees(math.atan2(rz, rx)) % 360.0, 2),
                       "lx": round(lx, 3), "lz": round(lz, 3),
                       "pv": round(math.degrees(d.qvel[pid]) / 6.0, 2),
                       "pa": round(abs(float(d.actuator_force[aid])), 4)})
    res = pv2.analyse(tr)
    tv = np.array([s["pa"] for s in tr]); pvv = np.array([s["pv"] for s in tr])
    res["first_contact"] = first
    res["jam_frac"] = round(float((tv > 0.40).mean()), 3)
    res["rpm_med"] = round(float(np.median(pvv)), 1)
    res["start"] = (round(bx, 1), round(pv2.tray_top_z(bx) + pv2.BALL_R, 1))
    res["_trace"] = tr
    return res


if __name__ == "__main__":
    print("=== entry position test: blades local (10,190), 25-4 motor 290 rpm, 10 s ===")
    print("  x0    launched  exitT  exitV  firstT  rho0   jam%  rpmMed  minAng  peakV")
    for bx in (145.0, 130.0, 110.0, 95.0, 80.0, 70.0, 61.0, 40.0, 20.9):
        r = run(bx)
        fc = r["first_contact"] or (None, None)
        ex = r.get("exit", {})
        print("  %5.1f  %-5s   %6s %6s  %6s %6s  %4.0f%%  %6.1f  %6.1f  %.2f"
              % (bx, r["launched"], ex.get("t", "--"), ex.get("speed_m_s", "--"),
                 fc[0], fc[1], 100 * r["jam_frac"], r["rpm_med"], r["min_angle_deg"],
                 r["peak_speed_m_s"]))
