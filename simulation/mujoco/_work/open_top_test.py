"""Which channel panel is actually blocking the under-paddle lift?

Variants remove one / all roof panels and report whether the ball reaches the nip.
"""
from __future__ import annotations
import json, math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pollen_launcher_sim as P
import feeder_fair_test as F

NIP, T52 = P.SHOOTER_ORIGIN, P.T52
FLOOR_TOP = 17.5


def strip_named(xml, prefixes):
    keep = []
    for line in xml.splitlines():
        if any(p in line for p in prefixes) and "<geom" in line:
            continue
        keep.append(line)
    return "\n".join(keep)


def run(bx, psign, prpm, prefixes, sec=3.0, rpm=1620.0):
    import mujoco, numpy as np
    omega = psign * prpm * 2 * math.pi / 60.0
    xml, ctrl = P.build_xml(rpm, omega, -1, bx, FLOOR_TOP + P.BALL_R)
    xml = strip_named(F.strip(xml), prefixes)
    m = mujoco.MjModel.from_xml_string(xml)
    d = mujoco.MjData(m)
    d.ctrl[:] = ctrl
    mujoco.mj_forward(m, d)
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    dt = m.opt.timestep
    every = max(1, int(round(0.002 / dt)))
    smax, zmax, vmax, launch = -1e9, -1e9, 0.0, 0.0
    for i in range(int(round(sec / dt))):
        mujoco.mj_step(m, d)
        if i % every:
            continue
        p = d.xpos[bid]
        sp = float(np.linalg.norm(d.cvel[bid][3:]))
        x, z = float(p[0]) * 1000, float(p[2]) * 1000
        s = (x - NIP[0]) * T52[0] + (z - NIP[2]) * T52[1]
        smax = max(smax, s); zmax = max(zmax, z); vmax = max(vmax, sp)
        if s > 20 and sp > launch:
            launch = sp
    return {"s_max_mm": round(smax, 1), "z_max_mm": round(zmax, 1),
            "v_max": round(vmax, 2), "launch_v": round(launch, 2)}


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    variants = [("base", []), ("no_roof1", ["guide_roof_1"]),
                ("no_roof3", ["guide_roof_3"]), ("no_roof_all", ["guide_roof"])]
    rows = []
    for name, pref in variants:
        for bx in (-95.0, -105.0):
            for pr in (120.0, 480.0):
                r = run(bx, 1, pr, pref)
                r.update(variant=name, x0=bx, paddle_rpm=pr)
                rows.append(r)
                print(json.dumps(r, ensure_ascii=False), flush=True)
    (Path(__file__).resolve().parent.parent / "out" / "open_top_test.json").write_text(
        json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    print("done", flush=True)
