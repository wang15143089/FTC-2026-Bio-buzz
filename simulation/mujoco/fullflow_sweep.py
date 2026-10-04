"""Full-flow sweep: paddle feeder -> flywheel launch (T06 / POLLEN).

Finds whether any (ball staging point, paddle rpm, paddle direction) combination
delivers the ball to the flywheel nip.
"""
from __future__ import annotations

import argparse, json, math, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pollen_launcher_sim as P

NIP = P.SHOOTER_ORIGIN
T52, N52 = P.T52, P.N52


def s_of(x_mm, z_mm):
    return (x_mm - NIP[0]) * T52[0] + (z_mm - NIP[2]) * T52[1]


def run_one(ball_x, ball_z, rpm, paddle_sign, paddle_rpm, seconds):
    import mujoco, numpy as np
    omega = paddle_sign * paddle_rpm * 2 * math.pi / 60.0
    xml, ctrl = P.build_xml(rpm, omega, -1, ball_x, ball_z)
    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)
    data.ctrl[:] = ctrl
    mujoco.mj_forward(model, data)
    bid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "ball")
    dt = model.opt.timestep
    every = max(1, int(round(0.004 / dt)))
    best_s, best_v, launch_v = -1e9, 0.0, 0.0
    for i in range(int(round(seconds / dt))):
        mujoco.mj_step(model, data)
        if i % every:
            continue
        p = data.xpos[bid]
        v = data.cvel[bid][3:]
        sp = float(np.linalg.norm(v))
        s = s_of(float(p[0]) * 1000, float(p[2]) * 1000)
        if s > best_s:
            best_s = s
        if s > 20.0 and sp > launch_v:
            launch_v = sp
        if sp > best_v and s > -60.0:
            best_v = sp
    return {"s_max_mm": round(best_s, 1), "v_at_nip_m_s": round(best_v, 3),
            "launch_v_m_s": round(launch_v, 3), "reached_nip": best_s > -20.0}


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--rpm", type=float, default=1620.0)
    ap.add_argument("--seconds", type=float, default=3.0)
    a = ap.parse_args()
    out = Path(__file__).resolve().parent / "out"
    out.mkdir(exist_ok=True)

    spots = [
        ("tray_far", -150.0, 17.5 + P.BALL_R),
        ("tray_mid", -128.0, 17.5 + P.BALL_R),
        ("notch_edge", -95.6, 49.3),
        ("dropped_in", -47.0, 130.0),
    ]
    rows = []
    for name, bx, bz in spots:
        for sign in (-1, 1):
            for prpm in (30.0, 120.0, 480.0):
                r = run_one(bx, bz, a.rpm, sign, prpm, a.seconds)
                r.update({"spot": name, "ball_x": bx, "ball_z": bz,
                          "paddle_sign": sign, "paddle_rpm": sign * prpm})
                rows.append(r)
                print(json.dumps(r, ensure_ascii=False), flush=True)
    (out / "fullflow_sweep.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    hits = [r for r in rows if r["reached_nip"]]
    print(f"\n=== reached nip: {len(hits)}/{len(rows)} ===", flush=True)
    for r in hits:
        print(json.dumps(r, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
