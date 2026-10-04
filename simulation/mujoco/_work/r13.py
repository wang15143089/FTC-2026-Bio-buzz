# -*- coding: utf-8 -*-
"""R13: how much carry radius does the NECTAR ball need?

NECTAR R=45.974.  The paddle hub radius is 18 mm, so the ball centre must sit
at r >= 18 + 45.974 = 63.97 mm or the hub punches into the ball (R12 jam=98%).
Shell inner radius is R_CARRY + ball R for each ball.
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


def main():
    res = {}
    g = R10.make_geom(56.0, 292.0)
    print("=== R13 NECTAR carry-radius ladder, ball pre-seated, sign=+1 (CCW) ===")
    print("  (POLLEN control: r_in=93.96, R_CARRY=58.4)")
    res["pollen_ctrl"] = r12.run("POLLEN ctrl", g, sign=+1.0, sec=3.0)
    for r_carry in (64.0, 66.0, 70.0, 76.0):
        r_in = r_carry + BN
        bz = pv2.PADDLE_CZ - r_carry
        print("  -- NECTAR R_CARRY=%.2f  r_in=%.2f --" % (r_carry, r_in))
        res["nectar_%.0f" % r_carry] = r12.run(
            "NECTAR %.0f" % r_carry, g, sign=+1.0, sec=3.0,
            bx=pv2.PADDLE_CX, bz=bz, ball_r=BN, r_in=r_in)
    print("  -- NECTAR R_CARRY=66, sign=-1 (CW) for comparison --")
    res["nectar_66_cw"] = r12.run("NECTAR 66 -1", g, sign=-1.0, sec=3.0,
                                  bx=pv2.PADDLE_CX, bz=pv2.PADDLE_CZ - 66.0,
                                  ball_r=BN, r_in=66.0 + BN)
    OUT.joinpath("_r13_nectar.json").write_text(
        json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "_trace"}
                    for k, v in res.items()}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    print("saved", OUT / "_r13_nectar.json")


if __name__ == "__main__":
    main()
