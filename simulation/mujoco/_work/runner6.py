import json, math, sys, importlib.util
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
spec = importlib.util.spec_from_file_location("pv2", r"simulation/mujoco/pollen_v2_sim.py")
pv2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(pv2)
def bz(x): return pv2.tray_top_z(x)+pv2.BALL_R
out=[];ok=0;tot=0
for x in (120.,125.,130.,135.,140.,145.,150.,155.,160.,165.,170.):
    xml,ctrl = pv2.build_xml(1620.0,-1,200.0*2*math.pi/60.0,x,bz(x))
    tr=pv2.simulate(xml,7.0,ctrl); r=pv2.analyse(tr)
    Path(f"simulation/mujoco/out/trace_v2_xsweep_{int(x)}.json").write_text(json.dumps(tr),encoding="utf-8")
    tot+=1; ok+=1 if r["launched"] else 0
    print("x=%5.0f  launched=%-5s minAng=%7.2f  出口 %s"%(x,r["launched"],r["min_angle_deg"],
          ("%.2f m/s @%.1f deg"%(r["exit"]["speed_m_s"],r["exit"]["angle_deg"])) if "exit" in r else "-"),flush=True)
    out.append({"x":x,"launched":r["launched"],"min_angle_deg":r["min_angle_deg"]})
print("200 rpm 下起始位置成功率 %d/%d"%(ok,tot))
Path("simulation/mujoco/out/summary_v2_xsweep.json").write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding="utf-8")
