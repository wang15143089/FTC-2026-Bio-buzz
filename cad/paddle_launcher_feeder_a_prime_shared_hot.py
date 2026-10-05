# -*- coding: utf-8 -*-
"""T06 R35: 按「热态外径」配轮轴间距的共用送球段（NECTAR + POLLEN）。

背景
----
飞轮是 goBILDA 3613-0014-0096（Ø96 × 24，30A 硅胶）。1620 rpm 下硅胶外缘
离心长大 dr（calculations/t06_flywheel_silicone_centrifugal.py）：
    M1 自由薄环（上界） 2.4-5.2 mm
    M2 厚环自由         0.6-1.2 mm
    M3 厚环固支（下界） 0.3-0.6 mm
设计取值 dr_hot = 0.8 mm（ASSUMED，见 DEC-0032）。

R27 的装配间距按冷态 Ø96 定（half_spacing = nip/2 + 48），轮子转起来后运行
夹口自动变成 nip - 2*dr，R33 仿真证明这会把 POLLEN 的送球相位打乱。
R34 仿真证明：把轮轴间距按热态外径装
    half_spacing = nip/2 + WHEEL_R + dr_hot
运行夹口恒为设计值（NECTAR 82 / POLLEN 64），30/30 通过、拨杆-飞轮零接触。

本模块只改轮轴间距，送球段（外罩 + 托盘 + 拨杆）几何与 R27 完全一致，
不覆盖 R27 的任何源文件或产物。

用法: python cad/paddle_launcher_feeder_a_prime_shared_hot.py [nectar] [pollen] [--stl]
产物: cad/output/_r35_hot/ （整机 STEP/STL + 报告 JSON）
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

DR_HOT_MM = 0.8                     # ASSUMED 设计膨胀量（DEC-0032）
OUT_DIR_NAME = "_r35_hot"

import paddle_launcher_feeder_a_prime_shared as SH  # noqa: E402

F = SH.F
pl = SH.pl


def build_variant_hot(name):
    """与 SH.build_variant 相同，只把轮轴间距加上热态膨胀量。"""
    v = SH.VARIANTS[name]
    ball_r, nip = v["ball_r"], v["nip"]
    half_spacing = nip / 2.0 + pl.WHEEL_OD / 2.0 + DR_HOT_MM
    F.BALL_D = 2.0 * ball_r
    F.BALL_R = ball_r
    F.R_CARRY = SH.R_IN - ball_r
    kept, dropped, relieved, consumed, kinematics = F.build(name, half_spacing)
    relief = SH._relieve_shell(kept)
    print("[hot %s] half_spacing = %.3f mm (nip %.1f + WHEEL_R 48 + dr %.2f)"
          % (name, half_spacing, nip, DR_HOT_MM), flush=True)
    return kept, dropped, relieved, consumed, kinematics, half_spacing, relief


SH.build_variant = build_variant_hot
SH.F.OUT = F.OUT / OUT_DIR_NAME
SH.F.OUT.mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    raise SystemExit(SH.main(sys.argv[1:]))
