# -*- coding: utf-8 -*-
"""R16: a' cradle with the NECTAR ball (D=91.948).

Winning recipe from R14: a' geometry + SLOW paddle (60 rpm) + mu 0.40.
New: the NECTAR ball needs R_CARRY >= 18 + 45.974 = 63.97 mm to clear the
paddle hub, so the carry circle (and therefore the shell inner arc) grows.
The tray cut is moved to the point where the tray end face clears the resting
ball by ~4 mm.

Runs:
  A. POLLEN control, a' cut=56 lip=292, 60 rpm  -> must reproduce R14 launch
  B. NECTAR R_CARRY=64, r_in=109.97, cut=73, lip=300, 60 rpm
  C. NECTAR R_CARRY=64, same, 20 rpm (creep check)
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
BM_NECTAR = 0.130          # kg, ASSUMED (volume-scaled from the 0.060 kg POLLEN)


def run_rpm(tag, geom, rpm, sign=+1.0, mu=0.40, bx=145.0, bz=None, sec=20.0,
            ball_r=None, ball_m=None, r_in=None, r_carry=None, quiet=False):
    old_n, old_o = r12.N_FREE, r12.OMEGA
    old_c = pv2.R_CARRY
    r12.N_FREE, r12.OMEGA = rpm, rpm * 2 * math.pi / 60.0
    if r_carry is not None:
        pv2.R_CARRY = r_carry
    if bz is None:
        bz = pv2.tray_top_z(bx) + (ball_r if ball_r else pv2.BALL_R)
    try:
        return r12.run(tag, geom, sign=sign, mu=mu, bx=bx, bz=bz, sec=sec,
                       ball_r=ball_r, ball_m=ball_m, r_in=r_in,
                       detail=1.0, quiet=quiet)
    finally:
        r12.N_FREE, r12.OMEGA = old_n, old_o
        pv2.R_CARRY = old_c


def main():
    res = {}
    print("=== R16 a' cradle, slow feed (R14 recipe) ===", flush=True)

    print("-- A. POLLEN control: cut=56 lip=292 R_CARRY=58.4, 60 rpm --", flush=True)
    gP = R10.make_geom(56.0, 292.0)
    res["A_pollen_ctrl"] = run_rpm("POLLEN 60rpm", gP, 60.0, sign=+1.0, sec=20.0)

    print("-- B. NECTAR: cut=73 lip=300 R_CARRY=64.0 r_in=109.97, 60 rpm --", flush=True)
    gN = R10.make_geom(73.0, 300.0)
    res["B_nectar_60rpm"] = run_rpm(
        "NECTAR 60rpm", gN, 60.0, sign=+1.0, sec=20.0, bx=145.0,
        ball_r=BN, ball_m=BM_NECTAR, r_in=64.0 + BN, r_carry=64.0)

    print("-- C. NECTAR same geometry, 20 rpm --", flush=True)
    gN2 = R10.make_geom(73.0, 300.0)
    res["C_nectar_20rpm"] = run_rpm(
        "NECTAR 20rpm", gN2, 20.0, sign=+1.0, sec=30.0, bx=145.0,
        ball_r=BN, ball_m=BM_NECTAR, r_in=64.0 + BN, r_carry=64.0)

    thin = {k: {kk: vv for kk, vv in v.items() if kk != "_trace"} for k, v in res.items()}
    OUT.joinpath("_r16_nectar_feed.json").write_text(
        json.dumps(thin, ensure_ascii=False, indent=1), encoding="utf-8")
    print("saved", OUT / "_r16_nectar_feed.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
