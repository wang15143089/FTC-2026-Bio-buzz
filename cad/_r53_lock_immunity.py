# -*- coding: utf-8 -*-
r"""T06 R53h: 锁紧件对换档的几何免疫 + 夹紧件保持力口径（CALCULATED）。

不新增几何，只做三件事：
  1) 把 V-0056 的预载阈值反解成「限位环长度」窗口 => 不依赖预载数字的几何免疫证明
  2) 夹紧件单独保持力（每滑座）vs 发射反力峰值 / 舵机保持力
  3) 环端面压溃上限与 M4 拧紧力矩上限

输入全部读已落盘报告，输出 cad/output/_r53f_lock/immunity_r53_lock.json。
用法：.\.venv-cad\Scripts\python.exe -X utf8 cad\_r53_lock_immunity.py
"""
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTD = ROOT / "cad" / "output"
OUT = OUTD / "_r53f_lock" / "immunity_r53_lock.json"


def load(p):
    return json.load(io.open(p, encoding="utf-8"))

seat = load(OUTD / "_r53f_lock" / "report_r53f_pollen.json")
limit = load(OUTD / "_r53g_limit" / "report_r53g_preload_limit.json")["sweep"]
match = load(OUTD / "_r53e_match" / "report_r53e_match.json")
cal = load(OUTD / "_r53f_lock" / "caliber_clamp_interface.json")["steps"]

rate = seat["clamp_calc"]["spring_rate_n_per_mm"]
free = seat["clamp_calc"]["spring_free_mm"]
ring = seat["seat"]["length_mm"]
section = seat["seat"]["section_mm2"]
studs = seat["clamp_calc"]["studs_per_carriage"]
faces = 2.0
pre_nom = round(cal["clamped_preload_n_per_stud"], 4)
pre_lo = round(cal["loose_preload_n_per_stud"], 4)


def ring_len(p_n):
    return free - p_n / rate


l30 = limit["mu0.30"]
l60 = limit["mu0.60"]
imm = {
    "law": "preload(L) = k x (free - L)，L = 限位环长度（k = %.2f N/mm，free = %.1f mm）" % (rate, free),
    "ring_len_nominal_mm": ring,
    "ring_len_for_60pct_margin_mm": {
        "mu0.30": round(ring_len(l30["limit_60pct_stall_n"]), 3),
        "mu0.60": round(ring_len(l60["limit_60pct_stall_n"]), 3)},
    "ring_len_for_hard_stall_mm": {"mu0.60": round(ring_len(l60["limit_hard_n"]), 3),
                                   "mu0.30": None},
    "safe_ring_window_mm": [round(ring_len(l60["limit_60pct_stall_n"]), 3), free],
    "statement": "支配工况是 mu 0.60：环长 2.74 mm 才会吃掉 60 % 堵转余量，硬顶停要 -1.28 mm（负值，几何不可能）；mu 0.30 对应 -2.92 mm。=> 只要环长不超过弹簧自由长 8.4 mm，锁紧件在几何上不可能顶停 25-2",
    "statement2": "环长 >= 8.4 mm 或螺母未拧到端面 => 预载 <= 0 => 摩擦更小、换档更轻松；失效方向只有「锁不住」，没有「顶停」",
    "print_tolerance_mm": 0.2,
    "print_tolerance_n": seat["seat"]["print_tolerance_effect_n"],
    "margin_to_lower_bound_mm": round(ring - ring_len(l60["limit_60pct_stall_n"]), 3),
    "status": "CALCULATED",
}

# --- 2) 夹紧件单独保持力 vs 发射反力 / 舵机保持力
def hold(mu, pre):
    return mu * faces * studs * pre


rec = match["recoil"]
sh = match["servo_hold"]["f_hold_per_carriage_N"]
pk = {v: rec[v]["f_separation_per_carriage_peak_N"] for v in ("pollen", "nectar")}
tbl = {}
for tag, mu in (("mu0.30", 0.30), ("mu0.60", 0.60)):
    for ptag, pre in (("preload_nominal", pre_nom), ("preload_lower_bound", pre_lo)):
        h = hold(mu, pre)
        tbl["%s_%s" % (tag, ptag)] = {
            "preload_n_per_stud": pre,
            "friction_per_carriage_n": round(h, 2),
            "friction_both_carriages_n": round(2 * h, 2),
            "vs_pollen_recoil_peak_x": round(pk["pollen"] / h, 2),
            "vs_nectar_recoil_peak_x": round(pk["nectar"] / h, 2),
        }
hold_sum = {
    "recoil_peak_per_carriage_n": pk,
    "servo_hold_per_carriage_n": sh,
    "servo_margin_x": {v: round(sh[v] / pk[v], 2) for v in pk},
    "table": tbl,
    "verdict": "夹紧件保持力 14.3 N/滑座（mu 0.30、名义预载 2.976 N/颗）只有发射反力峰值 37.5 / 81.3 N 的 1/2.61、1/5.65 => 断电/无指令时夹紧件挡不住发射反力；发射时守住夹口的是通电的 25-2（余量 3.0x / 4.8x）。R53b 的「弹簧常压 => 断电也锁」应读作「挡得住 14.3 N/滑座以内的漂移」",
    "status": "CALCULATED",
}
# --- 3) 力矩与环端面强度（装配口径）
SIGMA_Y = 50.0
D_M4 = 4.0
K_TIGHT = 0.20
bearing_nom = pre_nom / section
over_axial = 3.0 * 1000.0 / (K_TIGHT * D_M4)
torq = {
    "ring_section_mm2": section,
    "bearing_stress_at_nominal_mpa": round(bearing_nom, 4),
    "bearing_stress_at_10x_mpa": round(bearing_nom * 10.0, 3),
    "material_yield_mpa": SIGMA_Y,
    "crush_limit_n": round(section * SIGMA_Y, 1),
    "k_factor": K_TIGHT,
    "m4_d_mm": D_M4,
    "over_torque_example_n_m": 3.0,
    "over_torque_axial_n": round(over_axial, 1),
    "crush_stress_at_over_torque_mpa": round(over_axial / section, 1),
    "torque_cap_n_m": 1.0,
    "statement": "螺母拧到与环端面贴合后轴向力由环承担：预载只由环长决定，力矩不再改变预载（几何免疫的工程实现）。名义预载下环端面应力 %.3f MPa，10 倍也只有 %.2f MPa，远低于 %.0f MPa 屈服。只有把环做长到超过弹簧自由长再强拧（约 3.0 N.m 量级）才会压溃环，按 1.0 N.m 上限 + 尼龙锁紧螺母 + 螺纹胶 243 即可排除。" % (bearing_nom, bearing_nom * 10.0, SIGMA_Y),
    "status": "CALCULATED",
}

inputs = {
    "spring_rate_n_per_mm": rate,
    "spring_free_mm": free,
    "spring_installed_mm": ring,
    "studs_per_carriage": studs,
    "faces": faces,
    "preload_nominal_n_per_stud": pre_nom,
    "preload_lower_bound_n_per_stud": pre_lo,
    "sources": [
        "cad/output/_r53f_lock/caliber_clamp_interface.json",
        "cad/output/_r53g_limit/report_r53g_preload_limit.json",
        "cad/output/_r53e_match/report_r53e_match.json",
    ],
}

rep = {
    "caliber": "T06 R53h 锁紧件对换档的几何免疫 + 夹紧件保持力口径",
    "units": "mm / N / N.m",
    "inputs": inputs,
    "immunity": imm,
    "hold": hold_sum,
    "torque": torq,
    "verdict": "锁紧件不会影响正常位置改变：失效方向只有「锁不住」（预载 <= 0），没有「顶停」。发射时守住夹口的是通电 25-2（余量 3.0x / 4.8x）。",
    "tbd": ["限位环 PET 压缩强度实测", "弹簧 k 实测", "台架 50 次来回后预载衰减", "实机验证"],
    "status": "CALCULATED",
}

OUT.parent.mkdir(parents=True, exist_ok=True)
io.open(OUT, "w", encoding="utf-8", newline="\n").write(
    json.dumps(rep, indent=2, ensure_ascii=False) + "\n")

print("safe_ring_window_mm =", imm["safe_ring_window_mm"], "margin =", imm["margin_to_lower_bound_mm"])
print("ring_len_for_60pct:", imm["ring_len_for_60pct_margin_mm"])
print("hold mu0.30 nominal:", tbl["mu0.30_preload_nominal"]["friction_per_carriage_n"],
      "x_pollen", tbl["mu0.30_preload_nominal"]["vs_pollen_recoil_peak_x"])
print("WROTE", OUT)
