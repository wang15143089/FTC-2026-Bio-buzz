# -*- coding: utf-8 -*-
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly
from matplotlib.collections import PatchCollection
import cadquery as cq

OUT = Path("cad/output/_r60_frame")
rep = json.loads((OUT / "report_r60_pollen.json").read_text(encoding="utf-8"))
src = OUT / rep["print_set_step"]["file"]
rd = cq.importers.importStep(str(src))

def fam(n):
    if n.startswith("shooter_frame"): return "frame (merged, 1)"
    if n.startswith("base_rail"):     return "base rail (2)"
    if n.startswith("bearing_carriage"): return "bearing carriage (4)"
    if n.startswith("carriage_clamp_seat"): return "clamp seat (16)"
    if n.startswith("carriage_link_spacer"): return "link spacer (2)"
    if n.startswith("crosshead_guide"): return "crosshead guide/stop (4)"
    if n.startswith("crosshead"): return "crosshead (1)"
    if n.startswith("gap_servo_standoff"): return "servo standoff (4)"
    if n.startswith("main_spacing_link"): return "spacing link (2)"
    if n.startswith("motor_bridge"): return "motor bridge (4)"
    if n.startswith(("paddle_rotor", "paddle_flex_tip")): return "paddle rotor+tip (3)"
    if n.startswith(("servo_crank", "servo_drag_link")): return "servo crank+drag (2)"
    return "other"

solids = rd.val().Solids()
# name lookup: STEP export used named bodies; importStep flattens -> use report order
names = rep["print_set_step"]["parts"]
assert len(names) == len(solids), (len(names), len(solids))

fams = []
for n in names:
    f = fam(n)
    if f not in fams: fams.append(f)
cmap = plt.get_cmap("tab20")
col = {f: cmap(i % 20) for i, f in enumerate(fams)}

groups = {}
for n, s in zip(names, solids):
    groups.setdefault(fam(n), []).append(s)

fig, axes = plt.subplots(1, 3, figsize=(21, 8))
views = [("Top  (X-Y projection)", 0, 1), ("Front (X-Z projection)", 0, 2), ("Side (Y-Z projection)", 1, 2)]
for ax, (title, i1, i2) in zip(axes, views):
    for f, ss in groups.items():
        polys = []
        for s in ss:
            vs, ts = s.tessellate(1.5)
            P = np.array([[v.x, v.y, v.z] for v in vs])
            for t in ts:
                polys.append(P[np.asarray(t, dtype=int)][:, [i1, i2]])
        pc = PatchCollection([MPoly(p, closed=True) for p in polys],
                             facecolor=col[f], edgecolor="none", alpha=0.95)
        ax.add_collection(pc)
    ax.autoscale_view()
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=13)
    ax.grid(True, lw=0.3, alpha=0.4)
    ax.set_xlabel(["X (mm)", "Y (mm)", "Y (mm)"][ [0,1,2].index(i1) ] if False else "mm")
axes[0].set_xlabel("X (mm)"); axes[0].set_ylabel("Y (mm)")
axes[1].set_xlabel("X (mm)"); axes[1].set_ylabel("Z (mm)")
axes[2].set_xlabel("Y (mm)"); axes[2].set_ylabel("Z (mm)")

handles = [plt.Line2D([], [], marker="s", ls="", ms=11, color=col[f], label=f) for f in fams]
fig.legend(handles=handles, loc="lower center", ncol=5, fontsize=10, frameon=False)
fig.suptitle("R60B print set - %d bodies, V = %.1f mm3, 3.08 MB STEP (COTS excluded)"
             % (len(names), sum(s.Volume() for s in solids)), fontsize=15)
fig.tight_layout(rect=[0, 0.10, 1, 0.95])
dst = Path("cad/output/_r60_frame/sections/r60b_print_set_45.png")
fig.savefig(dst, dpi=130)
print("saved", dst, dst.stat().st_size / 1e3, "KB")
