# -*- coding: utf-8 -*-
import pathlib
p = pathlib.Path("simulation/mujoco/_work/r6_fig_zh.py")
s = p.read_text(encoding="utf-8")
def rep(old, new):
    global s
    assert old in s, "NOT FOUND:\n" + old
    s = s.replace(old, new, 1)

rep('y0, dy = 0.80, 0.085', 'y0, dy = 0.865, 0.083')
rep('ax.text(0.02, 0.44,', 'ax.text(0.02, 0.505,')
rep('fontsize=9.0, color="#333", va="top", linespacing=1.55)',
    'fontsize=8.4, color="#333", va="top", linespacing=1.5)')
p.write_text(s, encoding="utf-8")
print("ok")
