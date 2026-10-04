"""MuJoCo full-flow simulation of the C06B-POLLEN-FEEDER-V2 launcher.

Flow: ball enters at the right end of the 5 deg gravity tray -> rolls down and
wedges at the 225 deg shell lip -> the three-paddle rotor carries it along the
shell inner wall (225 deg -> 142 deg, i.e. about 99 deg of paddle travel) -> the
ball is released tangentially on the 52 deg channel centreline -> it travels to
the opposed-flywheel nip -> the flywheels launch it.

Geometry comes from cad/paddle_launcher_feeder_redesign.py (V2 generator) and
cad/paddle_launcher_constrained.py (parent: the 52 deg roof, both side walls and
the +55 throat cheek stay exactly where the parent put them).  MuJoCo only
supports convex collision shapes, so the concave shell is approximated by a
chain of boxes that follow the real arc.

World frame = CAD chassis frame, millimetres scaled to metres.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

MM = 0.001
HERE = Path(__file__).resolve().parent

# ------------------------------------------------------------------ V2 design
ANGLE = 52.0
HALF_SPACING = 80.0
WHEEL_R = 48.0
WHEEL_W = 24.0
WHEEL_AXIAL_GAP = 6.0
WHEEL_Y = (-(WHEEL_W + WHEEL_AXIAL_GAP) / 2.0, (WHEEL_W + WHEEL_AXIAL_GAP) / 2.0)
CHANNEL_CLEAR_W = 108.0
CHANNEL_CLEAR_H = 110.0
THROAT_LENGTH = 83.0
PADDLE_CX, PADDLE_CZ = 29.49, 111.46
PADDLE_CENTER = (PADDLE_CX, 0.0, PADDLE_CZ)
PADDLE_SWEEP_R = 60.0
PADDLE_W = 96.0
PADDLE_PHASE = 18.0
BALL_D = 71.12
BALL_R = BALL_D / 2.0
BALL_MASS = 0.060          # kg, ASSUMED
FLYWHEEL_MASS = 0.105
FLYWHEEL_SHAFT_MASS = 0.050
R_CARRY = 58.4
SHELL_WALL = 7.0
R_IN = R_CARRY + BALL_R    # 93.96
R_OUT = R_IN + SHELL_WALL  # 100.96
A_LIP = 225.0
A_EXIT = 142.0
FEEDER_W = CHANNEL_CLEAR_W
TILT = 5.0
PIVOT_X, PIVOT_Z = -2.30, 17.50
TRAY_T = 6.0
TRAY_X0, TRAY_X1 = -56.0, 150.0
STRUT_X0, STRUT_X1 = -41.90, -36.95
STRUT_Z0, STRUT_Z1 = 14.00, 45.00
GUIDE_SPEC = [((-150.0, 16.0), 70.0, 0.0), (None, 55.0, 26.0), (None, 70.0, ANGLE)]


def direction(angle):
    a = math.radians(angle)
    return math.cos(a), math.sin(a)


def normal(angle):
    a = math.radians(angle)
    return -math.sin(a), math.cos(a)


def _segments():
    out, start = [], GUIDE_SPEC[0][0]
    for _, length, angle in GUIDE_SPEC:
        tx, tz = direction(angle)
        end = (start[0] + length * tx, start[1] + length * tz)
        out.append((start, end, length, angle))
        start = end
    return out


SEGS = _segments()
G52 = SEGS[2]
GUIDE_END = G52[1]
N52 = normal(ANGLE)
T52 = direction(ANGLE)
THROAT_CENTER = (GUIDE_END[0] + 55.0 * N52[0], GUIDE_END[1] + 55.0 * N52[1])
SHOOTER_ORIGIN = (THROAT_CENTER[0] + 135.0 * T52[0], 0.0, THROAT_CENTER[1] + 135.0 * T52[1])


def to_world(x, y, z):
    a = math.radians(-ANGLE)
    return (x * math.cos(a) + z * math.sin(a) + SHOOTER_ORIGIN[0],
            y + SHOOTER_ORIGIN[1],
            -x * math.sin(a) + z * math.cos(a) + SHOOTER_ORIGIN[2])


def to_shooter(px, pz):
    dx, dz = px - SHOOTER_ORIGIN[0], pz - SHOOTER_ORIGIN[2]
    return dx * T52[0] + dz * T52[1], dx * N52[0] + dz * N52[1]


def quat_y(deg):
    h = math.radians(deg) / 2.0
    return (math.cos(h), 0.0, math.sin(h), 0.0)


def quat_x(deg):
    h = math.radians(deg) / 2.0
    return (math.cos(h), math.sin(h), 0.0, 0.0)


def rot_local(center, deg):
    a = math.radians(deg)
    x, y, z = center
    return (x * math.cos(a) + z * math.sin(a), y, -x * math.sin(a) + z * math.cos(a))


def polar(r, angle_deg):
    a = math.radians(angle_deg)
    return (PADDLE_CX + r * math.cos(a), PADDLE_CZ + r * math.sin(a))


def tray_top_z(x):
    return PIVOT_Z + (x - PIVOT_X) * math.tan(math.radians(TILT))


def flywheel_axle_center(sign):
    return to_world(0.0, 0.0, sign * HALF_SPACING)


# ------------------------------------------------------------------- geometry
def static_geoms():
    """(name, class, type, size, pos, quat) in the world (chassis) frame, mm."""
    g = []
    start, end, length, angle = G52
    mx, mz = (start[0] + end[0]) / 2.0, (start[1] + end[1]) / 2.0
    nx, nz = N52
    g.append(("guide_roof_3", "guide", "box", (length, CHANNEL_CLEAR_W + 6.0, 3.0),
              (mx + CHANNEL_CLEAR_H * nx, 0.0, mz + CHANNEL_CLEAR_H * nz), quat_y(-angle)))
    for side in (-1, 1):
        g.append((f"guide_wall_3_{side:+d}", "guide", "box", (length, 3.0, CHANNEL_CLEAR_H),
                  (mx + CHANNEL_CLEAR_H / 2.0 * nx, side * (CHANNEL_CLEAR_W / 2.0 + 1.5),
                   mz + CHANNEL_CLEAR_H / 2.0 * nz), quat_y(-angle)))
    g.append(("shooter_throat_+55", "guide", "box", (THROAT_LENGTH, CHANNEL_CLEAR_W + 6.0, 3.0),
              to_world(-135.0 + THROAT_LENGTH / 2.0, 0.0, 55.0), quat_y(-ANGLE)))
    r_mid = 0.5 * (R_IN + R_OUT)
    radial = R_OUT - R_IN
    n = 24
    for i in range(n):
        a0 = A_EXIT + (A_LIP - A_EXIT) * i / n
        a1 = A_EXIT + (A_LIP - A_EXIT) * (i + 1) / n
        am = 0.5 * (a0 + a1)
        half = 0.5 * r_mid * math.radians(a1 - a0) * 1.35
        cx, cz = polar(r_mid, am)
        g.append((f"shell_{i:02d}", "shell", "box", (2.0 * half, FEEDER_W, radial),
                  (cx, 0.0, cz), quat_y(-(am + 90.0))))
    for tag, ang in (("lip", A_LIP), ("exit", A_EXIT)):
        cx, cz = polar(r_mid, ang)
        g.append((f"shell_{tag}_face", "shell", "box", (radial, FEEDER_W, 3.0),
                  (cx, 0.0, cz), quat_y(-ang)))
    nmx, nmz = normal(-TILT)
    x_mid = 0.5 * (TRAY_X0 + TRAY_X1)
    zt = tray_top_z(x_mid)
    L = (TRAY_X1 - TRAY_X0) / math.cos(math.radians(TILT))
    g.append(("tray", "shell", "box", (L, FEEDER_W, TRAY_T),
              (x_mid - nmx * TRAY_T / 2.0, 0.0, zt - nmz * TRAY_T / 2.0), quat_y(-TILT)))
    g.append(("strut", "shell", "box", (STRUT_X1 - STRUT_X0, FEEDER_W, STRUT_Z1 - STRUT_Z0),
              (0.5 * (STRUT_X0 + STRUT_X1), 0.0, 0.5 * (STRUT_Z0 + STRUT_Z1)), quat_y(0.0)))
    return g


def paddle_parts():
    parts = [("hub", (0.0, 0.0, 0.0), (18.0, 17.0, 18.0), 0.0, "cylY")]
    for i, a in enumerate((PADDLE_PHASE, PADDLE_PHASE + 120.0, PADDLE_PHASE + 240.0), 1):
        parts.append((f"arm_{i}", (30.0, 0.0, 0.0), (16.0, 9.0, 5.0), a, "box"))
        parts.append((f"blade_{i}", (52.0, 0.0, 0.0), (6.0, PADDLE_W / 2.0, 15.0), a, "box"))
        parts.append((f"flex_{i}", (58.0, 0.0, 0.0), (2.0, PADDLE_W / 2.0, 17.0), a, "box"))
    return parts


# ----------------------------------------------------------------------- MJCF
def _f(v):
    return f"{v:.6f}"


def build_xml(rpm, spin_sign, paddle_omega, ball_x, ball_z, ball_vx=0.0, ball_vz=0.0):
    m = MM
    L = []
    w = L.append
    w('<mujoco model="t06_pollen_launcher_v2">')
    w('  <compiler angle="radian" autolimits="true"/>')
    w('  <option timestep="0.0002" gravity="0 0 -9.81" integrator="implicitfast" cone="elliptic"/>')
    w('  <default>')
    w('    <geom friction="0.5 0.01 0.0001" solref="0.008 1" solimp="0.95 0.99 0.001"/>')
    w('    <default class="guide"><geom friction="0.25 0.005 0.0001" rgba="0.2 0.56 0.84 0.45"/></default>')
    w('    <default class="shell"><geom friction="0.25 0.005 0.0001" rgba="0.2 0.56 0.84 0.45"/></default>')
    w('    <default class="flywheel"><geom friction="1.6 0.02 0.0001" solref="0.006 1" rgba="0.18 0.18 0.20 1"/></default>')
    w('    <default class="paddle"><geom friction="0.7 0.01 0.0001" solref="0.006 1" rgba="0.92 0.54 0.12 1"/></default>')
    w('    <default class="ball"><geom friction="1.0 0.02 0.0001" solref="0.010 1" solimp="0.9 0.95 0.002" rgba="0.95 0.85 0.15 1" priority="1"/></default>')
    w('  </default>')
    w('  <worldbody>')
    w('    <light pos="0.2 -0.6 1.0" dir="-0.2 0.6 -1" diffuse="0.8 0.8 0.8"/>')
    for name, cls, kind, size, pos, q in static_geoms():
        w(f'    <geom name="{name}" class="{cls}" type="{kind}" '
          f'size="{_f(size[0] / 2 * m)} {_f(size[1] / 2 * m)} {_f(size[2] / 2 * m)}" '
          f'pos="{_f(pos[0] * m)} {_f(pos[1] * m)} {_f(pos[2] * m)}" '
          f'quat="{q[0]:.6f} {q[1]:.6f} {q[2]:.6f} {q[3]:.6f}"/>')
    qx = quat_x(-90)
    for sign, label in ((1, "upper"), (-1, "lower")):
        cx, cy, cz = flywheel_axle_center(sign)
        w(f'  <body name="flywheel_{label}" pos="{_f(cx * m)} {_f(cy * m)} {_f(cz * m)}">')
        w(f'    <joint name="fw_{label}" type="hinge" axis="0 1 0" damping="0.0002"/>')
        w(f'    <geom name="fw_shaft_{label}" class="flywheel" type="cylinder" '
          f'size="{_f(4.0 * m)} {_f(84.0 * m)}" quat="{qx[0]:.6f} {qx[1]:.6f} 0 0" mass="{FLYWHEEL_SHAFT_MASS}"/>')
        for i, y in enumerate(WHEEL_Y, 1):
            w(f'    <geom name="fw_{label}_{i}" class="flywheel" type="cylinder" '
              f'size="{_f(WHEEL_R * m)} {_f(WHEEL_W / 2 * m)}" pos="0 {_f(y * m)} 0" '
              f'quat="{qx[0]:.6f} {qx[1]:.6f} 0 0" mass="{FLYWHEEL_MASS}"/>')
        w('  </body>')
    px, py, pz = PADDLE_CENTER
    w(f'  <body name="paddle" pos="{_f(px * m)} {_f(py * m)} {_f(pz * m)}">')
    w('    <joint name="paddle_joint" type="hinge" axis="0 1 0" damping="0.0005"/>')
    for name, center, half, ang, kind in paddle_parts():
        c = rot_local(center, ang)
        if kind == "cylY":
            w(f'    <geom name="paddle_{name}" class="paddle" type="cylinder" '
              f'size="{_f(half[0] * m)} {_f(half[1] * m)}" quat="{qx[0]:.6f} {qx[1]:.6f} 0 0" mass="0.05"/>')
        else:
            mass = 0.010 if name.startswith("arm") else (0.020 if name.startswith("blade") else 0.008)
            q = quat_y(ang)
            w(f'    <geom name="paddle_{name}" class="paddle" type="box" '
              f'size="{_f(half[0] * m)} {_f(half[1] * m)} {_f(half[2] * m)}" '
              f'pos="{_f(c[0] * m)} {_f(c[1] * m)} {_f(c[2] * m)}" '
              f'quat="{q[0]:.6f} {q[1]:.6f} {q[2]:.6f} {q[3]:.6f}" mass="{mass}"/>')
    w('  </body>')
    w(f'  <body name="ball" pos="{_f(ball_x * m)} 0 {_f(ball_z * m)}">')
    w('    <freejoint name="ball_free"/>')
    w(f'    <geom name="ball_geom" class="ball" type="sphere" size="{_f(BALL_R * m)}" mass="{BALL_MASS}"/>')
    w('  </body>')
    w('  </worldbody>')
    fw = spin_sign * rpm * 2.0 * math.pi / 60.0
    w('  <actuator>')
    w(f'    <velocity name="fw_upper_vel" joint="fw_upper" kv="0.5" ctrlrange="-400 400" forcerange="-3.0 3.0"/>')
    w(f'    <velocity name="fw_lower_vel" joint="fw_lower" kv="0.5" ctrlrange="-400 400" forcerange="-3.0 3.0"/>')
    w(f'    <velocity name="paddle_vel" joint="paddle_joint" kv="0.08" ctrlrange="-100 100" forcerange="-1.5 1.5"/>')
    w('  </actuator>')
    w('</mujoco>')
    return "\n".join(L), [fw, -fw, paddle_omega]


# ------------------------------------------------------------------ simulate
def simulate(xml, seconds, ctrl, sample_dt=0.002):
    import mujoco
    import numpy as np

    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)
    data.ctrl[:] = ctrl
    mujoco.mj_forward(model, data)
    bid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "ball")
    dt = model.opt.timestep
    every = max(1, int(round(sample_dt / dt)))
    trace = []
    for i in range(int(round(seconds / dt))):
        mujoco.mj_step(model, data)
        if i % every == 0:
            p = data.xpos[bid]
            v = data.cvel[bid][3:]
            px, pz = float(p[0]) * 1000.0, float(p[2]) * 1000.0
            rx, rz = px - PADDLE_CX, pz - PADDLE_CZ
            lx, lz = to_shooter(px, pz)
            trace.append({
                "t": round(i * dt, 4),
                "x": round(px, 3), "z": round(pz, 3),
                "v": round(float(np.linalg.norm(v)), 4),
                "vx": round(float(v[0]), 4), "vz": round(float(v[2]), 4),
                "r": round(math.hypot(rx, rz), 3),
                "ang": round(math.degrees(math.atan2(rz, rx)) % 360.0, 2),
                "lx": round(lx, 3), "lz": round(lz, 3),
            })
    return trace


def analyse(trace):
    peak = max(trace, key=lambda s: s["v"])
    carried = [s for s in trace if 130.0 <= s["ang"] <= 232.0 and 45.0 <= s["r"] <= 70.0]
    entered = any(s["ang"] < 224.0 and 45.0 <= s["r"] <= 70.0 for s in trace)
    reached_exit = [s for s in trace if s["ang"] <= 143.0 and 45.0 <= s["r"] <= 70.0]
    rest = trace[0]
    rest_idx = max(range(len(trace)), key=lambda i: trace[i]["t"] if trace[i]["v"] < 0.02 and trace[i]["t"] < 3.0 else -1)
    passed_nip = [s for s in trace if s["lx"] > 0.0]
    fast = [s for s in trace if s["lx"] > -20.0 and s["v"] > 3.0]
    out = {
        "peak_speed_m_s": peak["v"], "peak_speed_t": peak["t"],
        "rest_position_mm": [rest["x"], rest["z"]],
        "settled_position_mm": [trace[rest_idx]["x"], trace[rest_idx]["z"]],
        "min_angle_deg": min(s["ang"] for s in trace),
        "entered_shell": entered,
        "reached_142deg_exit": bool(reached_exit),
        "release_speed_m_s": round(reached_exit[0]["v"], 3) if reached_exit else 0.0,
        "max_lx_mm": max(s["lx"] for s in trace),
        "passed_nip": bool(passed_nip),
        "launched": bool(fast),
        "max_z_mm": max(s["z"] for s in trace),
        "final_mm": [trace[-1]["x"], trace[-1]["z"]],
    }
    if passed_nip:
        idx = next(i for i, s in enumerate(trace) if s["lx"] > 40.0) if any(s["lx"] > 40.0 for s in trace) else None
        if idx is not None:
            s = trace[idx]
            vx, vz = s["vx"], s["vz"]
            out["exit"] = {
                "t": s["t"], "speed_m_s": round(math.hypot(vx, vz), 3),
                "angle_deg": round(math.degrees(math.atan2(vz, vx)), 2),
                "apex_above_exit_mm": round(vz * vz / (2 * 9.81) * 1000.0, 1),
                "range_same_height_m": round(2 * vx * vz / 9.81, 2),
            }
    return out


def main():
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="V2 POLLEN launcher full-flow MuJoCo run")
    ap.add_argument("--rpm", type=float, default=1620.0)
    ap.add_argument("--paddle-rpm", type=float, default=40.0)
    ap.add_argument("--paddle-sign", type=int, default=1, choices=(-1, 1),
                    help="+1 = rotation about +Y (ball carried 241 deg -> 142 deg)")
    ap.add_argument("--spin-sign", type=int, default=-1, choices=(-1, 1))
    ap.add_argument("--seconds", type=float, default=6.0)
    ap.add_argument("--ball-x", type=float, default=145.0)
    ap.add_argument("--ball-z", type=float, default=None)
    ap.add_argument("--tag", default="v2")
    ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--outdir", default=str(HERE / "out"))
    args = ap.parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    def run(tag, paddle_rpm, paddle_sign):
        omega = paddle_sign * paddle_rpm * 2.0 * math.pi / 60.0
        bz = args.ball_z if args.ball_z is not None else tray_top_z(args.ball_x) + BALL_R
        xml, ctrl = build_xml(args.rpm, args.spin_sign, omega, args.ball_x, bz)
        (outdir / f"model_{tag}.xml").write_text(xml, encoding="utf-8")
        trace = simulate(xml, args.seconds, ctrl)
        res = analyse(trace)
        res.update({"tag": tag, "paddle_rpm": paddle_rpm, "paddle_sign": paddle_sign,
                    "flywheel_rpm": args.rpm, "ball_start_mm": [args.ball_x, round(bz, 3)],
                    "seconds": args.seconds})
        (outdir / f"trace_{tag}.json").write_text(json.dumps(trace), encoding="utf-8")
        return res, trace

    results = []
    if args.sweep:
        for rpm in (25.0, 40.0, 100.0, 200.0, 320.0):
            res, _ = run(f"v2_paddle{int(rpm)}", rpm, args.paddle_sign)
            results.append(res)
            print(json.dumps(res, ensure_ascii=False), flush=True)
    else:
        res, _ = run(args.tag, args.paddle_rpm, args.paddle_sign)
        results.append(res)
        print(json.dumps(res, indent=2, ensure_ascii=False), flush=True)
    (outdir / f"summary_{args.tag}.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print("summary -> " + str(outdir / f"summary_{args.tag}.json"), flush=True)


if __name__ == "__main__":
    main()
