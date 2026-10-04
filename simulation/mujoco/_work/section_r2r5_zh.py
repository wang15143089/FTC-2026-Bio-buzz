# -*- coding: utf-8 -*-
"""T06 POLLEN V2 送球段剖面：方案 R2 vs 方案 R5（修订标注版）"""
import json, math, sys, importlib.util
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Circle, Polygon, Rectangle
from matplotlib.lines import Line2D
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

spec = importlib.util.spec_from_file_location("pv2", r"simulation/mujoco/pollen_v2_sim.py")
pv2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(pv2)
C = (pv2.PADDLE_CX, pv2.PADDLE_CZ)
R_IN, R_OUT, BALL_R, R_CARRY = pv2.R_IN, pv2.R_OUT, pv2.BALL_R, pv2.R_CARRY
C_SHELL, C_SHELL_E = "#9fc6e0", "#2a6f97"
C_TRAY,  C_TRAY_E  = "#b9d8b0", "#3f7d3a"
C_PADDLE,C_PADDLE_E= "#f2a65a", "#b5651d"
C_BALL             = "#e8c33a"
C_FLARE            = "#e07a5f"
C_PAD              = "#c9a0dc"
C_GUIDE            = "#b0b0b0"
PAD_X0, PAD_X1, PAD_STEP = -17.0, 13.0, 6.8
PAD_TOP = pv2.tray_top_z(-2.0) + PAD_STEP

def fp(ang, r):
    a = math.radians(ang); return (C[0]+r*math.cos(a), C[1]+r*math.sin(a))
def rect_xz(x0, x1, z0, z1):
    return Polygon([(x0,z0),(x1,z0),(x1,z1),(x0,z1)], closed=True)
def finger(cx, cz, ang_deg, r0, r1, halfw):
    a = math.radians(ang_deg)
    ux, uz = math.cos(a), -math.sin(a); tx, tz = math.sin(a), math.cos(a)
    pts = [(cx+u*ux+v*tx, cz+u*uz+v*tz) for (u,v) in ((r0,-halfw),(r1,-halfw),(r1,halfw),(r0,halfw))]
    return Polygon(pts, closed=True)
def draw_finger(ax, ang, fc=C_PADDLE, ec=C_PADDLE_E, lw=1.2, alpha=1.0, z=6):
    for (r0,r1,hw) in ((14,46,5),(46,58,15),(56,60,17)):
        p = finger(C[0], C[1], ang, r0, r1, hw)
        p.set(facecolor=fc, edgecolor=ec, lw=lw, alpha=alpha, zorder=z); ax.add_patch(p)
def draw_base(ax, flare=False, pad=False, guide=True, trackline=True):
    ax.add_patch(Wedge(C, R_OUT, 142, 225, width=R_OUT-R_IN, facecolor=C_SHELL, edgecolor=C_SHELL_E, lw=1.4, zorder=4))
    for ang in (142.0, 225.0):
        p = pv2.polar(0.5*(R_IN+R_OUT), ang)
        ax.add_patch(Rectangle((p[0]-R_OUT+R_IN, p[1]-1.5), R_OUT-R_IN, 3.0, angle=-ang,
                     facecolor=C_SHELL, edgecolor=C_SHELL_E, lw=1.2, zorder=5))
    if flare:
        for (am, rin) in ((227.5,95.5),(231.5,99.5),(235.5,103.5)):
            ax.add_patch(Wedge(C, rin+7.0, am-2.7, am+2.7, width=7.0,
                         facecolor=C_FLARE, edgecolor="#a33b20", lw=1.2, zorder=6))
    nx, nz = pv2.normal(-pv2.TILT)
    x0, x1 = pv2.TRAY_X0, pv2.TRAY_X1
    t0 = (x0, pv2.tray_top_z(x0)); t1 = (x1, pv2.tray_top_z(x1))
    ax.add_patch(Polygon([t0, t1, (t1[0]-nx*pv2.TRAY_T, t1[1]-nz*pv2.TRAY_T),
                          (t0[0]-nx*pv2.TRAY_T, t0[1]-nz*pv2.TRAY_T)], closed=True,
                 facecolor=C_TRAY, edgecolor=C_TRAY_E, lw=1.3, zorder=4))
    sp = rect_xz(pv2.STRUT_X0, pv2.STRUT_X1, pv2.STRUT_Z0, pv2.STRUT_Z1)
    sp.set(facecolor=C_TRAY, edgecolor=C_TRAY_E, lw=1.2, zorder=4); ax.add_patch(sp)
    if pad:
        q = rect_xz(PAD_X0, PAD_X1, PAD_TOP-(PAD_STEP+6.0), PAD_TOP)
        q.set(facecolor=C_PAD, edgecolor="#6a3d9a", lw=1.4, zorder=5); ax.add_patch(q)
    if guide:
        for (s, e, L, a) in pv2.SEGS:
            ax.plot([s[0], e[0]], [s[1], e[1]], color=C_GUIDE, lw=1.6, ls=(0,(6,4)), zorder=2)
    if trackline:
        th = [142.0 + (225.0-142.0)*i/120.0 for i in range(121)]
        ax.plot([fp(t,R_CARRY)[0] for t in th], [fp(t,R_CARRY)[1] for t in th],
                color="#c0392b", lw=1.3, ls=(0,(5,3)), zorder=5)
def draw_hub(ax):
    ax.add_patch(Circle(C, 18.0, facecolor=C_PADDLE, edgecolor=C_PADDLE_E, lw=1.3, zorder=7))
    ax.plot(*C, marker="+", color="#333", ms=10, mew=1.6, zorder=8)
def axis_setup(ax, xlim, zlim, title=None):
    ax.set_aspect("equal"); ax.set_xlim(*xlim); ax.set_ylim(*zlim)
    if title: ax.set_title(title, fontsize=12, pad=8)
    ax.grid(True, color="#e6e6e6", lw=0.7); ax.set_axisbelow(True)
    for s in ax.spines.values(): s.set_color("#bbb")
    ax.tick_params(labelsize=8, colors="#555")

TR = json.loads(Path("simulation/mujoco/out/_r2r5_paths.json").read_text(encoding="utf-8"))
def track(ax, key, tmax=2.4):
    pts = [(p[1], p[2]) for p in TR[key]["path"] if p[0] <= tmax]
    ax.plot([q[0] for q in pts], [q[1] for q in pts], color="#8e44ad", lw=2.3, alpha=0.9, zorder=9)

fig = plt.figure(figsize=(16.2, 11.4), dpi=130)
fig.suptitle("T06 POLLEN V2 送球段剖面 —— 方案 R2（A 唇口喇叭）vs 方案 R5（D 球窝抬高 6.8）", fontsize=16, y=0.986)
fig.text(0.5, 0.952, "剖面 = 拨杆轴心 XZ 平面；单位 mm；轨迹为 MuJoCo 实测球心路径；指片标注 θ 为送球角，几何角度 ang = 360−θ",
         ha="center", fontsize=10, color="#666")
gs = fig.add_gridspec(2, 2, left=0.055, right=0.975, top=0.922, bottom=0.062, hspace=0.24, wspace=0.16)
PARK = (113.46, 63.22)

# ---------------- (a) R2 ----------------
ax = fig.add_subplot(gs[0,0])
draw_base(ax, flare=True, pad=False)
for ang in (10.0, 190.0): draw_finger(ax, ang)
draw_hub(ax); track(ax, "R2")
ax.add_patch(Circle(PARK, BALL_R, facecolor=C_BALL, edgecolor="#8a6d1a", lw=1.4, alpha=0.9, zorder=8))
ax.annotate("A 唇口喇叭（三段）\n替代 225° 直挡墙", xy=fp(233.0, 104.0), xytext=(-124, 52), fontsize=9.2,
            color="#a33b20", arrowprops=dict(arrowstyle="->", color="#a33b20", lw=1.2), zorder=11)
ax.annotate("球自滚到球道 r≈59\nθ≈225° 起爬唇口", xy=fp(228.0, 60.0), xytext=(-124, 26), fontsize=9.2,
            color="#2f6b2a", arrowprops=dict(arrowstyle="->", color="#2f6b2a", lw=1.1), zorder=11)
ax.annotate("指片 θ=350°", xy=fp(10.0, 56.0), xytext=(44, 150), fontsize=9, color=C_PADDLE_E,
            arrowprops=dict(arrowstyle="->", color=C_PADDLE_E, lw=1.1), zorder=11)
ax.annotate("指片 θ=170°", xy=fp(190.0, 56.0), xytext=(-124, 150), fontsize=9, color=C_PADDLE_E,
            arrowprops=dict(arrowstyle="->", color=C_PADDLE_E, lw=1.1), zorder=11)
ax.annotate("停位球（二指停车位）", xy=(PARK[0]-BALL_R*0.85, PARK[1]-BALL_R*0.5), xytext=(30, 26),
            fontsize=9, color="#7a5c10", arrowprops=dict(arrowstyle="->", color="#7a5c10", lw=1.0), zorder=11)
ax.plot([], [], color="#8e44ad", lw=2.3, label="球心轨迹（实测）")
ax.legend(loc="upper right", fontsize=8.6, frameon=False)
axis_setup(ax, (-128, 178), (-12, 205), "(a) R2 = 二指 350°/170° + A 唇口喇叭（新增 3 段台阶件）")
ax.text(0.985, 0.03, "双入口门槛 0.50 N·m（@200rpm）；90 rpm 需 0.60 N·m", transform=ax.transAxes, ha="right",
        fontsize=9.4, color="#a33b20", bbox=dict(fc="#fff2ec", ec="#a33b20", lw=0.8, alpha=0.95))

# ---------------- (b) R5 ----------------
ax = fig.add_subplot(gs[0,1])
draw_base(ax, flare=False, pad=True)
for ang in (10.0, 190.0): draw_finger(ax, ang)
draw_hub(ax); track(ax, "R5")
ax.add_patch(Circle(PARK, BALL_R, facecolor=C_BALL, edgecolor="#8a6d1a", lw=1.4, alpha=0.9, zorder=8))
ax.annotate("保留 225° 直挡墙\n（不加喇叭件）", xy=fp(226.0, 97.5), xytext=(-124, 52), fontsize=9.2,
            color="#2a6f97", arrowprops=dict(arrowstyle="->", color="#2a6f97", lw=1.2), zorder=11)
ax.annotate("D 球窝垫块（新增）\n抬高 6.8 mm", xy=(-2.0, PAD_TOP), xytext=(16, 40), fontsize=9.4,
            color="#6a3d9a", arrowprops=dict(arrowstyle="->", color="#6a3d9a", lw=1.2), zorder=11)
ax.annotate("指片 θ=350°", xy=fp(10.0, 56.0), xytext=(44, 150), fontsize=9, color=C_PADDLE_E,
            arrowprops=dict(arrowstyle="->", color=C_PADDLE_E, lw=1.1), zorder=11)
ax.annotate("指片 θ=170°", xy=fp(190.0, 56.0), xytext=(-124, 150), fontsize=9, color=C_PADDLE_E,
            arrowprops=dict(arrowstyle="->", color=C_PADDLE_E, lw=1.1), zorder=11)
ax.annotate("停位球（二指停车位）", xy=(PARK[0]-BALL_R*0.85, PARK[1]-BALL_R*0.5), xytext=(30, 26),
            fontsize=9, color="#7a5c10", arrowprops=dict(arrowstyle="->", color="#7a5c10", lw=1.0), zorder=11)
ax.plot([], [], color="#8e44ad", lw=2.3, label="球心轨迹（实测）")
ax.legend(loc="upper right", fontsize=8.6, frameon=False)
axis_setup(ax, (-128, 178), (-12, 205), "(b) R5 = 二指 350°/170° + D 球窝抬高 6.8（新增平垫块）")
ax.text(0.985, 0.03, "双入口门槛 0.44 N·m（@200rpm）；90 rpm 需 0.50 N·m", transform=ax.transAxes, ha="right",
        fontsize=9.4, color="#2f6b2a", bbox=dict(fc="#eef7ec", ec="#2f6b2a", lw=0.9, alpha=0.95))

# ---------------- (c) 球窝区放大 ----------------
ax = fig.add_subplot(gs[1,0])
draw_base(ax, pad=True, guide=False, trackline=False)
for ang in (10.0, 190.0): draw_finger(ax, ang, z=3, alpha=0.85)
c2 = (-2.0, pv2.tray_top_z(-2.0) + BALL_R)
c5 = (-2.0, PAD_TOP + BALL_R)
ax.add_patch(Circle(c2, BALL_R, facecolor="none", edgecolor="#a33b20", lw=1.8, ls=(0,(6,3)), zorder=4))
ax.add_patch(Circle(c5, BALL_R, facecolor=C_BALL, edgecolor="#6a3d9a", lw=1.8, alpha=0.30, zorder=3))
ax.plot([-52, c2[0]], [c2[1], c2[1]], color="#a33b20", lw=0.9, ls=":", zorder=4)
ax.plot([-52, c5[0]], [c5[1], c5[1]], color="#6a3d9a", lw=0.9, ls=":", zorder=4)
ax.annotate("", xy=(-48, c5[1]), xytext=(-48, c2[1]),
            arrowprops=dict(arrowstyle="<->", color="#6a3d9a", lw=1.8), zorder=12)
ax.text(-50, 0.5*(c2[1]+c5[1]), "6.8", fontsize=10.5, color="#6a3d9a", fontweight="bold", ha="right", va="center", zorder=12)
ax.annotate("无垫块 z=53.1", xy=(c2[0]+BALL_R*0.72, c2[1]+BALL_R*0.62), xytext=(34, 34), fontsize=9.2,
            color="#a33b20", arrowprops=dict(arrowstyle="->", color="#a33b20", lw=1.0), zorder=12)
ax.annotate("有垫块 z=59.9", xy=(c5[0]+BALL_R*0.70, c5[1]+BALL_R*0.66), xytext=(34, 86), fontsize=9.2,
            color="#6a3d9a", arrowprops=dict(arrowstyle="->", color="#6a3d9a", lw=1.0), zorder=12)
ax.text(-63, 143, "D 的作用（球窝窗口 x = −17…13）：把球抬高 6.8 mm，\n实测该窗口内球心 z 由 ≈54.3–56.5 升到 ≈58.7–60.5\n（弹跳损耗导致实测抬高约 4 mm）→ 脱离叶尖端面刮擦",
        fontsize=9.2, color="#444", va="top", zorder=12)
ax.annotate("垫块 30×108×12.8\n顶面 z = 24.33", xy=(PAD_X1, PAD_TOP), xytext=(4, 12), fontsize=9,
            color="#6a3d9a", va="top", arrowprops=dict(arrowstyle="->", color="#6a3d9a", lw=1.1), zorder=12)
ax.annotate("托板顶面 z=17.53", xy=(-8.0, pv2.tray_top_z(-8.0)), xytext=(30, 16), fontsize=9,
            color=C_TRAY_E, arrowprops=dict(arrowstyle="->", color=C_TRAY_E, lw=1.0), zorder=12)
axis_setup(ax, (-70, 62), (-6, 152), "(c) 球窝区放大 —— D 的作用：把球抬高 6.8 mm 脱离端面夹持")

# ---------------- (d) 通过性矩阵 ----------------
ax = fig.add_subplot(gs[1,1]); ax.axis("off"); ax.set_xlim(0,1); ax.set_ylim(0,1)
ax.set_title("(d) 离散扭矩扫描 —— 两个入口高度 x = 145 / 138（各 7 s MuJoCo）", fontsize=12, pad=8)
cols = ["扭矩限幅\nN·m", "R2 @200rpm\n145/138", "R5 @200rpm\n145/138", "R2 @90rpm\n145/138", "R5 @90rpm\n145/138"]
data = [("0.38","\u00d7 \u00d7","\u00d7 \u00d7","\u2014","\u2014"),
        ("0.40","\u00d7 \u00d7","\u221a \u00d7","\u2014","\u00d7 \u00d7"),
        ("0.42","\u00d7 \u00d7","\u221a \u00d7","\u2014","\u00d7 \u00d7"),
        ("0.44","\u00d7 \u00d7","\u221a \u221a","\u2014","\u221a \u00d7"),
        ("0.46","\u221a \u00d7","\u221a \u221a","\u2014","\u221a \u00d7"),
        ("0.48","\u221a \u00d7","\u221a \u221a","\u2014","\u221a \u00d7"),
        ("0.50","\u221a \u221a","\u221a \u221a","\u00d7 \u00d7","\u221a \u221a"),
        ("0.60","\u2014","\u2014","\u221a \u221a","\u2014")]
x0, y0, dx, dy = 0.10, 0.86, 0.185, 0.083
for j, c in enumerate(cols):
    ax.text(x0+j*dx, y0+0.055, c, ha="center", va="center", fontsize=9.4, fontweight="bold", color="#333")
for i, row in enumerate(data):
    yy = y0 - i*dy
    ax.add_patch(Rectangle((0.02, yy-0.5*dy+0.006), 0.96, dy-0.012,
                 facecolor="#f7f7f7" if i % 2 else "white", edgecolor="#e0e0e0", lw=0.6, zorder=0))
    for j, v in enumerate(row):
        col = "#2f6b2a" if v.startswith("\u221a") else ("#a33b20" if v.startswith("\u00d7") else "#999")
        ax.text(x0+j*dx, yy, v, ha="center", va="center", fontsize=11.5 if j else 9.6,
                color=col, fontweight="bold" if j and v != "\u2014" else "normal", zorder=2)
ax.text(0.02, 0.145, "结论：R5 的双入口门槛比 R2 低 0.06 N·m（@200 rpm），90 rpm 下低 0.10 N·m；\n"
        "并且 R5 不需要新增喇叭件（保留原 225° 直墙），只多一块 30×108×12.8 的平垫块。",
        fontsize=9.6, color="#333", va="top")
ax.text(0.02, 0.055, "\u00d7 = 未发射   \u221a = 完成发射   \u2014 = 未测。两者飞轮同为 1620 rpm、球同初值。",
        fontsize=8.4, color="#777", va="top")

lg = [Line2D([],[],marker="s",ls="",ms=10,mfc=C_SHELL,mec=C_SHELL_E,label="外罩"),
      Line2D([],[],marker="s",ls="",ms=10,mfc=C_TRAY,mec=C_TRAY_E,label="托板 + 立柱"),
      Line2D([],[],marker="s",ls="",ms=10,mfc=C_FLARE,mec="#a33b20",label="A 唇口喇叭（仅 R2）"),
      Line2D([],[],marker="s",ls="",ms=10,mfc=C_PAD,mec="#6a3d9a",label="D 球窝垫块（仅 R5）"),
      Line2D([],[],marker="s",ls="",ms=10,mfc=C_PADDLE,mec=C_PADDLE_E,label="拨杆指片（二指 350°/170°）"),
      Line2D([],[],marker="o",ls="",ms=11,mfc=C_BALL,mec="#8a6d1a",label="POLLEN 球 D71.12"),
      Line2D([],[],ls=(0,(5,3)),color="#c0392b",label="球心轨道 R58.4"),
      Line2D([],[],ls=(0,(6,4)),color=C_GUIDE,label="导向 / 52° 发射通道")]
fig.legend(handles=lg, loc="lower center", ncol=8, fontsize=9.2, frameon=False, bbox_to_anchor=(0.5, 0.004))
out = Path("simulation/mujoco/out/section_r2_vs_r5_zh.png")
fig.savefig(out, facecolor="white"); print("已生成", out)
