"""T06 POLLEN 发射器 送球段改型 —— 设计评审剖面图.

左图 = 现状（三段平板导槽 + 顶板逐段平移 110mm），
右图 = 改后（绕拨杆轴的连续曲面通道 + 拨杆移到发射线法向 58.4mm 外）。
不修改任何原有 CAD 文件，只出图。
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
from matplotlib.patches import Circle, Rectangle

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

OUT = Path(__file__).resolve().parent.parent / "out"
OUT.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------
# 与 CAD / 仿真脚本完全一致的几何公式 (单位 mm)
# --------------------------------------------------------------------------
ANGLE = 52.0


def direction(a):
    r = math.radians(a)
    return math.cos(r), math.sin(r)


def normal(a):
    r = math.radians(a)
    return -math.sin(r), math.cos(r)


T52, N52 = direction(ANGLE), normal(ANGLE)
GUIDE_SPEC = [((-150.0, 16.0), 70.0, 0.0), (None, 55.0, 26.0), (None, 70.0, ANGLE)]


def guide_segments():
    out, start = [], GUIDE_SPEC[0][0]
    for _, length, angle in GUIDE_SPEC:
        tx, tz = direction(angle)
        end = (start[0] + length * tx, start[1] + length * tz)
        out.append((start, end, angle))
        start = end
    return out


GUIDES = guide_segments()
GUIDE_END = GUIDES[-1][1]
THROAT = (GUIDE_END[0] + 55.0 * N52[0], GUIDE_END[1] + 55.0 * N52[1])
NIP = (THROAT[0] + 135.0 * T52[0], THROAT[1] + 135.0 * T52[1])

BALL_D = 71.12
BALL_R = BALL_D / 2.0
HUB_R = 18.0
SWEEP = 60.0
FLOOR_TOP = 17.5
BALL_Z = FLOOR_TOP + BALL_R          # 球在托板上的球心高度 = 53.06
C_OLD = (-47.0, 73.0)
WHEEL_R = 48.0
AXLE = {}

# --------------------------------------------------------------------------
# 改后：拨杆轴 C_new，使 (a) 外罩最低点与托板相切，(b) 球心线到发射线最近 58.4
# --------------------------------------------------------------------------
R_CARRY = 58.4                        # 球心绕拨杆轴的半径 = 喉道中心半径
R_SHELL = R_CARRY + BALL_R            # 外罩半径 93.96
CZ = FLOOR_TOP + R_SHELL
CX = NIP[0] + (-R_CARRY - (CZ - NIP[1]) * N52[1]) / N52[0]
C_NEW = (CX, CZ)
TANGENT = (CX + R_CARRY * N52[0], CZ + R_CARRY * N52[1])
A_ENTRY, A_EXIT = 270.0, 142.0        # 球心绕拨杆轴的角度：底部 -> 切点


def on_arc(a_deg, r=R_CARRY, c=C_NEW):
    a = math.radians(a_deg)
    return (c[0] + r * math.cos(a), c[1] + r * math.sin(a))


def ball_path_pts(n=400):
    pts = [(-150.0, BALL_Z)]
    pts += [on_arc(a) for a in np.linspace(A_ENTRY, A_EXIT, n)]
    pts += [NIP]
    return np.array(pts, float)


def path_normals(pts):
    t = np.gradient(pts, axis=0)
    t /= np.linalg.norm(t, axis=1, keepdims=True)
    return np.stack([-t[:, 1], t[:, 0]], axis=1)


# --------------------------------------------------------------------------
# 绘图工具
# --------------------------------------------------------------------------
def draw_wheels(ax):
    for sign in (1, -1):
        c = (NIP[0] + (-1) * sign * 63.0 * 0 + 0, 0)
    axles = [(NIP[0] + 63.0 * N52[1] * 0 - 63.0 * math.sin(math.radians(ANGLE)) * 0, 0)]
    axles = [(NIP[0] - 63.0 * math.sin(math.radians(ANGLE)) * -1 * 0, 0)]
    # 两个飞轮轴心 = nip 沿法向 ±80（等效于下面两式）
    a1 = (NIP[0] - 63.06 * 1.0, 0)
    axles = [(NIP[0] + (-N52[0]) * 0, 0)]
    # 直接按 CAD: 轴心 = SHOOTER_ORIGIN + rotate(0,0,±80) by -52deg
    for z in (80.0, -80.0):
        r = math.radians(-ANGLE)
        dx = z * math.sin(-r) if False else z * math.sin(r) * -1
        # rotate about Y by -ANGLE: (x,z) -> (x cos + z sin, -x sin + z cos)
        x2 = 0.0 * math.cos(r) + z * math.sin(r)
        z2 = -0.0 * math.sin(r) + z * math.cos(r)
        axles.append((NIP[0] + x2, NIP[1] + z2))
    axles = axles[-2:]
    for c in axles:
        ax.add_patch(Circle(c, WHEEL_R, fill=False, ec="#222", lw=1.8, zorder=3))
        ax.plot([c[0]], [c[1]], "+", color="#222", ms=10, zorder=4)
        ax.add_patch(Circle(c, 9, fill=False, ec="#666", lw=1.0, ls=":", zorder=3))
    ax.plot([axles[0][0], axles[1][0]], [axles[0][1], axles[1][1]],
            color="#222", lw=0.8, ls="-.", zorder=2)
    ax.plot([NIP[0]], [NIP[1]], marker="o", ms=5, color="#c00000", zorder=6)
    ax.annotate("夹口 nip", NIP, textcoords="offset points", xytext=(10, -14), fontsize=10)
    return axles


def draw_paddle(ax, C, phases=(18.0, 138.0, 258.0), tip=SWEEP, label=True):
    ax.add_patch(Circle(C, HUB_R, fill=False, ec="#c8610f", lw=1.8, zorder=4))
    ax.add_patch(Circle(C, tip, fill=False, ec="#c8610f", lw=1.2, ls="--", zorder=3))
    for p in phases:
        a = math.radians(p)
        for r0, r1, lw in ((HUB_R, 46.0, 1.4), (46.0, tip, 5.0)):
            ax.plot([C[0] + r0 * math.cos(a), C[0] + r1 * math.cos(a)],
                    [C[1] + r0 * math.sin(a), C[1] + r1 * math.sin(a)],
                    color="#c8610f", lw=lw, solid_capstyle="butt", zorder=4)
    ax.plot([C[0]], [C[1]], "+", color="#c8610f", ms=12, zorder=5)
    if label:
        ax.annotate("拨杆", C, textcoords="offset points", xytext=(6, 6),
                    fontsize=10, color="#c8610f")


def draw_chassis(ax):
    ax.add_patch(Rectangle((-175, 2), 395, 14, fc="#cfd6e0", ec="#8d97a5", lw=1.0, zorder=1))


def draw_flywheel_axis(ax, axles):
    """夹口方向的 52 度参考线"""
    ax.annotate("", xy=(NIP[0] + 150 * T52[0], NIP[1] + 150 * T52[1]),
                xytext=(NIP[0] - 260 * T52[0], NIP[1] - 260 * T52[1]),
                arrowprops=dict(arrowstyle="-", color="#c00000", lw=0.9, ls="--"), zorder=2)


# --------------------------------------------------------------------------
# 图
# --------------------------------------------------------------------------
fig, (axA, axB) = plt.subplots(1, 2, figsize=(21, 11.5))

# ============================== 左：现状 ==============================
ax = axA
draw_chassis(ax)
axles = draw_wheels(ax)

# 三段地板 / 顶板（顶板 = 各段自己平移 110）
for i, (s, e, ang) in enumerate(GUIDES):
    nx, nz = normal(ang)
    ax.plot([s[0], e[0]], [s[1], e[1]], color="#2b6a91", lw=5, alpha=0.85, zorder=3)
    rx0, rz0 = s[0] + 110 * nx, s[1] + 110 * nz
    rx1, rz1 = e[0] + 110 * nx, e[1] + 110 * nz
    ax.plot([rx0, rx1], [rz0, rz1], color="#7a2ea8", lw=4, alpha=0.75, zorder=3)
    ax.plot([(s[0] + e[0]) / 2, (rx0 + rx1) / 2], [(s[1] + e[1]) / 2, (rz0 + rz1) / 2],
            color="#999", lw=0.8, ls=":", zorder=2)
    ax.annotate(f"{ang:.0f}° 段", ((s[0] + e[0]) / 2, (s[1] + e[1]) / 2),
                textcoords="offset points", xytext=(-6, -18), fontsize=9, color="#2b6a91")

ax.annotate("每段顶板各自平移 110mm\n→ 三段互相错位、并在 x≈-100 处重叠",
            (-100, 127), textcoords="offset points", xytext=(-40, 78), fontsize=10,
            color="#7a2ea8", arrowprops=dict(arrowstyle="->", color="#7a2ea8", lw=1.2))

ax.add_patch(Circle(C_OLD, SWEEP + 3.0, fill=False, ec="#c8610f", lw=1.6, ls="--", zorder=3))
ax.add_patch(Circle(C_OLD, 1.0, fc="#c8610f", ec="none", zorder=3))
draw_paddle(ax, C_OLD)
ax.annotate("拨杆轴 (-47, 73)", C_OLD, textcoords="offset points", xytext=(-118, -34),
            fontsize=10, color="#c8610f")

# 52° 球心线的不可用段
tt = np.linspace(139.5, 237.3, 60)
ax.plot([NIP[0] - t * T52[0] for t in tt], [NIP[1] - t * T52[1] for t in tt],
        color="#d62728", lw=6, alpha=0.55, zorder=4)
ax.annotate("52° 发射线穿过拨杆鼓\n（球心线离拨杆轴仅 21.8mm，\n需要 ≥53.6mm）",
            (-70, 90), textcoords="offset points", xytext=(-90, -70), fontsize=10,
            color="#d62728", arrowprops=dict(arrowstyle="->", color="#d62728", lw=1.4))

ax.add_patch(Circle((-105, BALL_Z), BALL_R, fill=False, ec="#d62728", lw=1.6, zorder=5))
ax.add_patch(Circle((-105, BALL_Z), 1.0, fc="#d62728", ec="none", zorder=5))
ax.annotate("球（起）\n球心 z=53.06", (-105, BALL_Z), textcoords="offset points",
            xytext=(-30, -66), fontsize=10, color="#d62728")
ax.plot([-150, -80], [FLOOR_TOP, FLOOR_TOP], color="#1f7a3d", lw=0)
ax.annotate("托板顶面 z=17.5", (-148, FLOOR_TOP), textcoords="offset points",
            xytext=(-4, -26), fontsize=10, color="#1f7a3d")

ax.text(-195, 300, "现状：26°/52° 段地板被鼓形开孔吃光\n"
                   "  · 26° 地板只剩 x=-80.7…-75.2\n"
                   "  · 52° 地板只剩 x=11.7…13.7\n"
                   "  · 球心升到 z≈77-95 被楔死",
        fontsize=10.5, color="#a02020", va="top",
        bbox=dict(boxstyle="round,pad=0.45", fc="#fff2f2", ec="#e0a0a0"))

ax.set_title("A. 现状剖面（问题）", fontsize=14)

# ============================== 右：改后 ==============================
ax = axB
draw_chassis(ax)
draw_wheels(ax)

# 连续曲面通道：球心线 ± (球半径 + 间隙)
pts = ball_path_pts()
nrm = path_normals(pts)
# 选定"外侧"法向（离 C_NEW 更远的一侧）
mid = pts[len(pts) // 2]
if np.linalg.norm(mid + 10 * nrm[len(pts) // 2] - np.array(C_NEW)) < \
   np.linalg.norm(mid - 10 * nrm[len(pts) // 2] - np.array(C_NEW)):
    nrm = -nrm

gap = 3.5
outer = pts + nrm * (BALL_R + gap)
inner = pts - nrm * (BALL_R + gap)
ax.fill_between(outer[:, 0], outer[:, 1], inner[:, 1], color="#1f7a3d", alpha=0.10, zorder=1)
ax.plot(outer[:, 0], outer[:, 1], color="#1f7a3d", lw=3.0, zorder=4)
ax.plot(inner[:, 0], inner[:, 1], color="#1f7a3d", lw=1.6, ls="-.", zorder=4)
ax.plot(pts[:, 0], pts[:, 1], color="#d62728", lw=2.0, ls=":", zorder=5)

# 外罩 / 内侧保持面（圆弧段）
arc_a = np.linspace(A_ENTRY, A_EXIT, 200)
for r, lw, ls, col in ((R_SHELL, 3.0, "-", "#1f7a3d"), (R_SHELL - 2 * BALL_R, 1.6, "-.", "#1f7a3d")):
    ax.plot([C_NEW[0] + r * math.cos(math.radians(a)) for a in arc_a],
            [C_NEW[1] + r * math.sin(math.radians(a)) for a in arc_a],
            color=col, lw=lw, ls=ls, zorder=4)

draw_paddle(ax, C_NEW, tip=60.0)
ax.annotate(f"拨杆轴 ({CX:.1f}, {CZ:.1f})", C_NEW, textcoords="offset points",
            xytext=(14, 10), fontsize=10, color="#c8610f")

# 拨杆轴上移/右移到发射线法向 58.4mm 外
ax.annotate("", xy=C_NEW, xytext=C_OLD,
            arrowprops=dict(arrowstyle="-|>", color="#c8610f", lw=2.0, ls="--"), zorder=6)
ax.plot([C_OLD[0]], [C_OLD[1]], marker="x", ms=9, color="#888", zorder=6)
ax.annotate("原位", C_OLD, textcoords="offset points", xytext=(-40, -14), fontsize=9, color="#888")
ax.annotate("拨杆轴移到发射线法向 58.4mm 外\n→ 整条 52° 线离拨杆轴 ≥58.4 (>53.6)\n→ 地板不再被鼓挖空",
            (0, 90), textcoords="offset points", xytext=(30, 96), fontsize=10,
            color="#c8610f", arrowprops=dict(arrowstyle="->", color="#c8610f", lw=1.2))

# 球：入口 / 中途 / 切点
for a, tag, off in ((270.0, "球：滚到鼓底（与托板相切）", (-150, -30)),
                    (205.0, "被叶片推着走", (-96, 26)),
                    (A_EXIT, f"切点：球以 52° 切向离开\n球心 ({TANGENT[0]:.1f}, {TANGENT[1]:.1f})", (-40, 44))):
    p = on_arc(a)
    ax.add_patch(Circle(p, BALL_R, fill=False, ec="#d62728", lw=1.4, zorder=6))
    ax.plot([p[0]], [p[1]], marker="+", ms=7, color="#d62728", zorder=6)
    ax.annotate(tag, p, textcoords="offset points", xytext=off, fontsize=9.5, color="#d62728")

# 半径标注
ax.annotate("", xy=C_NEW, xytext=on_arc(200.0),
            arrowprops=dict(arrowstyle="<->", color="#1f7a3d", lw=1.4), zorder=7)
ax.annotate("球心半径 R58.4\n外罩 R93.96", (C_NEW[0] - 46, C_NEW[1] - 8),
            textcoords="offset points", xytext=(-30, -70), fontsize=10, color="#1f7a3d")

ax.annotate("52° 直槽 111.8mm\n→ 夹口", ((TANGENT[0] + NIP[0]) / 2, (TANGENT[1] + NIP[1]) / 2),
            textcoords="offset points", xytext=(20, 10), fontsize=10, color="#2b6a91")

# 旋转方向
arc_r = 88.0
ax.annotate("", xy=(C_NEW[0] + arc_r * math.cos(math.radians(196)),
                    C_NEW[1] + arc_r * math.sin(math.radians(196))),
            xytext=(C_NEW[0] + arc_r * math.cos(math.radians(250)),
                    C_NEW[1] + arc_r * math.sin(math.radians(250))),
            arrowprops=dict(arrowstyle="-|>", color="#0b6bb5", lw=3.0,
                            connectionstyle="arc3,rad=0.28"), zorder=8)
ax.annotate("球必须这样走：托板 → 鼓底 → 沿左侧上行 → 切向进入发射段\n"
            "对应 前视逆时针（ω_y>0）", C_NEW, textcoords="offset points",
            xytext=(-215, -118), fontsize=10, color="#0b6bb5")

# 距离对比
ax.annotate(f"拨杆轴→夹口：190.5 → {math.dist(C_NEW, NIP):.1f} mm", (0, 268),
            textcoords="offset points", xytext=(24, 30), fontsize=11, color="#a05000",
            bbox=dict(boxstyle="round,pad=0.3", fc="#fff6e8", ec="#e0b070"))

ax.set_title("B. 改后剖面（连续曲面通道 + 拨杆外移）", fontsize=14)

# ---------------- 小插图：前视转向 ----------------
ins = axB.inset_axes([0.015, 0.015, 0.30, 0.30])
ins.set_xlim(-1.6, 3.6)
ins.set_ylim(-1.6, 1.6)
ins.set_aspect("equal")
ins.axis("off")
for k, (dx, ccw, ok) in enumerate(((0.0, False, True), (1.9, True, False))):
    cx = dx
    ins.add_patch(Circle((cx, 0), 0.62, fill=False, ec="#c8610f", lw=1.4))
    ang0, ang1 = (230, 150) if ccw else (150, 230)
    ins.add_patch(matplotlib.patches.Arc((cx, 0), 1.3, 1.3, theta1=min(ang0, ang1),
                                         theta2=max(ang0, ang1), color="#0b6bb5", lw=2.2))
    ins.plot([cx + 0.62 * math.cos(math.radians(ang1))],
             [0.62 * math.sin(math.radians(ang1))], marker=">", color="#0b6bb5", ms=7)
    ins.plot([cx], [0], marker="+", color="#c8610f", ms=8)
    ins.add_patch(Circle((cx - 0.62 - 0.36, -0.30), 0.36, fill=False, ec="#8a5a00", lw=1.0))
    ins.text(cx - 0.62 - 0.36, -1.22, "球", ha="center", fontsize=8)
    ins.text(cx + 0.62 + 0.42, 0.62, "→发射", fontsize=8, ha="center", color="#8a5a00")
    ins.text(cx, 1.28, ("前视 逆时针 ✓" if ok else "前视 顺时针 ✗（球被带反）"),
             ha="center", fontsize=9, color=("#1a7a3a" if ok else "#c00000"))
ins.text(0.5, -0.02, "前视 = 发射部分在拨杆左侧（左右镜像）", transform=ins.transAxes,
         ha="center", fontsize=8, color="#555")

for ax in (axA, axB):
    ax.set_aspect("equal")
    ax.set_xlim(-215, 205)
    ax.set_ylim(-30, 330)
    ax.grid(alpha=0.25, lw=0.6)
    ax.set_xlabel("X [mm]")
    ax.set_ylabel("Z [mm]")

fig.suptitle("T06 POLLEN：把送球段从「三段平板」改成「绕拨杆轴的连续曲面通道」（单位 mm，剖面为 X–Z 面）",
             fontsize=15)
fig.tight_layout(rect=(0, 0, 1, 0.965))
path = OUT / "design_review_zh.png"
fig.savefig(path, dpi=125)
print("saved:", path)
print()
print(f"C_OLD            = {C_OLD}")
print(f"C_NEW            = ({CX:.2f}, {CZ:.2f})")
print(f"R_SHELL          = {R_SHELL:.2f}   R_CARRY = {R_CARRY}   ball centre z on tray = {BALL_Z:.2f}")
print(f"TANGENT          = ({TANGENT[0]:.2f}, {TANGENT[1]:.2f})")
print(f"|C_OLD - nip|    = {math.dist(C_OLD, NIP):.1f} mm")
print(f"|C_NEW - nip|    = {math.dist(C_NEW, NIP):.1f} mm")
print(f"52deg line perp distance to C_OLD = {(C_OLD[0]-NIP[0])*N52[0]+(C_OLD[1]-NIP[1])*N52[1]:.2f} mm")
print(f"52deg line perp distance to C_NEW = {(C_NEW[0]-NIP[0])*N52[0]+(C_NEW[1]-NIP[1])*N52[1]:.2f} mm")

# ============================== 中右：转向不放在图上 ==============================
