import json, math, sys
from pathlib import Path
sys.path.insert(0, str(Path("cad").resolve()))
import cadquery as cq
import paddle_launcher_feeder_a_prime_nectar as N

F = N.F
r_in = F.R_CARRY + F.BALL_R
r_out = r_in + F.SHELL_WALL
def pol(r, a):
    return (F.PADDLE_CX + r*math.cos(math.radians(a)),
            F.PADDLE_CZ + r*math.sin(math.radians(a)))

pts_x = [pol(r, a)[0] for r in (r_in, r_out) for a in (F.A_LIP, F.A_EXIT, 180.0, 208.5)]
pts_z = [pol(r, a)[1] for r in (r_in, r_out) for a in (F.A_LIP, F.A_EXIT, 208.5, 270.0)]
print(json.dumps({
    "PADDLE_CX": F.PADDLE_CX, "PADDLE_CZ": F.PADDLE_CZ,
    "FEEDER_W": F.FEEDER_W, "TRAY_T": F.TRAY_T, "TRAY_X1": F.TRAY_X1,
    "TRAY_X0": F.TRAY_X0, "A_EXIT": F.A_EXIT, "A_LIP": F.A_LIP,
    "TILT_DEG": F.TILT_DEG, "PIVOT": [F.PIVOT_X, F.PIVOT_Z],
    "r_in": r_in, "r_out": r_out,
    "tray_top_z_TRAY_X1": F._tray_top_z(F.TRAY_X1),
    "tray_top_z_TRAY_X0": F._tray_top_z(F.TRAY_X0),
    "shell_min_x": min(pts_x), "shell_max_x": max(pts_x),
    "shell_min_z": min(pts_z), "shell_max_z": max(pts_z),
    "hub_d": 2.0*N.HUB_R, "hub_len": 34.0,
}, indent=2))
