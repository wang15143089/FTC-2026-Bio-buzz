# -*- coding: utf-8 -*-
"""R26: full feed->launch with the CAD-true 2-blade paddle, clean start, both balls."""
import math, sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import opt_lib as ol
import r10_cradle as R10
import r23, r12
import numpy as np

pv2 = ol.pv2
OUT = Path("simulation/mujoco/out")
R_IN = 107.974; CUT_X = 38.901; A_LIP = 275.0; PIVOT = (-0.806, 0.423)
TRAY_X1 = 150.0; TILT = 5.0; WHEEL_R = 48.0
SIN_T = math.sin(math.radians(TILT)); COS_T = math.cos(math.radians(TILT))

def start(xc, ball_r):
    return xc - ball_r*SIN_T, pv2.tray_top_z(xc) + ball_r*COS_T

def go(tag, ball_r, ball_m, nip, xc, rpm=60.0, sec=20.0, mu=0.40, paddle=None):
    pv2.HALF_SPACING = nip/2.0 + WHEEL_R
    pv2.R_CARRY = R_IN - ball_r
    pv2.PIVOT_X, pv2.PIVOT_Z = PIVOT
    g = (lambda: R10.stat(CUT_X, A_LIP, tray_x1=TRAY_X1),
         paddle or r23.parts_hub(12.0))
    bx, bz = start(xc, ball_r)
    print("--- %s  start=(%.2f, %.2f) r_carry=%.2f ---" % (tag, bx, bz, R_IN-ball_r), flush=True)
    return r12.run(tag, g, sign=+1.0, mu=mu, bx=bx, bz=bz, sec=sec,
                   ball_r=ball_r, ball_m=ball_m, r_in=R_IN, detail=1.0, quiet=False)

res = {}
N = dict(ball_r=45.974, ball_m=0.130, nip=82.0)
P = dict(ball_r=35.56, ball_m=0.060, nip=64.0)
print("=== R26 NECTAR r=45.974, nip 82, CAD 2-blade paddle @18deg, 60 rpm sign=+1 ===", flush=True)
res["nectar_60"] = go("N60", **N, xc=96.0)
print(flush=True)
print("=== R26 POLLEN r=35.56, nip 64, same paddle/shell, 60 rpm sign=+1 ===", flush=True)
res["pollen_60"] = go("P60", **P, xc=104.0)
thin = {}
for k, v in res.items():
    thin[k] = {kk: vv for kk, vv in v.items() if kk != "_trace"}
out = OUT/"_r26_cad2blade.json"
out.write_text(json.dumps(thin, ensure_ascii=False, indent=1), encoding="utf-8")
print("saved", out, flush=True)
