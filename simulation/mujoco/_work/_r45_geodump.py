# -*- coding: utf-8 -*-
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import mujoco, r37_multiball as R
MM = R.MM
R.TRAY_X1 = 460.0
m, d, aid, jid, meta, w, xml = R.build_multi(["NECTAR"], 0.0, 82)
qp = m.jnt_qposadr[jid]
for P in (53.3, 185.0):
    d.qpos[qp] = math.radians(P); mujoco.mj_forward(m, d)
    print("=== J=%.1f  pivot body xpos=%s" % (P, d.xpos[m.body_parentid[0]]))
    for g in range(m.ngeom):
        nm = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, g) or ""
        if nm.startswith("paddle") or nm.startswith("r10_2") or nm.startswith("shell_lip"):
            print("   %-18s type=%s size=%s world xpos=(%.1f, %.1f, %.1f)"
                  % (nm, m.geom_type[g], m.geom_size[g][:3], *(d.geom_xpos[g] * 1000)))
