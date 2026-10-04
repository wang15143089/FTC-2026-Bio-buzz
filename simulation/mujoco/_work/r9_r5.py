# -*- coding: utf-8 -*-
"""R9 full flow on the ACCEPTED R5 layout (two fingers 350/170 + D 6.8 pad), mu band."""
import math, sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import r6_smooth as r6          # registers GEOM["R5"], GEOM["R6"]
import r9_nest as R
import opt_lib as ol
import mujoco, numpy as np

pv2 = ol.pv2
T_STALL, N_FREE = 0.530, 290.0
KV = T_STALL / (N_FREE * 2 * math.pi / 60.0)
OUT = Path("simulation/mujoco/out")
STAT_R5, PART_R5 = ol.GEOM["R5"]


def run(tag, static, parts, bx=145.0, mu_ball=0.40, sec=12.0, rpm=N_FREE):
    pv2.static_geoms = static
    pv2.paddle_parts = parts
    xml, ctrl = pv2.build_xml(1620.0, -1, rpm * 2 * math.pi / 60.0, bx,
                              pv2.tray_top_z(bx) + pv2.BALL_R)
    xml = xml.replace('kv="0.08"', 'kv="%.6f"' % KV)
    xml = xml.replace('forcerange="-1.5 1.5"', 'forcerange="-%g %g"' % (T_STALL, T_STALL))
    xml = xml.replace('class="ball"><geom friction="1.0 0.02 0.0001"',
                      'class="ball"><geom friction="%g 0.02 0.0001"' % mu_ball)
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
            tr.append({"t": round(i * dt, 4), "x": round(p[0], 3), "z": round(p[2], 3),
                       "v": round(float(np.linalg.norm(d.cvel[bid][3:])), 4),
                       "vx": round(float(d.cvel[bid][3]), 4), "vz": round(float(d.cvel[bid][5]), 4),
                       "r": round(math.hypot(rx, rz), 3),
                       "ang": round(math.degrees(math.atan2(rz, rx)) % 360.0, 2),
                       "lx": round(lx, 3), "lz": round(lz, 3)})
    res = pv2.analyse(tr)
    ent = next((s for s in tr if s["ang"] < 232.0 and 45 <= s["r"] <= 80), None)
    ex = next((s for s in tr if s["ang"] <= 143.0 and 45 <= s["r"] <= 80), None)
    res["jam_frac"] = round(float((tq > 0.40).mean()), 3)
    res["rpm_med"] = round(float(np.median(rp)), 1)
    res["carry_s"] = round(ex["t"] - ent["t"], 2) if (ent and ex) else -1.0
    res["enter_t"] = ent["t"] if ent else -1.0
    res["_trace"] = tr
    e = res.get("exit") or {}
    print("  %-16s launched=%-5s exit_t=%-6s exit_v=%-6s ang=%-7s apex=%-7s range=%-6s carry=%-6s jam=%-5s rpmMed=%.1f maxlx=%.0f"
          % (tag, res["launched"], e.get("t", "--"), e.get("speed_m_s", "--"),
             e.get("angle_deg", "--"), e.get("apex_above_exit_mm", "--"), e.get("range_same_height_m", "--"),
             res["carry_s"], "%.0f%%" % (100 * res["jam_frac"]), res["rpm_med"], res["max_lx_mm"]), flush=True)
    return res


if __name__ == "__main__":
    out = {}
    print("=== R9 full flow on R5 (2 fingers 350/170 + D 6.8 pad), tray entry x=145, 12 s ===")
    for mu in (1.00, 0.60, 0.50, 0.45, 0.40, 0.35):
        out["R5 mu%.2f" % mu] = run("R5 mu=%.2f" % mu, STAT_R5, PART_R5, mu_ball=mu)
    print("--- R5 with raised nest 20 mm @ x=28 ---")
    for mu in (0.45, 0.40):
        out["R5+nest20 mu%.2f" % mu] = run(
            "R5+nest20 mu=%.2f" % mu, R.nest("flat", step=20.0, xc=28.0), PART_R5, mu_ball=mu)
    OUT.joinpath("_r9_r5.json").write_text(
        json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "_trace"} for k, v in out.items()},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    print("  saved", OUT / "_r9_r5.json")
