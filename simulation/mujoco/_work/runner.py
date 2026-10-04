import json, math, sys, importlib.util
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
spec = importlib.util.spec_from_file_location("pv2", r"simulation/mujoco/pollen_v2_sim.py")
pv2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(pv2)

def run(tag, ball_x, ball_z, paddle_rpm, seconds=6.0, paddle_sign=1, fw_rpm=1620.0, spin_sign=-1):
    omega = paddle_sign*paddle_rpm*2*math.pi/60.0
    xml, ctrl = pv2.build_xml(fw_rpm, spin_sign, omega, ball_x, ball_z)
    trace = pv2.simulate(xml, seconds, ctrl)
    res = pv2.analyse(trace)
    res.update({"tag":tag,"paddle_rpm":paddle_rpm,"flywheel_rpm":fw_rpm,
                "ball_start_mm":[ball_x,round(ball_z,3)],"seconds":seconds})
    Path(f"simulation/mujoco/out/trace_{tag}.json").write_text(json.dumps(trace),encoding="utf-8")
    return res, trace

REST=(-2.30, pv2.tray_top_z(-2.30)+pv2.BALL_R)
print("rest ball z =", round(REST[1],3))
jobs=[("v2_rest_p120",REST,120),("v2_rest_p150",REST,150),("v2_rest_p180",REST,180),
      ("v2_tray_p200",(145.0,pv2.tray_top_z(145.0)+pv2.BALL_R),200),
      ("v2_tray_p320",(145.0,pv2.tray_top_z(145.0)+pv2.BALL_R),320)]
out=[]
for tag,(bx,bz),rpm in jobs:
    res,tr = run(tag,bx,bz,rpm)
    out.append(res)
    print(json.dumps(res,ensure_ascii=False),flush=True)
Path("simulation/mujoco/out/summary_v2_extra.json").write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding="utf-8")
