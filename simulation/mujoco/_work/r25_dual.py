# -*- coding: utf-8 -*-
"""R25 dual-ball: ONE shared feeder (shell inner arc 107.974, tray tangent to
the carry circle, hub O24) must feed BOTH balls; only the flywheel nip differs.

  POLLEN  R=35.56  nip 64 -> half = 32 + 48 = 80.0
  NECTAR  R=45.974 nip 82 -> half = 41 + 48 = 89.0

Paddle here is the CAD-faithful R25 rotor from
cad/paddle_launcher_constrained.paddle_parts() with the R25 hub/arm override.
"""
import math, sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import opt_lib as ol
import r10_cradle as R10
import r12

pv2 = ol.pv2
OUT = Path("simulation/mujoco/out")

R_IN = 107.974
CUT_X = 38.901
A_LIP = 275.0
HUB_R = 12.0
PIVOT = (-0.806, 0.423)
T_STALL = 0.530
N_FREE = 290.0

BALLS = {
    "POLLEN": dict(r=35.56, m=0.060, nip=64.0),
    "NECTAR": dict(r=45.974, m=0.130, nip=82.0),
}
WHEEL_R = 48.0


def parts_cad_r25(hub_r=HUB_R):
    """R25 rotor exactly as CAD: hub O24, arm r10..46, hinge pin, blade r46..58, flex r56..60."""
    def f():
        out = [("hub", (0.0, 0.0, 0.0), (hub_r, 17.0), 0.0, "cylY")]
        for i, a in enumerate((18.0, 138.0, 258.0), 1):
            out.append(("arm_%d" % i, (28.0, 0.0, 0.0), (36.0, 18.0, 10.0), a, "box"))
            out.append(("hinge_%d" % i, (46.0, 0.0, 0.0), (5.0, 50.0), a, "cylY"))
            out.append(("blade_%d" % i, (52.0, 0.0, 0.0), (12.0, 96.0, 30.0), a, "box"))
            out.append(("flex_%d" % i, (58.0, 0.0, 0.0), (4.0, 96.0, 34.0), a, "box"))
        return out
    return f


def geom_shared():
    return (lambda: R10.stat(CUT_X, A_LIP, tray_x1=185.0), parts_cad_r25())


def run(tag, ball, rpm, sec=20.0, quiet=True, extra_mu=None):
    r_in = R_IN
    r_carry = R_IN - ball["r"]
    half = ball["nip"] / 2.0 + WHEEL_R
    old = (pv2.HALF_SPACING, r12.N_FREE, r12.OMEGA, r12.KV, pv2.R_CARRY,
           pv2.PIVOT_X, pv2.PIVOT_Z)
    w = rpm * 2.0 * math.pi / 60.0
    pv2.HALF_SPACING = half
    r12.N_FREE, r12.OMEGA = rpm, w
    r12.KV = T_STALL / w
    pv2.R_CARRY = r_carry
    pv2.PIVOT_X, pv2.PIVOT_Z = PIVOT
    bx = 145.0
    bz = pv2.tray_top_z(bx) + ball["r"]
    try:
        res = r12.run(tag, geom_shared(), sign=+1.0, mu=0.40, bx=bx, bz=bz,
                      sec=sec, ball_r=ball["r"], ball_m=ball["m"], r_in=r_in,
                      detail=0.5, quiet=quiet)
    finally:
        (pv2.HALF_SPACING, r12.N_FREE, r12.OMEGA, r12.KV, pv2.R_CARRY,
         pv2.PIVOT_X, pv2.PIVOT_Z) = old
    return res, dict(r_carry=r_carry, half=half, r_in=r_in, rpm=rpm,
                     start=[bx, round(bz, 3)])


def analyse(res, ball):
    tr = res["_trace"]
    r_c = R_IN - ball["r"]
    lo, hi = r_c - 14.0, r_c + 14.0
    near = lambda s: lo <= s["r"] <= hi
    reached = [s for s in tr if s["ang"] <= 143.0 and near(s)]
    carried = [s for s in tr if 145.0 <= s["ang"] <= 268.0 and near(s)]
    entered = [s for s in tr if s["ang"] < 268.0 and near(s)]
    fast = [s for s in tr if s["lx"] > -20.0 and s["v"] > 3.0]
    passed_nip = [s for s in tr if s["lx"] > 0.0]
    out = {
        "launched": bool(fast),
        "entered_shell": bool(entered),
        "reached_exit_142deg": bool(reached),
        "carried_samples": len(carried),
        "min_angle_deg": round(min(s["ang"] for s in tr), 2),
        "min_r_mm": round(min(s["r"] for s in tr), 2),
        "max_r_mm": round(max(s["r"] for s in tr), 2),
        "max_lx_mm": round(max(s["lx"] for s in tr), 2),
        "passed_nip": bool(passed_nip),
        "final_mm": [tr[-1]["x"], tr[-1]["z"]],
        "r_carry_expected_mm": round(r_c, 3),
        "rest_after_1s_mm": None,
    }
    settled = [s for s in tr if s["t"] <= 1.5]
    if settled:
        out["rest_after_1s_mm"] = [settled[-1]["x"], settled[-1]["z"]]
    if reached:
        s = reached[0]
        out["release"] = {"t": s["t"], "v_m_s": s["v"], "ang_deg": s["ang"]}
    idx = next((i for i, s in enumerate(tr) if s["lx"] > 40.0), None)
    if idx is not None:
        s = tr[idx]
        vx, vz = s["vx"], s["vz"]
        out["exit"] = {"t": s["t"], "speed_m_s": round(math.hypot(vx, vz), 3),
                       "angle_deg": round(math.degrees(math.atan2(vz, vx)), 2),
                       "range_same_height_m": round(2 * vx * vz / 9.81, 2)}
    return out


def main():
    res_all = {}
    print("=== R25 DUAL-BALL: one shared feeder, only the nip changes ===", flush=True)
    print("shared: R_IN=%.3f  A_LIP=%.1f  CUT_X=%.3f  hub_r=%.1f  pivot=(%.3f, %.3f)"
          % (R_IN, A_LIP, CUT_X, HUB_R, PIVOT[0], PIVOT[1]), flush=True)
    plan = [("NECTAR_60rpm", "NECTAR", 60.0),
            ("POLLEN_60rpm", "POLLEN", 60.0),
            ("POLLEN_90rpm", "POLLEN", 90.0),
            ("NECTAR_90rpm", "NECTAR", 90.0)]
    for tag, bn, rpm in plan:
        ball = BALLS[bn]
        print("-- %-14s ball_r=%6.3f nip=%4.1f -> half=%5.2f  %5.1f rpm --"
              % (tag, ball["r"], ball["nip"], ball["nip"] / 2 + WHEEL_R, rpm), flush=True)
        res, meta = run(tag, ball, rpm)
        a = analyse(res, ball)
        a.update(meta)
        res_all[tag] = a
        e = a.get("exit") or {}
        print("   launched=%-5s exit_t=%-6s v=%-6s ang=%-7s min_ang=%-7.2f min_r=%-6.2f "
              "max_lx=%-7.2f final=(%.0f,%.0f)"
              % (a["launched"], e.get("t", "--"), e.get("speed_m_s", "--"),
                 e.get("angle_deg", "--"), a["min_angle_deg"], a["min_r_mm"],
                 a["max_lx_mm"], a["final_mm"][0], a["final_mm"][1]), flush=True)
    OUT.joinpath("_r25_dual_ball.json").write_text(
        json.dumps(res_all, ensure_ascii=False, indent=1), encoding="utf-8")
    print("saved", OUT / "_r25_dual_ball.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
