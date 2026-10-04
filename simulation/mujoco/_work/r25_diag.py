# -*- coding: utf-8 -*-
"""R25 diagnostic: separate the tray/shell question from the rotor question.

ROTOR variants (all in the R25 shared shell, R_IN=107.974, A_LIP=275, CUT_X=38.901):
  cad  : the real CAD rotor  hub O24, arm 36x18x10 @r28, hinge O10 @r46,
                             blade 12x96x30 @r52 (radial 46..58), flex 4x96x34 @r58 (56..60)
  sim3 : the rotor used by pollen_v2_sim / r23.parts_hub  arm 16x9x5 @30,
                             blade 6x48x15 @52, flex 2x48x17 @58
ROTOR rpm = 0 means a blocked rotor (velocity servo at 0 -> acts as a brake).
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
T_STALL = 0.530
WHEEL_R = 48.0


def parts_cad(hub_r=12.0):
    def f():
        out = [("hub", (0.0, 0.0, 0.0), (hub_r, 17.0), 0.0, "cylY")]
        for i, a in enumerate((18.0, 138.0, 258.0), 1):
            out.append(("arm_%d" % i, (28.0, 0.0, 0.0), (36.0, 18.0, 10.0), a, "box"))
            out.append(("hinge_%d" % i, (46.0, 0.0, 0.0), (5.0, 50.0), a, "cylY"))
            out.append(("blade_%d" % i, (52.0, 0.0, 0.0), (12.0, 96.0, 30.0), a, "box"))
            out.append(("flex_%d" % i, (58.0, 0.0, 0.0), (4.0, 96.0, 34.0), a, "box"))
        return out
    return f


def parts_sim3(hub_r=18.0):
    def f():
        out = [("hub", (0.0, 0.0, 0.0), (hub_r, 17.0), 0.0, "cylY")]
        for i, a in enumerate((18.0, 138.0, 258.0), 1):
            out.append(("arm_%d" % i, (30.0, 0.0, 0.0), (16.0, 9.0, 5.0), a, "box"))
            out.append(("blade_%d" % i, (52.0, 0.0, 0.0), (6.0, 48.0, 15.0), a, "box"))
            out.append(("flex_%d" % i, (58.0, 0.0, 0.0), (2.0, 48.0, 17.0), a, "box"))
        return out
    return f


def parts_sim2(hub_r=18.0):
    def f():
        out = [("hub", (0.0, 0.0, 0.0), (hub_r, 17.0), 0.0, "cylY")]
        for i, a in enumerate((10.0, 190.0), 1):
            out.append(("arm_%d" % i, (30.0, 0.0, 0.0), (16.0, 9.0, 5.0), a, "box"))
            out.append(("blade_%d" % i, (52.0, 0.0, 0.0), (6.0, 48.0, 15.0), a, "box"))
            out.append(("flex_%d" % i, (58.0, 0.0, 0.0), (2.0, 48.0, 17.0), a, "box"))
        return out
    return f


ROTOR = {"cad": parts_cad, "sim3": parts_sim3, "sim2": parts_sim2}


def sim(tag, rotor, ball_r, ball_m, nip, rpm, sec=20.0, bx=145.0, mu=0.40, sign=+1.0):
    pv2.HALF_SPACING = nip / 2.0 + WHEEL_R
    pv2.R_CARRY = R_IN - ball_r
    pv2.PIVOT_X, pv2.PIVOT_Z = PIVOT
    pv2.R_IN = R_IN
    pv2.R_OUT = R_IN + pv2.SHELL_WALL
    R10.R_MID = R_IN + 3.5
    pv2.BALL_R = ball_r
    pv2.BALL_MASS = ball_m
    pv2.static_geoms = (lambda: R10.stat(CUT_X, A_LIP, tray_x1=185.0))
    pv2.paddle_parts = ROTOR[rotor]()
    bz = pv2.tray_top_z(bx) + ball_r
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
    out = {"tag": tag, "rotor": rotor, "ball_r": ball_r, "nip": nip, "rpm": rpm,
           "min_r": min(s["r"] for s in tr), "min_ang": min(s["ang"] for s in tr),
           "final": [tr[-1]["x"], tr[-1]["z"]],
           "samples": [(s["t"], s["x"], s["z"], s["r"], s["ang"]) for s in tr[::4]]}
    return out


def main():
    res = []
    N = dict(ball_r=45.974, ball_m=0.130, nip=82.0)
    P = dict(ball_r=35.56, ball_m=0.060, nip=64.0)
    plan = [("NECTAR static rotor", "cad", N, 0.0),
            ("NECTAR rotor=cad 60rpm", "cad", N, 60.0),
            ("NECTAR rotor=sim3 60rpm", "sim3", N, 60.0),
            ("NECTAR rotor=sim2 60rpm", "sim2", N, 60.0),
            ("POLLEN rotor=cad 60rpm", "cad", P, 60.0),
            ("POLLEN rotor=sim3 60rpm", "sim3", P, 60.0)]
    for tag, rotor, ball, rpm in plan:
        r = sim(tag, rotor, rpm=rpm, **ball)
        res.append(r)
        print("%-26s rotor=%-4s ball_r=%6.3f  min_r=%7.2f min_ang=%7.1f final=(%8.1f,%8.1f)"
              % (tag, rotor, ball["ball_r"], r["min_r"], r["min_ang"],
                 r["final"][0], r["final"][1]), flush=True)
        print("      path: " + " | ".join("t=%.1f x=%.0f z=%.0f r=%.0f a=%.0f" % s
                                           for s in r["samples"]), flush=True)
    OUT.joinpath("_r25_diag.json").write_text(json.dumps(res, ensure_ascii=False, indent=1),
                                              encoding="utf-8")
    print("saved", OUT / "_r25_diag.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
