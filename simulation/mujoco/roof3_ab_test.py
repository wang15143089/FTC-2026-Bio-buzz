"""A/B: is the 52 deg roof panel lip (guide_roof_3) what jams the ball?"""
from __future__ import annotations
import json, math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pollen_launcher_sim as P
import feeder_fair_test as F

NIP = P.SHOOTER_ORIGIN
T52 = P.T52
Z0 = 17.5 + P.BALL_R


def strip_extra(xml, drop=()):
    return "\n".join(l for l in xml.splitlines() if not any(d in l for d in drop))


def run(bx, psign, prpm, drop=(), rpm=1620.0, sec=3.5):
    import mujoco, numpy as np
    omega = psign * prpm * 2 * math.pi / 60.0
    xml, ctrl = P.build_xml(rpm, omega, -1, bx, Z0)
    xml = F.strip(strip_extra(xml, drop))
    m = mujoco.MjModel.from_xml_string(xml)
    d = mujoco.MjData(m); d.ctrl[:] = ctrl
    mujoco.mj_forward(m, d)
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    pj = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "paddle_joint")
    dt = m.opt.timestep
    every = max(1, int(round(0.002 / dt)))
    smax, v_at, zmax, xend, zend, qd_end = -1e9, 0.0, -1e9, 0, 0, 0.0
    for i in range(int(round(sec / dt))):
        mujoco.mj_step(m, d)
        if i % every:
            continue
        p = d.xpos[bid]; v = d.cvel[bid][3:]
        x, z = float(p[0])*1000, float(p[2])*1000
        sp = float(np.linalg.norm(v))
        s = (x-NIP[0])*T52[0] + (z-NIP[2])*T52[1]
        if s > smax:
            smax = s
        zmax = max(zmax, z); xend, zend = x, z
        qd_end = float(d.qvel[m.jnt_dofadr[pj]])
    return {"variant": "base" if not drop else "no_roof3", "x0": bx, "paddle_sign": psign,
            "paddle_rpm": psign*prpm, "s_max_mm": round(smax,1), "z_max_mm": round(zmax,1),
            "x_end": round(xend,1), "z_end": round(zend,1), "paddle_qvel_end": round(qd_end,3),
            "target_qvel": round(omega,1)}


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    out = []
    for drop in ((), ("guide_roof_3",)):
        for bx in (-95.0, -85.0):
            for ps in (1, -1):
                for pr in (120.0, 480.0):
                    r = run(bx, ps, pr, drop)
                    out.append(r)
                    print(json.dumps(r, ensure_ascii=False), flush=True)
    (Path(__file__).resolve().parent / "out" / "roof3_ab.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print("done")
