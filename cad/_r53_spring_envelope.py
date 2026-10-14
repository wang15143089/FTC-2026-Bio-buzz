# -*- coding: utf-8 -*-
r"""T06 R53h-2: 弹簧采购包络 + 限位环长反解。

目的：让「锁紧件不影响正常位置改变（不顶停 25-2）」这条不变量**不依赖未实测的 k**。
做法：CAD 里环长固定 6.0 mm，于是预载 = k x (L0 - 6.0)，只由买到的弹簧 (k, L0) 决定；
      把 V-0056 的门槛换算成对 (k, L0) 的采购包络，并给出「若弹簧偏离设计值，环长应取多少」。

只读已落盘报告，输出 cad/output/_r53f_lock/spring_envelope_r53h.json。
用法：.\.venv-cad\Scripts\python.exe -X utf8 cad\_r53_spring_envelope.py
"""
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTD = ROOT / "cad" / "output"
OUT = OUTD / "_r53f_lock" / "spring_envelope_r53h.json"


def load(p):
    return json.load(io.open(p, encoding="utf-8"))


seat = load(OUTD / "_r53f_lock" / "report_r53f_pollen.json")
limit = load(OUTD / "_r53g_limit" / "report_r53g_preload_limit.json")["sweep"]

RING = seat["seat"]["length_mm"]
pre_target = seat["seat"]["preload_n_per_stud_geometric"]
cap60 = limit["mu0.60"]["limit_60pct_stall_n"]
cap_hard = limit["mu0.60"]["limit_hard_n"]
floor = 1.5
spec_k = seat["clamp_calc"]["spring_rate_n_per_mm"]
spec_l0 = seat["clamp_calc"]["spring_free_mm"]

L0S = [6.5, 7.0, 7.5, 8.0, 8.4, 8.8, 9.0, 9.5, 10.0, 11.0, 12.0]
env = {}
for l0 in L0S:
    d = l0 - RING
    env["L0_%.1f" % l0] = {
        "travel_mm": round(d, 2),
        "k_max_60pct_n_per_mm": round(cap60 / d, 3),
        "k_max_hard_n_per_mm": round(cap_hard / d, 3),
        "k_min_floor_n_per_mm": round(floor / d, 3),
        "k_for_target_preload_n_per_mm": round(pre_target / d, 4),
        "preload_at_spec_k_n": round(spec_k * d, 3),
    }

adj = {}
for l0 in (7.0, 8.0, 8.4, 9.0, 10.0, 12.0):
    for k in (0.8, 1.0, 1.24, 1.5, 2.0, 2.5, 3.0):
        adj["L0_%.1f_k_%.2f" % (l0, k)] = {
            "ring_len_for_target_mm": round(l0 - pre_target / k, 3),
            "ring_len_min_for_60pct_mm": round(l0 - cap60 / k, 3),
            "preload_with_cad_ring_n": round(k * (l0 - RING), 3),
            "verdict": "ok" if k * (l0 - RING) <= cap60 else "over_60pct",
        }

spec_preload = spec_k * (spec_l0 - RING)
worst = {"k_n_per_mm": round(cap60 / (spec_l0 - RING), 3),
         "note": "在 L0 = 8.4 mm 时，弹簧刚度不得超过此值，否则 CAD 的 6.0 mm 环会吃掉 60 % 堵转余量"}

rep = {
    "caliber": "T06 R53h-2 弹簧采购包络 + 限位环长反解（让锁紧件不顶停换档舵机）",
    "units": "mm / N / N/mm",
    "inputs": {
        "ring_len_mm": RING,
        "preload_target_n_per_stud": round(pre_target, 4),
        "cap_60pct_n_per_stud": cap60,
        "cap_hard_n_per_stud": cap_hard,
        "floor_n_per_stud": floor,
        "design_spring": {"k_n_per_mm": spec_k, "free_len_mm": spec_l0,
                          "preload_n_per_stud": round(spec_preload, 4)},
        "spring_size_limits": {
            "od_max_mm": 5.6,
            "id_min_mm": 4.1,
            "why": "弹簧在限位环内（环内径 5.7）、套在 M4 螺柱外（Ø4.0），安装长 6.0 mm",
        },
        "sources": [
            "cad/output/_r53f_lock/report_r53f_pollen.json",
            "cad/output/_r53g_limit/report_r53g_preload_limit.json",
        ],
    },
    "rule": "预载 = k x (L0 - 6.0)。只要 k x (L0 - 6.0) <= 7.02 N（60 % 堵转余量门槛，mu 0.60），锁紧件就不可能顶停 25-2；>= 1.5 N 才算夹得住。",
    "envelope": env,
    "adjust": adj,
    "spec": {
        "requirement": "k x (L0 - 6.0) in [1.5, 7.0] N，OD <= 5.6 mm，ID >= 4.1 mm，安装长 6.0 mm",
        "k_cap_at_L0_8p4": worst,
        "if_out_of_window": "按实测 (k, L0) 反解环长 L = L0 - 2.976/k（下限 L0 - 7.02/k），改打印环长而不是改装配力矩",
    },
    "status": "CALCULATED",
    "tbd": ["实测购得弹簧的 k 与 L0", "限位环打印长度与 PET 压缩强度", "台架 50 次来回后预载衰减", "实机"],
}

OUT.parent.mkdir(parents=True, exist_ok=True)
io.open(OUT, "w", encoding="utf-8", newline="\n").write(
    json.dumps(rep, indent=2, ensure_ascii=False) + "\n")

print("设计弹簧 k=%.2f L0=%.1f => 预载 %.3f N" % (spec_k, spec_l0, spec_preload))
print("L0=8.4 时刚度上限: %.3f N/mm (60%% 门槛)" % worst["k_n_per_mm"])
for key in ("L0_8.4", "L0_7.0", "L0_10.0"):
    print(key, "-> k_max_60pct =", env[key]["k_max_60pct_n_per_mm"], "k_for_target =", env[key]["k_for_target_preload_n_per_mm"])
print("WROTE", OUT)
