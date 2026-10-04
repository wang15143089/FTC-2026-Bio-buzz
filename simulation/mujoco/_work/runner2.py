import json, math, sys, importlib.util
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
spec = importlib.util.spec_from_file_location("pv2", r"simulation/mujoco/pollen_v2_sim.py")
pv2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(pv2)
def run(tag,bx,bz,rpm,sec=6.0):
    xml,ctrl = pv2.build_xml(1620.0,-1,rpm*2*math.pi/60.0,bx,bz)
    tr = pv2.simulate(xml,sec,ctrl); res = pv2.analyse(tr)
    res.update({"tag":tag,"paddle_rpm":rpm,"ball_start_mm":[bx,round(bz,3)]})
    Path(f"simulation/mujoco/out/trace_{tag}.json").write_text(json.dumps(tr),encoding="utf-8")
    return res
def bz(x): return pv2.tray_top_z(x)+pv2.BALL_R
REST=( -2.30, bz(-2.30))
jobs=[("rest_p105",REST,105),("rest_p110",REST,110),("rest_p115",REST,115),
      ("tray120_x145",(145.0,bz(145.0)),120),("tray150_x145",(145.0,bz(145.0)),150),
      ("tray200_x130",(130.0,bz(130.0)),200),("tray200_x160",(160.0,bz(160.0)),200)]
out=[]
for tag,(bx,z),rpm in jobs:
    r=run(tag,bx,z,rpm); out.append(r)
    print("%-14s rpm=%3d  launched=%-5s exit142=%-5s minAng=%7.2f maxZ=%7.1f  %s"%(
        tag,rpm,r["launched"],r["reached_142deg_exit"],r["min_angle_deg"],r["max_z_mm"],
        ("" if "exit" not in r else "exit %.2f m/s @%.1f deg range %.2f m"%(r["exit"]["speed_m_s"],r["exit"]["angle_deg"],r["exit"]["range_same_height_m"]))),flush=True)
Path("simulation/mujoco/out/summary_v2_threshold.json").write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding="utf-8")
