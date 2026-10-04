import json, math, sys, importlib.util
sys.stdout.reconfigure(encoding="utf-8")
import mujoco, numpy as np
spec = importlib.util.spec_from_file_location("pv2", r"simulation/mujoco/pollen_v2_sim.py")
pv2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(pv2)
bz = pv2.tray_top_z(145.0)+pv2.BALL_R
xml,ctrl = pv2.build_xml(1620.0,-1,0.0,145.0,bz)
m=mujoco.MjModel.from_xml_string(xml); d=mujoco.MjData(m); d.ctrl[:]=ctrl; mujoco.mj_forward(m,d)
bid=mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_BODY,"ball")
for i in range(int(2.0/m.opt.timestep)):
    mujoco.mj_step(m,d)
print("球心 = (%.2f, %.2f)  r=%.2f  ang=%.2f"%(d.xpos[bid][0]*1000,d.xpos[bid][2]*1000,
    math.hypot(d.xpos[bid][0]*1000-pv2.PADDLE_CX, d.xpos[bid][2]*1000-pv2.PADDLE_CZ),
    math.degrees(math.atan2(d.xpos[bid][2]*1000-pv2.PADDLE_CZ, d.xpos[bid][0]*1000-pv2.PADDLE_CX))%360))
names={}
for c in range(d.ncon):
    con=d.contact[c]
    g1,g2=con.geom1,con.geom2
    if g1==mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_GEOM,"ball_geom") or g2==mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_GEOM,"ball_geom"):
        n1=mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_GEOM,g1); n2=mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_GEOM,g2)
        print("  接触: %s <-> %s   dist=%.4f  normal=(%.3f,%.3f,%.3f)"%(n1,n2,con.dist,*con.frame[0:3]))
        names[n2 if n1=="ball_geom" else n1]=con.dist
print("接触对:", names)
