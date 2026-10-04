# -*- coding: utf-8 -*-
import sys, math, importlib.util
sys.stdout.reconfigure(encoding="utf-8")
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np
from matplotlib.patches import Circle, Wedge, Rectangle, FancyArrow
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
spec = importlib.util.spec_from_file_location("pv2", r"simulation/mujoco/pollen_v2_sim.py")
pv2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(pv2)
import mujoco
C = (pv2.PADDLE_CX, pv2.PADDLE_CZ); R_IN, R_OUT = pv2.R_IN, pv2.R_OUT

# ---------- 图 A ----------
def run(bx, rpm, fr, sec=7.0):
    xml, ctrl = pv2.build_xml(1620.0, -1, rpm*2*math.pi/60.0, bx, pv2.tray_top_z(bx)+pv2.BALL_R)
    xml = xml.replace('-1.5 1.5"', '-%g %g"' % (fr, fr))
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
    aid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "paddle_vel")
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    dt = m.opt.timestep; n = int(round(sec/dt)); tq = np.zeros(n); rr = np.zeros(n)
    for i in range(n):
        mujoco.mj_step(m, d); tq[i] = abs(float(d.actuator_force[aid]))
        p = d.xpos[bid]; rr[i] = math.hypot(float(p[0])*1000.-C[0], float(p[2])*1000.-C[1])
    return tq, dt, rr

tq, dt, rr = run(145.0, 200.0, 20.0)
t = np.arange(len(tq))*dt
fig, ax = plt.subplots(1, 2, figsize=(13.2, 4.6))
a = ax[0]
a.plot(t, tq, lw=0.7, color="#1f4e79")
a.axhline(1.0, color="#c00000", ls="--", lw=1.3, label="实测发射门槛 ≈1.0 N·m")
a.axhline(1.638, color="#2e7d32", ls=":", lw=1.3, label="SRS V2 Balanced 堵转 1.638 N·m")
a.axhline(0.608, color="#e07b00", ls=":", lw=1.3, label="SRS V2 UltraSpeed 堵转 0.608 N·m")
a.axvline(0.441, color="#888", lw=0.8)
a.annotate("t=0.44 s 峰值 1.71 N·m\n≈ kv×ω → 拨杆被完全卡停\n(球同时被叶片/托板/唇口夹住)",
           xy=(0.441, 1.71), xytext=(0.55, 1.45), fontsize=9,
           arrowprops=dict(arrowstyle="->", color="#333"))
a.set_xlim(0, 1.2); a.set_ylim(0, 1.9)
a.set_xlabel("时间 t (s)"); a.set_ylabel("拨杆关节力矩 |τ| (N·m)")
a.set_title("(a) 实测拨杆扭矩（200 rpm，球从托板滚入）", fontsize=11)
a.legend(fontsize=8, loc="upper right"); a.grid(alpha=.25)

b = ax[1]
sp = np.linspace(0.1, 320, 200)
b.plot(sp, np.maximum(0, 1.638*(1-sp/83.33)), color="#2e7d32", lw=2, label="SRS V2 Balanced @7.4 V")
b.plot(sp, np.maximum(0, 0.608*(1-sp/285.7)), color="#e07b00", lw=2, label="SRS V2 UltraSpeed @7.4 V")
b.add_patch(Rectangle((105, 1.0), 215, 1.4, color="#1f4e79", alpha=.18))
b.text(215, 1.72, "工作区（需同时满足）\nτ ≥ 1.0 N·m  且  n ≥ 105 rpm", ha="center", fontsize=9.5, color="#1f4e79")
b.plot([105, 320, 320, 105, 105], [1.0, 1.0, 2.4, 2.4, 1.0], color="#1f4e79", lw=1.2)
b.set_xlim(0, 320); b.set_ylim(0, 2.4)
b.set_xlabel("输出转速 n (rpm)"); b.set_ylabel("输出扭矩 τ (N·m)")
b.set_title("(b) 舵机能力线 vs 送球需求（两条线都不进入工作区）", fontsize=11)
b.legend(fontsize=9, loc="upper right"); b.grid(alpha=.25)
for X, Y, s in ((83.3, 0.0, "Balanced 空载 83 rpm\n→ 远低于 105 rpm"), (285.7, 0.0, "UltraSpeed 堵转 0.61\n→ 远低于 1.0 N·m")):
    b.annotate(s, xy=(X, Y), xytext=(X-60, 0.55), fontsize=8.5, color="#444",
               arrowprops=dict(arrowstyle="->", color="#888"))
plt.tight_layout(); plt.savefig("simulation/mujoco/out/servo_verdict_zh.png", dpi=150)
print("saved servo_verdict_zh.png")

# ---------- 图 B：现状机理 + 方案 ----------
def section(ax, title, mode):
    ax.set_aspect("equal"); ax.set_xlim(-95, 120); ax.set_ylim(-10, 190); ax.axis("off")
    ax.add_patch(Wedge(C, R_OUT, pv2.A_EXIT, pv2.A_LIP, width=R_OUT-R_IN, fc="#cfe0ef", ec="#5b7f9e", lw=1.0))
    tx = np.array([-56, 150]); tz = pv2.PIVOT_Z + (tx-pv2.PIVOT_X)*math.tan(math.radians(pv2.TILT))
    ax.plot(tx, tz, color="#5b7f9e", lw=3, solid_capstyle="butt")
    ax.plot(tx, tz-6, color="#5b7f9e", lw=2)
    if mode in ("base", "opt1"):
        lx, lz = pv2.polar(97.46, 225); q = math.radians(225)
        ax.plot([lx+3.5*math.cos(q), lx-3.5*math.cos(q)], [lz+3.5*math.sin(q), lz-3.5*math.sin(q)],
                color="#c00000" if mode=="base" else "#2e7d32", lw=4)
    for i, ang in enumerate((pv2.PADDLE_PHASE, pv2.PADDLE_PHASE+120, pv2.PADDLE_PHASE+240)):
        col = "#f0a020" if (mode!="base" or i!=2) else "#c00000"
        ax.add_patch(Wedge(C, 60, ang-13, ang+13, width=14, fc=col, ec="#8a5a00", lw=.8))
        ax.add_patch(Wedge(C, 46, ang-5.7, ang+5.7, fc=col, ec="#8a5a00", lw=.8))
    ax.add_patch(Circle(C, 18, fc="#888", ec="k", lw=.8))
    ax.plot(*C, "k+", ms=8)
    bx_, bz_ = -1.56, 53.20
    ax.add_patch(Circle((bx_, bz_), pv2.BALL_R, fc="#d8f0c0", ec="#3a6b1a", lw=1.4))
    ax.text(C[0], C[1]-85, "拨杆轴 / 外罩圆心", ha="center", fontsize=8, color="#333")
    ax.set_title(title, fontsize=9.5)
    return (bx_, bz_)

fig, axs = plt.subplots(1, 5, figsize=(20, 4.4))
section(axs[0], "① 现状：球停在托板+225°挡墙的 V 形硬窝里\n叶片推球 = 逼球翻过挡墙 → 卡停 1.7 N·m", "base")
axs[0].annotate("红色 = 硬挡墙\n(壳唇端面)", xy=(pv2.polar(97.46,225)), xytext=(-90, 95), fontsize=8.5, color="#c00000",
                arrowprops=dict(arrowstyle="->", color="#c00000"))
axs[0].annotate("球底距托板仅 0.07 mm\n(托板伸到球窝正下方)", xy=(-1.5, 17.6), xytext=(-80, 30), fontsize=8.5, color="#c00000",
                arrowprops=dict(arrowstyle="->", color="#c00000"))

section(axs[1], "方案A：225°挡墙改斜楔/圆弧过渡\n球被平滑导入外罩，不再翻越", "opt1")
axs[2].remove()
ax3 = fig.add_subplot(1, 5, 3); section(ax3, "方案B：托板末端缩进 10–15 mm 并下倾\n球窝下方让空，消除硬夹", "opt2")
ax3.add_patch(Rectangle((-56, 10), 52, 8, color="#2e7d32", alpha=.35))
ax3.annotate("托板末端退到此处", xy=(-28, 15), xytext=(-88, 60), fontsize=8.5, color="#2e7d32",
             arrowprops=dict(arrowstyle="->", color="#2e7d32"))
axs[3].remove(); ax4 = fig.add_subplot(1, 5, 4)
section(ax4, "方案C：叶片前缘卸载 + 端角倒圆\n300°–330° 区段外缘半径 ≤58.4", "opt3")
ax4.add_patch(Wedge(C, 60, 288, 342, width=16, fc="none", ec="#2e7d32", lw=2.2, ls="--"))
ax4.annotate("削掉这一段\n(球还在托板上时不接触)", xy=(C[0]+52*math.cos(math.radians(315)), C[1]+52*math.sin(math.radians(315))),
             xytext=(50, 30), fontsize=8.5, color="#2e7d32", arrowprops=dict(arrowstyle="->", color="#2e7d32"))
axs[4].remove(); ax5 = fig.add_subplot(1, 5, 5)
section(ax5, "方案D：球窝改单侧斜坡（逃逸窝）\n只留托板+与出球方向相切的斜面", "opt4")
ax5.plot([-40, 6], [22, 58], color="#2e7d32", lw=3.5)
ax5.annotate("切向斜坡代替挡墙\n球一推就走", xy=(-8, 44), xytext=(-90, 95), fontsize=8.5, color="#2e7d32",
             arrowprops=dict(arrowstyle="->", color="#2e7d32"))
fig.suptitle("T06 POLLEN V2 送球段：夹持机理与接触几何改善方案（前视剖面，单位 mm）", fontsize=13)
plt.tight_layout(rect=[0, 0, 1, 0.94]); plt.savefig("simulation/mujoco/out/contact_fix_options_zh.png", dpi=150)
print("saved contact_fix_options_zh.png")
