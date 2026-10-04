# -*- coding: utf-8 -*-
"""R23: gravity hand-off.  The a' recipe only works when the tray top face is
tangent to the shell inner circle (radius R_IN = R_CARRY + ball_r) about the
paddle axis, i.e. the ball rolling down the tray arrives exactly on the carry
circle at the shell lip.

Tray plane (through PIVOT, tilt 5 deg) sits d0 = 90.83 mm from the paddle axis.
Needed: d0 = R_IN, so the whole tray must move OUT along its own normal by
    delta = R_IN - d0.
Then the tangency point (and therefore the tray cut and the shell lip) is
    F = A + R_IN * (sin(tilt), -cos(tilt)).

POLLEN a' had delta = 3.13 mm -> ball arrives 1.1 mm high -> tolerated.
NECTAR hub r=12 -> delta = 13.5 mm, hub r=18 -> delta = 19.1 mm.  That mismatch
is exactly why R20/R21/R22 could not feed: the ball was dropped 13-16 mm.
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
SIN_T = math.sin(math.radians(pv2.TILT))
COS_T = math.cos(math.radians(pv2.TILT))


def plane_dist():
    """perpendicular distance from the paddle axis to the current tray top plane"""
    dx = pv2.PADDLE_CX - pv2.PIVOT_X
    dz = pv2.PADDLE_CZ - pv2.PIVOT_Z
    return dz * COS_T - dx * SIN_T          # normal (sin, -cos) pointing A->plane


def tangent_setup(r_carry, ball_r):
    R_IN = r_carry + ball_r
    d0 = plane_dist()
    delta = R_IN - d0
    Fx = pv2.PADDLE_CX + R_IN * SIN_T
    Fz = pv2.PADDLE_CZ - R_IN * COS_T
    ang = math.degrees(math.atan2(Fz - pv2.PADDLE_CZ, Fx - pv2.PADDLE_CX)) % 360.0
    piv = (pv2.PIVOT_X + delta * SIN_T, pv2.PIVOT_Z - delta * COS_T)
    return dict(R_IN=R_IN, d0=d0, delta=delta, Fx=Fx, Fz=Fz, a_lip=ang, pivot=piv)


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
       sec=25.0, seated=False, bx=None, bz=None, pivot=None):
    old = (pv2.HALF_SPACING, r12.N_FREE, r12.OMEGA, r12.KV, pv2.R_CARRY,
           pv2.PIVOT_X, pv2.PIVOT_Z)
    w = rpm * 2 * math.pi / 60.0
    pv2.HALF_SPACING = half
    r12.N_FREE, r12.OMEGA = rpm, w
    r12.KV = T_STALL / w
    pv2.R_CARRY = r_carry
    if pivot is not None:
        pv2.PIVOT_X, pv2.PIVOT_Z = pivot
    if bx is None:
        bx = pv2.PADDLE_CX if seated else 145.0
    if bz is None:
        bz = (pv2.PADDLE_CZ - r_carry) if seated else pv2.tray_top_z(bx) + ball_r
    try:
        return r12.run("%s" % tag, geom, sign=lr, mu=mu, bx=bx, bz=bz, sec=sec,
                       ball_r=ball_r, ball_m=ball_m, r_in=r_carry + ball_r,
                       detail=0.5, quiet=False)
    finally:
        (pv2.HALF_SPACING, r12.N_FREE, r12.OMEGA, r12.KV, pv2.R_CARRY,
         pv2.PIVOT_X, pv2.PIVOT_Z) = old


def main():
    res = {}
    print("=== R23 NECTAR gravity hand-off: tray tangent to carry circle ===", flush=True)
    s12 = tangent_setup(58.4, BN)
    s18 = tangent_setup(64.0, BN)
    for nm, s in (("hub12", s12), ("hub18", s18)):
        print("  %s: d0=%.3f delta=%.3f pivot=(%.3f, %.3f) cut_x=%.3f a_lip=%.3f" %
              (nm, s["d0"], s["delta"], s["pivot"][0], s["pivot"][1], s["Fx"], s["a_lip"]),
              flush=True)
    res["_setup"] = {k: {kk: (list(vv) if isinstance(vv, tuple) else vv)
                         for kk, vv in v.items()} for k, v in (("hub12", s12), ("hub18", s18))}

    g12 = (lambda: R10.stat(s12["Fx"], s12["a_lip"]), parts_hub(12.0))
    g18 = (lambda: R10.stat(s18["Fx"], s18["a_lip"]), parts_hub(18.0))

    print("-- G1. hub12 R_CARRY=58.4 tangent tray, nip82, 60rpm sign=+1, 25s --", flush=True)
    res["G1_hub12_60_plus"] = go("G1", g12, 60.0, 89.0, BN, BN_MASS, 58.4,
                                 lr=+1.0, pivot=s12["pivot"])
    print("-- G2. same but 90 rpm --", flush=True)
    res["G2_hub12_90_plus"] = go("G2", g12, 90.0, 89.0, BN, BN_MASS, 58.4,
                                 lr=+1.0, pivot=s12["pivot"])
    print("-- G3. hub18 R_CARRY=64 tangent tray, nip82, 60rpm sign=+1, 25s --", flush=True)
    res["G3_hub18_60_plus"] = go("G3", g18, 60.0, 89.0, BN, BN_MASS, 64.0,
                                 lr=+1.0, pivot=s18["pivot"])
    print("-- G4. hub18 tangent tray, pre-seated launch check, 60rpm sign=+1 --", flush=True)
    res["G4_hub18_seated"] = go("G4", g18, 60.0, 89.0, BN, BN_MASS, 64.0,
                                lr=+1.0, sec=8.0, seated=True, pivot=s18["pivot"])

    thin = {k: ({kk: vv for kk, vv in v.items() if kk != "_trace"}
                if isinstance(v, dict) and "launched" in v else v) for k, v in res.items()}
    OUT.joinpath("_r23_nectar_gravity.json").write_text(
        json.dumps(thin, ensure_ascii=False, indent=1), encoding="utf-8")
    print("saved", OUT / "_r23_nectar_gravity.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
