# -*- coding: utf-8 -*-
import pathlib
p = pathlib.Path("simulation/mujoco/_work/r6_fig_zh.py")
s = p.read_text(encoding="utf-8")
def rep(old, new):
    global s
    assert old in s, "NOT FOUND:\n" + old
    s = s.replace(old, new, 1)

rep('"结论 2（回答本次问题）：把外罩与球窝垫连成平滑弧面**不能**消除「蠕动」，\\n"',
    '"结论 2（回答本次问题）：把外罩与球窝垫连成平滑弧面不能消除「蠕动」，\\n"')
rep('"结论 3（根因，实测）：蠕动出在球停稳后的**停位球窝**——球停在 r≈83–95 mm、被指片\\n"',
    '"结论 3（根因，实测）：蠕动出在球停稳后的 停位球窝——球停在 r≈83–95 mm、被指片\\n"')
rep('"说明这是**卡滞**而不是单纯扭矩不够。\\n"', '"说明这是卡滞而不是单纯扭矩不够。\\n"')
rep('"结论 4（建议）：治本要改**停位球窝几何**（让球停在指片扫掠范围之外），或提高伺服\\n"',
    '"结论 4（建议）：治本要改 停位球窝几何（让球停在指片扫掠范围之外），或提高伺服\\n"')
rep('''        "R5/R6/R6c 均一次通过（launched=True），出口球速 6.67 m/s，飞轮 1620 rpm。"
        "抓球前蠕动 = 球停稳 → 拨杆把球推出停位的时间。"
        "「运载段舵机」列由 25-4 线性扭矩—转速模型驱动拨杆时实测。",
        fontsize=8.6, color="#777", va="top")''',
    '''        "R5/R6/R6c 均一次通过（launched=True），出口球速 6.67 m/s，飞轮 1620 rpm。\\n"
        "抓球前蠕动 = 球停稳 → 拨杆把球推出停位的时间；「运载段舵机」列为 25-4 线性扭矩—转速模型实测。",
        fontsize=8.2, color="#777", va="top")''')
p.write_text(s, encoding="utf-8")
print("ok")
