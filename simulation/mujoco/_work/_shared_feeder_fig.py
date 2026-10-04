# -*- coding: utf-8 -*-
"""Shared feeder (NECTAR + POLLEN) design figure: section, blade layout, traces, grid."""
import math, sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Wedge
import numpy as np

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

AX, AZ = 29.49, 111.46
PIVOT_X, PIVOT_Z, TILT = -0.806, 0.423, 5.0
R_IN, SHELL_WALL, TRAY_T = 107.974, 7.0, 6.0
TRAY_X0, TRAY_X1 = 38.901, 150.0
A_EXIT, A_LIP = 142.0, 275.0
HUB_R = 12.0
ANGLE = 52.0
WHEEL_OD = 96.0
BALLS = {"NECTAR": (45.974, 82.0), "POLLEN": (35.56, 64.0)}
BLUE, GREEN, ORANGE, RED, GREY = "#1f77b4", "#2e8b3d", "#eb8a1e", "#d62728", "#8b9098"

def polar(r, a):
    return (AX + r*math.cos(math.radians(a)), AZ + r*math.sin(math.radians(a)))

def tray_top_z(x):
    return PIVOT_Z + (x - PIVOT_X)*math.tan(math.radians(TILT))

# shooter frame (pollen_v2_sim constants)
SEGS = [((-150.0, 16.0), 70.0, 0.0), (None, 55.0, 26.0), (None, 70.0, ANGLE)]
_s = SEGS[0][0]
for i, (_, L, a) in enumerate(SEGS):
    e = (_s[0] + L*math.cos(math.radians(a)), _s[1] + L*math.sin(math.radians(a)))
    if i == 2: G52 = (_s, e)
    _s = e
N52 = (-math.sin(math.radians(ANGLE)), math.cos(math.radians(ANGLE)))
T52 = (math.cos(math.radians(ANGLE)), math.sin(math.radians(ANGLE)))
TC = (G52[1][0] + 55.0*N52[0], G52[1][1] + 55.0*N52[1])
SO = (TC[0] + 135.0*T52[0], TC[1] + 135.0*T52[1])

def wheel_c(sign, half):
    return (SO[0] - sign*half*math.sin(math.radians(ANGLE)),
            SO[1] + sign*half*math.cos(math.radians(ANGLE)))

# ---------------------------------------------------------------- sim run
def run_trace(ball_r, ball_m, nip, xc, hold=1.8, sw=248.0, rpm=290.0, t_end=6.0):
    import opt_lib as ol, r10_cradle as R10, mujoco
    pv2 = ol.pv2
    T_STALL = 0.530
    pv2.HALF_SPACING = nip/2.0 + WHEEL_OD/2.0
    pv2.R_CARRY = R_IN - ball_r
    pv2.PIVOT_X, pv2.PIVOT_Z = PIVOT_X, PIVOT_Z
    pv2.R_IN = R_IN; pv2.R_OUT = R_IN + pv2.SHELL_WALL
    R10.R_MID = R_IN + 3.5
    pv2.BALL_R = ball_r; pv2.BALL_MASS = ball_m
    pv2.static_geoms = (lambda: R10.stat(TRAY_X0, A_LIP, tray_x1=TRAY_X1))
    def pf():
        out = [("hub", (0.,0.,0.), (HUB_R, 17.), 0.0, "cylY")]
        for i, a in enumerate((330.0, 150.0), 1):
            out += [("arm_%d" % i, (28.,0.,0.), (18.,9.,5.), a, "box"),
                    ("blade_%d" % i, (52.,0.,0.), (6., pv2.PADDLE_W/2., 15.), a, "box"),
                    ("flex_%d" % i, (58.,0.,0.), (2., pv2.PADDLE_W/2., 17.), a, "box")]
        return out
    pv2.paddle_parts = pf
    bx = xc - ball_r*math.sin(math.radians(TILT))
    bz = tray_top_z(xc) + ball_r*math.cos(math.radians(TILT))
    w = rpm*2*math.pi/60.0
    xml, ctrl = pv2.build_xml(1620.0, -1, 0.0, bx, bz)
    xml = xml.replace('kv="0.08"', 'kv="%.6f"' % (T_STALL/w))
    xml = xml.replace('forcerange="-1.5 1.5"', 'forcerange="-%g %g"' % (T_STALL, T_STALL))
    xml = xml.replace('class="ball"><geom friction="1.0 0.02 0.0001"',
                      'class="ball"><geom friction="0.4 0.02 0.0001"')
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    aid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "paddle_vel")
    jid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "paddle_joint")
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    d.ctrl[:] = [ctrl[0], ctrl[1], 0.0]; mujoco.mj_forward(m, d)
    dt = m.opt.timestep; n = int(t_end/dt); released = False
    T, R, A = [], [], []
    for i in range(n):
        t = i*dt; J = math.degrees(d.qpos[jid])
        if t < hold: d.ctrl[aid] = 0.0
        elif not released and J < sw: d.ctrl[aid] = w
        else: released = True; d.ctrl[aid] = 0.0
        mujoco.mj_step(m, d)
        p = d.xpos[bid]*1000.0
        rx, rz = p[0]-AX, p[2]-AZ
        T.append(t); R.append(math.hypot(rx, rz))
        A.append(math.degrees(math.atan2(rz, rx)) % 360.0)
    return np.array(T), np.array(R), np.array(A)

# ---------------------------------------------------------------- figure
fig = plt.figure(figsize=(17.5, 15.5))
gs = fig.add_gridspec(2, 2, hspace=0.22, wspace=0.16)

# (a) section ------------------------------------------------------------
ax = fig.add_subplot(gs[0, 0])
th = np.linspace(A_EXIT, A_LIP, 200)
ax.plot([polar(R_IN, a)[0] for a in th], [polar(R_IN, a)[1] for a in th], color=GREEN, lw=2.6)
ax.plot([polar(R_IN+SHELL_WALL, a)[0] for a in th], [polar(R_IN+SHELL_WALL, a)[1] for a in th], color=GREEN, lw=1.2)
for a in (A_EXIT, A_LIP):
    p, q = polar(R_IN, a), polar(R_IN+SHELL_WALL, a)
    ax.plot([p[0], q[0]], [p[1], q[1]], color=GREEN, lw=1.2)
xs = np.array([TRAY_X0, TRAY_X1])
ax.fill_between(xs, tray_top_z(xs)-TRAY_T, tray_top_z(xs), color="#9ecbf0", alpha=0.6, zorder=1)
ax.plot(xs, tray_top_z(xs), color=GREEN, lw=2.4, zorder=2)
ax.plot(xs, tray_top_z(xs)-TRAY_T, color=GREEN, lw=1.2)
ax.plot([TRAY_X1+3, TRAY_X1+3], [tray_top_z(TRAY_X1+3)-6, tray_top_z(TRAY_X1+3)+40], color=GREEN, lw=1.6)
ax.add_patch(Circle((AX, AZ), HUB_R, color="#b9bec6", zorder=5))
for a in (330.0, 150.0):
    for (rc, hr, ht) in ((28.0, 18.0, 5.0), (52.0, 6.0, 15.0), (58.0, 2.0, 17.0)):
        cx = AX + rc*math.cos(math.radians(a)); cz = AZ + rc*math.sin(math.radians(a))
        ax.add_patch(Rectangle((cx-hr, cz-ht), 2*hr, 2*ht, angle=a, rotation_point="center",
                               color=ORANGE, ec="#a85a00", lw=0.7, zorder=6))
for name, (br, nip) in BALLS.items():
    col = RED if name == "NECTAR" else "#7b2fbe"
    n = (AX, AZ - (R_IN - br))
    ax.add_patch(Circle(n, br, fill=False, ec=col, lw=2.0, ls="--", zorder=8))
    ax.plot([n[0]], [n[1]], "+", color=col, ms=9, zorder=9)
    ax.annotate("%s D=%.0f 球心 r=%.1f" % (name, 2*br, R_IN-br), n,
                (( -150, 30) if name == "NECTAR" else (-150, 116)), color=col, fontsize=9,
                arrowprops=dict(arrowstyle="->", color=col, lw=1.1))
    e = (TRAY_X1 - br*math.sin(math.radians(TILT)), tray_top_z(TRAY_X1) + br*math.cos(math.radians(TILT)))
    ax.add_patch(Circle(e, br, fill=False, ec=col, lw=1.1, ls=":", alpha=0.8, zorder=7))
half = BALLS["NECTAR"][1]/2.0 + WHEEL_OD/2.0
for s in (1, -1):
    c = wheel_c(s, half)
    ax.add_patch(Circle(c, WHEEL_OD/2.0, fill=False, ec=GREY, lw=1.4, ls=(0, (5, 3)), zorder=4))
ax.annotate("飞轮夹口：唯一随球改变的一项\nNECTAR 82 mm / POLLEN 64 mm", xy=(-60, 265), fontsize=10,
            color=GREY, ha="center")
ax.annotate("托盘 5° 自流", (110, tray_top_z(110)), (150, tray_top_z(110)+42), color=GREEN,
            fontsize=10, arrowprops=dict(arrowstyle="->", color=GREEN, lw=1.1))
ax.annotate("外罩内弧 r=%.1f" % R_IN, polar(R_IN, 210), (-135, 155), color=GREEN, fontsize=10,
            arrowprops=dict(arrowstyle="->", color=GREEN, lw=1.1))
ax.annotate("入料口 275°", polar(R_IN, A_LIP), (135, 150), color=GREEN, fontsize=10,
            arrowprops=dict(arrowstyle="->", color=GREEN, lw=1.1))
ax.annotate("出口 142°", polar(R_IN, A_EXIT), (-130, 60), color=GREEN, fontsize=10,
            arrowprops=dict(arrowstyle="->", color=GREEN, lw=1.1))
ax.set_title("(a) 共用送球段剖面 XZ：同一外罩 / 托盘 / 拨杆，两种球各自的静止半径", fontsize=12)
ax.set_aspect("equal"); ax.set_xlim(-150, 215); ax.set_ylim(-45, 340); ax.grid(alpha=0.25)
ax.set_xlabel("X (mm)"); ax.set_ylabel("Z (mm)")

# (b) blade layout -------------------------------------------------------
ax = fig.add_subplot(gs[0, 1])
ax.add_patch(Wedge((AX, AZ), R_IN, A_EXIT, A_LIP, width=SHELL_WALL, facecolor="#cfe8d4", ec=GREEN))
for a in (A_LIP, A_EXIT):
    ax.plot(*zip(polar(0, a), polar(R_IN+40, a)), color=GREEN, lw=1.0, ls=":")
ax.add_patch(Wedge((AX, AZ), R_IN, A_LIP, 360+A_EXIT, width=70, facecolor="#ffe9e9", ec=RED, alpha=0.6))
pass
ax.text(-168, 205, "进料走廊 275° → 142°（逆时针 137°）", fontsize=10, color=RED, va="top")
for name, ph, col in (("CAD 三叶 18/138/258", (18.0, 138.0, 258.0), RED),
                      ("建议 两叶 330/150", (330.0, 150.0), GREEN)):
    for k, a in enumerate(ph):
        c = polar(52, a)
        ax.add_patch(Rectangle((c[0]-6, c[1]-30), 12, 60, angle=a, rotation_point="center",
                               facecolor="none", ec=col, lw=1.8, ls="-" if k else (0, (4, 2))))
        ax.plot(*zip(polar(0, a), polar(46, a)), color=col, lw=3.0, alpha=0.55)
for name, (br, _) in BALLS.items():
    col = RED if name == "NECTAR" else "#7b2fbe"
    n = (AX, AZ - (R_IN - br))
    ha = math.degrees(math.asin(min(1.0, br/(R_IN-br))))
    ax.add_patch(Wedge(n, br, 180-ha, 180+ha, facecolor=col, alpha=0.13))
    e = (TRAY_X1 - br*math.sin(math.radians(TILT)), tray_top_z(TRAY_X1) + br*math.cos(math.radians(TILT)))
    ax.add_patch(Wedge(e, br, 180-ha, 180+ha, facecolor=col, alpha=0.08))
ax.text(-168, -68, "实线=CAD 现有三叶（258° 叶落在入料口前缘\n→ 大球被推回托盘，NECTAR 卡死 80%）\n虚线=建议两叶（入料口完全净空，两球均通过）",
        fontsize=10, color="#333333")
ax.add_patch(Circle((AX, AZ), HUB_R, color="#b9bec6"))
ax.arrow(AX, AZ, 60*math.cos(math.radians(-115)), 60*math.sin(math.radians(-115)),
         head_width=7, color="#444444", length_includes_head=True)
ax.text(AX+22, AZ-84, "扫掠 248°", fontsize=10)
ax.set_title("(b) 俯视（面向 +Y）：叶片布置 vs 入料走廊", fontsize=12)
ax.set_aspect("equal"); ax.set_xlim(-172, 195); ax.set_ylim(-100, 275); ax.grid(alpha=0.25)
ax.set_xlabel("X (mm)"); ax.set_ylabel("Z (mm)")

# (c) traces -------------------------------------------------------------
ax = fig.add_subplot(gs[1, 0])
print("running NECTAR trace ...", flush=True)
tN, rN, aN = run_trace(BALLS["NECTAR"][0], 0.130, BALLS["NECTAR"][1], xc=108.0)
print("running POLLEN trace ...", flush=True)
tP, rP, aP = run_trace(BALLS["POLLEN"][0], 0.060, BALLS["POLLEN"][1], xc=117.0)
mN = rN < 200.0; mP = rP < 200.0
tN, rN, aN = tN[mN], rN[mN], aN[mN]
tP, rP, aP = tP[mP], rP[mP], aP[mP]
ax.plot(tN, rN, color=RED, lw=2.0, label="NECTAR D91.9  r(t)")
ax.plot(tP, rP, color="#7b2fbe", lw=2.0, label="POLLEN D71.1  r(t)")
ax.axhline(R_IN-BALLS["NECTAR"][0], color=RED, ls=":", lw=1.0)
ax.axhline(R_IN-BALLS["POLLEN"][0], color="#7b2fbe", ls=":", lw=1.0)
ax.text(0.12, R_IN-BALLS["NECTAR"][0]+2.0, "NECTAR 球窝 r=62.0", color=RED, fontsize=9)
ax.text(0.12, R_IN-BALLS["POLLEN"][0]+2.0, "POLLEN 球窝 r=72.4", color="#7b2fbe", fontsize=9)
ax.axvline(1.8, color="#888888", ls="--", lw=1.0)
ax.text(1.86, 90, "1.8 s 起拨杆扫掠 248°", fontsize=9, color="#555555")
for _tt, _cc in ((2.80, RED), (2.40, "#7b2fbe")):
    ax.axvline(_tt, color=_cc, ls="-.", lw=1.0, alpha=0.75)
ax.text(0.12, 116, "球离开飞轮夹口（发射）：NECTAR t=2.80 s, 4.63 m/s, 49.8° / POLLEN t=2.40 s, 5.93 m/s, 49.9°", fontsize=9, color="#555555")
ax.set_xlabel("t (s)"); ax.set_ylabel("球心到拨杆轴距离 r (mm)")
ax.set_ylim(56, 120)
ax.set_title("(c) 两球共用一套机构的球心半径历程（自流进料 → 球窝 → 扫掠 → 飞轮发射）", fontsize=12)
ax.grid(alpha=0.25); ax.legend(fontsize=10)
ax2 = ax.twinx()
ax2.plot(tN, aN, color="#d95f02", lw=1.0, alpha=0.65, ls="--")
ax2.plot(tP, aP, color="#1b9e77", lw=1.0, alpha=0.65, ls="--")
ax2.set_ylabel("方位角 (°，虚线)", color="#555555"); ax2.set_ylim(120, 380)

# (d) robustness grid ----------------------------------------------------
ax = fig.add_subplot(gs[1, 1])
rows = json.loads(Path("simulation/mujoco/out/_r29_grid.json").read_text(encoding="utf-8"))
homes = ["330_150", "10_190"]
sws = [180.0, 200.0, 248.0]
xcs = [98.0, 108.0, 118.0, 128.0]
holds = [1.2, 1.8]
cells = []
for hi, h in enumerate(homes):
    for si, s in enumerate(sws):
        for xi, x in enumerate(xcs):
            for oi, o in enumerate(holds):
                hit = [r for r in rows if r["home"] == h and r["sweep"] == s
                       and r["xc"] == x and r["hold"] == o]
                if not hit: continue
                r = hit[0]
                ok = r["nectar"][0] and r["pollen"][0]
                one = r["nectar"][0] or r["pollen"][0]
                y = 0
                ax.add_patch(Rectangle((xi*2+oi + si*9 + hi*28, 0), 1.7, 1.0,
                                       color=("#2e8b3d" if ok else ("#f0c419" if one else "#d62728"))))
                ax.text(xi*2+oi + si*9 + hi*28 + 0.85, 0.5,
                        "%s" % ("双球OK" if ok else ("单球" if one else "失败")),
                        ha="center", va="center", fontsize=6.2, rotation=90,
                        color="white" if ok else "#333333")
for si, s in enumerate(sws):
    for hi, h in enumerate(homes):
        ax.text(hi*28 + si*9 + 4.5, 1.08, "%s / %.0f°" % (h.replace("_", "/"), s),
                ha="center", fontsize=9)
        ax.text(hi*28 + si*9 + 4.5, -0.12, "入料 x=98,108,118,128 × t=1.2/1.8 s",
                ha="center", fontsize=6.5, color="#555555")
ax.set_xlim(-1, 74); ax.set_ylim(-0.35, 1.35); ax.axis("off")
ax.set_title("(d) 鲁棒性网格：同一拨杆，两种球同时通过（绿=双球通过）", fontsize=12)
ax.add_patch(Rectangle((0, 0), 0, 0, color="#2e8b3d"))
ax.text(0, 0.72, "绿=两种球都通过   黄=只有一种通过   红=都不过", transform=ax.transAxes, fontsize=9)

fig.suptitle("T06 共用送球段（NECTAR D91.95 / POLLEN D71.12）：只有飞轮夹口随球改变，外罩·托盘·拨杆完全共用",
             fontsize=14, y=0.995)
out = "cad/output/_t06_shared_feeder_zh.png"
fig.savefig(out, dpi=118, bbox_inches="tight")
print("saved", out, flush=True)




