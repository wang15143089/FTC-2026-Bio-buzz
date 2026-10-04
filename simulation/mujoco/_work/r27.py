# -*- coding: utf-8 -*-
"""R27: indexed servo cycle - park paddle clear, let the ball settle in the nest,
then ONE sweep carries it from the lip (275 deg) to the exit (142 deg).
Both ball sizes, same shell, only the flywheel nip differs."""
import math, sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import opt_lib as ol
import r10_cradle as R10
import r23
import mujoco, numpy as np

pv2 = ol.pv2
OUT = Path("simulation/mujoco/out")
R_IN = 107.974; CUT_X = 38.901; A_LIP = 275.0; PIVOT = (-0.806, 0.423)
TRAY_X1 = 150.0; TILT = 5.0; WHEEL_R = 48.0; T_STALL = 0.530
SIN_T = math.sin(math.radians(TILT)); COS_T = math.cos(math.radians(TILT))
D = math.degrees

def setup(ball_r, ball_m, nip):
    pv2.HALF_SPACING = nip/2.0 + WHEEL_R
    pv2.R_CARRY = R_IN - ball_r
    pv2.PIVOT_X, pv2.PIVOT_Z = PIVOT
    pv2.R_IN = R_IN; pv2.R_OUT = R_IN + pv2.SHELL_WALL
    R10.R_MID = R_IN + 3.5
    pv2.BALL_R = ball_r; pv2.BALL_MASS = ball_m
    pv2.static_geoms = (lambda: R10.stat(CUT_X, A_LIP, tray_x1=TRAY_X1))
    pv2.paddle_parts = r23.parts_hub(12.0)

def run(tag, ball_r, ball_m, nip, xc, hold=1.6, sweep_deg=228.0,
        rpm=290.0, t_end=8.0, mu=0.40):
    setup(ball_r, ball_m, nip)
    bx = xc - ball_r*SIN_T
    bz = pv2.tray_top_z(xc) + ball_r*COS_T
    w = rpm*2*math.pi/60.0
    kv = T_STALL/w
    xml, ctrl = pv2.build_xml(1620.0, -1, 0.0, bx, bz)
    xml = xml.replace('class="ball"><geom friction="1.0 0.02 0.0001"',
                      'class="ball"><geom friction="%g 0.02 0.0001"' % mu)
    m = mujoco.MjModel.from_xml_string(xml)
    d = mujoco.MjData(m)
    aid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "paddle_vel")
    jid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "paddle_joint")
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    bgeom = {g for g in range(m.ngeom) if m.geom_bodyid[g] == bid}
    d.ctrl[:] = [ctrl[0], ctrl[1], 0.0]
    mujoco.mj_forward(m, d)
    dt = m.opt.timestep; n = int(t_end/dt)
    k = max(1, int(round(0.05/dt)))
    tr = []; tq = np.zeros(n); rp = np.zeros(n)
    KVC = 1.0/max(dt,1e-6)
    for i in range(n):
        t = i*dt
        if t < hold:
            m.actuator_gainprm[aid, 0] = -KVC          # strong brake at angle 0
            m.actuator_biasprm[aid, 1] = KVC
            d.ctrl[aid] = 0.0
        else:
            m.actuator_gainprm[aid, 0] = kv             # normal velocity servo
            m.actuator_biasprm[aid, 1] = -kv
            d.ctrl[aid] = w
        mujoco.mj_step(m, d)
        tq[i] = abs(float(d.actuator_force[aid]))
        rp[i] = D(d.qvel[jid])/6.0
        p = d.xpos[bid]*1000.0
        rx, rz = p[0]-pv2.PADDLE_CX, p[2]-pv2.PADDLE_CZ
        if i % k == 0:
            cnt = sorted({mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM,
                           int(cc.geom2 if cc.geom1 in bgeom else cc.geom1))
                          for cc in d.contact[:d.ncon] if (cc.geom1 in bgeom or cc.geom2 in bgeom)})
            lx, lz = pv2.to_shooter(p[0], p[2])
            tr.append({"t": round(t,3), "x": round(float(p[0]),2), "z": round(float(p[2]),2),
                       "v": round(float(np.linalg.norm(d.cvel[bid][3:])),3),
                       "vx": round(float(d.cvel[bid][3]),3), "vz": round(float(d.cvel[bid][5]),3),
                       "r": round(math.hypot(rx,rz),2), "ang": round(D(math.atan2(rz,rx))%360.0,1),
                       "joint": round(D(d.qpos[jid]),1), "lx": round(lx,2), "lz": round(lz,2),
                       "touch": ",".join(cnt) or "-"})
    res = pv2.analyse(tr)
    e = res.get("exit") or {}
    print("%-22s launch=%-5s exit_t=%-6s v=%-6s ang=%-7s jam=%-5s rpmMed=%-6.1f "
          "min_r=%-6.2f minang=%-6.1f final=(%.0f,%.0f)"
          % (tag, res["launched"], e.get("t","--"), e.get("speed_m_s","--"),
             e.get("angle_deg","--"), "%.0f%%" % (100*float((tq > 0.40).mean())),
             float(np.median(rp[n//4:])), min(s["r"] for s in tr),
             res["min_angle_deg"], res["final_mm"][0], res["final_mm"][1]), flush=True)
    return res, tr

def main():
    res = {}
    N = dict(ball_r=45.974, ball_m=0.130, nip=82.0)
    P = dict(ball_r=35.56, ball_m=0.060, nip=64.0)
    print("=== R27 indexed cycle: park 1.6 s -> one 228 deg sweep, servo 290 rpm ===", flush=True)
    r, tr = run("NECTAR r45.97 nip82", **N, xc=96.0)
    res["nectar"] = {k: v for k, v in r.items() if k != "_trace"}
    print("  trace:", flush=True)
    for s in tr[::max(1, len(tr)//16)]:
        print("     t=%5.2f x=%7.2f z=%7.2f r=%6.2f ang=%6.1f J=%7.1f lx=%7.1f  %s"
              % (s["t"], s["x"], s["z"], s["r"], s["ang"], s["joint"], s["lx"], s["touch"]), flush=True)
    r, tr = run("POLLEN r35.56 nip64", **P, xc=104.0)
    res["pollen"] = {k: v for k, v in r.items() if k != "_trace"}
    print("  trace:", flush=True)
    for s in tr[::max(1, len(tr)//16)]:
        print("     t=%5.2f x=%7.2f z=%7.2f r=%6.2f ang=%6.1f J=%7.1f lx=%7.1f  %s"
              % (s["t"], s["x"], s["z"], s["r"], s["ang"], s["joint"], s["lx"], s["touch"]), flush=True)
    OUT.joinpath("_r27_indexed.json").write_text(json.dumps(res, ensure_ascii=False, indent=1),
                                                 encoding="utf-8")
    print("saved", OUT/"_r27_indexed.json", flush=True)

if __name__ == "__main__":
    raise SystemExit(main())
