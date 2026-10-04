# -*- coding: utf-8 -*-
import importlib.util, math, sys, time
sys.stdout.reconfigure(encoding="utf-8")
import mujoco, numpy as np
spec = importlib.util.spec_from_file_location("pv2", r"simulation/mujoco/pollen_v2_sim.py")
pv2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(pv2)
xml, ctrl = pv2.build_xml(1620.0, -1, 200.0*2*math.pi/60.0, 145.0, pv2.tray_top_z(145.0)+pv2.BALL_R)
xml = xml.replace('-1.5 1.5"', '-0.8 0.8"')
t0=time.time()
m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
d.ctrl[:]=ctrl; mujoco.mj_forward(m,d)
dt=m.opt.timestep; n=int(round(7.0/dt))
for i in range(n):
    mujoco.mj_step(m,d)
print("n steps", n, "elapsed %.2f s"%(time.time()-t0), "-> %.0f steps/s"%(n/(time.time()-t0)))
