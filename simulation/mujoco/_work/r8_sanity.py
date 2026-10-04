# -*- coding: utf-8 -*-
import mujoco, numpy as np
xml = """
<mujoco><option timestep="0.0002" gravity="0 0 -9.81" integrator="implicitfast"/>
<default><geom friction="0.5 0.01 0.0001" solref="0.010 1" solimp="0.9 0.95 0.002"/></default>
<worldbody>
  <geom name="floor" type="plane" size="1 1 0.1"/>
  <body name="ball" pos="0 0 0.03556"><freejoint/><geom name="bg" type="sphere" size="0.03556" mass="0.06"/></body>
</worldbody></mujoco>"""
m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
for i in range(20000):
    mujoco.mj_step(m, d)
print("z =", round(float(d.xpos[bid][2]), 6), " (rest z should be 0.03556)")
print("vz =", round(float(d.cvel[bid][5]), 6))
print("cacc =", [round(float(x), 4) for x in d.cacc[bid][0:3]])
tot = 0.0
for k in range(d.ncon):
    ff = np.zeros(6); mujoco.mj_contactForce(m, d, k, ff)
    nm1 = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, d.contact[k].geom1)
    nm2 = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, d.contact[k].geom2)
    print("  contact", nm1, nm2, "dist=", round(float(d.contact[k].dist), 6), "Fn=", round(float(ff[0]), 4))
    tot += abs(ff[0])
print("sum |Fn| =", round(tot, 4), "  ball weight =", round(0.06 * 9.81, 4))
