# -*- coding: utf-8 -*-
import io, os, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

DEC = """## DEC-0026 - 送球门槛改用 12 s 统一预算重测；舵机问题由「不可行」改判为「可行」，推荐 25-4 Super Speed + R5

- Decision: 送球门槛的仿真预算由 7 s（单入口 x=145）统一改为 **12 s 且双入口（x=145 与 x=138）**，并以此重测 R5 几何（二指 θ=350/170 + D 球窝垫 6.8 mm）；**推荐几何由 R2 改为 R5**；舵机选型推荐 **goBILDA 25-4 Super Speed @7.4 V**。DEC-0025 的「0.46 N·m @90 rpm / 边界可行 / 单只 SRS V2 不得判定安全」结论记为 **SUPERSEDED**；其相对排序（A 唇口喇叭有效 −23%、D 球窝抬高有效 −28%、B 托板缩进无效、C 叶尖卸载恶化 +33%）与根因分析保留有效。
- Reason: 旧 7 s 预算下，30/40/60/70/75/145 rpm **即使把力矩限幅给到 3.0 N·m 也判失败**；把预算延长到 12 s 后这些转速**全部成功发射**。机理不是扭矩不足，而是**球在球窝里蠕动**：球滚下托板后停在球窝边缘（r≈83–95.5 mm，θ≈322–328°），要等指片转到才被抓住——40/50 rpm 首抓约 0.6 s，70 rpm 约 4.2 s。旧门槛 0.94 / 0.46 因此把「球还没被抓住」的耗时混进了力矩门槛，不是纯粹的发动力矩需求。
- Alternatives considered: (a) 保留 7 s 口径只调扭矩——会把「球还没被抓住」错判成「扭矩不够」，已用 3.0 N·m 仍失败反证否掉；(b) 只延长到 10 s——70 rpm 首抓约 4.2 s，余量偏薄，取 12 s；(c) 单入口 x=145——会漏掉入口位置敏感性，改为双入口取较坏值。
- Evidence/calculation: `simulation/mujoco/out/_r2r5_speed_req12.json`（R5，双入口，二分容差 ±0.03 N·m）门槛（N·m）：40/50 ≤0.24（0.24 是扫描下限，真实值 ≤0.24）、60 → 0.339、75 → 0.439、90 → 0.24、105 → 0.24、120 → 0.289、130 → 0.356、**145 → 0.472（最坏点）**、160 → 0.323、200 → 0.273、290 → 0.306。预算敏感性 `simulation/mujoco/_work/diag_lowrpm.py`、`_work/r5_lowrpm.py`；包线与舵机判定图 `simulation/mujoco/out/servo_envelope_zh.png`（脚本 `_work/servo_envelope_zh.py`）。R5 在 90/105 rpm 门槛仅 0.24，明显优于 R2。舵机换算 1 kg·cm = 0.0980665 N·m；厂家扭矩为堵转值，可用扭矩沿堵转→空载直线插值。
- Impact: 舵机问题由「不满足」改判为 **可行**。7.4 V 逐只判定：25-4 Super Speed（堵转 0.530 N·m / 空载 290 rpm）窗口 30–70、80–122 rpm → **推荐**（唯一能上 120 rpm，90–105 rpm 余量 >40%，避开 70–80 rpm 缺口）；25-3 Speed（1.059 / 145）30–110；Axon MAX MK2（3.825 / 100）30–94，低速余量最大；25-2 Torque 与 25-2 5-Turn（2.471 / 60）30–53，可用但慢（约 1.2 s/球）；旧参考件 REV SRS V2 UltraSpeed（0.608 / 285.7）30–125，**此前误判为不可行，现同样可用**。新增开放项：送球**相位敏感**——结论随拨杆转速经「指片—球到达相位」耦合，相邻 10 rpm 即可翻转（145 rpm 单入口过、双入口不过），拨杆转速必须锁在窗口内稳态运行；根因仍未解决——球停在 r≈95.5 mm 而设计轨道 R=58.4 mm，**差 37.1 mm**，送球仍靠叶尖拖拽而非输送轨道（DEC-0025 根因，本轮未改）。
- Reversible?: 是；旧 7 s 数字在 `config/parameters.yaml` 以 `SUPERSEDED` 标签连同原始 source 保留，可随时复算对比。
- Date/version: 2026-10-03 / C06B-POLLEN-FEEDER-V2

"""

# --- 1) decision_log.md ---
p = os.path.join(ROOT, "docs", "decision_log.md")
t = io.open(p, encoding="utf-8").read()
anchor = "- Date/version: 2026-10-03 / C06B-POLLEN-FEEDER-V2 候选修订（待用户接受）\n\n```text"
assert t.count(anchor) == 1, ("anchor count", t.count(anchor))
t = t.replace(anchor, "- Date/version: 2026-10-03 / C06B-POLLEN-FEEDER-V2 候选修订（待用户接受）\n\n" + DEC + "```text")
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("decision_log.md OK, lines =", t.count("\n"))

# --- 2) PROJECT_STATUS.md ---
p2 = os.path.join(ROOT, "PROJECT_STATUS.md")
s = io.open(p2, encoding="utf-8").read()
OLD_H = "## T06 POLLEN V2 舵机选型校核与接触几何分析（2026-10-03）"
NEW_BLOCK = """## T06 POLLEN V2 送球门槛重测与舵机选型（2026-10-03，DEC-0026 口径）

> 本节结论取代下方早先的「T06 POLLEN V2 舵机选型校核与接触几何分析（2026-10-03）」段落；该段落基于 7 s 仿真预算，混入了送料耗时假象，其原结论已标 SUPERSEDED 保留供上溯。

- 口径修正（KNOWN）：送球门槛仿真预算由 7 s / 单入口 x=145，统一改为 **12 s / 双入口 x=145 与 x=138**（取较坏值），二分容差 ±0.03 N·m。
- 修正原因（SIMULATED）：7 s 预算下 30/40/60/70/75/145 rpm 即使给到 3.0 N·m 也判失败；延长到 12 s 后全部成功发射。机理是**球在球窝蠕动**——球停在球窝边缘 r≈83–95.5 mm（θ≈322–328°），要等指片转到才被抓住，70 rpm 首抓约 4.2 s。旧门槛把送料耗时混进了发动力矩。
- R5 门槛（SIMULATED，`simulation/mujoco/out/_r2r5_speed_req12.json`，单位 N·m）：40/50 ≤0.24（扫描下限）、60 → 0.339、75 → 0.439、90 → 0.24、105 → 0.24、120 → 0.289、130 → 0.356、**145 → 0.472（最坏点）**、160 → 0.323、200 → 0.273、290 → 0.306。
- 几何取舍（SIMULATED）：推荐 **R5**（二指 θ=350/170 + D 球窝垫 6.8 mm）；90/105 rpm 门槛仅 0.24，优于 R2。DEC-0025 的 A 有效 / D 有效 / B 无效 / C 恶化的相对排序保留有效。
- 舵机判定（CALCULATED，7.4 V，厂家堵转值线性插值到空载）：**25-4 Super Speed 0.530 N·m / 290 rpm → 可直驱窗口 30–70、80–122 rpm，推荐**（唯一能上 120 rpm；90–105 rpm 余量 >40%；避开 70–80 rpm 缺口）；25-3 Speed 1.059 / 145 → 30–110；Axon MAX MK2 3.825 / 100 → 30–94（低速余量最大）；25-2 Torque 与 25-2 5-Turn 2.471 / 60 → 30–53（可用但慢，约 1.2 s/球）；REV SRS V2 UltraSpeed 0.608 / 285.7 → 30–125（**此前误判不可行，现同样可用**）。图：`simulation/mujoco/out/servo_envelope_zh.png`。
- 仍开放（TBD）：送球**相位敏感**（相邻 10 rpm 即可翻转结论），拨杆转速必须锁在窗口内稳态运行；根因未解决——球停 r≈95.5 mm 而设计轨道 R=58.4 mm，**差 37.1 mm**，送球靠叶尖拖拽而非输送轨道；R5 尚未进 CAD；刚性（非扎带）指片与 ASSUMED 0.060 kg 球质量仍未验证。

"""
assert s.count(OLD_H) == 1, ("header count", s.count(OLD_H))
s = s.replace(OLD_H, OLD_H + "\n\n> （SUPERSEDED by DEC-0026 — 以下内容为 7 s 预算下的旧口径，保留供上溯，不作为当前结论。）\n")
assert s.count("\n## NEXT ACTION\n") == 1
s = s.replace("\n## NEXT ACTION\n", "\n" + NEW_BLOCK + "## NEXT ACTION\n")

NEW_ITEM1 = """1. （立即）向用户确认是否锁定 **R5**（二指 θ=350/170 + 6.8 mm 球窝垫倒角）出 CAD V3。确认后改 `cad/paddle_launcher_feeder_redesign.py`（**不得改** `cad/paddle_launcher_constrained.py`、不得覆盖原 STEP），再用 `simulation/mujoco/_work/opt_lib.py` 复核门槛，最后制作台架实测。舵机推荐 goBILDA **25-4 Super Speed @7.4 V**，拨杆转速设定在 90–105 rpm（该区间门槛仅 0.24 N·m、余量 >40%，且避开 70–80 rpm 缺口）；**必须锁速**，因为送球结论对转速相位敏感。几何根因（球停 r≈95.5 mm vs 设计轨道 R=58.4 mm，差 37.1 mm）仍未解决，属已知风险。"""
lines = s.split("\n")
start = next(i for i, l in enumerate(lines) if l.startswith("1. （立即）"))
end = next(i for i, l in enumerate(lines) if l.startswith("2. （并行阻塞项）"))
lines[start:end] = [NEW_ITEM1, ""]
s = "\n".join(lines)
io.open(p2, "w", encoding="utf-8", newline="\n").write(s)
print("PROJECT_STATUS.md OK, lines =", s.count("\n"))
