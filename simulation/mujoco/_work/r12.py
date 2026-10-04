# -*- coding: utf-8 -*-
"""R12: does the launcher actually work when the ball IS on the carry circle?

R11 proved the ball never gets there from the tray.  This run skips the feed
problem: the ball starts in the nest at 270 deg (r = R_CARRY = 58.4) and we test
both paddle directions, plus the NECTAR ball in its own shell radius.
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


def run(tag, geom, sign=-1.0, mu=0.40, bx=None, bz=None, sec=12.0,
        ball_r=None, ball_m=None, r_in=None, detail=0.25, quiet=False):
    if r_in is not None:
        pv2.R_IN = r_in
        pv2.R_OUT = r_in + pv2.SHELL_WALL
        R10.R_MID = r_in + 3.5
    if ball_r is not None:
        pv2.BALL_R = ball_r
    if ball_m is not None:
        pv2.BALL_MASS = ball_m
    if bx is None:
        bx = pv2.PADDLE_CX
    if bz is None:
        bz = pv2.PADDLE_CZ - pv2.R_CARRY
    st, pt = geom
    pv2.static_geoms, pv2.paddle_parts = st, pt
    xml, ctrl = pv2.build_xml(1620.0, -1, sign * OMEGA, bx, bz)
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
                       "v": round(float(np.linalg.norm(d.cvel[bid][3:])), 4), "vx": round(float(d.cvel[bid][3]), 4), "vz": round(float(d.cvel[bid][5]), 4),
                       "r": round(math.hypot(rx, rz), 2),
                       "ang": round(math.degrees(math.atan2(rz, rx)) % 360.0, 2),
                       "lx": round(lx, 2), "lz": round(lz, 2)})
        if i % kd == 0 and not quiet:
            p = d.xpos[bid] * 1000.0
            rx, rz = p[0] - pv2.PADDLE_CX, p[2] - pv2.PADDLE_CZ
            cnt = sorted({mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM,
                           int(cc.geom2 if cc.geom1 in bgeom else cc.geom1))
                          for cc in d.contact[:d.ncon] if (cc.geom1 in bgeom or cc.geom2 in bgeom)})
            print("    t=%5.2f  x=%7.2f z=%7.2f  r=%6.2f ang=%6.1f  c=%s"
                  % (i * dt, p[0], p[2], math.hypot(rx, rz),
                     math.degrees(math.atan2(rz, rx)) % 360.0,
                     ",".join(cnt) or "-"), flush=True)
    res = pv2.analyse(tr)
    e = res.get("exit") or {}
    if not quiet:
        print("  %-14s sign=%+.0f R_in=%-6.2f launch=%-5s exit_t=%-6s v=%-6s ang=%-7s jam=%-5s "
              "rpmMed=%-6.1f min_r=%-5.1f minang=%-6.1f final=(%.0f,%.0f)"
              % (tag, sign, pv2.R_IN, res["launched"], e.get("t", "--"), e.get("speed_m_s", "--"),
                 e.get("angle_deg", "--"), "%.0f%%" % (100 * float((tq > 0.40).mean())),
                 float(np.median(rp)), min(s["r"] for s in tr), res["min_angle_deg"],
                 res["final_mm"][0], res["final_mm"][1]), flush=True)
    out = {kk: vv for kk, vv in res.items() if kk != "_trace"}
    out["_trace"] = tr
    out["sign"] = sign
    return out


def main():
    res = {}
    g = R10.make_geom(56.0, 292.0)
    print("=== R12 pre-seated ball in the nest (r=58.4, ang=270), POLLEN R=35.56 ===")
    print("  -- paddle CCW (sign=+1, the direction requested so far) --")
    res["pollen_cw_like"] = run("POLLEN +1", g, sign=+1.0, sec=3.0)
    print("  -- paddle CW (sign=-1) --")
    res["pollen_ccw_like"] = run("POLLEN -1", g, sign=-1.0, sec=3.0)
    print()
    print("=== R12 same test with the NECTAR ball (R=45.97, shell inner r=104.37) ===")
    gN = R10.make_geom(56.0, 292.0)
    print("  -- paddle CW (sign=-1) --")
    res["nectar_ccw_like"] = run("NECTAR -1", gN, sign=-1.0, sec=3.0,
                                 ball_r=45.974, r_in=104.37)
    print("  -- paddle CCW (sign=+1) --")
    res["nectar_cw_like"] = run("NECTAR +1", gN, sign=+1.0, sec=3.0,
                                ball_r=45.974, r_in=104.37)
    OUT.joinpath("_r12_seated.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print("saved", OUT / "_r12_seated.json")


if __name__ == "__main__":
    main()
