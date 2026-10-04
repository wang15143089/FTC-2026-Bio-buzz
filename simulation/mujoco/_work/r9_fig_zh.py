# -*- coding: utf-8 -*-
"""R9 停球窝 + 摩擦 结论图（中文）"""
import json, math, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import r6_smooth as r6
import opt_lib as ol
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, Rectangle
from matplotlib.lines import Line2D

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
pv2 = ol.pv2
C = (pv2.PADDLE_CX, pv2.PADDLE_CZ)
R_IN, R_OUT, BALL_R = pv2.R_IN, pv2.R_OUT, pv2.BALL_R
OUT = Path("simulation/mujoco/out")
C_SHELL, C_TRAY, C_PAD, C_PADDLE, C_BALL = "#9fc6e0", "#b9d8b0", "#c9a0dc", "#f2a65a", "#e8c33a"


def fp(ang, r):
    a = math.radians(ang)
    return (C[0] + r * math.cos(a), C[1] + r * math.sin(a))


def arc_poly(a0, a1, r0=R_IN, r1=R_OUT, n=48, **kw):
    inn = [fp(a0 + (a1 - a0) * i / n, r0) for i in range(n + 1)]
    out = [fp(a0 + (a1 - a0) * i / n, r1) for i in range(n + 1)]
    p = Polygon(inn + out[::-1], closed=True)
    if kw:
        p.set(**kw)
    return p


def finger(ax, ang_deg, r0, r1, halfw, **kw):
    a = math.radians(ang_deg)
    ux, uz = math.cos(a), -math.sin(a)
    tx, tz = math.sin(a), math.cos(a)
    p = Polygon([(C[0] + u * ux + v * tx, C[1] + u * uz + v * tz)
                 for (u, v) in ((r0, -halfw), (r1, -halfw), (r1, halfw), (r0, halfw))], closed=True)
    p.set(**kw)
    ax.add_patch(p)


def section(ax, pad_step, pad_xc, ball, title, note=""):
    ax.add_patch(arc_poly(142.0, 225.0, facecolor=C_SHELL, edgecolor="#2a6f97", lw=1.4))
    ax.plot(*zip(*[fp(225.0, r) for r in (R_IN, R_OUT)]), color="#2a6f97", lw=2.0)
    xs = [pv2.TRAY_X0, pv2.TRAY_X1]
    ax.plot(xs, [pv2.tray_top_z(x) for x in xs], color="#3f7d3a", lw=2.5)
    ax.plot(xs, [pv2.tray_top_z(x) - pv2.TRAY_T for x in xs], color="#3f7d3a", lw=1.0)
    for a in (18.0, 138.0, 258.0):
        finger(ax, a, 14, 46, 5, facecolor=C_PADDLE, edgecolor="#b5651d", lw=1.0, zorder=3)
        finger(ax, a, 46, 58, 15, facecolor=C_PADDLE, edgecolor="#b5651d", lw=1.2, zorder=3)
        finger(ax, a, 56, 60, 17, facecolor="#f6c58b", edgecolor="#b5651d", lw=1.0, zorder=4)
    if pad_step > 0:
        ztop = pv2.tray_top_z(pad_xc) + pad_step
        ax.add_patch(Rectangle((pad_xc - 15, ztop - pad_step - 6), 30, pad_step + 6,
                               facecolor=C_PAD, edgecolor="#6a3d9a", lw=1.4, zorder=2))
    bx, bz = ball
    ax.add_patch(Circle((bx, bz), BALL_R, facecolor=C_BALL, edgecolor="#8a6d0b", lw=1.6, zorder=6, alpha=0.92))
    ax.plot(*C, "k+", ms=9, mew=2)
    ax.set_aspect("equal")
    ax.set_xlim(-60, 105)
    ax.set_ylim(-15, 105)
    ax.set_title(title, fontsize=10.5)
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Z (mm)")
    ax.grid(alpha=0.25, lw=0.4)
    if note:
        ax.text(0.02, 0.98, note, transform=ax.transAxes, va="top", ha="left", fontsize=8.5,
                bbox=dict(fc="white", ec="#999", alpha=0.9, pad=3))


fig = plt.figure(figsize=(13.2, 9.4))
gs = fig.add_gridspec(2, 2, hspace=0.32, wspace=0.22)

ax = fig.add_subplot(gs[0, 0])
section(ax, 6.8, -2.0, (11.74, 59.89), "(a) 现状 停球窝 6.8 mm：球停 r=54.5 mm，全程自锁爬行",
        "堵转占比 63%\n运载 3.72 s\n拨杆中位 4.3 rpm\n发射 5.13 s")
ax = fig.add_subplot(gs[0, 1])
section(ax, 20.0, 28.0, (38.0, 65.41), "(b) 加高并后移球窝 20 mm @ x=28：球停 r=46.8 mm，脱锁",
        "堵转占比 44%（≈受载时长）\n运载 3.00 s\n拨杆中位 281.9 rpm\n发射 3.63 s")

ax = fig.add_subplot(gs[1, 0])
labels = ["现状\n6.8", "加高13", "加高16", "加高20", "加高20\nx=28", "加高24", "mu=0.50", "mu=0.45", "mu=0.40"]
vals = [5.134, 4.436, 4.084, 3.838, 3.626, 0.0, 3.102, 0.98, 0.818]
cols = ["#8c8c8c", C_PAD, C_PAD, C_PAD, C_PAD, "#c0392b", "#2980b9", "#2980b9", "#2980b9"]
bars = ax.bar(range(len(vals)), vals, color=cols, edgecolor="#444", lw=0.8)
for i, (b, v) in enumerate(zip(bars, vals)):
    ax.text(b.get_x() + b.get_width() / 2, v + 0.09, ("失败" if v == 0 else "%.2f" % v),
            ha="center", fontsize=9)
ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels, fontsize=8.5)
ax.set_ylabel("从停位到发射的时刻 (s)")
ax.set_title("(c) 各方案全流程耗时（8 s 预算，25-4 真实电机模型）", fontsize=10.5)
ax.grid(axis="y", alpha=0.3, lw=0.4)
ax.axvspan(0.5, 4.5, color=C_PAD, alpha=0.10)
ax.axvspan(4.5, 5.5, color="#c0392b", alpha=0.10)
ax.axvspan(5.5, 8.5, color="#2980b9", alpha=0.10)

ax = fig.add_subplot(gs[1, 1])
mu = [1.0, 0.8, 0.7, 0.6, 0.55, 0.5, 0.45, 0.4, 0.35, 0.3]
carry = [3.72, 3.70, 3.68, 3.65, 3.62, 2.52, 0.48, 0.34, 0.24, 0.13]
rpm = [4.3, 4.4, 4.5, 5.5, 10.2, 281.9, 281.9, 281.9, 281.9, 281.9]
ax.plot(mu, carry, "o-", color="#d35400", lw=2, ms=6, label="运载耗时 (s)")
ax.set_xlabel("球-外罩摩擦系数 mu")
ax.set_ylabel("运载耗时 (s)", color="#d35400")
ax.tick_params(axis="y", labelcolor="#d35400")
ax.invert_xaxis()
ax.grid(alpha=0.3, lw=0.4)
ax2 = ax.twinx()
ax2.plot(mu, rpm, "s--", color="#2471a3", lw=2, ms=6, label="拨杆中位转速 (rpm)")
ax2.set_ylabel("拨杆中位转速 (rpm)", color="#2471a3")
ax2.tick_params(axis="y", labelcolor="#2471a3")
ax2.set_ylim(-20, 320)
ax.axvline(0.5, color="#7f8c8d", ls=":", lw=2)
ax.text(0.51, 3.3, "自锁门槛\nmu≈0.5", fontsize=9, color="#7f8c8d", ha="right")
ax.set_title("(d) 球摩擦系数阶梯：mu>=0.55 自锁，mu<=0.50 解锁", fontsize=10.5)

fig.suptitle("T06 POLLEN FEEDER V2 — R9 停球窝与摩擦结论：卡滞是摩擦自锁，球窝几何只能挤掉约 28% 行程时间",
             fontsize=12.5)
fig.savefig(OUT / "r9_nest_friction_zh.png", dpi=150, bbox_inches="tight")
print("saved", OUT / "r9_nest_friction_zh.png")
