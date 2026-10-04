import json, math, sys, importlib.util
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
spec = importlib.util.spec_from_file_location("pv2", r"simulation/mujoco/pollen_v2_sim.py")
pv2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(pv2)
def bz(x): return pv2.tray_top_z(x)+pv2.BALL_R
def run(mu, tag):
    xml,_ = pv2.build_xml(1620.0,-1,0.0,145.0,bz(145.0))
    old='<default class="ball"><geom friction="1.0 0.02 0.0001"'
    assert old in xml
    xml = xml.replace(old, f'<default class="ball"><geom friction="{mu} 0.02 0.0001"')
    tr = pv2.simulate(xml,8.0,[0.0,0.0,0.0])
    Path(f"simulation/mujoco/out/trace_v2_traystatic_mu{tag}.json").write_text(json.dumps(tr),encoding="utf-8")
    return tr
for mu,tag in ((0.6,"060"),(0.3,"030"),(0.15,"015")):
    tr=run(mu,tag)
    print("球摩擦=%.2f -> 终点 (%.1f, %.1f)  r=%.1f ang=%.1f   全程最大速度 %.3f m/s"%(
        mu,tr[-1]["x"],tr[-1]["z"],tr[-1]["r"],tr[-1]["ang"],max(s["v"] for s in tr)),flush=True)
