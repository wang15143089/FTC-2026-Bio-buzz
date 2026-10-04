# -*- coding: utf-8 -*-
"""T06 POLLEN 送球段 方案B 修订版：开口朝左 + 拨杆反转 + 球从左侧送入。
只出图，不修改任何 CAD 文件。单位 mm。"""
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
from matplotlib.patches import Circle, FancyArrowPatch

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
R_SHELL = R_CARRY + BALL_R          # 93.96
TRAY_TOP = 17.5
BALL_Z = TRAY_TOP + BALL_R          # 53.06
C = (29.49, 111.46)                 # 鼓 / 拨杆轴
GUIDE_END = (12.53, 95.27)
NIP = (52.31, 235.51)
A_EXIT = 142.0
A_ENTER = 250.0
A_TAIL = A_ENTER + 252.0            # 502 == 142 + 360
HUB_R, SWEEP_R = 18.0, 60.0
WHEEL_R, HALF = 48.0, 80.0
AX_A = (NIP[0] - HALF * math.sin(math.radians(ANG)),
        NIP[1] + HALF * math.cos(math.radians(ANG)))
AX_B = (NIP[0] + HALF * math.sin(math.radians(ANG)),
        NIP[1] - HALF * math.cos(math.radians(ANG)))
PHASES = (18.0, 138.0, 258.0)

GREEN = "#1f7a3d"
RED = "#c00000"
BLUE = "#2b6a91"
ORANGE = "#c8610f"
GRAY = "#9a9a9a"
PURPLE = "#6b3fa0"
DGRAY = "#666666"


def on_arc(a_deg, r=R_CARRY, c=C):
    a = math.radians(a_deg)
    return (c[0] + r * math.cos(a), c[1] + r * math.sin(a))


def arc_xy(a0, a1, r=R_CARRY, c=C, n=520):
    a = np.radians(np.linspace(a0, a1, n))
    return c[0] + r * np.cos(a), c[1] + r * np.sin(a)


def bez(p0, p1, p2, p3, n=240):
    t = np.linspace(0.0, 1.0, n)[:, None]
    P = np.array([p0, p1, p2, p3], float)
    return ((1 - t) ** 3) * P[0] + 3 * ((1 - t) ** 2) * t * P[1] + 3 * (1 - t) * t ** 2 * P[2] + t ** 3 * P[3]


LIP = on_arc(A_ENTER, R_SHELL)
P_TRAY = (-72.0, BALL_Z)
P_ENTER = on_arc(A_ENTER)


def make_ramp(bulge):
    p0 = P_TRAY
    p1 = (p0[0] + 26.0, p0[1] + 1.2 * bulge)
    p2 = (P_ENTER[0] - 22.0, P_ENTER[1] + 1.8 * bulge)
    return bez(p0, p1, p2, P_ENTER, 240)


lip_clear = lambda path: float(np.linalg.norm(path - np.array(LIP), axis=1).min())

NEED = BALL_R - 0.05
bulge, best_b, best_v = None, 0.0, -1e9
for k in range(240):
    b = k * 0.2
    v = lip_clear(make_ramp(b))
    if v > best_v:
        best_b, best_v = b, v
    if v >= NEED:
        bulge = b
        break
if bulge is None:
    bulge = best_b
ramp = make_ramp(bulge)

carry = np.stack(arc_xy(A_ENTER, A_TAIL, R_CARRY, n=420), axis=1)
full_path = np.vstack([ramp, carry])
sx, sy = arc_xy(A_ENTER, A_TAIL, R_SHELL, n=700)
SHELL_PTS = np.stack([sx, sy], axis=1)
dmin = min(float(np.linalg.norm(SHELL_PTS - p, axis=1).min()) for p in full_path)
tray_pts = np.stack([np.linspace(-150.0, P_TRAY[0], 120), np.full(120, BALL_Z)], axis=1)
dmin_tray = min(float(np.linalg.norm(SHELL_PTS - p, axis=1).min()) for p in tray_pts)

print("[check] ramp bulge = %.2f mm" % bulge)
print("[check] 球心到外罩最小距离（斜坡+球心圆）= %.2f mm  (球半径 %.2f)" % (dmin, BALL_R))
print("[check] 球心到外罩最小距离（托板段）      = %.2f mm" % dmin_tray)
print("[check] 唇口坐标 = (%.2f, %.2f)" % LIP)


# ------------------------------------------------------------------ 画图元件
def draw_tray(ax, x0, x1, color=BLUE, lw=7, ls="-", alpha=1.0, zorder=4):
    ax.plot([x0, x1], [TRAY_TOP, TRAY_TOP], color=color, lw=lw, ls=ls, alpha=alpha,
            solid_capstyle="butt", zorder=zorder)


def draw_shell(ax, a0, a1, color=GREEN, lw=7, ls="-", alpha=1.0, zorder=6, n=520):
    x, y = arc_xy(a0, a1, R_SHELL, n=n)
    ax.plot(x, y, color=color, lw=lw, ls=ls, alpha=alpha, solid_capstyle="round", zorder=zorder)


def draw_ball(ax, p, color=RED, lw=1.8, ls="-", zorder=8):
    ax.add_patch(Circle(p, BALL_R, fill=False, ec=color, lw=lw, ls=ls, zorder=zorder))
    ax.plot([p[0]], [p[1]], marker="+", ms=8, mew=1.6, color=color, zorder=zorder)


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
    ax.annotate("夹口", NIP, textcoords="offset points", xytext=(14, 14), fontsize=10.5,
                color=RED, zorder=20)


def draw_drum(ax, blades=True, hub=True, sweep=True):
    if sweep:
        x, y = arc_xy(0, 360, SWEEP_R)
        ax.plot(x, y, color=ORANGE, lw=1.1, ls="--", alpha=0.75, zorder=2)
    if blades:
        for ph in PHASES:
            a = math.radians(ph)
            p0 = (C[0] + HUB_R * math.cos(a), C[1] + HUB_R * math.sin(a))
            p1 = (C[0] + SWEEP_R * math.cos(a), C[1] + SWEEP_R * math.sin(a))
            ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=ORANGE, lw=5.5,
                    solid_capstyle="round", zorder=3)
    if hub:
        ax.add_patch(Circle(C, HUB_R, fc="#f6e0cb", ec=ORANGE, lw=1.8, zorder=4))
        ax.plot([C[0]], [C[1]], marker="+", ms=10, mew=1.8, color=ORANGE, zorder=5)


def arrow(ax, p0, p1, color=RED, lw=2.6, ms=20, zorder=9):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=ms, lw=lw,
                                 color=color, shrinkA=0, shrinkB=0, zorder=zorder))


def path_arrows(ax, pts, idx, color=RED, lw=2.4, ms=18, zorder=9, step=14):
    n = len(pts)
    for i in idx:
        j = min(i + step, n - 1)
        if j > i:
            arrow(ax, tuple(pts[i]), tuple(pts[j]), color=color, lw=lw, ms=ms, zorder=zorder)


def wall_of(pts, r=BALL_R):
    out = []
    m = len(pts)
    for i, p in enumerate(pts):
        w = i / (m - 1.0)
        n1 = np.array([0.0, -1.0])
        v = np.array([p[0] - C[0], p[1] - C[1]])
        n2 = v / np.linalg.norm(v)
        nn = (1 - w) * n1 + w * n2
        nn = nn / np.linalg.norm(nn)
        out.append(np.array([p[0], p[1]]) + r * nn)
    return np.array(out)


def lab(ax, xy, text, xytext, color="#333333", fs=10.0, ha="left"):
    ax.annotate(text, xy, textcoords="offset points", xytext=xytext, fontsize=fs,
                color=color, zorder=30, linespacing=1.5, ha=ha,
                arrowprops=dict(arrowstyle="->", color=color, lw=1.1, shrinkA=2, shrinkB=4))


def lab_at(ax, xy, text_xy, text, color="#333333", fs=10.0, ha="left", lw=1.1):
    ax.annotate(text, xy=xy, xytext=text_xy, textcoords="data", fontsize=fs,
                color=color, zorder=30, ha=ha, va="center", linespacing=1.5,
                arrowprops=dict(arrowstyle="->", color=color, lw=lw, shrinkA=2, shrinkB=4))


def note(ax, s, xy, color="#333333", fs=10.5):
    ax.text(xy[0], xy[1], s, fontsize=fs, color=color, ha="left", va="top", zorder=30,
            linespacing=1.7,
            bbox=dict(boxstyle="round,pad=0.45", fc="white", ec=color, lw=1.3, alpha=0.96))


# ------------------------------------------------------------------ 版面
fig, axes = plt.subplots(1, 2, figsize=(17.6, 9.8),
                         gridspec_kw=dict(width_ratios=[1.40, 1.0]))
fig.subplots_adjust(left=0.05, right=0.985, top=0.905, bottom=0.055, wspace=0.10)

# ============================== (A) 整体 ==============================
ax = axes[0]
draw_drum(ax)
draw_launcher(ax)
draw_tray(ax, -150.0, C[0])
draw_shell(ax, A_ENTER, A_TAIL, color=GREEN, lw=7.5)
draw_shell(ax, A_EXIT, A_ENTER, color=GRAY, lw=4.0, ls=(0, (6, 5)), alpha=0.9)

wp = wall_of(ramp)
ax.plot(wp[:, 0], wp[:, 1], color=GREEN, lw=6.0, solid_capstyle="round", zorder=6)
ax.plot(ramp[:, 0], ramp[:, 1], color=RED, lw=1.8, ls=(0, (7, 4)), zorder=7)
ax.add_patch(Circle(LIP, 4.5, fc=RED, ec="white", lw=1.0, zorder=10))

path_arrows(ax, ramp, [55, 140, 200], step=18)
path_arrows(ax, carry, [30, 110, 190, 270, 350], step=16)
arrow(ax, on_arc(A_TAIL - 8.0), NIP, color=RED, lw=2.4, ms=20, zorder=9)

draw_ball(ax, tuple(ramp[120]), color=GRAY, lw=1.3, ls=(0, (4, 3)))
draw_ball(ax, P_ENTER, color=RED, lw=1.9)
for a in (272.0, 320.0, 30.0, 88.0):
    draw_ball(ax, on_arc(a), color=GRAY, lw=1.2, ls=(0, (4, 3)))
draw_ball(ax, on_arc(A_EXIT), color=RED, lw=1.6, ls=(0, (5, 3)))

lab_at(ax, tuple(ramp[60]), (-205.0, 62.0), "导入斜坡（越过唇口）", GREEN, 10.5)
lab_at(ax, on_arc(200.0, R_SHELL), (-92.0, 122.0), "开口 142°-250°（朝左）", DGRAY, 10.5, ha="right")
lab_at(ax, on_arc(315.0), (206.0, 42.0), "球贴外罩内壁走 ≈252°", GREEN, 10.5, ha="right")
lab_at(ax, on_arc(A_EXIT), (-140.0, 205.0), "出口 142°", RED, 10.5)
lab_at(ax, LIP, (-58.0, -58.0), "外罩唇口 ≈250°", RED, 10.0)
lab_at(ax, (-140.0, TRAY_TOP), (-205.0, -20.0), "托板（左侧送入）", BLUE, 10.5)
lab_at(ax, C, (96.0, -58.0), "拨杆：逆时针（紫弧箭）", PURPLE, 10.5)

ax.add_patch(FancyArrowPatch(on_arc(78.0, 74.0), on_arc(44.0, 74.0),
                             connectionstyle="arc3,rad=0.32", arrowstyle="-|>",
                             mutation_scale=20, lw=2.6, color=PURPLE, zorder=10))

note(ax, "方案B 修订：开口朝左 + 拨杆反转 + 球从左侧送入\n"
         "外罩只做 250°→142°（逆时针经鼓底 270°、右侧 0°、顶部 90°），开口 142°-250° 朝左。\n"
         "球沿托板右滚，在唇口前由导入斜坡抬起约 %.0f mm 越过唇口，落到球心圆 R58.4 的 ≈250°。\n"
         "拨杆逆时针把球从 250° 一路带到 142°，全程贴外罩内壁，不缺支撑。\n"
         "142° 处切向脱离，沿 52° 进入夹口 —— 与发射段对接方向不变。"
         % (bulge,), (-212.0, 494.0), GREEN)

ax.set_title("① 方案B 修订：开口朝左、球从左侧送入、拨杆反转", fontsize=14, pad=10)

# ============================== (B) 进料口局部 ==============================
ax = axes[1]
draw_tray(ax, -118.0, C[0])
draw_shell(ax, A_ENTER, A_TAIL, color=GREEN, lw=7.5)
draw_shell(ax, A_EXIT - 360.0, A_ENTER, color=GRAY, lw=4.0, ls=(0, (6, 5)), alpha=0.9)
ax.plot(wp[:, 0], wp[:, 1], color=GREEN, lw=6.0, solid_capstyle="round", zorder=6)
ax.plot(ramp[:, 0], ramp[:, 1], color=RED, lw=1.8, ls=(0, (7, 4)), zorder=7)
ax.add_patch(Circle(LIP, 4.5, fc=RED, ec="white", lw=1.0, zorder=10))
ax.add_patch(Circle(LIP, BALL_R, fill=False, ec=GRAY, lw=1.1, ls=(0, (3, 3)), zorder=5))

for f in (0.0, 0.30, 0.55, 0.78, 1.0):
    i = int(round(f * (len(ramp) - 1)))
    draw_ball(ax, tuple(ramp[i]), color=RED if f == 1.0 else GRAY,
              lw=1.9 if f == 1.0 else 1.2, ls="-" if f == 1.0 else (0, (4, 3)))
path_arrows(ax, ramp, [30, 100, 170, 215], step=20)

lab_at(ax, LIP, (18.0, 62.0), "唇口 ≈250°", RED, 11.0)
lab_at(ax, tuple(ramp[150]), (-100.0, 84.0), "导入斜坡", GREEN, 11.0)
lab_at(ax, (-110.0, TRAY_TOP), (-120.0, -12.0), "托板（左侧送入）", BLUE, 11.0)
lab_at(ax, (LIP[0] - BALL_R, LIP[1]), (-58.0, -36.0), "虚线圈 = 球心禁区 R35.56", GRAY, 10.5)

note(ax, "进料口局部\n"
         "球沿托板右滚，球心到唇口最近 %.1f mm ≥ 球半径 35.56，能越过不会顶死。\n"
         "斜坡把球心抬高约 %.0f mm，越过唇口后落到球心圆 R58.4 的 ≈250°，\n"
         "之后交给拨杆（逆时针）带走。"
         % (lip_clear(ramp), bulge), (-116.0, 176.0), RED)

ax.set_title("② 进料口局部：托板 → 斜坡 → 越过唇口进鼓", fontsize=14, pad=10)

for a in axes:
    a.set_aspect("equal")
    a.grid(alpha=0.22, lw=0.6)
    a.set_xlabel("X [mm]")
    a.set_ylabel("Z [mm]")
axes[0].set_xlim(-218, 218)
axes[0].set_ylim(-88, 500)
axes[1].set_xlim(-124, 66)
axes[1].set_ylim(-44, 180)

fig.suptitle("T06 POLLEN 送球段：方案B 修订（开口朝左 / 拨杆反转 / 左侧进料），X-Z 剖面，单位 mm",
             fontsize=16)

path = OUT / "options_b_left_zh.png"
fig.savefig(path, dpi=120)
print("saved:", path)

