# -*- coding: utf-8 -*-
import sys, io
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path

SEC = """## T06 POLLEN V2 舵机选型校核与接触几何分析（2026-10-03）

- 用户指令（KNOWN）：核对 REV SRS V2 舵机规格是否满足 V2 送球段要求；若不满足，给出改善接触几何的方法。
- 舵机规格（KNOWN，用户提供规格图）：SRS V2 Balanced 6 V / 7.4 V → 13.5 / 16.7 kg·cm，0.14 / 0.12 s/60°；SRS V2 UltraSpeed 6 V / 7.4 V → 5.6 / 6.2 kg·cm，0.043 / 0.035 s/60°。换算 @7.4 V：Balanced 堵转 1.638 N·m、空载 83.3 rpm；UltraSpeed 堵转 0.608 N·m、空载 285.7 rpm。
- 送球需求（SIMULATED，本轮实测）：拨杆力矩门槛 ≈ **1.0 N·m**，且在 140–200 rpm 区间**基本不随转速变化**（105 rpm 即使给 1.5 N·m 也不发射，属转速受限，不是 torque 受限）→ 该需求是"球被夹住后的起步/突破力"，不是惯性力。
- 峰值扭矩（SIMULATED）：200 rpm 自由跑峰值 1.71 N·m，恰等于执行器 `kv·ω = 0.08 × 20.94 = 1.675`，即**拨杆在接球瞬间被完全卡停**；峰值与叶尖形状无关（5 种叶尖方案实测 1.69–1.72 N·m），说明缩短叶尖不能降低需求。
- 卡停机理（SIMULATED，接触对实测）：球在停位仅由 `tray` + `shell_lip_face` 支撑（V 形硬窝，球底距托板仅 0.07 mm）；峰值帧球同时接触 `paddle_blade`、`paddle_flex`、`tray`、`shell`、`shell_lip_face`、`strut` → 球被"叶片 + 固定件"多面夹持。
- 判定（CALCULATED）：**两型号均不满足直接驱动**。Balanced 扭矩够（1.638 > 1.0，余量 1.6×），但在该扭矩下转速仅约 22 rpm，远低于 105 rpm 下限；UltraSpeed 转速够（286 > 105），但堵转 0.608 < 1.0。所需机械功率 ≈ 1.0 N·m × 105 rpm ≈ 11 W（200 rpm 时 ≈ 21 W），该级别舵机理论极限（堵转 × 空载）仅 14–18 W、可用值约 5 W → 单只 SRS V2 无法直接驱动该送球段；需求点落在舵机扭矩—转速线段之外，减速比也无法解决。
- 改善接触几何方案（ASSUMED，待仿真验证）：A 225° 挡墙改斜楔/圆弧过渡，让球平滑导入外罩；B 托板末端缩进 10–15 mm 并下倾，使球窝下方让空；C 叶片前缘卸载（球还在托板上的 300°–330° 区段外缘半径 ≤ 58.4）+ 端角倒圆；D 球窝改单侧斜坡"逃逸窝"，只留托板 + 与出球方向相切的斜面。
- 产物（KNOWN）：`simulation/mujoco/out/servo_verdict_zh.png`、`contact_fix_options_zh.png`、`summary_v2_torque_detail.json`、`summary_v2_servo_req.json`、`summary_v2_blade_variants.json`。

"""

p = Path("PROJECT_STATUS.md"); s = p.read_text(encoding="utf-8")
assert "## NEXT ACTION" in s
s = s.replace("## NEXT ACTION", SEC + "## NEXT ACTION", 1)
old1 = "1. （立即）确认舵机（或拨杆传动）在 200 rpm（3.3 rev/s）处的可用扭矩，用以关闭 V2 送球段的 forcerange ±1.5 N·m 假设；这是拨杆转速门槛结论唯一的未关闭项。若实测扭矩不足，按 FINDINGS_v2_zh.md 第六节减小叶片端角半径或加陡托板末段。"
new1 = "1. （立即）舵机扭矩项已由本轮实测关闭为**不满足**：送球需求 ≈1.0 N·m 且需 ≥105 rpm，SRS V2 Balanced / UltraSpeed 均不达标（详见上节）。下一步按本轮 A–D 方案改接触几何（优先 A 唇口斜楔 + B 托板末端让位），改完重跑 `simulation/mujoco/pollen_v2_sim.py` 的力矩门槛扫描，目标把门槛降到 ≤1.0 N·m 并复核全流程；若几何改善不足，再考虑更大扭矩舵机或加一级减速。"
assert old1 in s
s = s.replace(old1, new1, 1)
p.write_text(s, encoding="utf-8")
print("PROJECT_STATUS.md updated")

q = Path("config/parameters.yaml"); lines = q.read_text(encoding="utf-8").split("\n")
out = []
for ln in lines:
    if ln.startswith("    paddle_torque_limit:"):
        out.append('    paddle_torque_limit: {value: 1.5, unit: "N*m", status: "SUPERSEDED", source: "old ASSUMED forcerange; replaced by paddle_torque_threshold below"}')
        out.append('    paddle_torque_threshold: {value: 1.0, unit: "N*m", status: "SIMULATED", source: "capped-torque launch scan: 0.8 N*m fails, 1.0 N*m launches at both 140 and 200 rpm; essentially speed-independent 105-200 rpm"}')
        out.append('    servo_direct_drive_feasible: {value: false, status: "CALCULATED", source: "REV SRS V2 Balanced 1.638 N*m / 83.3 rpm no-load and UltraSpeed 0.608 N*m / 285.7 rpm no-load; requirement is >=1.0 N*m AND >=105 rpm simultaneously; both outside their torque-speed line"}')
    elif ln.startswith("  open_question:"):
        out.append('  open_question: {value: "Servo torque question is now CLOSED as NOT SATISFIED: the feeder needs ~1.0 N*m at >=105 rpm and neither REV SRS V2 Balanced nor UltraSpeed can supply both. The paddle stalls completely at pickup (peak = actuator kv*omega), caused by the ball being pinched between the blade and the fixed parts (tray + 225 deg lip face + shell). Next: apply contact-geometry fixes A-D from the 2026-10-03 analysis (lip ramp, tray end relief, blade leading-edge relief, escape pocket) and re-run the capped-torque scan; the rigid (non zip-tie) blade and the ASSUMED 0.060 kg ball mass remain open.", status: "TBD"}')
    else:
        out.append(ln)
q.write_text("\n".join(out), encoding="utf-8")
import yaml
yaml.safe_load(q.read_text(encoding="utf-8"))
print("config/parameters.yaml updated + yaml OK")

f = Path("simulation/mujoco/out/FINDINGS_v2_zh.md")
f.write_text(f.read_text(encoding="utf-8") + "\n" + SEC.replace("## T06", "## 六、T06"), encoding="utf-8")
print("FINDINGS_v2_zh.md appended")
