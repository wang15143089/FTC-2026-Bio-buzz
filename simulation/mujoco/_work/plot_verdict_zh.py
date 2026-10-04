# -*- coding: utf-8 -*-
"""面板 ⑤ 重绘：相位/指片数 -> 门槛；并修正表格中未实测的转速"""
import json, math, sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
OUT = Path("simulation/mujoco/out")
J = lambda n: json.loads((OUT / n).read_text(encoding="utf-8"))
D, P, B = J("summary_v2_options_final.json"), J("summary_v2_phase.json"), J("summary_v2_best.json")
BLUE, GREEN, RED, ORANGE = "#4a7fb5", "#2e9e5b", "#d1495b", "#c8791b"
def T_us(w): return 0.608 * (1 - w / 285.7)
def T_ba(w): return 1.638 * (1 - w / 83.3)

fig = plt.figure(figsize=(24.5, 13.2))
gs = fig.add_gridspec(2, 3, hspace=0.36, wspace=0.22)

# ① 门槛对比
ax = fig.add_subplot(gs[0, 0])
rows = [("V0\n现状", D["geom"]["V0 现状"]["threshold_Nm"], "#9aa6b2"),
        ("A\n唇口喇叭", D["geom"]["A 唇口喇叭"]["threshold_Nm"], GREEN),
        ("B\n托板缩进", D["geom"]["B 托板缩进"]["threshold_Nm"], "#9aa6b2"),
        ("C\n叶尖卸载", D["geom"]["C 叶尖卸载"]["threshold_Nm"], RED),
        ("D\n球窝抬高", D["geom"]["D 球窝抬高6.8"]["threshold_Nm"], GREEN),
        ("A+D", D["geom"]["A+D"]["threshold_Nm"], GREEN),
        ("P3\n二指", B["P3 二指350/170"]["threshold_Nm"], "#1f7a45"),
        ("P5\n二指+A+D", B["P5 二指+A+D"]["threshold_Nm"], "#0f5c33")]
x = np.arange(len(rows))
ax.bar(x, [r[1] for r in rows], 0.62, color=[r[2] for r in rows], zorder=3)
for xi, r in zip(x, rows):
    ax.text(xi, r[1] + 0.035, "%.2f" % r[1], ha="center", fontsize=13, fontweight="bold", zorder=4)
ax.axhline(0.608, color=ORANGE, ls="--", lw=2.2, zorder=2)
ax.text(2.6, 0.30, "UltraSpeed 堵转 0.608 N·m", ha="center", fontsize=11, color="#a25c0c", zorder=5)
ax.axhline(1.638, color="#7b4fd1", ls="--", lw=2.0, zorder=2)
ax.text(3.5, 1.665, "Balanced 堵转 1.638（该扭矩下仅 ~22 rpm）", ha="center", fontsize=10.5, color="#5b34ad")
ax.set_xticks(x); ax.set_xticklabels([r[0] for r in rows], fontsize=11)
ax.set_ylabel("发射门槛扭矩（拨杆轴，N·m）", fontsize=13); ax.set_ylim(0, 1.9)
ax.grid(axis="y", alpha=0.3, zorder=0)
ax.set_title("① 逐个仿真：把球从托板送进外罩再发射所需的最小拨杆扭矩\n"
             "拨杆 200 rpm，球从托板 x=145 滚入，二分法分辨率 0.05 N·m", fontsize=13.5, loc="left")

# ② 舵机包络
ax = fig.add_subplot(gs[0, 1])
w = np.linspace(0, 300, 400)
ax.plot(w, np.clip(T_us(w), 0, None), color=ORANGE, lw=2.8, label="SRS V2 UltraSpeed 7.4 V")
ax.plot(w, np.clip(T_ba(w), 0, None), color="#7b4fd1", lw=2.8, label="SRS V2 Balanced 7.4 V")
ax.axvspan(90, 140, color="#ffe9c2", alpha=0.75, zorder=0)
ax.text(115, 1.55, "送球所需转速窗口", ha="center", fontsize=11, color="#8a5a00")
for lab, ww, tt, c, off in (("现状需求 0.94 @140", 140, 0.94, RED, (9, 6)),
                            ("A+D 0.64 @140", 140, 0.64, BLUE, (9, -16)),
                            ("P5 0.42 @90", 90, 0.42, "#0f5c33", (12, 4))):
    ax.plot(ww, tt, "o", ms=11, color=c, zorder=5, mec="w", mew=1.6)
    ax.annotate(lab, (ww, tt), textcoords="offset points", xytext=off, fontsize=10.5, color=c)
ax.plot(90, T_us(90), "*", ms=20, color="#b3231b", zorder=6)
ax.annotate("UltraSpeed @90 rpm 只能给 %.3f N·m\n≈ P5 需求 0.42 → 刚好压在边界" % T_us(90),
            (90, T_us(90)), textcoords="offset points", xytext=(-130, -34), fontsize=10.5, color="#b3231b")
ax.set_xlabel("拨杆转速（rpm）", fontsize=12.5); ax.set_ylabel("可用扭矩（N·m）", fontsize=12.5)
ax.set_xlim(0, 300); ax.set_ylim(0, 1.75); ax.grid(alpha=0.3); ax.legend(fontsize=11, loc="upper right")
ax.set_title("② 需求点 vs 舵机力矩—转速包络（线性模型）\n几何优化把需求推进到包络边界，但没有翻盘",
             fontsize=13.5, loc="left")

# ③ 轨迹
ax = fig.add_subplot(gs[0, 2])
for tag, c, lab in (("v2opt_V0_0p8", RED, "V0 现状 @0.8（卡死）"),
                    ("v2opt_A_0p8", GREEN, "A 唇口喇叭 @0.8（通过）"),
                    ("v2opt_D_0p8", "#1f7a45", "D 球窝抬高 @0.8（通过）"),
                    ("v2opt_V0_1p0", "#8a8a8a", "V0 现状 @1.0（通过）")):
    p = OUT / ("trace_%s.json" % tag)
    if not p.exists(): continue
    tr = json.loads(p.read_text(encoding="utf-8"))
    ax.plot([s["t"] for s in tr], [s["ang"] for s in tr], color=c, lw=2.5, label=lab)
for a, t, dy, ha in ((225, "唇口 225°（进口）", 5, "right"), (142, "出口 142°", -16, "right")):
    ax.axhline(a, color="#1f4e79", ls="--", lw=1.3)
    ax.text(6.1, a + dy, t, fontsize=10, color="#1f4e79", ha=ha)
ax.set_xlabel("时间（s）", fontsize=12.5); ax.set_ylabel("球心极角 θ（°）", fontsize=12.5)
ax.set_xlim(0, 7); ax.grid(alpha=0.3); ax.legend(fontsize=10.5, loc="lower left")
ax.set_title("③ 同一 0.8 N·m 限幅下的实际走位\n现状卡在 θ≈300°，A / D 均能走完全程并发射",
             fontsize=13.5, loc="left")

# ④ 摩擦
ax = fig.add_subplot(gs[1, 0])
fr = D["friction"]
xl = ["μ=1.0\n(现状)", "μ=0.7", "μ=0.5", "μ=0.35"]
v0 = [fr["V0 u=1.0(现状)"]["threshold_Nm"], fr["V0 u_ball=0.7"]["threshold_Nm"],
      fr["V0 u_ball=0.5"]["threshold_Nm"], fr["V0 u_ball=0.35"]["threshold_Nm"]]
va = [None, fr["A u_ball=0.7"]["threshold_Nm"], fr["A u_ball=0.5"]["threshold_Nm"],
      fr["A u_ball=0.35"]["threshold_Nm"]]
C = 1.72
x = np.arange(4)
ax.bar(x - 0.19, [v or C for v in v0], 0.36, color=BLUE, label="V0 现状几何", zorder=3)
ax.bar(x + 0.19, [v or C for v in va], 0.36, color=GREEN, label="A 唇口喇叭", zorder=3)
for xi, v in zip(x - 0.19, v0): ax.text(xi, (v or C) + 0.04, "%.2f" % v if v else "不发射", ha="center", fontsize=11, zorder=4)
for xi, v in zip(x + 0.19, va): ax.text(xi, (v or C) + 0.04, "%.2f" % v if v else "不发射", ha="center", fontsize=11, zorder=4)
ax.axhline(0.608, color=ORANGE, ls="--", lw=2)
ax.text(3.45, 0.63, "UltraSpeed 堵转 0.608", ha="right", fontsize=10, color="#a25c0c")
ax.set_xticks(x); ax.set_xticklabels(xl, fontsize=12); ax.set_ylim(0, 2.02)
ax.grid(axis="y", alpha=0.3, zorder=0); ax.legend(fontsize=11); ax.set_ylabel("发射门槛扭矩（N·m）", fontsize=12.5)
ax.set_title("④ 摩擦不是杠杆：越滑越送不进去\n（拨杆靠摩擦“拽”球；外罩摩擦被球 priority=1 覆盖，实测无影响）",
             fontsize=13.5, loc="left")

# ⑤ 相位 / 指片数
ax = fig.add_subplot(gs[1, 1])
ks = list(P.keys())
short = {"P0 三指 原相位 θ=342/222/102": "P0 三指\n342/222/102",
         "P1 三指 θ=240/120/0": "P1 三指\n240/120/0",
         "P2 三指 θ=154/34/274": "P2 三指\n154/34/274",
         "P3 二指 θ=350/170": "P3 二指\n350/170",
         "P4 二指 θ=350/170 + A喇叭": "P4 二指\n350/170+A"}
th = [P[k]["threshold_Nm"] for k in ks]
rs = [P[k]["rest_r"] for k in ks]
angs = [P[k]["rest_ang"] for k in ks]
cols = ["#9aa6b2"] + ["#9aa6b2"] + ["#9aa6b2"] + ["#1f7a45", "#0f5c33"]
x = np.arange(len(ks))
ax.bar(x, th, 0.55, color=cols, zorder=3)
for xi, t, r0, a0 in zip(x, th, rs, angs):
    ax.text(xi, t + 0.03, "%.2f" % t, ha="center", fontsize=13, fontweight="bold", zorder=4)
    ax.text(xi, t - 0.10, "停位 r=%.1f\nθ=%.0f°" % (r0, a0), ha="center", fontsize=9.5, color="#333", zorder=4)
ax.axhline(0.608, color=ORANGE, ls="--", lw=2.2)
ax.text(4.45, 0.63, "UltraSpeed 堵转 0.608", ha="right", fontsize=10.5, color="#a25c0c")
ax.set_xticks(x); ax.set_xticklabels([short[k] for k in ks], fontsize=11)
ax.set_ylabel("发射门槛扭矩（N·m）", fontsize=12.5); ax.set_ylim(0, 1.35)
ax.grid(axis="y", alpha=0.3, zorder=0)
ax.set_title("⑤ 真正的杠杆是指片布置：3 指 120° → 2 指 180°\n"
             "现状球永远停在 R95（球靠在指片尖端面上，设计轨道是 R58.4）", fontsize=13.5, loc="left")

# ⑥ 收尾表
ax = fig.add_subplot(gs[1, 2]); ax.axis("off")
tab = [["方案", "门槛\nN·m", "相对现状", "转速门槛\nrpm", "UltraSpeed\n90rpm 可给"],
       ["V0 现状", "0.94", "—", "120~140", "0.416"],
       ["A 唇口喇叭", "0.72", "−23%", "未测", "0.416"],
       ["B 托板缩进", "0.94", "0（无效）", "未测", "0.416"],
       ["C 叶尖卸载", "1.25", "+33%（恶化）", "未测", "0.416"],
       ["D 球窝抬高 6.8", "0.68", "−28%", "未测", "0.416"],
       ["A+D", "0.64", "−32%", "未测", "0.416"],
       ["P3 二指 350/170", "0.55", "−41%", "105", "0.416"],
       ["P4 二指 + A", "0.55", "−41%", "105", "0.416"],
       ["P5 二指 + A + D", "0.42", "−55%", "90", "0.416"]]
tb = ax.table(cellText=tab[1:], colLabels=tab[0], loc="center", cellLoc="center",
              colWidths=[0.31, 0.13, 0.20, 0.18, 0.24])
tb.auto_set_font_size(False); tb.set_fontsize(11.5); tb.scale(1, 1.85)
for (i, j), c in tb.get_celld().items():
    c.set_edgecolor("#b9c6d4")
    if i == 0: c.set_facecolor("#dce8f4"); c.set_text_props(fontweight="bold")
    elif i == len(tab) - 1: c.set_facecolor("#e6f5ea")
    elif j == 4: c.set_facecolor("#fdf1e0")
ax.set_title("⑥ 收尾：最优组合与舵机对照\nP5 = 0.42 N·m @90 rpm，刚好压在 UltraSpeed 曲线边界（0.416 N·m）",
             fontsize=13.5, loc="left")
ax.text(0.0, 0.02, "结论：几何优化把送球需求砍掉一半（0.94 → 0.42），但压不进“单只 SRS V2 直驱”的安全区，\n"
        "P5 属“边界可行”，必须台架实测。B（托板缩进）与 C（叶尖卸载）按负结果归档，不再投入。",
        transform=ax.transAxes, fontsize=11.5, color="#123",
        bbox=dict(boxstyle="round,pad=0.5", fc="#eef4fa", ec="#8bb4d4"))
fig.suptitle("T06 POLLEN V2 送球段接触几何 —— 方案逐个仿真对比（MuJoCo，2026-10-03）", fontsize=18, y=0.985)
fig.savefig(OUT / "geom_options_verdict_zh.png", dpi=130, bbox_inches="tight")
print("已保存", OUT / "geom_options_verdict_zh.png")
