# -*- coding: utf-8 -*-
"""T06 R53f -- cross section of the rigid fixed-length stop ring (schematic).

Proportions come from the generator constants, not from a screenshot.
Panel A = adopted ring around the spring.  Panel B = the rejected thin sleeve
inside the spring (0.25 mm wall, kept as the record of why it was dropped).
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
from matplotlib import font_manager

F = font_manager.FontProperties(fname="C:/Windows/Fonts/msyhbd.ttc")
OUT = "cad/output/_r53f_lock"
os.makedirs(OUT, exist_ok=True)
DESK = "C:/Users/admin/OneDrive/Desktop/T06_R53f_限位环剖面.png"
GRAY = "#c9ced6"; DARK = "#2b3440"; ORANGE = "#e08c2e"; GREEN = "#1f9d55"
RED = "#c0392b"; TEAL = "#0f8b8d"; STEEL = "#8d949e"; PURPLE = "#7b52ab"

# generator constants (cad/paddle_launcher_shooter_lock_r53b.py / _r53f.py)
EAR_HI = 75.3                     # outer ear face
SP_R, SP_W, SP_TURNS, SP_INST = 2.5, 0.25, 4, 6.0
SEAT_OD_R, SEAT_BORE_R, SEAT_L = 4.00, 2.85, 6.0
WASHER_R, WASHER_T = 5.0, 1.2
NUT_R, NUT_T = 4.0, 3.2
CLAMP_U = 36.0
Y0 = EAR_HI
Y1 = EAR_HI + SEAT_L               # 81.3  ring / spring end face
Y2 = Y1 + WASHER_T                 # 82.5
Y3 = Y2 + NUT_T                    # 85.7

fig = plt.figure(figsize=(19.0, 8.6), dpi=110)
fig.patch.set_facecolor("white")
gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 0.86], wspace=0.14)


def stack(ax, ring_mode):
    u = CLAMP_U
    # ear plate band (the thing being clamped)
    for yy in (72.3,):
        ax.add_patch(Rectangle((u - 14, yy), 28, 3.0, fc=ORANGE, ec=DARK, lw=1.8,
                               alpha=0.92, zorder=3))
    ax.text(u - 16.5, 73.8, "耳板 3 mm", fontproperties=F, fontsize=10.5,
            ha="right", va="center")
    # friction face
    ax.add_patch(Rectangle((u - 9, Y0 - 0.35), 18, 0.7, fc=RED, ec="none", zorder=6))
    ax.text(u - 12.0, Y0 - 2.2, "夹紧摩擦面", fontproperties=F, fontsize=10,
            color=RED, ha="right", va="center")
    # spring coils, always Ø5.5 compressed to 6.0
    pitch = (SP_INST - 2 * SP_W) / (SP_TURNS - 1)
    for i in range(SP_TURNS):
        cy = Y0 + SP_W + i * pitch
        ax.add_patch(Rectangle((u - SP_R, cy - SP_W), 2 * SP_R, 2 * SP_W, fc=TEAL,
                               ec="none", alpha=0.95, zorder=5))
    ax.add_patch(Rectangle((u - SP_R, Y0), 2 * SP_R, SP_INST, fc="none", ec=TEAL,
                           lw=1.4, ls="--", zorder=5))
    if ring_mode:
        # adopted: rigid ring OUTSIDE the spring, R2.85..R4.0, 6.0 long
        ax.add_patch(Rectangle((u - SEAT_OD_R, Y0), SEAT_OD_R - SEAT_BORE_R, SEAT_L,
                               fc=PURPLE, ec=DARK, lw=1.8, alpha=0.95, zorder=6))
        ax.add_patch(Rectangle((u + SEAT_BORE_R, Y0), SEAT_OD_R - SEAT_BORE_R, SEAT_L,
                               fc=PURPLE, ec=DARK, lw=1.8, alpha=0.95, zorder=6))
        ax.annotate("", xy=(u - SEAT_OD_R - 0.6, Y0), xytext=(u - SEAT_OD_R - 0.6, Y1),
                    arrowprops=dict(arrowstyle="<|-|>", color=PURPLE, lw=1.7), zorder=8)
        ax.text(u - SEAT_OD_R - 1.4, (Y0 + Y1) / 2, "定长环 6.0\nØ8.0 / Ø5.7",
                fontproperties=F, fontsize=10.5, color=PURPLE, ha="right",
                va="center")
        ax.text(u + 1.2, 78.3, "弹簧 Ø5.5\n被压到 6.0", fontproperties=F,
                fontsize=10.5, color=TEAL, va="center", zorder=9)
    else:
        # rejected: 0.25 mm wall sleeve INSIDE the spring, Ø4.5 / Ø4.3
        ax.add_patch(Rectangle((u - 2.25, Y0), 0.25, SEAT_L, fc=RED, ec=DARK,
                               lw=1.2, alpha=0.95, zorder=6))
        ax.add_patch(Rectangle((u + 2.00, Y0), 0.25, SEAT_L, fc=RED, ec=DARK,
                               lw=1.2, alpha=0.95, zorder=6))
        ax.annotate("", xy=(u + 2.25, 78.9), xytext=(u - 2.25, 78.9),
                    arrowprops=dict(arrowstyle="<|-|>", color=RED, lw=1.5), zorder=8)
        ax.text(u + 9.0, 78.3, "细套筒壁厚只有 0.25 mm\n截面 1.38 mm2 ≈ 69 N\n手拧就压溃",
                fontproperties=F, fontsize=10.5, color=RED, va="center", zorder=9)
        # M4 stud passing through
        ax.add_patch(Rectangle((u - 2.0, Y0), 4.0, SEAT_L, fc=STEEL, ec=DARK,
                               lw=1.2, alpha=0.55, zorder=5))
    # washer + nyloc nut, both resting on the ring end face at Y1
    ax.add_patch(Rectangle((u - WASHER_R, Y1), 2 * WASHER_R, WASHER_T, fc=STEEL,
                           ec=DARK, lw=1.6, zorder=7))
    ax.add_patch(Polygon([(u + NUT_R, Y2), (u + NUT_R * 0.5, Y3),
                          (u - NUT_R * 0.5, Y3), (u - NUT_R, Y2)], closed=True,
                         fc=STEEL, ec=DARK, lw=1.6, zorder=7))
    ax.annotate("", xy=(u - WASHER_R - 0.5, Y1), xytext=(u - WASHER_R - 0.5, Y1 - 6.0),
                arrowprops=dict(arrowstyle="-|>", color=DARK, lw=2.0), zorder=8)
    ax.text(u + WASHER_R + 1.2, Y2 + 1.0, "平垫 R5.0 + M4 尼龙锁紧螺母\n再拧只压环，预载不再增长",
            fontproperties=F, fontsize=10.5, va="center", zorder=9)
    ax.set_xlim(u - 26.0, u + 30.0)
    ax.set_ylim(66.0, 88.0)
    ax.set_aspect("equal")
    ax.set_xlabel("u  [mm]", fontproperties=F, fontsize=11)
    ax.set_ylabel("n（螺柱轴 / 装配轴向）  [mm]", fontproperties=F, fontsize=11)
    ax.grid(alpha=0.18, lw=0.6)


axA = fig.add_subplot(gs[0, 0])
axA.set_title("A  采用：刚性定长限位环套在弹簧外面 Ø8.0 / Ø5.7 x 6.0\n"
              "平垫压到环端面即到底 => 预载 = 1.24 x (8.4 - 6.0) = 2.976 N/颗",
              fontproperties=F, fontsize=12.5)
stack(axA, True)

axB = fig.add_subplot(gs[0, 1])
axB.set_title("B  已否决：套在螺柱上的细套筒 Ø4.5 / Ø4.3 x 6.0\n"
              "径向只剩 0.25 mm => 扛不住手拧（保留作否决记录）",
              fontproperties=F, fontsize=12.5)
stack(axB, False)

fig.text(0.5, 0.025,
         "T06 R53f  每根 M4 螺柱 1 件，16 件/档；环截面 24.75 mm2（约 1.24 kN）；"
         "打印 ±0.2 mm => 预载 ±0.25 N；换档仍由已有 2000-0025-0002 完成（DEC-0052 / V-0055 / V-0056）",
         fontproperties=F, fontsize=11, ha="center", color=DARK)
fig.subplots_adjust(left=0.055, right=0.985, top=0.87, bottom=0.10)

for path in (os.path.join(OUT, "T06_R53f_限位环剖面.png"), DESK):
    fig.savefig(path, facecolor="white")
    print("wrote", path)
