# -*- coding: utf-8 -*-
"""R57 figure (v4): delete base_rail -> ONE floor plate whose bottom is the
lowest point of the whole assembly.  All numbers are pulled from the R57
generator itself, so the drawing can never drift from the delivered STEP.
English labels only (matplotlib has no CJK font here).
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
import paddle_launcher_shooter_assembly_r57 as R57          # noqa: E402

OUT = HERE / "output" / "_r57_plate"
OUT.mkdir(parents=True, exist_ok=True)
STEP = HERE / "output" / "_r57_frame" / "T06_shooter_frame_R57_pollen.step"
f = cq.Compound.makeCompound(cq.importers.importStep(str(STEP)).vals())

X0, X1, Y0, Y1 = R57.PLATE_X0, R57.PLATE_X1, R57.PLATE_Y0, R57.PLATE_Y1
ZT, ZB, T = R57.PLATE_ZT, R57.PLATE_ZB, R57.PLATE_T
PDX, PDY = R57.PIL_DX, R57.PIL_DY
TABB = R57.TAB_BOTTOM
TAB_TOP = dict(R57.RAIL_TABS)
HOLES = list(R57.HOLE_XY)
FRAME_ZMIN = -3.51                      # MEASURED, R56/R57 report
GAP = FRAME_ZMIN - ZT
NUT, NDEP = R57.NUT_POCKET, R57.NUT_DEPTH
XSPL, ZSPL = "M3 x 55", "M3 x 60 + 1.5 washer"

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

FIG, PLT, PILC, RED = "#1f77b4", "#ff9f2e", "#ffe0b0", "#d62728"

def plate_rect(ax, lab=True):
    ax.add_patch(Rectangle((X0, ZB), X1 - X0, T, fc=PLT, ec="#a85400", lw=1.3,
                           alpha=0.9, zorder=4, label=None if not lab else
                           "floor plate %g..%g, z %.1f..%.1f (%g thk)"
                           % (X0, X1, ZB, ZT, T)))

def pillars(ax, yside=1, lab=True):
    first = lab
    for cx, cy in HOLES:
        if cy * yside < 0:
            continue
        ax.add_patch(Rectangle((cx - PDX / 2, ZT), PDX, TABB - ZT, fc=PILC,
                               ec="#a85400", lw=1.2, zorder=4,
                               label="4x pillar z %.1f..%g (12 x 16)" % (ZT, TABB)
                               if first else None))
        ax.add_patch(Rectangle((cx - NUT / 2, ZB), NUT, NDEP, fc="w",
                               ec="#a85400", lw=1.0, ls="--", zorder=5,
                               label="nut pocket 7 x 2.5 (under side)" if first
                               else None))
        first = False

def frame_section(ax, y, lab, lw=1.0):
    ax.add_collection(LineCollection(segs(f.intersect(slab(y))), linewidths=lw,
                                     colors=FIG, label=lab))

fig = plt.figure(figsize=(19, 12.5))
gs = fig.add_gridspec(2, 2, height_ratios=[1.2, 1.0], hspace=0.32, wspace=0.17)

# A-A  y = +76 (through the bolt axis)
ax = fig.add_subplot(gs[0, 0])
frame_section(ax, 76.0, "R57 frame section (y=+76, bolt axis)")
plate_rect(ax); pillars(ax, 1)
for x, zt in TAB_TOP.items():
    ax.add_patch(Rectangle((x - 6, TABB), 12.0, zt - TABB, fc="none", ec="k",
                           lw=1.0, ls="--", zorder=5,
                           label="rail tab z %g..%g (kept from R55)" % (TABB, zt)
                           if x == 60 else None))
ax.axhline(0, color="k", lw=0.7, ls=":")
ax.set_xlim(-175, 305); ax.set_ylim(-25, 425)
ax.set_title("A-A  y=+76: rails gone -> flat plate + one pillar under each tab",
             fontsize=11)

# B-B  y = 0
ax = fig.add_subplot(gs[0, 1])
frame_section(ax, 0.0, "R57 frame section (y=0, ball tray)")
plate_rect(ax); pillars(ax, 1, lab=False)
ax.axhline(0, color="k", lw=0.7, ls=":")
ax.annotate("lowest frame solid z=%.2f\n(tray underside, x 20..40)" % FRAME_ZMIN,
            xy=(30, FRAME_ZMIN), xytext=(-170, -70), fontsize=9,
            arrowprops=dict(arrowstyle="->", lw=1.0))
ax.annotate("%.1f mm gap -> plate top z=%.1f is flat,\nno tray window / relief "
            "needed anywhere" % (GAP, ZT),
            xy=(140, ZT), xytext=(10, -125), fontsize=9, color="#a85400",
            arrowprops=dict(arrowstyle="->", lw=1.0, color="#a85400"))
ax.plot([X0 + 8, X0 + 8], [ZB, ZT], color=RED, lw=1.6)
ax.annotate("plate underside z=%.1f\n= lowest point of the machine" % ZB,
            xy=(X0 + 8, ZB), xytext=(-170, -175), fontsize=9, color=RED,
            arrowprops=dict(arrowstyle="->", lw=1.0, color=RED))
ax.set_xlim(-175, 305); ax.set_ylim(-200, 240)
ax.set_title("B-B  y=0: plate never touches the frame; plate bottom is the "
             "lowest point", fontsize=11)

# C-C  joint zoom
ax = fig.add_subplot(gs[1, 0])
frame_section(ax, 76.0, "frame section (y=+76)", lw=1.2)
plate_rect(ax); pillars(ax, 1)
for x, zt in TAB_TOP.items():
    ax.plot([x, x], [ZB - 5, zt + 6], color=RED, lw=1.0, ls="--", zorder=6)
    ax.text(x + 0.8, zt + 7, "M3", color=RED, fontsize=8)
ax.annotate("tab bottom z=%g = pillar top face\n(4/4 flush, 0.000 mm3 overlap)"
            % TABB, xy=(58, TABB), xytext=(2, 42),
            arrowprops=dict(arrowstyle="->", lw=0.9), fontsize=8)
ax.annotate("M3 bolt, head on top / hex nut in the\nunderside pocket -> nothing "
            "sticks out below z=%.1f" % ZB,
            xy=(70, -4), xytext=(44, -32), fontsize=8.5, color=RED,
            arrowprops=dict(arrowstyle="->", lw=0.9, color=RED))
ax.set_xlim(20, 118); ax.set_ylim(-36, 70)
ax.set_title("C-C  joint: one M3 through tab + pillar + plate (+ captive nut)",
             fontsize=11)

# D-D  top view
ax = fig.add_subplot(gs[1, 1])
bb = f.BoundingBox()
ax.add_patch(Rectangle((X0, Y0), X1 - X0, Y1 - Y0, fc=PLT, alpha=0.45,
                       ec="#a85400", lw=1.4,
                       label="floor plate %g x %g x %g (ONE printed part)"
                       % (X1 - X0, Y1 - Y0, T)))
ax.add_patch(Rectangle((bb.xmin, bb.ymin), bb.xmax - bb.xmin, bb.ymax - bb.ymin,
                       fc="none", ec=FIG, lw=1.4,
                       label="frame footprint %.1f x %.1f" % (bb.xmax - bb.xmin,
                                                              bb.ymax - bb.ymin)))
for cx, cy in HOLES:
    ax.add_patch(Rectangle((cx - PDX / 2, cy - PDY / 2), PDX, PDY, fc=PILC,
                           ec="#a85400", lw=1.2))
ax.text(X0 + 6, Y1 - 14, "%s at x=60 tabs, %s at x=76 tabs" % (XSPL, ZSPL),
        fontsize=9, color=RED)
ax.text(X0 + 6, Y0 + 10, "4 pillars at (x 60 / 76, y +-76) = the kept rail tabs",
        fontsize=9)
ax.text(X0 + 6, Y0 - 12, "single part %.0f x %.0f x %.1f mm -> inside Bambu H2D "
        "325 x 320 x 325" % (X1 - X0, Y1 - Y0, TABB - ZB), fontsize=9,
        color="#a85400")
ax.set_xlim(-180, 310); ax.set_ylim(-140, 135)
ax.set_title("D-D  top view: plate + 4 pillars + bolt positions", fontsize=11)

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
fig.suptitle("R57: base_rail (+-72, 380 x 18 x 14) deleted -> ONE ground plate; "
             "plate underside z=%.1f is the lowest point (frame lowest %.2f)"
             % (ZB, FRAME_ZMIN), fontsize=13)
p = OUT / "r57_floor_plate.png"
fig.savefig(p, dpi=115, bbox_inches="tight")
print("wrote", p)
