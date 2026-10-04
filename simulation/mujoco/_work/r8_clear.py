# -*- coding: utf-8 -*-
"""R8: hypothesis - the bore R_IN = R_CARRY + R_BALL is a ZERO-clearance fit.
Test by opening the bore by c mm."""
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
R_IN0, R_OUT0 = 93.96, 100.96


def blades(angs, W=pv2.PADDLE_W):
    def f():
        parts = [("hub", (0., 0., 0.), (18., 17., 18.), 0., "cylY")]
        for i, a in enumerate(angs, 1):
            parts += [("arm_%d" % i, (30., 0, 0), (16., 9., 5.), a, "box"),
                      ("blade_%d" % i, (52., 0, 0), (6., W / 2., 15.), a, "box"),
                      ("flex_%d" % i, (58., 0, 0), (2., W / 2., 17.), a, "box")]
        return parts
    return f


def run(bx, clear_mm, angs=(10.0, 190.0), sec=8.0, rpm=N_FREE, out=True):
    pv2.R_IN = R_IN0 + clear_mm
    pv2.R_OUT = R_OUT0
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
    dt = m.opt.timestep
    tr = []
    rs = []
    for i in range(int(sec / dt)):
        mujoco.mj_step(m, d)
        p = d.xpos[bid] * 1000.0
        rs.append(math.hypot(p[0] - pv2.PADDLE_CX, p[2] - pv2.PADDLE_CZ))
        if i % int(0.002 / dt) == 0:
            rx, rz = p[0] - pv2.PADDLE_CX, p[2] - pv2.PADDLE_CZ
            lx, lz = pv2.to_shooter(p[0], p[2])
            tr.append({"t": round(i * dt, 4), "x": round(p[0], 3), "z": round(p[2], 3),
                       "v": round(float(np.linalg.norm(d.cvel[bid][3:])), 4),
                       "vx": round(float(d.cvel[bid][3]), 4), "vz": round(float(d.cvel[bid][5]), 4),
                       "r": round(math.hypot(rx, rz), 3),
                       "ang": round(math.degrees(math.atan2(rz, rx)) % 360.0, 2),
                       "lx": round(lx, 3), "lz": round(lz, 3),
                       "pv": round(math.degrees(d.qvel[pid]) / 6.0, 2),
                       "pa": round(abs(float(d.actuator_force[aid])), 4)})
    res = pv2.analyse(tr)
    tv = np.array([s["pa"] for s in tr]); pvv = np.array([s["pv"] for s in tr])
    res["jam_frac"] = round(float((tv > 0.40).mean()), 3)
    res["rpm_med"] = round(float(np.median(pvv)), 1)
    res["exit_t"] = res.get("exit", {}).get("t")
    res["exit_v"] = res.get("exit", {}).get("speed_m_s")
    res["r_min"] = round(min(rs), 2)
    res["r_carry"] = round(float(np.median([s["r"] for s in tr if 143 <= s["ang"] <= 232])), 2)
    return res


if __name__ == "__main__":
    print("=== bore clearance sweep (blades local 10/190, 25-4 @290 rpm, 8 s) ===")
    print("  start   clr   launched exitT  exitV  jam%   rpmMed  r_carry  r_min")
    for bx, tag in ((145.0, "full"), (20.9, "pocket")):
        for c in (0.0, 0.5, 1.0, 1.5, 2.0, 3.0):
            r = run(bx, c)
            print("  %-6s %4.1f  %-5s   %6s %6s  %4.0f%%  %6.1f  %6.2f  %6.2f"
                  % (tag, c, r["launched"], r["exit_t"], r["exit_v"],
                     100 * r["jam_frac"], r["rpm_med"], r["r_carry"], r["r_min"]))
        print()
