"""Interim result figure for the T06/POLLEN motion simulation."""
from __future__ import annotations
import json, math, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['Microsoft YaHei','SimHei','DejaVu Sans']
plt.rcParams['axes.unicode_minus']=False
import pollen_launcher_sim as P

NIP = P.SHOOTER_ORIGIN
T52 = P.T52


def draw_frame(ax):
    for name, panel, cls in P.static_geoms():
        pieces = P.clip_drum(panel) if name.startswith(("guide_floor", "guide_roof")) else [panel]
        col = {"guide": "#2f8fd4", "finger": "#9b59b6"}[cls]
        for center, size, rot in pieces:
            a = math.radians(rot)
            hx, hz = size[0] / 2, size[2] / 2
            pts = [(-hx, -hz), (hx, -hz), (hx, hz), (-hx, hz), (-hx, -hz)]
            ax.plot([center[0] + u * math.cos(a) + v * math.sin(a) for u, v in pts],
                    [center[2] - u * math.sin(a) + v * math.cos(a) for u, v in pts],
                    "-", color=col, lw=0.7 if size[1] > 6 else 0.5,
                    alpha=1.0 if size[1] > 6 else 0.4)
    ax.add_patch(plt.Circle((P.PADDLE_CENTER[0], P.PADDLE_CENTER[2]),
                            P.PADDLE_SWEEP_R + 3, fill=False, color="0.4", ls="--", lw=0.8))
    for name, center, half, ang, kind in P.paddle_parts():
        if kind != "box":
            continue
        a = math.radians(ang)
        c = P.rot_local(center, ang)
        hx, hz = half[0], half[2]
        pts = [(-hx, -hz), (hx, -hz), (hx, hz), (-hx, hz), (-hx, -hz)]
        ax.plot([P.PADDLE_CENTER[0] + c[0] + u * math.cos(a) + v * math.sin(a) for u, v in pts],
                [P.PADDLE_CENTER[2] + c[2] - u * math.sin(a) + v * math.cos(a) for u, v in pts],
                "-", color="orange", lw=1.0)
    for sign in (1, -1):
        cx, _, cz = P.flywheel_axle_center(sign)
        ax.add_patch(plt.Circle((cx, cz), P.WHEEL_R, fill=False, color="k", lw=1.4))
        ax.plot([cx], [cz], "k+", ms=8)
        ax.plot([cx - P.WHEEL_R, cx + P.WHEEL_R], [cz, cz], "k:", lw=0.6)
        ax.plot([NIP[0] + s * T52[0] for s in (-100, 120)],
                [NIP[2] + s * T52[1] for s in (-100, 120)], "r--", lw=0.8)
    ax.set_aspect("equal")
    ax.grid(alpha=0.25)
    ax.set_xlabel("X [mm]")
    ax.set_ylabel("Z [mm]")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    out = HERE / "out"
    tr_ok = json.loads((out / "trace_launch_rpm1620_v2.5.json").read_text())
    tr_bad = json.loads((out / "trace_paddlem_spinm.json").read_text())

    fig, axes = plt.subplots(1, 3, figsize=(19, 7))
    ax = axes[0]
    draw_frame(ax)
    ax.plot([t[1] for t in tr_ok], [t[2] for t in tr_ok], "-", color="crimson", lw=2.0)
    ax.plot([tr_ok[0][1]], [tr_ok[0][2]], "o", color="crimson", ms=6)
    ax.set_title("A. 发射段成功注入（跳过拨杆）\n"
                 "1620 rpm, 注入 2.5 m/s -> 出射约 6.5 m/s @ 51°")
    ax.set_xlim(-180, 400)
    ax.set_ylim(-40, 800)

    ax = axes[1]
    draw_frame(ax)
    ax.plot([t[1] for t in tr_bad], [t[3] for t in tr_bad], "-", color="darkred", lw=2.0)
    ax.plot([tr_bad[0][1]], [tr_bad[0][3]], "o", color="darkred", ms=6)
    ax.annotate("球被推向左下\n挤出导槽", xy=(tr_bad[-1][1], tr_bad[-1][3]),
                xytext=(tr_bad[-1][1] + 20, tr_bad[-1][3] + 60), fontsize=10,
                arrowprops=dict(arrowstyle="->", color="darkred"))
    ax.set_title("B. 全流程失败：球放在托板 x=-128\n拨杆 30 rpm 把球推离导轨后掉落")
    ax.set_xlim(-260, 160)
    ax.set_ylim(-250, 160)

    ax = axes[2]
    for tag, lbl, col in (("launch_rpm1620_v2.5", "注入 2.5 m/s（发射段）", "crimson"),
                          ("paddlem_spinm", "拨杆送球 30 rpm", "darkred")):
        t = json.loads((out / f"trace_{tag}.json").read_text())
        s = [((r[1] - NIP[0]) * T52[0] + (r[2] - NIP[2]) * T52[1]) for r in t]
        v = [r[5] if len(r) > 6 else r[4] for r in t]
        ax.plot([r[0] for r in t], s, label=lbl, color=col)
    ax.axhline(0, color="k", lw=1.2)
    ax.text(0.02, 4, "飞轮夹口 (s=0)", fontsize=9)
    ax.set_xlabel("t [s]")
    ax.set_ylabel("沿发射轴位移 s [mm]")
    ax.set_title("C. 沿 52° 发射轴的位置\ns=0 为飞轮夹口，负值表示尚未到达")
    ax.legend(fontsize=9)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(out / "interim_result.png", dpi=130)
    print("saved", out / "interim_result.png")


if __name__ == "__main__":
    main()
