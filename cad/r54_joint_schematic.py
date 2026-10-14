# -*- coding: utf-8 -*-
"""R54 joint schematic: where the M3 bolt + nut actually goes."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

RAIL = dict(x0=-170.0, x1=210.0, y0=63.0, y1=81.0, z0=2.0, z1=16.0)
TAB  = dict(x0=54.0, x1=66.0, y0=64.0, y1=76.0, z0=16.0, z1=44.0)   # x=60 tab
PLATE= dict(y0=68.0, y1=72.0, zlow=38.0, ztop=401.0)
BOLT = dict(y=70.0, z0=0.0, z1=40.0, r=1.7)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6.2))

# ---- (a) YZ section through the joint -------------------------------------
ax1.add_patch(Rectangle((RAIL["y0"], RAIL["z0"]), RAIL["y1"]-RAIL["y0"], RAIL["z1"]-RAIL["z0"],
                        fc="#c9d6e3", ec="k", lw=1.4))
ax1.text(72, 9, "base rail\n(y 63..81, z 2..16)", ha="center", va="center", fontsize=8)
ax1.add_patch(Rectangle((TAB["y0"], TAB["z0"]), TAB["y1"]-TAB["y0"], TAB["z1"]-TAB["z0"],
                        fc="#ffe0a3", ec="k", lw=1.4))
ax1.text(70, 30, "rail tab\n(fused into frame)", ha="center", va="center", fontsize=8)
ax1.add_patch(Rectangle((PLATE["y0"], PLATE["zlow"]), PLATE["y1"]-PLATE["y0"], 60,
                        fc="#bde3b5", ec="k", lw=1.4))
ax1.text(70, 66, "side plate\n(4 mm)", ha="center", va="center", fontsize=8)
ax1.plot([BOLT["y"], BOLT["y"]], [BOLT["z0"], BOLT["z1"]], color="#c0392b", lw=2.2, zorder=5)
ax1.plot([BOLT["y"]-4.5, BOLT["y"]+4.5], [BOLT["z1"], BOLT["z1"]], color="#c0392b", lw=2.6, zorder=5)
ax1.plot([BOLT["y"]-4.5, BOLT["y"]+4.5], [BOLT["z1"]+3, BOLT["z1"]+3], color="#c0392b", lw=1.0)
ax1.plot([BOLT["y"]-5.5, BOLT["y"]+5.5], [BOLT["z0"], BOLT["z0"]], color="#c0392b", lw=3.0, zorder=5)
ax1.annotate("M3 bolt head", (BOLT["y"], BOLT["z1"]+6), ha="center", fontsize=8, color="#c0392b")
ax1.annotate("M3 nut", (BOLT["y"]+13, BOLT["z0"]+1), ha="left", fontsize=8, color="#c0392b")
ax1.annotate("", xy=(BOLT["y"], BOLT["z0"]+1), xytext=(BOLT["y"]+12, BOLT["z0"]+1),
             arrowprops=dict(arrowstyle="->", color="#c0392b", lw=1.0))
ax1.annotate("O3.4 through both", (95, 22), fontsize=8.5, color="#c0392b")
ax1.set_title("(a) YZ section at x = 60  -  frame -> base rail joint", fontsize=10)
ax1.set_xlabel("Y (mm)"); ax1.set_ylabel("Z (mm)")
ax1.set_xlim(45, 115); ax1.set_ylim(-8, 95); ax1.set_aspect("equal"); ax1.grid(alpha=0.3)

# ---- (b) XZ view: plate lower edge + tab pair + gussets -------------------
MEAS = [194,188,182,176,170,162,156,150,144,138,132,126,120,112,106,100,94,88,82,76,
        70,62,56,50,44,38,34,42,52,62,72,84,94,104,114,124,134,144,154,164,176,186,196,
        206,228]
XS = list(range(-140, 213, 8))
ax2.plot(XS, MEAS, "-", color="#2e7d32", lw=1.8,
         label="side plate lower edge (MEASURED, 8 mm steps)")
ax2.plot([-147.2, 213.8], [33.6, 33.6], ":", color="gray", lw=1.0)
ax2.add_patch(Rectangle((-170, 2), 380, 14, fc="#c9d6e3", ec="k", lw=1.0, alpha=0.7,
                        label="base rail z 2..16 (kept part)"))
for x, ztop in ((60.0, 44.0), (76.0, 48.0)):
    ax2.add_patch(Rectangle((x-6, 16), 12, ztop-16, fc="#ffe0a3", ec="k", lw=1.3,
                            label="rail tab (printed)" if x == 60 else None))
ax2.plot([60, 76], [18, 18], "o", color="#c0392b", ms=7, zorder=6,
         label="M3 bolt+nut (2 per side)")
ax2.text(-140, 165, "16 gussets (8 slots x 2 sides)\nlive in the y = 54..68 gap\nsee r54_pollen_section_y64.png",
         fontsize=8, color="#8e44ad")
ax2.set_title("(b) XZ: where the frame meets the rails", fontsize=10)
ax2.set_xlabel("X (mm)"); ax2.set_ylabel("Z (mm)")
ax2.set_xlim(-180, 230); ax2.set_ylim(-10, 215); ax2.set_aspect("equal"); ax2.grid(alpha=0.3)
ax2.legend(fontsize=7.5, loc="upper right")

fig.suptitle("T06 R54 - printed frame fastening (no self-tapping: straight O3.4 hole, bolt + nut)",
             fontsize=11)
fig.tight_layout(rect=(0, 0, 1, 0.95))
out = r"cad\output\_r54_frame\sections\r54_joint_schematic.png"
fig.savefig(out, dpi=150)
print("wrote", out)
