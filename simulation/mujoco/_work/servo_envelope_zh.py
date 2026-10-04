# -*- coding: utf-8 -*-
"""goBILDA servo envelope vs R5 feed torque requirement (12 s run budget)."""
import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

KGCM = 0.0980665
WMIN = 30.0
SERVOS = [
    ("25-4 Super Speed", 5.4*KGCM,  290.0, "#d62728"),
    ("25-3 Speed",       10.8*KGCM, 145.0, "#1f77b4"),
    ("Axon MAX MK2",     39.0*KGCM, 100.0, "#9467bd"),
    ("25-2 Torque",      25.2*KGCM, 60.0,  "#2ca02c"),
]
D = json.loads(Path("simulation/mujoco/out/_r2r5_speed_req12.json").read_text(encoding="utf-8"))["R5"]
pts = sorted((float(k), v) for k, v in D.items() if v is not None)
xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
def need(w):
    if w <= xs[0]: return ys[0]
    if w >= xs[-1]: return ys[-1]
    for i in range(len(pts)-1):
        if xs[i] <= w <= xs[i+1]:
            t = (w-xs[i])/(xs[i+1]-xs[i]); return ys[i] + t*(ys[i+1]-ys[i])
    return ys[-1]

grid = [WMIN + i*0.5 for i in range(0, int((330-WMIN)*2)+1)]
win = {}
for name, ts, wnl, c in SERVOS:
    segs = []; cur = []
    for w in grid:
        if w < wnl and ts*(1.0-w/wnl) >= need(w):
            cur.append(w)
        else:
            if cur: segs.append((cur[0], cur[-1])); cur = []
    if cur: segs.append((cur[0], cur[-1]))
    win[name] = segs

fig = plt.figure(figsize=(12.8, 8.8))
gs = fig.add_gridspec(2, 1, height_ratios=[2.45, 1.05], hspace=0.36)
ax = fig.add_subplot(gs[0])
ax.plot(xs, ys, "o-", color="#c00000", lw=3.0, ms=8, zorder=7,
        label="R5 送球扭矩需求（双入口, 12 s 预算, SIMULATED）")
for x, y in zip(xs, ys):
    ax.annotate("%.2f" % y, (x, y), textcoords="offset points", xytext=(0, 8),
                ha="center", fontsize=8.5, color="#c00000")
xx = [i*1.0 for i in range(0, 341)]
for name, ts, wnl, c in SERVOS:
    ax.plot(xx, [ts*(1.0-v/wnl) if v <= wnl else 0.0 for v in xx], color=c, lw=2.0, zorder=3,
            label="%s @7.4V（堵转 %.2f N·m / 空载 %.0f rpm）" % (name, ts, wnl))
    for a, b in win[name]:
        ax.plot([a, b], [need(a), need(b)], color=c, lw=5.0, alpha=0.28, zorder=2)
ax.axvspan(0, WMIN, color="#999999", alpha=0.18, zorder=1)
ax.text(WMIN/2, 1.16, "节拍过慢\n(<30 rpm)", ha="center", va="top", fontsize=8.5, color="#555")
ax.set_xlim(0, 320); ax.set_ylim(0, 1.25)
ax.set_xlabel("拨杆转速 (rpm)", fontsize=12)
ax.set_ylabel("扭矩 (N·m)", fontsize=12)
ax.set_title("T06 POLLEN V2 — R5 送球需求 vs goBILDA 舵机 7.4V 直驱能力（12 s 仿真预算）\n"
             "粗淡色段 = 该舵机可用扭矩高于送球需求；曲线以下/以上均可用的转速区间称为「可直驱窗口」", fontsize=12.5)
ax.grid(alpha=0.3)
ax.legend(fontsize=8.8, loc="upper right", framealpha=0.96)
ax.text(0.015, 0.03,
        "需求线为 11 个转速点的仿真门槛（二分容差 ±0.03 N·m）；0.24 为扫描下限，实际 ≤0.24\n"
        "舵机线为堵转→空载线性包络（可用扭矩需按转速插值，表列扭矩均为堵转值）",
        transform=ax.transAxes, fontsize=8.2, color="#333", va="bottom",
        bbox=dict(boxstyle="round", fc="white", ec="#bbb", alpha=0.9))

ax2 = fig.add_subplot(gs[1])
for i, (name, ts, wnl, c) in enumerate(SERVOS):
    ax2.barh(i, max(0.0, wnl-WMIN), left=WMIN, height=0.44, color=c, alpha=0.13)
    ax2.text(WMIN+2, i, "%.0f" % wnl, va="center", fontsize=8, color="#555")
    for a, b in win[name]:
        ax2.barh(i, b-a, left=a, height=0.44, color=c, alpha=0.88)
        ax2.text((a+b)/2.0, i, "%.0f–%.0f" % (a, b), ha="center", va="center",
                 fontsize=9.5, color="white", fontweight="bold")
ax2.set_yticks(range(len(SERVOS)))
ax2.set_yticklabels([s[0] for s in SERVOS], fontsize=10)
ax2.set_xlim(0, 320); ax2.set_xlabel("拨杆转速 (rpm)", fontsize=11)
ax2.set_title("各舵机可直驱的拨杆转速窗口（淡底 = 该舵机从 30 rpm 到空载转速的范围）", fontsize=11)
ax2.grid(alpha=0.3, axis="x"); ax2.invert_yaxis()
fig.subplots_adjust(left=0.115, right=0.985, top=0.915, bottom=0.07)
out = Path("simulation/mujoco/out/servo_envelope_zh.png")
fig.savefig(out, dpi=150)
print("saved", out)
print("need:", pts)
for name, ts, wnl, c in SERVOS:
    print("%-18s stall=%.3f noload=%3.0f windows=%s" % (name, ts, wnl,
          ["%.0f-%.0f" % s for s in win[name]] or "NONE"))
