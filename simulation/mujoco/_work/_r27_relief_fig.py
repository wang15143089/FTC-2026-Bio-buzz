# -*- coding: utf-8 -*-
"""R27 shared-shell relief figure: what was cut away, and where.

Left  : 3-D view of the relief context (shell after relief + the two kept parent
        parts that used to run through it).
Right : the same model sliced at mid width (y ~ 0) and projected on X-Z, with the
        ball track arcs overlaid so it is obvious the notch never touches it.
"""
import sys, math, json
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Circle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import cadquery as cq

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

AX, AZ = 29.49, 111.46
R_IN = 107.974
WALL = 7.0
A_EXIT, A_LIP = 142.0, 275.0
GREEN, RED, ORANGE, BLUE = "#2e8b3d", "#d62728", "#eb8a1e", "#1f77b4"

SRC = Path("cad/output/inspection/_r27_shared_relief_context.step")
NECT = json.loads(Path("cad/output/paddle_launcher_feeder_a_prime_shared_report_nectar.json")
                  .read_text(encoding="utf-8"))["variants"]["nectar"]
relief = NECT["shell_relief"]

wp = cq.importers.importStep(str(SRC))
solids = [s for s in wp.solids().vals()]
solids.sort(key=lambda s: s.Volume(), reverse=True)
shell = solids[0]
others = solids[1:]
print("solids:", [round(s.Volume(), 1) for s in solids], flush=True)


def tris(shape, tol=0.4):
    v, f = shape.tessellate(tol)
    return np.array([[p.x, p.y, p.z] for p in v]), np.array(f)


def slab(shape, half=0.6):
    box = cq.Solid.makeBox(600, 2 * half, 600, cq.Vector(-300 + AX, -half, -300 + AZ))
    return shape.intersect(box)


fig = plt.figure(figsize=(17.0, 8.6))
fig.suptitle("T06 共用送球段 R27：外罩让位（挖去与保留父级结构重叠的料，球道不受影响）",
             fontsize=15, y=0.975)

# ---- (a) 3-D -------------------------------------------------------------
ax = fig.add_subplot(1, 2, 1, projection="3d")
for shape, col, alpha in [(shell, GREEN, 0.55)] + [(s, RED if i == 0 else ORANGE, 0.75)
                                                  for i, s in enumerate(others)]:
    v, f = tris(shape, 1.0)
    pc = Poly3DCollection(v[f], facecolor=col, edgecolor="none", alpha=alpha)
    ax.add_collection3d(pc)
allv = np.vstack([tris(s, 2.0)[0] for s in [shell] + others])
c = allv.mean(axis=0); r = (allv.max(axis=0) - allv.min(axis=0)).max() / 2
ax.set_xlim(c[0]-r, c[0]+r); ax.set_ylim(c[1]-r, c[1]+r); ax.set_zlim(c[2]-r, c[2]+r)
ax.set_box_aspect((1, 1, 1))
ax.view_init(elev=26, azim=-58)
ax.set_xlabel("X (mm)"); ax.set_ylabel("Y (mm)"); ax.set_zlabel("Z (mm)")
ax.set_title("(a) 让位上下文（3D）\n绿=让位后的外罩  红=shooter_throat_+55  橙=guide_roof_3",
             fontsize=12)
ax.text2D(0.02, 0.86, "让位量：throat %(a).1f mm³ / roof %(b).1f mm³\n让位间隙 %(c).1f mm" % {
    "a": relief["relief_targets_removed_mm3"].get("shooter_throat_+55", 0.0),
    "b": relief["relief_targets_removed_mm3"].get("guide_roof_3", 0.0),
    "c": max(relief["relief_clearance_mm"].values())}, transform=ax.transAxes, fontsize=11)

# ---- (b) section ---------------------------------------------------------
ax = fig.add_subplot(1, 2, 2)
for shape, col, alpha in [(shell, GREEN, 0.30)] + [(s, RED if i == 0 else ORANGE, 0.45)
                                                   for i, s in enumerate(others)]:
    cut = slab(shape)
    if cut is None or cut.Volume() <= 0:
        continue
    for solid in cut.Solids():
        v, f = tris(solid, 0.3)
        for tri in v[f]:
            ax.fill(tri[:, 0], tri[:, 2], color=col, alpha=alpha, lw=0)
th = np.linspace(A_EXIT, A_LIP, 240)
for rr, ls, lab in [(R_IN, "-", "球道内弧 r=107.974（球外表面极限）"),
                    (R_IN + WALL, "--", "外罩外弧 r=114.974")]:
    ax.plot(AX + rr*np.cos(np.radians(th)), AZ + rr*np.sin(np.radians(th)),
            color=BLUE, ls=ls, lw=1.8, label=lab)
for a in (A_EXIT, A_LIP):
    p = (AX + R_IN*math.cos(math.radians(a)), AZ + R_IN*math.sin(math.radians(a)))
    q = (AX + (R_IN+WALL)*math.cos(math.radians(a)), AZ + (R_IN+WALL)*math.sin(math.radians(a)))
    ax.plot([p[0], q[0]], [p[1], q[1]], color=BLUE, lw=1.4)
ax.text(AX + R_IN*math.cos(math.radians(A_LIP)) - 6, AZ + R_IN*math.sin(math.radians(A_LIP)) + 6,
        "唇口 275°", fontsize=10, color=BLUE)
ax.text(AX + R_IN*math.cos(math.radians(A_EXIT)) + 4, AZ + R_IN*math.sin(math.radians(A_EXIT)) - 8,
        "出口 142°", fontsize=10, color=BLUE)
ax.add_patch(Circle((AX, AZ), 12.0, color="#b9bec6"))
ax.set_aspect("equal")
ax.set_title("(b) 中截面（y≈0）俯视：让位都发生在 r > 108 的球道外侧", fontsize=12)
ax.set_xlabel("X (mm)"); ax.set_ylabel("Z (mm)")
ax.grid(alpha=0.25); ax.legend(fontsize=10, loc="lower right")
ax.text(0.02, 0.97,
        "外罩体积 267723.3 → %(v).1f mm³（削掉 %(d).1f mm³）\n让位后 外罩∩throat = 外罩∩roof = 0 mm³\n球道扫描 19 点：球∩外罩 = 0 mm³" % {
            "v": relief["shell_volume_after_mm3"], "d": relief["shell_volume_removed_mm3"]},
        transform=ax.transAxes, fontsize=10.5, va="top",
        bbox=dict(fc="white", ec="#cccccc", alpha=0.85, pad=3.0))

out = "cad/output/_t06_shared_relief_r27_zh.png"
fig.savefig(out, dpi=115, bbox_inches="tight")
print("saved", out, flush=True)
