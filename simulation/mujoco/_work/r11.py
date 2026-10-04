# -*- coding: utf-8 -*-
"""R11: trace the ball on the R10 cradle and test paddle direction.

Question: with the shell arc extended past the bottom of the carry circle
(a_lip = 292 deg) and the tray cut back to x = 56, does the ball ever reach the
carry radius R_CARRY = 58.4 mm, or does it jam on the tray?

The ball rests on the 5 deg tray near ang ~330 deg.  A CCW rotor sweeps that
angle and pushes the ball up-slope (towards larger ang) = backwards.  So the
sign of the paddle rotation is tested explicitly.
"""
import math, sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import r6_smooth as r6
import opt_lib as ol
import r10_cradle as R10
import mujoco, numpy as np

pv2 = ol.pv2
T_STALL, N_FREE = 0.530, 290.0
KV = T_STALL / (N_FREE * 2 * math.pi / 60.0)
OMEGA = N_FREE * 2 * math.pi / 60.0
OUT = Path("simulation/mujoco/out")


def run(tag, geom, sign=1.0, mu=0.40, bx=145.0, sec=12.0,
        ball_r=None, ball_m=None, detail=0.25, quiet=False):
    if ball_r is not None:
        pv2.BALL_R = ball_r
    if ball_m is not None:
        pv2.BALL_MASS = ball_m
    st, pt = geom
    pv2.static_geoms, pv2.paddle_parts = st, pt
    xml, ctrl = pv2.build_xml(1620.0, -1, sign * OMEGA, bx,
                              pv2.tray_top_z(bx) + pv2.BALL_R)
    xml = xml.replace('kv="0.08"', 'kv="%.6f"' % KV)
    xml = xml.replace('forcerange="-1.5 1.5"', 'forcerange="-%g %g"' % (T_STALL, T_STALL))
    xml = xml.replace('class="ball"><geom friction="1.0 0.02 0.0001"',
                      'class="ball"><geom friction="%g 0.02 0.0001"' % mu)
    m = mujoco.MjModel.from_xml_string(xml)
    d = mujoco.MjData(m)
    d.ctrl[:] = ctrl
    mujoco.mj_forward(m, d)
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    bgeom = {g for g in range(m.ngeom) if m.geom_bodyid[g] == bid}
    pid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "paddle_joint")
    aid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "paddle_vel")
    dt = m.opt.timestep
    n = int(sec / dt)
    k = max(1, int(round(0.002 / dt)))
    kd = max(1, int(round(detail / dt)))
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
        if i % kd == 0 and not quiet:
            p = d.xpos[bid] * 1000.0
            rx, rz = p[0] - pv2.PADDLE_CX, p[2] - pv2.PADDLE_CZ
            cnt = sorted({mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM,
                           int(cc.geom2 if cc.geom1 in bgeom else cc.geom1))
                          for cc in d.contact[:d.ncon] if (cc.geom1 in bgeom or cc.geom2 in bgeom)})
            print("    t=%5.2f  x=%7.2f z=%7.2f  r=%6.2f ang=%6.1f  pad=%6.1f  c=%s"
                  % (i * dt, p[0], p[2], math.hypot(rx, rz),
                     math.degrees(math.atan2(rz, rx)) % 360.0,
                     math.degrees(d.qpos[pid]) % 360.0,
                     ",".join(cnt) or "-"), flush=True)
    res = pv2.analyse(tr)
    e = res.get("exit") or {}
    if not quiet:
        print("  %-16s sign=%+.0f mu=%.2f launch=%-5s exit_t=%-6s v=%-6s jam=%-5s "
              "rpmMed=%-6.1f min_r=%-5.1f minang=%-6.1f final=(%.0f,%.0f)"
              % (tag, sign, mu, res["launched"], e.get("t", "--"), e.get("speed_m_s", "--"),
                 "%.0f%%" % (100 * float((tq > 0.40).mean())), float(np.median(rp)),
                 min(s["r"] for s in tr), res["min_angle_deg"],
                 res["final_mm"][0], res["final_mm"][1]), flush=True)
    out = {kk: vv for kk, vv in res.items() if kk != "_trace"}
    out["_trace"] = tr
    out["sign"] = sign
    out["mu"] = mu
    return out


def main():
    res = {}
    print("=== R11 direction test, R10 cradle (cut=56, lip=292), POLLEN, mu=0.40 ===")
    g = R10.make_geom(56.0, 292.0)
    for sign in (+1.0, -1.0):
        print("  -- paddle sign=%+.0f --" % sign)
        res["R10_%+.0f" % sign] = run("R10", g, sign=sign, sec=12.0)
    print()
    print("=== R5 reference, same test ===")
    g5 = (lambda: r6.DPB(), r6.th2((350.0, 170.0)))
    for sign in (+1.0, -1.0):
        print("  -- paddle sign=%+.0f --" % sign)
        res["R5_%+.0f" % sign] = run("R5", g5, sign=sign, sec=12.0)
    OUT.joinpath("_r11_dir.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print("saved", OUT / "_r11_dir.json")


if __name__ == "__main__":
    main()
