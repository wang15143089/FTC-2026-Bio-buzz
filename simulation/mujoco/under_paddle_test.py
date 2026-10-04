"""Ball parked under the paddle rotor: which way does the blade throw it?

Ball starts resting on the channel floor just left of / below the paddle axis.
Paddle CCW in the user front view = omega_y > 0.
Wheels opposed at the vendor no-load speed.
"""
from __future__ import annotations
import json, math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pollen_launcher_sim as P
import feeder_fair_test as F

NIP = P.SHOOTER_ORIGIN
T52 = P.T52
Z_FLOOR_TOP = 17.5


def run(bx, bz, psign, prpm, rpm=P.DEFAULT_RPM if hasattr(P, "DEFAULT_RPM") else 1620.0,
        sec=3.0, vx0=0.0):
    import mujoco, numpy as np
    omega = psign * prpm * 2 * math.pi / 60.0
    xml, ctrl = P.build_xml(rpm, omega, -1, bx, bz)
    xml = F.strip(xml)
    m = mujoco.MjModel.from_xml_string(xml)
    d = mujoco.MjData(m)
    d.ctrl[:] = ctrl
    mujoco.mj_forward(m, d)
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    jid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "ball_free")
    dof = m.jnt_dofadr[jid]
    d.qvel[dof] = vx0
    dt = m.opt.timestep
    every = max(1, int(round(0.002 / dt)))
    smax, vmax, zmax, zmin, xend, zend = -1e9, 0.0, -1e9, 1e9, 0.0, 0.0
    launch = 0.0
    hist = []
    for i in range(int(round(sec / dt))):
        mujoco.mj_step(m, d)
        if i % every:
            continue
        p = d.xpos[bid]
        v = d.cvel[bid][3:]
        x, z = float(p[0]) * 1000, float(p[2]) * 1000
        sp = float(np.linalg.norm(v))
        s = (x - NIP[0]) * T52[0] + (z - NIP[2]) * T52[1]
        smax = max(smax, s)
        zmax = max(zmax, z); zmin = min(zmin, z)
        if sp > vmax:
            vmax = sp
        if s > 20 and sp > launch:
            launch = sp
        xend, zend = x, z
        hist.append((round(i * dt, 3), round(x, 1), round(z, 1), round(s, 1), round(sp, 2)))
    return {"x0": bx, "paddle_sign": psign, "paddle_rpm": psign * prpm, "rpm": rpm,
            "s_max_mm": round(smax, 1), "z_max_mm": round(zmax, 1), "z_min_mm": round(zmin, 1),
            "v_max": round(vmax, 2), "launch_v": round(launch, 2),
            "x_end": round(xend, 1), "z_end": round(zend, 1)}, hist


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    out = []
    for bx in (-105.0, -95.0):
        for ps in (1, -1):
            for pr in (30.0, 120.0, 480.0):
                res, hist = run(bx, Z_FLOOR_TOP + P.BALL_R, ps, pr)
                out.append(res)
                print(json.dumps(res, ensure_ascii=False), flush=True)
                if ps > 0 and pr == 120.0:
                    (Path(__file__).resolve().parent / "out" / f"under_paddle_x{int(bx)}_p{int(pr)}.json"
                     ).write_text(json.dumps(hist), encoding="utf-8")
    (Path(__file__).resolve().parent / "out" / "under_paddle_test.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print("done", flush=True)
