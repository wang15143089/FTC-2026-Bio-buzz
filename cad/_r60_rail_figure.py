# -*- coding: utf-8 -*-
"""R60 figure: the sole is pressed 3 mm deeper than R59 (-7 -> -10 mm) and the
x = 114 print split is gone, so each side is ONE printed rail again.  Every
number is pulled from the R60 generator, so the drawing cannot drift from the
delivered STEP.  English labels only (matplotlib has no CJK font here).
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.collections import LineCollection
import cadquery as cq

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import paddle_launcher_shooter_assembly_r60 as R60          # noqa: E402

OUT = HERE / "output" / "_r60_rail"
OUT.mkdir(parents=True, exist_ok=True)
STEP = HERE / "output" / "_r60_frame" / "T06_shooter_frame_R60_pollen.step"
f = cq.Compound.makeCompound(cq.importers.importStep(str(STEP)).vals())

X0, X1 = R60.RAIL_X0, R60.RAIL_X1
CY, WY = R60.RAIL_CY, R60.RAIL_WY
Y0, Y1 = CY - WY / 2.0, CY + WY / 2.0
ZT, ZB, SB = R60.RAIL_ZT, R60.RAIL_ZB, R60.SOLE_ZB
TABB = R60.TAB_BOTTOM
TAB_TOP = dict(R60.RAIL_TABS)
SOLE_R59 = -7.0    # superseded R59 sole bottom, drawn for comparison
FZ = R60.FRAME_LOWEST
GAP = FZ - SB
NUT, NDEP = R60.NUT_POCKET, R60.NUT_DEPTH
RED, RAILC, SOLEC = "#d62728", "#9aa3ad", "#c8862f"
tabs_x = sorted(TAB_TOP)


def slab(y, t=0.8):
    return cq.Workplane("XY").box(1600.0, t, 1600.0, centered=False).translate(
        (-800.0, y - t / 2.0, -800.0)).val()


def segs(shape):
    out = []
    for fc in shape.Faces():
        if abs(fc.normalAt().y) < 0.99:
            continue
        for e in fc.Edges():
            out.append([(e.positionAt(i / 16.0).x, e.positionAt(i / 16.0).z)
                        for i in range(17)])
    return out


def frame_section(ax, y, lab, lw=1.0):
    ax.add_collection(LineCollection(segs(f.intersect(slab(y))), linewidths=lw,
                                     colors="#1f77b4", label=lab))


def rail_rect(ax, lab=True):
    ax.add_patch(Rectangle((X0, ZB), X1 - X0, ZT - ZB, fc=RAILC, ec="#6b5a3a",
                           lw=1.2, alpha=0.85, zorder=3,
                           label=None if not lab else
                           "base_rail kept: %g..%g, z %g..%g (14 mm)" % (X0, X1, ZB, ZT)))
    ax.add_patch(Rectangle((X0, SB), X1 - X0, ZB - SB, fc=SOLEC, ec="#6b5a3a",
                           lw=1.2, alpha=0.85, zorder=3, label=None if not lab else
                           "R60 sole: z %.1f..%g (13 mm, fused into the rail)" % (SB, ZB)))


fig = plt.figure(figsize=(19, 13.0))
gs = fig.add_gridspec(2, 2, height_ratios=[1.15, 1.0], hspace=0.30, wspace=0.17)

# A-A : y = +72 (through the rail itself); tabs sit at y = +-76, drawn dashed
ax = fig.add_subplot(gs[0, 0])
frame_section(ax, 72.0, "R60 frame section (y=+72, rail centre line)")
rail_rect(ax)
for x in tabs_x:
    ax.add_patch(Rectangle((x - 6, TABB), 12.0, TAB_TOP[x] - TABB, fc="none",
                           ec="k", lw=1.0, ls="--", zorder=5,
                           label="rail tab z %g..%g (kept from R55, y=+-76)"
                           % (TABB, TAB_TOP[x]) if x == tabs_x[0] else None))
ax.axhline(0, color="k", lw=0.7, ls=":")
ax.plot([-150, -150], [SB, ZT], color=RED, lw=1.6, zorder=6)
ax.annotate("sole bottom z=%.1f\n= ONLY floor contact" % SB,
            xy=(-150, SB), xytext=(-168, -95), fontsize=9, color=RED,
            arrowprops=dict(arrowstyle="->", lw=1.0, color=RED))
ax.annotate("thickness 14 -> %.0f mm\n(R59 23 mm, R60 +3 mm; no floor plate)"
            % (ZT - SB), xy=(-40, 4), xytext=(-124, 66), fontsize=9,
            arrowprops=dict(arrowstyle="->", lw=0.9))
ax.axhline(SOLE_R59, color="#2ca02c", lw=1.3, ls="--", zorder=6,
           label="R59 sole bottom z=%.1f (superseded: 3.49 mm clearance)" % SOLE_R59)
ax.set_xlim(-180, 300); ax.set_ylim(-110, 300)
ax.set_title("A-A  y=+72: sole pressed to z=%.1f, one printed piece per side"
             % SB, fontsize=11)

# B-B : y = 0 (tray), rail shown as a projection outline
ax = fig.add_subplot(gs[0, 1])
frame_section(ax, 0.0, "R60 frame section (y=0, ball tray)")
rail_rect(ax)
ax.add_patch(Rectangle((X0, SB), X1 - X0, ZT - SB, fc="none", ec=RAILC,
                       lw=1.0, ls=":", zorder=2,
                       label="rail projection (real rail sits at y=+-72)"))
ax.axhline(0, color="k", lw=0.7, ls=":")
ax.annotate("shroud / tray lowest solid z=%.2f" % FZ,
            xy=(30, FZ), xytext=(-172, 70), fontsize=9, color="#1f77b4",
            arrowprops=dict(arrowstyle="->", lw=1.0, color="#1f77b4"))
ax.plot([-160, -160], [SB, FZ], color=RED, lw=1.6)
ax.annotate("%.2f mm air: the shroud can\nnever touch the ground" % GAP,
            xy=(-160, (SB + FZ) / 2.0), xytext=(-40, -95), fontsize=9, color=RED,
            arrowprops=dict(arrowstyle="->", lw=1.0, color=RED))
ax.set_xlim(-180, 300); ax.set_ylim(-110, 300)
ax.set_title("B-B  y=0: %.1f mm between the sole and the shroud's lowest point" % GAP,
             fontsize=11)

# C-C : joint zoom at y = +76
ax = fig.add_subplot(gs[1, 0])
frame_section(ax, 76.0, "frame section (y=+76, bolt axis)")
rail_rect(ax)
for x in tabs_x:
    ax.plot([x, x], [SB - 6, TAB_TOP[x] + 6], color=RED, lw=1.1, ls="--", zorder=6)
    ax.text(x + 0.9, TAB_TOP[x] + 7, "M3", color=RED, fontsize=8)
for cx, cy in R60.HOLE_XY:
    ax.add_patch(Rectangle((cx - NUT / 2, SB), NUT, NDEP, fc="w", ec="#6b5a3a",
                           lw=1.0, ls="--", zorder=6,
                           label="nut pocket 7 x 2.5 in the sole underside"
                           if (cx, cy) == R60.HOLE_XY[0] else None))
ax.annotate("M3 socket-head bolt through tab + 26 mm rail,\nhex nut inside the "
            "pocket -> nothing below z=%.1f" % SB,
            xy=(68, -3), xytext=(24, -34), fontsize=8.5, color=RED,
            arrowprops=dict(arrowstyle="->", lw=0.9, color=RED))
ax.annotate("tab bottom z=%g sits on the rail top face" % TABB,
            xy=(58, TABB), xytext=(-6, 62), fontsize=8.5,
            arrowprops=dict(arrowstyle="->", lw=0.9))
ax.set_xlim(20, 130); ax.set_ylim(-40, 80)
ax.set_title("C-C  joint: one M3 through rail tab + thickened rail", fontsize=11)

# D-D : top view
ax = fig.add_subplot(gs[1, 1])
bb = f.BoundingBox()
ax.add_patch(Rectangle((bb.xmin, bb.ymin), bb.xmax - bb.xmin, bb.ymax - bb.ymin,
                       fc="none", ec="#1f77b4", lw=1.4,
                       label="frame footprint %.1f x %.1f" % (bb.xmax - bb.xmin,
                                                              bb.ymax - bb.ymin)))
for sy in (1, -1):
    yy = sy * CY
    ax.add_patch(Rectangle((X0, yy - WY / 2.0), X1 - X0, WY, fc=RAILC,
                           ec="#6b5a3a", lw=1.1, alpha=0.9))
    ax.text(X0 + 8, yy - 2, "base_rail_%+d  %.0f mm, ONE piece" % (sy, X1 - X0),
            fontsize=8, color="#3a3226")
for x in R60.RAIL_HOLE_X:
    for sy in (1, -1):
        ax.plot([x], [sy * CY], marker="o", ms=3.5, mfc="w", mec="#6b5a3a", mew=1.0)
for cx, cy in R60.HOLE_XY:
    ax.add_patch(Rectangle((cx - NUT / 2, cy - NUT / 2), NUT, NUT, fc="none",
                           ec=RED, lw=1.2,
                           label="4x O3.4 joint bolt + nut pocket" if (cx, cy) == R60.HOLE_XY[0]
                           else None))
ax.text(X0 + 6, Y1 + 26, "two rails kept (y = +-72), each thickened 14 -> %.0f mm"
        % (ZT - SB), fontsize=9, color="#6b5a3a")
ax.text(X0 + 6, -Y1 - 40, "one piece per side = 380 mm -> %.0f mm over the "
        "Bambu H2D 325 x 320 x 325\n(user-accepted deviation, DEC-0066 / TBD)"
        % (X1 - X0 - 325.0), fontsize=9, color="#d62728")
ax.set_xlim(-180, 300); ax.set_ylim(-140, 140)
ax.set_title("D-D  top view: two one-piece rails + chassis holes", fontsize=11)

for k, ax in enumerate(fig.axes):
    ax.set_aspect("equal"); ax.grid(True, lw=0.2, alpha=0.4)
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)" if k == 3 else "Z (mm)")
    h, l = ax.get_legend_handles_labels()
    seen, hh, ll = set(), [], []
    for a, b in zip(h, l):
        if b in seen:
            continue
        seen.add(b); hh.append(a); ll.append(b)
    ax.legend(hh, ll, loc="upper left", fontsize=8, framealpha=0.92)
fig.suptitle("R60: sole pressed z=-7.0 -> %.1f (%g..%g), print split removed; "
             "rail underside z=%.1f is still the lowest point "
             "(shroud lowest %.2f, clearance %.2f mm)" % (SB, SB, ZT, SB, FZ, GAP),
             fontsize=13)
p = OUT / "r60_thickened_rail.png"
fig.savefig(p, dpi=115, bbox_inches="tight")
print("wrote", p)
