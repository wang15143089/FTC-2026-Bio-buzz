# -*- coding: utf-8 -*-
"""R14: can a LOW paddle speed walk the ball from the tray into the nest?

R11 showed 290 rpm just batters the ball (it bounces between x=104..152).
A 25-4 Super Speed servo is a velocity servo, so a slower command is available.
Here the ball starts on the tray at x=145 and we sweep the paddle speed.
Success criterion: min_r <= 62 (ball reaches the carry circle r=58.4).
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


def run_rpm(tag, geom, rpm, sign=+1.0, mu=0.40, bx=145.0, sec=15.0):
    old_n, old_o = r12.N_FREE, r12.OMEGA
    r12.N_FREE, r12.OMEGA = rpm, rpm * 2 * math.pi / 60.0
    try:
        return r12.run(tag, geom, sign=sign, mu=mu, bx=bx, sec=sec,
                       detail=1.0, quiet=False)
    finally:
        r12.N_FREE, r12.OMEGA = old_n, old_o


def main():
    res = {}
    g = R10.make_geom(56.0, 292.0)
    print("=== R14 slow-feed sweep, R10 cradle (cut=56, lip=292), POLLEN, mu=0.40 ===")
    print("=== ball starts on tray x=145, paddle CCW (sign=+1), 15 s ===")
    for rpm in (20.0, 40.0, 60.0, 90.0):
        print("  -- paddle %.0f rpm --" % rpm)
        res["rpm%.0f" % rpm] = run_rpm("CCW %.0f" % rpm, g, rpm, sign=+1.0)
    OUT.joinpath("_r14_slowfeed.json").write_text(
        json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "_trace"}
                    for k, v in res.items()}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    print("saved", OUT / "_r14_slowfeed.json")


if __name__ == "__main__":
    main()
