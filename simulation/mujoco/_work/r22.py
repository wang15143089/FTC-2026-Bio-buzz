# -*- coding: utf-8 -*-
"""R22: fix the NECTAR hand-off.  a' needs the tray top face to END exactly at
the shell inner-wall lip, so the falling ball is tangent to the lip corner and
then rolls down the wall into the nest.

R20 used cut=84, lip=300 with R_CARRY=64 (R_IN=109.974) -> tray ended 15 mm
short of the real tangency, so the ball fell off the tray edge into a wedge.
R21 used the POLLEN cut=56 / lip=292 with R_CARRY=58.4 -> for a 91.948 ball the
tangency is at x=88.6, lip=304.5, so the tray again ended far too early.

Correct pairs solved from the geometry (tray top face = plane through PIVOT at
TILT, shell inner circle radius R_IN = R_CARRY + ball_r about the paddle axis):
  hub r=18 -> R_CARRY 64.000, R_IN 109.974, cut_x 99.1, a_lip 309.3
  hub r=12 -> R_CARRY 58.400, R_IN 104.374, cut_x 88.6, a_lip 304.5
"""
import math, sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import r6_smooth as r6
import opt_lib as ol
import r10_cradle as R10
import r12

pv2 = ol.pv2
OUT = Path("simulation/mujoco/out")
BN = 45.974
BN_MASS = 0.130
T_STALL = 0.530


def parts_hub(r_hub):
    def f():
        parts = [("hub", (0., 0., 0.), (r_hub, 17., r_hub), 0.0, "cylY")]
        for i, a in enumerate((10.0, 190.0), 1):
            parts += [("arm_%d" % i, (30., 0, 0), (16., 9., 5.), a, "box"),
                      ("blade_%d" % i, (52., 0., 0.), (6., pv2.PADDLE_W / 2., 15.), a, "box"),
                      ("flex_%d" % i, (58., 0., 0.), (2., pv2.PADDLE_W / 2., 17.), a, "box")]
        return parts
    return f


def go(tag, geom, rpm, half, ball_r, ball_m, r_carry, lr=+1.0, mu=0.40,
       sec=25.0, seated=False, bx=None, bz=None):
    old_half = pv2.HALF_SPACING
    old = (r12.N_FREE, r12.OMEGA, r12.KV, pv2.R_CARRY)
    w = rpm * 2 * math.pi / 60.0
    pv2.HALF_SPACING = half
    r12.N_FREE, r12.OMEGA = rpm, w
    r12.KV = T_STALL / w
    pv2.R_CARRY = r_carry
    if bx is None:
        bx = pv2.PADDLE_CX if seated else 145.0
    if bz is None:
        bz = (pv2.PADDLE_CZ - r_carry) if seated else pv2.tray_top_z(bx) + ball_r
    try:
        return r12.run("%s" % tag, geom, sign=lr, mu=mu, bx=bx, bz=bz, sec=sec,
                       ball_r=ball_r, ball_m=ball_m, r_in=r_carry + ball_r,
                       detail=0.5, quiet=False)
    finally:
        pv2.HALF_SPACING = old_half
        r12.N_FREE, r12.OMEGA, r12.KV, pv2.R_CARRY = old


def main():
    res = {}
    print("=== R22 NECTAR hand-off: tray end == shell lip tangency ===", flush=True)

    g18 = (lambda: R10.stat(99.1, 309.3), parts_hub(18.0))
    g12 = (lambda: R10.stat(88.6, 304.5), parts_hub(12.0))

    print("-- A1. hub18 R_CARRY=64 cut=99.1 lip=309.3 nip82 60rpm sign=+1 --", flush=True)
    res["A1_hub18_plus"] = go("A1", g18, 60.0, 89.0, BN, BN_MASS, 64.0, lr=+1.0)
    print("-- A2. hub18 same, sign=-1 --", flush=True)
    res["A2_hub18_minus"] = go("A2", g18, 60.0, 89.0, BN, BN_MASS, 64.0, lr=-1.0)

    print("-- B1. hub12 R_CARRY=58.4 cut=88.6 lip=304.5 nip82 60rpm sign=+1 --", flush=True)
    res["B1_hub12_plus"] = go("B1", g12, 60.0, 89.0, BN, BN_MASS, 58.4, lr=+1.0)
    print("-- B2. hub12 same, sign=-1 --", flush=True)
    res["B2_hub12_minus"] = go("B2", g12, 60.0, 89.0, BN, BN_MASS, 58.4, lr=-1.0)

    thin = {k: {kk: vv for kk, vv in v.items() if kk != "_trace"} for k, v in res.items()}
    OUT.joinpath("_r22_nectar_handoff.json").write_text(
        json.dumps(thin, ensure_ascii=False, indent=1), encoding="utf-8")
    print("saved", OUT / "_r22_nectar_handoff.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
