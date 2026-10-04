"""Fair feeder test for T06/POLLEN.

The one-way backflow fingers as modelled sit inside the 3-paddle sweep radius and
jam the rotor, so they are removed here to give the feeder a fair chance.
"""
from __future__ import annotations
import json, math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pollen_launcher_sim as P

NIP = P.SHOOTER_ORIGIN
T52 = P.T52


def strip(xml, drop_ball=False, drop_paddle=False, drop_fingers=True):
    """Remove whole <body> blocks / lines by name, plus the sensor block."""
    lines = xml.splitlines()
    out, skip_body, in_sensor = [], False, False
    for line in lines:
        if "<sensor>" in line:
            in_sensor = True
            continue
        if "</sensor>" in line:
            in_sensor = False
            continue
        if in_sensor:
            continue
        if skip_body:
            if line.strip() == "</body>":
                skip_body = False
            continue
        if '<body name="paddle"' in line and drop_paddle:
            skip_body = True
            continue
        if '<body name="ball"' in line and drop_ball:
            skip_body = True
            continue
        if drop_fingers and "finger" in line:
            continue
        if drop_paddle and "paddle_joint" in line:
            continue
        out.append(line)
    return "\n".join(out)


def _paddle_index(m):
    import mujoco
    return mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "paddle_joint")


def spin_test(rpm_paddle=30.0):
    import mujoco
    xml, ctrl = P.build_xml(1620.0, -rpm_paddle * 2 * math.pi / 60.0, -1, -300.0, 400.0)
    xml = strip(xml, drop_ball=True)
    m = mujoco.MjModel.from_xml_string(xml)
    d = mujoco.MjData(m)
    d.ctrl[:] = ctrl
    mujoco.mj_forward(m, d)
    pj = _paddle_index(m)
    for _ in range(2500):
        mujoco.mj_step(m, d)
    return float(d.qvel[m.jnt_dofadr[pj]]), float(d.qpos[m.jnt_qposadr[pj]])


def run(bx, bz, psign, prpm, sec=3.0, rpm=1620.0):
    import mujoco, numpy as np
    omega = psign * prpm * 2 * math.pi / 60.0
    xml, ctrl = P.build_xml(rpm, omega, -1, bx, bz)
    xml = strip(xml)
    m = mujoco.MjModel.from_xml_string(xml)
    d = mujoco.MjData(m)
    d.ctrl[:] = ctrl
    mujoco.mj_forward(m, d)
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    pj = _paddle_index(m)
    dt = m.opt.timestep
    every = max(1, int(round(0.004 / dt)))
    smax, vb, lv, qmax = -1e9, 0.0, 0.0, 0.0
    for i in range(int(round(sec / dt))):
        mujoco.mj_step(m, d)
        qmax = max(qmax, abs(float(d.qvel[m.jnt_dofadr[pj]])))
        if i % every:
            continue
        p = d.xpos[bid]
        v = d.cvel[bid][3:]
        sp = float(np.linalg.norm(v))
        s = (p[0] * 1000 - NIP[0]) * T52[0] + (p[2] * 1000 - NIP[2]) * T52[1]
        smax = max(smax, s)
        if s > 20 and sp > lv:
            lv = sp
        if s > -60 and sp > vb:
            vb = sp
    return round(smax, 1), round(vb, 3), round(lv, 3), round(qmax, 2)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    qd, q = spin_test()
    print(json.dumps({"paddle_qd_no_fingers_no_ball": round(qd, 3), "angle": round(q, 2),
                      "target_qd": round(30 * 2 * math.pi / 60, 3)}), flush=True)
    rows = []
    spots = [("tray_far", -150.0, 17.5 + P.BALL_R), ("tray_mid", -128.0, 17.5 + P.BALL_R),
             ("notch_edge", -95.6, 49.3), ("dropped_above", -47.0, 165.0)]
    for name, bx, bz in spots:
        for ps in (-1, 1):
            for pr in (30.0, 120.0, 480.0):
                smax, vb, lv, qmax = run(bx, bz, ps, pr)
                r = {"spot": name, "sign": ps, "rpm": ps * pr, "s_max_mm": smax,
                     "v_best": vb, "launch_v": lv, "paddle_qd_max": qmax}
                rows.append(r)
                print(json.dumps(r, ensure_ascii=False), flush=True)
    hits = [r for r in rows if r["s_max_mm"] > -20]
    print(f"\n=== reached nip: {len(hits)}/{len(rows)} ===", flush=True)
    for r in sorted(rows, key=lambda r: -r["s_max_mm"])[:6]:
        print(json.dumps(r, ensure_ascii=False), flush=True)
    (Path(__file__).resolve().parent / "out" / "feeder_fair_test.json").write_text(
        json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
