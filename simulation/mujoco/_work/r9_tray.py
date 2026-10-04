# -*- coding: utf-8 -*-
"""Is the low-mu failure an artifact of the 5 mm rear overhang? Controlled sweep."""
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


def run(tag, static, parts, bx, mu, sec=12.0):
    pv2.static_geoms, pv2.paddle_parts = static, parts
    xml, ctrl = pv2.build_xml(1620.0, -1, N_FREE * 2 * math.pi / 60.0, bx,
                              pv2.tray_top_z(bx) + pv2.BALL_R)
    xml = xml.replace('kv="0.08"', 'kv="%.6f"' % KV)
    xml = xml.replace('forcerange="-1.5 1.5"', 'forcerange="-%g %g"' % (T_STALL, T_STALL))
    xml = xml.replace('class="ball"><geom friction="1.0 0.02 0.0001"',
                      'class="ball"><geom friction="%g 0.02 0.0001"' % mu)
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
                       "r": round(math.hypot(rx, rz), 2),
                       "ang": round(math.degrees(math.atan2(rz, rx)) % 360.0, 2),
                       "lx": round(lx, 2), "lz": round(lz, 2)})
    res = pv2.analyse(tr)
    e = res.get("exit") or {}
    print("  %-26s launch=%-5s exit_t=%-6s v=%-6s ang=%-7s jam=%-5s rpmMed=%-6.1f "
          "min_r=%-6.1f maxlx=%-8.0f maxz=%-7.0f final=(%.0f,%.0f)"
          % (tag, res["launched"], e.get("t", "--"), e.get("speed_m_s", "--"),
             e.get("angle_deg", "--"), "%.0f%%" % (100 * float((tq > 0.40).mean())),
             float(np.median(rp)), min(s["r"] for s in tr), res["max_lx_mm"],
             res["max_z_mm"], res["final_mm"][0], res["final_mm"][1]), flush=True)
    return {kk: vv for kk, vv in res.items() if kk != "_trace"}


if __name__ == "__main__":
    out = {}
    print("=== mu=0.40, R5 baseline, entry x sweep (tray ends at x=150) ===")
    for bx in (145.0, 135.0, 125.0, 115.0, 105.0):
        out["bx%d" % bx] = run("bx=%.0f no wall" % bx, STAT_R5, PART_R5, bx, 0.40)
    print("--- mu=0.40 with rear wall at x=153 ---")
    for bx in (145.0, 125.0):
        out["wall_bx%d" % bx] = run("bx=%.0f + wall" % bx, STAT_R5 + [wall()], PART_R5, bx, 0.40)
    print("--- mu=1.00 with rear wall (control) ---")
    out["wall_mu1_bx145"] = run("mu=1.00 + wall", STAT_R5 + [wall()], PART_R5, 145.0, 1.00)
    OUT.joinpath("_r9_tray.json").write_text(json.dumps(out, ensure_ascii=False, indent=1),
                                             encoding="utf-8")
    print("  saved", OUT / "_r9_tray.json")
