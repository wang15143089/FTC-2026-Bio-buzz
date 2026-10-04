import json, math, sys, importlib.util
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
import mujoco, numpy as np
spec = importlib.util.spec_from_file_location("pv2", r"simulation/mujoco/pollen_v2_sim.py")
pv2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(pv2)

def run_phase(bx,bz,rpm,phase_deg,sec=6.0):
    xml,ctrl = pv2.build_xml(1620.0,-1,rpm*2*math.pi/60.0,bx,bz)
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    jid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "paddle_joint")
    d.qpos[jid] = math.radians(phase_deg)
    d.ctrl[:] = ctrl; mujoco.mj_forward(m,d)
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    dt=m.opt.timestep; every=max(1,int(round(0.002/dt))); tr=[]
    for i in range(int(round(sec/dt))):
        mujoco.mj_step(m,d)
        if i%every==0:
            p=d.xpos[bid]; v=d.cvel[bid][3:]
            px,pz=float(p[0])*1000.,float(p[2])*1000.
            rx,rz=px-pv2.PADDLE_CX,pz-pv2.PADDLE_CZ
            lx,lz=pv2.to_shooter(px,pz)
            tr.append({"t":round(i*dt,4),"x":round(px,3),"z":round(pz,3),
                       "v":round(float(np.linalg.norm(v)),4),"vx":round(float(v[0]),4),"vz":round(float(v[2]),4),
                       "r":round(math.hypot(rx,rz),3),"ang":round(math.degrees(math.atan2(rz,rx))%360.,2),
                       "lx":round(lx,3),"lz":round(lz,3)})
    return pv2.analyse(tr)

def bz(x): return pv2.tray_top_z(x)+pv2.BALL_R
for rpm in (140.0, 200.0):
    ok=0; tot=0; lines=[]
    for ph in range(0,120,15):
        r=run_phase(145.0,bz(145.0),rpm,ph)
        tot+=1; ok+= 1 if r["launched"] else 0
        lines.append("ph=%3d launched=%-5s minAng=%7.2f"%(ph,r["launched"],r["min_angle_deg"]))
    print("rpm=%.0f  捕获成功 %d/%d"%(rpm,ok,tot))
    for l in lines: print("   ",l)
    print(flush=True)
