# -*- coding: utf-8 -*-
"""R19: NECTAR feed -- fix the tray cut, not the blade.

R17/R18 ruled out blade reach (a longer blade jams even harder).  The wedge is
at r = 18 + 45.974 = 63.97: the ball cannot get closer to the axis than the hub
radius, so wherever the tray still exists below r=64 the ball is pinned between
tray and hub.
The tray must therefore END before the resting ball's centre radius falls to 64
(contact-x about 83.6), i.e. cut_x ~ 84..92 instead of 73.
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


def go(tag, geom, rpm, lr=+1.0, mu=0.40, sec=25.0, ball_r=None, ball_m=None,
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
    print("=== R19 NECTAR, tray cut moved past the hub tangency ===", flush=True)
    for cut, lip, rpm in ((84.0, 300.0, 60.0), (92.0, 300.0, 60.0),
                          (92.0, 330.0, 60.0), (92.0, 300.0, 120.0)):
        g = R10.make_geom(cut, lip)
        key = "cut%g_lip%g_rpm%g" % (cut, lip, rpm)
        res[key] = go("N", g, rpm, sec=25.0, ball_r=BN, ball_m=0.130,
                      r_in=64.0 + BN, r_carry=64.0)
    thin = {k: {kk: vv for kk, vv in v.items() if kk != "_trace"} for k, v in res.items()}
    OUT.joinpath("_r19_nectar_traycut.json").write_text(
        json.dumps(thin, ensure_ascii=False, indent=1), encoding="utf-8")
    print("saved", OUT / "_r19_nectar_traycut.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
