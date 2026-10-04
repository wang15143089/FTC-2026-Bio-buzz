# -*- coding: utf-8 -*-
"""T06 POLLEN 送球段：出口方向问题 + 修正（外罩缩短 / 入口提前）。只出图，不改 CAD。单位 mm。"""
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
GUIDE_END = (12.53, 95.27)
NIP = (52.31, 235.51)
A_EXIT = 142.0
A_ENTER_OLD = 250.0
A_ENTER_NEW = 225.0
HUB_R, SWEEP_R = 18.0, 60.0
WHEEL_R, HALF = 48.0, 80.0
AX_A = (NIP[0] - HALF * math.sin(math.radians(ANG)), NIP[1] + HALF * math.cos(math.radians(ANG)))
AX_B = (NIP[0] + HALF * math.sin(math.radians(ANG)), NIP[1] - HALF * math.cos(math.radians(ANG)))
PHASES = (18.0, 138.0, 258.0)

GREEN, RED, BLUE, ORANGE = "#1f7a3d", "#c00000", "#2b6a91", "#c8610f"
GRAY, PURPLE, DGRAY = "#9a9a9a", "#6b3fa0", "#666666"


def on_arc(a, r=R_CARRY, c=C):
    a = math.radians(a)
    return (c[0] + r * math.cos(a), c[1] + r * math.sin(a))


def arc_xy(a0, a1, r=R_CARRY, c=C, n=520):
    a = np.radians(np.linspace(a0, a1, n))
    return c[0] + r * np.cos(a), c[1] + r * np.sin(a)


def bez(p0, p1, p2, p3, n=240):
    t = np.linspace(0.0, 1.0, n)[:, None]
    P = np.array([p0, p1, p2, p3], float)
    return ((1 - t) ** 3) * P[0] + 3 * ((1 - t) ** 2) * t * P[1] + 3 * (1 - t) * t ** 2 * P[2] + t ** 3 * P[3]


# ------------------------------------------------------- 出口方向核算
D = np.array(NIP) - np.array(C)
L = float(np.linalg.norm(D))
phi = math.degrees(math.atan2(D[1], D[0]))
half = math.degrees(math.acos(R_CARRY / L))
sol = []
for th in (phi - half, phi + half):
    v = np.array([math.sin(math.radians(th)), -math.cos(math.radians(th))])   # 顺时针切向
    t = float(D @ v)
    sol.append((th, t))
    print("[dir] 出口角 %.2f deg, 顺时针切向 %.1f deg, 到夹口行程 %.1f mm" %
          (th, math.degrees(math.atan2(v[1], v[0])), t))
print("[dir] 逆时针在 142 deg 的切向 = %.1f deg (指向左下)" %
      math.degrees(math.atan2(math.cos(math.radians(A_EXIT)), -math.sin(math.radians(A_EXIT)))))
print("[dir] 顺时针在 142 deg 的切向 = %.1f deg (指向夹口)" %
      math.degrees(math.atan2(-math.cos(math.radians(A_EXIT)), math.sin(math.radians(A_EXIT)))))

# ------------------------------------------------------- 修正方案几何
P_ENTER_NEW = on_arc(A_ENTER_NEW)
LIP_NEW = on_arc(A_ENTER_NEW, R_SHELL)


def make_ramp(bulge):
    p0 = (-95.0, BALL_Z)
    p1 = (p0[0] + 26.0, p0[1] + 1.2 * bulge)
    p2 = (P_ENTER_NEW[0] - 22.0, P_ENTER_NEW[1] + 1.8 * bulge)
    return bez(p0, p1, p2, P_ENTER_NEW, 240)


lip_clear = lambda pth: float(np.linalg.norm(pth - np.array(LIP_NEW), axis=1).min())
NEED = BALL_R - 0.05
bulge, best_b, best_v = None, 0.0, -1e9
for k in range(300):
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
carry = np.stack(arc_xy(A_ENTER_NEW, A_EXIT, R_CARRY, n=320), axis=1)
path_pts = np.vstack([ramp, carry])
sx, sy = arc_xy(A_EXIT, A_ENTER_NEW, R_SHELL, n=600)
SHELL2 = np.stack([sx, sy], axis=1)
d_shell = min(float(np.linalg.norm(SHELL2 - p, axis=1).min()) for p in path_pts)

# 出口直线到夹口，检查外罩是否挡路
E = np.array(on_arc(A_EXIT))
u = np.array([math.sin(math.radians(A_EXIT)), -math.cos(math.radians(A_EXIT))])
line = np.array([E + u * t for t in np.linspace(0.0, np.linalg.norm(np.array(NIP) - E), 400)])
d_line = min(float(np.linalg.norm(SHELL2 - p, axis=1).min()) for p in line)

print("[chk] ramp bulge = %.2f mm" % bulge)
print("[chk] 球心到外罩最小距离（托板+斜坡+球心圆）= %.2f mm (球半径 %.2f)" % (d_shell, BALL_R))
print("[chk] 出口直线到外罩最小距离 = %.2f mm (需 >= %.2f)" % (d_line, BALL_R))
print("[chk] 新入口角 %.0f deg, 拨杆行程 = %.0f deg (旧版 %.0f deg)" %
      (A_ENTER_NEW, A_ENTER_NEW - A_EXIT, A_ENTER_OLD - A_EXIT))
print("[chk] 入口球心 (%0.2f, %0.2f), 抬升 %.1f mm" % (P_ENTER_NEW + (P_ENTER_NEW[1] - BALL_Z,)))


# ------------------------------------------------------- 画图元件
def draw_tray(ax, x0, x1, color=BLUE, lw=7, ls="-", zorder=4):
    ax.plot([x0, x1], [TRAY_TOP, TRAY_TOP], color=color, lw=lw, ls=ls,
            solid_capstyle="butt", zorder=zorder)


def draw_shell(ax, a0, a1, color=GREEN, lw=7, ls="-", zorder=6):
    x, y = arc_xy(a0, a1, R_SHELL)
    ax.plot(x, y, color=color, lw=lw, ls=ls, solid_capstyle="round", zorder=zorder)


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
        ax.plot([c[0]], [c[1]], marker="+", ms=10, mew=1.6, color="#111111", zorder=3)
    ax.add_patch(Circle(NIP, 5.0, fc=RED, ec="none", zorder=6))
    ax.annotate("夹口", NIP, textcoords="offset points", xytext=(14, 14), fontsize=10.5, color=RED, zorder=20)


def draw_drum(ax, phases=PHASES):
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
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=ms, lw=lw,
                                 color=color, shrinkA=0, shrinkB=0, zorder=zorder, linestyle=ls))


def path_arrows(ax, pts, idx, color=RED, lw=2.4, ms=18, zorder=11, step=12):
    for i in idx:
        j = min(i + step, len(pts) - 1)
        if j > i:
            arrow(ax, tuple(pts[i]), tuple(pts[j]), color=color, lw=lw, ms=ms, zorder=zorder)


def wall_of(pts, r=BALL_R):
    out, m = [], len(pts)
    for i, p in enumerate(pts):
        w = i / (m - 1.0)
        n1 = np.array([0.0, -1.0])
        v = np.array([p[0] - C[0], p[1] - C[1]])
        n2 = v / np.linalg.norm(v)
        nn = (1 - w) * n1 + w * n2
        out.append(np.array([p[0], p[1]]) + r * nn / np.linalg.norm(nn))
    return np.array(out)


def lab_at(ax, xy, text_xy, text, color="#333333", fs=10.5, ha="left"):
    ax.annotate(text, xy=xy, xytext=text_xy, textcoords="data", fontsize=fs, color=color,
                zorder=30, ha=ha, va="center", linespacing=1.5,
                arrowprops=dict(arrowstyle="->", color=color, lw=1.1, shrinkA=2, shrinkB=4))


def note(ax, s, xy, color="#333333", fs=10.5):
    ax.text(xy[0], xy[1], s, fontsize=fs, color=color, ha="left", va="top", zorder=30,
            linespacing=1.65, bbox=dict(boxstyle="round,pad=0.45", fc="white", ec=color, lw=1.3, alpha=0.96))


# ------------------------------------------------------- 版面
fig, axes = plt.subplots(1, 2, figsize=(17.4, 9.4))
fig.subplots_adjust(left=0.05, right=0.985, top=0.90, bottom=0.095, wspace=0.09)

# ===================== (1) 问题 =====================
ax = axes[0]
draw_drum(ax)
draw_launcher(ax)
draw_tray(ax, -150.0, C[0])
draw_shell(ax, A_ENTER_OLD, A_ENTER_OLD + 252.0, color=GREEN, lw=7)
draw_shell(ax, 66.0, A_EXIT, color=RED, lw=8.5)
ax.add_patch(Circle(on_arc(90.4, R_SHELL), 6.0, fc="none", ec=RED, lw=2.0, zorder=12))
lab_at(ax, on_arc(90.4, R_SHELL), (-205.0, 158.0), "球心线在 90.4° 处和外罩相交", RED, 10.0)

Ea = np.array(on_arc(A_EXIT))
v_ccw = np.array([-math.sin(math.radians(A_EXIT)), math.cos(math.radians(A_EXIT))])
draw_ball(ax, on_arc(A_EXIT), color=RED, lw=2.0)
arrow(ax, tuple(Ea), tuple(Ea + v_ccw * 85), color=RED, lw=3.4, ms=26, zorder=14)
arrow(ax, tuple(Ea), NIP, color=GREEN, lw=2.2, ms=20, zorder=13, ls=(0, (6, 4)))

lab_at(ax, tuple(Ea + v_ccw * 85), (-152.0, 60.0), "球飞出去的方向\n（左下，背对夹口）", RED, 10.5)
lab_at(ax, (Ea[0] * 0.5 + NIP[0] * 0.5, Ea[1] * 0.5 + NIP[1] * 0.5), (60.0, 168.0),
       "真正要走的方向", GREEN, 10.5)
lab_at(ax, on_arc(104.0, R_SHELL), (108.0, 30.0), "外罩 66°-142° 这段压在\n出口→夹口直线上（挡球）", RED, 10.5)
lab_at(ax, on_arc(300.0), (150.0, -30.0), "球其实是从这边绕过来的", GREEN, 10.5)
lab_at(ax, C, (108.0, 78.0), "拨杆：逆时针", PURPLE, 10.5)
ax.add_patch(FancyArrowPatch(on_arc(78.0, 74.0), on_arc(44.0, 74.0), connectionstyle="arc3,rad=0.32",
                             arrowstyle="-|>", mutation_scale=20, lw=2.6, color=PURPLE, zorder=10))

note(ax, "① 现状：外罩挡住了出口→夹口的直线，而且出口方向反了\n"
         "球贴外罩内壁走 252°（本图坐标：逆时针）到 142°，外罩到 142° 就结束 → 球沿切线飞出。\n"
         "但逆时针在 142° 的切向 = 左下（背离夹口）→ 球被甩回鼓内/托板，进不了发射部分。\n"
         "同时外罩 66°-142° 这一段正好从“出口→夹口”的直线上穿过去（球心线在 90.4° 处和外罩相交）——\n"
         "这就是你看到的挡路。\n"
         "结论：挡路是表面现象。要按 52° 进夹口，球必须在 142° 朝右上飞出，也就是本图坐标里\n"
         "【顺时针】走短路（见右图）。", (-200.0, 478.0), RED)

ax.set_title("① 现状：外罩长 252° + 出口反了 → 142° 速度朝左下，进不了夹口", fontsize=13.5, pad=10)

# ===================== (2) 修正 =====================
ax = axes[1]
draw_drum(ax, (233.0, 353.0, 113.0))
draw_launcher(ax)
draw_tray(ax, -150.0, C[0])
draw_shell(ax, A_ENTER_NEW, A_ENTER_NEW + 360.0 - (A_ENTER_NEW - A_EXIT), color=GRAY, lw=4, ls=(0, (6, 5)))
draw_shell(ax, A_EXIT, A_ENTER_NEW, color=GREEN, lw=7.5)

wp = wall_of(ramp)
ax.plot(wp[:, 0], wp[:, 1], color=GREEN, lw=6.0, solid_capstyle="round", zorder=6)
ax.plot(ramp[:, 0], ramp[:, 1], color=RED, lw=1.8, ls=(0, (7, 4)), zorder=7)
ax.add_patch(Circle(LIP_NEW, 4.5, fc=RED, ec="white", lw=1.0, zorder=10))

path_arrows(ax, ramp, [60, 150, 205], step=18)
path_arrows(ax, carry, [40, 110, 180, 250], step=16)
arrow(ax, tuple(E), NIP, color=RED, lw=2.4, ms=20)

draw_ball(ax, tuple(ramp[130]), color=GRAY, lw=1.3, ls=(0, (4, 3)))
draw_ball(ax, P_ENTER_NEW, color=RED, lw=1.9)
for a in (192.0, 168.0):
    draw_ball(ax, on_arc(a), color=GRAY, lw=1.2, ls=(0, (4, 3)))
draw_ball(ax, on_arc(A_EXIT), color=RED, lw=1.6, ls=(0, (5, 3)))

lab_at(ax, tuple(ramp[130]), (-200.0, 62.0), "导入斜坡（把球抬到 225°）", GREEN, 10.5)
lab_at(ax, LIP_NEW, (-150.0, -18.0), "外罩下端 ≈225°", RED, 10.0)
lab_at(ax, on_arc(180.0, R_SHELL), (-190.0, 150.0), "外罩只剩 142°-225°", GREEN, 10.5)
lab_at(ax, on_arc(110.0, R_SHELL), (-204.0, 268.0), "这段全部去掉\n（225°→142° 的长路，含挡路段）", DGRAY, 10.5)
lab_at(ax, on_arc(A_EXIT), (196.0, 118.0), "出口仍 142°，切向仍 52°", RED, 10.5, ha="right")
lab_at(ax, (-140.0, TRAY_TOP), (-200.0, -52.0), "托板（左侧送入）", BLUE, 10.5)

ax.add_patch(FancyArrowPatch(on_arc(192.0, 74.0), on_arc(162.0, 74.0), connectionstyle="arc3,rad=0.32",
                             arrowstyle="-|>", mutation_scale=20, lw=2.6, color=PURPLE, zorder=10))
lab_at(ax, on_arc(176.0, 74.0), (150.0, -20.0), "拨杆：本图顺时针\n（= 你前视的逆时针）", PURPLE, 10.5)

note(ax, "② 修正：外罩缩到 142°-225° + 球在 225° 就位 + 走短路（本图顺时针）\n"
         "外罩只做 142°-225°（83°），从 225° 经 90°、0° 再回到 142° 的那一大段全部去掉 →\n"
         "出口→夹口的直线完全空出来（核算：直线到外罩最小距离 35.56 mm = 球半径，刚好相切）。\n"
         "球由托板 → 导入斜坡抬到球心圆 225°（球心抬高 %.0f mm），拨杆从 225° 推到 142° 只需 83°。\n"
         "叶片相位跟着从 258° 挪到 233°（球在 225° 就位时叶片正好在球后）→ 行程 252° 缩到 83°。\n"
         "出口仍 142°、切向仍 52°、沿 52° 直线进夹口 → 发射段一根都不用动。"
         % (P_ENTER_NEW[1] - BALL_Z,), (-200.0, 478.0), GREEN)

ax.set_title("② 修正：外罩缩到 142°-225° + 球在 225° 就位（行程 252°→83°）", fontsize=13.5, pad=10)

for a in axes:
    a.set_aspect("equal")
    a.grid(alpha=0.22, lw=0.6)
    a.set_xlabel("X [mm]")
    a.set_ylabel("Z [mm]")
    a.set_xlim(-210, 210)
    a.set_ylim(-72, 480)

fig.suptitle("T06 POLLEN 送球段：出口方向问题与修正（X-Z 剖面，单位 mm）", fontsize=16)
fig.text(0.5, 0.022,
         "方向约定：本图 X 向右 / Z 向上，发射部分在拨杆右侧。你的前视（发射部分在拨杆左侧）是本图的镜像 → "
         "本图顺时针 = 前视逆时针，是同一个方向。",
         ha="center", fontsize=11.5, color="#333333")
path = OUT / "options_b_exit_fix_zh.png"
fig.savefig(path, dpi=120)
print("saved:", path)
