# -*- coding: utf-8 -*-
import math, sys, importlib.util
sys.stdout.reconfigure(encoding="utf-8")
import mujoco
spec = importlib.util.spec_from_file_location("ol", r"simulation/mujoco/_work/opt_lib.py")
ol = importlib.util.module_from_spec(spec); spec.loader.exec_module(ol)
pv2 = ol.pv2; W = pv2.PADDLE_W
def blades(angs):
    def f():
        parts = [("hub", (0.0,0.0,0.0), (18.0,17.0,18.0), 0.0, "cylY")]
        for i, a in enumerate(angs, 1):
            parts.append(("arm_%d"%i,   (30.0,0.0,0.0), (16.0, 9.0, 5.0), a, "box"))
            parts.append(("blade_%d"%i, (52.0,0.0,0.0), (6.0, W/2.0, 15.0), a, "box"))
            parts.append(("flex_%d"%i,  (58.0,0.0,0.0), (2.0, W/2.0, 17.0), a, "box"))
        return parts
    return f
ol.GEOM["R2"] = (ol.GEOM["A 唇口喇叭"][0], blades([10.0, 190.0]))
names = {}
for name in ("V0 现状", "R2"):
    ol.apply_geom(name)
    xml, ctrl = pv2.build_xml(1620.0, -1, 1.0*2*math.pi/60.0, 145.0, pv2.tray_top_z(145.0)+pv2.BALL_R)
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
    for _ in range(int(8.0/m.opt.timestep)): mujoco.mj_step(m, d)
    bg = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, "ball_geom")
    for i in range(m.ngeom):
        names[i] = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, i)
    print("==", name, " ball x,z =", round(float(d.geom_xpos[bg][0])*1000,2), round(float(d.geom_xpos[bg][2])*1000,2))
    for c in d.contact:
        if bg in (c.geom1, c.geom2):
            print("    触点: %-16s %-16s dist=%8.4f mm" % (names[c.geom1], names[c.geom2], c.dist*1000))
