# -*- coding: utf-8 -*-
"""R24: NECTAR gravity hand-off, hub radius / nest radius trade study."""
import math, sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import r6_smooth as r6
import opt_lib as ol
import r10_cradle as R10
import r12
import r23

pv2 = ol.pv2
OUT = Path("simulation/mujoco/out")
BN, BN_MASS, T_STALL = 45.974, 0.130, 0.530


def main():
    res = {}
    print("=== R24 NECTAR hub/nest trade study ===", flush=True)
    cases = [("H1_hub18_r70", 18.0, 70.0), ("H2_hub15_r66", 15.0, 66.0),
             ("H3_hub12_r62", 12.0, 62.0)]
    for tag, hub_r, r_c in cases:
        s = r23.tangent_setup(r_c, BN)
        print("  %s: hub r=%.1f r_carry=%.1f clr=%.2f delta=%.2f cut=%.2f lip=%.2f"
              % (tag, hub_r, r_c, r_c - BN - hub_r, s["delta"], s["Fx"], s["a_lip"]), flush=True)
        g = (lambda s=s: R10.stat(s["Fx"], s["a_lip"]), r23.parts_hub(hub_r))
        res[tag] = r23.go(tag, g, 60.0, 89.0, BN, BN_MASS, r_c, lr=+1.0,
                          pivot=s["pivot"])
        res[tag]["hub_r"] = hub_r
        res[tag]["r_carry"] = r_c
        res[tag]["hub_clearance_mm"] = round(r_c - BN - hub_r, 3)
        res[tag]["delta_mm"] = round(s["delta"], 3)
        res[tag]["cut_x_mm"] = round(s["Fx"], 3)
    thin = {k: {kk: vv for kk, vv in v.items() if kk != "_trace"} for k, v in res.items()}
    OUT.joinpath("_r24_nectar_trade.json").write_text(
        json.dumps(thin, ensure_ascii=False, indent=1), encoding="utf-8")
    print("saved", OUT / "_r24_nectar_trade.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
