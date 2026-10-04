# -*- coding: utf-8 -*-
"""Record DEC-0027: R6 smooth-arc candidate + creep root cause (rest-pocket jam)."""
import io, pathlib

DEC = u"""
## DEC-0027 — 送球段「平滑曲面」优化（R6）与蠕动根因：卡滞在停位球窝，不在接合处台阶

- Decision: 新增候选几何 **R6**：取消 R5 的 30×108×12.8 平垫块，把外罩内弧（r = R_IN = 93.96 mm，圆心 = 拨杆轴 29.49/111.46）从 225° 唇口沿同一半径平滑延伸到 **260.2°**，终点落在托板顶面 x = 13.5 mm（z = 18.87 mm，该处抬升 0.0 mm、与托板相切）；弧面块用 12 段 box 近似，与 `shell_*` 同类。**R5 保留不删**，与 R6 并列记录；R6 标为**候选，待用户接受**。两种几何都仅存在于 MuJoCo 仿真，**均尚未进入 CAD**。
- Reason: 用户 2026-10-03 指令「采用 goBILDA 25-4 Super Speed（0.530 N·m / 290 rpm），尝试对 R5 优化，把外罩和球窝垫用平滑曲面连接，看会不会效果更好、尽量减少球的蠕动」。仿真给出的答案是**不能**：抓球前等待 2.98 s → 2.93 s（仅 −1.7%，在噪声量级），全程 7.49 s → 7.38 s（−1.5%）。因此本决策记录的是「R6 有效但微小 + 蠕动根因另有他处」，而不是把 R6 当作已解决的问题。
- Alternatives considered: (a) R5 原样（二指 θ=350/170 + 6.8 mm 平垫块，基线，保留）；(b) **R6** 弧面延伸到与托板相切（本决策，推荐用于「本来就要改版」的场合，因为它少一个零件、无台阶）；(c) R6c 弧面止于 256° 且半径收窄 2 mm（全程再快 0.26 s / 3.5%，但球窝变窄、对球径与公差更敏感，未推荐）。三者均一次通过全流程（launched=True），出口球速 6.67 m/s、飞轮 1620 rpm，无失败工况可区分优劣，只能按时间排序。
- Evidence/calculation: 图 `simulation/mujoco/out/r5_vs_r6_smooth_zh.png`（脚本 `_work/r6_fig_zh.py`）；数据 `_work/r6_summary.py` → `out/_r6_summary.json`、`out/_r6_fig_data.json`。电机模型 `_work/r6_motor.py`：把 `paddle_vel` 的 `kv` 由 0.08 换成 25-4 的真实线性斜率 kv = 0.530 /(290·2π/60) = 0.017452、`forcerange` 改为 ±0.530、`ctrl` = 空载 290 rpm（即全油门直流电机线 T = T_stall(1 − ω/ω_free)）；球从托板 x = 145 mm 滚入，12 s 预算。结果（s，抓球前蠕动 / 运载 / 放球—发射）：R5 2.98 / 3.72 / 7.49；R6 2.93 / 3.66 / 7.38；R6c 2.99 / 3.46 / 7.23。运载段实测（拨杆转速 / 输出力矩均值）：R5 3.95 rpm / 0.523 N·m；R6 4.05 rpm / 0.523 N·m；R6c 4.36 rpm / 0.522 N·m。
- Evidence/calculation（蠕动根因，独立复测）: `_work/r7_loadprobe2.py` 用同一 R5 几何把拨杆换成刚性速度源（kv = 0.08、指令 145 rpm、限幅放宽到 ±5 N·m），运载段拨杆仍只有约 6.8 rpm、出力约 1.16 N·m；球心半径实测 59.4 mm（设计 R_CARRY = 58.4 mm）。**蠕动发生在球停稳后的停位球窝**：球停稳在 r ≈ 83–95 mm、角 ≈ 322–329°，被指片楔住，把拨杆拖到几 rpm，等楔口松脱（约 2.3 s @145 rpm 指令）才被指片带入运载轨道。接合处的台阶在蠕动时段根本不参与接触。
- Impact: (1) 「外罩—球窝接合处形状」被证伪为蠕动的成因，**不得再作为缩短循环时间的手段**；有效方向是改**停位球窝**（让球停在指片扫掠范围之外）或提高伺服扭矩。(2) 舵机余量口径需重开：DEC-0026 的 `paddle_torque_threshold_12s_by_rpm` 由 kv = 0.08 的假执行器取得，「通过」只表示在限幅内 12 s 跑完，与真实电机模型的扭矩余量不是同一件事；本决策只主张「25-4 全油门模型下运载段拨杆约 4 rpm、出力 0.523 N·m 已贴 0.530 N·m 堵转，余量很薄」，**不主张 DEC-0026 的 0.24 N·m 数字作废**（两者口径不同，不可直接相除比较）。(3) 卡滞力矩在仿真里对接触正则化与到达相位敏感（同一几何在 3.95 rpm 与 6.8 rpm 下分别读出 0.52 与 1.16 N·m），上述绝对值只能当量级参考，**不得作为选型定论**。(4) R6 若被接受，需在 `cad/paddle_launcher_feeder_redesign.py` 增加「弧面替换平垫块」的生成逻辑；**不得改** `cad/paddle_launcher_constrained.py`、不得覆盖原 STEP。
- Reversible?: 是。R5 与 R6/R6c 的几何、脚本与数据全部保留，可随时复算对比；被替代方案以本记录链接，不删除历史。
- Date/version: 2026-10-03 / C06B-POLLEN-FEEDER-V2（R6 候选，待用户接受）

"""

p = pathlib.Path("docs/decision_log.md")
s = p.read_text(encoding="utf-8")
marker = "```text\nDecision:"
assert marker in s, "template block not found"
s = s.replace(marker, DEC.lstrip("\n") + marker, 1)
p.write_text(s, encoding="utf-8")
print("decision_log.md: DEC-0027 added")
