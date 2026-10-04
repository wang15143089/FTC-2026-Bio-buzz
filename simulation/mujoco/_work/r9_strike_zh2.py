# -*- coding: utf-8 -*-
"""R9 friction verdict figure v2 (Chinese) - clean geometry (tray to 185, stop wall 188)."""
import math, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import r6_smooth as r6
import r9_clean as K
import opt_lib as ol
import mujoco, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon
from matplotlib.lines import Line2D

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
pv2 = ol.pv2
C = (pv2.PADDLE_CX, pv2.PADDLE_CZ)
OUT = Path("simulation/mujoco/out")
STAT_R5, PART_R5 = ol.GEOM["R5"]
T_STALL, N_FREE = 0.530, 290.0
KV = T_STALL / (N_FREE * 2 * math.pi / 60.0)


def build(mu, bx=145.0):
    pv2.static_geoms, pv2.paddle_parts = K.stat, PART_R5
    xml, ctrl = pv2.build_xml(1620.0, -1, N_FREE * 2 * math.pi / 60.0, bx,
                              pv2.tray_top_z(bx) + pv2.BALL_R)
    xml = xml.replace('kv="0.08"', 'kv="%.6f"' % KV)
    xml = xml.replace('forcerange="-1.5 1.5"', 'forcerange="-%g %g"' % (T_STALL, T_STALL))
    xml = xml.replace('class="ball"><geom friction="1.0 0.02 0.0001"',
                      'class="ball"><geom friction="%g 0.02 0.0001"' % mu)
    return mujoco.MjModel.from_xml_string(xml), ctrl


def trace(mu, sec=4.0, want_carry=False):
    m, ctrl = build(mu); d = mujoco.MjData(m); d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    pbid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "paddle")
    bgeom = {g for g in range(m.ngeom) if m.geom_bodyid[g] == bid}
    pgeom = {g for g in range(m.ngeom) if m.geom_bodyid[g] == pbid}
    out = {"strike": None, "carry": None, "path": [], "minr": None}
    dt = m.opt.timestep
    for i in range(int(sec / dt)):
        mujoco.mj_step(m, d)
        p = d.xpos[bid] * 1000.0
        r = math.hypot(p[0] - C[0], p[2] - C[1])
        hit = None
        for c in range(d.ncon):
            con = d.contact[c]
            if (con.geom1 in bgeom and con.geom2 in pgeom) or (con.geom2 in bgeom and con.geom1 in pgeom):
                hit = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM,
                                        int(con.geom2 if con.geom1 in bgeom else con.geom1))
                break
        if out["strike"] is None and hit:
            out["strike"] = {"t": i * dt, "x": p[0], "z": p[2], "r": r, "geom": hit,
                             "gx": d.geom_xpos.copy(), "gq": d.geom_xmat.copy(),
                             "gs": m.geom_size.copy(), "gt": m.geom_type.copy()}
        if want_carry and out["carry"] is None and r <= 56.0:
            out["carry"] = {"t": i * dt, "x": p[0], "z": p[2], "r": r}
        if out["minr"] is None or r < out["minr"][1]:
            out["minr"] = (i * dt, r, p[0], p[2])
        if i % max(1, int(0.01 / dt)) == 0:
            out["path"].append((i * dt, p[0], p[2], r))
    return out


if __name__ == "__main__":
    print("mu=0.40 ...", flush=True); t40 = trace(0.40)
    print("mu=1.00 ...", flush=True); t100 = trace(1.00, want_carry=True)
    print("  strike", None if not t40["strike"] else
          (round(t40["strike"]["t"], 3), round(t40["strike"]["x"], 1), round(t40["strike"]["z"], 1),
           round(t40["strike"]["r"], 1), t40["strike"]["geom"]))
    print("  mu0.40 minr", tuple(round(v, 2) for v in t40["minr"]))
    print("  carry", t100["carry"] and (round(t100["carry"]["t"], 3), round(t100["carry"]["r"], 1)))

    fig = plt.figure(figsize=(15.5, 10.2))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.35, 1.0], hspace=0.26, wspace=0.2)
    axA = fig.add_subplot(gs[0, :])
    st = t40["strike"]
    if st:
        R = st["gq"].reshape(-1, 3, 3); pos = st["gx"] * 1000.0; H = st["gs"] * 1000.0
        for i in range(len(H)):
            if st["gt"][i] != mujoco.mjtGeom.mjGEOM_BOX:
                continue
            pts = [(pos[i, 0] + (R[i] @ np.array([sx * H[i, 0], 0.0, sz * H[i, 2]]))[0],
                    pos[i, 2] + (R[i] @ np.array([sx * H[i, 0], 0.0, sz * H[i, 2]]))[2])
                   for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
            axA.add_patch(Polygon(pts, closed=True, facecolor="#cfd8dc", edgecolor="#78909c",
                                  lw=0.5, alpha=0.8, zorder=2))
        axA.add_patch(Circle((st["x"], st["z"]), pv2.BALL_R, facecolor="#e8c33a",
                             edgecolor="#8d6e00", lw=1.3, alpha=0.92, zorder=5))
        n = (st["x"] - C[0]) / st["r"], (st["z"] - C[1]) / st["r"]
        axA.annotate("μ=0.40：指尖擦打处\n球心 r=%.0f mm" % st["r"],
                     (st["x"], st["z"]), textcoords="offset points", xytext=(-95, 40),
                     fontsize=11.5, color="#b71c1c", ha="center",
                     arrowprops=dict(arrowstyle="->", color="#b71c1c"))
        axA.plot([C[0], C[0] + n[0] * st["r"]], [C[1], C[1] + n[1] * st["r"]],
                 color="#b71c1c", lw=1.0, ls=":")
    if t100["carry"]:
        axA.add_patch(Circle((t100["carry"]["x"], t100["carry"]["z"]), pv2.BALL_R, facecolor="none",
                             edgecolor="#c62828", lw=1.8, ls="--", zorder=6))
        axA.annotate("μ=1.00：被拖入运载\n球心 r=%.0f mm（设计 58.4）" % t100["carry"]["r"],
                     (t100["carry"]["x"], t100["carry"]["z"]), textcoords="offset points",
                     xytext=(-60, -62), fontsize=11.5, color="#c62828", ha="center",
                     arrowprops=dict(arrowstyle="->", color="#c62828"))
    axA.plot([C[0]], [C[1]], marker="+", ms=15, mew=2.3, color="#37474f", zorder=7)
    axA.annotate("拨杆轴", (C[0], C[1]), textcoords="offset points", xytext=(8, -16), fontsize=11)
    axA.add_patch(Circle(C, 58.4, facecolor="none", edgecolor="#f2a65a", lw=1.1, ls=":"))
    axA.text(C[0] + 20, C[1] + 44, "设计运载半径 58.4", color="#e07b1f", fontsize=10)
    axA.plot([-60, 190], [pv2.tray_top_z(-60), pv2.tray_top_z(190)], color="#2e7d32", lw=1.0, ls="-.")
    axA.text(96, pv2.tray_top_z(96) - 16, "托板顶面（5° 下倾）", color="#2e7d32", fontsize=10.5)
    axA.set_title("A. 剖面（同一拨杆姿态下的判定）：球停在 r≈86–128 mm 摆动，够不到 58.4 mm 的运载轨道",
                  fontsize=13.5)
    axA.set_xlim(-70, 205); axA.set_ylim(-25, 195); axA.set_aspect("equal")
    axA.set_xlabel("x / mm"); axA.set_ylabel("z / mm")

    axB = fig.add_subplot(gs[1, 0])
    for tr, mu, col in ((t40, 0.40, "#c62828"), (t100, 1.00, "#2e7d32")):
        a = np.array(tr["path"]); axB.plot(a[:, 0], a[:, 1], lw=1.9, color=col, label="μ=%.2f" % mu)
    axB.set_xlabel("t / s"); axB.set_ylabel("球心 x / mm")
    axB.legend(fontsize=11, title="球—外罩摩擦", title_fontsize=10)
    axB.grid(alpha=0.25); axB.set_xlim(0, 4)
    axB.set_title("B. 球的走向：μ=0.40 只被来回拨动，不前进", fontsize=12.5)

    axC = fig.add_subplot(gs[1, 1])
    mus = [0.40, 0.50, 0.60, 0.70, 0.80, 1.00]
    ex = [None, None, None, 15.69, 8.544, 7.498]
    axC.bar([m for m, e in zip(mus, ex) if not e], [20.0] * 3, width=0.075, color="#ef9a9a",
            edgecolor="#c62828", label="20 s 内未发射")
    axC.bar([m for m, e in zip(mus, ex) if e], [e for e in ex if e], width=0.075,
            color="#a5d6a7", edgecolor="#2e7d32", label="发射成功（柱高 = 出球时刻）")
    axC.axvline(0.65, color="#c62828", ls="--", lw=1.7)
    axC.annotate("门檻 μ≈0.65", (0.65, 10.4), textcoords="offset points", xytext=(-8, 0),
                 fontsize=11.5, color="#c62828", ha="right", rotation=90, va="center")
    axC.axvline(0.40, color="#1565c0", lw=2.2)
    axC.annotate("实际估算 μ≈0.40\n（光面塑料球 / 0.4 mm PET）", (0.40, 18.6),
                 textcoords="offset points", xytext=(7, 0), fontsize=10.5, color="#1565c0", va="top")
    axC.set_xlabel("球—外罩摩擦系数 μ"); axC.set_ylabel("出球时刻 / s")
    axC.set_ylim(0, 20.5); axC.set_xlim(0.30, 1.08)
    axC.legend(fontsize=10, loc="center right"); axC.grid(alpha=0.25, axis="y")
    axC.set_title("C. R5 送球对球摩擦的敏感度（20 s 预算）", fontsize=12.5)

    fig.suptitle("T06 POLLEN V2 — 光面塑料球 + 0.4 mm 层高 PET 打印外罩：送球能力判定", fontsize=15.5, y=0.985)
    p = OUT / "r9_mu_verdict_zh.png"
    fig.savefig(p, dpi=145, bbox_inches="tight")
    print("  saved", p)
