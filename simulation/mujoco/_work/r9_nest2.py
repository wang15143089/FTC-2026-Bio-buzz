# -*- coding: utf-8 -*-
"""R9b: raise/extend the rest pocket and measure the settled ball radius vs jam."""
import math, sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import r9_nest as R
import opt_lib as ol
import mujoco, numpy as np

pv2 = ol.pv2
T_STALL, N_FREE = 0.530, 290.0
KV = T_STALL / (N_FREE * 2 * math.pi / 60.0)
OUT = Path("simulation/mujoco/out")


def run(tag, static, bx=20.9, sec=8.0, mu_ball=None, rpm=N_FREE):
    pv2.static_geoms = static
    pv2.paddle_parts = ol.ORIG_PARTS
    xml, ctrl = pv2.build_xml(1620.0, -1, rpm * 2 * math.pi / 60.0, bx,
                              pv2.tray_top_z(bx) + pv2.BALL_R)
    xml = xml.replace('kv="0.08"', 'kv="%.6f"' % KV)
    xml = xml.replace('forcerange="-1.5 1.5"', 'forcerange="-%g %g"' % (T_STALL, T_STALL))
    if mu_ball is not None:
        xml = xml.replace('class="ball"><geom friction="1.0 0.02 0.0001"',
                          'class="ball"><geom friction="%g 0.02 0.0001"' % mu_ball)
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
    pid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "paddle_joint")
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    aid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "paddle_vel")
    dt = m.opt.timestep; n = int(sec / dt); k = max(1, int(0.002 / dt))
    tq = np.zeros(n); rp = np.zeros(n); tr = []
    settled_r = None
    for i in range(n):
        mujoco.mj_step(m, d)
        tq[i] = abs(float(d.actuator_force[aid]))
        rp[i] = math.degrees(d.qvel[pid]) / 6.0
        if i % k == 0:
            p = d.xpos[bid] * 1000.0
            rx, rz = p[0] - pv2.PADDLE_CX, p[2] - pv2.PADDLE_CZ
            lx, lz = pv2.to_shooter(p[0], p[2])
            v = float(np.linalg.norm(d.cvel[bid][3:]))
            s = {"t": round(i * dt, 4), "x": round(p[0], 3), "z": round(p[2], 3),
                 "v": round(v, 4), "vx": round(float(d.cvel[bid][3]), 4),
                 "vz": round(float(d.cvel[bid][5]), 4),
                 "r": round(math.hypot(rx, rz), 3),
                 "ang": round(math.degrees(math.atan2(rz, rx)) % 360.0, 2),
                 "lx": round(lx, 3), "lz": round(lz, 3)}
            tr.append(s)
            if settled_r is None and v > 0.05 and s["t"] > 0.05:
                settled_r = tr[-2]["r"] if len(tr) > 1 else s["r"]
    res = pv2.analyse(tr)
    ent = next((s for s in tr if s["ang"] < 232.0 and 45 <= s["r"] <= 80), None)
    ex = next((s for s in tr if s["ang"] <= 143.0 and 45 <= s["r"] <= 80), None)
    res["jam_frac"] = round(float((tq > 0.40).mean()), 3)
    res["rpm_med"] = round(float(np.median(rp)), 1)
    res["carry_s"] = round(ex["t"] - ent["t"], 2) if (ent and ex) else -1.0
    res["settled_r"] = settled_r if settled_r is not None else tr[-1]["r"]
    res["_trace"] = tr
    print("  %-26s settled_r=%6.2f  launched=%-5s exit_t=%-6s carry=%-6s jam=%-5s rpmMed=%.1f"
          % (tag, res["settled_r"], res["launched"], (res.get("exit") or {}).get("t", "--"),
             res["carry_s"], "%.0f%%" % (100 * res["jam_frac"]), res["rpm_med"]), flush=True)
    return res


flat = R.nest
out = {}
print("=== R9b rest-pocket height/offset sweep (mu=1.0, pocket start, 8 s) ===")
for st in (6.8, 13.0, 16.0, 20.0, 24.0, 28.0):
    out["step%g" % st] = run("pad step%g" % st, flat("flat", step=st))
for st, xc in ((13.0, 28.0), (16.0, 28.0), (20.0, 28.0)):
    out["step%g x%g" % (st, xc)] = run("pad step%g x=%g" % (st, xc), flat("flat", step=st, xc=xc))
for st in (13.0, 20.0):
    out["step%g wide60" % st] = run("pad step%g w=60" % st, flat("flat", step=st, w=60.0))
OUT.joinpath("_r9_nest2.json").write_text(
    json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "_trace"} for k, v in out.items()},
               ensure_ascii=False, indent=1), encoding="utf-8")
print("  saved", OUT / "_r9_nest2.json")
