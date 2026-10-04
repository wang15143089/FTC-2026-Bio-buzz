# -*- coding: utf-8 -*-
"""R21: shrink the paddle hub so the NECTAR ball can ride the POLLEN carry circle.

R20 showed the nectar nip (82 mm) is NOT the blocker: the ball never leaves the
tray, because the blade pushes it uphill.  Root cause: a 91.948 mm ball must keep
its centre at r >= r_hub + 45.974 to clear the 36 mm OD paddle hub, i.e. 63.97 mm
with the present hub.  At that radius the 5 deg tray is no longer tangent to the
carry circle anywhere the ball can reach, so the handoff geometry that makes the
a' recipe work for POLLEN (cut = 56 mm = tangency of the r = 58.4 circle with the
tray) simply does not exist.

Fix: reduce the paddle hub OD from 36 mm (r = 18) to 24 mm (r = 12).  Then the
nectar floor is 12 + 45.974 = 57.97 mm, so R_CARRY = 58.4 -- the POLLEN value --
and the whole a' handoff (TRAY_X0 = 56, A_LIP = 292, blade/flex tips) is reused
unchanged.  This is a printed rotor part, not the launcher, so the launch half of
T06 is untouched.
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
       sec=20.0, seated=False, bx=None, bz=None):
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
    print("=== R21 NECTAR: shrink the paddle hub 18 -> 12 mm ===", flush=True)

    print("-- P1. pre-seated NECTAR, hub18 R_CARRY=64, nip82, CCW (launch only) --", flush=True)
    g_old = (lambda: R10.stat(56.0, 292.0), parts_hub(18.0))
    res["P1_seated_hub18_r64"] = go("P1", g_old, 60.0, 89.0, BN, BN_MASS, 64.0,
                                    lr=+1.0, sec=6.0, seated=True)

    print("-- P2. pre-seated NECTAR, hub12 R_CARRY=58.4, nip82, CCW (launch only) --", flush=True)
    g_new = (lambda: R10.stat(56.0, 292.0), parts_hub(12.0))
    res["P2_seated_hub12_r58"] = go("P2", g_new, 60.0, 89.0, BN, BN_MASS, 58.4,
                                    lr=+1.0, sec=6.0, seated=True)

    print("-- F1. feed NECTAR, hub12 R_CARRY=58.4 cut=56 lip=292 nip82, 60 rpm CCW --", flush=True)
    res["F1_feed_hub12_ccw"] = go("F1", g_new, 60.0, 89.0, BN, BN_MASS, 58.4,
                                  lr=+1.0, sec=25.0)

    print("-- F2. feed NECTAR, same but CW --", flush=True)
    res["F2_feed_hub12_cw"] = go("F2", g_new, 60.0, 89.0, BN, BN_MASS, 58.4,
                                 lr=-1.0, sec=25.0)

    print("-- F3. feed NECTAR, hub12 but pollen nip (64) --", flush=True)
    res["F3_feed_hub12_nip64"] = go("F3", g_new, 60.0, 80.0, BN, BN_MASS, 58.4,
                                    lr=+1.0, sec=25.0)

    thin = {k: {kk: vv for kk, vv in v.items() if kk != "_trace"} for k, v in res.items()}
    OUT.joinpath("_r21_nectar_hub12.json").write_text(
        json.dumps(thin, ensure_ascii=False, indent=1), encoding="utf-8")
    print("saved", OUT / "_r21_nectar_hub12.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
