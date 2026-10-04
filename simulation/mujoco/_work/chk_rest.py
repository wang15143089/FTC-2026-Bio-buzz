# -*- coding: utf-8 -*-
import math, sys, importlib.util
sys.stdout.reconfigure(encoding="utf-8")
spec = importlib.util.spec_from_file_location("ol", r"simulation/mujoco/_work/opt_lib.py")
ol = importlib.util.module_from_spec(spec); spec.loader.exec_module(ol)
pv2 = ol.pv2
for name in ("V0 现状",):
    r = ol.run(name, bx=145.0, fr=1.0, sec=4.0, rest=True, trace=True)
    tr = r["_trace"]
    print("samples:", len(tr), " analyse settled:", r.get("settled_position_mm"), " rest0:", r["rest_position_mm"])
    for s in tr[::200]:
        print("  t=%5.2f x=%8.2f z=%8.2f r=%6.1f ang=%6.1f v=%5.3f" % (s["t"], s["x"], s["z"], s["r"], s["ang"], s["v"]))
    print("  last:", tr[-1])
