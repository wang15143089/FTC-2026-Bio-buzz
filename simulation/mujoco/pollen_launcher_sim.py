"""MuJoCo motion simulation of the T06 C06-B opposed-flywheel launcher (POLLEN).

The geometry is generated from the same formulas as
``cad/paddle_launcher_constrained.py`` -- the parent assembly of
``cad/output/paddle_launcher_motion_free_fingers_pollen.step`` -- so the
simulation runs the real launcher layout with convex primitive collision shapes
(the channel and the 3-paddle rotor are concave, and MuJoCo uses convex shapes).

World frame = CAD frame: chassis X-Y plane, +Z up, mm scaled to m for MuJoCo.
Flywheel and paddle axes are +Y.

Usage:
    python simulation/mujoco/pollen_launcher_sim.py --sweep
    python simulation/mujoco/pollen_launcher_sim.py --paddle-sign -1 --spin-sign -1
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

MM = 0.001
HERE = Path(__file__).resolve().parent

# --------------------------------------------------------------------------
# Geometry constants (POLLEN configuration, half_spacing = 80 mm)
# --------------------------------------------------------------------------
ANGLE = 52.0
HALF_SPACING = 80.0
WHEEL_OD = 96.0
WHEEL_R = WHEEL_OD / 2.0
WHEEL_W = 24.0
WHEEL_AXIAL_GAP = 6.0
WHEEL_Y = (-(WHEEL_W + WHEEL_AXIAL_GAP) / 2.0, (WHEEL_W + WHEEL_AXIAL_GAP) / 2.0)
CHANNEL_CLEAR_W = 108.0
CHANNEL_CLEAR_H = 110.0
PADDLE_CENTER = (-47.0, 0.0, 73.0)
PADDLE_SWEEP_R = 60.0
PADDLE_W = 96.0
PADDLE_PHASE = 18.0
GUIDE_SPEC = [((-150.0, 16.0), 70.0, 0.0), (None, 55.0, 26.0), (None, 70.0, ANGLE)]
THROAT_LENGTH = 83.0

BALL_D = 71.12            # measured from the supplied Pollen STEP
BALL_R = BALL_D / 2.0
BALL_MASS = 0.060         # kg, ASSUMED
FLYWHEEL_MASS = 0.105     # kg each (vendor sheet)
FLYWHEEL_SHAFT_MASS = 0.050


def direction(angle):
    a = math.radians(angle)
    return math.cos(a), math.sin(a)


def normal(angle):
    a = math.radians(angle)
    return -math.sin(a), math.cos(a)


def guide_segments():
    result, start = [], GUIDE_SPEC[0][0]
    for _, length, angle in GUIDE_SPEC:
        tx, tz = direction(angle)
        end = (start[0] + length * tx, start[1] + length * tz)
        result.append((start, end, length, angle))
        start = end
    return result


GUIDES = guide_segments()
GUIDE_END = GUIDES[-1][1]
N52 = normal(ANGLE)
T52 = direction(ANGLE)
THROAT_CENTER = (GUIDE_END[0] + 55.0 * N52[0], GUIDE_END[1] + 55.0 * N52[1])
SHOOTER_ORIGIN = (THROAT_CENTER[0] + 135.0 * T52[0], 0.0,
                  THROAT_CENTER[1] + 135.0 * T52[1])


def to_world(x, y, z):
    a = math.radians(-ANGLE)
    return (x * math.cos(a) + z * math.sin(a) + SHOOTER_ORIGIN[0],
            y + SHOOTER_ORIGIN[1],
            -x * math.sin(a) + z * math.cos(a) + SHOOTER_ORIGIN[2])


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


# --------------------------------------------------------------------------
# Panels
# --------------------------------------------------------------------------
def panel_box(start, end, angle, kind, side=0):
    length = math.dist(start, end)
    mx, mz = (start[0] + end[0]) / 2.0, (start[1] + end[1]) / 2.0
    nx, nz = normal(angle)
    if kind == "floor":
        center, size = (mx, 0.0, mz), (length, CHANNEL_CLEAR_W + 6.0, 3.0)
    elif kind == "roof":
        center = (mx + CHANNEL_CLEAR_H * nx, 0.0, mz + CHANNEL_CLEAR_H * nz)
        size = (length, CHANNEL_CLEAR_W + 6.0, 3.0)
    else:
        center = (mx + CHANNEL_CLEAR_H / 2.0 * nx,
                  side * (CHANNEL_CLEAR_W / 2.0 + 1.5),
                  mz + CHANNEL_CLEAR_H / 2.0 * nz)
        size = (length, 3.0, CHANNEL_CLEAR_H)
    return center, size, -angle


def clip_drum(panel):
    """Drop the part of a floor/roof panel that lies inside the paddle drum."""
    center, size, rot = panel
    length, half_v = size[0], size[2] / 2.0
    ux, uz = direction(-rot)
    vx, vz = normal(-rot)
    px, pz = PADDLE_CENTER[0], PADDLE_CENTER[2]
    n = max(2, int(math.ceil(length / 4.0)))
    step = length / n
    out = []
    for i in range(n):
        u = -length / 2.0 + (i + 0.5) * step
        cx, cz = center[0] + u * ux, center[2] + u * uz
        du = max(0.0, abs((px - cx) * ux + (pz - cz) * uz) - step / 2.0)
        dv = max(0.0, abs((px - cx) * vx + (pz - cz) * vz) - half_v)
        if math.hypot(du, dv) < PADDLE_SWEEP_R + 3.0:
            continue
        out.append(((cx, center[1], cz), (step, size[1], size[2]), rot))
    return out


def static_geoms():
    geoms = []
    for i, (start, end, _, angle) in enumerate(GUIDES, 1):
        geoms.append((f"guide_floor_{i}", panel_box(start, end, angle, "floor"), "guide"))
        geoms.append((f"guide_roof_{i}", panel_box(start, end, angle, "roof"), "guide"))
        for side in (-1, 1):
            geoms.append((f"guide_wall_{i}_{side:+d}",
                          panel_box(start, end, angle, "wall", side), "guide"))
    for n in (-55.0, 55.0):
        center = to_world(-135.0 + THROAT_LENGTH / 2.0, 0.0, n)
        geoms.append((f"throat_{n:+.0f}",
                      (center, (THROAT_LENGTH, CHANNEL_CLEAR_W + 6.0, 3.0), -ANGLE), "guide"))
    anchor = GUIDES[-1][0]
    for side in (-1, 1):
        c = (anchor[0] + 16.0, side * 38.0, anchor[1] + 25.0)
        geoms.append((f"finger_{side:+d}", (c, (38.0, 1.2, 44.0), -ANGLE), "finger"))
    return geoms


def flywheel_axle_center(sign):
    return to_world(0.0, 0.0, sign * HALF_SPACING)


def paddle_parts():
    parts = [("hub", (0.0, 0.0, 0.0), (18.0, 17.0, 18.0), 0.0, "cylY")]
    for i, a in enumerate((PADDLE_PHASE, PADDLE_PHASE + 120.0, PADDLE_PHASE + 240.0), 1):
        parts.append((f"arm_{i}", (30.0, 0.0, 0.0), (16.0, 9.0, 5.0), a, "box"))
        parts.append((f"blade_{i}", (52.0, 0.0, 0.0), (6.0, PADDLE_W / 2.0, 15.0), a, "box"))
        parts.append((f"flex_{i}", (58.0, 0.0, 0.0), (2.0, PADDLE_W / 2.0, 17.0), a, "box"))
    return parts


# --------------------------------------------------------------------------
# MJCF
# --------------------------------------------------------------------------
def build_xml(rpm, paddle_omega, spin_sign, ball_x, ball_z):
    m = MM
    L = []
    w = L.append
    w('<mujoco model="t06_pollen_launcher">')
    w('  <compiler angle="radian" autolimits="true"/>')
    w('  <option timestep="0.0002" gravity="0 0 -9.81" integrator="implicitfast" cone="elliptic"/>')
    w('  <default>')
    w('    <geom friction="0.5 0.01 0.0001" solref="0.008 1" solimp="0.95 0.99 0.001"/>')
    w('    <default class="guide"><geom friction="0.25 0.005 0.0001" rgba="0.2 0.56 0.84 0.55"/></default>')
    w('    <default class="finger"><geom friction="0.2 0.005 0.0001" rgba="0.76 0.88 0.96 0.7"/></default>')
    w('    <default class="flywheel"><geom friction="1.6 0.02 0.0001" solref="0.006 1" rgba="0.18 0.18 0.20 1"/></default>')
    w('    <default class="paddle"><geom friction="0.7 0.01 0.0001" solref="0.006 1" rgba="0.92 0.54 0.12 1"/></default>')
    w('    <default class="ball"><geom friction="1.0 0.02 0.0001" solref="0.010 1" solimp="0.9 0.95 0.002" rgba="0.95 0.85 0.15 1" priority="1"/></default>')
    w('  </default>')
    w('  <worldbody>')
    w('    <light pos="0.2 -0.6 1.0" dir="-0.2 0.6 -1" diffuse="0.8 0.8 0.8"/>')
    for name, panel, cls in static_geoms():
        pieces = clip_drum(panel) if name.startswith(("guide_floor", "guide_roof")) else [panel]
        for k, (center, size, rot) in enumerate(pieces):
            q = quat_y(rot)
            w(f'    <geom name="{name}_{k}" class="{cls}" type="box" '
              f'size="{size[0]/2*m:.6f} {size[1]/2*m:.6f} {size[2]/2*m:.6f}" '
              f'pos="{center[0]*m:.6f} {center[1]*m:.6f} {center[2]*m:.6f}" '
              f'quat="{q[0]:.6f} {q[1]:.6f} {q[2]:.6f} {q[3]:.6f}"/>')
    qx = quat_x(-90)
    for sign, label in ((1, "upper"), (-1, "lower")):
        cx, cy, cz = flywheel_axle_center(sign)
        w(f'  <body name="flywheel_{label}" pos="{cx*m:.6f} {cy*m:.6f} {cz*m:.6f}">')
        w(f'    <joint name="fw_{label}" type="hinge" axis="0 1 0" damping="0.0002"/>')
        w(f'    <geom name="fw_shaft_{label}" class="flywheel" type="cylinder" '
          f'size="{4.0*m:.6f} {84.0*m:.6f}" quat="{qx[0]:.6f} {qx[1]:.6f} 0 0" mass="{FLYWHEEL_SHAFT_MASS}"/>')
        for i, y in enumerate(WHEEL_Y, 1):
            w(f'    <geom name="fw_{label}_{i}" class="flywheel" type="cylinder" '
              f'size="{WHEEL_R*m:.6f} {WHEEL_W/2*m:.6f}" pos="0 {y*m:.6f} 0" '
              f'quat="{qx[0]:.6f} {qx[1]:.6f} 0 0" mass="{FLYWHEEL_MASS}"/>')
        w('  </body>')
    px, py, pz = PADDLE_CENTER
    w(f'  <body name="paddle" pos="{px*m:.6f} {py*m:.6f} {pz*m:.6f}">')
    w('    <joint name="paddle_joint" type="hinge" axis="0 1 0" damping="0.0005"/>')
    for name, center, half, ang, kind in paddle_parts():
        c = rot_local(center, ang)
        if kind == "cylY":
            w(f'    <geom name="paddle_{name}" class="paddle" type="cylinder" '
              f'size="{half[0]*m:.6f} {half[1]*m:.6f}" quat="{qx[0]:.6f} {qx[1]:.6f} 0 0" mass="0.05"/>')
        else:
            mass = 0.010 if name.startswith("arm") else (0.020 if name.startswith("blade") else 0.008)
            q = quat_y(ang)
            w(f'    <geom name="paddle_{name}" class="paddle" type="box" '
              f'size="{half[0]*m:.6f} {half[1]*m:.6f} {half[2]*m:.6f}" '
              f'pos="{c[0]*m:.6f} {c[1]*m:.6f} {c[2]*m:.6f}" '
              f'quat="{q[0]:.6f} {q[1]:.6f} {q[2]:.6f} {q[3]:.6f}" mass="{mass}"/>')
    w('  </body>')
    w(f'  <body name="ball" pos="{ball_x*m:.6f} 0 {ball_z*m:.6f}">')
    w('    <freejoint name="ball_free"/>')
    w(f'    <geom name="ball_geom" class="ball" type="sphere" size="{BALL_R*m:.6f}" mass="{BALL_MASS}"/>')
    w('  </body>')
    w('  </worldbody>')
    fw = spin_sign * rpm * 2.0 * math.pi / 60.0
    w('  <actuator>')
    w(f'    <velocity name="fw_upper_vel" joint="fw_upper" kv="0.5" ctrlrange="-400 400" forcerange="-3.0 3.0"/>')
    w(f'    <velocity name="fw_lower_vel" joint="fw_lower" kv="0.5" ctrlrange="-400 400" forcerange="-3.0 3.0"/>')
    w(f'    <velocity name="paddle_vel" joint="paddle_joint" kv="0.08" ctrlrange="-100 100" forcerange="-0.6 0.6"/>')
    w('  </actuator>')
    w('  <sensor>')
    w('    <framepos name="ball_pos" objtype="body" objname="ball"/>')
    w('    <framelinvel name="ball_vel" objtype="body" objname="ball"/>')
    w('  </sensor>')
    w('</mujoco>')
    return "\n".join(L), [fw, -fw, paddle_omega]


# --------------------------------------------------------------------------
def simulate(xml, seconds, ctrl, sample_dt=0.004):
    import numpy as np
    import mujoco

    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)
    data.ctrl[:] = ctrl
    mujoco.mj_forward(model, data)
    bid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "ball")
    dt = model.opt.timestep
    every = max(1, int(round(sample_dt / dt)))
    trace = []
    peak = {"speed": 0.0, "time": 0.0}
    for i in range(int(round(seconds / dt))):
        mujoco.mj_step(model, data)
        if i % every == 0:
            p = data.xpos[bid]
            v = data.cvel[bid][3:]
            s = float(np.linalg.norm(v))
            if p[2] > 0.05 and s > peak["speed"]:
                peak = {"speed": s, "time": round(i * dt, 3)}
            trace.append((round(i * dt, 4), round(float(p[0]), 4), round(float(p[1]), 4),
                          round(float(p[2]), 4), round(s, 3)))
    return trace, peak


def run_case(tag, args, paddle_sign, spin_sign, outdir):
    omega = paddle_sign * args.paddle_rpm * 2.0 * math.pi / 60.0
    xml, ctrl = build_xml(args.rpm, omega, spin_sign, args.ball_x, args.ball_z)
    (outdir / f"model_{tag}.xml").write_text(xml, encoding="utf-8")
    trace, peak = simulate(xml, args.seconds, ctrl)
    result = {
        "tag": tag,
        "paddle_sign_about_plus_y": paddle_sign,
        "spin_sign_upper": spin_sign,
        "paddle_rpm": args.paddle_rpm * paddle_sign,
        "flywheel_rpm": args.rpm,
        "seconds": args.seconds,
        "peak_speed_above_z50_m_s": round(peak["speed"], 3),
        "peak_time_s": peak["time"],
        "final": trace[-1],
        "max_z_m": round(max(t[3] for t in trace), 3),
        "max_x_m": round(max(t[1] for t in trace), 3),
    }
    (outdir / f"trace_{tag}.json").write_text(json.dumps(trace), encoding="utf-8")
    return result, trace


def plot_case(tag, trace, outdir, title):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9, 7))
    for name, panel, cls in static_geoms():
        pieces = clip_drum(panel) if name.startswith(("guide_floor", "guide_roof")) else [panel]
        for center, size, rot in pieces:
            a = math.radians(rot)
            hx, hz = size[0] / 2.0, size[2] / 2.0
            pts = [(-hx, -hz), (hx, -hz), (hx, hz), (-hx, hz), (-hx, -hz)]
            xs, zs = [], []
            for u, v in pts:
                xs.append(center[0] + u * math.cos(a) + v * math.sin(a))
                zs.append(center[2] - u * math.sin(a) + v * math.cos(a))
            ax.plot(xs, zs, "-", color="#2f8fd4", lw=0.6)
    ax.add_patch(plt.Circle((PADDLE_CENTER[0], PADDLE_CENTER[2]), PADDLE_SWEEP_R + 3,
                            fill=False, color="0.4", ls="--", lw=0.8))
    for sign in (1, -1):
        cx, _, cz = flywheel_axle_center(sign)
        ax.add_patch(plt.Circle((cx, cz), WHEEL_R, fill=False, color="k", lw=1.2))
        ax.plot([cx], [cz], "k+", ms=8)
    for name, center, half, ang, kind in paddle_parts():
        if kind != "box":
            continue
        a = math.radians(ang)
        c = rot_local(center, ang)
        hx, hz = half[0], half[2]
        pts = [(-hx, -hz), (hx, -hz), (hx, hz), (-hx, hz), (-hx, -hz)]
        xs = [PADDLE_CENTER[0] + c[0] + u * math.cos(a) + v * math.sin(a) for u, v in pts]
        zs = [PADDLE_CENTER[2] + c[2] - u * math.sin(a) + v * math.cos(a) for u, v in pts]
        ax.plot(xs, zs, "-", color="orange", lw=1.0)
    ax.plot([t[1] * 1000 for t in trace], [t[3] * 1000 for t in trace], "-",
            color="crimson", lw=1.8, label="ball centre")
    ax.plot([trace[0][1] * 1000], [trace[0][3] * 1000], "o", color="crimson", ms=5)
    ax.set_aspect("equal")
    ax.set_xlabel("X [mm]")
    ax.set_ylabel("Z [mm]")
    ax.set_title(title)
    ax.grid(alpha=0.25)
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    fig.savefig(outdir / f"trajectory_{tag}.png", dpi=130)
    plt.close(fig)


def main():
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rpm", type=float, default=1620.0, help="flywheel no-load speed")
    ap.add_argument("--paddle-rpm", type=float, default=30.0)
    ap.add_argument("--paddle-sign", type=int, default=-1, choices=(-1, 1))
    ap.add_argument("--spin-sign", type=int, default=-1, choices=(-1, 1))
    ap.add_argument("--seconds", type=float, default=4.0)
    ap.add_argument("--ball-x", type=float, default=-128.0)
    ap.add_argument("--ball-z", type=float, default=17.5 + BALL_R)
    ap.add_argument("--outdir", default=str(HERE / "out"))
    ap.add_argument("--sweep", action="store_true", help="run all four direction combinations")
    args = ap.parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    results = []
    combos = [(ps, ss) for ps in (-1, 1) for ss in (-1, 1)] if args.sweep \
        else [(args.paddle_sign, args.spin_sign)]
    for ps, ss in combos:
        tag = f"paddle{'m' if ps < 0 else 'p'}_spin{'m' if ss < 0 else 'p'}"
        res, trace = run_case(tag, args, ps, ss, outdir)
        results.append(res)
        print(json.dumps(res, ensure_ascii=False), flush=True)
        if args.sweep:
            plot_case(tag, trace, outdir, f"{tag}  peak {res['peak_speed_above_z50_m_s']} m/s")
    (outdir / "summary.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print("\nsummary -> " + str(outdir / "summary.json"), flush=True)


if __name__ == "__main__":
    main()
