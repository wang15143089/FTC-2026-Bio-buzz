# -*- coding: utf-8 -*-
"""R9: ball-nest (rest pocket) geometry sweep + ball-friction threshold ladder."""
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


def nest(kind, step=6.8, xc=-2.0, w=30.0, ang=0.0):
    """Return a static-geoms factory with a shaped rest pocket."""
    def f():
        g = list(ol.ORIG_STATIC())
        if kind == "none":
            return g
        if kind == "flat":
            ztop = pv2.tray_top_z(xc) + step
            g.append(("rest_pad", "shell", "box", (w, pv2.FEEDER_W, step + 6.0),
                      (xc, 0.0, ztop - (step + 6.0) / 2.0), pv2.quat_y(0.0)))
        elif kind == "ramp":
            # a tilted plate: ball parks in the corner it makes with the tray
            L = w
            nmx, nmz = pv2.normal(ang)
            ztop = pv2.tray_top_z(xc) + step
            g.append(("rest_pad", "shell", "box", (L, pv2.FEEDER_W, 6.0),
                      (xc - nmx * 3.0, 0.0, ztop - nmz * 3.0), pv2.quat_y(-ang)))
        elif kind == "vee":
            # two plates at +/- (90-25) deg cradling the ball at xc
            for sgn in (-1, 1):
                a = sgn * (90.0 - kwv)  # noqa
        return g
    return f


KW = {}


def vee(xc, half_deg=35.0, plate_t=5.0, length=34.0):
    def f():
        g = list(ol.ORIG_STATIC())
        R = pv2.BALL_R
        h = R / math.sin(math.radians(half_deg))
        zc = pv2.tray_top_z(xc) + h
        for sgn in (-1, 1):
            a = sgn * half_deg
            # plate top face is tangent to the ball: place plate centre at
            # distance R+plate_t/2 from the ball centre along the inward normal
            nx, nz = math.sin(math.radians(a)), math.cos(math.radians(a))
            cx = xc - sgn * nx * (R + plate_t / 2.0)
            cz = zc - nz * (R + plate_t / 2.0)
            g.append(("vee_%+d" % sgn, "shell", "box", (length, pv2.FEEDER_W, plate_t),
                      (cx, 0.0, cz), pv2.quat_y(a)))
        return g
    return f


def run(tag, static, bx=20.9, sec=8.0, mu_ball=None, rpm=N_FREE, quiet=False):
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
    ent = next((s for s in tr if s["ang"] < 232.0 and 45 <= s["r"] <= 75), None)
    ex = next((s for s in tr if s["ang"] <= 143.0 and 45 <= s["r"] <= 75), None)
    res["jam_frac"] = round(float((tq > 0.40).mean()), 3)
    res["rpm_med"] = round(float(np.median(rp)), 1)
    res["carry_s"] = round(ex["t"] - ent["t"], 2) if (ent and ex) else -1.0
    res["rest_xy"] = [tr[0]["x"], tr[0]["z"]]
    res["rest_r"] = tr[0]["r"]; res["rest_ang"] = tr[0]["ang"]
    res["_trace"] = tr
    if not quiet:
        print("  %-24s launched=%-5s exit_t=%-6s exit_v=%-6s carry=%-6s jam=%-5s rpmMed=%-6s peak=%.2f"
              % (tag, res["launched"], (res.get("exit") or {}).get("t", "--"),
                 (res.get("exit") or {}).get("speed_m_s", "--"), res["carry_s"],
                 "%.0f%%" % (100 * res["jam_frac"]), res["rpm_med"], res["peak_speed_m_s"]),
              flush=True)
    return res


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "nest"
    out = {}
    if mode == "mu":
        print("=== R9 ball-friction ladder (base nest D6.8, pocket start, 8 s) ===")
        for mu in (1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.45, 0.4, 0.3):
            out["mu%g" % mu] = run("mu=%.2f" % mu, ol.GEOM["D 球窝抬高6.8"][0], mu_ball=mu)
    else:
        print("=== R9 ball-nest geometry sweep (mu=1.0, pocket start, 8 s) ===")
        out["N0 pad 6.8 (base)"] = run("pad step6.8 (base)", nest("flat"))
        for st in (0.0, 3.0, 10.0, 13.0):
            out["N1 pad step%g" % st] = run("pad step%g" % st, nest("flat", step=st))
        for xc in (8.0, 18.0, 28.0, 38.0):
            out["N2 pad x=%g" % xc] = run("pad x=%g" % xc, nest("flat", xc=xc))
        out["N3 no pad"] = run("no pad", nest("none"))
        out["N4 vee 35deg"] = run("vee 35deg", vee(-2.0, 35.0))
        out["N5 vee 45deg"] = run("vee 45deg", vee(-2.0, 45.0))
        out["N6 vee 25deg"] = run("vee 25deg", vee(-2.0, 25.0))
        out["N7 ramp -20"] = run("ramp -20", nest("ramp", ang=-20.0))
    (OUT / ("_r9_%s.json" % mode)).write_text(
        json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "_trace"} for k, v in out.items()},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    print("  saved", OUT / ("_r9_%s.json" % mode))


if __name__ == "__main__":
    main()
