# -*- coding: utf-8 -*-
"""T06 POLLEN V2 送球段剖面示意图：现状 vs 方案 R2（二指 350/170 + A 唇口喇叭）"""
import math, sys, importlib.util
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
R_IN, R_OUT = pv2.R_IN, pv2.R_OUT
BALL_R = pv2.BALL_R
R_CARRY = pv2.R_CARRY

C_SHELL   = "#9fc6e0"
C_SHELL_E = "#2a6f97"
C_TRAY    = "#b9d8b0"
C_TRAY_E  = "#3f7d3a"
C_PADDLE  = "#f2a65a"
C_PADDLE_E= "#b5651d"
C_BALL    = "#e8c33a"
C_FLARE   = "#e07a5f"
C_GUIDE   = "#b0b0b0"

def fp(ang, r):
    """极坐标(m,deg) -> 世界 XZ"""
    a = math.radians(ang)
    return (C[0] + r*math.cos(a), C[1] + r*math.sin(a))

def rect_xz(x0, x1, z0, z1):
    return Polygon([(x0,z0),(x1,z0),(x1,z1),(x0,z1)], closed=True)

def finger(cx, cz, ang_deg, r0, r1, halfw):
    """拨杆指片的一部分：局部 +X 指向径向 r，局部 +Z 切向。"""
    a = math.radians(ang_deg)
    ux, uz = math.cos(a), -math.sin(a)
    tx, tz = math.sin(a),  math.cos(a)
    pts = [(cx+u*ux+v*tx, cz+u*uz+v*tz) for (u,v) in ((r0,-halfw),(r1,-halfw),(r1,halfw),(r0,halfw))]
    return Polygon(pts, closed=True)

def draw_finger(ax, ang, fc=C_PADDLE, ec=C_PADDLE_E, lw=1.2, alpha=1.0, z=6):
    for (r0,r1,hw) in ((14,46,5),(46,58,15),(56,60,17)):
        p = finger(C[0], C[1], ang, r0, r1, hw)
        p.set(facecolor=fc, edgecolor=ec, lw=lw, alpha=alpha, zorder=z)
        ax.add_patch(p)

def draw_base(ax, flare=False, show_track=True, guide=True):
    # 外罩扇形 142..225
    w = Wedge(C, R_OUT, 142, 225, width=R_OUT-R_IN, facecolor=C_SHELL, edgecolor=C_SHELL_E, lw=1.4, zorder=4)
    ax.add_patch(w)
    # 出球端面 / 唇口端面
    for ang, lab in ((142.0,"出球 142°"), (225.0,"唇口 225°")):
        p = pv2.polar(0.5*(R_IN+R_OUT), ang)
        rr = Rectangle((p[0]-R_OUT+R_IN, p[1]-1.5), R_OUT-R_IN, 3.0, angle=-ang,
                       facecolor=C_SHELL, edgecolor=C_SHELL_E, lw=1.2, zorder=5)
        ax.add_patch(rr)
    if flare:
        for (am, rin) in ((227.5,95.5),(231.5,99.5),(235.5,103.5)):
            fw = Wedge(C, rin+7.0, am-2.7, am+2.7, width=7.0,
                       facecolor=C_FLARE, edgecolor="#a33b20", lw=1.2, zorder=6)
            ax.add_patch(fw)
    # 托板（含 5° 倾斜，顶面 z = PIVOT_Z + (x-PIVOT_X) tan5）
    nx, nz = pv2.normal(-pv2.TILT)
    x0, x1 = pv2.TRAY_X0, pv2.TRAY_X1
    t0 = (x0, pv2.tray_top_z(x0)); t1 = (x1, pv2.tray_top_z(x1))
    poly = [t0, t1, (t1[0]-nx*pv2.TRAY_T, t1[1]-nz*pv2.TRAY_T), (t0[0]-nx*pv2.TRAY_T, t0[1]-nz*pv2.TRAY_T)]
    ax.add_patch(Polygon(poly, closed=True, facecolor=C_TRAY, edgecolor=C_TRAY_E, lw=1.3, zorder=4))
    # 立柱
    ax.add_patch(rect_xz(pv2.STRUT_X0, pv2.STRUT_X1, pv2.STRUT_Z0, pv2.STRUT_Z1))
    for p in ax.patches[-1:]:
        p.set(facecolor=C_TRAY, edgecolor=C_TRAY_E, lw=1.2, zorder=4)
    # 导向（52° 通道，淡）
    if guide:
        for (s, e, L, a) in pv2.SEGS:
            ax.plot([s[0], e[0]], [s[1], e[1]], color=C_GUIDE, lw=1.6, ls=(0,(6,4)), zorder=2)
    if show_track:
        th = [142.0 + (225.0-142.0)*i/120.0 for i in range(121)]
        ax.plot([fp(t,R_CARRY)[0] for t in th], [fp(t,R_CARRY)[1] for t in th],
                color="#c0392b", lw=1.3, ls=(0,(5,3)), zorder=5)
        a = math.radians(160.0)
        ax.annotate("球心轨道 R58.4", xy=fp(160.0, R_CARRY),
                    xytext=(C[0]+30, C[1]-62), color="#c0392b", fontsize=9,
                    arrowprops=dict(arrowstyle="->", color="#c0392b", lw=1.0), zorder=9)

def draw_hub(ax):
    ax.add_patch(Circle(C, 18.0, facecolor=C_PADDLE, edgecolor=C_PADDLE_E, lw=1.3, zorder=7))
    ax.plot(*C, marker="+", color="#333", ms=10, mew=1.6, zorder=8)

def axis_setup(ax, xlim, zlim, title=None, box=True):
    ax.set_aspect("equal")
    ax.set_xlim(*xlim); ax.set_ylim(*zlim)
    if title: ax.set_title(title, fontsize=12, pad=8)
    ax.grid(True, color="#e6e6e6", lw=0.7)
    ax.set_axisbelow(True)
    for s in ax.spines.values(): s.set_color("#bbb")
    ax.tick_params(labelsize=8, colors="#555")

# ------------------------------------------------------------------ 画布
fig = plt.figure(figsize=(16.2, 11.0), dpi=130)
fig.suptitle("T06 POLLEN V2 送球段剖面示意图 —— 现状 vs 方案 R2（二指 350°/170° + A 唇口喇叭）", fontsize=16, y=0.985)
sub = "剖面 = 拨杆轴心所在的 XZ 平面；单位 mm；数据基准 simulation/mujoco/pollen_v2_sim.py（V2 几何）"
fig.text(0.5, 0.952, sub, ha="center", fontsize=10, color="#666")

gs = fig.add_gridspec(2, 2, left=0.055, right=0.975, top=0.925, bottom=0.055, hspace=0.22, wspace=0.16)

REST = (111.87, 63.08)

# ---- (a) 现状 -------------------------------------------------------
ax = fig.add_subplot(gs[0,0])
draw_base(ax, flare=False)
for ang in (18.0, 138.0, 258.0):
    draw_finger(ax, ang)
draw_hub(ax)
ax.add_patch(Circle(REST, BALL_R, facecolor=C_BALL, edgecolor="#8a6d1a", lw=1.4, alpha=0.95, zorder=8))
ax.annotate("停位：球被指片端面抵在托板上\nr≈95.5 mm（远未到 R58.4 球道）",
            xy=REST, xytext=(-124, 158), fontsize=9.2, color="#a33b20",
            arrowprops=dict(arrowstyle="->", color="#a33b20", lw=1.3), zorder=10)
ax.annotate("225° 直挡墙", xy=fp(225.0, 97.5), xytext=(-118, 92), fontsize=9,
            arrowprops=dict(arrowstyle="->", color="#2a6f97", lw=1.1), zorder=10)
axis_setup(ax, (-125, 175), (-15, 200), "(a) 现状：三指 342°/222°/102° + 225° 直挡墙")
ax.text(0.985, 0.03, "门檻 0.94 N·m @120–140 rpm", transform=ax.transAxes, ha="right",
        fontsize=10, color="#a33b20", bbox=dict(fc="#fff2ec", ec="#a33b20", lw=0.8, alpha=0.95))

# ---- (b) 方案 R2 ----------------------------------------------------
ax = fig.add_subplot(gs[0,1])
draw_base(ax, flare=True)
for ang in (10.0, 190.0):
    draw_finger(ax, ang)
draw_hub(ax)
ax.add_patch(Circle(REST, BALL_R, facecolor=C_BALL, edgecolor="#8a6d1a", lw=1.4, alpha=0.35, zorder=8))
ax.annotate("二指停位让开球道：球自滚到唇口\nθ≈235° r≈59.5 mm，落在球道上",
            xy=fp(232.0, 62.0), xytext=(-92, 152), fontsize=9.5, color="#2f6b2a",
            arrowprops=dict(arrowstyle="->", color="#2f6b2a", lw=1.3), zorder=10)
ax.annotate("A 唇口喇叭\n（三段台阶外扩）", xy=fp(234.0, 106.0), xytext=(-125, 55), fontsize=9.5,
            color="#a33b20", arrowprops=dict(arrowstyle="->", color="#a33b20", lw=1.2), zorder=10)
ax.annotate("指片 350°", xy=fp(350.0, 45.0), xytext=(60, 150), fontsize=9, color=C_PADDLE_E,
            arrowprops=dict(arrowstyle="->", color=C_PADDLE_E, lw=1.1), zorder=10)
ax.annotate("指片 170°", xy=fp(170.0, 45.0), xytext=(78, 55), fontsize=9, color=C_PADDLE_E,
            arrowprops=dict(arrowstyle="->", color=C_PADDLE_E, lw=1.1), zorder=10)
axis_setup(ax, (-125, 175), (-15, 200), "(b) 方案 R2：二指 350°/170° + A 唇口喇叭")
ax.text(0.985, 0.03, "门檻 0.46 N·m @90 rpm（稳健 2/2）", transform=ax.transAxes, ha="right",
        fontsize=10, color="#2f6b2a", bbox=dict(fc="#eef7ec", ec="#2f6b2a", lw=0.9, alpha=0.95))

# ---- (c) 唇口放大 ---------------------------------------------------
ax = fig.add_subplot(gs[1,0])
ax.add_patch(Wedge(C, R_OUT, 208, 225, width=R_OUT-R_IN, facecolor=C_SHELL, edgecolor=C_SHELL_E, lw=1.4, zorder=4))
ax.add_patch(Rectangle((fp(225.0,0.5*(R_IN+R_OUT))[0]-(R_OUT-R_IN), fp(225.0,0.5*(R_IN+R_OUT))[1]-1.5),
                       R_OUT-R_IN, 3.0, angle=-225.0, facecolor=C_SHELL, edgecolor=C_SHELL_E, lw=1.2, zorder=5))
for (am, rin) in ((227.5,95.5),(231.5,99.5),(235.5,103.5)):
    ax.add_patch(Wedge(C, rin+7.0, am-2.7, am+2.7, width=7.0,
                       facecolor=C_FLARE, edgecolor="#a33b20", lw=1.2, zorder=6))
ax.plot([fp(t,R_CARRY)[0] for t in [220+ i*0.2 for i in range(120)]],
        [fp(t,R_CARRY)[1] for t in [220+ i*0.2 for i in range(120)]], color="#c0392b", lw=1.2, ls=(0,(5,3)), zorder=5)
ax.add_patch(Circle(fp(222.0, R_CARRY+BALL_R), BALL_R, facecolor=C_BALL, edgecolor="#8a6d1a", lw=1.2, alpha=0.35, zorder=3))
for (am, rin, lab) in ((227.5,95.5,"227.5° r_in 95.5"),(231.5,99.5,"231.5° r_in 99.5"),(235.5,103.5,"235.5° r_in 103.5")):
    xy = fp(am, rin+7.0)
    ax.annotate(lab, xy=xy, xytext=(xy[0]+6, xy[1]+16), fontsize=8.6, color="#a33b20",
                arrowprops=dict(arrowstyle="->", color="#a33b20", lw=0.9), zorder=10)
ax.annotate("原 225° 直挡墙\n（方案 A 中删除）", xy=fp(225.0, R_IN+3.5), xytext=(-28, 118),
            fontsize=9, color="#2a6f97", arrowprops=dict(arrowstyle="->", color="#2a6f97", lw=1.1), zorder=9)
ax.annotate("三段台阶 = 让球沿外扩斜坡\n平顺爬出唇口，降低起拔力", xy=(-58, 22), fontsize=9.2, color="#444")
axis_setup(ax, (-62, 12), (18, 132), "(c) 唇口局部放大 —— 现状直墙 vs A 三段台阶")

# ---- (d) 停位/接球区放大 ---------------------------------------------
ax = fig.add_subplot(gs[1,1])
draw_base(ax, flare=False, show_track=True)
for ang in (18.0, 138.0):
    draw_finger(ax, ang, alpha=0.35, z=5)
ax.annotate("现状指片 342°\n（端面挡住球）", xy=fp(342.0, 50.0), xytext=(38, 92), fontsize=9,
            color="#a33b20", arrowprops=dict(arrowstyle="->", color="#a33b20", lw=1.1), zorder=10)
for ang in (10.0, 190.0):
    draw_finger(ax, ang, fc="#7fbf7f", ec="#2f6b2a", z=6)
ax.annotate("方案二指 350°\n（让开球道）", xy=fp(350.0, 50.0), xytext=(70, 132), fontsize=9,
            color="#2f6b2a", arrowprops=dict(arrowstyle="->", color="#2f6b2a", lw=1.1), zorder=10)
draw_hub(ax)
ax.add_patch(Circle(REST, BALL_R, facecolor=C_BALL, edgecolor="#8a6d1a", lw=1.4, alpha=0.9, zorder=8))
ax.annotate("停位球心 (111.9, 63.1)", xy=REST, xytext=(52, 22), fontsize=9,
            arrowprops=dict(arrowstyle="->", color="#7a5c10", lw=1.0), zorder=10)
ax.annotate("托板 5°", xy=(90.0, pv2.tray_top_z(90.0)), xytext=(102, 12), fontsize=9, color=C_TRAY_E)
ax.annotate("拨杆轴心 C (29.49, 111.46)", xy=C, xytext=(-118, 158), fontsize=9, color="#555",
            arrowprops=dict(arrowstyle="->", color="#888", lw=1.0), zorder=10)
axis_setup(ax, (-60, 175), (-8, 190), "(d) 停位区放大 —— 指片让开球道（橙=现状，绿=方案）")

lg = [Line2D([],[],marker="s",ls="",ms=10,mfc=C_SHELL,mec=C_SHELL_E,label="外罩 + 托板（一体）"),
      Line2D([],[],marker="s",ls="",ms=10,mfc=C_FLARE,mec="#a33b20",label="A 唇口喇叭（新增）"),
      Line2D([],[],marker="s",ls="",ms=10,mfc=C_PADDLE,mec=C_PADDLE_E,label="拨杆指片（现状相位）"),
      Line2D([],[],marker="s",ls="",ms=10,mfc="#7fbf7f",mec="#2f6b2a",label="拨杆指片（方案相位）"),
      Line2D([],[],marker="o",ls="",ms=11,mfc=C_BALL,mec="#8a6d1a",label="POLLEN 球 D71.12"),
      Line2D([],[],ls=(0,(5,3)),color="#c0392b",label="球心轨道 R58.4"),
      Line2D([],[],ls=(0,(6,4)),color=C_GUIDE,label="导向 / 52° 发射通道")]
fig.legend(handles=lg, loc="lower center", ncol=7, fontsize=9.5, frameon=False, bbox_to_anchor=(0.5, 0.003))

out = Path("simulation/mujoco/out/section_options_zh.png")
fig.savefig(out, facecolor="white")
print("已生成", out)
