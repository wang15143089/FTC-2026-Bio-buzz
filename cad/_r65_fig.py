# -*- coding: utf-8 -*-
"""R65 figure: how the splice plate + 2x M3 fix the x=-40 rail seam."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrow

DEST = Path("cad/output/_r65_splice")
d = json.loads((DEST / "report_r65_pollen.json").read_text(encoding="utf-8"))
SEAM, XA, XB = d["seam_x"], d["back_hole_x"], d["front_hole_x"]
HZ, PT = d["hole_z"], d["plate_thickness_mm"]
XR, XF = -90.0, 30.0
BLU, RED, GRN, GRY = "#aec6e8", "#f2b8b0", "#8fd18f", "0.45"

fig = plt.figure(figsize=(15.5, 12.0))
gs = fig.add_gridspec(3, 1, height_ratios=[1.0, 1.0, 1.15], hspace=0.42)

# ---------------- A: side elevation (looking along -Y) ----------------
ax = fig.add_subplot(gs[0])
ax.add_patch(Rectangle((XR, -10), SEAM - XR, 26, fc=BLU, ec="k", lw=1.2))
ax.add_patch(Rectangle((SEAM, -10), XF - SEAM, 26, fc=RED, ec="k", lw=1.2))
ax.text((XR + SEAM) / 2, 3, "base_rail_rear_joined\nx [-170, -40]", ha="center", va="center", fontsize=9)
ax.text((SEAM + XF) / 2, 3, "base_rail_front_±72\nx [-40, 210]", ha="center", va="center", fontsize=9)
ax.add_patch(Rectangle((d["plate_x_mm"][0], -10), 80, 26, fc="none", ec=GRN, lw=3.0, ls="-"))
ax.text(-40, 20.5, "splice plate (green) sits on the OUTER face y 81..86, x -80..0",
        ha="center", fontsize=9.5, color="#1a6b1a", weight="bold")
for x in (XA, XB):
    ax.plot([x], [HZ], marker="o", ms=11, mfc=GRY, mec="k", zorder=5)
    ax.plot([x, x], [HZ, HZ + 4], color="0.55", lw=1.0)
    ax.text(x, HZ + 5.2, "M3", ha="center", fontsize=8.5)
    ax.text(x, -15.5, "%.0f" % x, ha="center", fontsize=8.5)
ax.axvline(SEAM, color="k", ls="--", lw=1.6)
ax.annotate("split plane x = -40\n(flat butt, no tongue/lap)", xy=(SEAM, 16), xytext=(-38, 30),
            ha="left", fontsize=9.5, arrowprops=dict(arrowstyle="->", lw=1.1))
ax.annotate("bolt 26 mm from\nthe seam", xy=(XA, HZ), xytext=(-88, -19), fontsize=9,
            arrowprops=dict(arrowstyle="->", lw=1.0))
ax.annotate("bolt 24 mm from\nthe seam", xy=(XB, HZ), xytext=(4, -19), fontsize=9,
            arrowprops=dict(arrowstyle="->", lw=1.0))
ax.axhline(-10, color="k", lw=2.2)
ax.text(XF - 2, -12.5, "ground contact plane z = -10 (unchanged, plate does not go below)",
        ha="right", fontsize=9)
ax.set_xlim(XR - 4, XF + 4); ax.set_ylim(-24, 34)
ax.set_xlabel("X [mm]"); ax.set_ylabel("Z [mm]")
ax.set_title("A — side elevation at the rail: one plate spans the seam, 2 x M3 cross it (hole height z = %.0f mm)" % HZ,
             fontsize=11.5, weight="bold")

# ---------------- B: plan view ----------------
ax = fig.add_subplot(gs[1])
for ys in (1, -1):
    y0 = 63.0 * ys if ys > 0 else -81.0
    ax.add_patch(Rectangle((XR, y0), SEAM - XR, 18, fc=BLU, ec="k", lw=1.1))
    ax.add_patch(Rectangle((SEAM, y0), XF - SEAM, 18, fc=RED, ec="k", lw=1.1))
    ax.add_patch(Rectangle((-80, 81 * ys if ys > 0 else -86), 80, PT, fc=GRN, ec="k", lw=1.2, alpha=0.95))
    ax.text(-44.0, 72 * ys, "plate", fontsize=8.5, va="center", ha="center", rotation=0)
for xr in (-95.0, -60.0):
    ax.add_patch(Rectangle((xr, -66), 10, 132, fc=BLU, ec="k", lw=0.8, alpha=0.55))
for xr in (-160.0, -125.0):
    ax.add_patch(Rectangle((xr, -66), 10, 132, fc=BLU, ec="k", lw=0.8, alpha=0.35))
ax.text(-120, 0, "cross ribs\n(part of the rear piece)", fontsize=8.5, ha="center", va="center", style="italic")
for ys in (1, -1):
    for x in (XA, XB):
        y = 72.0 * ys
        ax.plot([x], [y], marker="o", ms=9, mfc=GRY, mec="k", zorder=5)
        ax.plot([x], [63 * ys - 4 * ys], marker="s", ms=7, mfc="none", mec="b", zorder=5)
        ax.plot([x, x], [y, 63 * ys - 4 * ys], color="0.55", lw=1.0, ls=":")
ax.annotate("nut goes on the INNER rail face (blue squares)\n-> free space verified vs the whole assembly",
            xy=(XB, 59), xytext=(-30, 24), fontsize=9,
            arrowprops=dict(arrowstyle="->", lw=1.0))
ax.axvline(SEAM, color="k", ls="--", lw=1.6)
ax.text(SEAM - 1.5, 96, "seam x = -40", ha="right", fontsize=9.5)
ax.set_xlim(XR - 4, XF + 4); ax.set_ylim(-104, 108)
ax.set_xlabel("X [mm]"); ax.set_ylabel("Y [mm]")
ax.set_title("B — plan: plates sit on the two OUTER faces (y 81..86 / -86..-81), spanning 40 mm each side",
             fontsize=11.5, weight="bold")

# ---------------- C: section at x = -55 (looking along +X) ----------------
ax = fig.add_subplot(gs[2])
cy = 1.0
ax.add_patch(Rectangle((63, -10), 18, 26, fc=BLU, ec="k", lw=1.4))
ax.add_patch(Rectangle((81, -10), PT, 26, fc=GRN, ec="k", lw=1.4))
ax.text(72, 12.5, "rail 18 x 26", ha="center", fontsize=9.5)
ax.text(83.5, 13.5, "plate\n5 mm", ha="center", fontsize=8.5, color="#1a6b1a", weight="bold")
ax.add_patch(Rectangle((86, HZ - 3.0), 3.0, 6.0, fc="0.35", ec="k", lw=1.0))
ax.text(90.5, HZ, "cap head\nM3 x 30", fontsize=8.5, va="center")
ax.add_patch(Rectangle((60.6, HZ - 3.2), 2.4, 6.4, fc="0.55", ec="k", lw=1.0))
ax.text(56, HZ - 7.5, "M3 nut\n(inner face)", fontsize=8.5, ha="center", va="top")
ax.plot([56, 86], [HZ, HZ], color="k", lw=2.0)
ax.text(71, HZ + 1.4, "bolt shaft through 5 + 18 mm", fontsize=8.5, ha="center", color="w", weight="bold")
ax.annotate("", xy=(63, 19.5), xytext=(86, 19.5), arrowprops=dict(arrowstyle="<->", lw=1.1))
ax.text(74.5, 20.5, "23 mm grip", ha="center", fontsize=9)
ax.text(72, -14.5, "section at x = -55 mm (rear side of the seam)\n"
                   "45 checks / 45 pass: holes open, walls present, no collision with any of the 82 bodies",
        ha="center", fontsize=9.5)
ax.set_xlim(50, 100); ax.set_ylim(-22, 26)
ax.set_xlabel("Y [mm]"); ax.set_ylabel("Z [mm]")
ax.set_aspect("equal")
ax.set_title("C — section: plate + rail sandwiched by one M3 (head outside, nut inside)", fontsize=11.5, weight="bold")

out = DEST / "r65_splice_schematic.png"
fig.savefig(out, dpi=165, bbox_inches="tight")
print("wrote", out)
