import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
from matplotlib.patches import Rectangle
from pathlib import Path

OUT = Path(r"C:\FTC design\FTC 2026 biobuzz\deliverables\R69_print_package\previews\bambu_fix_dimensions.png")
BED = (315.0, 310.0)

panels = [
    ("shroud_tray_mid  (外罩-托板)", (232.84, 248.43), 136.0,
     (403.69, 232.84), "旧中间件 _r69_split/mid.step"),
    ("side_plate_right  (右侧板)", (262.22, 284.00), 31.0,
     (361.06, 385.02), "旧中间件 _r69_split/plate_R.step"),
]

fig, axes = plt.subplots(1, 2, figsize=(13.2, 6.4), dpi=150)
for ax, (name, good, h, old, oldname) in zip(axes, panels):
    ax.add_patch(Rectangle((0, 0), BED[0], BED[1], fill=False, ec="#444", lw=1.4, ls="-"))
    ax.add_patch(Rectangle((0, 0), BED[0], BED[1], fill=True, fc="#f4f6f8", ec="none", zorder=-2))
    ax.add_patch(Rectangle((0, 0), good[0], good[1], fill=True, fc="#8fd18a", ec="#1f7a2e", lw=2.0, alpha=0.85))
    ax.add_patch(Rectangle((0, 0), old[0], old[1], fill=False, ec="#d33", lw=1.8, ls="--"))
    ax.text(good[0]/2, good[1]/2, "%.1f × %.1f\nh = %.1f mm\nOK 在盘内" % (good[0], good[1], h),
            ha="center", va="center", fontsize=11, fontweight="bold")
    ax.annotate("%.1f × %.1f  (超界/超高)" % old, xy=(min(old[0], BED[0]), min(old[1], BED[1])),
                xytext=(8, BED[1]+14), fontsize=10, color="#d33",
                arrowprops=dict(arrowstyle="-", color="#d33", lw=1.0))
    ax.set_xlim(-10, max(BED[0], old[0]) + 30)
    ax.set_ylim(-10, max(BED[1], old[1]) + 40)
    ax.set_aspect("equal")
    ax.set_title("%s\n正确件：parts_flat/%s.step" % (name, "shroud_tray_mid" if "shroud" in name else "side_plate_right"), fontsize=11)
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.grid(alpha=0.25, lw=0.5)

fig.suptitle("R69 打印件：正确件（绿，实线）vs 你导入的旧中间件（红，虚线）  |  灰框 = H2D 可用区 315 × 310 mm", fontsize=12)
fig.tight_layout()
fig.savefig(OUT)
print(OUT)


