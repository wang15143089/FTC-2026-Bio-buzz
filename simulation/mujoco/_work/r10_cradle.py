# -*- coding: utf-8 -*-
"""R10: ball parks ON the carry circle (DEC-0028 option a').

Change vs R5:
  * shell inner arc extended from A_LIP=225 deg down past the bottom of the
    carry circle (270 deg) to a_lip (288..300 deg), so the shell wall itself
    is the rest support and the ball centre sits at R_CARRY.
  * tray cut back to x = cut_x (about the tangency point) so it no longer
    lifts the ball off the wall.
  * R5 rest pad removed.
Paddle: R5 two-finger rotor (10/190 deg).
"""
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
OUT = Path("simulation/mujoco/out")
R_MID = pv2.R_IN + 3.5


def stat(cut_x=56.0, a_lip=292.0, tray_x1=185.0, wall_x=None, wall_h=70.0):
    base = [g for g in ol.ORIG_STATIC() if not g[0].startswith(("shell_", "tray", "strut"))]
    out = list(base)
    out += r6.arc_pad(pv2.A_EXIT, a_lip, thick=7.0, n=24, r_in=pv2.R_IN, tag="r10")
    for tag, ang in (("exit", pv2.A_EXIT), ("lip", a_lip)):
        cx, cz = pv2.polar(R_MID, ang)
        out.append(("shell_%s_face" % tag, "shell", "box", (7.0, pv2.FEEDER_W, 3.0),
                    (cx, 0.0, cz), pv2.quat_y(-ang)))
    nmx, nmz = pv2.normal(-pv2.TILT)
    xm = 0.5 * (cut_x + tray_x1)
    zt = pv2.tray_top_z(xm)
    L = (tray_x1 - cut_x) / math.cos(math.radians(pv2.TILT))
    out.append(("tray", "shell", "box", (L, pv2.FEEDER_W, pv2.TRAY_T),
                (xm - nmx * pv2.TRAY_T / 2, 0.0, zt - nmz * pv2.TRAY_T / 2), pv2.quat_y(-pv2.TILT)))
    if wall_x is None:
        wall_x = tray_x1 + 3.0
    out.append(("rear_wall", "shell", "box", (6.0, pv2.FEEDER_W, wall_h),
                (wall_x, 0.0, pv2.tray_top_z(wall_x) + wall_h / 2.0), pv2.quat_y(0.0)))
    return out


def make_geom(cut_x=56.0, a_lip=292.0, fingers=2):
    if fingers == 2:
        parts = r6.th2((350.0, 170.0))
    else:
        parts = ol.ORIG_PARTS()
    return (lambda: stat(cut_x, a_lip), parts)


def run(tag, geom, mu=0.40, bx=145.0, sec=12.0, ball_r=None, ball_m=None, quiet=False):
    if ball_r is not None:
        pv2.BALL_R = ball_r
    if ball_m is not None:
        pv2.BALL_MASS = ball_m
    st, pt = geom
    pv2.static_geoms, pv2.paddle_parts = st, pt
    xml, ctrl = pv2.build_xml(1620.0, -1, N_FREE * 2 * math.pi / 60.0, bx,
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
    touch0 = sorted({mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM,
                    int(c.geom2 if c.geom1 in bgeom else c.geom1))
                     for c in d.contact[:d.ncon] if (c.geom1 in bgeom or c.geom2 in bgeom)})
    pid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "paddle_joint")
    aid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "paddle_vel")
    dt = m.opt.timestep
    n = int(sec / dt)
    k = max(1, int(round(0.002 / dt)))
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
    if not quiet:
        print("  %-26s mu=%.2f t0=%-10s launch=%-5s exit_t=%-6s v=%-6s ang=%-7s jam=%-5s "
              "rpmMed=%-6.1f min_r=%-5.1f minang=%-6.1f final=(%.0f,%.0f)"
              % (tag, mu, ",".join(touch0) or "-", res["launched"], e.get("t", "--"),
                 e.get("speed_m_s", "--"), e.get("angle_deg", "--"),
                 "%.0f%%" % (100 * float((tq > 0.40).mean())), float(np.median(rp)),
                 min(s["r"] for s in tr), res["min_angle_deg"],
                 res["final_mm"][0], res["final_mm"][1]), flush=True)
    out = {kk: vv for kk, vv in res.items() if kk != "_trace"}
    out["_trace"] = tr
    out["jam_frac"] = round(float((tq > 0.40).mean()), 3)
    out["rpm_median"] = round(float(np.median(rp)), 1)
    out["mu"] = mu
    return out


def sweep():
    res = {}
    print("=== R10 shape sweep, POLLEN, mu=0.40, 12 s ===")
    for cut_x in (52.0, 56.0, 62.0, 70.0):
        for a_lip in (288.0, 292.0, 300.0):
            g = make_geom(cut_x, a_lip)
            key = "cut%g_lip%g" % (cut_x, a_lip)
            res[key] = run(key, g)
    print()
    print("=== R10 best-guess vs R5 reference, mu sweep, 20 s ===")
    g = make_geom(56.0, 292.0)
    for mu in (0.30, 0.40, 0.50, 0.60):
        res["R10_mu%.2f" % mu] = run("R10 cut=56 lip=292", g, mu=mu, sec=20.0)
    g5 = (lambda: r6.DPB(), r6.th2((350.0, 170.0)))
    for mu in (0.40, 1.00):
        res["R5_mu%.2f" % mu] = run("R5 reference", g5, mu=mu, sec=20.0)
    OUT.joinpath("_r10_sweep.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print("  saved", OUT / "_r10_sweep.json")


if __name__ == "__main__":
    sweep()
