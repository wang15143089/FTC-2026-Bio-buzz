# -*- coding: utf-8 -*-
"""R17: why does the NECTAR ball not feed?  Servo model vs geometry.

R16-B showed the NECTAR ball (R 45.974) oscillating on the tray and never
reaching the nest.  Two candidate causes:
  (1) servo model -- a velocity actuator gives torque = kv*(w_cmd - w), so at a
      low commanded speed the available torque is only kv*w_cmd (0.11 N.m at
      60 rpm), far below the 0.53 N.m stall.  A real servo keeps pushing to its
      torque limit.  "torque-authority" below sets kv = T_STALL/w_cmd so the
      full 0.53 N.m is available at any commanded speed.
  (2) geometry -- R_CARRY=64 is exactly the hub contact radius (18 + 45.974),
      so the ball rides on the hub; the lip angle may be too short to capture it.
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


def go(tag, geom, rpm, model, lr=+1.0, mu=0.40, sec=20.0, ball_r=None,
       ball_m=None, r_in=None, r_carry=None, bz=None, bx=145.0):
    old = (r12.N_FREE, r12.OMEGA, r12.KV, pv2.R_CARRY)
    w = rpm * 2 * math.pi / 60.0
    r12.N_FREE, r12.OMEGA = rpm, w
    r12.KV = T_STALL / w if model == "ta" else T_STALL / (290.0 * 2 * math.pi / 60.0)
    if r_carry is not None:
        pv2.R_CARRY = r_carry
    if bz is None:
        bz = pv2.tray_top_z(bx) + (ball_r if ball_r else pv2.BALL_R)
    try:
        return r12.run("%s %s %.0f" % (tag, model, rpm), geom, sign=lr, mu=mu,
                       bx=bx, bz=bz, sec=sec, ball_r=ball_r, ball_m=ball_m,
                       r_in=r_in, detail=1.0, quiet=False)
    finally:
        r12.N_FREE, r12.OMEGA, r12.KV, pv2.R_CARRY = old


def main():
    res = {}
    print("=== R17 NECTAR feed: servo model x speed ===", flush=True)
    for lip in (300.0, 330.0):
        for rpm in (60.0, 150.0, 290.0):
            for model in ("lin", "ta"):
                g = R10.make_geom(73.0, lip)
                key = "lip%g_rpm%g_%s" % (lip, rpm, model)
                res[key] = go("N", g, rpm, model, sec=20.0, ball_r=BN,
                              ball_m=0.130, r_in=64.0 + BN, r_carry=64.0)
    print("=== control: POLLEN at 290 rpm, torque-authority ===", flush=True)
    gP = R10.make_geom(56.0, 292.0)
    res["pollen_290_ta"] = go("P", gP, 290.0, "ta", sec=12.0)
    thin = {k: {kk: vv for kk, vv in v.items() if kk != "_trace"} for k, v in res.items()}
    OUT.joinpath("_r17_nectar_servo.json").write_text(
        json.dumps(thin, ensure_ascii=False, indent=1), encoding="utf-8")
    print("saved", OUT / "_r17_nectar_servo.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
