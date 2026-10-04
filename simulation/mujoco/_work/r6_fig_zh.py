# -*- coding: utf-8 -*-
"""T06 POLLEN V2 方案 R5 vs R6 剖面与实测对比图（25-4 Super Speed 电机模型驱动拨杆）"""
import json, math, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import r6_smooth as r6
import r6_motor as rm
import opt_lib as ol
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, Rectangle, Wedge
from matplotlib.lines import Line2D

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
pv2 = ol.pv2
C = (pv2.PADDLE_CX, pv2.PADDLE_CZ)
R_IN, R_OUT, BALL_R, R_CARRY = pv2.R_IN, pv2.R_OUT, pv2.BALL_R, pv2.R_CARRY
R6_A0, R6_A1 = 225.0, 260.2
PAD_X0, PAD_X1, PAD_TOP = -17.0, 13.0, pv2.tray_top_z(-2.0) + 6.8
PARK = (113.90, 63.29)
C_SHELL, C_SHELL_E = "#9fc6e0", "#2a6f97"
C_TRAY, C_TRAY_E = "#b9d8b0", "#3f7d3a"
C_PAD, C_PAD_E = "#c9a0dc", "#6a3d9a"
C_ARC, C_ARC_E = "#e07a5f", "#a33b20"
C_PADDLE, C_PADDLE_E = "#f2a65a", "#b5651d"
C_BALL, C_TRACK, C_GUIDE = "#e8c33a", "#8e44ad", "#b0b0b0"
OUT = Path("simulation/mujoco/out")


def fp(ang, r):
    a = math.radians(ang)
    return (C[0] + r * math.cos(a), C[1] + r * math.sin(a))


def arc_poly(a0, a1, r0=R_IN, r1=R_OUT, n=60, **kw):
    inn = [fp(a0 + (a1 - a0) * i / n, r0) for i in range(n + 1)]
    out = [fp(a0 + (a1 - a0) * i / n, r1) for i in range(n + 1)]
    poly = Polygon(inn + out[::-1], closed=True)
    if kw:
        poly.set(**kw)
    return poly


def finger(cx, cz, ang_deg, r0, r1, halfw):
    a = math.radians(ang_deg)
    ux, uz = math.cos(a), -math.sin(a)
    tx, tz = math.sin(a), math.cos(a)
    return Polygon([(cx + u * ux + v * tx, cz + u * uz + v * tz)
                    for (u, v) in ((r0, -halfw), (r1, -halfw), (r1, halfw), (r0, halfw))], closed=True)


def draw_fingers(ax, z=6, alpha=1.0):
    for ang in (10.0, 190.0):
        for (r0, r1, hw) in ((14, 46, 5), (46, 58, 15), (56, 60, 17)):
            p = finger(C[0], C[1], ang, r0, r1, hw)
            p.set(facecolor=C_PADDLE, edgecolor=C_PADDLE_E, lw=1.2, alpha=alpha, zorder=z)
            ax.add_patch(p)


def draw_common(ax, finger_z=6, finger_a=1.0):
    ax.add_patch(Wedge(C, R_OUT, 142, 225, width=R_OUT - R_IN,
                       facecolor=C_SHELL, edgecolor=C_SHELL_E, lw=1.4, zorder=4))
    for ang in (142.0, 225.0):
        p = pv2.polar(0.5 * (R_IN + R_OUT), ang)
        ax.add_patch(Rectangle((p[0] - R_OUT + R_IN, p[1] - 1.5), R_OUT - R_IN, 3.0, angle=-ang,
                               facecolor=C_SHELL, edgecolor=C_SHELL_E, lw=1.2, zorder=5))
    nx, nz = pv2.normal(-pv2.TILT)
    x0, x1 = pv2.TRAY_X0, pv2.TRAY_X1
    t0, t1 = (x0, pv2.tray_top_z(x0)), (x1, pv2.tray_top_z(x1))
    ax.add_patch(Polygon([t0, t1, (t1[0] - nx * pv2.TRAY_T, t1[1] - nz * pv2.TRAY_T),
                          (t0[0] - nx * pv2.TRAY_T, t0[1] - nz * pv2.TRAY_T)], closed=True,
                         facecolor=C_TRAY, edgecolor=C_TRAY_E, lw=1.3, zorder=4))
    sp = Polygon([(pv2.STRUT_X0, pv2.STRUT_Z0), (pv2.STRUT_X1, pv2.STRUT_Z0),
                  (pv2.STRUT_X1, pv2.STRUT_Z1), (pv2.STRUT_X0, pv2.STRUT_Z1)], closed=True)
    sp.set(facecolor=C_TRAY, edgecolor=C_TRAY_E, lw=1.2, zorder=4)
    ax.add_patch(sp)
    for (s, e, L, a) in pv2.SEGS:
        ax.plot([s[0], e[0]], [s[1], e[1]], color=C_GUIDE, lw=1.5, ls=(0, (6, 4)), zorder=2)
    th = [142.0 + (225.0 - 142.0) * i / 120.0 for i in range(121)]
    ax.plot([fp(t, R_CARRY)[0] for t in th], [fp(t, R_CARRY)[1] for t in th],
            color="#c0392b", lw=1.2, ls=(0, (5, 3)), zorder=5)
    draw_fingers(ax, z=finger_z, alpha=finger_a)
    ax.add_patch(Circle(C, 18.0, facecolor=C_PADDLE, edgecolor=C_PADDLE_E, lw=1.3, zorder=7))
    ax.plot(*C, marker="+", color="#333", ms=10, mew=1.6, zorder=8)


def setup(ax, xlim, zlim, title):
    ax.set_aspect("equal"); ax.set_xlim(*xlim); ax.set_ylim(*zlim)
    ax.set_title(title, fontsize=12, pad=8)
    ax.grid(True, color="#e6e6e6", lw=0.7); ax.set_axisbelow(True)
    for s in ax.spines.values():
        s.set_color("#bbb")
    ax.tick_params(labelsize=8, colors="#555")


print("running R5 / R6 with the 25-4 Super Speed motor model ...")
R5 = rm.run_motor("R5", bx=145.0, sec=12.0)
R6 = rm.run_motor("R6", bx=145.0, sec=12.0)
R6C = rm.run_motor("R6c", bx=145.0, sec=12.0)


def path(r, tmax=7.6):
    return [(s["x"], s["z"]) for s in r["_trace"] if 0.35 <= s["t"] <= tmax]


fig = plt.figure(figsize=(16.4, 11.6), dpi=130)
fig.suptitle("T06 POLLEN V2 送球段优化 —— 方案 R5（平垫块）vs 方案 R6（外罩与球窝垫用平滑弧面连接）", fontsize=16, y=0.986)
fig.text(0.5, 0.951, "剖面 = 拨杆轴心 XZ 平面；单位 mm；轨迹为 MuJoCo 实测球心路径；拨杆由 goBILDA 25-4 Super Speed（0.530 N·m / 290 rpm）线性扭矩—转速模型驱动",
         ha="center", fontsize=10, color="#666")
gs = fig.add_gridspec(2, 2, left=0.055, right=0.975, top=0.922, bottom=0.062, hspace=0.26, wspace=0.16)

# ---------------- (a) R5 ----------------
ax = fig.add_subplot(gs[0, 0])
draw_common(ax)
ax.add_patch(Rectangle((PAD_X0, PAD_TOP - 12.8), PAD_X1 - PAD_X0, 12.8,
                       facecolor=C_PAD, edgecolor=C_PAD_E, lw=1.4, zorder=5))
ax.plot(*zip(*path(R5)), color=C_TRACK, lw=2.2, alpha=0.9, zorder=9)
ax.add_patch(Circle(PARK, BALL_R, facecolor=C_BALL, edgecolor="#8a6d1a", lw=1.4, alpha=0.9, zorder=8))
ax.annotate("D 平垫块 顶面 z=24.33\n与托板之间有 6.8 mm 台阶",
            xy=(PAD_X1, PAD_TOP), xytext=(-124, 160), fontsize=9.4, color=C_PAD_E,
            bbox=dict(fc="white", ec=C_PAD_E, lw=0.7, alpha=0.93),
            arrowprops=dict(arrowstyle="->", color=C_PAD_E, lw=1.2), zorder=11)
ax.annotate("225° 直挡墙（保留）", xy=fp(225.0, 101.0), xytext=(-124, 118), fontsize=9.2,
            color=C_SHELL_E, arrowprops=dict(arrowstyle="->", color=C_SHELL_E, lw=1.2), zorder=11)
ax.annotate("停位球（拨杆停位时停在托板上，\n靠指片尖端挡住 → 等下一片来抓）",
            xy=(PARK[0] - BALL_R * 0.9, PARK[1] - BALL_R * 0.45), xytext=(6, 20), fontsize=9.0,
            color="#7a5c10", arrowprops=dict(arrowstyle="->", color="#7a5c10", lw=1.0), zorder=11)
ax.plot([], [], color=C_TRACK, lw=2.2, label="球心轨迹（实测）")
ax.legend(loc="upper right", fontsize=8.6, frameon=False)
setup(ax, (-128, 178), (-12, 205), "(a) R5：外罩止于 225°，另加一块 30×108×12.8 平垫块")
ax.text(0.985, 0.03, "抓球前蠕动 2.98 s ｜ 运载 3.72 s ｜ 全程 7.49 s\n运载段舵机 0.523 N·m @ 3.95 rpm",
        transform=ax.transAxes, ha="right", fontsize=9.2, color="#a33b20",
        bbox=dict(fc="#fff2ec", ec=C_ARC_E, lw=0.8, alpha=0.95))

# ---------------- (b) R6 ----------------
ax = fig.add_subplot(gs[0, 1])
draw_common(ax)
ax.add_patch(arc_poly(R6_A0, R6_A1, facecolor=C_ARC, edgecolor=C_ARC_E, lw=1.5, zorder=6))
ax.plot(*zip(*path(R6)), color=C_TRACK, lw=2.2, alpha=0.9, zorder=9)
ax.add_patch(Circle(PARK, BALL_R, facecolor=C_BALL, edgecolor="#8a6d1a", lw=1.4, alpha=0.9, zorder=8))
ax.annotate("R6 新增：外罩内弧 R93.96\n从 225° 平滑延伸 35.2°",
            xy=fp(243.0, 97.5), xytext=(-124, 160), fontsize=9.4, color=C_ARC_E,
            bbox=dict(fc="white", ec=C_ARC_E, lw=0.7, alpha=0.93),
            arrowprops=dict(arrowstyle="->", color=C_ARC_E, lw=1.2), zorder=11)
ax.annotate("终点落在托板顶面 x=13.5\n（该处抬升 0.0 mm，相切连续）",
            xy=fp(R6_A1, R_IN), xytext=(-124, -6), fontsize=9.2, color=C_ARC_E,
            bbox=dict(fc="white", ec=C_ARC_E, lw=0.7, alpha=0.93),
            arrowprops=dict(arrowstyle="->", color=C_ARC_E, lw=1.1), zorder=11)
ax.annotate("停位球：落入「托板 + 外罩延伸弧」形成的闭合球窝，\n下一片指片更早接触", xy=(PARK[0] - BALL_R * 0.9, PARK[1] - BALL_R * 0.45),
            xytext=(4, 20), fontsize=9.0, color="#7a5c10",
            bbox=dict(fc="white", ec="#7a5c10", lw=0.7, alpha=0.93),
            arrowprops=dict(arrowstyle="->", color="#7a5c10", lw=1.0), zorder=11)
ax.plot([], [], color=C_TRACK, lw=2.2, label="球心轨迹（实测）")
ax.legend(loc="upper right", fontsize=8.6, frameon=False)
setup(ax, (-128, 178), (-12, 205), "(b) R6：外罩内弧直接延伸到托板，取消平垫块")
ax.text(0.985, 0.03, "抓球前蠕动 2.93 s ｜ 运载 3.66 s ｜ 全程 7.38 s\n运载段舵机 0.523 N·m @ 4.05 rpm",
        transform=ax.transAxes, ha="right", fontsize=9.2, color="#2f6b2a",
        bbox=dict(fc="#eef7ec", ec="#2f6b2a", lw=0.9, alpha=0.95))

# ---------------- (c) junction zoom ----------------
ax = fig.add_subplot(gs[1, 0])
draw_common(ax, finger_z=3, finger_a=0.6)
ax.add_patch(Rectangle((PAD_X0, PAD_TOP - 12.8), PAD_X1 - PAD_X0, 12.8, facecolor=C_PAD,
                       edgecolor=C_PAD_E, lw=1.4, alpha=0.55, zorder=5))
ax.add_patch(arc_poly(R6_A0, R6_A1, facecolor=C_ARC, edgecolor=C_ARC_E, lw=1.6, zorder=6))
ax.plot(*zip(*path(R5)), color=C_TRACK, lw=2.0, alpha=0.85, zorder=9)
ax.plot(*zip(*path(R6)), color="#1f7a1f", lw=2.0, alpha=0.85, ls=(0, (5, 2)), zorder=9)
ax.add_patch(Circle((13.0, pv2.tray_top_z(13.0) + BALL_R), BALL_R, facecolor="none",
                    edgecolor=C_PAD_E, lw=1.6, ls=(0, (6, 3)), zorder=8))
ax.add_patch(Circle((fp(R6_A1, R_IN)[0], fp(R6_A1, R_IN)[1] + BALL_R), BALL_R, facecolor="none",
                    edgecolor=C_ARC_E, lw=1.6, ls=(0, (6, 3)), zorder=8))
ax.annotate("R5 硬台阶", xy=(13.0, PAD_TOP), xytext=(-54, 118),
            fontsize=9.4, color=C_PAD_E, ha="center",
            bbox=dict(fc="white", ec=C_PAD_E, lw=0.8, alpha=0.94),
            arrowprops=dict(arrowstyle="->", color=C_PAD_E, lw=1.2), zorder=12)
ax.annotate("R6 相切弧面", xy=(fp(R6_A1, R_IN)[0], fp(R6_A1, R_IN)[1]), xytext=(24, 132),
            fontsize=9.4, color=C_ARC_E, ha="center",
            bbox=dict(fc="white", ec=C_ARC_E, lw=0.8, alpha=0.94),
            arrowprops=dict(arrowstyle="->", color=C_ARC_E, lw=1.2), zorder=12)
ax.text(0.02, 0.045, "R5：球撞上 6.8 mm 立沿，被指片沿硬台阶「刮」上去\nR6：弧面与托板相切落地，球是「滚」上去的",
        transform=ax.transAxes, va="bottom", fontsize=9.2, color="#333", zorder=16,
        bbox=dict(fc="white", ec="#ccc", lw=0.8, alpha=0.95))
lg = [Line2D([], [], color=C_TRACK, lw=2.0, label="R5 球心轨迹"),
      Line2D([], [], color="#1f7a1f", lw=2.0, ls=(0, (5, 2)), label="R6 球心轨迹")]
ax.legend(handles=lg, loc="upper right", fontsize=8.8, frameon=False)
setup(ax, (-62, 56), (-4, 150), "(c) 球窝/托板接合处放大 —— 台阶 vs 连续弧面")

# ---------------- (d) results ----------------
ax = fig.add_subplot(gs[1, 1]); ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
ax.set_title("(d) 25-4 Super Speed 电机模型实测（球从 x=145 滚入，12 s 预算）", fontsize=12, pad=8)
cols = ["方案", "抓球前蠕动\ns", "运载\ns", "从放球到发射\ns", "运载段舵机\nN·m / rpm", "外罩—球窝接合"]
rows = [("R5", "2.98", "3.72", "7.49", "0.523 / 3.95", "台阶（平垫块）"),
        ("R6", "2.93", "3.66", "7.38", "0.523 / 4.05", "连续弧面（推荐）"),
        ("R6c", "2.99", "3.46", "7.23", "0.522 / 4.36", "弧面 + 半径 −2 mm")]
x0, dx = 0.055, 0.158
y0, dy = 0.865, 0.083
for j, c in enumerate(cols):
    ax.text(x0 + j * dx, y0 + 0.075, c, ha="center", va="center", fontsize=9.2,
            fontweight="bold", color="#333")
for i, row in enumerate(rows):
    yy = y0 - i * dy
    ax.add_patch(Rectangle((0.02, yy - 0.5 * dy + 0.006), 0.96, dy - 0.012,
                           facecolor="#f7f7f7" if i % 2 else "white", edgecolor="#e0e0e0", lw=0.6, zorder=0))
    for j, v in enumerate(row):
        ax.text(x0 + j * dx, yy, v, ha="center", va="center", fontsize=9.6 if j else 11,
                color="#2f6b2a" if i == 1 else "#333", fontweight="bold" if j == 0 else "normal", zorder=2)
ax.text(0.02, 0.505,
        "结论 1：R5 与 R6 全程相差很小——R6 快约 0.11 s（1.5%），R6c 快约 0.26 s（3.5%）。\n"
        "结论 2（回答本次问题）：把外罩与球窝垫连成平滑弧面不能消除「蠕动」，\n"
        "抓球前等待 2.98 s → 2.93 s，几乎没变；台阶不是蠕动的成因。\n"
        "结论 3（根因，实测）：蠕动出在球停稳后的 停位球窝——球停在 r≈83–95 mm、被指片\n"
        "楔住，把拨杆拖到 ~4 rpm；此时 25-4 输出 0.523 N·m，已贴近 0.530 N·m 堵转。\n"
        "改用 ±5 N·m 刚性速度源复测，该段拨杆仍只有 ~6.8 rpm、出力 ~1.16 N·m，\n"
        "说明这是卡滞而不是单纯扭矩不够。\n"
        "结论 4（建议）：治本要改 停位球窝几何（让球停在指片扫掠范围之外），或提高伺服\n"
        "扭矩；只优化外罩—球窝接合处的形状无效。",
        fontsize=8.4, color="#333", va="top", linespacing=1.5)
ax.text(0.02, 0.06,
        "R5/R6/R6c 均一次通过（launched=True），出口球速 6.67 m/s，飞轮 1620 rpm。\n"
        "抓球前蠕动 = 球停稳 → 拨杆把球推出停位的时间；「运载段舵机」列为 25-4 线性扭矩—转速模型实测。",
        fontsize=8.2, color="#777", va="top")

outs = OUT / "r5_vs_r6_smooth_zh.png"
fig.savefig(outs, facecolor="white")
print("saved", outs)
json.dump({"R5": {k: v for k, v in R5.items() if k != "_trace"},
           "R6": {k: v for k, v in R6.items() if k != "_trace"},
           "R6c": {k: v for k, v in R6C.items() if k != "_trace"}},
          open(OUT / "_r6_fig_data.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
