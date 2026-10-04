import json, math, sys, importlib.util
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
spec = importlib.util.spec_from_file_location("pv2", r"simulation/mujoco/pollen_v2_sim.py")
pv2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(pv2)
def bz(x): return pv2.tray_top_z(x)+pv2.BALL_R
def run(tag,bx,z,rpm_p,sec,rpm_fw=1620.0):
    xml,ctrl = pv2.build_xml(rpm_fw,-1,rpm_p*2*math.pi/60.0,bx,z)
    tr = pv2.simulate(xml,sec,ctrl); r = pv2.analyse(tr)
    r.update({"tag":tag,"paddle_rpm":rpm_p,"flywheel_rpm":rpm_fw,"ball_start_mm":[bx,round(z,3)]})
    Path(f"simulation/mujoco/out/trace_{tag}.json").write_text(json.dumps(tr),encoding="utf-8")
    return r,tr
r,tr = run("v2_tray_static",145.0,bz(145.0),0.0,8.0)
print("静止拨杆：球从 x=145 自滚 -> 终点 (%.1f, %.1f)  最终 r=%.1f ang=%.1f"%(tr[-1]["x"],tr[-1]["z"],tr[-1]["r"],tr[-1]["ang"]))
print("   最低点 (%.1f, %.1f)  ang=%.1f  r=%.1f ；停稳后 1s 内位移 %.2f mm"%(
    min(tr,key=lambda s:s["z"])["x"],min(tr,key=lambda s:s["z"])["z"],min(tr,key=lambda s:s["ang"])["ang"],
    tr[-1]["r"], math.hypot(tr[-1]["x"]-tr[-400]["x"],tr[-1]["z"]-tr[-400]["z"])))
REST=(-2.30,bz(-2.30))
for fw in (810.0,1620.0,2430.0):
    r,_ = run("v2_fw%d"%int(fw),REST[0],REST[1],200.0,6.0,fw)
    e=r.get("exit")
    print("飞轮 %4d rpm -> %s"%(fw, ("出口 %.2f m/s @ %.1f deg, 射程 %.2f m"%(e["speed_m_s"],e["angle_deg"],e["range_same_height_m"])) if e else "未发射"))
