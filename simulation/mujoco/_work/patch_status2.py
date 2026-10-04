# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
p = Path("PROJECT_STATUS.md")
txt = p.read_text(encoding="utf-8")
old_start = "1. （立即）舵机扭矩项已由本轮实测关闭为**不满足**"
i = txt.index(old_start)
j = txt.index("2. （并行阻塞项）", i)
new = """1. （立即）接触几何方案已逐个仿真完成，**最优组合 = 二指 θ=350/170 + A 唇口喇叭（可选 + D 6.8 mm 球窝垫）**：门槛 0.46 N·m @90 rpm（现状 0.94 N·m @120–140 rpm），稳健 2/2。几何净效果（200 rpm，二分 0.05 N·m，已现场复跑逐字复现）：A 唇口喇叭 0.72（−23%，有效）、B 托板缩进 0.94（无效，归档）、C 叶尖卸载 1.25（恶化，归档）、D 球窝抬高 6.8 为 0.68（−28%，有效）、A+D 0.64 但稳健 1/2。根因是指片布置：现状三指 120° 相位下球**滚不到唇口**，停在指片尖端平面 r=95.5 mm（设计轨道 R58.4），送球全靠叶尖拖拽。下一步：先用 `geom_options_verdict_zh.png` 与二指方案示意向用户确认，再改 `cad/paddle_launcher_feeder_redesign.py`（不得改 `cad/paddle_launcher_constrained.py`、不得覆盖原 STEP）→ 重跑 `simulation/mujoco/_work/opt_lib.py` 复核 → 制作台架实测。注意：0.42–0.46 N·m 刚好压在 SRS V2 UltraSpeed 7.4 V 线性包络边界（@90 rpm 仅 0.416 N·m），属**边界可行**，不得判定单只 SRS V2 直驱安全，必须实物验证。
"""
txt = txt[:i] + new + txt[j:]
p.write_text(txt, encoding="utf-8")
print("PROJECT_STATUS.md NEXT ACTION 已更新")
