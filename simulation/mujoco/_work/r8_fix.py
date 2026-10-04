# -*- coding: utf-8 -*-
"""R8 fix sweep: change the blade contact geometry so the push is tangential, not radial."""
import math, sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import r6_smooth as r6
import opt_lib as ol
import mujoco, numpy as np

pv2 = ol.pv2
T_STALL, N_FREE = 0.530, 290.0
KV = T_STALL / (N_FREE * 2 * math.pi / 60.0)
BASE = ol.GEOM["D 球窝抬高6.8"][0]
OUT = Path("simulation/mujoco/out")


def mk(angs, bc=52., bx_=6., fc=58., fx=2., bz=15., fz=17., arm=(30., 16., 9., 5.)):
    parts = [("hub", (0., 0., 0.), (18., 17., 18.), 0., "cylY")]
    for i, a in enumerate(angs, 1):
        parts += [("arm_%d" % i, (arm[0], 0, 0), (arm[1], arm[2], arm[3]), a, "box")]
        if bc is not None:
            parts += [("blade_%d" % i, (bc, 0, 0), (bx_, pv2.PADDLE_W / 2., bz), a, "box")]
        if fc is not None:
            parts += [("flex_%d" % i, (fc, 0, 0), (fx, pv2.PADDLE_W / 2., fz), a, "box")]
    return parts


def run(tag, parts, bx=20.9, sec=8.0, rpm=N_FREE, mu_ball=None, static=None, quiet=False):
    pv2.static_geoms = static or BASE
    pv2.paddle_parts = lambda: parts
    xml, ctrl = pv2.build_xml(1620.0, -1, rpm * 2 * math.pi / 60.0, bx, pv2.tray_top_z(bx) + pv2.BALL_R)
    xml = xml.replace('kv="0.08"', 'kv="%.6f"' % KV)
    xml = xml.replace('forcerange="-1.5 1.5"', 'forcerange="-%g %g"' % (T_STALL, T_STALL))
    if mu_ball is not None:
        xml = xml.replace('class="ball"><geom friction="1.0 0.02 0.0001"',
                          'class="ball"><geom friction="%g 0.02 0.0001"' % mu_ball)
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
    pid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "paddle_joint")
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    aid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "paddle_vel")
    bg = set(g for g in range(m.ngeom) if m.geom_bodyid[g] == bid)
    dt = m.opt.timestep; n = int(sec / dt); k = max(1, int(0.002 / dt))
    tq = []; rp = []; tr = []
    saw_carry = None
    for i in range(n):
        mujoco.mj_step(m, d)
        tq.append(abs(float(d.actuator_force[aid])))
        rp.append(math.degrees(d.qvel[pid]) / 6.0)
        if i % k == 0:
            p = d.xpos[bid] * 1000.0
            rx, rz = p[0] - pv2.PADDLE_CX, p[2] - pv2.PADDLE_CZ
            lx, lz = pv2.to_shooter(p[0], p[2])
            tr.append({"t": round(i * dt, 4), "x": round(p[0], 3), "z": round(p[2], 3),
                       "v": round(float(np.linalg.norm(d.cvel[bid][3:])), 4),
                       "vx": round(float(d.cvel[bid][3]), 4), "vz": round(float(d.cvel[bid][5]), 4),
                       "r": round(math.hypot(rx, rz), 3),
                       "ang": round(math.degrees(math.atan2(rz, rx)) % 360.0, 2),
                       "lx": round(lx, 3), "lz": round(lz, 3)})
    res = pv2.analyse(tr)
    tqa = np.array(tq); rpa = np.array(rp)
    ent = next((s for s in tr if s["ang"] < 232.0 and 45 <= s["r"] <= 75), None)
    ex = next((s for s in tr if s["ang"] <= 143.0 and 45 <= s["r"] <= 75), None)
    res["jam_frac"] = round(float((tqa > 0.40).mean()), 3)
    res["rpm_med"] = round(float(np.median(rpa)), 1)
    res["rpm_max"] = round(float(np.percentile(rpa, 95)), 1)
    res["carry_s"] = round(ex["t"] - ent["t"], 2) if (ent and ex) else -1.0
    res["enter_t"] = ent["t"] if ent else -1.0
    res["final_r"] = tr[-1]["r"]; res["final_ang"] = tr[-1]["ang"]
    res["_trace"] = tr
    if not quiet:
        print("  %-22s bx=%-6s launched=%-5s exit_t=%-6s exit_v=%-6s carry=%-6s jam=%-4s rpmMed=%-6s rpm95=%-7s peak=%.2f"
              % (tag, bx, res["launched"], (res.get("exit") or {}).get("t", "--"),
                 (res.get("exit") or {}).get("speed_m_s", "--"), res["carry_s"],
                 "%.0f%%" % (100 * res["jam_frac"]), res["rpm_med"], res["rpm_max"],
                 res["peak_speed_m_s"]), flush=True)
    return res


VARIANTS = {
    "V0 base":        dict(angs=(10., 190.), bc=52., bx_=6., fc=58., fx=2., bz=15., fz=17.),
    "V1 blade out58": dict(angs=(10., 190.), bc=58., bx_=6., fc=64., fx=2., bz=15., fz=17.),
    "V2 wide tang":   dict(angs=(10., 190.), bc=52., bx_=6., fc=58., fx=2., bz=24., fz=26.),
    "V3 low face":    dict(angs=(10., 190.), bc=44., bx_=12., fc=56., fx=2., bz=16., fz=17.),
    "V4 mid face":    dict(angs=(10., 190.), bc=50., bx_=12., fc=58., fx=2., bz=16., fz=17.),
    "V5 no flex":     dict(angs=(10., 190.), bc=52., bx_=6., fc=None, bz=15.),
    "V6 3 blades":    dict(angs=(10., 130., 250.), bc=52., bx_=6., fc=58., fx=2., bz=15., fz=17.),
    "V7 big blade":   dict(angs=(10., 190.), bc=56., bx_=14., fc=62., fx=2., bz=20., fz=22.),
}

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "pocket"
    bx = 20.9 if mode == "pocket" else 145.0
    print("=== R8 blade-geometry fix sweep (%s start, 25-4 @290 rpm, 8 s) ===" % mode)
    out = {}
    for nm, kw in VARIANTS.items():
        out[nm] = run(nm, mk(**kw), bx=bx)
    out["V0 base mu0.4"] = run("V0 base mu0.4", mk(**VARIANTS["V0 base"]), bx=bx, mu_ball=0.4)
    (OUT / ("_r8_fix_%s.json" % mode)).write_text(
        json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "_trace"} for k, v in out.items()},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    print("  saved", OUT / ("_r8_fix_%s.json" % mode))
