# -*- coding: utf-8 -*-
"""R9 friction threshold: how high must ball friction be for R5 pickup to work?
Rear wall prevents the ball from being lost off the tray end, so every case gets a fair 20 s."""
import math, sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import r6_smooth as r6
import opt_lib as ol
import mujoco, numpy as np

pv2 = ol.pv2
T_STALL, N_FREE = 0.530, 290.0
KV = T_STALL / (N_FREE * 2 * math.pi / 60.0)
STAT_R5, PART_R5 = ol.GEOM["R5"]
OUT = Path("simulation/mujoco/out")


def wall(x=153.0, h=60.0):
    z = pv2.tray_top_z(x) + h / 2.0
    return ("rear_wall", "shell", "box", (6.0, pv2.FEEDER_W, h), (x, 0.0, z), pv2.quat_y(0.0))


def run(tag, bx, mu, sec=20.0, fw_prio=False):
    pv2.static_geoms, pv2.paddle_parts = (lambda: list(STAT_R5()) + [wall()]), PART_R5
    xml, ctrl = pv2.build_xml(1620.0, -1, N_FREE * 2 * math.pi / 60.0, bx,
                              pv2.tray_top_z(bx) + pv2.BALL_R)
    xml = xml.replace('kv="0.08"', 'kv="%.6f"' % KV)
    xml = xml.replace('forcerange="-1.5 1.5"', 'forcerange="-%g %g"' % (T_STALL, T_STALL))
    xml = xml.replace('class="ball"><geom friction="1.0 0.02 0.0001"',
                      'class="ball"><geom friction="%g 0.02 0.0001"' % mu)
    if fw_prio:
        xml = xml.replace('<default class="flywheel"><geom friction="1.6 0.02 0.0001"',
                          '<default class="flywheel"><geom friction="1.6 0.02 0.0001" priority="2"')
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
    pid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "paddle_joint")
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    aid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "paddle_vel")
    dt = m.opt.timestep; n = int(sec / dt); k = max(1, int(0.002 / dt))
    tq = np.zeros(n); rp = np.zeros(n); tr = []
    for i in range(n):
        mujoco.mj_step(m, d)
        tq[i] = abs(float(d.actuator_force[aid]))
        rp[i] = math.degrees(d.qvel[pid]) / 6.0
        if i % k == 0:
            p = d.xpos[bid] * 1000.0
            rx, rz = p[0] - pv2.PADDLE_CX, p[2] - pv2.PADDLE_CZ
            lx, lz = pv2.to_shooter(p[0], p[2])
            tr.append({"t": round(i * dt, 4), "x": round(p[0], 2), "z": round(p[2], 2),
                       "v": round(float(np.linalg.norm(d.cvel[bid][3:])), 4),
                       "vx": round(float(d.cvel[bid][3]), 4), "vz": round(float(d.cvel[bid][5]), 4),
                       "r": round(math.hypot(rx, rz), 2),
                       "ang": round(math.degrees(math.atan2(rz, rx)) % 360.0, 2),
                       "lx": round(lx, 2), "lz": round(lz, 2)})
    res = pv2.analyse(tr)
    e = res.get("exit") or {}
    print("  %-22s launch=%-5s exit_t=%-6s v=%-6s ang=%-7s jam=%-5s rpmMed=%-6.1f min_r=%-6.1f final=(%.0f,%.0f)"
          % (tag, res["launched"], e.get("t", "--"), e.get("speed_m_s", "--"), e.get("angle_deg", "--"),
             "%.0f%%" % (100 * float((tq > 0.40).mean())), float(np.median(rp)),
             min(s["r"] for s in tr), res["final_mm"][0], res["final_mm"][1]), flush=True)
    return {kk: vv for kk, vv in res.items() if kk != "_trace"}


if __name__ == "__main__":
    out = {}
    print("=== R5 + rear wall, entry x=145, 20 s: ball friction threshold ===")
    for mu in (0.40, 0.60, 0.70, 0.80, 0.90, 1.00):
        out["mu%.2f" % mu] = run("mu=%.2f" % mu, 145.0, mu)
    print("--- mu=0.40 with correct per-pair model (flywheel keeps its own friction, priority 2) ---")
    out["mu0.40_fwgrip"] = run("mu=0.40 fw-grip", 145.0, 0.40, fw_prio=True)
    OUT.joinpath("_r9_mu2.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("  saved", OUT / "_r9_mu2.json")
