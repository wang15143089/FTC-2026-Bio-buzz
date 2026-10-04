# -*- coding: utf-8 -*-
"""R9 clean threshold: tray extended to x=185 + stop wall at 188 (clear of the ball at t=0)."""
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


def long_tray(x1=185.0):
    nmx, nmz = pv2.normal(-pv2.TILT)
    x0 = pv2.TRAY_X0
    xm = 0.5 * (x0 + x1)
    zt = pv2.tray_top_z(xm)
    L = (x1 - x0) / math.cos(math.radians(pv2.TILT))
    return ("tray", "shell", "box", (L, pv2.FEEDER_W, pv2.TRAY_T),
            (xm - nmx * pv2.TRAY_T / 2, 0.0, zt - nmz * pv2.TRAY_T / 2), pv2.quat_y(-pv2.TILT))


def wall(x, h=70.0):
    return ("rear_wall", "shell", "box", (6.0, pv2.FEEDER_W, h),
            (x, 0.0, pv2.tray_top_z(x) + h / 2.0), pv2.quat_y(0.0))


def stat():
    return [g for g in STAT_R5() if g[0] != "tray"] + [long_tray(185.0), wall(188.0)]


def run(tag, bx, mu, sec=20.0):
    pv2.static_geoms, pv2.paddle_parts = stat, PART_R5
    xml, ctrl = pv2.build_xml(1620.0, -1, N_FREE * 2 * math.pi / 60.0, bx,
                              pv2.tray_top_z(bx) + pv2.BALL_R)
    xml = xml.replace('kv="0.08"', 'kv="%.6f"' % KV)
    xml = xml.replace('forcerange="-1.5 1.5"', 'forcerange="-%g %g"' % (T_STALL, T_STALL))
    xml = xml.replace('class="ball"><geom friction="1.0 0.02 0.0001"',
                      'class="ball"><geom friction="%g 0.02 0.0001"' % mu)
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    bgeom = {g for g in range(m.ngeom) if m.geom_bodyid[g] == bid}
    touch0 = sorted({mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, int(c.geom2 if c.geom1 in bgeom else c.geom1))
                     for c in d.contact[:d.ncon] if (c.geom1 in bgeom or c.geom2 in bgeom)})
    pid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "paddle_joint")
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
    res = pv2.analyse(tr); e = res.get("exit") or {}
    print("  %-14s t0_contacts=%-12s launch=%-5s exit_t=%-6s v=%-6s ang=%-7s jam=%-5s rpmMed=%-6.1f "
          "min_r=%-6.1f run_r=%-7.1f final=(%.0f,%.0f)"
          % (tag, ",".join(touch0) or "-", res["launched"], e.get("t", "--"), e.get("speed_m_s", "--"),
             e.get("angle_deg", "--"), "%.0f%%" % (100 * float((tq > 0.40).mean())), float(np.median(rp)),
             min(s["r"] for s in tr), max(s["r"] for s in tr), res["final_mm"][0], res["final_mm"][1]),
          flush=True)
    return {kk: vv for kk, vv in res.items() if kk != "_trace"}


if __name__ == "__main__":
    out = {}
    print("=== R5, tray 185 + stop wall 188, entry x=145, 20 s ===")
    for mu in (0.40, 0.50, 0.60, 0.70, 0.80, 1.00):
        out["mu%.2f" % mu] = run("mu=%.2f" % mu, 145.0, mu)
    OUT.joinpath("_r9_clean.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("  saved", OUT / "_r9_clean.json")
