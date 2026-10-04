# -*- coding: utf-8 -*-
"""R9 friction verdict figure (Chinese): section at the finger-tip strike, trajectory, mu threshold."""
import json, math, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import r6_smooth as r6
import opt_lib as ol
import mujoco, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, Rectangle
from matplotlib.lines import Line2D

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
pv2 = ol.pv2
C = (pv2.PADDLE_CX, pv2.PADDLE_CZ)
OUT = Path("simulation/mujoco/out")
STAT_R5, PART_R5 = ol.GEOM["R5"]
T_STALL, N_FREE = 0.530, 290.0
KV = T_STALL / (N_FREE * 2 * math.pi / 60.0)


def wall(x=153.0, h=60.0):
    z = pv2.tray_top_z(x) + h / 2.0
    return ("rear_wall", "shell", "box", (6.0, pv2.FEEDER_W, h), (x, 0.0, z), pv2.quat_y(0.0))


def build(mu, bx=145.0):
    pv2.static_geoms = lambda: list(STAT_R5()) + [wall()]
    pv2.paddle_parts = PART_R5
    xml, ctrl = pv2.build_xml(1620.0, -1, N_FREE * 2 * math.pi / 60.0, bx,
                              pv2.tray_top_z(bx) + pv2.BALL_R)
    xml = xml.replace('kv="0.08"', 'kv="%.6f"' % KV)
    xml = xml.replace('forcerange="-1.5 1.5"', 'forcerange="-%g %g"' % (T_STALL, T_STALL))
    xml = xml.replace('class="ball"><geom friction="1.0 0.02 0.0001"',
                      'class="ball"><geom friction="%g 0.02 0.0001"' % mu)
    return mujoco.MjModel.from_xml_string(xml), ctrl


def trace(mu, sec=3.0, want_carry=False):
    m, ctrl = build(mu)
    d = mujoco.MjData(m); d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    pbid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "paddle")
    bgeom = {g for g in range(m.ngeom) if m.geom_bodyid[g] == bid}
    pgeom = {g for g in range(m.ngeom) if m.geom_bodyid[g] == pbid}
    out = {"strike": None, "carry": None, "path": []}
    dt = m.opt.timestep; n = int(sec / dt)
    for i in range(n):
        mujoco.mj_step(m, d)
        p = d.xpos[bid] * 1000.0
        rx, rz = p[0] - C[0], p[2] - C[1]
        r = math.hypot(rx, rz)
        hit = None
        for c in range(d.ncon):
            con = d.contact[c]
            if (con.geom1 in bgeom and con.geom2 in pgeom) or (con.geom2 in bgeom and con.geom1 in pgeom):
                other = int(con.geom2 if con.geom1 in bgeom else con.geom1)
                hit = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, other)
                break
        if out["strike"] is None and hit:
            out["strike"] = {"t": i * dt, "x": p[0], "z": p[2], "r": r, "geom": hit,
                             "gx": d.geom_xpos.copy(), "gq": d.geom_xmat.copy(),
                             "gs": m.geom_size.copy(), "gt": m.geom_type.copy()}
        if want_carry and out["carry"] is None and r <= 56.0:
            out["carry"] = {"t": i * dt, "x": p[0], "z": p[2], "r": r}
        if i % max(1, int(0.01 / dt)) == 0:
            out["path"].append((round(i * dt, 3), round(p[0], 2), round(p[2], 2), round(r, 2)))
    out["model"] = m
    return out


def draw_frame(ax, gx, gq, gs, gt, ball, color_map, alpha=0.75):
    for i in range(len(gs)):
        if gt[i] == mujoco.mjtGeom.mjGEOM_BOX:
            R = gq[i].reshape(3, 3); pos = gx[i] * 1000.0
            h = gs[i] * 1000.0
            pts = []
            for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                loc = np.array([sx * h[0], 0.0, sz * h[2]])
                w = pos + R @ loc
                pts.append((w[0], w[2]))
            ax.add_patch(Polygon(pts, closed=True, facecolor="#cfd8dc", edgecolor="#78909c",
                                 lw=0.5, alpha=alpha, zorder=2))
    ax.add_patch(Circle(ball, pv2.BALL_R, facecolor="#e8c33a", edgecolor="#8d6e00", lw=1.2,
                        alpha=0.9, zorder=5))


if __name__ == "__main__":
    print("running mu=0.40 ...", flush=True)
    t40 = trace(0.40, sec=3.0)
    print("running mu=1.00 ...", flush=True)
    t100 = trace(1.00, sec=3.0, want_carry=True)
    print("  strike:", t40["strike"] and (round(t40["strike"]["t"], 3), round(t40["strike"]["r"], 1),
                                         t40["strike"]["geom"]))
    print("  carry :", t100["carry"] and (round(t100["carry"]["t"], 3), round(t100["carry"]["r"], 1)))

    fig = plt.figure(figsize=(15.5, 9.6))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.35, 1.0], hspace=0.26, wspace=0.2)

    # ---- A: section at the strike frame ----
    axA = fig.add_subplot(gs[0, :])
    st = t40["strike"]
    draw_frame(axA, st["gx"], st["gq"], st["gs"], st["gt"], (st["x"], st["z"]), None)
    axA.add_patch(Circle((t100["carry"]["x"], t100["carry"]["z"]), pv2.BALL_R, facecolor="none",
                         edgecolor="#c62828", lw=1.6, ls="--", zorder=6))
    axA.plot([C[0]], [C[1]], marker="+", ms=14, mew=2.2, color="#37474f", zorder=7)
    axA.annotate("拨杆轴", (C[0], C[1]), textcoords="offset points", xytext=(6, -16), fontsize=11)
    axA.annotate("μ=0.40：指尖擦打（球心 r=%.0f mm）" % st["r"], (st["x"], st["z"]),
                 textcoords="offset points", xytext=(14, 18), fontsize=11.5, color="#b71c1c",
                 arrowprops=dict(arrowstyle="->", color="#b71c1c"))
    axA.annotate("μ=1.00：被拖到运载半径（球心 r=%.0f mm）" % t100["carry"]["r"],
                 (t100["carry"]["x"], t100["carry"]["z"]), textcoords="offset points",
                 xytext=(-30, -46), fontsize=11.5, color="#c62828",
                 arrowprops=dict(arrowstyle="->", color="#c62828"))
    axA.add_patch(Circle((C[0], C[1]), 60.0, facecolor="none", edgecolor="#f2a65a", lw=1.0, ls=":"))
    axA.plot([-60, 190], [pv2.tray_top_z(-60), pv2.tray_top_z(190)], color="#2e7d32", lw=1.0, ls="-.")
    axA.text(150, pv2.tray_top_z(150) + 6, "托板顶面（5° 下倾）", color="#2e7d32", fontsize=10.5)
    axA.set_title("A. 剖面：μ=0.40 时球在 r≈95 mm 处被拨杆指尖擦打，未进入运载（R5 布局 + 尾端挡板）",
                  fontsize=13.5)
    axA.set_xlim(-70, 200); axA.set_ylim(-25, 190); axA.set_aspect("equal")
    axA.set_xlabel("x / mm"); axA.set_ylabel("z / mm")

    # ---- B: trajectory ----
    axB = fig.add_subplot(gs[1, 0])
    p40 = np.array([(a, b) for a, b, c, d in t40["path"]])
    p100 = np.array([(a, b) for a, b, c, d in t100["path"]])
    axB.plot(p40[:, 0], p40[:, 1], lw=1.8, color="#c62828", label="μ=0.40 球心 x(t)")
    axB.plot(p100[:, 0], p100[:, 1], lw=1.8, color="#2e7d32", label="μ=1.00 球心 x(t)")
    axB.axhline(150, color="#78909c", ls=":", lw=1.0)
    axB.text(0.03, 152, "托板尾端 x=150", color="#546e7a", fontsize=9.5)
    axB.annotate("被弹回并飞出托板", (0.5, 156), fontsize=10.5, color="#c62828",
                 arrowprops=dict(arrowstyle="->", color="#c62828"), textcoords="offset points", xytext=(30, 8))
    axB.set_xlabel("t / s"); axB.set_ylabel("球心 x / mm"); axB.set_xlim(0, 3)
    axB.legend(fontsize=10, loc="lower right"); axB.grid(alpha=0.25)
    axB.set_title("B. 球在托板上的走向", fontsize=12.5)

    # ---- C: mu threshold ----
    axC = fig.add_subplot(gs[1, 1])
    mus = [0.40, 0.60, 0.70, 0.80, 0.90, 1.00]
    ex = [None, None, 11.65, 7.94, 7.438, 7.112]
    ok = [m for m, e in zip(mus, ex) if e]
    axC.bar([m for m, e in zip(mus, ex) if not e], [20] * 2, width=0.07, color="#ef9a9a",
            edgecolor="#c62828", label="失败（20 s 内未发射）")
    axC.bar(ok, [e for e in ex if e], width=0.07, color="#a5d6a7", edgecolor="#2e7d32",
            label="发射成功（柱高 = 出球时刻）")
    axC.axvline(0.65, color="#c62828", ls="--", lw=1.6)
    axC.text(0.655, 17.5, "门檻 μ≈0.65", color="#c62828", fontsize=11)
    axC.axvline(0.40, color="#1565c0", ls="-", lw=2.0)
    axC.text(0.33, 13.0, "实际估算\nμ≈0.40", color="#1565c0", fontsize=11, ha="right")
    axC.set_xlabel("球—外罩摩擦系数 μ"); axC.set_ylabel("出球时刻 / s")
    axC.set_ylim(0, 20); axC.legend(fontsize=10, loc="upper right"); axC.grid(alpha=0.25, axis="y")
    axC.set_title("C. R5 送球对摩擦的敏感度", fontsize=12.5)

    fig.suptitle("T06 POLLEN V2 — 光面塑料球 + 0.4 mm PET 打印外罩（μ≈0.40）送球能力判定",
                 fontsize=15.5, y=0.985)
    p = OUT / "r9_mu_verdict_zh.png"
    fig.savefig(p, dpi=145, bbox_inches="tight")
    print("  saved", p)
