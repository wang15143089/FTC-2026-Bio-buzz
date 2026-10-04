# -*- coding: utf-8 -*-
"""取 V0 / R2 的停位球心，用于剖面图。"""
import math, sys, json, importlib.util
sys.stdout.reconfigure(encoding="utf-8")
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
def th2(ts): return blades([(360.0-t) % 360.0 for t in ts])
ol.GEOM["R2"] = (ol.GEOM["A 唇口喇叭"][0], th2((350.0, 170.0)))

out = {}
for name in ("V0 现状", "R2"):
    r = ol.run(name, bx=145.0, fr=1.0, sec=4.0, rest=True, trace=True)
    tr = r["_trace"][-30:]
    x = sum(p["x"] for p in tr)/len(tr); z = sum(p["z"] for p in tr)/len(tr)
    dx, dz = x - pv2.PADDLE_CX, z - pv2.PADDLE_CZ
    out[name] = {"x": round(x,2), "z": round(z,2),
                 "r": round(math.hypot(dx,dz),2),
                 "ang": round(math.degrees(math.atan2(dz,dx))%360.0,2),
                 "yaw_deg": round(math.degrees(r.get("_paddle_yaw", 0.0)),3) if "_paddle_yaw" in r else None}
    print(name, out[name])
open(r"simulation/mujoco/out/probe_rest_for_section.json","w",encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=2))
