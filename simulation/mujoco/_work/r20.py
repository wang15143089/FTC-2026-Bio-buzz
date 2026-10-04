# -*- coding: utf-8 -*-
"""R20: NECTAR ball fed into the NECTAR flywheel gap (82 mm), not the POLLEN 64 mm.

Every earlier NECTAR run (R13..R19) inherited pollen_v2_sim.HALF_SPACING = 80.0,
i.e. a 64 mm nip.  A 91.948 mm ball can never pass that, so launch=False was a
model artefact, not a design verdict.  HALF_SPACING = 89.0 -> nip 82 mm, which
is the nectar configuration of the accepted constrained launcher
(half_axle_spacing_mm = 89.0, nominal_flywheel_gap_mm = 82.0).
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
POLLEN_R = 35.56


def go(tag, geom, rpm, half, ball_r, ball_m, r_carry, lr=+1.0, mu=0.40,
       sec=25.0, bz=None, bx=145.0):
    old_half = pv2.HALF_SPACING
    old = (r12.N_FREE, r12.OMEGA, r12.KV, pv2.R_CARRY)
    w = rpm * 2 * math.pi / 60.0
    pv2.HALF_SPACING = half
    r12.N_FREE, r12.OMEGA = rpm, w
    r12.KV = T_STALL / w
    pv2.R_CARRY = r_carry
    if bz is None:
        bz = pv2.tray_top_z(bx) + ball_r
    try:
        return r12.run("%s %g/%.0f" % (tag, half, rpm), geom, sign=lr, mu=mu,
                       bx=bx, bz=bz, sec=sec, ball_r=ball_r, ball_m=ball_m,
                       r_in=r_carry + ball_r, detail=1.0, quiet=False)
    finally:
        pv2.HALF_SPACING = old_half
        r12.N_FREE, r12.OMEGA, r12.KV, pv2.R_CARRY = old


def main():
    res = {}
    print("=== R20 NECTAR feed with the nectar nip (82 mm, HALF=89) ===", flush=True)

    print("-- A. POLLEN control: half=80 cut=56 lip=292 R_CARRY=58.4, 60 rpm --", flush=True)
    res["A_pollen_ctrl"] = go("P", R10.make_geom(56.0, 292.0), 60.0, 80.0,
                              POLLEN_R, 0.060, 58.4)

    print("-- B. NECTAR half=89 cut=84 lip=300 R_CARRY=64, 60 rpm --", flush=True)
    res["B_nectar_84_60"] = go("N", R10.make_geom(84.0, 300.0), 60.0, 89.0, BN, BN_MASS, 64.0)

    print("-- C. NECTAR half=89 cut=73 lip=300, 60 rpm --", flush=True)
    res["C_nectar_73_60"] = go("N", R10.make_geom(73.0, 300.0), 60.0, 89.0, BN, BN_MASS, 64.0)

    print("-- D. NECTAR half=89 cut=92 lip=300, 60 rpm --", flush=True)
    res["D_nectar_92_60"] = go("N", R10.make_geom(92.0, 300.0), 60.0, 89.0, BN, BN_MASS, 64.0)

    print("-- E. NECTAR half=89 cut=84 lip=300, 120 rpm --", flush=True)
    res["E_nectar_84_120"] = go("N", R10.make_geom(84.0, 300.0), 120.0, 89.0, BN, BN_MASS, 64.0)

    print("-- F. NECTAR half=80 (pollen nip 64) cut=84, 60 rpm --", flush=True)
    res["F_nectar_nip64"] = go("N", R10.make_geom(84.0, 300.0), 60.0, 80.0, BN, BN_MASS, 64.0)

    thin = {k: {kk: vv for kk, vv in v.items() if kk != "_trace"} for k, v in res.items()}
    OUT.joinpath("_r20_nectar_nip82.json").write_text(
        json.dumps(thin, ensure_ascii=False, indent=1), encoding="utf-8")
    print("saved", OUT / "_r20_nectar_nip82.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
