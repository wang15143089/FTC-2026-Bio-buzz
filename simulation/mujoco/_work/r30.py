# -*- coding: utf-8 -*-
"""R29: robustness grid for the shared 2-blade paddle.
Which home phase (330/150 vs 10/190), which sweep (180 vs 248), and how much
entry-position / settle-time tolerance, for BOTH ball sizes with the same shell,
tray and paddle.  Only the flywheel nip differs."""
import math, sys, json, itertools
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import opt_lib as ol
import r10_cradle as R10
import mujoco, numpy as np

pv2 = ol.pv2
OUT = Path("simulation/mujoco/out")
R_IN = 107.974; CUT_X = 38.901; A_LIP = 275.0; PIVOT = (-0.806, 0.423)
TRAY_X1 = 150.0; TILT = 5.0; WHEEL_R = 48.0; T_STALL = 0.530
SIN_T = math.sin(math.radians(TILT)); COS_T = math.cos(math.radians(TILT))
D = math.degrees

def parts(phases, hub_r=12.0):
    def f():
        out = [("hub", (0.,0.,0.), (hub_r, 17.), 0.0, "cylY")]
        for i, a in enumerate(phases, 1):
            out += [("arm_%d" % i, (28.,0.,0.), (18.,9.,5.), a, "box"),
                    ("blade_%d" % i, (52.,0.,0.), (6., pv2.PADDLE_W/2., 15.), a, "box"),
                    ("flex_%d" % i, (58.,0.,0.), (2., pv2.PADDLE_W/2., 17.), a, "box")]
        return out
    return f

HOME = {"330_150": parts((330.0, 150.0)), "10_190": parts((10.0, 190.0))}

def run(ball_r, ball_m, nip, xc, hold, sw, rpm=290.0, t_end=8.0, mu=0.40, paddle=None):
    pv2.HALF_SPACING = nip/2.0 + WHEEL_R
    pv2.R_CARRY = R_IN - ball_r
    pv2.PIVOT_X, pv2.PIVOT_Z = PIVOT
    pv2.R_IN = R_IN; pv2.R_OUT = R_IN + pv2.SHELL_WALL
    R10.R_MID = R_IN + 3.5
    pv2.BALL_R = ball_r; pv2.BALL_MASS = ball_m
    pv2.static_geoms = (lambda: R10.stat(CUT_X, A_LIP, tray_x1=TRAY_X1))
    pv2.paddle_parts = paddle
    bx = xc - ball_r*SIN_T
    bz = pv2.tray_top_z(xc) + ball_r*COS_T
    w = rpm*2*math.pi/60.0; kv = T_STALL/w
    xml, ctrl = pv2.build_xml(1620.0, -1, 0.0, bx, bz)
    xml = xml.replace('kv="0.08"', 'kv="%.6f"' % kv)
    xml = xml.replace('forcerange="-1.5 1.5"', 'forcerange="-%g %g"' % (T_STALL, T_STALL))
    xml = xml.replace('class="ball"><geom friction="1.0 0.02 0.0001"',
                      'class="ball"><geom friction="%g 0.02 0.0001"' % mu)
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    aid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "paddle_vel")
    jid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "paddle_joint")
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    bgeom = {g for g in range(m.ngeom) if m.geom_bodyid[g] == bid}
    d.ctrl[:] = [ctrl[0], ctrl[1], 0.0]
    mujoco.mj_forward(m, d)
    dt = m.opt.timestep; n = int(t_end/dt); k = max(1, int(round(0.05/dt)))
    tr = []; tq = np.zeros(n); released = False
    for i in range(n):
        t = i*dt; J = D(d.qpos[jid])
        if t < hold: d.ctrl[aid] = 0.0
        elif not released and J < sw: d.ctrl[aid] = w
        else:
            released = True; d.ctrl[aid] = 0.0
        mujoco.mj_step(m, d)
        tq[i] = abs(float(d.actuator_force[aid]))
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
                       "r": round(math.hypot(rx,rz),2),
                       "ang": round(D(math.atan2(rz,rx))%360.0,1),
                       "J": round(D(d.qpos[jid])%360.0,1), "joint": round(J,1),
                       "lx": round(lx,2), "lz": round(lz,2), "touch": ",".join(cnt) or "-"})
    res = pv2.analyse(tr)
    res["_jam"] = float((tq > 0.40).mean())
    res["_minr"] = min(s["r"] for s in tr)
    res["_trace"] = tr[::max(1, len(tr)//12)]
    return res

BALLS = {"NECTAR": dict(ball_r=45.974, ball_m=0.130, nip=82.0),
         "POLLEN": dict(ball_r=35.56, ball_m=0.060, nip=64.0)}

def main():
    rows = []
    print("=== R30 margin: home x sweep x entry xc x settle hold (same shell/paddle for both balls) ===",
          flush=True)
    print("%-8s %-6s %-7s %-5s %-5s | %-16s | %-16s" %
          ("home", "sweep", "nx", "xc", "hold", "NECTAR", "POLLEN"), flush=True)
    for home, sw in itertools.product(("330_150",), (240.0, 248.0, 260.0)):
        for xc in (98.0, 128.0):
            for hold in (3.0, 5.0):
                out = {}
                for bname, bprm in BALLS.items():
                    prm = dict(bprm)
                    prm["xc"] = xc - 108.0 + 108.0   # same tray frame for both
                    r = run(hold=hold, sw=sw, paddle=HOME[home], **prm)
                    e = r.get("exit") or {}
                    out[bname] = (r["launched"], e.get("t"), e.get("speed_m_s"),
                                  e.get("angle_deg"), round(100*r["_jam"]), r["_minr"])
                rows.append(dict(home=home, sweep=sw, xc=xc, hold=hold,
                                 nectar=out["NECTAR"], pollen=out["POLLEN"]))
                print("%-8s %-6.0f %-7.0f %-5.0f %-5.1f | %-16s | %-16s" %
                      (home, sw, 0.0, xc, hold,
                       "OK t=%.2f v=%.2f j=%d%%" % (out["NECTAR"][1] or -1,
                                                    out["NECTAR"][2] or -1, out["NECTAR"][4])
                       if out["NECTAR"][0] else "FAIL j=%d%%" % out["NECTAR"][4],
                       "OK t=%.2f v=%.2f j=%d%%" % (out["POLLEN"][1] or -1,
                                                    out["POLLEN"][2] or -1, out["POLLEN"][4])
                       if out["POLLEN"][0] else "FAIL j=%d%%" % out["POLLEN"][4]),
                      flush=True)
    OUT.joinpath("_r30_margin.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1),
                                              encoding="utf-8")
    print("saved", OUT/"_r30_margin.json", flush=True)

if __name__ == "__main__":
    raise SystemExit(main())

