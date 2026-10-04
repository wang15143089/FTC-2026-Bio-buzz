# -*- coding: utf-8 -*-
"""R25 figure: NECTAR final geometry set (O24 hub, tray dropped to tangency)."""
import math
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, FancyArrowPatch
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

OUT = Path("cad/output")
PADDLE = (29.49, 111.46)
PIVOT_OLD = (-2.30, 17.50)
TILT = 5.0
BALL_R = 45.974
HUB_R = 12.0
R_CARRY = 62.0
R_IN = R_CARRY + BALL_R
A_LIP, A_EXIT = 275.0, 142.0
SHELL_WALL = 7.0
TRAY_X1 = 150.0
SIN, COS = math.sin(math.radians(TILT)), math.cos(math.radians(TILT))
D0 = (PADDLE[1] - PIVOT_OLD[1]) * COS - (PADDLE[0] - PIVOT_OLD[0]) * SIN
DELTA = R_IN - D0
CUT_X = PADDLE[0] + R_IN * SIN
PIVOT = (PIVOT_OLD[0] + DELTA * SIN, PIVOT_OLD[1] - DELTA * COS)


def tz(x, piv=PIVOT):
    return piv[1] + (x - piv[0]) * math.tan(math.radians(TILT))


def polar(r, a):
    return (PADDLE[0] + r * math.cos(math.radians(a)),
            PADDLE[1] + r * math.sin(math.radians(a)))


def arcpts(r, a0, a1, n=200):
    return [polar(r, a0 + (a1 - a0) * i / (n - 1)) for i in range(n)]


fig = plt.figure(figsize=(16.5, 10.8))
gs = fig.add_gridspec(2, 2, height_ratios=[1.5, 1.0], hspace=0.30, wspace=0.18)

# ---------------------------------------------------------------- (a) section
ax = fig.add_subplot(gs[0, :])
ax.set_title("(a) R25 定稿剖面（XZ，Y=0）：外罩 142°→275°、托盘下移 %.1f mm 与运载圆精确相切、桨毂缩至 Ø24"
             % DELTA, fontsize=12.5, pad=26)

ax.fill(*zip(*(arcpts(R_IN, A_EXIT, A_LIP) + list(reversed(arcpts(R_IN + SHELL_WALL, A_EXIT, A_LIP))))),
        color="#4f8fd4", alpha=0.30, ec="#2f6fb4", lw=1.6, zorder=2)
tx = [CUT_X, TRAY_X1]
ax.add_patch(Polygon([(tx[0], tz(tx[0])), (tx[1], tz(tx[1])),
                      (tx[1], tz(tx[1]) - 6.0), (tx[0], tz(tx[0]) - 6.0)],
                     closed=True, fc="#4f8fd4", alpha=0.30, ec="#2f6fb4", lw=1.6, zorder=3))
ax.add_patch(Polygon([(CUT_X, tz(CUT_X, PIVOT_OLD)), (TRAY_X1, tz(TRAY_X1, PIVOT_OLD)),
                      (TRAY_X1, tz(TRAY_X1, PIVOT_OLD) - 6.0), (CUT_X, tz(CUT_X, PIVOT_OLD) - 6.0)],
                     closed=True, fc="none", ec="#9aa0aa", lw=1.1, ls=(0, (5, 3)), zorder=2))
ax.annotate("", xy=PIVOT, xytext=PIVOT_OLD,
            arrowprops=dict(arrowstyle="<->", color="#c0392b", lw=1.9), zorder=8)
ax.text(-38, 34, "托盘沿法线外移\nΔ = %.1f mm" % DELTA,
        color="#c0392b", fontsize=10.5, ha="center", va="bottom", zorder=9)
ax.text(-36, 26, "（虚线 = 托盘原位）", color="#7a7f88", fontsize=9, ha="center", va="top", zorder=9)

ax.add_patch(Circle(PADDLE, R_CARRY, fill=False, ec="#e67e22", lw=1.4, ls="--", zorder=4))
ax.add_patch(Circle(PADDLE, R_IN, fill=False, ec="#2f6fb4", lw=1.1, ls=":", zorder=4))
ax.text(*polar(R_CARRY, 186), " 球心运载圆 r=%.1f" % R_CARRY, color="#e67e22",
        fontsize=10, ha="left", va="center", zorder=9)
ax.text(*polar(R_IN, 300), "外壳内弧 r=%.1f" % R_IN, color="#2f6fb4",
        fontsize=10, ha="left", va="top", zorder=9)

ax.add_patch(Circle(PADDLE, HUB_R, fc="#b9bec6", ec="#6b7280", lw=1.3, zorder=6))
for a in (18.0, 138.0, 258.0):
    ax.add_patch(Polygon([polar(10, a - 3.0), polar(46, a - 3.4), polar(46, a + 3.4), polar(10, a + 3.0)],
                         closed=True, fc="#e8a33d", ec="#b97a18", lw=1.0, zorder=6))
    ax.add_patch(Polygon([polar(46, a - 4.5), polar(58, a - 4.5), polar(58, a + 4.5), polar(46, a + 4.5)],
                         closed=True, fc="#f6c453", ec="#b97a18", lw=1.0, zorder=6))
    ax.add_patch(Polygon([polar(58, a - 3.0), polar(60, a - 3.0), polar(60, a + 3.0), polar(58, a + 3.0)],
                         closed=True, fc="#fde9a8", ec="#b97a18", lw=1.0, zorder=6))
ax.plot(*PADDLE, "k+", ms=12, mew=2.0, zorder=9)
ax.text(PADDLE[0] + 8, PADDLE[1] + 8, "桨轴 C", fontsize=10.5, zorder=9)

for cx_, cz_, lb in ((PADDLE[0], PADDLE[1] - R_CARRY, "球窝（停机位）"),
                     (TRAY_X1, tz(TRAY_X1) + BALL_R, "入料位")):
    ax.add_patch(Circle((cx_, cz_), BALL_R, fill=False, ec="#2e8b57", lw=1.7, zorder=7))
    ax.text(cx_, cz_ - 8, lb, color="#2e8b57", fontsize=10.5, ha="center", va="top", zorder=9)
ax.add_patch(FancyArrowPatch((TRAY_X1 - 14, tz(TRAY_X1) + BALL_R + 8),
                             (PADDLE[0] + 30, PADDLE[1] - R_CARRY + 18),
                             arrowstyle="-|>", mutation_scale=16, color="#2e8b57", lw=1.6, zorder=7))

ax.plot([CUT_X], [PADDLE[1] - R_IN * COS], "o", color="#c0392b", ms=8, zorder=9)
ax.plot([CUT_X, -60], [PADDLE[1] - R_IN * COS, 26], color="#c0392b", lw=0.8, ls=":", zorder=8)
ax.text(-62, 25, "相切点 (%.1f, %.1f)，唇口 275°" % (CUT_X, PADDLE[1] - R_IN * COS),
        color="#c0392b", fontsize=10, ha="right", va="top", zorder=9)

ax.text(222, 132, "飞轮对（Y = ±89 轴线）\n夹口 82 mm < 球径 91.9 mm\n→ 过盈 9.9 mm\n（NECTAR 文件几何，KNOWN）",
        fontsize=10.5, color="#8e44ad", ha="right", va="top", zorder=9,
        bbox=dict(fc="#f6eefc", ec="#8e44ad", lw=1.0, alpha=0.9))

ax.set_xlim(-105, 225)
ax.set_ylim(-42, 218)
ax.set_aspect("equal")
ax.set_xlabel("X / mm"); ax.set_ylabel("Z / mm")
ax.grid(alpha=0.22, ls=":")

# ------------------------------------------------------------- (b) delta chart
ax2 = fig.add_subplot(gs[1, 0])
ax2.set_title("(b) 托盘必须外移量 Δ = R_in − d0（d0 = %.2f mm 固定）" % D0, fontsize=11.5)
names = ["H1\nhub Ø36\nr_c=70", "H2\nhub Ø30\nr_c=66", "H3\nhub Ø24\nr_c=62"]
deltas = [115.974 - D0, 111.974 - D0, 107.974 - D0]
b = ax2.bar(names, deltas, color=["#c9ccd2", "#9aa2ad", "#2f6fb4"], width=0.55)
for r_, d_ in zip(b, deltas):
    ax2.text(r_.get_x() + r_.get_width() / 2, d_ + 0.4, "%.1f" % d_, ha="center", fontsize=10.5)
ax2.text(0.5, 29.4, "托盘原距轴 d0 = %.2f mm（固定）\n外移量 Δ = R_in − d0" % D0,
         color="#c0392b", fontsize=9.5, ha="left", va="top")
ax2.set_ylabel("Δ / mm"); ax2.set_ylim(0, 30); ax2.grid(axis="y", alpha=0.25, ls=":")

# ------------------------------------------------------------- (c) results
ax3 = fig.add_subplot(gs[1, 1])
ax3.set_title("(c) MuJoCo 全流程（NECTAR 球、夹口 82、60 rpm、μ=0.40）", fontsize=11.5)
tag = ["H1 Ø36\nr_c=70", "H2 Ø30\nr_c=66", "H3 Ø24\nr_c=62", "G1 Ø24\nr_c=58.4", "G3 Ø36\nr_c=64"]
tt = [11.728, 8.784, 3.264, 4.016, 6.316]
jam = [43, 31, 8, 10, 21]
cols = ["#c9ccd2", "#9aa2ad", "#2f6fb4", "#7fb069", "#c9ccd2"]
xx = range(len(tag))
ax3.bar(xx, tt, color=cols, width=0.55)
for i, (t_, j_) in enumerate(zip(tt, jam)):
    ax3.text(i, t_ + 0.3, "%.2f s\n卡滞 %d%%" % (t_, j_), ha="center", fontsize=9.5)
ax3.set_xticks(list(xx)); ax3.set_xticklabels(tag, fontsize=9)
ax3.set_ylabel("出球时刻 t / s"); ax3.set_ylim(0, 15.5)
ax3.grid(axis="y", alpha=0.25, ls=":")
ax3.text(0.02, 0.97, "5 种配置全部发射成功，v = 4.71–4.74 m/s",
         transform=ax3.transAxes, fontsize=10, va="top",
         bbox=dict(fc="#eaf5ea", ec="#2e8b57", lw=1.0))
ax3.annotate("选定", xy=(2, 3.264), xytext=(2, 5.6), ha="center", color="#2f6fb4",
             fontsize=11, fontweight="bold",
             arrowprops=dict(arrowstyle="-|>", color="#2f6fb4", lw=1.6))

fig.suptitle("T06 a' NECTAR R25 —— 送球段定稿：外罩唇口 275°、托盘下移相切、桨毂 Ø24",
             fontsize=15, y=0.99)
p = OUT / "_r25_nectar_final_zh.png"
fig.savefig(p, dpi=155, bbox_inches="tight", facecolor="white")
print("saved", p)
