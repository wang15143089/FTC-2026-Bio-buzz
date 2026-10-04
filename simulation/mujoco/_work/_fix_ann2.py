# -*- coding: utf-8 -*-
import pathlib
p = pathlib.Path("simulation/mujoco/_work/r6_fig_zh.py")
s = p.read_text(encoding="utf-8")
def rep(old, new):
    global s
    assert old in s, "NOT FOUND:\n" + old
    s = s.replace(old, new, 1)

rep('xy=fp(R6_A1, R_IN), xytext=(26, -8), fontsize=9.2, color=C_ARC_E,',
    'xy=fp(R6_A1, R_IN), xytext=(-124, -6), fontsize=9.2, color=C_ARC_E,')

rep('''            xytext=(48, -2), fontsize=9.0, color="#7a5c10",
            bbox=dict(fc="white", ec="#7a5c10", lw=0.7, alpha=0.93),''',
    '''            xytext=(4, 20), fontsize=9.0, color="#7a5c10",
            bbox=dict(fc="white", ec="#7a5c10", lw=0.7, alpha=0.93),''')

rep('''        transform=ax.transAxes, va="bottom", fontsize=9.2, color="#333",
        bbox=dict(fc="white", ec="#ccc", lw=0.8, alpha=0.95))''',
    '''        transform=ax.transAxes, va="bottom", fontsize=9.2, color="#333", zorder=16,
        bbox=dict(fc="white", ec="#ccc", lw=0.8, alpha=0.95))''')

p.write_text(s, encoding="utf-8")
print("ok")
