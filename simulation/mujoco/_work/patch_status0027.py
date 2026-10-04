# -*- coding: utf-8 -*-
import pathlib

p = pathlib.Path("PROJECT_STATUS.md")
s = p.read_text(encoding="utf-8")

SEC = u"""
## T06 POLLEN V2 送球段「平滑曲面」优化与蠕动根因（2026-10-03，DEC-0027）

- 用户指令：采用 goBILDA **25-4 Super Speed（0.530 N·m / 290 rpm）** 作送球舵机，尝试把**外罩与球窝垫用平滑曲面连接**，看能否减少球的「蠕动」。
- 新增候选 **R6**（SIMULATED）：取消 R5 的 30×108×12.8 平垫块，外罩内弧（r = 93.96 mm）从 225° 沿同一半径平滑延伸到 **260.2°**，终点与托板顶面在 x = 13.5 mm 处相切（抬升 0.0 mm）。**R5 保留**，两者并列；R6 标为**候选待接受**。两者都仅在 MuJoCo 中，**均尚未进入 CAD**。
- **直接回答：平滑曲面不能消除蠕动。** 抓球前等待 2.98 s → 2.93 s（−1.7%，噪声量级）；全程 7.49 s → 7.38 s（−1.5%）；R6c（弧面止于 256°、半径收窄 2 mm）→ 7.23 s（−3.5%）。三者均**一次通过**全流程，出口球速 6.67 m/s、飞轮 1620 rpm，没有失败工况可区分优劣。
- 判定口径（KNOWN/SIMULATED）：拨杆改用 25-4 的真实线性扭矩—转速模型驱动（kv = 0.017452、限幅 ±0.530、ctrl = 空载 290 rpm），球从托板 x = 145 mm 滚入，12 s 预算。运载段实测：R5 3.95 rpm / 0.523 N·m，R6 4.05 rpm / 0.523 N·m，R6c 4.36 rpm / 0.522 N·m。
- **根因（SIMULATED，独立复测）**：蠕动发生在球停稳后的**停位球窝**——球停在 r ≈ 83–95 mm、角 ≈ 322–329°，被指片楔住，把拨杆拖到几 rpm，约 2.3 s 后楔口松脱才被带入运载轨道。用刚性速度源（±5 N·m 不限幅）复测同一 R5 几何，该段拨杆仍只有约 **6.8 rpm、出力约 1.16 N·m**（球心 r 实测 59.4 mm），说明是**卡滞**而不是「扭矩差一点」。接合处的台阶在该时段根本不参与接触，因此**改接合处形状无效**。
- 产物的图：`simulation/mujoco/out/r5_vs_r6_smooth_zh.png`（4 面板：R5 剖面 / R6 剖面 / 接合处放大 / 结果表与结论）；脚本 `_work/r6_fig_zh.py`、`_work/r6_motor.py`、`_work/r6_summary.py`、`_work/r7_loadprobe2.py`；数据 `out/_r6_summary.json`、`out/_r6_fig_data.json`。
- **重新打开的开放项（TBD）**：DEC-0026 的 `paddle_torque_threshold_12s_by_rpm`（90/105 rpm ≤ 0.24 N·m）由 kv = 0.08 的假执行器取得，其中「通过」只表示在限幅内 12 s 跑完，**不等于**真实电机有相应扭矩余量；25-4 全油门模型下运载段出力 0.523 N·m 已贴 0.530 N·m 堵转，**余量很薄**。两种口径不可直接相除比较，但都指向「运载段余量薄」→ 舵机余量复核重开。卡滞力矩对接触正则化与到达相位敏感（同一几何 0.52 与 1.16 N·m 两个读数），绝对值只能当量级参考。

## NEXT ACTION
"""

old_next = "## NEXT ACTION\n"
assert old_next in s
s = s.replace(old_next, SEC.lstrip("\n"), 1)

# rewrite the first NEXT ACTION item (formerly "confirm R5 -> CAD V3") to reflect R6 + the pocket fix
old_item = s[s.index("1. （立即）向用户确认是否锁定 **R5**"):]
end = old_item.index("\n\n2. （并行阻塞项）")
new_item = (u"1. （立即，等用户决策）向用户报告 DEC-0027 结论并请其在两条路线中选一条：\n"
            u"   (a) 接受 **R6** 作为送球段几何（少一个平垫块、无台阶、全程快 1.5%），据此改 `cad/paddle_launcher_feeder_redesign.py` 出候选 STEP（**不得改** `cad/paddle_launcher_constrained.py`、不得覆盖原 STEP）；\n"
            u"   (b) 先不动几何，改做**停位球窝**改型（让球停在指片扫掠范围之外，例如加深/缩进球窝或调整停位半径），这是唯一被证明能缩短蠕动时间的方向。\n"
            u"   两条路线都需在改 CAD 前用 `simulation/mujoco/_work/opt_lib.py` 复核门槛；舵机余量复核（真实电机模型口径）与本项并行。")
s = s.replace(old_item[:end], new_item, 1)
p.write_text(s, encoding="utf-8")
print("PROJECT_STATUS.md updated")
