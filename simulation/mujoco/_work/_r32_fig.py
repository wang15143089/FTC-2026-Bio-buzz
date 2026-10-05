# -*- coding: utf-8 -*-
"""R32 结果出图：R27 共用送球段全流程（NECTAR + POLLEN，各自正确飞轮夹口）。"""
import json, math, sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

ROOT = Path(".").resolve()
DATA = json.loads((ROOT / "simulation/mujoco/out/_r32_r27_full.json").read_text(encoding="utf-8"))

PCX, PCZ = 29.49, 111.46
R_IN, R_OUT = 107.974, 114.974
A_EXIT, A_LIP = 142.0, 275.0
CUT_X, TRAY_X1, TILT = 38.901, 150.0, 5.0
PIVOT_X, PIVOT_Z = -0.806, 0.423
BLADE_PH = (330.0, 150.0)
BALL_R = {"NECTAR": 45.974, "POLLEN": 35.56}
CASE_C = {0: "#d62728", 1: "#1f77b4", 2: "#2ca02c"}

def polar(r, a):
    return PCX + r * math.cos(math.radians(a)), PCZ + r * math.sin(math.radians(a))

def tray_z(x):
    return PIVOT_Z + (x - PIVOT_X) * math.tan(math.radians(TILT))

def machine_phase(row):
    """只取球还在机构内的采样：出口后再取 30 ms。"""
    tr = row["trace"]; te = row.get("t") or tr[-1]["t"]
    return [s for s in tr if s["t"] <= te + 0.03]

def release_t(row):
    sw = row["sweep"]; hold = row["hold"]; best = hold
    for s in row["trace"]:
        if s["t"] > hold and s["J"] < sw - 0.5:
            best = s["t"]
    return best

fig = plt.figure(figsize=(18.0, 12.2), dpi=105)
gs = fig.add_gridspec(2, 2, height_ratios=[0.95, 1.25], hspace=0.28, wspace=0.18)
fig.suptitle("T06 R27 共用送球段 — NECTAR / POLLEN 全流程仿真复核（索引式驱动，飞轮 1620 rpm，μ=0.40，舵机 25-4 Super Speed）",
             fontsize=15.5, fontweight="bold", y=0.972)

# ---------------- 上排 ----------------
for col, ball in enumerate(("NECTAR", "POLLEN")):
    ax = fig.add_subplot(gs[0, col]); ax2 = ax.twinx()
    rows = [r for r in DATA if r["ball"] == ball]
    for i, row in enumerate(rows):
        ms = machine_phase(row); c = CASE_C[i]
        t = [s["t"] for s in ms]; rr = [s["r"] for s in ms]; aa = [s["ang"] for s in ms]
        ax.plot(t, rr, color=c, lw=2.0, label=row["case"])
        ax2.plot(t, aa, color=c, lw=1.1, ls=":", alpha=0.7)
        tr_ = release_t(row)
        ax.axvspan(row["hold"], tr_, color=c, alpha=0.06)
        ax.plot([row["t"]], [rr[-1]], marker="v", color=c, ms=10, mec="k", mew=0.5)
        ax.plot([row["hold"]], [rr[0]], marker="|", color="0.35", ms=12)
    ax.axhline(60.0, color="gray", lw=1.0, ls="--")
    ax.axhline(R_IN - BALL_R[ball], color="black", lw=1.1, ls="-.")
    ax.set_xlim(-0.15, (rows[-1]["t"] or 4) + 0.9)
    ax.set_ylim(40, 175)
    ax.set_xlabel("时间 t (s)", fontsize=11)
    ax.set_ylabel("球心到拨杆中心距离 r (mm)", fontsize=11)
    ax2.set_ylim(0, 360)
    ax2.set_ylabel("球方位角 α (°)  [点线，右轴]", fontsize=9.5, color="0.35")
    ax2.tick_params(axis="y", colors="0.35")
    ax.grid(alpha=0.3)
    ax.set_title("%s  球 D=%.1f mm，飞轮夹口 %.0f mm" % (ball, 2 * BALL_R[ball], rows[0]["nip"]),
                 fontsize=13.5, fontweight="bold")
    ax.plot([], [], color="gray", ls="--", lw=1.0, label="叶片扫掠半径 60 mm")
    ax.plot([], [], color="black", ls="-.", lw=1.1, label="球贴内弧面 r=%.1f mm" % (R_IN - BALL_R[ball]))
    ax.legend(loc="upper left", fontsize=8.6, framealpha=0.93,
              title="工况（浅带 = 扫掠段，" + chr(9660) + " = 出夹口，| = 停球结束）")

# ---------------- 左下：俯视剖面 ----------------
ax = fig.add_subplot(gs[1, 0])
th = np.linspace(A_EXIT, A_LIP, 200)
xi = [polar(R_IN, a)[0] for a in th]; zi = [polar(R_IN, a)[1] for a in th]
xo = [polar(R_OUT, a)[0] for a in th]; zo = [polar(R_OUT, a)[1] for a in th]
ax.fill(xi + xo[::-1], zi + zo[::-1], color="#9fb3c8", alpha=0.5, zorder=1,
        label="外罩扇区 142°–275°（壁厚 7 mm）")
ax.plot(xi, zi, color="#12395c", lw=2.2, zorder=3, label="球道内弧 R_IN = 107.974 mm")
ax.plot([polar(R_IN + 0.5, a)[0] for a in th], [polar(R_IN + 0.5, a)[1] for a in th],
        color="#e07b39", lw=2.8, ls="--", zorder=4, label="R27 让位面（外扩 0.5 mm，球未触及）")
ax.plot([CUT_X, TRAY_X1], [tray_z(CUT_X), tray_z(TRAY_X1)], color="#7b3f00", lw=5.5,
        solid_capstyle="butt", zorder=2, label="倾斜托板 5°（球由右端滚入）")
ax.add_patch(Circle((PCX, PCZ), 12.0, color="#333333", zorder=6))
for a0 in BLADE_PH:
    ax.plot(*zip(polar(19, a0), polar(59, a0)), color="#333333", lw=6.5, zorder=6, solid_capstyle="round")
ax.plot([], [], color="#333333", lw=6.5, label="拨杆两叶 330°/150°（初始相位）")
ax.add_patch(FancyArrowPatch(polar(78, 300), polar(78, 250), connectionstyle="arc3,rad=-0.25",
                             arrowstyle="-|>", mutation_scale=18, color="#8e44ad", lw=2.2, zorder=7))
ax.text(36, 16, "球行进方向（α 递减，共 181°）", fontsize=8.6, color="#8e44ad",
        ha="center", va="center", fontweight="bold", zorder=10,
        bbox=dict(fc="white", ec="none", alpha=0.85))
for col_i, ball in enumerate(("NECTAR", "POLLEN")):
    row = [x for x in DATA if x["ball"] == ball][1]
    te = row.get("t") or 0
    tr_ = row["trace"]
    edge = "#e6194b" if ball == "NECTAR" else "#2ca02c"
    entry = [s_ for s_ in tr_ if 0.0 <= s_["t"] <= 0.30][::4]
    carry = [s_ for s_ in tr_ if (release_t(row) - 0.03) <= s_["t"] and s_["lx"] <= 45.0]
    step = max(1, len(carry) // 20)
    for s_ in entry:
        ax.add_patch(Circle((s_["x"], s_["z"]), BALL_R[ball], facecolor="none",
                            edgecolor=edge, lw=0.7, alpha=0.38, zorder=7))
    for s_ in carry[::step]:
        ax.add_patch(Circle((s_["x"], s_["z"]), BALL_R[ball], facecolor="none",
                            edgecolor=edge, lw=1.0, alpha=0.9, zorder=8))
    ax.plot([], [], color=edge, lw=1.3,
            label="%s 球轮廓（工况 B；淡=滚入，深=扇区携带）" % ball)
ax.plot([polar(R_IN, A_EXIT)[0]], [polar(R_IN, A_EXIT)[1]], marker="P", ms=14, color="#ff7f0e", zorder=9)
ax.annotate("出口 142° → 进夹口", polar(R_IN, A_EXIT), textcoords="offset points", xytext=(22, 16),
            fontsize=9.5, color="#b35900", fontweight="bold")
ax.annotate("档唇 275°（球道下端）", polar(R_IN, A_LIP), textcoords="offset points", xytext=(0, -36),
            fontsize=9.5, color="#12395c")
ax.annotate("拨杆中心 (29.49, 111.46)", (PCX, PCZ), textcoords="offset points", xytext=(-96, -60),
            fontsize=9, color="#333333")
ax.annotate("飞轮对（±y 方向，夹口 82 / 64 mm）\n→ 球从这里进夹口", (-19.4, 149.6),
            textcoords="offset points", xytext=(26, 30), fontsize=9.2, color="#555555")
ax.set_aspect("equal"); ax.grid(alpha=0.25)
ax.set_xlim(-60, 215); ax.set_ylim(-40, 245)
ax.set_xlabel("x (mm)", fontsize=11); ax.set_ylabel("z (mm)", fontsize=11)
ax.set_title("俯视剖面（前后视平面）：球道 / 让位面 / 托板 / 球轮廓轨迹", fontsize=13.5, fontweight="bold")
ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.30), ncol=3, fontsize=8.2, framealpha=0.95)

# ---------------- 右下：结果表 ----------------
ax = fig.add_subplot(gs[1, 1]); ax.axis("off")
cols = ["球", "工况", "夹口\n(mm)", "出口 t\n(s)", "出口 v\n(m/s)", "出口角\n(°)", "最高点\n(mm)",
        "平射程\n(m)", "卡滞\n(%)", "峰值扭矩\n(N·m)", "最小 r\n(mm)", "判定"]
cell, colors = [], []
for r in DATA:
    ok = r["ok"]
    cell.append([r["ball"], r["case"], "%.0f" % r["nip"], "%.2f" % r["t"], "%.2f" % r["v"],
                 "%.1f" % r["ang"], "%.0f" % r["apex"], "%.1f" % r["rng"],
                 "%.0f" % (100 * r["jam"]), "%.3f" % r["tq_peak"],
                 "%.2f" % r["min_r"], "通过" if ok else "失败"])
    colors.append(["#e8f5e9" if ok else "#ffebee"] * len(cols))
tab = ax.table(cellText=cell, colLabels=cols, cellColours=colors, loc="upper center", cellLoc="center")
tab.auto_set_font_size(False); tab.set_fontsize(10.0); tab.scale(1.0, 2.15)
tab.auto_set_column_width(col=list(range(len(cols))))
for j in range(len(cols)):
    tab[0, j].set_facecolor("#37474f"); tab[0, j].set_text_props(color="w", fontweight="bold")
for i in range(1, len(cell) + 1):
    tab[i, 0].set_text_props(fontweight="bold")
nok = sum(1 for r in DATA if r["ok"])
ax.set_title("仿真结果汇总：%d/%d 通过" % (nok, len(DATA)), fontsize=13.5, fontweight="bold", pad=14)
ax.text(0.0, 0.055,
        "口径与判读：\n"
        "• 出口 t / v = 球进入夹口后沿喉道越过 40 mm 参考面时的时刻与速度（判定量，未使用 peak_speed）。\n"
        "• 卡滞%% = 舵机扭矩 > 0.40 N·m 的采样占比；舵机 25-4 Super Speed 堵转 0.530 N·m / 290 rpm（kv=0.017452）。\n"
        "• 球在外罩扇区内的最大外缘半径 %.2f mm（NECTAR）/ %.2f mm（POLLEN），比内弧面 107.974 mm 多 0.5–0.7 mm，\n"
        "  这是球被叶片压在内弧面上的接触压入量，不是让位面被触及；让位面在 r > 107.974 mm 的球道外侧，全程未与球接触\n"
        "  （CAD 19 点球道扫描同样为 0 mm³ 干涉）。\n"
        "• 两球共用同一套送球段（外罩 / 托板 / 拨杆 / 舵机），仅飞轮夹口随球改变：NECTAR 82 mm、POLLEN 64 mm。" %
        (DATA[0]["sector_max_r"], DATA[3]["sector_max_r"]),
        transform=ax.transAxes, fontsize=9.3, color="0.22", va="top")
fig.savefig(ROOT / "cad/output/_t06_r32_fullflow_zh.png", bbox_inches="tight", facecolor="white")
print("saved", ROOT / "cad/output/_t06_r32_fullflow_zh.png")
