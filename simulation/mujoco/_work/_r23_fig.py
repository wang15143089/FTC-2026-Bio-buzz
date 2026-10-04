# -*- coding: utf-8 -*-
"""Section view: why the NECTAR ball must have a tangent tray (R23)."""
import math, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, Arc
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

AX, AZ = 29.49, 111.46
PIVX, PIVZ = -2.30, 17.50
TILT = 5.0
BR = 45.974
HUB = 12.0
A_EXIT = 142.0
R_CARRY = 58.4
R_IN = R_CARRY + BR
SIN, COS = math.sin(math.radians(TILT)), math.cos(math.radians(TILT))
D0 = (AZ - PIVZ) * COS - (AX - PIVX) * SIN


def mk(delta, cut_x, a_lip, tray_x1=150.0):
    piv = (PIVX + delta * SIN, PIVZ - delta * COS)

    def top(x):
        return piv[1] + (x - piv[0]) * math.tan(math.radians(TILT))
    return piv, top, cut_x, a_lip, tray_x1


def draw(ax, delta, label, note):
    piv, top, cut_x, a_lip, tray_x1 = mk(delta, 0, 0)
    if delta == 0.0:
        cut_x, a_lip = 99.17, 309.32
    else:
        cut_x = AX + R_IN * SIN
        a_lip = math.degrees(math.atan2(-R_IN * COS, R_IN * SIN)) % 360.0
    # shell band
    ax.add_patch(Arc((AX, AZ), 2 * R_IN, 2 * R_IN, theta1=A_EXIT, theta2=a_lip,
                     color="#1f4e79", lw=7, zorder=3))
    ax.add_patch(Circle((AX, AZ), R_IN, fill=False, ls=":", color="#7f7f7f", lw=0.8, zorder=1))
    ax.add_patch(Circle((AX, AZ), HUB, color="#c00000", zorder=4))
    ax.add_patch(Circle((AX, AZ), 60.0, fill=False, ls="-.", color="#e08a00", lw=0.9, zorder=2))
    # tray
    poly = [(cut_x, top(cut_x)),
            (tray_x1, top(tray_x1)),
            (tray_x1 - (-COS) * 6, top(tray_x1) - SIN * 6),
            (cut_x - (-COS) * 6, top(cut_x) - SIN * 6)]
    ax.add_patch(Polygon(poly, closed=True, fc="#bfbfbf", ec="#404040", lw=1.0, zorder=2))
    # balls on the tray + nest
    for x in (145, 130, 115, 100, 88, 78, 68, 58, 48):
        if x < cut_x - 0.5:
            continue
        ax.add_patch(Circle((x, top(x) + BR), BR, fill=False, ec="#2e7d32", lw=0.9,
                            alpha=0.55, zorder=5))
    ax.add_patch(Circle((AX, AZ - R_CARRY), BR, fc="#2e7d32", alpha=0.25,
                        ec="#1b5e20", lw=1.4, zorder=6))
    # drop annotation for the un-shifted case
    if delta == 0.0:
        xd = cut_x
        r_end = math.hypot(xd - AX, top(xd) + BR - AZ)
        ax.annotate("", xy=(xd, top(xd) + BR - (r_end - R_CARRY)), xytext=(xd, top(xd) + BR),
                    arrowprops=dict(arrowstyle="<->", color="#d32f2f", lw=1.6))
        ax.text(xd + 6, top(xd) + BR - (r_end - R_CARRY) / 2,
                "落差 %.1f mm\n球撞在唇口后弹回" % (r_end - R_CARRY),
                color="#d32f2f", fontsize=9, va="center")
    else:
        ax.plot([AX + R_IN * SIN], [AZ - R_IN * COS], "o", ms=6, color="#d32f2f", zorder=7)
        ax.annotate("切点 = 球窝\n(落差 0)",
                    xy=(AX + R_IN * SIN, AZ - R_IN * COS),
                    xytext=(AX + R_IN * SIN + 8, AZ - R_IN * COS - 40),
                    color="#d32f2f", fontsize=9,
                    arrowprops=dict(arrowstyle="->", color="#d32f2f", lw=1.2))
    ax.set_title(label, fontsize=11)
    ax.text(0.02, 0.02, note, transform=ax.transAxes, fontsize=9, color="#333333",
            va="bottom")
    ax.set_xlim(-70, 175)
    ax.set_ylim(-35, 215)
    ax.set_aspect("equal")
    ax.grid(alpha=0.25, lw=0.5)
    ax.set_xlabel("x / mm")
    ax.set_ylabel("z / mm")


fig, axes = plt.subplots(1, 2, figsize=(16.5, 9.2))
draw(axes[0], 0.0, "(a) 托盘不动（R20/R21/R22）",
     "托盘顶面到桨轴 %0.1f mm\n外壳内圆 R_IN=%0.1f → 差 %0.1f mm\n球在托盘末端比运载圆高 %.1f mm"
     % (D0, R_IN, R_IN - D0, 71.41 - R_CARRY if False else 13.0))
draw(axes[1], R_IN - D0, "(b) R23：托盘沿法线下移 %.1f mm，与运载圆相切" % (R_IN - D0),
     "托盘顶面到桨轴 = R_IN = %0.1f mm\n球滚到切点正好落在球窝 (r=%.1f)\n外壳唇口收在 %.1f°（切点角）" % (R_IN, R_CARRY, 275.0))
fig.suptitle("NECTAR 送球交接：托盘必须与外罩内圆相切（球 Ø%.1f mm，夹口 82 mm）" % (2 * BR),
             fontsize=13)
fig.tight_layout(rect=(0, 0, 1, 0.96))
out = Path("cad/output/_r23_gravity_handoff_zh.png")
fig.savefig(out, dpi=130, bbox_inches="tight")
print("saved", out)
