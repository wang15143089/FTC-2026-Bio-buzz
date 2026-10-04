"""Plot why the under-paddle lift stalls: ball trajectory vs the channel panels."""
from __future__ import annotations
import json, math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
import pollen_launcher_sim as P
import feeder_fair_test as F

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
OUT = Path(__file__).resolve().parent.parent / "out"
FLOOR_TOP = 17.5


def strip_named(xml, prefixes):
    return "\n".join(l for l in xml.splitlines()
                     if not (any(p in l for p in prefixes) and "<geom" in l))


def trace(bx, psign, prpm, prefixes=(), sec=3.0, rpm=1620.0):
    import mujoco, numpy as np
    omega = psign * prpm * 2 * math.pi / 60.0
    xml, ctrl = P.build_xml(rpm, omega, -1, bx, FLOOR_TOP + P.BALL_R)
    xml = strip_named(F.strip(xml), prefixes)
    m = mujoco.MjModel.from_xml_string(xml)
    d = mujoco.MjData(m)
    d.ctrl[:] = ctrl
    mujoco.mj_forward(m, d)
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    pj = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "paddle_joint")
    pdof = m.jnt_dofadr[pj]
    dt = m.opt.timestep
    every = max(1, int(round(0.002 / dt)))
    xs, zs, om = [], [], []
    for i in range(int(round(sec / dt))):
        mujoco.mj_step(m, d)
        if i % every:
            continue
        p = d.xpos[bid]
        xs.append(float(p[0]) * 1000)
        zs.append(float(p[2]) * 1000)
        om.append(float(d.qvel[pdof]))
    return xs, zs, om


def draw_geometry(ax, prefixes=()):
    for name, (center, size, rot), cls in P.static_geoms():
        if not name.startswith(("guide_floor", "guide_roof")):
            continue
        if any(p in name for p in prefixes):
            continue
        for (cx, cy, cz), (sx, sy, sz), r in P.clip_drum((center, size, rot)):
            ax.add_patch(Rectangle((cx - sx / 2.0, cz - sz / 2.0), sx, sz, angle=r,
                                   rotation_point="xy", facecolor="#9ec9e2",
                                   edgecolor="#2b6a91", lw=0.6, alpha=0.95, zorder=1))
    ax.add_patch(Circle((P.PADDLE_CENTER[0], P.PADDLE_CENTER[2]), P.PADDLE_SWEEP_R,
                        fill=False, ec="#c8610f", lw=1.4, ls="--", zorder=2))
    ax.add_patch(Circle((P.PADDLE_CENTER[0], P.PADDLE_CENTER[2]), 18.0,
                        fill=False, ec="#c8610f", lw=1.6, zorder=2))
    a = math.radians(-P.ANGLE)
    for n in (-55.0, 55.0):
        c = P.to_world(-135.0 + P.THROAT_LENGTH / 2.0, 0.0, n)
        ux, uz = math.cos(a), math.sin(a)
        hx, hz = P.THROAT_LENGTH / 2.0 * ux, P.THROAT_LENGTH / 2.0 * uz
        ax.plot([c[0] - hx, c[0] + hx], [c[2] - hz, c[2] + hz], color="#2b6a91", lw=1.8, zorder=1)
    ax.plot([P.SHOOTER_ORIGIN[0]], [P.SHOOTER_ORIGIN[2]], "+", color="k", ms=10, zorder=3)
    ax.annotate("夹口 nip", (P.SHOOTER_ORIGIN[0], P.SHOOTER_ORIGIN[2]),
                textcoords="offset points", xytext=(6, 6), fontsize=9)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    base = trace(-95.0, 1, 120.0)
    opentop = trace(-95.0, 1, 120.0, ("guide_roof",), sec=1.0)

    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    panels = [(axes[0], base, (), "A 原始几何：升到 z≈77 被 52°顶板+轮毂楔死，拨杆堵转"),
              (axes[1], opentop, ("guide_roof",), "B 去掉全部顶板：被抛到 z≈144 后落回，仍到不了夹口")]
    for ax, (xs, zs, om), pref, ttl in panels:
        draw_geometry(ax, pref)
        ax.plot(xs, zs, color="#d62728", lw=2.2, zorder=5, label="球心轨迹")
        ax.add_patch(Circle((xs[0], zs[0]), P.BALL_R, fill=False, ec="#d62728", lw=1.0, ls=":", zorder=5))
        ax.add_patch(Circle((xs[-1], zs[-1]), P.BALL_R, fill=False, ec="#8c564b", lw=1.8, zorder=6))
        ax.plot([xs[-1]], [zs[-1]], "x", color="#8c564b", ms=10, zorder=6)
        ax.annotate("终了", (xs[-1], zs[-1]), textcoords="offset points",
                    xytext=(8, 8), fontsize=10, color="#8c564b")
        ax.set_title(ttl, fontsize=12, pad=10)
        ax.set_xlabel("X [mm]"); ax.set_ylabel("Z [mm]")
        ax.set_xlim(-175, 120); ax.set_ylim(-20, 270)
        ax.set_aspect("equal"); ax.grid(alpha=0.3)
        ax.legend(loc="lower right", fontsize=9)
    ax = axes[0]
    ax.plot([-95.0], [53.1], "o", color="#d62728", ms=6, zorder=6)
    ax.annotate("放球点(-95,53)", (-95.0, 53.1), textcoords="offset points",
                xytext=(-96, -6), fontsize=10, color="#d62728",
                arrowprops=dict(arrowstyle="->", color="#d62728", lw=1.1))
    ax.annotate("52°顶板 guide_roof_3 近端(-118,107)\n伸到举升路径正上方",
                (-118, 107), textcoords="offset points", xytext=(-14, 48),
                fontsize=10, color="#1f4e6b",
                arrowprops=dict(arrowstyle="->", color="#1f4e6b", lw=1.3))
    ax.annotate("拨杆轮毂 R18", (-47, 73), textcoords="offset points",
                xytext=(14, -40), fontsize=10, color="#c8610f")
    fig.suptitle("T06 POLLEN 送球段仿真：球从拨杆下方出发，无法送达夹口", fontsize=14, y=0.98)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(OUT / "jam_trajectory.png", dpi=130)
    print("saved", OUT / "jam_trajectory.png", flush=True)
