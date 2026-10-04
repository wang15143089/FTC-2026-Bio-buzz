# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
p = Path("docs/decision_log.md")
txt = p.read_text(encoding="utf-8")
if "DEC-0025" in txt:
    print("已存在，跳过"); raise SystemExit
marker = "```text\nDecision:"
i = txt.index(marker)
entry = """## DEC-0025 — 送球段方案取舍：以指片布置为主、唇口喇叭为辅，B/C 归档

- Decision: V2 送球段的改进以**指片布置**为主杠杆——由现状三指 120° 等分（θ=342/222/102）改为**二指对置 180°（θ=350/170）**；几何上叠加 **A 唇口喇叭**（删 225° 挡墙，改 227.5/231.5/235.5° 三段斜楔，r_in 95.5/99.5/103.5），可选叠加 **D 球窝抬高 6.8 mm**。目标门槛 **0.46 N·m @ 90 rpm**、稳健 2/2。**B 托板末端缩进与 C 叶尖卸载记为负结果并归档，不再投入**。
- Reason: 逐个仿真实测显示真正的门槛来源不是唇口而是指片停位——现状三指相位下球**滚不到唇口**，沿托板滚到 X≈112（θ=330°）即撞在指片**尖端平面**上停住，球心 r=95.5 mm，而设计轨道为 R=58.40 mm；送球完全靠叶尖拖拽与硬夹，这才是 0.94 N·m 的来源。改二指对置后停位让出球道，门槛降至 0.55，叠加 A 后 0.46。
- Alternatives considered: (a) 仅做 A 唇口喇叭 0.72（−23%，有效但不足）；(b) 仅做 B 托板缩进 0.94（与现状相同，无效）；(c) 仅做 C 叶尖卸载 1.25（比现状恶化 33%）；(d) 仅做 D 球窝抬高 0.68（−28%，有效）；(e) A+D 0.64（最低但稳健性掉到 1/2）；(f) R2/R5/R3 二指组合 0.46/0.42/0.42，稳健均 2/2 —— **采用 (f) 的 R2**。
- Evidence/calculation: `simulation/mujoco/out/FINDINGS_v2_zh.md` 第七节；`summary_v2_rerun_opts.json`（逐个复跑，与首轮逐字一致）；`summary_v2_phase.json`、`summary_v2_best.json`；总图 `geom_options_verdict_zh.png`；脚本 `_work/opt_lib.py`、`_work/rerun_opts.py`、`_work/best_probe2.py`。工况：拨杆 200 rpm，球从托板 X=145 滚入，门槛用二分法求最小可通过力矩限幅，分辨率 0.05 N·m。全流程 `pass`（飞轮 1620 rpm → 出口 6.53 m/s @ 50.2°）。摩擦为**反杠杆**：μ_ball 1.0→0.94、0.7→1.16、0.5/0.35→>1.6 不发射；μ_shell 无影响（球 geom `priority=1` 覆盖）。
- Impact: 送球门槛从 0.94 降到 0.46 N·m（−51%），转速门槛从 120–140 rpm 降到 90 rpm，但仍**只压在 SRS V2 UltraSpeed 7.4 V 线性包络边界**（该转速下模型可用 0.416 N·m）——属**边界可行**，**不得判定单只 SRS V2 直驱安全**，必须台架实测。二指转子**尚未进入 CAD**：`cad/paddle_launcher_feeder_redesign.py` 仍生成原三指转子，改 CAD 前需先经用户确认方案示意。
- Reversible?: 是；B/C 负结果以 `superseded` 方式归档，保留原始数据与判据以便复算。
- Date/version: 2026-10-03 / C06B-POLLEN-FEEDER-V2 候选修订（待用户接受）

"""
txt = txt[:i] + entry + txt[i:]
p.write_text(txt, encoding="utf-8")
print("DEC-0025 已写入 docs/decision_log.md")
