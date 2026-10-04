# -*- coding: utf-8 -*-
"""Drive the paddle with a real DC-motor model of the goBILDA 25-4 Super Speed
(7.4 V: stall 0.530 N.m, no-load 290 rpm) instead of the arbitrary kv=0.08.

T(n) = T_stall * (1 - n / n_free)  ==  velocity actuator with
kv = T_stall / w_free, ctrl = w_free, forcerange = +-T_stall.
"""
import json, math, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import r6_smooth as r6
import opt_lib as ol
import mujoco, numpy as np

pv2 = ol.pv2
OUT = Path("simulation/mujoco/out")
T_STALL, N_FREE = 0.530, 290.0
KV = T_STALL / (N_FREE * 2 * math.pi / 60.0)
print("25-4 Super Speed model: T_stall=%.3f Nm  n_free=%.0f rpm  kv=%.6f  w_free=%.2f rad/s"
      % (T_STALL, N_FREE, KV, N_FREE * 2 * math.pi / 60.0))


def run_motor(name, bx=145.0, sec=12.0, fr=T_STALL, rpm=N_FREE, trace=False):
    ol.apply_geom(name)
    xml, ctrl = pv2.build_xml(1620.0, -1, rpm * 2 * math.pi / 60.0, bx,
                              pv2.tray_top_z(bx) + pv2.BALL_R)
    xml = xml.replace('kv="0.08"', 'kv="%.6f"' % KV)
    xml = xml.replace('forcerange="-1.5 1.5"', 'forcerange="-%g %g"' % (fr, fr))
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
    pid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "paddle_joint")
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    aid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "paddle_vel")
    dt = m.opt.timestep
    tr = []
    for i in range(int(sec / dt)):
        mujoco.mj_step(m, d)
        if i % max(1, int(0.002 / dt)) == 0:
            p = d.xpos[bid] * 1000.0
            lx, lz = pv2.to_shooter(p[0], p[2])
            tr.append({"t": round(i * dt, 4), "x": round(p[0], 3), "z": round(p[2], 3),
                       "v": round(float((d.cvel[bid][3:] ** 2).sum() ** 0.5), 4),
                       "vx": round(float(d.cvel[bid][3]), 4), "vz": round(float(d.cvel[bid][5]), 4),
                       "r": round(math.hypot(p[0] - pv2.PADDLE_CX, p[2] - pv2.PADDLE_CZ), 3),
                       "ang": round(math.degrees(math.atan2(p[2] - pv2.PADDLE_CZ,
                                                            p[0] - pv2.PADDLE_CX)) % 360.0, 2),
                       "lx": round(lx, 3), "lz": round(lz, 3),
                       "pv": round(float(math.degrees(d.qvel[pid])), 2),
                       "pa": round(abs(float(d.actuator_force[aid])), 4)})
    res = pv2.analyse(tr)
    win = [s for s in tr if 143.0 <= s["ang"] <= 232.0]
    res["_trace"] = tr
    if win:
        res["carry_s"] = round(win[-1]["t"] - win[0]["t"], 2)
        res["carry_paddle_rpm"] = round(float(np.mean([s["pv"] for s in win])) / 6.0, 2)
        res["carry_torque_Nm"] = round(float(np.mean([s["pa"] for s in win])), 3)
    else:
        res["carry_s"] = None
    return res


def brief(name, bx, sec=12.0):
    r = run_motor(name, bx=bx, sec=sec)
    ex = r.get("exit", {})
    print("  %-3s bx=%-6g launched=%-5s t_peak=%.2fs  peak=%.2f m/s  v_exit=%.2f m/s  "
          "carry=%s s @ %s rpm, %s Nm  min_ang=%.1f  max_z=%.0f"
          % (name, bx, r["launched"], r["peak_speed_t"], r["peak_speed_m_s"],
             ex.get("speed_m_s", 0.0), r.get("carry_s"), r.get("carry_paddle_rpm"),
             r.get("carry_torque_Nm"), r["min_angle_deg"], r["max_z_mm"]))
    return r


if __name__ == "__main__":
    print("=== 25-4 Super Speed (0.530 Nm / 290 rpm) driving the paddle ===")
    R = {}
    for nm in ("R5", "R6", "R6c"):
        for bx in (145.0, 138.0):
            R["%s_%g" % (nm, bx)] = brief(nm, bx)
    OUT.joinpath("_r6_motor.json").write_text(
        json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "_trace"} for k, v in R.items()},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    print()
    print("R5 @bx145 paddle speed / ball angle (0.2 s):")
    for s in R["R5_145"]["_trace"]:
        if abs(s["t"] * 5 - round(s["t"] * 5)) < 1e-6 and s["t"] <= 8.0:
            print("   t=%5.2f  rpm=%7.1f  T=%.3f  ball x=%7.2f z=%7.2f ang=%6.1f v=%.3f"
                  % (s["t"], s["pv"] / 6.0, s["pa"], s["x"], s["z"], s["ang"], s["v"]))
