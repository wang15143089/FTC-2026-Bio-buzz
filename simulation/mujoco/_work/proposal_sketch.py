"""Concept section: replace the flat roof panels with a circular guide around the paddle."""
from __future__ import annotations
import math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
OUT = Path(__file__).resolve().parent.parent / "out"
import pollen_launcher_sim as P

CX, CZ = P.PADDLE_CENTER[0], P.PADDLE_CENTER[2]
RB = 58.4                      # ball-centre carry radius (= throat centre radius)
SHROUD = RB + P.BALL_R         # outer curved guide radius
FLOOR_TOP = 17.5
BALL_Z = FLOOR_TOP + P.BALL_R
THROAT = (-30.81, 129.13)
NIP = (P.SHOOTER_ORIGIN[0], P.SHOOTER_ORIGIN[2])
A_IN, A_OUT = 200.0, 73.9

fig, ax = plt.subplots(figsize=(11, 10))

# existing throat / launcher
T = math.radians(52.0)
for k in (0.0,):
    for n in (-55.0, 55.0):
        c = (NIP[0] - 135 * math.cos(T) + n * -math.sin(T),
             NIP[1] - 135 * math.sin(T) + n * math.cos(T))
        ax.plot([c[0] - 42 * math.cos(T), c[0] + 42 * math.cos(T)],
                [c[1] - 42 * math.sin(T), c[1] + 42 * math.sin(T)],
                color="#2b6a91", lw=2.0, zorder=2)
for (fx, fz), r in (((P.SHOOTER_ORIGIN[0] + 63 * math.sin(T), P.SHOOTER_ORIGIN[2] - 63 * math.cos(T)), 48.0),
                    ((P.SHOOTER_ORIGIN[0] - 63 * math.sin(T), P.SHOOTER_ORIGIN[2] + 63 * math.cos(T)), 48.0)):
    ax.add_patch(Circle((fx, fz), r, fill=False, ec="#222", lw=1.6, zorder=2))
    ax.plot([fx], [fz], "+", color="#222", ms=9, zorder=3)
ax.annotate("夹口 nip", NIP, textcoords="offset points", xytext=(8, 6), fontsize=10)

# flat tray
ax.plot([-150, -104], [FLOOR_TOP, FLOOR_TOP], color="#2b6a91", lw=6, alpha=0.85, zorder=2)
ax.annotate("0° 平托板", (-148, FLOOR_TOP), textcoords="offset points", xytext=(0, -22),
            fontsize=10, color="#2b6a91")

# paddle
ax.add_patch(Circle((CX, CZ), 60, fill=False, ec="#c8610f", lw=1.4, ls="--", zorder=2))
ax.add_patch(Circle((CX, CZ), 18, fill=False, ec="#c8610f", lw=1.8, zorder=2))
ax.plot([CX], [CZ], "+", color="#c8610f", ms=11, zorder=3)
ax.annotate("拨杆轴", (CX, CZ), textcoords="offset points", xytext=(12, -30), fontsize=10, color="#c8610f")

# new circular guide: outer shroud + ball-centre track
ts = [math.radians(a) for a in [A_IN - (A_IN - A_OUT) * i / 240 for i in range(241)]]
ax.plot([CX + SHROUD * math.cos(t) for t in ts], [CZ + SHROUD * math.sin(t) for t in ts],
        color="#1f7a3d", lw=3.0, zorder=3)
ax.plot([CX + RB * math.cos(t) for t in ts], [CZ + RB * math.sin(t) for t in ts],
        color="#1f7a3d", lw=1.2, ls=":", zorder=3)

# ball-centre path: flat tray then arc
ax.plot([-150, CX + RB * math.cos(math.radians(A_IN))], [BALL_Z, BALL_Z],
        color="#d62728", lw=2.4, zorder=4)
ax.plot([CX + RB * math.cos(t) for t in ts], [CZ + RB * math.sin(t) for t in ts],
        color="#d62728", lw=2.4, zorder=4)
ax.plot([THROAT[0], NIP[0]], [THROAT[1], NIP[1]], color="#d62728", lw=2.4, zorder=4)

ax.add_patch(Circle((CX + RB * math.cos(math.radians(A_IN)), CZ + RB * math.sin(math.radians(A_IN))),
                    P.BALL_R, fill=False, ec="#d62728", lw=1.2, zorder=5))
ax.add_patch(Circle(THROAT, P.BALL_R, fill=False, ec="#d62728", lw=1.2, ls="--", zorder=5))
ar = math.radians(120.0)
ax.annotate("", xy=(CX + RB * math.cos(ar + 0.25), CZ + RB * math.sin(ar + 0.25)),
            xytext=(CX + RB * math.cos(ar), CZ + RB * math.sin(ar)),
            arrowprops=dict(arrowstyle="-|>", color="#d62728", lw=2.4), zorder=6)
ax.annotate("球心轨迹（改后）", (CX + RB * math.cos(math.radians(150)), CZ + RB * math.sin(math.radians(150))),
            textcoords="offset points", xytext=(-118, 26), fontsize=10, color="#d62728",
            arrowprops=dict(arrowstyle="->", color="#d62728", lw=1.2))
ax.annotate("外罩：绕拨杆轴的圆柱面\nR = 58.4+35.6 = 94 mm", (CX - SHROUD, CZ + 6),
            textcoords="offset points", xytext=(-124, 40), fontsize=10, color="#1f7a3d",
            arrowprops=dict(arrowstyle="->", color="#1f7a3d", lw=1.2))
ax.annotate("入口用曲面从平托板\n平滑过渡到圆弧道", (-104, FLOOR_TOP + 8),
            textcoords="offset points", xytext=(-30, -58), fontsize=10, color="#1f7a3d",
            arrowprops=dict(arrowstyle="->", color="#1f7a3d", lw=1.2))

ax.set_xlim(-230, 190); ax.set_ylim(-20, 330)
ax.set_aspect("equal"); ax.grid(alpha=0.3)
ax.set_xlabel("X [mm]"); ax.set_ylabel("Z [mm]")
ax.set_title("T06 POLLEN 送球段改法：取消平板顶盖，改成绕拨杆轴的圆弧导槽", fontsize=13)
fig.tight_layout()
fig.savefig(OUT / "proposal_curved_guide.png", dpi=130)
print("saved", OUT / "proposal_curved_guide.png")
