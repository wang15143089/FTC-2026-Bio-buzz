# -*- coding: utf-8 -*-
"""R9 probe: where does the ball really rest, and which paddle geoms touch it."""
import math, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import r6_smooth as r6
import opt_lib as ol
import mujoco, numpy as np

pv2 = ol.pv2
BASE = ol.GEOM["D 球窝抬高6.8"][0]
pv2.static_geoms = BASE

xml, ctrl = pv2.build_xml(0.0, -1, 0.0, 20.9, pv2.tray_top_z(20.9) + pv2.BALL_R)
m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
for i in range(int(2.0 / m.opt.timestep)):
    mujoco.mj_step(m, d)
bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
p = d.xpos[bid] * 1000.0
rx, rz = p[0] - pv2.PADDLE_CX, p[2] - pv2.PADDLE_CZ
print("ball rest mm x=%.2f z=%.2f  r_from_paddle=%.2f  ang=%.2f deg"
      % (p[0], p[2], math.hypot(rx, rz), math.degrees(math.atan2(rz, rx)) % 360))
print("ball gap to shell wall = %.2f mm (should be ~0)"
      % (pv2.R_IN - math.hypot(rx, rz) - pv2.BALL_R))
print()
print("--- paddle geoms: ball-centre distance (mujoco mj_geomDistance) ---")
bg = [g for g in range(m.ngeom) if m.geom_bodyid[g] == bid]
for g in range(m.ngeom):
    nm = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, g)
    if not nm or not nm.startswith("paddle_") or nm.startswith("paddle_joint"):
        continue
    dmin = 1e9; best = None
    for b in bg:
        try:
            dd = mujoco.mj_geomDistance(m, d, g, b, 0.5, None)
        except Exception:
            dd = float("nan")
        if dd < dmin:
            dmin, best = dd, b
    print("  %-16s min_dist_to_ball_surface = %7.2f mm" % (nm, dmin * 1000.0))
print()
print("--- active contacts ---")
for i in range(d.ncon):
    c = d.contact[i]
    n1 = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, c.geom1) or "?"
    n2 = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, c.geom2) or "?"
    f = np.zeros(6); mujoco.mj_contactForce(m, d, i, f)
    if "ball" in n1 or "ball" in n2:
        print("  %-16s | %-16s dist=%7.3f mm  |F|=%6.2f N  Fn=%6.2f N"
              % (n1, n2, c.dist * 1000.0, np.linalg.norm(f[:3]), abs(f[0])))
