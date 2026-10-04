# -*- coding: utf-8 -*-
"""T06 POLLEN songqiu: right-side entry (remove left long tray) + 225deg lip pivot. Figure only. Unit mm."""
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

ANG = 52.0
T52 = (math.cos(math.radians(ANG)), math.sin(math.radians(ANG)))
N52 = (-math.sin(math.radians(ANG)), math.cos(math.radians(ANG)))
BALL_R = 35.56
R_CARRY = 58.4
R_SHELL = R_CARRY + BALL_R
TRAY_TOP = 17.5
BALL_Z = TRAY_TOP + BALL_R
C = (29.49, 111.46)
NIP = (52.31, 235.51)
A_EXIT = 142.0
A_ENTRY = 225.0
HUB_R, SWEEP_R = 18.0, 60.0
WHEEL_R, HALF = 48.0, 80.0
LEFT_X0, LEFT_X1 = -150.0, -80.0
RIGHT_X1, RIGHT_X0 = 175.0, -10.0
PHASES_OLD = (18.0, 138.0, 258.0)
PHASES_NEW = (273.6, 153.6, 33.6)  # = 叶片接触位相位 B_START 及其余两片

AX_A = (NIP[0] - HALF * math.sin(math.radians(ANG)), NIP[1] + HALF * math.cos(math.radians(ANG)))
AX_B = (NIP[0] + HALF * math.sin(math.radians(ANG)), NIP[1] - HALF * math.cos(math.radians(ANG)))

GREEN, RED, BLUE, ORANGE = "#1f7a3d", "#c00000", "#2b6a91", "#c8610f"
GRAY, PURPLE, DGRAY = "#9a9a9a", "#6b3fa0", "#666666"


def on_arc(a, r=R_CARRY, c=C):
    a = math.radians(a)
    return (c[0] + r * math.cos(a), c[1] + r * math.sin(a))


def arc_xy(a0, a1, r=R_CARRY, c=C, n=520):
    a = np.radians(np.linspace(a0, a1, n))
    return c[0] + r * np.cos(a), c[1] + r * np.sin(a)


# ================================ 数值核查 ================================
LIP = np.array(on_arc(A_ENTRY, R_SHELL))
P_ENTRY = np.array(on_arc(A_ENTRY, R_CARRY))
P_EXIT = np.array(on_arc(A_EXIT, R_CARRY))
E = np.array(on_arc(A_EXIT))

dx = math.sqrt(BALL_R ** 2 - (BALL_Z - LIP[1]) ** 2)
P_REST = np.array((LIP[0] + dx, BALL_Z))
v = P_REST - C
r_rest = float(np.linalg.norm(v))
a_rest = math.degrees(math.atan2(v[1], v[0])) % 360.0
a_l2r = math.degrees(math.atan2(P_REST[1] - LIP[1], P_REST[0] - LIP[0]))
a_l2e = math.degrees(math.atan2(P_ENTRY[1] - LIP[1], P_ENTRY[0] - LIP[0]))
TRAVEL = a_rest - A_EXIT
LIFT = P_ENTRY[1] - BALL_Z
DX_PIVOT = P_REST[0] - P_ENTRY[0]


def blade_angle(ball_center, sweep=SWEEP_R, r_ball=BALL_R):
    """叶片(径向段 r<=sweep) 刚好接触球时, 叶片角 = 球角 + d."""
    rc = float(np.linalg.norm(np.asarray(ball_center) - np.array(C)))
    if rc <= sweep:
        d = math.degrees(math.asin(r_ball / rc))
    else:
        d = math.degrees(math.acos((rc * rc + sweep * sweep - r_ball * r_ball) / (2.0 * rc * sweep)))
    return d


d_rest = blade_angle(P_REST)
B_START = a_rest + d_rest
B_END = A_EXIT + blade_angle(P_ENTRY)
BLADE_TRAVEL = B_START - B_END

# 左侧托板: 球沿 z=BALL_Z 从左往右滚, 与外罩(142-225, 内壁 R=93.96)相切的解析解
dx_blk = math.sqrt(max((R_SHELL + BALL_R) ** 2 - (BALL_Z - C[1]) ** 2, 0.0))
X_BLOCK = C[0] - dx_blk
P_BLOCK = np.array((X_BLOCK, BALL_Z))
_vb = P_BLOCK - C
a_block = math.degrees(math.atan2(_vb[1], _vb[0])) % 360.0
P_BLOCK_CT = np.asarray(C) + R_SHELL * _vb / float(np.linalg.norm(_vb))

# 出口直线到外罩最小距离
u = np.array([math.sin(math.radians(A_EXIT)), -math.cos(math.radians(A_EXIT))])
line = np.array([E + u * t for t in np.linspace(0.0, float(np.linalg.norm(np.array(NIP) - E)), 600)])
sx, sy = arc_xy(A_EXIT, A_ENTRY, R_SHELL, n=900)
SHELL = np.stack([sx, sy], axis=1)
d_line = min(float(np.linalg.norm(SHELL - p, axis=1).min()) for p in line)
D_LINE = float(np.linalg.norm(np.array(NIP) - E))

print("lip(225deg, R=93.96)      = (%.2f, %.2f)" % tuple(LIP))
print("entry ball center(225deg) = (%.2f, %.2f)  |P-C|=%.2f" % (P_ENTRY[0], P_ENTRY[1], np.linalg.norm(P_ENTRY - C)))
print("rest ball center (right)  = (%.2f, %.2f)  r=%.2f ang=%.2f deg  |rest-lip|=%.2f" % (P_REST[0], P_REST[1], r_rest, a_rest, np.linalg.norm(P_REST - LIP)))
print("pivot around lip: %.1f deg -> %.1f deg  (%.1f deg turn)" % (a_l2r, a_l2e, a_l2e - a_l2r))
print("lift dz = %.2f mm, travel dx = %.2f mm (to the left)" % (LIFT, DX_PIVOT))
print("paddle blade: contact at %.1f deg, release at %.1f deg -> stroke %.1f deg" % (B_START, B_END, BLADE_TRAVEL))
print("ball angular travel = %.1f deg (rest %.1f -> exit %.1f)" % (TRAVEL, a_rest, A_EXIT))
print("left tray blocked: x = %.2f, contact angle %.1f deg" % (X_BLOCK, a_block))
print("exit 142deg pos (%.2f,%.2f), straight to NIP = %.1f mm, clearance to cover = %.2f (ball R %.2f)" % (E[0], E[1], D_LINE, d_line, BALL_R))
print("left tray contact point = (%.2f, %.2f)" % tuple(P_BLOCK_CT))
_gx, _gy = arc_xy(A_EXIT, A_ENTRY, R_SHELL, n=900)
_SA = np.stack([_gx, _gy], axis=1)
_gap = []
for _f in np.linspace(0.0, 1.0, 201):
    _aa = math.radians(a_l2r + (a_l2e - a_l2r) * _f)
    _pp = LIP + BALL_R * np.array([math.cos(_aa), math.sin(_aa)])
    _gap.append(float(np.linalg.norm(_SA - _pp, axis=1).min()) - BALL_R)
print("pivot clearance to cover: min = %.2f mm  (>=0 -> 无干涉)" % min(_gap))


# ================================ 画图 ================================
def draw_tray(ax, x0, x1, color=BLUE, lw=7, ls="-", zorder=4):
    ax.plot([x0, x1], [TRAY_TOP, TRAY_TOP], color=color, lw=lw, ls=ls, solid_capstyle="butt", zorder=zorder)


def draw_shell(ax, a0, a1, color=GREEN, lw=7, ls="-", zorder=6):
    x, y = arc_xy(a0, a1, R_SHELL)
    ax.plot(x, y, color=color, lw=lw, ls=ls, solid_capstyle="round", zorder=zorder)


def draw_ball(ax, p, color=RED, lw=1.8, ls="-", zorder=8, r=BALL_R):
    ax.add_patch(Circle(tuple(p), r, fill=False, ec=color, lw=lw, ls=ls, zorder=zorder))
    ax.plot([p[0]], [p[1]], marker="+", ms=8, mew=1.6, color=color, zorder=zorder)


def draw_launcher(ax):
    for s in (0.0, 110.0):
        p0 = (12.53 + s * N52[0], 95.27 + s * N52[1])
        p1 = (p0[0] + 135.0 * T52[0], p0[1] + 135.0 * T52[1])
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color="#8a8a8a", lw=2.4, zorder=2)
    for c in (AX_A, AX_B):
        ax.add_patch(Circle(c, WHEEL_R, fill=False, ec="#111111", lw=2.0, zorder=3))
        ax.plot([c[0]], [c[1]], marker="+", ms=10, mew=1.6, color="#111111", zorder=3)
    ax.add_patch(Circle(NIP, 5.0, fc=RED, ec="none", zorder=6))
    ax.annotate("夹口", NIP, textcoords="offset points", xytext=(14, 14), fontsize=10.5, color=RED, zorder=20)


def draw_drum(ax, phases=PHASES_NEW):
    x, y = arc_xy(0, 360, SWEEP_R)
    ax.plot(x, y, color=ORANGE, lw=1.1, ls="--", alpha=0.75, zorder=2)
    for ph in phases:
        a = math.radians(ph)
        p0 = (C[0] + HUB_R * math.cos(a), C[1] + HUB_R * math.sin(a))
        p1 = (C[0] + SWEEP_R * math.cos(a), C[1] + SWEEP_R * math.sin(a))
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=ORANGE, lw=5.5, solid_capstyle="round", zorder=3)
    ax.add_patch(Circle(C, HUB_R, fc="#f6e0cb", ec=ORANGE, lw=1.8, zorder=4))
    ax.plot([C[0]], [C[1]], marker="+", ms=10, mew=1.8, color=ORANGE, zorder=5)
    ax.plot([C[0], AX_A[0]], [C[1], AX_A[1]], color=ORANGE, lw=1.0, ls=":", alpha=0.8, zorder=2)
    ax.plot([C[0], NIP[0]], [C[1], NIP[1]], color=ORANGE, lw=1.0, ls=":", alpha=0.8, zorder=2)


def arrow(ax, p0, p1, color=RED, lw=2.6, ms=20, zorder=12, ls="-"):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=ms, lw=lw, color=color,
                                 shrinkA=0, shrinkB=0, zorder=zorder, linestyle=ls))


def path_arrows(ax, pts, idx, color=RED, lw=2.4, ms=16, zorder=11, step=12):
    for i in idx:
        j = min(i + step, len(pts) - 1)
        if j > i:
            arrow(ax, tuple(pts[i]), tuple(pts[j]), color=color, lw=lw, ms=ms, zorder=zorder)


def lab_at(ax, xy, text_xy, text, color="#333333", fs=10.5, ha="left"):
    ax.annotate(text, xy=xy, xytext=text_xy, textcoords="data", fontsize=fs, color=color,
                zorder=30, ha=ha, va="center", linespacing=1.5,
                arrowprops=dict(arrowstyle="->", color=color, lw=1.1, shrinkA=2, shrinkB=4))


def note(ax, s, xy, color="#333333", fs=10.5):
    ax.text(xy[0], xy[1], s, fontsize=fs, color=color, ha="left", va="top", zorder=30,
            linespacing=1.65, bbox=dict(boxstyle="round,pad=0.45", fc="white", ec=color, lw=1.3, alpha=0.96))


fig, axes = plt.subplots(1, 2, figsize=(17.4, 9.4))
fig.subplots_adjust(left=0.045, right=0.985, top=0.90, bottom=0.095, wspace=0.10)

# ---------------- (1) 整体 ----------------
ax = axes[0]
draw_drum(ax)
draw_launcher(ax)
draw_shell(ax, A_EXIT, A_ENTRY, color=GREEN, lw=7.5)
draw_tray(ax, LEFT_X0, LEFT_X1, color=GRAY, lw=6, ls=(0, (6, 5)), zorder=3)
draw_tray(ax, RIGHT_X1, RIGHT_X0, color=BLUE, lw=7.5, zorder=4)

carry = np.stack(arc_xy(A_ENTRY, A_EXIT, R_CARRY, n=320), axis=1)
path_arrows(ax, carry, [40, 110, 180, 250], step=16, color=RED)
arrow(ax, tuple(E), NIP, color=RED, lw=2.4, ms=20)
arrow(ax, (120.0, BALL_Z), (60.0, BALL_Z), color=BLUE, lw=2.6, ms=20, zorder=11)

draw_ball(ax, P_BLOCK, color=GRAY, lw=1.3, ls=(0, (4, 3)))
ax.plot([P_BLOCK[0]], [P_BLOCK[1]], marker="x", ms=11, mew=2.4, color=GRAY, zorder=9)
draw_ball(ax, P_REST, color=RED, lw=1.9)
draw_ball(ax, P_ENTRY, color=RED, lw=1.9)
for a in (196.0, 168.0):
    draw_ball(ax, on_arc(a), color=GRAY, lw=1.2, ls=(0, (4, 3)))
draw_ball(ax, P_EXIT, color=RED, lw=1.5, ls=(0, (5, 3)))

ax.add_patch(FancyArrowPatch(on_arc(268.0, 50.0), on_arc(225.0, 50.0), connectionstyle="arc3,rad=0.28",
                             arrowstyle="-|>", mutation_scale=20, lw=2.6, color=PURPLE, zorder=10))
lab_at(ax, on_arc(247.0, 50.0), (-118.0, -40.0), "拨杆：本图顺时针\n（俯视看是同一转向）", PURPLE, 10.5)
lab_at(ax, P_BLOCK, (-205.0, 108.0), "原左侧长托板：球滚到 x=%.1f 就被\n外罩(206.8°)挡住 → 已无用，删除" % X_BLOCK, GRAY, 10.5)
lab_at(ax, (100.0, TRAY_TOP), (-30.0, -58.0), "新右侧托板（顶面 z=17.5）\n球从此进入", BLUE, 10.5)
lab_at(ax, tuple(P_REST), (150.0, 20.0), "球停在这里\n球心 (%.1f, %.1f)" % tuple(P_REST), RED, 10.5)
lab_at(ax, tuple(P_ENTRY), (-208.0, 210.0), "225° 就位点\n球心 (%.1f, %.1f)" % tuple(P_ENTRY), RED, 10.5)
lab_at(ax, on_arc(180.0, R_SHELL), (-206.0, 148.0), "外罩 142°-225°（83°）", GREEN, 10.5)
lab_at(ax, tuple(P_EXIT), (150.0, 122.0), "出口 142°，切向 52°\n直线到夹口 %.1f mm" % D_LINE, RED, 10.5, ha="right")
lab_at(ax, tuple(E + u * 40.0), (150.0, 190.0), "外罩让开：直线到外罩最小 %.1f mm\n（= 球半径，正好相切）" % d_line, DGRAY, 10.0, ha="right")

note(ax, "① 整体：球只从右侧进料，拨杆从右侧压下，把球沿外罩推到 142° 出口\n"
         "· 左侧长托板（0° 段，x=-150..-80）确认无用：球沿 z=53.06 从左往右滚，到 x=%.1f 就顶到\n"
         "  142°-225° 外罩（接触点 206.8°）→ 直接删掉，不再保留。\n"
         "· 新右侧托板顶面 z=17.5（沿用原托板高度），球从右侧滚入。\n"
         "· 球在托板上贴住外罩下端(225°)的边停下：球心 (%.1f, %.1f)（= 本图 241.4° 方向、r=%.1f）。\n"
         "· 拨杆从右侧压下 → 球绕 225° 那条边向上翻 %.0f°，落到球心圆 225° 就位点 (%.1f, %.1f)，\n"
         "  这段抬高 %.2f mm、水平只走 %.2f mm —— 所以不需要额外做斜坡。\n"
         "· 之后球贴外罩内壁由 225° 推到 142°；拨杆总推程 %.0f°，球总转角 %.1f° ≈ 100°。"
         % (X_BLOCK, P_REST[0], P_REST[1], r_rest, a_l2e - a_l2r, P_ENTRY[0], P_ENTRY[1], LIFT, DX_PIVOT,
            BLADE_TRAVEL, TRAVEL),
     (-205.0, 470.0), GREEN)

ax.set_title("① 整体：右侧进料 + 球绕 225° 边就位 + 推到 142° 出口", fontsize=13.5, pad=10)

# ---------------- (2) 进料细节 ----------------
ax = axes[1]
draw_drum(ax, PHASES_NEW)
draw_shell(ax, A_EXIT, A_ENTRY, color=GREEN, lw=7.5)
draw_tray(ax, RIGHT_X1, RIGHT_X0, color=BLUE, lw=7.5, zorder=4)
draw_tray(ax, LEFT_X0, LEFT_X1, color=GRAY, lw=6, ls=(0, (6, 5)), zorder=3)

# 翻转圆弧（球心绕 225° 边，半径 = 球半径）
t = np.radians(np.linspace(a_l2r, a_l2e, 200))
ax.plot(LIP[0] + BALL_R * np.cos(t), LIP[1] + BALL_R * np.sin(t), color=PURPLE, lw=1.8, ls=(0, (6, 4)), zorder=7)
ax.add_patch(Circle(tuple(LIP), 5.5, fc=GREEN, ec="white", lw=1.2, zorder=10))
ax.plot([LIP[0] - 14.0, LIP[0] + 14.0], [LIP[1], LIP[1]], color=GREEN, lw=1.0, ls=":", zorder=9)
ax.plot([LIP[0], LIP[0]], [LIP[1] - 14.0, LIP[1] + 14.0], color=GREEN, lw=1.0, ls=":", zorder=9)

draw_ball(ax, P_REST, color=RED, lw=2.0)
draw_ball(ax, P_ENTRY, color=GREEN, lw=2.2)
pivot = np.array([LIP + BALL_R * np.array([math.cos(aa), math.sin(aa)]) for aa in np.radians(np.linspace(a_l2r, a_l2e, 6))])
for i in range(5):
    arrow(ax, tuple(pivot[i]), tuple(pivot[i + 1]), color=PURPLE, lw=2.2, ms=15, zorder=11)

# 抬高 / 水平尺寸
ax.annotate("", xy=(P_ENTRY[0], P_ENTRY[1]), xytext=(P_ENTRY[0], BALL_Z),
            arrowprops=dict(arrowstyle="<|-|>", color=DGRAY, lw=1.6), zorder=12)
ax.text(P_ENTRY[0] - 4.0, (P_ENTRY[1] + BALL_Z) / 2.0, "抬高 %.1f mm" % LIFT, fontsize=10.5, color=DGRAY,
        ha="right", va="center", zorder=20)
ax.plot([P_ENTRY[0], P_REST[0]], [BALL_Z, BALL_Z], color=DGRAY, lw=1.0, ls=":", zorder=9)
ax.annotate("", xy=(P_REST[0], BALL_Z - 30.0), xytext=(P_ENTRY[0], BALL_Z - 30.0),
            arrowprops=dict(arrowstyle="<|-|>", color=DGRAY, lw=1.6), zorder=12)
ax.text((P_REST[0] + P_ENTRY[0]) / 2.0, BALL_Z - 33.0, "水平 %.1f mm" % DX_PIVOT, fontsize=10.5, color=DGRAY,
        ha="center", va="top", zorder=20)

draw_ball(ax, on_arc(196.0), color=GRAY, lw=1.3, ls=(0, (4, 3)))
lab_at(ax, LIP, (-64.0, 96.0), "外罩下端 = 225°\n（球就绕这条边翻上去）", GREEN, 10.5)
lab_at(ax, tuple(P_REST), (92.0, 46.0), "球在托板上停住\n球心 (%.1f, %.1f)，本图 241.4°\n（托板顶面 z=17.5）" % tuple(P_REST), RED, 10.5)
lab_at(ax, tuple(P_ENTRY), (58.0, 104.0), "225° 就位点\n球心 (%.1f, %.1f)（在球心圆上，\n与外罩内壁相切）" % tuple(P_ENTRY), GREEN, 10.5)
lab_at(ax, tuple(on_arc(196.0)), (58.0, 150.0), "之后沿外罩内壁 225°→142°", RED, 10.5)
lab_at(ax, tuple(pivot[3]), (-70.0, -30.0), "球心绕 225° 边转 %.0f°" % (a_l2e - a_l2r), PURPLE, 10.5)

# 叶片：接触位 + 释放位
for bb, cc, txt, txy in ((B_START, RED, "叶片接触位 273.6°", (52.0, 62.0)),
                         (B_END, GREEN, "叶片释放位 179.5°", (-72.0, 140.0))):
    a = math.radians(bb)
    ax.plot([C[0] + HUB_R * math.cos(a), C[0] + SWEEP_R * math.cos(a)],
            [C[1] + HUB_R * math.sin(a), C[1] + SWEEP_R * math.sin(a)],
            color=cc, lw=5.0, solid_capstyle="round", zorder=5)
    lab_at(ax, (C[0] + SWEEP_R * math.cos(a), C[1] + SWEEP_R * math.sin(a)), txy, txt, cc, 10.5)
ax.add_patch(FancyArrowPatch(on_arc(268.0, 52.0), on_arc(240.0, 52.0), connectionstyle="arc3,rad=0.30",
                             arrowstyle="-|>", mutation_scale=18, lw=2.4, color=PURPLE, zorder=10))

note(ax, "② 进料细节：不需要斜坡\n"
         "1) 球从右侧托板滚入 → 被外罩下端 225° 的边挡住，停在\n"
         "    (球心 %.1f, %.1f)；到该边距离恒 = 球半径 %.2f，所以能绕着它转。\n"
         "2) 拨杆（本图顺时针）在 %.1f° 接触，推程 %.1f°，球被压在边上只能向上翻。\n"
         "3) 球心绕 225° 边转 %.1f°，抬高 %.1f mm → 落在球心圆 225° 就位点 (球心 %.1f, %.1f)\n"
         "   与外罩内壁正好相切 → 之后贴内壁 225°→142°；球总转 %.1f° ≈ 100°"
         % (P_REST[0], P_REST[1], BALL_R, B_START, BLADE_TRAVEL, a_l2e - a_l2r, LIFT, P_ENTRY[0], P_ENTRY[1], TRAVEL),
     (-72.0, -22.0), PURPLE)

ax.set_title("② 进料放大：球绕外罩 225° 边翻转就位（抬高 %.1f mm）" % LIFT, fontsize=13.5, pad=10)

for a in axes:
    a.set_aspect("equal")
    a.grid(alpha=0.22, lw=0.6)
    a.set_xlabel("X [mm]")
    a.set_ylabel("Z [mm]")

axes[0].set_xlim(-215, 215)
axes[0].set_ylim(-80, 480)
axes[1].set_xlim(-85, 135)
axes[1].set_ylim(-95, 175)

fig.suptitle("T06 POLLEN 送球段：改为右侧进料 + 剔除左侧长托板（X-Z 剖面，单位 mm）", fontsize=16)
fig.text(0.5, 0.022,
         "左右约定：按本图坐标 —— X 正方向为“右”、Z 向上。发射部分在拨杆右侧（图上），托板在拨杆左侧（图上）即为“左侧长托板”。",
         ha="center", fontsize=11.5, color="#333333")
path = OUT / "options_b_right_tray_zh.png"
fig.savefig(path, dpi=120)
print("saved:", path)