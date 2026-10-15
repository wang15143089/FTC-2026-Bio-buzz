# -*- coding: utf-8 -*-
"""R56 步骤1：托板加长量选择（纯解析，不建 CAD）+ 现有件 H2D 尺寸清单。"""
import json, math, sys
sys.path.insert(0, "cad")
import paddle_launcher_feeder_a_prime_shared as SH
import paddle_launcher_feeder_a_prime_shared_staging as ST

F = SH.F
print("PADDLE_CX/CZ", F.PADDLE_CX, F.PADDLE_CZ, "TILT", F.TILT_DEG,
      "TRAY_T", F.TRAY_T, "FEEDER_W", F.FEEDER_W)
print("CUT_X(切点x)", round(SH.CUT_X, 3), "TRAY_X0", round(F.TRAY_X0, 3),
      "TRAY_X1", F.TRAY_X1)
print("tray_top_z(215)", round(F.PIVOT_Z + (215 - F.PIVOT_X) * math.tan(math.radians(F.TILT_DEG)), 3))
print("ball_r pollen", SH.VARIANTS["pollen"]["ball_r"], "nectar", round(SH.VARIANTS["nectar"]["ball_r"], 3))

def cap(x1, ball_r):
    ST.STAGE_X1 = x1
    tr = ST.ball_centre_track(ball_r)
    return tr

for x1 in (215.0, 240.0, 260.0, 270.0, 275.0, 280.0, 285.0, 300.0, 310.0, 320.0, 356.0):
    for name in ("pollen", "nectar"):
        br = SH.VARIANTS[name]["ball_r"]
        tr = cap(x1, br)
        last = tr[-1][0] + br
        print("TRAY_X1=%6.1f %-6s n=%d  last_ball_surface_x=%7.2f  (%s)" % (
            x1, name, len(tr), last, "OK" if last <= x1 + 1e-6 else "OVER"))
