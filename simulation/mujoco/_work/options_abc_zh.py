# -*- coding: utf-8 -*-
"""T06 POLLEN 送球段：进料问题 + 三个方案 示意剖面图（单位 mm，X-Z 剖面）。

只出图，不修改任何 CAD 文件。
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

OUT = Path(__file__).resolve().parent.parent / "out"
OUT.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------------ 几何常量
ANG = 52.0
T52 = (math.cos(math.radians(ANG)), math.sin(math.radians(ANG)))
N52 = (-math.sin(math.radians(ANG)), math.cos(math.radians(ANG)))
BALL_R = 35.56
R_CARRY = 58.4
R_SHELL = R_CARRY + BALL_R            # 93.96
TRAY_TOP = 17.5
BALL_Z = TRAY_TOP + BALL_R            # 53.06
C = (29.49, 111.46)                   # 新拨杆轴
GUIDE_END = (12.53, 95.27)
NIP = (52.31, 235.51)
A_EXIT = 142.0
HUB_R, SWEEP_R = 18.0, 60.0
WHEEL_R, HALF = 48.0, 80.0
AX_A = (NIP[0] - HALF * math.sin(math.radians(ANG)), NIP[1] + HALF * math.cos(math.radians(ANG)))
AX_B = (NIP[0] + HALF * math.sin(math.radians(ANG)), NIP[1] - HALF * math.cos(math.radians(ANG)))
BLOCK_X = -86.1                       # 球心 x：球面刚好顶到 R93.96 外罩
BLOCK_ANG = 206.8
PHASES = (18.0, 138.0, 258.0)

GREEN = "#1f7a3d"
RED = "#c00000"
BLUE = "#2b6a91"
ORANGE = "#c8610f"
GRAY = "#9a9a9a"

NOTE_Y = 462.0
X0 = -200.0


def on_arc(a_deg, r=R_CARRY, c=C):
    a = math.radians(a_deg)
    return (c[0] + r * math.cos(a), c[1] + r * math.sin(a))


def arc_xy(a0, a1, r=R_CARRY, c=C, n=260):
    a = np.radians(np.linspace(a0, a1, n))
    return c[0] + r * np.cos(a), c[1] + r * np.sin(a)


def bez(p0, p1, p2, p3, n=160):
    t = np.linspace(0.0, 1.0, n)[:, None]
    P = np.array([p0, p1, p2, p3], float)
    return ((1 - t) ** 3) * P[0] + 3 * ((1 - t) ** 2) * t * P[1] + 3 * (1 - t) * t ** 2 * P[2] + t ** 3 * P[3]


# ------------------------------------------------------------------ 画图元件
def draw_tray(ax, x0, x1, color=BLUE, lw=7, ls="-", alpha=1.0, zorder=4):
    ax.plot([x0, x1], [TRAY_TOP, TRAY_TOP], color=color, lw=lw, ls=ls, alpha=alpha,
            solid_capstyle="butt", zorder=zorder)


def draw_launcher(ax):
    for s in (0.0, 110.0):
        p0 = (GUIDE_END[0] + s * N52[0], GUIDE_END[1] + s * N52[1])
        p1 = (p0[0] + 135.0 * T52[0], p0[1] + 135.0 * T52[1])
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color="#8a8a8a", lw=2.4, zorder=2)
    for c in (AX_A, AX_B):
        ax.add_patch(Circle(c, WHEEL_R, fill=False, ec="#111111", lw=2.0, zorder=3))
        ax.add_patch(Circle(c, 13, fill=False, ec="#111111", lw=1.0, ls=":", zorder=3))
        ax.plot([c[0]], [c[1]], marker="+", ms=10, mew=1.6, color="#111111", zorder=3)
    ax.add_patch(Circle(NIP, 5.0, fc=RED, ec="none", zorder=6))
    ax.annotate("夹口", NIP, textcoords="offset points", xytext=(13, -17), fontsize=10, color=RED, zorder=20)


def draw_drum(ax, blades=True, hub=True, sweep=True, scoop=(None,)):
    if sweep:
        x, y = arc_xy(0, 360, SWEEP_R)
        ax.plot(x, y, color=ORANGE, lw=1.1, ls="--", alpha=0.75, zorder=2)
    for i, ph in enumerate(PHASES):
        a = math.radians(ph)
        p0 = (C[0] + HUB_R * math.cos(a), C[1] + HUB_R * math.sin(a))
        p1 = (C[0] + SWEEP_R * math.cos(a), C[1] + SWEEP_R * math.sin(a))
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=ORANGE, lw=5.5,
                solid_capstyle="round", zorder=3)
        if i in scoop:
            b = math.radians(ph + 48.0)
            q = (C[0] + (SWEEP_R + 7) * math.cos(b), C[1] + (SWEEP_R + 7) * math.sin(b))
            ax.plot([p1[0], q[0]], [p1[1], q[1]], color=ORANGE, lw=4.5,
                    solid_capstyle="round", zorder=3)
    if hub:
        ax.add_patch(Circle(C, HUB_R, fc="#f6e0cb", ec=ORANGE, lw=1.8, zorder=4))
        ax.plot([C[0]], [C[1]], marker="+", ms=10, mew=1.8, color=ORANGE, zorder=5)


def draw_shell(ax, a0, a1, color=GREEN, lw=7, ls="-", alpha=1.0, zorder=6):
    x, y = arc_xy(a0, a1, R_SHELL)
    ax.plot(x, y, color=color, lw=lw, ls=ls, alpha=alpha, solid_capstyle="round", zorder=zorder)


def draw_ball(ax, p, color=RED, lw=1.8, ls="-", zorder=8):
    ax.add_patch(Circle(p, BALL_R, fill=False, ec=color, lw=lw, ls=ls, zorder=zorder))
    ax.plot([p[0]], [p[1]], marker="+", ms=8, mew=1.6, color=color, zorder=zorder)


def arrow(ax, p0, p1, color=RED, lw=2.6, ms=20, zorder=9):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=ms, lw=lw,
                                 color=color, shrinkA=0, shrinkB=0, zorder=zorder))


def path_arrows(ax, pts, idx, color=RED, lw=2.4, ms=18, zorder=9):
    for i in idx:
        p0 = tuple(pts[i])
        p1 = tuple(pts[min(i + 14, len(pts) - 1)])
        arrow(ax, p0, p1, color=color, lw=lw, ms=ms, zorder=zorder)


def lab(ax, xy, text, xytext, color="#333333", fs=10.0, ha="left"):
    ax.annotate(text, xy, textcoords="offset points", xytext=xytext, fontsize=fs,
                color=color, zorder=30, linespacing=1.5, ha=ha,
                arrowprops=dict(arrowstyle="->", color=color, lw=1.1, shrinkA=2, shrinkB=4))


def note(ax, s, color="#333333"):
    ax.text(X0, NOTE_Y, s, fontsize=10.0, color=color, ha="left", va="top", zorder=30,
            linespacing=1.65,
            bbox=dict(boxstyle="round,pad=0.42", fc="white", ec=color, lw=1.2, alpha=0.96))


# ------------------------------------------------------------------ 轨迹
def hook_path(n=160):
    p0 = (-25.0, BALL_Z)
    p1 = (27.0, BALL_Z)
    p3 = on_arc(228.0)
    p2 = (p3[0] + 26.0, p3[1] - 19.0)
    return bez(p0, p1, p2, p3, n)


def wall_of(pts):
    out = []
    m = len(pts)
    for i, p in enumerate(pts):
        w = i / (m - 1.0)
        n1 = np.array([0.0, -1.0])
        v = np.array([p[0] - C[0], p[1] - C[1]])
        n2 = v / np.linalg.norm(v)
        nn = (1 - w) * n1 + w * n2
        nn = nn / np.linalg.norm(nn)
        out.append(np.array([p[0], p[1]]) + BALL_R * nn)
    return np.array(out)


def arc_path(a0, a1, n=200):
    a = np.radians(np.linspace(a0, a1, n))
    return np.stack([C[0] + R_CARRY * np.cos(a), C[1] + R_CARRY * np.sin(a)], axis=1)


# ------------------------------------------------------------------ 版面
fig, axes = plt.subplots(2, 2, figsize=(16.5, 15.6))
fig.subplots_adjust(left=0.045, right=0.985, top=0.935, bottom=0.045, wspace=0.06, hspace=0.13)

# ============================== (1) 进料问题 ==============================
ax = axes[0][0]
draw_launcher(ax)
draw_drum(ax)
draw_tray(ax, -150.0, -80.0)
draw_tray(ax, -80.0, C[0], color=GRAY, lw=5, ls=(0, (6, 5)), alpha=0.9)
draw_shell(ax, 142.0, BLOCK_ANG, color=GREEN)
draw_shell(ax, BLOCK_ANG, 270.0, color=RED, lw=9)
x, y = arc_xy(BLOCK_ANG, 270.0, R_SHELL + 8)
ax.plot(x, y, color=RED, lw=1.0, ls=":", alpha=0.8, zorder=4)

pb = (BLOCK_X, BALL_Z)
draw_ball(ax, pb)
draw_ball(ax, (-120.0, BALL_Z), color=GRAY, lw=1.3, ls=(0, (4, 3)))
cnt = on_arc(BLOCK_ANG, R_SHELL)
ax.plot([cnt[0]], [cnt[1]], marker="o", ms=6.5, color=RED, zorder=10)
ax.plot([pb[0], cnt[0]], [pb[1], cnt[1]], color=RED, lw=1.0, ls="--", alpha=0.85, zorder=7)

lab(ax, pb, "球心 x≈-86：球面顶到外罩，进不去", (-84, -80), RED, 10.0)
lab(ax, cnt, "接触点", (30, 22), RED, 9.5)
lab(ax, on_arc(240.0, R_SHELL), "红段 207°-270°：\n必须挖掉球才进得来", (66, -34), RED, 10.0)
lab(ax, (C[0], TRAY_TOP), "外罩与托板在鼓底相切", (96, 36), GREEN, 9.5)

arcp = arc_path(270.0, A_EXIT)
path_arrows(ax, arcp, [16, 80, 145])
lab(ax, tuple(arcp[95]), "球被拨上去的方向", (-150, 44), RED, 9.5)

note(ax, "① 进料问题\n"
         "球沿托板右滚，球心到 x≈-86 时球面就顶在外罩上，进不去。\n"
         "要进料 → 外罩必须挖掉 207°-270°；\n"
         "可这段正是球被拨上去时的外支撑段 →\n"
         "同一段既要“有”又要“没有”，这就是冲突。", RED)
ax.set_title("① 进料问题：新外罩把托板入口挡死", fontsize=14, pad=8)

# ============================== (2) 方案 A ==============================
ax = axes[0][1]
draw_launcher(ax)
draw_drum(ax, scoop=(2,))
draw_tray(ax, -150.0, C[0] + 8.0)
draw_shell(ax, 142.0, 230.0, color=GREEN)
draw_shell(ax, 230.0, 270.0, color=GRAY, lw=5, ls=(0, (5, 5)))

lab(ax, on_arc(250.0, R_SHELL), "外罩开大孔 230°-270°", (58, -46), "#666666", 10.0)
tip = (C[0] + (SWEEP_R + 7) * math.cos(math.radians(258.0 + 48.0)),
       C[1] + (SWEEP_R + 7) * math.sin(math.radians(258.0 + 48.0)))
lab(ax, tip, "叶片头部改勺形\n靠“舀”把球兜住", (30, -34), ORANGE, 10.0)
lab(ax, on_arc(215.0), "这段没有外支撑", (-158, 30), RED, 10.0)

draw_ball(ax, on_arc(268.0), color=RED, lw=1.6)
draw_ball(ax, on_arc(215.0), color=RED, lw=1.2, ls=(0, (4, 3)))
draw_ball(ax, on_arc(165.0), color=RED, lw=1.2, ls=(0, (4, 3)))
arcp = arc_path(268.0, A_EXIT)
path_arrows(ax, arcp, [14, 70, 130, 180])

note(ax, "② 方案A：外罩开大孔 + 叶片改勺形\n"
         "外罩只做 142°-230°，230°-270° 开孔；\n"
         "叶片头部改勺形，靠“舀”把球兜住带走。\n"
         "风险：230°-270° 没有外支撑，球容易被\n"
         "甩回托板或反向滚出 —— 不保险。", "#8a5a00")
ax.set_title("② 方案A：开大孔 + 勺形叶片", fontsize=14, pad=8)

# ============================== (3) 方案 B ==============================
ax = axes[1][0]
draw_launcher(ax)
draw_drum(ax)
draw_tray(ax, -150.0, C[0])
draw_shell(ax, 142.0, 230.0, color=GREEN)

hp = hook_path()
wp = wall_of(hp)
ax.plot(wp[:, 0], wp[:, 1], color=GREEN, lw=6.5, solid_capstyle="round", zorder=6)
ax.plot(hp[:, 0], hp[:, 1], color=RED, lw=2.0, ls=(0, (7, 4)), zorder=7)

lab(ax, tuple(wp[95]), "鼓底导入斜坡（新）", (-158, 34), GREEN, 10.5)
lab(ax, on_arc(228.0), "斜坡在 ≈228° 切向\n接上球心圆 R58.4", (-54, 100), RED, 10.0, ha="right")
lab(ax, (-100.0, TRAY_TOP), "托板伸进鼓，一直到鼓底", (0, -48), BLUE, 10.0)

for a in (250.0, 215.0, 180.0):
    draw_ball(ax, on_arc(a), color=RED, lw=1.3, ls=(0, (4, 3)))
arcp = arc_path(228.0, A_EXIT)
path_arrows(ax, arcp, [16, 80, 140])
path_arrows(ax, hp, [40, 100, 145])

note(ax, "③ 方案B：托板伸进鼓 + 鼓底导入斜坡（推荐）\n"
         "托板一直伸到鼓底（球心 x=29.5），不再被切到 x=-80；\n"
         "鼓底加一段导入斜坡，在 ≈228° 切向接上球心圆。\n"
         "外罩只做 142°-230°：进料口与承载段不重叠，\n"
         "球从托板→斜坡→球心圆→52°发射段，全程有支撑。", GREEN)
ax.set_title("③ 方案B：托板伸进鼓 + 导入斜坡（推荐）", fontsize=14, pad=8)

# ============================== (4) 方案 C ==============================
ax = axes[1][1]
draw_launcher(ax)
draw_drum(ax)
draw_tray(ax, -150.0, -40.0, color=GRAY, lw=5, ls=(0, (5, 5)))

draw_shell(ax, 145.0, 480.0, color=GREEN, lw=7)
for a in (120.0, 145.0):
    p = on_arc(a, R_SHELL)
    q = on_arc(a, R_SHELL - 28)
    ax.plot([p[0], q[0]], [p[1], q[1]], color=GREEN, lw=4, zorder=6)

ax.plot([-150.0, -62.0, -25.4], [150.0, 174.0, 184.0], color="#666666", lw=5,
        solid_capstyle="round", zorder=4)
ax.plot([-150.0, -62.0, -25.4], [161.0, 185.0, 195.0], color="#666666", lw=5,
        solid_capstyle="round", zorder=4)
arrow(ax, (-25.4, 188.0), (-25.4, 170.0), color=RED, lw=3.0, ms=22)

lab(ax, (-120.0, 160.0), "现有托板改作溜槽（示意）", (-72, -68), "#666666", 10.0)
lab(ax, (-25.4, 176.0), "球从上方投进缺口", (96, 78), RED, 10.0)
lab(ax, on_arc(160.0), "落点 160°", (-18, 54), RED, 9.5, ha="right")

draw_ball(ax, on_arc(160.0), color=RED, lw=1.6)
draw_ball(ax, on_arc(A_EXIT), color=RED, lw=1.2, ls=(0, (4, 3)))
arcp = arc_path(160.0, A_EXIT)
path_arrows(ax, arcp, [10, 55, 95])

note(ax, "④ 方案C：球从鼓上方投放 + 封闭 C 形通道\n"
         "外罩做成整圈 C 形，只在上方留 120°-145° 缺口；\n"
         "现有托板改作溜槽，把球从上方送进缺口。\n"
         "优点：彻底绕开“进料 vs 承载”矛盾，全程有支撑；\n"
         "缺点：要多一套上方喂球结构，占用上方空间。", BLUE)
ax.set_title("④ 方案C：上方投放 + 封闭C形通道", fontsize=14, pad=8)

# ------------------------------------------------------------------ 统一坐标
for row in axes:
    for a in row:
        a.set_aspect("equal")
        a.set_xlim(-205, 200)
        a.set_ylim(-40, 492)
        a.grid(alpha=0.22, lw=0.6)
        a.set_xlabel("X [mm]")
        a.set_ylabel("Z [mm]")

fig.suptitle("T06 POLLEN 送球段：进料问题与三个改法（X-Z 剖面示意，单位 mm）", fontsize=17)

path = OUT / "options_abc_zh.png"
fig.savefig(path, dpi=115)
print("saved:", path)
