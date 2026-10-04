# -*- coding: utf-8 -*-
"""R5 vs R6 / R6c, driven by the real 25-4 Super Speed motor curve: milestone timings."""
import json, math, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import r6_smooth as r6
import r6_motor as rm
import opt_lib as ol

pv2 = ol.pv2
OUT = Path("simulation/mujoco/out")


def milestones(name, bx=145.0):
    r = rm.run_motor(name, bx=bx, sec=12.0)
    tr = r["_trace"]

    def first(pred, after=0.0):
        for s in tr:
            if s["t"] > after and pred(s):
                return s["t"]
        return None

    t_set = first(lambda s: s["v"] < 0.05, 0.30)
    t_leave = first(lambda s: s["v"] > 0.10, (t_set or 0.0) + 0.05)
    t_enter = first(lambda s: s["ang"] <= 232.0 and 45.0 <= s["r"] <= 70.0)
    t_exit = first(lambda s: s["ang"] <= 143.0 and 45.0 <= s["r"] <= 70.0)
    t_launch = first(lambda s: s["lx"] > -20.0 and s["v"] > 3.0)
    pk = max((s["v"] for s in tr if s["t"] < (t_enter or 99)), default=0.0)
    d = {"settle": t_set, "leave": t_leave, "enter": t_enter, "exit": t_exit, "launch": t_launch,
         "creep": (t_enter - t_set) if (t_enter and t_set) else None,
         "carry": (t_exit - t_enter) if (t_exit and t_enter) else None,
         "hop_peak_v": round(pk, 3)}
    print("  %-5s bx=%-6g settle=%.2f  leave=%.2f  enter_drum=%.2f  exit=%.2f  launch=%.2f  "
          "| creep=%s  carry=%s  pre-drum peak v=%.2f m/s"
          % (name, bx, t_set or -1, t_leave or -1, t_enter or -1, t_exit or -1, t_launch or -1,
             ("%.2f" % d["creep"]) if d["creep"] else "-",
             ("%.2f" % d["carry"]) if d["carry"] else "-", d["hop_peak_v"]))
    return r, d


if __name__ == "__main__":
    print("=== 25-4 Super Speed (0.530 Nm / 290 rpm) : milestone timings ===")
    out = {}
    for nm in ("R5", "R6", "R6c"):
        for bx in (145.0, 138.0):
            r, d = milestones(nm, bx)
            out["%s_%g" % (nm, bx)] = d
    OUT.joinpath("_r6_summary.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("saved", OUT / "_r6_summary.json")
