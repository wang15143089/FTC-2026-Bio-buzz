# -*- coding: utf-8 -*-
"""R18: NECTAR feed with a LONGER blade.

R17 showed that every servo model fails to feed the NECTAR ball at R_CARRY=64,
because the blade tip only reaches r=60 while the ball centre rides at r=64:
the blade can only stroke the ball's inner surface and the ball slides back down
the 5 deg tray.  Here the blade is extended (blade_low tip=64/70/78) so the tip
passes beyond the ball centre circle and scoops it.
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
T_STALL = 0.530


def go(tag, geom, rpm, lr=+1.0, mu=0.40, sec=20.0, ball_r=None, ball_m=None,
       r_in=None, r_carry=None, bz=None, bx=145.0):
    old = (r12.N_FREE, r12.OMEGA, r12.KV, pv2.R_CARRY)
    w = rpm * 2 * math.pi / 60.0
    r12.N_FREE, r12.OMEGA = rpm, w
    r12.KV = T_STALL / w
    if r_carry is not None:
        pv2.R_CARRY = r_carry
    if bz is None:
        bz = pv2.tray_top_z(bx) + (ball_r if ball_r else pv2.BALL_R)
    try:
        return r12.run("%s %.0f" % (tag, rpm), geom, sign=lr, mu=mu, bx=bx, bz=bz,
                       sec=sec, ball_r=ball_r, ball_m=ball_m, r_in=r_in,
                       detail=1.0, quiet=False)
    finally:
        r12.N_FREE, r12.OMEGA, r12.KV, pv2.R_CARRY = old


def main():
    res = {}
    print("=== R18 NECTAR, longer blade, R_CARRY=64, cut=73 lip=300 ===", flush=True)
    for tip in (64.0, 70.0, 78.0):
        parts = ol.blade_low(ol.ORIG_PARTS, tip)
        g = (lambda cx, lp: (lambda: R10.stat(cx, lp)), 73.0, 300.0)
        g = (lambda cx=73.0, lp=300.0: R10.stat(cx, lp), parts)
        for rpm in (60.0, 150.0):
            res["tip%g_rpm%g" % (tip, rpm)] = go(
                "N tip%.0f" % tip, g, rpm, sec=20.0, ball_r=BN, ball_m=0.130,
                r_in=64.0 + BN, r_carry=64.0)
    thin = {k: {kk: vv for kk, vv in v.items() if kk != "_trace"} for k, v in res.items()}
    OUT.joinpath("_r18_nectar_blade.json").write_text(
        json.dumps(thin, ensure_ascii=False, indent=1), encoding="utf-8")
    print("saved", OUT / "_r18_nectar_blade.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
