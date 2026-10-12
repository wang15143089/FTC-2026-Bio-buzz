# -*- coding: utf-8 -*-
import math, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False
T = math.radians(5.0); ct, st = math.cos(T), math.sin(T)
c_ = (ct, st); n_ = (-st, ct)
S = 42.0; CUT = 38.901; CLEAR = 3.0; HF = 22.0; HP = 50.0; NIP = 53.0
GPX = CUT + S*ct; GPZ = 0.423 + (CUT + 0.806)*math.tan(T) + S*st
RB = 45.97
trayz = lambda x: 0.423 + (x + 0.806)*math.tan(T)
plt.figure(figsize=(13.5, 6.2))

def frame(ax, title):
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.set_xlim(-25, 200); ax.set_ylim(-18, 112)
    ax.set_aspect("equal"); ax.grid(alpha=0.22, lw=0.5)
    ax.set_xlabel("x (mm)    下游(发射部分) ←", fontsize=9); ax.set_ylabel("z (mm)", fontsize=9)
    ax.plot([-18, 192], [trayz(-18), trayz(192)], color="0.4", lw=7, solid_capstyle="butt", zorder=1)
    ax.text(160, trayz(160) + 3, "托板 5°", fontsize=8, color="0.35")

def plank(ax, p0, p1, col, ls="-"):
    d = (p1[0]-p0[0], p1[1]-p0[1]); L = math.hypot(*d); n = (-d[1]/L, d[0]/L); w = 2.4
    ax.add_patch(Polygon([[p0[0], p0[1]], [p1[0], p1[1]],
                          [p1[0]-w*n[0], p1[1]-w*n[1]], [p0[0]-w*n[0], p0[1]-w*n[1]]],
                         closed=True, fc=col, ec="k", lw=0.9, ls=ls,
                         alpha=1.0 if ls == "-" else 0.5, zorder=4))

ax = plt.subplot(1, 2, 1)
frame(ax, "B1 弹性片 k=0.02（zip-tie）：摆开 18.1° 后片体自己成了 72° 斜坡")
pb = (GPX + CLEAR*n_[0], GPZ + CLEAR*n_[1])
th = math.radians(18.1)
tip = (pb[0] + HF*(math.sin(th)*c_[0] + math.cos(th)*n_[0]),
       pb[1] + HF*(math.sin(th)*c_[1] + math.cos(th)*n_[1]))
plank(ax, pb, tip, "#4fb87a")
ax.plot(*pb, marker="o", ms=5, color="k", zorder=6)
ax.annotate("贴托板铰", xy=pb, xytext=(pb[0]-46, pb[1]-14), fontsize=8,
            arrowprops=dict(arrowstyle="->", lw=0.8))
xc = 122.7; bc = (xc, trayz(xc) + RB)
ax.add_patch(Circle(bc, RB, fc="#e8eef7", ec="#2b4c7e", lw=1.4, zorder=3))
ax.annotate("球顶在挡片上，推不过去\n（球只能爬 5°，挡片面 72°）",
            xy=(90, 40), xytext=(20, 88), fontsize=8.5, color="#8a2b2b",
            arrowprops=dict(arrowstyle="->", lw=0.8, color="#8a2b2b"))
ax.text(20, 74, "单颗球驱动力 0.05 N(POLLEN) / 0.11 N(NECTAR)", fontsize=8, color="#444")

ax2 = plt.subplot(1, 2, 2)
frame(ax2, "B2 自重挡爪 5 g：上铰离托板仅 53 mm —— 爪尖最高只到 53 mm")
pv = (GPX + NIP*n_[0], GPZ + NIP*n_[1])
th2 = math.radians(61.6)
tipd = (pv[0] + HP*(-math.sin(th2)*c_[0] - math.cos(th2)*n_[0]),
        pv[1] + HP*(-math.sin(th2)*c_[1] - math.cos(th2)*n_[1]))
tipr = (pv[0] - HP*n_[0], pv[1] - HP*n_[1])
plank(ax2, pv, tipd, "#e69439", ls="--")
plank(ax2, pv, tipr, "#e69439")
ax2.plot(*pv, marker="o", ms=6, color="k", zorder=6)
ax2.annotate("上铰（离托板 53 mm）", xy=pv, xytext=(pv[0]-70, pv[1]+16), fontsize=8,
             arrowprops=dict(arrowstyle="->", lw=0.8))
ax2.plot([pv[0], pv[0]], [trayz(pv[0]), pv[1]], ls=":", color="0.45", lw=1.0)
ax2.annotate("爪尖永远抬不过 53 mm\n球通过需 ≥ 94 mm", xy=(pv[0], trayz(pv[0])+18),
             xytext=(pv[0]+14, 82), fontsize=8.5, color="#8a2b2b",
             arrowprops=dict(arrowstyle="->", lw=0.8, color="#8a2b2b"))
ax2.annotate("被球推到 61.6°（虚线）仍挡在球道上", xy=tipd, xytext=(tipd[0]-22, tipd[1]-22),
             fontsize=8, color="#a05a10", arrowprops=dict(arrowstyle="->", lw=0.8, color="#a05a10"))
xc2 = pv[0] + RB*ct + 4
ax2.add_patch(Circle((xc2, trayz(xc2) + RB), RB, fc="#e8eef7", ec="#2b4c7e", lw=1.4, zorder=3))
ax2.text(6, 96, "球停在爪的上游侧：后续球全部被挡死\n（无挡件时这轮本可继续送球）", fontsize=8, color="#2b4c7e")
plt.suptitle("R44 判决：B1 / B2 两种被动分球件都过不去 —— 6 相位均 6/24 真出膛、全清 0/6（无挡件 19/24、5/6）",
             fontsize=11.5, fontweight="bold")
plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.savefig("simulation/mujoco/out/_r44_gate_verdict.png", dpi=130)
print("ok")
