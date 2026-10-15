# -*- coding: utf-8 -*-
"""R56 split figures: two X-Z sections, coloured by printed piece."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from pathlib import Path
import cadquery as cq

SPL = Path("cad/output/_r56_frame/split")
NAMES = ["frameP_1_rear_lower", "frameP_2_front_lower", "frameP_3_top"]
COL = {"frameP_1_rear_lower": "#1f77b4", "frameP_2_front_lower": "#d62728",
       "frameP_3_top": "#2ca02c"}
LBL = {"frameP_1_rear_lower": "P1 rear chassis (x<=100, z<=300)",
       "frameP_2_front_lower": "P2 front tray kit (x>=100, z<=300)",
       "frameP_3_top": "P3 upper plates (z>=300)"}

def slab(y, t=0.8):
    return cq.Workplane("XY").box(1200.0, t, 1200.0, centered=False).translate(
        (-600.0, y - t / 2.0, -600.0)).val()

def segs(shape):
    out = []
    for f in shape.Faces():
        n = f.normalAt()
        if abs(n.y) < 0.99:
            continue
        for e in f.Edges():
            out.append([(e.positionAt(i / 16.0).x, e.positionAt(i / 16.0).z)
                        for i in range(17)])
    return out

fig, axes = plt.subplots(1, 2, figsize=(20, 9))
for ax, (y, title) in zip(axes, ((70.0, "y = 70 mm  (through both side plates: seams + M3 holes"),
                                 (0.0, "y = 0 mm  (through the ball tray: tray lap)"))):
    s = slab(y)
    for n in NAMES:
        sh = cq.importers.importStep(str(SPL / ("%s.step" % n))).val().intersect(s)
        g = segs(sh)
        if g:
            ax.add_collection(LineCollection(g, linewidths=1.1, colors=COL[n], label=LBL[n]))
    ax.axvline(100.0, ls="--", lw=1.0, color="k")
    ax.axhline(300.0, ls="--", lw=1.0, color="k")
    ax.set_aspect("equal"); ax.grid(True, linewidth=0.2, alpha=0.4)
    ax.set_xlabel("X (mm)"); ax.set_ylabel("Z (mm)"); ax.set_title(title, fontsize=11)
    ax.autoscale_view()
axes[0].legend(loc="lower left", fontsize=9)
fig.suptitle("T06 R56 print split for Bambu Lab H2D (325x320x325): 2 planes -> 8 printable lumps, "
             "largest 247.6 mm", fontsize=12)
fig.tight_layout()
fig.savefig("cad/output/_r56_frame/split/r56_split_sections.png", dpi=130)
print("wrote r56_split_sections.png")
