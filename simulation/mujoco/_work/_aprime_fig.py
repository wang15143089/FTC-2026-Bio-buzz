# -*- coding: utf-8 -*-
"""a' cradle cross sections (XZ) for POLLEN and the NECTAR variant."""
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

AX, AZ = 29.49, 111.46
PIVOT_X, PIVOT_Z, TILT = -2.30, 17.50, 5.0
TRAY_T, SHELL_WALL, FEEDER_W = 6.0, 7.0, 108.0
A_EXIT = 142.0
HUB_R = 18.0
FINGERS = (18.0, 138.0, 258.0)
ARM = (30.0, 16.0, 5.0)      # r, radial half, tangential half
BLADE = (52.0, 6.0, 15.0)
FLEX = (58.0, 2.0, 17.0)


def tray_top_z(x):
    return PIVOT_Z + (x - PIVOT_X) * math.tan(math.radians(TILT))


def polar(r, a):
    return (AX + r * math.cos(math.radians(a)), AZ + r * math.sin(math.radians(a)))


def draw(ax, title, ball_r, r_carry, a_lip, tray_x0):
    r_in = r_carry + ball_r
    r_out = r_in + SHELL_WALL
    th = [a for a in range(int(A_EXIT), int(a_lip) + 1, 2)]
    ax.plot([polar(r_in, a)[0] for a in th], [polar(r_in, a)[1] for a in th],
            color="#1f7a3d", lw=2.2)
    ax.plot([polar(r_out, a)[0] for a in th], [polar(r_out, a)[1] for a in th],
            color="#1f7a3d", lw=1.2)
    for a in (A_EXIT, a_lip):
        p, q = polar(r_in, a), polar(r_out, a)
        ax.plot([p[0], q[0]], [p[1], q[1]], color="#1f7a3d", lw=1.2)
    xs = [tray_x0, 150.0]
    ax.plot(xs, [tray_top_z(x) for x in xs], color="#1f7a3d", lw=2.0)
    ax.plot(xs, [tray_top_z(x) - TRAY_T for x in xs], color="#1f7a3d", lw=1.2)
    ax.fill_between(xs, [tray_top_z(x) - TRAY_T for x in xs],
                    [tray_top_z(x) for x in xs], color="#9ecbf0", alpha=0.55)

    ax.add_patch(plt.Circle((AX, AZ), HUB_R, color="#b9bec6", zorder=4))
    for a in FINGERS:
        for (rc, hr, ht) in (ARM, BLADE, FLEX):
            cx = AX + rc * math.cos(math.radians(a))
            cz = AZ + rc * math.sin(math.radians(a))
            ax.add_patch(plt.Rectangle((cx - hr, cz - ht), 2 * hr, 2 * ht,
                                       angle=a, rotation_point="center",
                                       color="#eb8a1e", ec="#a85a00", lw=0.6, zorder=5))
    bx, bz = AX, AZ - r_carry
    ax.add_patch(plt.Circle((bx, bz), ball_r, fill=False, ec="#d62728", lw=1.8, zorder=8))
    ax.plot([bx], [bz], "+", color="#d62728", ms=8, zorder=8)
    ax.annotate("球心 r=%.1f" % r_carry, (bx, bz), (bx - 95, bz - 42), color="#d62728",
                fontsize=9, arrowprops=dict(arrowstyle="->", color="#d62728", lw=1))
    ax.annotate("外罩内弧 r=%.2f" % r_in, (polar(r_in, 200)), (polar(r_in, 200)[0] - 70,
                polar(r_in, 200)[1] + 18), color="#1f7a3d", fontsize=9,
                arrowprops=dict(arrowstyle="->", color="#1f7a3d", lw=1))
    ax.annotate("托盘 x=%.0f..150" % tray_x0, (tray_x0, tray_top_z(tray_x0)),
                (tray_x0 + 6, tray_top_z(tray_x0) - 40), color="#1f7a3d", fontsize=9,
                arrowprops=dict(arrowstyle="->", color="#1f7a3d", lw=1))
    ax.set_title(title, fontsize=11)
    ax.set_aspect("equal")
    ax.set_xlim(-90, 200)
    ax.set_ylim(-30, 210)
    ax.grid(alpha=0.25)
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Z (mm)")


fig, axes = plt.subplots(1, 2, figsize=(15.5, 7.4))
draw(axes[0], "a' POLLEN  D=71.12  R_CARRY=58.4  lip=292deg  tray 56..150",
     35.56, 58.4, 292.0, 56.0)
draw(axes[1], "a' NECTAR  D=91.95  R_CARRY=64.0 (hub limit 63.97)  lip=300deg  tray 84..150",
     45.974, 64.0, 300.0, 84.0)
fig.tight_layout()
out = "cad/output/_aprime_cradle_sections_zh.png"
fig.savefig(out, dpi=135)
print("saved", out)
