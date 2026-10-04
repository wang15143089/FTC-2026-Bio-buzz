# -*- coding: utf-8 -*-
"""R25-C diag (clean start).  Previous NECTAR runs started the ball at bx=145 with
tray_x1=185 -> ball outer face at 191 mm, rear-wall inner face at 185 mm: a 6 mm
initial penetration that fired the ball off with a contact-force explosion.
Every NECTAR conclusion from R13..R24 (and this morning's R25 runs) is therefore
contaminated.  Here the ball is placed exactly at rest on the tray, clear of the
rear wall, tray_x1 = 150 (matches CAD TRAY_X1).

Rotors: cad  = real CAD rotor  (blade 12x96x30 @r52 -> radial 46..58, flex 4x96x34 @r58)
        sim3 = pollen_v2_sim proxy rotor (blade 6x48x15 @52, flex 2x48x17 @58)
        reach= CAD rotor + 2nd blade 58..70 + tongue 70..76  (engages BOTH carry radii)
"""
import math, sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import opt_lib as ol
import r10_cradle as R10
import mujoco, numpy as np

pv2 = ol.pv2
OUT = Path("simulation/mujoco/out")
R_IN = 107.974
CUT_X = 38.901
A_LIP = 275.0
PIVOT = (-0.806, 0.423)
TRAY_X1 = 150.0
T_STALL = 0.530
WHEEL_R = 48.0
TILT = 5.0
SIN_T = math.sin(math.radians(TILT))
COS_T = math.cos(math.radians(TILT))


def rotor(kind, hub_r=12.0):
    def f():
        out = [("hub", (0.0, 0.0, 0.0), (hub_r, 17.0), 0.0, "cylY")]
        for i, a in enumerate((18.0, 138.0, 258.0), 1):
            out.append(("arm_%d" % i, (28.0, 0.0, 0.0), (36.0, 18.0, 10.0), a, "box"))
            out.append(("hinge_%d" % i, (46.0, 0.0, 0.0), (5.0, 50.0), a, "cylY"))
            if kind == "cad":
                out.append(("blade_%d" % i, (52.0, 0.0, 0.0), (12.0, 96.0, 30.0), a, "box"))
                out.append(("flex_%d" % i, (58.0, 0.0, 0.0), (4.0, 96.0, 34.0), a, "box"))
            elif kind == "sim3":
                out.append(("blade_%d" % i, (52.0, 0.0, 0.0), (6.0, 48.0, 15.0), a, "box"))
                out.append(("flex_%d" % i, (58.0, 0.0, 0.0), (2.0, 48.0, 17.0), a, "box"))
            elif kind == "reach":
                out.append(("blade_%d" % i, (52.0, 0.0, 0.0), (12.0, 96.0, 30.0), a, "box"))
                out.append(("reach_%d" % i, (64.0, 0.0, 0.0), (12.0, 96.0, 26.0), a, "box"))
                out.append(("tongue_%d" % i, (73.0, 0.0, 0.0), (6.0, 96.0, 34.0), a, "box"))
        return out
    return f


def rest_start(xc, ball_r):
    """ball centre resting on the tray with its contact foot at x = xc"""
    return xc - ball_r * SIN_T, pv2.tray_top_z(xc) + ball_r * COS_T


def sim(tag, kind, ball_r, ball_m, nip, rpm, sec=12.0, mu=0.40, sign=+1.0,
        xc=None, hub_r=12.0, tray_x1=TRAY_X1):
    pv2.HALF_SPACING = nip / 2.0 + WHEEL_R
    pv2.R_CARRY = R_IN - ball_r
    pv2.PIVOT_X, pv2.PIVOT_Z = PIVOT
    pv2.R_IN = R_IN
    pv2.R_OUT = R_IN + pv2.SHELL_WALL
    R10.R_MID = R_IN + 3.5
    pv2.BALL_R = ball_r
    pv2.BALL_MASS = ball_m
    pv2.static_geoms = (lambda: R10.stat(CUT_X, A_LIP, tray_x1=tray_x1))
    pv2.paddle_parts = rotor(kind, hub_r)
    if xc is None:
        xc = tray_x1 - ball_r * 0.91284 - 2.0
    bx, bz = rest_start(xc, ball_r)
    w = rpm * 2.0 * math.pi / 60.0
    xml, ctrl = pv2.build_xml(1620.0, -1, sign * w, bx, bz)
    if rpm > 0.0:
        xml = xml.replace('kv="0.08"', 'kv="%.6f"' % (T_STALL / w))
    else:
        xml = xml.replace('kv="0.08"', 'kv="40.0"')
        xml = xml.replace('forcerange="-1.5 1.5"', 'forcerange="0 0"')
    xml = xml.replace('class="ball"><geom friction="1.0 0.02 0.0001"',
                      'class="ball"><geom friction="%g 0.02 0.0001"' % mu)
    m = mujoco.MjModel.from_xml_string(xml)
    d = mujoco.MjData(m)
    d.ctrl[:] = ctrl
    mujoco.mj_forward(m, d)
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    dt = m.opt.timestep
    n = int(sec / dt)
    k = max(1, int(round(0.05 / dt)))
    tr = []
    for i in range(n):
        mujoco.mj_step(m, d)
        if i % k == 0:
            p = d.xpos[bid] * 1000.0
            rx, rz = p[0] - pv2.PADDLE_CX, p[2] - pv2.PADDLE_CZ
            tr.append({"t": round(i * dt, 3), "x": round(p[0], 2), "z": round(p[2], 2),
                       "v": round(float(np.linalg.norm(d.cvel[bid][3:])), 3),
                       "r": round(math.hypot(rx, rz), 2),
                       "ang": round(math.degrees(math.atan2(rz, rx)) % 360.0, 1)})
    rc = R_IN - ball_r
    carried = [s for s in tr if s["ang"] <= 200.0 and 130.0 <= s["ang"] <= 275.0
               and abs(s["r"] - rc) <= 12.0]
    out = {"tag": tag, "rotor": kind, "ball_r": ball_r, "nip": nip, "rpm": rpm,
           "start": [round(bx, 2), round(bz, 2)], "carry_radius": round(rc, 3),
           "min_r": min(s["r"] for s in tr), "min_ang": min(s["ang"] for s in tr),
           "reached_exit": bool([s for s in tr if s["ang"] <= 143.0 and abs(s["r"] - rc) <= 12.0]),
           "final": [tr[-1]["x"], tr[-1]["z"]],
           "samples": [(s["t"], s["x"], s["z"], s["r"], s["ang"]) for s in tr[::2]]}
    return out


def main():
    res = []
    N = dict(ball_r=45.974, ball_m=0.130, nip=82.0)
    P = dict(ball_r=35.56, ball_m=0.060, nip=64.0)
    plan = [("NECTAR free rotor", "cad", N, 0.0, None),
            ("NECTAR cad 60rpm", "cad", N, 60.0, None),
            ("NECTAR sim3 60rpm", "sim3", N, 60.0, 18.0),
            ("NECTAR reach 60rpm", "reach", N, 60.0, None),
            ("POLLEN free rotor", "cad", P, 0.0, None),
            ("POLLEN cad 60rpm", "cad", P, 60.0, None),
            ("POLLEN sim3 60rpm", "sim3", P, 60.0, 18.0),
            ("POLLEN reach 60rpm", "reach", P, 60.0, None)]
    for tag, kind, ball, rpm, hub in plan:
        kw = dict(ball)
        if hub is not None:
            kw["hub_r"] = hub
        r = sim(tag, kind, rpm=rpm, **kw)
        res.append(r)
        print("%-20s rotor=%-5s r=%.3f start=(%.1f,%.1f) min_r=%7.2f min_ang=%7.1f "
              "exit=%-5s final=(%8.1f,%8.1f)"
              % (tag, kind, ball["ball_r"], r["start"][0], r["start"][1], r["min_r"],
                 r["min_ang"], r["reached_exit"], r["final"][0], r["final"][1]), flush=True)
    OUT.joinpath("_r25c_diag.json").write_text(json.dumps(res, ensure_ascii=False, indent=1),
                                               encoding="utf-8")
    print("saved", OUT / "_r25c_diag.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

