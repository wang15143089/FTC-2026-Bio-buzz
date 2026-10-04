# -*- coding: utf-8 -*-
"""T06 POLLEN 送球段：托板略向下倾斜（球自滚到位）+ 外罩与托板合并为 1 个零件。示意图，单位 mm。"""
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
from matplotlib.patches import Circle, Polygon, Wedge, FancyArrowPatch

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

OUT = Path(__file__).resolve().parent.parent / "out"

# ================= 基准（沿用已确认的送球段几何） =================
ANG = 52.0
T52 = (math.cos(math.radians(ANG)), math.sin(math.radians(ANG)))
N52 = (-math.sin(math.radians(ANG)), math.cos(math.radians(ANG)))
BALL_R = 35.56
R_CARRY = 58.4
R_SHELL = R_CARRY + BALL_R
C = (29.49, 111.46)
NIP = (52.31, 235.51)
A_EXIT, A_ENTRY = 142.0, 225.0
HUB_R, SWEEP_R = 18.0, 60.0
WHEEL_R, HALF = 48.0, 80.0
AX_A = (NIP[0] - HALF * math.sin(math.radians(ANG)), NIP[1] + HALF * math.cos(math.radians(ANG)))
AX_B = (NIP[0] + HALF * math.sin(math.radians(ANG)), NIP[1] - HALF * math.cos(math.radians(ANG)))

TILT = 5.0
PIVOT = (-2.30, 17.5)
WALL, PLATE = 7.0, 6.0
X_LEG, X_RIGHT = -56.0, 150.0

GREEN, RED, BLUE, ORANGE = "#1f7a3d", "#c00000", "#2b6a91", "#c8610f"
GRAY, PURPLE, DGRAY = "#9a9a9a", "#6b3fa0", "#666666"


def pol(a_deg, r, c=C):
    a = math.radians(a_deg)
    return (c[0] + r * math.cos(a), c[1] + r * math.sin(a))


def arcpts(a0, a1, r, c=C, n=360):
    a = np.radians(np.linspace(a0, a1, n))
    return np.stack([c[0] + r * np.cos(a), c[1] + r * np.sin(a)], axis=1)


LIP = np.array(pol(A_ENTRY, R_SHELL))
LIP_OUT = np.array(pol(A_ENTRY, R_SHELL + WALL))

tt = math.radians(TILT)
d = np.array([math.cos(tt), math.sin(tt)])
nrm = np.array([-math.sin(tt), math.cos(tt)])
P0 = np.array(PIVOT)


def tray_z(x):
    return float(P0[1] + (x - P0[0]) * math.tan(tt))


Avec = P0 + BALL_R * nrm - LIP
bq = 2.0 * float(Avec @ d)
cq = float(Avec @ Avec) - BALL_R ** 2
s_rest = (-bq + math.sqrt(bq * bq - 4.0 * cq)) / 2.0
P_REST = P0 + s_rest * d + BALL_R * nrm
P_FLAT = np.array([PIVOT[0], PIVOT[1] + BALL_R])
SHIFT = float(np.linalg.norm(P_REST - P_FLAT))
a_rest = math.degrees(math.atan2(P_REST[1] - C[1], P_REST[0] - C[0])) % 360.0

u = np.array([X_LEG, tray_z(X_LEG)]) - LIP_OUT
u = u / float(np.linalg.norm(u))
t_in = -(LIP[1] - tray_z(LIP[0])) / (u[1] - math.tan(tt) * u[0])
W_IN = LIP + t_in * u

Z_IN = float(tray_z(X_RIGHT) + BALL_R / math.cos(tt))
DROP = float(Z_IN - P_REST[1])
V_IN = math.sqrt(10.0 / 7.0 * 9.81 * (DROP / 1000.0))

inner = arcpts(A_ENTRY, A_EXIT, R_SHELL)
outer = arcpts(A_EXIT, A_ENTRY, R_SHELL + WALL)
xs = np.linspace(X_RIGHT, W_IN[0], 260)
traytop = np.stack([xs, [tray_z(x) for x in xs]], axis=1)
loop = [inner, outer,
        np.array([[X_LEG, tray_z(X_LEG)], [X_LEG, tray_z(X_LEG) - PLATE],
                  [X_RIGHT, tray_z(X_RIGHT) - PLATE], [X_RIGHT, tray_z(X_RIGHT)]]),
        traytop]
PART = np.vstack(loop)

print("lip(225deg)            = (%.2f, %.2f)" % tuple(LIP))
print("rest ball centre(tilt) = (%.2f, %.2f)  r=%.2f ang=%.2f" % (P_REST[0], P_REST[1], np.linalg.norm(P_REST - C), a_rest))
print("rest ball centre(flat) = (%.2f, %.2f)" % tuple(P_FLAT))
print("rest shift by tilt     = %.3f mm" % SHIFT)
print("web inner meets tray   = (%.2f, %.2f)" % tuple(W_IN))
print("entry ball centre z    = %.2f  (x=%d)   drop = %.2f mm  v_roll = %.2f m/s" % (Z_IN, X_RIGHT, DROP, V_IN))

env = arcpts(A_EXIT, a_rest, R_SHELL)
pts = np.vstack([env, PART])
WEB = np.array([LIP_OUT, [X_LEG, tray_z(X_LEG)]])
gi = 1e9
for seg_i in range(len(WEB) - 1):
    p1, p2 = WEB[seg_i], WEB[seg_i + 1]
    seg = p2 - p1
    L2 = float(seg @ seg)
    if L2 < 1e-9:
        continue
    for ang in np.radians(np.linspace(A_EXIT, a_rest, 400)):
        q = np.array([C[0] + R_SHELL * math.cos(ang), C[1] + R_SHELL * math.sin(ang)])
        t = float((q - p1) @ seg) / L2
        t = min(max(t, 0.0), 1.0)
        gi = min(gi, float(np.linalg.norm(q - (p1 + t * seg))))
print("min clearance web<->ball envelope = %.2f mm" % gi)
print("web r-range = %.2f .. %.2f" % (min(np.linalg.norm(WEB - C, axis=1)), max(np.linalg.norm(WEB - C, axis=1))))


def lab(ax, pt, xy, text, color, fs=10.0):
    ax.annotate(text, xy=tuple(pt), xytext=tuple(xy), fontsize=fs, color=color,
                ha="left", va="center", zorder=30,
                arrowprops=dict(arrowstyle="-", color=color, lw=0.9, shrinkA=0, shrinkB=2),
                bbox=dict(boxstyle="round,pad=0.26", fc="white", ec=color, lw=0.8, alpha=0.92))


def note(ax, text, xy, color, fs=10.2):
    ax.text(xy[0], xy[1], text, fontsize=fs, color="#222222", ha="left", va="top", zorder=40,
            bbox=dict(boxstyle="round,pad=0.5", fc="#fdfdfd", ec=color, lw=1.6, alpha=0.97))


def ball(ax, p, color=RED, lw=1.8, ls="-", zorder=9, r=BALL_R):
    ax.add_patch(Circle(tuple(p), r, fill=False, ec=color, lw=lw, ls=ls, zorder=zorder))
    ax.plot([p[0]], [p[1]], marker="+", ms=8, mew=1.6, color=color, zorder=zorder)


def launcher(ax):
    for s in (0.0, 110.0):
        p0 = (12.53 + s * N52[0], 95.27 + s * N52[1])
        p1 = (p0[0] + 135.0 * T52[0], p0[1] + 135.0 * T52[1])
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color="#8a8a8a", lw=2.4, zorder=2)
    for c in (AX_A, AX_B):
        ax.add_patch(Circle(c, WHEEL_R, fill=False, ec="#111111", lw=2.0, zorder=3))
        ax.plot([c[0]], [c[1]], marker="+", ms=10, mew=1.6, color="#111111", zorder=3)
    ax.add_patch(Circle(NIP, 5.0, fc=RED, ec="none", zorder=6))
    ax.annotate("夹口", NIP, textcoords="offset points", xytext=(14, 12), fontsize=10.5, color=RED, zorder=20)


def drum(ax):
    a = np.radians(np.linspace(0, 360, 360))
    ax.plot(C[0] + SWEEP_R * np.cos(a), C[1] + SWEEP_R * np.sin(a), color=ORANGE, lw=1.1, ls="--", alpha=0.7, zorder=2)
    for ph in (273.6, 153.6, 33.6):
        aa = math.radians(ph)
        ax.plot([C[0] + HUB_R * math.cos(aa), C[0] + SWEEP_R * math.cos(aa)],
                [C[1] + HUB_R * math.sin(aa), C[1] + SWEEP_R * math.sin(aa)],
                color=ORANGE, lw=5.5, solid_capstyle="round", zorder=3)
    ax.add_patch(Circle(C, HUB_R, fc="#f0c9a0", ec=ORANGE, lw=1.8, zorder=4))
    ax.plot([C[0]], [C[1]], marker="+", ms=11, mew=1.8, color=ORANGE, zorder=5)


fig = plt.figure(figsize=(24, 13.4))
gs = fig.add_gridspec(2, 2, width_ratios=[1.05, 1.0], hspace=0.19, wspace=0.13)
ax0 = fig.add_subplot(gs[:, 0])
ax1 = fig.add_subplot(gs[0, 1])
ax2 = fig.add_subplot(gs[1, 1])

# ---------------- (1) 整体 ----------------
launcher(ax0)
drum(ax0)
ax0.add_patch(Polygon(PART, closed=True, fc=GREEN, ec=GREEN, lw=2.0, alpha=0.30, zorder=5))
ax0.plot([PIVOT[0], X_RIGHT], [tray_z(PIVOT[0]), tray_z(X_RIGHT)], color=GREEN, lw=2.6, zorder=6)
ax0.plot([X_LEG, X_RIGHT], [tray_z(X_LEG) - PLATE, tray_z(X_RIGHT) - PLATE], color=GREEN, lw=2.6, zorder=6)
ball(ax0, P_REST, RED, 2.0)
ax0.add_patch(FancyArrowPatch((X_RIGHT + 55, tray_z(X_RIGHT) + 40), (X_RIGHT + 5, tray_z(X_RIGHT) + 12),
                              arrowstyle="-|>", mutation_scale=22, lw=3.0, color=BLUE, zorder=12))
ax0.text(X_RIGHT + 30, tray_z(X_RIGHT) + 62, "球从右侧进入", fontsize=12, color=BLUE, ha="center", zorder=20)

lab(ax0, tuple(LIP), (-150, 62), "唇口 225°：球自滚到此停住\n(球心 %.1f, %.1f)" % tuple(P_REST), GREEN, 10.5)
lab(ax0, (C[0], C[1]), (72, 128), "拨杆轴 (29.5, 111.5)\n= 外罩圆心（不变）", ORANGE, 10.5)
lab(ax0, tuple(W_IN), (10, -18), "斜筋：外罩 225° 端 → 托板左端\n与托板/外罩同为一体 → 1 个零件", GREEN, 10.5)
lab(ax0, (60, tray_z(60)), (60, -46), "托板向下倾斜 %.0f°（右高左低）\n球靠自重滚到停位" % TILT, BLUE, 10.5)

note(ax0, "① 本轮两处改动（都只在送球段，发射段一根都不动）\n"
          "1) 托板改为略向下倾斜 %.0f°（右端抬高）：球从右侧进入后靠自重滚到停位，\n"
          "   不需要额外的斜坡/推杆。倾斜基准取原停位的接触点 (-2.3, 17.5)，\n"
          "   所以球停位只挪 %.2f mm —— 现有轨迹实际不变。\n"
          "2) 外罩(142°–225°) 与托板合并成 1 个零件：外罩 225° 端 → 斜筋 → 托板左端，\n"
          "   一次成型/一件装配。外罩圆心仍落在拨杆轴上 → 托板倾斜不影响同轴度。"
     % (TILT, SHIFT), (-196, 470), GREEN, 10.4)

ax0.set_xlim(-215, 215)
ax0.set_ylim(-90, 480)
ax0.set_title("① 整体剖面：倾斜托板 + 外罩/托板合并为 1 个零件", fontsize=13.5, pad=10)

# ---------------- (2) 自滚细节 ----------------
drum(ax1)
ax1.add_patch(Polygon(PART, closed=True, fc=GREEN, ec=GREEN, lw=2.0, alpha=0.30, zorder=4))
ax1.plot([PIVOT[0], X_RIGHT], [tray_z(PIVOT[0]), tray_z(X_RIGHT)], color=GREEN, lw=2.4, zorder=6)
ax1.plot([-108, -60], [17.5, 17.5], color=GRAY, lw=2.2, ls=(0, (7, 5)), zorder=3)
ax1.text(-106, 25, "原平托板（参考，实做删除）", fontsize=9.6, color=GRAY, zorder=20)

for xw in (120.0, 70.0, 25.0):
    cw = np.array([xw, tray_z(xw)]) + BALL_R * nrm
    ball(ax1, cw, BLUE, 1.4, ls=(0, (5, 4)), zorder=7)
ax1.add_patch(FancyArrowPatch((152, 62), (118, 52), arrowstyle="-|>", mutation_scale=18, lw=2.4,
                              color=BLUE, zorder=12))
ax1.text(150, 70, "球从右侧滚入", fontsize=10.6, color=BLUE, ha="right", zorder=20)
ball(ax1, P_REST, RED, 2.2)
ax1.add_patch(Circle(tuple(LIP), 4.6, fc=GREEN, ec="white", lw=1.2, zorder=12))

ax1.annotate("", xy=(P0[0] + 70, P0[1]), xytext=(P0[0], P0[1]),
             arrowprops=dict(arrowstyle="-", color=DGRAY, lw=1.2, ls=":"), zorder=8)
aa = np.radians(np.linspace(0, TILT, 40))
ax1.plot(P0[0] + 46 * np.cos(aa), P0[1] + 46 * np.sin(aa), color=DGRAY, lw=1.6, zorder=8)
ax1.text(P0[0] + 52, P0[1] + 6, "%.0f°" % TILT, fontsize=11, color=DGRAY, zorder=20)

gl = np.array([-math.sin(tt), -math.cos(tt)]) * 34.0
ax1.add_patch(FancyArrowPatch((30, P_REST[1] + 46), (30 + gl[0] * 0.0 - 26, P_REST[1] + 46 - 22),
                              arrowstyle="-|>", mutation_scale=16, lw=2.0, color=PURPLE, zorder=12))
ax1.text(34, P_REST[1] + 50, "重力沿斜面分量 g·sin%.0f° = %.3f g\n（远大于滚动阻力 ~0.01–0.02）" % (TILT, math.sin(tt)),
         fontsize=10.2, color=PURPLE, zorder=20)

lab(ax1, tuple(P_REST), (-120, 122), "停位：球心 (%.1f, %.1f)\n到唇口恒 = 球半径 %.2f" % (P_REST[0], P_REST[1], BALL_R), RED, 10.3)
lab(ax1, tuple(LIP), (-120, 36), "唇口 225°（挡住球继续往左）", GREEN, 10.3)
lab(ax1, (120, tray_z(120) + BALL_R), (52, 134), "入口球心 z≈%.1f\n落差 %.1f mm → 落位≈%.2f m/s" % (Z_IN, DROP, V_IN), BLUE, 10.3)

note(ax1, "② 自滚进料\n"
          "· 托板倾角 %.0f°，入口(x=%d) 球心 z≈%.1f → 停位球心 z=%.1f，落差 %.1f mm\n"
          "· 停位仍由外罩 225° 唇口定位，与改动前是同一点（本图偏差仅 %.2f mm）\n"
          "· 落位速度约 %.2f m/s（纯滚动）→ 很轻，撞唇口基本不回弹\n"
          "· 灰色虚线 = 原平托板，仅作对比；实做按绿线倾斜板"
     % (TILT, X_RIGHT, Z_IN, P_REST[1], DROP, SHIFT, V_IN), (-120, -30), BLUE, 10.2)

ax1.set_xlim(-126, 176)
ax1.set_ylim(-98, 160)
ax1.set_title("② 进料细节：托板 %0.f° 自滚 + 唇口停位" % TILT, fontsize=13.5, pad=10)

# ---------------- (3) 合并件 + 干涉校核 ----------------
ax2.add_patch(Wedge(C, R_SHELL, A_EXIT, a_rest, width=BALL_R * 2.0,
                    fc="#fdecec", ec="none", zorder=2))
ax2.add_patch(Polygon(PART, closed=True, fc=GREEN, ec=GREEN, lw=2.0, alpha=0.28, zorder=4))
ax2.plot([PIVOT[0], X_RIGHT], [tray_z(PIVOT[0]), tray_z(X_RIGHT)], color=GREEN, lw=2.6, zorder=6)
ax2.plot([X_LEG, X_RIGHT], [tray_z(X_LEG) - PLATE, tray_z(X_RIGHT) - PLATE], color=GREEN, lw=2.6, zorder=6)
ea = np.radians(np.linspace(A_EXIT, a_rest, 300))
ax2.plot(C[0] + R_CARRY * np.cos(ea), C[1] + R_CARRY * np.sin(ea), color=RED, lw=1.5, ls=":", zorder=7)
ax2.plot(C[0] + R_SHELL * np.cos(ea), C[1] + R_SHELL * np.sin(ea), color=GREEN, lw=1.6, zorder=7)
ax2.add_patch(Circle(C, HUB_R, fc="#f0c9a0", ec=ORANGE, lw=1.6, zorder=6))
for ph in (273.6, 153.6, 33.6):
    aa = math.radians(ph)
    ax2.plot([C[0] + HUB_R * math.cos(aa), C[0] + SWEEP_R * math.cos(aa)],
             [C[1] + HUB_R * math.sin(aa), C[1] + SWEEP_R * math.sin(aa)],
             color=ORANGE, lw=5.0, solid_capstyle="round", zorder=5)
ball(ax2, P_REST, RED, 2.0)
for ph in (225.0, 200.0, 175.0, 150.0):
    ball(ax2, np.array(pol(ph, R_CARRY)), GRAY, 1.3, ls=(0, (5, 4)), zorder=7)
ax2.add_patch(Circle(tuple(LIP), 4.6, fc=GREEN, ec="white", lw=1.2, zorder=12))

ax2.annotate("", xy=(W_IN[0], W_IN[1]), xytext=(LIP_OUT[0], LIP_OUT[1]),
             arrowprops=dict(arrowstyle="<|-|>", color=PURPLE, lw=1.8), zorder=13)
ax2.text(-120, -34,
         "斜筋（与外罩同厚 %.0f）\n到球外缘 %.1f mm" % (WALL, gi), fontsize=10.2, color=PURPLE, zorder=20)

lab(ax2, tuple(pol(178.0, R_SHELL)), (-120, 142), "外罩内壁 R=%.2f" % R_SHELL, GREEN, 10.3)
lab(ax2, tuple(pol(163.0, R_CARRY)), (-120, 102), "球心轨迹 R=%.1f" % R_CARRY, RED, 10.3)
lab(ax2, tuple(P_REST), (-86, -6), "停位球", RED, 10.3)
lab(ax2, (60, tray_z(60) - PLATE), (34, -20), "倾斜托板（同 1 个零件）", BLUE, 10.3)

note(ax2, "③ 合并件校核：斜筋不挡球\n"
          "· 球被拨杆托着走时，球心在 R=%.1f 上，球外缘正好贴外罩内壁 R=%.2f\n"
          "· 斜筋整条都在 R≥%.0f 的外侧 → 到球外缘最小间隙 %.1f mm（红色扇形=球的扫掠范围）\n"
          "· 唇口 225° 仍然保留在斜筋顶端 → 球照样能绕这条边翻上去\n"
          "· 结论：合并成一个零件不改变送球轨迹，只减少零件数与装配次数"
     % (R_CARRY, R_SHELL, R_SHELL + WALL, gi), (44, 192), GREEN, 10.2)

ax2.set_xlim(-126, 180)
ax2.set_ylim(-62, 200)
ax2.set_title("③ 合并件 + 干涉校核（外罩 + 斜筋 + 托板 = 1 件）", fontsize=13.5, pad=10)

for a in (ax0, ax1, ax2):
    a.set_aspect("equal")
    a.grid(alpha=0.22, lw=0.6)
    a.set_xlabel("X [mm]")
    a.set_ylabel("Z [mm]")

fig.suptitle("T06 POLLEN 送球段：托板略向下倾斜（自滚到位）+ 外罩与托板合并为 1 个零件（X-Z 剖面，单位 mm）", fontsize=16)
fig.text(0.5, 0.018,
         "左右约定：按本图坐标 —— X 正方向为“右”、Z 向上；发射部分（两飞轮 + 夹口）在图上右侧。"
         "示意用，尺寸可放宽到 ±1 mm；倾角 %.0f° 可调（建议 3–7°）。" % TILT,
         ha="center", fontsize=11.5, color="#333333")
path = OUT / "options_c_tilted_merged_zh.png"
fig.savefig(path, dpi=126)
print("saved:", path)