# -*- coding: utf-8 -*-
"""R45 停位角窗示意图：为什么待机段 ctrl=0 会楔死球，以及 J_park 的安全区间。

几何单位统一 mm。输出 simulation/mujoco/out/_r45_park_window.png
输入 simulation/mujoco/out/_r45_park3_sweep.log（_work/_r45_park3.py 的实测扫角）
"""
import os, re
import matplotlib
matplotlib.use("Agg")
from matplotlib import font_manager, pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "out"))
for f in ("C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf"):
    if os.path.exists(f):
        font_manager.fontManager.addfont(f)
        plt.rcParams["font.family"] = font_manager.FontProperties(fname=f).get_name()
        break
plt.rcParams["axes.unicode_minus"] = False

CX, CZ = 29.49, 111.46
R_FLEX, R_BALL, R_NEST = 61.0, 46.0, 100.3
R_TRACK = R_FLEX + R_BALL
WIN = (235.0, 355.0)

rows = []
log = os.path.join(OUT, "_r45_park3_sweep.log")
pat = re.compile(r"P=\s*([-\d.]+)\s+x0=\s*([-\d.]+)\s+->\s+x=\s*([-\d.]+)\s+z=\s*([-\d.]+)\s+\|\s*J=\s*([-\d.]+)")
if os.path.exists(log):
    for line in open(log, encoding="utf-8", errors="replace"):
        m = pat.match(line.strip())
        if m:
            rows.append((float(m.group(1)), float(m.group(3))))

fig, ax = plt.subplots(1, 2, figsize=(14.5, 6.3))

a = ax[0]
th = np.linspace(0, 2 * np.pi, 720)
tt = np.linspace(np.radians(WIN[0]), np.radians(WIN[1]), 160)
a.fill(np.concatenate([[CX], CX + R_TRACK * np.cos(tt), [CX]]),
       np.concatenate([[CZ], CZ + R_TRACK * np.sin(tt), [CZ]]),
       color="#ffd6d6", alpha=0.85, zorder=0, label="球道/球窝窗口 [235,355]")
a.plot(CX + R_FLEX * np.cos(th), CZ + R_FLEX * np.sin(th), "-", color="#1f77b4", lw=2,
       label="弹性指扫掠外缘 R61")
a.plot(CX + R_NEST * np.cos(th), CZ + R_NEST * np.sin(th), "--", color="#7f7f7f", lw=1.3,
       label="球窝球心 R100.3")
a.plot(CX + R_TRACK * np.cos(th), CZ + R_TRACK * np.sin(th), ":", color="#2ca02c", lw=1.4,
       label="球道球心 R107 (NECTAR)")
a.plot(CX, CZ, "k+", ms=14, mew=2)

for J, col, lab, off in ((53.0, "#d62728", "J=53 (自由下垂)\n挡片极角 337\n→ 正好楔在球道上", (10, -34)),
                         (143.0, "#ff7f0e", "J=143\n挡片极角 247 → 挡住球道", (10, 6)),
                         (188.0, "#2ca02c", "J=188 (推荐)\n挡片极角 202 → 让开窗口", (10, 10))):
    phi = np.radians(390.0 - J)
    px, pz = CX + R_FLEX * np.cos(phi), CZ + R_FLEX * np.sin(phi)
    a.plot([px], [pz], "o", color=col, ms=10, zorder=6)
    a.plot([CX, px], [CZ, pz], "-", color=col, lw=1.5, alpha=0.65, zorder=5)
    a.annotate(lab, (px, pz), textcoords="offset points", xytext=off, fontsize=9.5, color=col)
a.annotate("拨杆轴心 C", (CX, CZ), textcoords="offset points", xytext=(6, 6), fontsize=10)
a.set_aspect("equal")
a.set_xlabel("x (mm)   ← 球自右侧滚入")
a.set_ylabel("z (mm)")
a.set_title("(A) 挡片极角 = 390 − J 不得落进窗口 [235°,355°]\n→ J_park ∈ (171°,199°)", fontsize=11)
a.legend(fontsize=8.5, loc="upper left")
a.grid(alpha=0.25)

b = ax[1]
if rows:
    J = [r[0] for r in rows]
    X = [r[1] for r in rows]
    b.plot(J, X, "o-", color="#444", ms=5, lw=1.2, label="实测球最终 x（NECTAR 自行滚入, 5 s）")
b.axvspan(171, 199, color="#c8f7c5", alpha=0.85, label="推荐停位区间 J_park ∈ (171,199)")
b.axvline(188, color="#2ca02c", lw=1.6, ls="--")
b.annotate("J_park = 188°", (188, 108), color="#2ca02c", fontsize=10,
           textcoords="offset points", xytext=(6, 0))
b.axhline(45, color="#888", ls=":", lw=1)
b.text(4, 20, "进球窝（球最终 x < 45 mm）", fontsize=9.5, color="#2ca02c")
b.text(4, 60, "被挡 / 楔死", fontsize=9.5, color="#d62728")
b.annotate("J=230 撞到对称侧\npaddle_flex_2 又楔死", (230, 123.6), textcoords="offset points",
           xytext=(-95, -18), fontsize=9, color="#d62728",
           arrowprops=dict(arrowstyle="->", color="#d62728", lw=1))
b.set_xlabel("拨杆待机停位角 J_park (deg)")
b.set_ylabel("球最终 x (mm)")
b.set_title("(B) 待机角扫描：球能不能滚到球窝", fontsize=11)
b.set_xlim(0, 250)
b.grid(alpha=0.25)
b.legend(fontsize=9, loc="center right")

fig.suptitle("R45 待机姿态：真实舵机是位置保持，不是自由下垂（ctrl=0）", fontsize=13, y=0.99)
fig.tight_layout()
p = os.path.join(OUT, "_r45_park_window.png")
fig.savefig(p, dpi=150)
print("saved", p, "rows =", len(rows))