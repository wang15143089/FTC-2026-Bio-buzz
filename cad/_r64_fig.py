# -*- coding: utf-8 -*-
"""R64: schematic of the x=-40 rail split and where each piece is fastened."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrow

D = Path("cad/output/_r64_joint"); D.mkdir(parents=True, exist_ok=True)
SPLIT = -40.0
RAIL_Z = (-10.0, 16.0)
CH_REAR = [-150.0, -102.0, -54.0]
CH_FRONT = [-6.0, 42.0, 90.0, 138.0, 186.0]
TAB_X = [60.0, 76.0]
TAB_TOP = {60.0: 44.0, 76.0: 48.0}
RIBS = [-160.0, -125.0, -90.0, -55.0]

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 9.6),
                               gridspec_kw={"height_ratios": [1, 1.15]})

# ---------------- (1) XZ elevation, looking along -Y at the +72 rail -----------
ax1.add_patch(Rectangle((-170, RAIL_Z[0]), 130, 26, fc="#c9d8f0", ec="k", lw=1.4))
ax1.add_patch(Rectangle((SPLIT, RAIL_Z[0]), 250, 26, fc="#f6c9c0", ec="k", lw=1.4))
ax1.text(-105, 3, "rear_joined\nx[-170,-40]\n6 x O4.6 chassis holes",
         ha="center", va="center", fontsize=7.5)
ax1.text(60, 3, "front_+72   x[-40,210]   5 x O4.6", ha="center", va="center", fontsize=8)
ax1.plot([SPLIT, SPLIT], [-16, 60], color="k", ls="--", lw=1.6)
ax1.text(SPLIT - 2, 62, "split plane x = -40.0   (flat butt, 18x26 = 468 mm2 per rail)",
         fontsize=8, ha="left", color="k")

# frame above: only over the FRONT piece
ax1.add_patch(Rectangle((-3.51 + 4, 16), 0, 0, fc="none"))   # spacer no-op
ax1.add_patch(Rectangle((SPLIT, 16), 250, 30, fc="#d6f0d0", ec="g", lw=1.2, alpha=0.55,
                        hatch="//"))
ax1.text(120, 31, "frame sits on the rail top ONLY here (1763 mm3 per side)",
         ha="center", va="center", fontsize=8, color="darkgreen")
ax1.add_patch(Rectangle((-170, 16), 130, 30, fc="#ffe9a8", ec="orange", lw=1.2, alpha=0.55,
                        hatch="\\\\"))
ax1.text(-105, 33, "frame has 0 material above\nand 0 contact here", ha="center", va="center",
         fontsize=8, color="#a05000")

# tab joints (front piece only)
for x in TAB_X:
    ax1.plot([x, x], [RAIL_Z[0] - 4, TAB_TOP[x] + 6], color="#b00000", lw=1.4)
    ax1.plot([x - 2.2, x + 2.2], [TAB_TOP[x], TAB_TOP[x]], color="#b00000", lw=2)
    ax1.plot([x - 2.2, x + 2.2], [RAIL_Z[0], RAIL_Z[0]], color="#b00000", lw=2)
    ax1.text(x, TAB_TOP[x] + 8, "M3 x2", ha="center", fontsize=7, color="#b00000")
# chassis holes
for x in CH_REAR + CH_FRONT:
    ax1.plot([x, x], [RAIL_Z[0], RAIL_Z[1]], color="0.35", ls=":", lw=1.0)
for x in CH_REAR:
    ax1.plot(x, -13, marker="v", color="#0a58ca", ms=5)
ax1.text(-150, -19, "O4.6 down-mount (nothing above, nothing below) -> only ties to an external chassis",
         fontsize=7.5, color="#0a58ca", ha="left")
ax1.set_xlim(-190, 250); ax1.set_ylim(-26, 72)
ax1.set_aspect("equal"); ax1.set_xlabel("X [mm]"); ax1.set_ylabel("Z [mm]")
ax1.set_title("Side elevation of the +72 rail after the split (frame shown as hatched band)",
              fontsize=10)

# ---------------- (2) XY plan -------------------------------------------------
ax2.add_patch(Rectangle((-170, 63), 130, 18, fc="#c9d8f0", ec="k", lw=1.2))
ax2.add_patch(Rectangle((SPLIT, 63), 250, 18, fc="#f6c9c0", ec="k", lw=1.2))
ax2.add_patch(Rectangle((-170, -81), 130, 18, fc="#c9d8f0", ec="k", lw=1.2))
ax2.add_patch(Rectangle((SPLIT, -81), 250, 18, fc="#f6c9c0", ec="k", lw=1.2))
for x in RIBS:
    ax2.add_patch(Rectangle((x - 5, -66), 10, 132, fc="#8fb3e0", ec="k", lw=0.8, alpha=0.85))
ax2.plot([SPLIT, SPLIT], [-95, 110], color="k", ls="--", lw=1.8)
ax2.text(SPLIT - 3, 112, "x = -40.0", fontsize=9, ha="right")
for x in CH_REAR + CH_FRONT:
    ax2.plot([x, x], [72, 72], marker="o", mfc="none", mec="0.3", ms=6)
    ax2.plot([x, x], [-72, -72], marker="o", mfc="none", mec="0.3", ms=6)
for x in TAB_X:
    ax2.plot([x, x], [76, -76], marker="x", color="#b00000", ms=8, mew=2, ls="none")
    ax2.text(x + 4, 88, "M3", fontsize=7.5, color="#b00000")
ax2.text(-105, 0, "REAR joined piece\n4 ribs join L+R rails\nNO M3 tab joint\nframe contact 0 mm3",
         ha="center", va="center", fontsize=8.5, color="#0a2f66")
ax2.text(150, 0, "two FRONT bars\n4 x M3 rail-tab joints (x=60/76, y=+/-76)\nframe contact 1763 mm3 per side",
         ha="center", va="center", fontsize=8.5, color="#8a2f22")
ax2.set_xlim(-200, 250); ax2.set_ylim(-108, 128)
ax2.set_aspect("equal"); ax2.set_xlabel("X [mm]"); ax2.set_ylabel("Y [mm]")
ax2.set_title("Plan: O = O4.6 chassis hole, X = M3 rail-tab joint (frame -> rail)", fontsize=10)
fig.tight_layout(); fig.savefig(D / "r64_split_fastening_schematic.png", dpi=165)
print("wrote", D / "r64_split_fastening_schematic.png")

json.dump({
  "units": "mm",
  "question": "after the x=-40 split, can the 3 rail pieces be assembled and stay together?",
  "split_plane_x": SPLIT,
  "seam": {"kind": "flat butt joint, no tongue / no lap / no cross bolt",
           "rail_section_mm2": 468.0, "faces_all_at_x": -40.0},
  "frame_contact_on_rail_top_z16_22_mm3": {"rear_+72": 0.0, "rear_-72": 0.0,
                                           "front_+72": 1763.05, "front_-72": 1763.05},
  "m3_rail_tab_joints": [{"x": 60.0, "y": 76.0, "piece": "base_rail_front_+72"},
                         {"x": 60.0, "y": -76.0, "piece": "base_rail_front_-72"},
                         {"x": 76.0, "y": 76.0, "piece": "base_rail_front_+72"},
                         {"x": 76.0, "y": -76.0, "piece": "base_rail_front_-72"}],
  "chassis_holes_O4.6": {"rear_joined": [-150.0, -102.0, -54.0],
                         "front_+72": CH_FRONT, "front_-72": CH_FRONT,
                         "frame_material_above_any_of_them_mm3": 0.0},
  "rear_piece_frame_intersection_mm3": 0.0,
  "conclusion": "each piece lands correctly (seam flush) but the rear joined piece has "
                "no fastener to the frame; its 6 O4.6 holes have neither frame material "
                "above nor support below, so it can only be tied to an external chassis.",
}, open(D / "r64_split_fastening.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("wrote", D / "r64_split_fastening.json")
