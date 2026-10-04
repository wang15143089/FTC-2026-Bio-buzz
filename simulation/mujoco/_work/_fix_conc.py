# -*- coding: utf-8 -*-
import pathlib
p = pathlib.Path("simulation/mujoco/_work/r6_fig_zh.py")
s = p.read_text(encoding="utf-8")

old = '''ax.text(0.02, 0.425,
        "结论 1：R5 与 R6 的运载段负载扭矩几乎相同（0.523 N·m），R6 只让球更早被抓到、\\n"
        "运载略快，全程缩短约 0.11 s（1.5%）；R6c 再快一点（0.26 s，3.5%）。\\n"
        "结论 2（更重要）：运载段舵机全程堵转在 ~4 rpm、输出 0.523 N·m——已经贴着 25-4\\n"
        "Super Speed 的堵转扭矩 0.530 N·m，几乎没有余量；负载再大 2% 就会彻底堵死。\\n"
        "结论 3：把外罩与球窝垫连成平滑曲面不能解决「蠕动」，因为蠕动来自舵机接近堵转，\\n"
        "不来自接合处的台阶；要缩短运载时间必须降低爬壁负载（指片前端形状/摩擦）或换更大扭矩舵机。",
        fontsize=9.4, color="#333", va="top", linespacing=1.5)'''

new = '''ax.text(0.02, 0.44,
        "结论 1：R5 与 R6 全程相差很小——R6 快约 0.11 s（1.5%），R6c 快约 0.26 s（3.5%）。\\n"
        "结论 2（回答本次问题）：把外罩与球窝垫连成平滑弧面**不能**消除「蠕动」，\\n"
        "抓球前等待 2.98 s → 2.93 s，几乎没变；台阶不是蠕动的成因。\\n"
        "结论 3（根因，实测）：蠕动出在球停稳后的**停位球窝**——球停在 r≈83–95 mm、被指片\\n"
        "楔住，把拨杆拖到 ~4 rpm；此时 25-4 输出 0.523 N·m，已贴近 0.530 N·m 堵转。\\n"
        "改用 ±5 N·m 刚性速度源复测，该段拨杆仍只有 ~6.8 rpm、出力 ~1.16 N·m，\\n"
        "说明这是**卡滞**而不是单纯扭矩不够。\\n"
        "结论 4（建议）：治本要改**停位球窝几何**（让球停在指片扫掠范围之外），或提高伺服\\n"
        "扭矩；只优化外罩—球窝接合处的形状无效。",
        fontsize=9.0, color="#333", va="top", linespacing=1.55)'''

assert old in s, "conclusion block not found"
s = s.replace(old, new, 1)

old2 = '''        "R5/R6 均一次通过（launched=True），出口球速 6.67 m/s，飞轮 1620 rpm。"
        "抓球前蠕动 = 球停稳 → 拨杆把球推出停位的时间。",'''
new2 = '''        "R5/R6/R6c 均一次通过（launched=True），出口球速 6.67 m/s，飞轮 1620 rpm。"
        "抓球前蠕动 = 球停稳 → 拨杆把球推出停位的时间。"
        "「运载段舵机」列由 25-4 线性扭矩—转速模型驱动拨杆时实测。",'''
assert old2 in s, "note block not found"
s = s.replace(old2, new2, 1)

p.write_text(s, encoding="utf-8")
print("ok")
