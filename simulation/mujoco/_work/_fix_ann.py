# -*- coding: utf-8 -*-
import pathlib
p = pathlib.Path("simulation/mujoco/_work/r6_fig_zh.py")
s = p.read_text(encoding="utf-8")

def rep(old, new):
    global s
    assert old in s, "NOT FOUND:\n" + old
    s = s.replace(old, new, 1)

# --- panel (b): move + white bbox ---
rep('''ax.annotate("R6 新增：外罩内弧 R93.96\\n从 225° 平滑延伸 35.2°",
            xy=fp(243.0, 97.5), xytext=(20, 62), fontsize=9.4, color=C_ARC_E,
            arrowprops=dict(arrowstyle="->", color=C_ARC_E, lw=1.2), zorder=11)''',
    '''ax.annotate("R6 新增：外罩内弧 R93.96\\n从 225° 平滑延伸 35.2°",
            xy=fp(243.0, 97.5), xytext=(-124, 160), fontsize=9.4, color=C_ARC_E,
            bbox=dict(fc="white", ec=C_ARC_E, lw=0.7, alpha=0.93),
            arrowprops=dict(arrowstyle="->", color=C_ARC_E, lw=1.2), zorder=11)''')

rep('''ax.annotate("终点落在托板顶面 x=13.5\\n（该处抬升 0.0 mm，与 225° 处相切连续）",
            xy=fp(R6_A1, R_IN), xytext=(-8, 30), fontsize=9.2, color=C_ARC_E,
            arrowprops=dict(arrowstyle="->", color=C_ARC_E, lw=1.1), zorder=11)''',
    '''ax.annotate("终点落在托板顶面 x=13.5\\n（该处抬升 0.0 mm，相切连续）",
            xy=fp(R6_A1, R_IN), xytext=(26, -8), fontsize=9.2, color=C_ARC_E,
            bbox=dict(fc="white", ec=C_ARC_E, lw=0.7, alpha=0.93),
            arrowprops=dict(arrowstyle="->", color=C_ARC_E, lw=1.1), zorder=11)''')

rep('''            xytext=(6, 20), fontsize=9.0, color="#7a5c10",
            arrowprops=dict(arrowstyle="->", color="#7a5c10", lw=1.0), zorder=11)
ax.plot([], [], color=C_TRACK, lw=2.2, label="球心轨迹（实测）")
ax.legend(loc="upper right", fontsize=8.6, frameon=False)
setup(ax, (-128, 178), (-12, 205), "(b) R6：外罩内弧直接延伸到托板，取消平垫块")''',
    '''            xytext=(48, -2), fontsize=9.0, color="#7a5c10",
            bbox=dict(fc="white", ec="#7a5c10", lw=0.7, alpha=0.93),
            arrowprops=dict(arrowstyle="->", color="#7a5c10", lw=1.0), zorder=11)
ax.plot([], [], color=C_TRACK, lw=2.2, label="球心轨迹（实测）")
ax.legend(loc="upper right", fontsize=8.6, frameon=False)
setup(ax, (-128, 178), (-12, 205), "(b) R6：外罩内弧直接延伸到托板，取消平垫块")''')

# --- panel (a): white bbox on the pad callout ---
rep('''ax.annotate("D 平垫块 顶面 z=24.33\\n与托板之间有 6.8 mm 台阶",
            xy=(PAD_X1, PAD_TOP), xytext=(6, 62), fontsize=9.4, color=C_PAD_E,''',
    '''ax.annotate("D 平垫块 顶面 z=24.33\\n与托板之间有 6.8 mm 台阶",
            xy=(PAD_X1, PAD_TOP), xytext=(-124, 160), fontsize=9.4, color=C_PAD_E,
            bbox=dict(fc="white", ec=C_PAD_E, lw=0.7, alpha=0.93),''')

# --- panel (c): short labels + corner legend ---
rep('''ax.annotate("R5：球在 x=13 撞上 6.8 mm 立沿，\\n被指片沿硬台阶向上刮", xy=(13.0, PAD_TOP), xytext=(-46, 66),
            fontsize=9.2, color=C_PAD_E, arrowprops=dict(arrowstyle="->", color=C_PAD_E, lw=1.1), zorder=12)
ax.annotate("R6：弧面与托板在此相切落地，\\n球是「滚」上去的而不是「刮」上去的",
            xy=(fp(R6_A1, R_IN)[0], fp(R6_A1, R_IN)[1]), xytext=(18, 40), fontsize=9.2, color=C_ARC_E,
            arrowprops=dict(arrowstyle="->", color=C_ARC_E, lw=1.1), zorder=12)''',
    '''ax.annotate("R5 硬台阶", xy=(13.0, PAD_TOP), xytext=(-54, 118),
            fontsize=9.4, color=C_PAD_E, ha="center",
            bbox=dict(fc="white", ec=C_PAD_E, lw=0.8, alpha=0.94),
            arrowprops=dict(arrowstyle="->", color=C_PAD_E, lw=1.2), zorder=12)
ax.annotate("R6 相切弧面", xy=(fp(R6_A1, R_IN)[0], fp(R6_A1, R_IN)[1]), xytext=(24, 132),
            fontsize=9.4, color=C_ARC_E, ha="center",
            bbox=dict(fc="white", ec=C_ARC_E, lw=0.8, alpha=0.94),
            arrowprops=dict(arrowstyle="->", color=C_ARC_E, lw=1.2), zorder=12)
ax.text(0.02, 0.045, "R5：球撞上 6.8 mm 立沿，被指片沿硬台阶「刮」上去\\nR6：弧面与托板相切落地，球是「滚」上去的",
        transform=ax.transAxes, va="bottom", fontsize=9.2, color="#333",
        bbox=dict(fc="white", ec="#ccc", lw=0.8, alpha=0.95))''')

p.write_text(s, encoding="utf-8")
print("patched annotations")
