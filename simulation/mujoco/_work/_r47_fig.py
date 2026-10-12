# -*- coding: utf-8 -*-
"""R47 胶带位置剖面示意图（xz 平面，真实件位，单位 mm）。"""
import math, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Wedge
from matplotlib.transforms import Affine2D
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

CX, CZ = 29.49, 111.46
R_IN = 107.974
r10_pos = [(-61.6,175.8),(-67.4,166.7),(-72.2,157.1),(-76.2,147.0),(-79.1,136.7),
           (-81.0,126.0),(-81.9,115.3),(-81.8,104.5),(-80.6,93.8),(-78.4,83.3),
           (-75.1,73.0),(-70.9,63.1),(-65.8,53.6),(-59.8,44.7),(-52.9,36.4),
           (-45.3,28.8),(-36.9,21.9),(-28.0,15.9),(-18.5,10.8),(-8.5,6.7),
           (1.8,3.5),(12.3,1.3),(23.0,0.2),(33.8,0.1)]
r10_pos = [(x, z, math.degrees(math.atan2(z - CZ, x - CX)) % 360.0) for (x, z) in r10_pos]
SEG = 7.5     # 每段弧长 deg 近似
TAPE_A0, TAPE_A1 = 133.0, 260.0

fig, ax = plt.subplots(figsize=(11.5, 9))
T = ax.transData

def box(x, z, hl, hw, ang, fc, ec="k", lw=0.5, alpha=1.0, zo=4):
    t = Affine2D().rotate_deg_around(x, z, ang) + T
    p = Rectangle((x - hl, z - hw), 2*hl, 2*hw, facecolor=fc, edgecolor=ec,
                  lw=lw, alpha=alpha, zorder=zo)
    p.set_transform(t); ax.add_patch(p)

# --- 外罩内弧段（按真实角度旋转矩形） ---
for (x0, z0, a) in r10_pos:
    on = TAPE_A0 <= a <= TAPE_A1
    box(x0, z0, 3.65, 1.75, a, "#e8442a" if on else "#a9c1dc", alpha=1.0 if on else 0.55)

# --- 胶带区弧带高亮 ---
th = [math.radians(t) for t in [k * 0.5 for k in range(int(TAPE_A0 * 2), int(TAPE_A1 * 2) + 1)]]
ax.plot([CX + (R_IN - 0.6) * math.cos(q) for q in th],
        [CZ + (R_IN - 0.6) * math.sin(q) for q in th], "-", color="#e8442a", lw=3.2, alpha=0.55, zorder=3)

# 球心参考轨迹
ax.plot([CX + 63.2 * math.cos(q) for q in th], [CZ + 63.2 * math.sin(q) for q in th],
        "--", color="#555", lw=1.0, zorder=2)

# --- 拨杆：3 组 臂/叶片/弹性指，相位 30/150/270，半径 28/52/58 ---
for ph in (30.0, 150.0, 270.0):
    q = math.radians(ph)
    for rad, hr, ht, fc in ((28.0, 16.0, 5.0, "#f2b183"),
                            (52.0, 6.0, 15.0, "#e07b39"),
                            (58.0, 2.0, 17.0, "#c95f1e")):
        x, z = CX + rad * math.cos(q), CZ + rad * math.sin(q)
        box(x, z, hr, ht, ph, fc, alpha=0.95, zo=5)
ax.add_patch(Circle((CX, CZ), 12.0, facecolor="#f4a261", edgecolor="k", lw=0.9, zorder=6))

# --- 卡滞球（NECTAR, r=45.97, 实测球心 -16.5,154.8） ---
ax.add_patch(Circle((-16.5, 154.8), 45.97, facecolor="#2a9d8f", edgecolor="k",
                    lw=1.1, alpha=0.35, zorder=1))
ax.plot([-16.5], [154.8], "o", color="#1d6f66", ms=5, zorder=6)
ax.annotate("卡滞球位 (NECTAR)", (-16.5, 154.8), textcoords="offset points",
            xytext=(12, -20), fontsize=10, color="#1d6f66")

ax.plot([CX], [CZ], "k+", ms=15, mew=1.8, zorder=7)
ax.annotate("拨杆轴心", (CX, CZ), textcoords="offset points", xytext=(10, -16), fontsize=10)
ax.annotate("拨杆叶片/弹性指\n（本次不贴带）", (-30, 60), fontsize=10, color="#8a4a12", ha="center")

ax.set_aspect("equal")
ax.set_xlim(-140, 130); ax.set_ylim(-30, 235)
ax.set_xlabel("x (mm)    ← 飞轮发射侧          托板/进料侧 →")
ax.set_ylabel("z (mm)")
ax.set_title("R47 低摩擦胶带贴敷位置：红色段 = 球与外罩实际滑动接触弧 135°→258°（约 123°）", fontsize=12.5)
ax.grid(alpha=0.25)
fig.tight_layout()
fig.savefig("simulation/mujoco/out/_r47_tape_section.png", dpi=130)
print("saved")
