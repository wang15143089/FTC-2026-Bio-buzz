# -*- coding: utf-8 -*-
"""R15: NECTAR ball with the shell end-face radius kept consistent with the ball.

R13 was invalid: r10_cradle.R_MID was frozen at import time (97.46 mm), so for
the bigger shell the exit end face sat 18 mm inside the ball path and jammed it.
Here R_MID follows R_IN, the tray is cut at the true tangency point for each
carry radius, and the shell lip angle is set to cover that tangency.
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
    print("=== R15 NECTAR, corrected end-face radius, ball pre-seated, sign=+1 ===")
    gP = R10.make_geom(56.0, 292.0)
    res["pollen_ctrl"] = r12.run("POLLEN ctrl", gP, sign=+1.0, sec=3.0, r_in=93.96)
    for r_carry, cut, lip in ((64.0, 79.0, 320.0), (66.0, 81.0, 322.0), (70.0, 86.0, 325.0)):
        r_in = r_carry + BN
        gN = R10.make_geom(cut, lip)
        bz = pv2.PADDLE_CZ - r_carry
        print("  -- NECTAR R_CARRY=%.1f r_in=%.2f tray_x0=%.1f lip=%.0f --"
              % (r_carry, r_in, cut, lip))
        res["nectar_%.0f" % r_carry] = r12.run(
            "NECTAR %.0f" % r_carry, gN, sign=+1.0, sec=4.0,
            bx=pv2.PADDLE_CX, bz=bz, ball_r=BN, r_in=r_in)
    print("  -- NECTAR R_CARRY=66, sign=-1 (CW) --")
    gN = R10.make_geom(81.0, 322.0)
    res["nectar_66_cw"] = r12.run("NECTAR 66 -1", gN, sign=-1.0, sec=4.0,
                                  bx=pv2.PADDLE_CX, bz=pv2.PADDLE_CZ - 66.0,
                                  ball_r=BN, r_in=66.0 + BN)
    OUT.joinpath("_r15_nectar.json").write_text(
        json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "_trace"}
                    for k, v in res.items()}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    print("saved", OUT / "_r15_nectar.json")


if __name__ == "__main__":
    main()
