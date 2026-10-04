# -*- coding: utf-8 -*-
"""T06 POLLEN 送球段 V2（重做）剖面示意图，单位 mm。"""
from __future__ import annotations
import math, sys
from pathlib import Path
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, Wedge
from matplotlib.lines import Line2D

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
OUT = Path(__file__).resolve().parent.parent / "out"

ANG = 52.0
T52 = np.array([math.cos(math.radians(ANG)), math.sin(math.radians(ANG))])
N52 = np.array([-math.sin(math.radians(ANG)), math.cos(math.radians(ANG))])
BALL_R = 35.56
C = np.array([29.49, 111.46])
R_CARRY, WALL, SWEEP_R, HUB_R = 58.4, 7.0, 60.0, 18.0
R_IN, R_OUT = R_CARRY + BALL_R, R_CARRY + BALL_R + WALL
A_LIP, A_EXIT = 225.0, 142.0
G0 = np.array([-30.56632745354581, 40.11041307339926])
TILT, PIVOT = 5.0, np.array([-2.30, 17.50])
TRAY_T, X0, X1 = 6.0, -56.0, 150.0
NIP = np.array([52.31, 235.51]); WHEEL_R, HALF = 48.0, 80.0
FINGER = np.array([-14.57, 65.11])
BLUE, DKBLUE, ORANGE, GREEN = "#8cbde8", "#1c4c78", "#d98b1f", "#1f7a3d"
RED, PURPLE, GRAY = "#c00000", "#6b3fa0", "#8f8f8f"
BOX = dict(fc="white", ec="#b0b0b0", alpha=0.95, lw=0.9, boxstyle="round,pad=0.35")

def tz(x): return PIVOT[1] + (x - PIVOT[0]) * math.tan(math.radians(TILT))
def pol(a, r, c=C):
    a = math.radians(a); return np.array([c[0] + r * math.cos(a), c[1] + r * math.sin(a)])
def arcpts(a0, a1, r, n=400):
    a = np.radians(np.linspace(a0, a1, n))
    return np.stack([C[0] + r * np.cos(a), C[1] + r * np.sin(a)], axis=1)
def ramp_pt(t, perp): return G0 + t * T52 + perp * N52
REST = np.array([PIVOT[0], tz(PIVOT[0]) + BALL_R])
LIP = pol(A_LIP, R_IN); EXIT_BALL = pol(A_EXIT, R_CARRY)
T_C, P_C = (C - G0) @ T52, (C - G0) @ N52

def ball(ax, p, **kw): ax.add_patch(Circle(tuple(p), BALL_R, **kw))
def shell(ax, a=0.9, lw=1.7):
    ax.add_patch(Wedge(tuple(C), R_OUT, A_EXIT, A_LIP, width=WALL, fc=BLUE, ec=DKBLUE, lw=lw, alpha=a, zorder=3))
def tray(ax, a=0.9, lw=1.7):
    pts = [(X0, tz(X0) - TRAY_T), (X1, tz(X1) - TRAY_T), (X1, tz(X1)), (LIP[0] + 5.0, tz(LIP[0] + 5.0))]
    ax.add_patch(Polygon(pts, closed=True, fc=BLUE, ec=DKBLUE, lw=lw, alpha=a, zorder=3))
    ax.annotate("", xy=(LIP[0], LIP[1]), xytext=(LIP[0], tz(LIP[0])),
                arrowprops=dict(arrowstyle="-", color=DKBLUE, lw=lw), zorder=4)
def paddle(ax, flex=True):
    ax.add_patch(Circle(tuple(C), HUB_R, fc="#b9bec6", ec="#5a6069", lw=1.0, zorder=6))
    for a in (18.0, 138.0, 258.0):
        th = math.radians(a); u = np.array([math.cos(th), math.sin(th)]); n = np.array([-math.sin(th), math.cos(th)])
        segs = [(14.0, 46.0, 5.0, ORANGE), (46.0, 58.0, 15.0, ORANGE)]
        if flex: segs.append((56.0, 60.0, 17.0, "#f0b429"))
        for (r0, r1, hw, c) in segs:
            pts = [C + r0*u + hw*n, C + r1*u + hw*n, C + r1*u - hw*n, C + r0*u - hw*n]
            ax.add_patch(Polygon(pts, closed=True, fc=c, ec="#7a4a08", lw=0.7, zorder=6))
    ax.add_patch(Circle(tuple(C), SWEEP_R, fill=False, ec=ORANGE, lw=1.1, ls=(0, (6, 3)), zorder=5))
def head(fig, title, sub, top=0.90):
    fig.subplots_adjust(top=top)
    fig.text(0.030, 0.965, title, fontsize=14.5, weight="bold", va="center")
    fig.text(0.030, 0.928, sub, fontsize=10.5, color="#444", va="center")
def arrow(ax, xy, xytext, color="#222", fs=10.5, **kw):
    return ax.annotate(xytext, xy=tuple(xy), xytext=xytext, fontsize=fs, color=color,
                       arrowprops=dict(arrowstyle="->", color=color, lw=1.3, shrinkA=2, shrinkB=4), **kw)

# ============================================ 图 1 总体剖面
def fig_overview():
    fig, ax = plt.subplots(figsize=(16.0, 10.8))
    ax.set_xlim(-195, 270); ax.set_ylim(-40, 350); ax.set_aspect("equal")
    shell(ax); tray(ax)
    for (t0, t1, perp, ls, lw) in ((0.0, 70.0, 0.0, (0, (7, 4)), 1.4), (0.0, 70.0, 110.0, "-", 2.0),
                                   (70.0, 153.0, 110.0, "--", 2.0)):
        p0, p1 = ramp_pt(t0, perp), ramp_pt(t1, perp)
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]], ls=ls, color=DKBLUE, lw=lw, zorder=3)
    ax.plot(*np.stack([ramp_pt(0, 55), ramp_pt(205, 55)]).T, color=DKBLUE, lw=0.8, ls=":", zorder=2)
    for s in (-1, 1):
        c = NIP + s * HALF * N52
        ax.add_patch(Circle(tuple(c), WHEEL_R, fc="#4a4f57", ec="#20242a", lw=1.4, zorder=6))
        ax.plot([c[0]], [c[1]], "+", color="w", ms=10, zorder=7)
    ax.plot([NIP[0]], [NIP[1]], "x", color=RED, ms=11, mew=2.4, zorder=8)
    for a, al in ((225.0, 0.95), (195.0, 0.45), (168.0, 0.45), (142.0, 0.95)):
        ball(ax, pol(a, R_CARRY), fc="#ffe9a8", ec="#b8860b", lw=1.3, alpha=al, zorder=5)
    for t, al in ((93.2, 0.75), (135.0, 0.4), (180.0, 0.4), (205.0, 0.75)):
        ball(ax, ramp_pt(t, 55.0), fc="#ffe9a8", ec="#b8860b", lw=1.2, alpha=al, zorder=5)
    ball(ax, REST, fc="#ffe9a8", ec=RED, lw=2.2, zorder=7)
    paddle(ax)
    ax.plot([C[0]], [C[1]], "+", color="#111", ms=15, mew=2.6, zorder=9)
    ax.add_patch(Circle(tuple(C), 3.2, fc="#111", ec="none", zorder=9))
    ax.annotate("", xy=tuple(pol(190, R_CARRY + 30)), xytext=tuple(pol(228, R_CARRY + 30)),
                arrowprops=dict(arrowstyle="->", color=RED, lw=2.2, connectionstyle="arc3,rad=-0.35"), zorder=9)
    ax.text(-192, 342, "设计要点\n"
        "① 拨杆轴 C(29.49, 111.46) = 外罩圆心 → 同轴是构造事实\n"
        "② 外罩内壁 R93.96 = 球道，球心轨迹 R58.40\n"
        "③ 出口 142° 球心距 52° 地板线 55.00 mm（通道中线，偏差 0.002）\n"
        "④ 停位球心 (-2.30, 53.06)：球楔在 225° 唇口，靠重力自锁\n"
        "⑤ 拨杆推球 99°；托板 5°，自滚落差 18.0 mm\n"
        "⑥ 52° 地板已删（新拨杆扫掠必打穿它），roof / 侧壁保持父文件位置",
        fontsize=10.5, va="top", ha="left", zorder=12,
        bbox=dict(fc="white", ec="#b0b0b0", alpha=1.0, lw=0.9))
    arrow(ax, C + np.array([-6, -8]), (-192, 268), fs=10.5, color="#111", zorder=11)
    ax.text(-192, 262, "拨杆轴 = 外罩圆心", fontsize=10.5, va="top", zorder=12, bbox=BOX)
    arrow(ax, REST, (-192, 34), color=RED, zorder=11)
    ax.text(-192, 28, "停位（楔在唇口）", fontsize=10.5, color=RED, va="top", zorder=12, bbox=BOX)
    arrow(ax, pol(184, R_IN), (-192, 128), color=DKBLUE, zorder=11)
    ax.text(-192, 122, "外罩 + 倾斜托板\n（合成单一零件）", fontsize=10.5, color=DKBLUE, va="top", zorder=12, bbox=BOX)
    arrow(ax, EXIT_BALL, (178, 300), color=RED, zorder=11)
    ax.text(178, 296, "出口 142°：球心落在\n52° 通道中线上", fontsize=10.5, color=RED, va="top", zorder=12, bbox=BOX)
    arrow(ax, pol(190, R_CARRY + 32), (178, 175), color=RED, zorder=11)
    ax.text(178, 171, "拨杆推球 99°（沿外罩内壁）", fontsize=10.5, color=RED, va="top", zorder=12, bbox=BOX)
    arrow(ax, NIP, (178, 105), color=RED, zorder=11)
    ax.text(178, 101, "两飞轮对向旋转\n夹口 NIP(52.31, 235.51)", fontsize=10.5, color=RED, va="top", zorder=12, bbox=BOX)
    arrow(ax, ramp_pt(120, 110), (178, 40), color=DKBLUE, zorder=11)
    ax.text(178, 36, "52° 通道 / 喉道\n（父文件位置，不动）", fontsize=10.5, color=DKBLUE, va="top", zorder=12, bbox=BOX)
    _lg = ax.legend(handles=[Line2D([], [], color=ORANGE, lw=8, label="拨杆（3 叶，含 zip-tie 软尖）"),
                       Line2D([], [], color=BLUE, lw=8, label="外罩 + 倾斜托板（合一零件）"),
                       Line2D([], [], color=DKBLUE, lw=2, label="52° 通道 / 喉道（不动）"),
                       Line2D([], [], marker="o", color="none", markerfacecolor="#ffe9a8",
                              markeredgecolor="#b8860b", ms=13, label="球的运动路径（示意）")],
              loc="lower right", fontsize=10.5, framealpha=1.0)
    _lg.set_zorder(12)
    head(fig, "T06 POLLEN 送球段 V2（重做）总体剖面   y = 0",
         "拨杆轴 = 外罩圆心；外罩与 5° 倾斜托板合并为单一零件；发射段位置完全不动")
    ax.grid(alpha=0.18); ax.set_xlabel("X (mm)"); ax.set_ylabel("Z (mm)")
    fig.savefig(OUT / "redesign_v2_overview_zh.png", dpi=125); plt.close(fig)

# ============================================ 图 2 进料 / 止回
def fig_feed():
    fig, ax = plt.subplots(figsize=(16.0, 7.8))
    ax.set_xlim(-135, 215); ax.set_ylim(-45, 185); ax.set_aspect("equal")
    shell(ax); tray(ax)
    ax.plot([X0, X1], [PIVOT[1], PIVOT[1]], color=GRAY, lw=1.0, ls="--", zorder=2)
    for x, al in ((140.0, 0.35), (100.0, 0.45), (55.0, 0.6), (18.0, 0.8)):
        p = np.array([x, tz(x) + BALL_R]); ball(ax, p, fc="#ffe9a8", ec="#b8860b", lw=1.2, alpha=al, zorder=5)
        ax.annotate("", xy=(x - 30, tz(x - 30) + BALL_R), xytext=(x + 6, tz(x + 6) + BALL_R),
                    arrowprops=dict(arrowstyle="->", color=ORANGE, lw=1.6), zorder=6)
    ball(ax, REST, fc="#ffe9a8", ec=RED, lw=2.4, zorder=7)
    n1 = (REST - LIP) / np.linalg.norm(REST - LIP)
    ax.annotate("", xy=tuple(LIP + 2 * n1), xytext=tuple(LIP - 34 * n1),
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.8), zorder=8)
    n2 = np.array([math.sin(math.radians(TILT)), -math.cos(math.radians(TILT))])
    ax.annotate("", xy=tuple(REST + BALL_R * n2), xytext=tuple(REST + (BALL_R + 38) * n2),
                arrowprops=dict(arrowstyle="->", color=GREEN, lw=1.8), zorder=8)
    p_in = np.array([X1, tz(X1) + BALL_R])
    ax.annotate("", xy=(X1, PIVOT[1] + BALL_R), xytext=tuple(p_in),
                arrowprops=dict(arrowstyle="<->", color=PURPLE, lw=1.6))
    ax.annotate("", xy=(75, tz(75)), xytext=(75, PIVOT[1]),
                arrowprops=dict(arrowstyle="<->", color=GREEN, lw=1.6))
    ax.plot(*FINGER, "x", color=RED, ms=18, mew=3.8, zorder=10)
    arrow(ax, REST + np.array([-18, 24]), (-128, 168), color="#111")
    ax.text(-128, 163, "停位：球同时压住唇口和托板\n球心到唇口 35.57 mm = 球半径 → 楔紧自锁",
            fontsize=10.5, va="top", bbox=BOX)
    arrow(ax, LIP - 26 * n1, (-128, 108), color=RED)
    ax.text(-128, 103, "唇口法向反力", fontsize=10.5, color=RED, va="top", bbox=BOX)
    arrow(ax, REST + (BALL_R + 30) * n2, (-28, 148), color=GREEN)
    ax.text(-28, 143, "托板支撑", fontsize=10.5, color=GREEN, va="top", bbox=BOX)
    arrow(ax, p_in, (108, 150), color=PURPLE)
    ax.text(108, 145, "入口 → 停位落差 13.33 mm\n落位速度 ≈ 0.43 m/s（不会弹飞）",
            fontsize=10.5, color=PURPLE, va="top", bbox=BOX)
    arrow(ax, (75, tz(75) - 6), (20, -18), color=GREEN)
    ax.text(20, -22, "5° 自滚 206 mm，落差 18.0 mm", fontsize=10.5, color=GREEN, va="top", bbox=BOX)
    arrow(ax, FINGER + np.array([0, -6]), (-128, 20), color=RED)
    ax.text(-128, 15, "旧止回指位置\n球心距仅 17.2 mm（< 球半径）→ 必须删除\n止回改由 5° 托板自锁承担",
            fontsize=10.5, color=RED, va="top", bbox=BOX)
    head(fig, "进料与止回：5° 倾斜托板自滚 + 唇口楔紧（无需止回指）",
         "球从右侧滚入 → 沿 5° 托板自滚 206 mm → 楔死在 225° 唇口等拨杆")
    ax.grid(alpha=0.18); ax.set_xlabel("X (mm)"); ax.set_ylabel("Z (mm)")
    fig.savefig(OUT / "redesign_v2_feed_zh.png", dpi=125); plt.close(fig)

# ============================================ 图 3 同轴 / 配合
def fig_coax():
    fig, ax = plt.subplots(figsize=(14.0, 11.0))
    ax.set_xlim(-105, 115); ax.set_ylim(-55, 235); ax.set_aspect("equal")
    shell(ax, a=1.0, lw=1.9); tray(ax, a=1.0, lw=1.9)
    for r, ls in ((R_IN, ":"), (R_OUT, ":")):
        a = arcpts(A_EXIT, A_LIP, r); ax.plot(a[:, 0], a[:, 1], color=DKBLUE, lw=0.9, ls=ls, zorder=2)
    a = arcpts(A_EXIT, A_LIP, R_CARRY); ax.plot(a[:, 0], a[:, 1], color=GREEN, lw=1.2, ls=(0, (5, 3)), zorder=4)
    paddle(ax, flex=False)
    ball(ax, pol(A_LIP, R_CARRY), fc="none", ec="#b8860b", lw=1.6, ls="--", zorder=8)
    ball(ax, EXIT_BALL, fc="none", ec=RED, lw=1.6, ls="--", zorder=8)
    ball(ax, REST, fc="none", ec=RED, lw=1.4, ls=(0, (4, 2)), alpha=0.85, zorder=7)
    for perp, ls, lw in ((0.0, (0, (7, 4)), 1.4), (110.0, "-", 2.2)):
        p0, p1 = ramp_pt(-25, perp), ramp_pt(65, perp)
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]], ls=ls, color=DKBLUE, lw=lw, zorder=3)
    ax.plot(*np.stack([ramp_pt(-25, 55), ramp_pt(65, 55)]).T, color=DKBLUE, lw=0.9, ls=":", zorder=2)
    ax.plot([C[0]], [C[1]], "+", color="#111", ms=17, mew=3.2, zorder=9)
    ax.add_patch(Circle(tuple(C), 3.6, fc="#111", ec="none", zorder=9))
    for a in (A_LIP, A_EXIT):
        ax.annotate("", xy=tuple(C), xytext=tuple(pol(a, R_IN)),
                    arrowprops=dict(arrowstyle="<->", color=DKBLUE, lw=1.4), zorder=8)
    ax.annotate("", xy=tuple(C), xytext=tuple(C - P_C * N52),
                arrowprops=dict(arrowstyle="<->", color=PURPLE, lw=1.6), zorder=8)
    ax.annotate("", xy=tuple(ramp_pt(T_C, 0)), xytext=tuple(ramp_pt(T_C, 55)),
                arrowprops=dict(arrowstyle="<->", color=RED, lw=1.8), zorder=8)
    ax.text(*(C + np.array([9, 9])), "C(29.49, 111.46) = 拨杆轴 = 外罩圆心",
            fontsize=11, bbox=BOX, zorder=10)
    ax.text(*(pol(A_LIP, R_OUT + 10) + np.array([-6, -2])), "唇口 225°", fontsize=10.5, color=DKBLUE, ha="center")
    ax.text(*(pol(A_EXIT, R_OUT + 12) + np.array([6, 6])), "出口 142°", fontsize=10.5, color=DKBLUE, ha="center")
    ax.text(*pol(A_LIP, R_IN / 2 + 6), "R93.96", color=DKBLUE, fontsize=10.5, ha="center", zorder=10)
    ax.text(*pol(A_EXIT, R_IN / 2 + 6), "R93.96", color=DKBLUE, fontsize=10.5, ha="center", zorder=10)
    ax.text(*(C - P_C * N52 / 2 + np.array([-74, 4])), "轴到斜坡地板线\n3.40 mm", color=PURPLE, fontsize=10.5, bbox=BOX)
    ax.text(*(ramp_pt(T_C, 27) + np.array([-40, 0])), "55.00\n(通道中线)", color=RED, fontsize=10.5, bbox=BOX)
    arrow(ax, pol(196, R_CARRY), (-102, 222), color=GREEN)
    ax.text(-102, 217, "球心轨迹 R58.40", fontsize=10.5, color=GREEN, va="top", bbox=BOX)
    arrow(ax, LIP + np.array([2, 0]), (-102, -22), color=ORANGE)
    ax.text(-102, -27, "托板与外罩在唇口连成一体\n（单个零件，连接筋 5 mm 宽）",
            fontsize=10.5, color=ORANGE, va="top", bbox=BOX)
    arrow(ax, EXIT_BALL, (46, 34), color=RED)
    ax.text(46, 29, "出口球心距 52° 地板 55.00 mm\n落在通道中线上（偏差 0.002 mm）",
            fontsize=10.5, color=RED, va="top", bbox=BOX)
    arrow(ax, (LIP[0] + 2.5, (LIP[1] + tz(LIP[0])) / 2), (46, 175), color="#111")
    ax.text(46, 170, "外罩圆弧以拨杆轴为圆心\n直接画出 → 同轴不靠公差",
            fontsize=10.5, va="top", bbox=BOX)
    head(fig, "同轴度与配合校核：拨杆 / 外罩 / 托板",
         "外罩圆弧以拨杆轴为圆心构造 → 同轴是构造事实；出口球心正好落在 52° 通道中线上")
    ax.grid(alpha=0.18); ax.set_xlabel("X (mm)"); ax.set_ylabel("Z (mm)")
    fig.savefig(OUT / "redesign_v2_coax_zh.png", dpi=125); plt.close(fig)

if __name__ == "__main__":
    fig_overview(); fig_feed(); fig_coax(); print("figures done")
