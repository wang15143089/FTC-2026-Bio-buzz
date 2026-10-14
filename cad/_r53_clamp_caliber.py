# -*- coding: utf-8 -*-
"""T06 R53f 夹紧态口径复算（CALCULATED）。

只读生成器里的常量文本（正则，不导入 OCC），复算两件事：
  1) 建模态链长：head 接触面 -> 平垫内侧面（含两处 0.30 mm 耳-板间隙）
  2) 装配夹紧后弹簧长度与预载（两种设定假设）

结论：0.30 mm 是「零件化建模的 running clearance」，装配后弹簧预载把两侧耳片
压到板面上（0.60 mm 归零）=> 摩擦副 = 2 面/螺柱，正是 clamp_calc 的 faces = 2.0。
输出 cad/output/_r53f_lock/caliber_clamp_interface.json，单位 mm / N。
"""
import io
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_B = ROOT / "cad" / "paddle_launcher_shooter_lock_r53b.py"
SRC_F = ROOT / "cad" / "paddle_launcher_shooter_lock_r53f.py"
SRC_R51 = ROOT / "cad" / "paddle_launcher_shooter_drive_r51.py"
OUT = ROOT / "cad" / "output" / "_r53f_lock" / "caliber_clamp_interface.json"


def const(src, name):
    txt = io.open(src, encoding="utf-8", newline="").read()
    m = re.search(r"^%s\s*=\s*([-0-9.]+)" % name, txt, re.M)
    assert m, "%s not found in %s" % (name, src.name)
    return float(m.group(1))


plate_t = const(SRC_R51, "PLATE_T")                     # 4.0
ear_t = const(SRC_B, "EAR_T")                           # 3.0
ear_gap = const(SRC_B, "EAR_GAP")                       # 0.30
txt_f = io.open(SRC_F, encoding="utf-8", newline="").read()
assert re.search(r"^SEAT_L\s*=\s*B\.SPRING_INSTALLED", txt_f, re.M), "SEAT_L binding changed"
seat_l = const(SRC_B, "SPRING_INSTALLED")  # SEAT_L = B.SPRING_INSTALLED (r53f)
spring_installed = const(SRC_B, "SPRING_INSTALLED")     # 6.0
spring_free = const(SRC_B, "SPRING_FREE")               # 8.4
spring_rate = const(SRC_B, "SPRING_RATE")               # 1.24 N/mm

# 建模态：耳片与板面各留 ear_gap；弹簧按 installed 画
modeled_chain = 2 * ear_t + 2 * ear_gap + plate_t + spring_installed
# 夹紧态 A（螺母拧到限位环端面）：两处耳-板间隙归零，弹簧 = 环长
clamped_a_spring = seat_l
clamped_a_preload = spring_rate * (spring_free - clamped_a_spring)
# 夹紧态 B（螺母只在未夹紧态按 installed 设定，链长不变）：间隙被吃掉 0.60
clamped_b_spring = modeled_chain - (2 * ear_t + plate_t)
clamped_b_preload = spring_rate * (spring_free - clamped_b_spring)

rep = {
    "caliber": "T06 R53f 夹紧态口径：0.30 mm 耳-板间隙是建模态 running clearance",
    "units": "mm / N",
    "inputs": {
        "plate_t_mm": plate_t, "ear_t_mm": ear_t, "ear_gap_mm": ear_gap,
        "seat_len_mm": seat_l, "spring_installed_mm": spring_installed,
        "spring_free_mm": spring_free, "spring_rate_n_per_mm": spring_rate,
    },
    "steps": {
        "modeled_chain_mm": modeled_chain,
        "modeled_ear_gap_total_mm": 2 * ear_gap,
        "clamped_spring_len_mm": clamped_a_spring,
        "clamped_preload_n_per_stud": clamped_a_preload,
        "loose_spring_len_mm": clamped_b_spring,
        "loose_preload_n_per_stud": clamped_b_preload,
    },
    "answer": {
        "ear_gap_in_assembly_mm": 0.0,
        "friction_faces_per_stud": 2,
        "preload_nominal_n_per_stud": clamped_a_preload,
        "preload_lower_bound_n_per_stud": clamped_b_preload,
        "assembly_instruction": "螺母拧到限位环端面贴合（preload = k x (free - ring))",
        "note": "0.30 mm 只存在于 CAD 建模态，装配后归零；夹紧摩擦只在归零后成立",
    },
    "status": "CALCULATED",
    "source": "docs/decision_log.md V-0055（夹紧态口径说明）",
}

OUT.parent.mkdir(parents=True, exist_ok=True)
io.open(OUT, "w", encoding="utf-8", newline="\n").write(
    json.dumps(rep, indent=2, ensure_ascii=False) + "\n")
print("modeled_chain_mm      =", modeled_chain)
print("clamped A preload (N) =", round(clamped_a_preload, 4))
print("loose  B preload (N)  =", round(clamped_b_preload, 4))
print("wrote", OUT)

