"""Launch-stage check: inject the ball at the throat entry and see whether the
opposed flywheels actually launch it (T06 / POLLEN).

The feeder (paddle rotor) is removed so the test isolates the flywheel stage.
World frame = CAD frame, metres.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

import pollen_launcher_sim as P

HERE = Path(__file__).resolve().parent
T52 = P.T52
N52 = P.N52
NIP = P.SHOOTER_ORIGIN


def strip_paddle(xml: str) -> str:
    out, skip = [], False
    for line in xml.splitlines():
        if 'name="paddle"' in line and "<body" in line:
            skip = True
            continue
        if skip:
            if line.strip() == "</body>":
                skip = False
            continue
        if "paddle_" in line:
            continue
        out.append(line)
    return "\n".join(out)


def local_sn(px, pz):
    dx, dz = px - NIP[0], pz - NIP[2]
    return dx * T52[0] + dz * T52[1], dx * N52[0] + dz * N52[1]


def run(rpm, spin_sign, v_inj, s0, seconds=1.5, dt=0.0002):
    import mujoco
    import numpy as np

    px = NIP[0] + s0 * T52[0]
    pz = NIP[2] + s0 * T52[1]
    xml, _ = P.build_xml(rpm, 0.0, spin_sign, px, pz)
    xml = strip_paddle(xml)
    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)

    fw = spin_sign * rpm * 2.0 * math.pi / 60.0
    data.ctrl[:] = [fw, -fw]
    mujoco.mj_forward(model, data)

    bid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "ball")
    jid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, "ball_free")
    va = int(model.jnt_dofadr[jid])
    data.qvel[va:va + 3] = [v_inj * T52[0], 0.0, v_inj * T52[1]]

    every = max(1, int(round(0.002 / dt)))
    trace, peak = [], {"v": 0.0, "t": 0.0}
    for i in range(int(round(seconds / dt))):
        mujoco.mj_step(model, data)
        if i % every:
            continue
        p = data.xpos[bid]
        v = data.cvel[bid][3:]
        sp = float(np.linalg.norm(v))
        px_mm, pz_mm = float(p[0]) * 1000.0, float(p[2]) * 1000.0
        s, n = local_sn(px_mm, pz_mm)
        trace.append((round(i * dt, 4), round(px_mm, 1), round(pz_mm, 1),
                      round(s, 1), round(n, 1), round(sp, 3),
                      round(float(v[0]), 3), round(float(v[2]), 3)))
        if s > 20.0 and sp > peak["v"]:
            peak = {"v": sp, "t": round(i * dt, 3)}
    return trace, peak


def summarize(trace):
    z_arr = [t[2] for t in trace]
    # clean ballistic phase starts once the ball is 40 mm past the nip moving up
    idx = next((i for i, t in enumerate(trace) if t[3] > 40.0 and t[7] > 0.5), None)
    if idx is None:
        return {"launched": False, "s_max_mm": round(max(t[3] for t in trace), 1),
                "z_max_mm": round(max(z_arr), 1), "v_max_m_s": round(max(t[5] for t in trace), 3),
                "exit_v_m_s": 0.0, "exit_angle_deg": 0.0, "apex_m": 0.0,
                "range_m": 0.0, "shaft_speed_m_s": 0.0}
    ex = trace[idx]
    angle = math.degrees(math.atan2(ex[7], ex[6]))
    ran = ex[5] ** 2 * math.sin(2 * math.radians(angle)) / 9.81
    apex = ex[5] ** 2 * math.sin(math.radians(angle)) ** 2 / (2 * 9.81)
    return {
        "launched": True,
        "s_max_mm": round(max(t[3] for t in trace), 1),
        "z_max_mm": round(max(z_arr), 1),
        "v_max_m_s": round(max(t[5] for t in trace[:idx + 25]), 3),
        "exit_v_m_s": round(ex[5], 3),
        "exit_angle_deg": round(angle, 1),
        "apex_m": round(apex, 2),
        "range_m": round(ran, 2),
        "shaft_speed_m_s": 0.0,
    }


def main():
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--rpm", type=float, nargs="+", default=[1620.0])
    ap.add_argument("--v-inj", type=float, nargs="+", default=[1.5, 2.5, 3.5])
    ap.add_argument("--s0", type=float, default=-140.0, help="injection station along launch axis (mm)")
    ap.add_argument("--seconds", type=float, default=1.5)
    ap.add_argument("--outdir", default=str(HERE / "out"))
    ap.add_argument("--plot", action="store_true")
    args = ap.parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    rows = []
    for rpm in args.rpm:
        for v in args.v_inj:
            trace, peak = run(rpm, -1, v, args.s0, args.seconds)
            s = summarize(trace)
            s.update({"rpm": rpm, "v_inj": v, "peak_v_m_s": round(peak["v"], 3),
                      "peak_t_s": peak["t"]})
            rows.append(s)
            print(json.dumps(s, ensure_ascii=False), flush=True)
            tag = f"launch_rpm{int(rpm)}_v{v}"
            (outdir / f"trace_{tag}.json").write_text(json.dumps(trace), encoding="utf-8")
            if args.plot:
                plot(tag, trace, outdir, f"rpm={rpm:.0f} v_inj={v} m/s  exit={s['exit_v_m_s']} m/s")
    (outdir / "launch_summary.json").write_text(
        json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n-> " + str(outdir / "launch_summary.json"), flush=True)


def plot(tag, trace, outdir, title):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    ax.plot([t[1] for t in trace], [t[2] for t in trace], "-", color="crimson", lw=1.6)
    ax.plot([trace[0][1]], [trace[0][2]], "o", color="crimson")
    for (dx, dz) in ((0, 55), (0, -55)):
        c = P.to_world(-135 + P.THROAT_LENGTH / 2, 0, dz)
        a = math.radians(-P.ANGLE)
        hx, hz = P.THROAT_LENGTH / 2, 1.5
        pts = [(-hx, -hz), (hx, -hz), (hx, hz), (-hx, hz), (-hx, -hz)]
        ax.plot([c[0] + u * math.cos(a) + v * math.sin(a) for u, v in pts],
                [c[2] - u * math.sin(a) + v * math.cos(a) for u, v in pts], "-", color="#2f8fd4")
    for sign in (1, -1):
        cx, _, cz = P.flywheel_axle_center(sign)
        ax.add_patch(plt.Circle((cx * 1000, cz * 1000), P.WHEEL_R, fill=False, color="k"))
    ax.set_aspect("equal")
    ax.grid(alpha=0.25)
    ax.set_xlabel("X [mm]")
    ax.set_ylabel("Z [mm]")
    ax.set_title(title)
    ax2.plot([t[0] for t in trace], [t[5] for t in trace], color="navy")
    ax2.set_xlabel("t [s]")
    ax2.set_ylabel("ball speed [m/s]")
    ax2.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(outdir / f"launch_{tag}.png", dpi=130)
    plt.close(fig)


if __name__ == "__main__":
    main()
