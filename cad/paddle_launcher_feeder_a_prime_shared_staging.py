# -*- coding: utf-8 -*-
"""T06 R37 / DEC-0035 + DEC-0036: 等待区搬出扫掠圆（方向 B）+ 重叠实体清理（b）。

方向 B（DEC-0035）——等待球必须在扫掠圆外
----------------------------------------
拨杆扫掠带 = 绕轴心 C=(29.49, 111.46) mm、半径 0..60 mm 的圆盘（叶片 46..58、
TPU 尖 56..60、宽度 ±48 mm）。球心距轴心的安全下限 = 60 + r_ball：
    NECTAR  r = 45.974  ->  105.974 mm
    POLLEN  r = 35.560  ->   95.560 mm
托板面是绕 C 与 R_IN = 107.974 圆相切的 5° 斜面，球心距轴心 d(s)=sqrt(R_CARRY^2+s^2)
（s = 沿托板上坡的距离，R_CARRY = R_IN - r_ball = 62.000 / 72.414）⇒ 等待区从切点
起算：NECTAR s>=85.9 mm（x>=124.5）、POLLEN s>=62.3 mm（x>=101.0）。
排队时第 k 颗的球心 s=(k-1)*2r，所以**第 2 颗本来就落在安全区**：
    NECTAR  第 2 颗 x=126.49（限 120.5）余量 6.0 mm
    POLLEN  第 2 颗 x=106.65（限  97.5）余量 9.2 mm
R36 里「托板上 x>=30 的球被打飞」是**探针瞬时位**（滚落途中），不是排队稳态位；
真正的限制是容量：托板右端（进料口）原在 x=150，NECTAR 第 2 颗球面要到 172.46，
装不下 ⇒ 实测容量 NECTAR 1 / POLLEN 2。

本模块对 B 只有一处几何改动：``TRAY_X1 = 150.0 -> 215.0``（+65 mm）。加长后：
    NECTAR  2 颗（球心 34.894 停位 + 126.49 等待，球面到 172.46）
    POLLEN  3 颗（球心 35.802 / 106.65 / 177.50，球面到 213.05）
除停位球（本来就要被叶片推）以外，所有等待球都在扫掠圆外。轮轴间距按 DEC-0032
的热态口径 half_spacing = nip/2 + WHEEL_OD/2 + dr_hot（= R35 已接受的装配口径）。

(b) 重叠实体清理（DEC-0036）
---------------------------
R37 普查实测（cad/output/_r37_census3.json，布尔交）：
    paddle_hub  x  paddle_arm_1/2        295.762 mm3   x2   -> 并为一个 paddle_rotor
    paddle_blade x paddle_flex_tip_1/2  5760.000 mm3   x2   -> 尖片径向缩到 r 58..60
    guide_roof_3 x guide_wall_3_+1/-1    315.000 mm3   x2   -> 侧壁按 0.5 mm 间隙让位
    feeder_shell_tray 为 2 个相接实体（球道弧 + 托板只在切点相碰）
                                                        -> 托板向里延 14 mm 后并为一个
    另外：轮毂内孔 Ø4.1 与 Ø12 拨杆轴实测相交（占位孔），改为 Ø12.1 让位孔。
清理后本模型内的自制件两两重叠 = 0，每个部件 = 1 个实体。

不覆盖 R27 / R35 的源文件与产物。
用法: python cad/paddle_launcher_feeder_a_prime_shared_staging.py [nectar] [pollen] [--dry] [--stl]
产物: cad/output/_r37_stage/（--dry 只算不导出）
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

STAGE_X1 = 215.0          # DEC-0035: 托板右端 / 进料口 150 -> 215（+65 mm）
TRAY_ROOT_EXT = 14.0      # DEC-0036: 托板向里延，与球道弧体积相交后才能并为一个实体
DR_HOT_MM = 0.8           # DEC-0032 热态膨胀（R35 口径）
SWEEP_MAX_R = 60.0        # DEC-0034 实测：TPU 尖外缘 r = 60
HUB_BORE_D = 12.1         # DEC-0036: 原 Ø4.1 占位孔与 Ø12 拨杆轴相交
FLEX_TIP_R0, FLEX_TIP_R1 = 58.0, 60.0    # TPU 尖只保留伸出叶片的那 2 mm
OUT_DIR_NAME = "_r37_stage"

import cadquery as cq                                    # noqa: E402
from cadquery import exporters                           # noqa: E402

import paddle_launcher_feeder_a_prime_shared as SH       # noqa: E402

F = SH.F
pl = SH.pl

# ------------------------------------------------------------- geometry overrides
F.TRAY_X1 = STAGE_X1
F.TRAY_X0 = SH.CUT_X - TRAY_ROOT_EXT
F.OUT = F.OUT / OUT_DIR_NAME
F.OUT.mkdir(parents=True, exist_ok=True)


def _paddle_parts_clean():
    """一个刚性拨杆本体（轮毂+双臂+双叶片并为一个实体）+ 两片 TPU 尖（0 重叠）。"""
    cx, _, cz = pl.PADDLE_CENTER
    c = pl.C["paddle"]
    rotor = pl.cyl_y(SH.HUB_R, 34.0, pl.PADDLE_CENTER).cut(
        pl.cyl_y(HUB_BORE_D / 2.0, 38.0, pl.PADDLE_CENTER))
    for a in SH.BLADE_PHASE:
        rotor = rotor.fuse(pl.box(36, 18, 10, (cx + 28, 0, cz)).rotate(
            pl.PADDLE_CENTER, (cx, 1, cz), a))
        rotor = rotor.fuse(pl.box(12, pl.PADDLE_W, 30, (cx + 52, 0, cz)).rotate(
            pl.PADDLE_CENTER, (cx, 1, cz), a))
    parts = [("paddle_rotor", rotor.clean(), c)]
    for i, a in enumerate(SH.BLADE_PHASE, 1):
        r_mid = 0.5 * (FLEX_TIP_R0 + FLEX_TIP_R1)
        parts.append(("paddle_flex_tip_%d" % i,
                      pl.box(FLEX_TIP_R1 - FLEX_TIP_R0, pl.PADDLE_W, 34,
                             (cx + r_mid, 0, cz)).rotate(
                          pl.PADDLE_CENTER, (cx, 1, cz), a), None))
    return parts


pl.paddle_parts = _paddle_parts_clean

# 父模块 build() 的保留过滤器只认 KEEP_PREFIXES / KEEP_EXACT 里的名字；
# “拨杆并为一个实体”后部件名变成 paddle_rotor，必须显式加入保留名单，
# 否则 build() 会在过滤阶段把它丢掉（R37 第一次 dry-run 的 KeyError 根因）。
F.KEEP_EXACT = tuple(F.KEEP_EXACT) + ("paddle_rotor",)


# ------------------------------------------------------------------ ball / tray math
def _tray_top_z(x):
    return F.PIVOT_Z + (x - F.PIVOT_X) * math.tan(math.radians(F.TILT_DEG))


def ball_centre_track(ball_r):
    """托板上（含球道停位）的球心，按上坡方向依次排开；最后一颗球面不得越过进料口。"""
    n = (math.sin(math.radians(F.TILT_DEG)), -math.cos(math.radians(F.TILT_DEG)))
    foot = (F.PADDLE_CX + SH.R_IN * n[0], F.PADDLE_CZ + SH.R_IN * n[1])
    c0 = (foot[0] - ball_r * n[0], foot[1] - ball_r * n[1])
    d = (math.cos(math.radians(F.TILT_DEG)), math.sin(math.radians(F.TILT_DEG)))
    out = [c0]
    while True:
        c = (out[-1][0] + 2.0 * ball_r * d[0], out[-1][1] + 2.0 * ball_r * d[1])
        if c[0] + ball_r > STAGE_X1 + 1.0e-9:
            break
        out.append(c)
    return out


def safe_limit_x(ball_r):
    target = SWEEP_MAX_R + ball_r
    lo, hi = 0.0, STAGE_X1
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        d = math.hypot(mid - F.PADDLE_CX, F.PADDLE_CZ - (_tray_top_z(mid) + ball_r))
        lo, hi = (mid, hi) if d < target else (lo, mid)
    return 0.5 * (lo + hi)


def queue_report(ball_r):
    lim = safe_limit_x(ball_r)
    slots = []
    for k, (x, z) in enumerate(ball_centre_track(ball_r), 1):
        d = math.hypot(x - F.PADDLE_CX, F.PADDLE_CZ - z)
        need = SWEEP_MAX_R + ball_r
        slots.append({"slot": k, "x_mm": round(x, 3), "z_mm": round(z, 3),
                      "centre_to_axis_mm": round(d, 3),
                      "required_min_mm": round(need, 3),
                      "clear_of_sweep": bool(d >= need),
                      # slot 1 = 停在扫掠圆内的待推球：这是设计意图（叶片就是要推它）
                      "expected_pushed": k == 1,
                      "margin_mm": round(d - need, 3)})
    waiting = [s for s in slots if s["slot"] > 1]
    return {"ball_r_mm": round(ball_r, 3), "capacity_balls": len(slots),
            "waiting_zone_starts_at_x_mm": round(lim, 3),
            "waiting_balls_all_clear": all(s["clear_of_sweep"] for s in waiting),
            "slots": slots}


# COTS 前缀：厂商 STEP 派生件（飞轮/轴），多实体属于供应商装配语义，不参与判定。
COTS_PREFIXES = ("gecko_flywheel_", "flywheel_shaft_", "paddle_shaft_2106")


def _is_our_part(name):
    return not name.startswith(COTS_PREFIXES)


# ------------------------------------------------------------------- cleanup pass
def _cleanup(kept):
    """(b)：让位 + 并实体。返回清理记录。"""
    rec = {"guide_wall_relief": {}, "single_solid_check": {}}
    roof = kept.get("guide_roof_3")
    if roof is not None:
        grown = SH._grow(roof, SH.RELIEF_CLEARANCE_MM)
        cutter = grown if grown is not None else roof
        for n in ("guide_wall_3_+1", "guide_wall_3_-1"):
            w = kept.get(n)
            if w is None:
                continue
            v = max(0.0, w.intersect(roof).Volume())
            if v <= 0.0:
                continue
            kept[n] = w.cut(cutter).clean()
            rec["guide_wall_relief"][n] = round(v, 4)
    for n, s in kept.items():
        try:
            rec["single_solid_check"][n] = len(s.Solids())
        except Exception:
            rec["single_solid_check"][n] = -1
    return rec


def build_variant_stage(name):
    v = SH.VARIANTS[name]
    ball_r, nip = v["ball_r"], v["nip"]
    half = nip / 2.0 + pl.WHEEL_OD / 2.0 + DR_HOT_MM
    F.BALL_D = 2.0 * ball_r
    F.BALL_R = ball_r
    F.R_CARRY = SH.R_IN - ball_r
    t0 = time.time()
    kept, dropped, relieved, consumed, kinematics = F.build(name, half)
    relief = SH._relieve_shell(kept)
    cleanup = _cleanup(kept)
    print("[stage %s] %.1f s  half_spacing=%.3f  tray x=[%.1f %.1f]  kept=%d"
          % (name, time.time() - t0, half, F.TRAY_X0, F.TRAY_X1, len(kept)), flush=True)
    return kept, dropped, relieved, consumed, kinematics, half, relief, cleanup


def _rotor_checks(kept):
    """自制件两两重叠 + 拨杆轴/轮毂配合 的最终实测。"""
    res = {"our_part_overlaps_mm3": {}, "shaft_fit_mm3": {}}
    ours = [n for n in kept if n == "feeder_shell_tray" or n.startswith(
        ("paddle_rotor", "paddle_flex_tip_", "paddle_shaft_support_bridge",
         "guide_", "shooter_throat_"))]
    for i in range(len(ours)):
        for j in range(i + 1, len(ours)):
            a, b = ours[i], ours[j]
            ba, bb = kept[a].BoundingBox(), kept[b].BoundingBox()
            if (bb.xmax <= ba.xmin or ba.xmax <= bb.xmin or bb.ymax <= ba.ymin
                    or ba.ymax <= bb.ymin or bb.zmax <= ba.zmin or ba.zmax <= bb.zmin):
                continue
            v = kept[a].intersect(kept[b]).Volume()
            if v > 1.0e-6:
                res["our_part_overlaps_mm3"]["%s|%s" % (a, b)] = round(v, 4)
    for n in ("paddle_shaft_2106-4008-1920",):
        if n in kept:
            res["shaft_fit_mm3"][n + "|paddle_rotor"] = round(
                max(0.0, kept[n].intersect(kept["paddle_rotor"]).Volume()), 4)
            res["shaft_fit_mm3"][n + "|paddle_shaft_support_bridge"] = round(
                max(0.0, kept[n].intersect(kept["paddle_shaft_support_bridge"]).Volume()), 4)
    return res


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    dry = "--dry" in argv
    want_stl = "--stl" in argv
    names = [a for a in argv if not a.startswith("-")] or ["nectar", "pollen"]

    out = {"units": "mm", "round": "R37 / DEC-0035 (方向 B) + DEC-0036 (清理)",
           "geometry_change": {"tray_x1_mm": [150.0, STAGE_X1],
                               "tray_x0_root_extension_mm": TRAY_ROOT_EXT,
                               "hub_bore_d_mm": [4.1, HUB_BORE_D],
                               "flex_tip_radial_range_mm": [56.0, 60.0, FLEX_TIP_R0, FLEX_TIP_R1],
                               "flywheel_dr_hot_mm": DR_HOT_MM},
           "untouched_inputs": ["cad/paddle_launcher_constrained.py",
                                "cad/paddle_launcher_feeder_a_prime.py",
                                "cad/paddle_launcher_feeder_redesign.py",
                                "cad/paddle_launcher_feeder_a_prime_shared.py",
                                "cad/paddle_launcher_feeder_a_prime_shared_hot.py"],
           "paddle_axis_mm": [F.PADDLE_CX, 0.0, F.PADDLE_CZ],
           "shell_inner_mm": SH.R_IN, "shell_sector_deg": [F.A_EXIT, SH.A_LIP],
           "sweep_max_r_mm": SWEEP_MAX_R, "feeder_width_mm": F.FEEDER_W,
           "variants": {}}
    for name in names:
        (kept, dropped, relieved, consumed, kinematics, half, relief, cleanup
         ) = build_variant_stage(name)
        checks = _rotor_checks(kept)
        data = {"half_spacing_mm": round(half, 4),
                "ball_d_mm": round(2.0 * F.BALL_R, 3), "nip_mm": SH.VARIANTS[name]["nip"],
                "relief": relief, "cleanup": cleanup, "checks": checks,
                "queue": queue_report(F.BALL_R),
                "solid_counts": {n: len(s.Solids()) for n, s in kept.items()}}
        bad = [k for k, v in data["solid_counts"].items()
               if v != 1 and _is_our_part(k)]
        data["parts_not_single_solid"] = bad
        data["cots_multi_solid_parts"] = [k for k, v in data["solid_counts"].items()
                                          if v != 1 and not _is_our_part(k)]
        ok = (not checks["our_part_overlaps_mm3"] and not bad
              and data["queue"]["waiting_balls_all_clear"])
        data["status"] = "pass" if ok else "unresolved"
        out["variants"][name] = data
        print(json.dumps({name: {"status": data["status"],
                                 "capacity": data["queue"]["capacity_balls"],
                                 "waiting_balls_all_clear":
                                     data["queue"]["waiting_balls_all_clear"],
                                 "overlaps": checks["our_part_overlaps_mm3"],
                                 "multi_solid_parts": bad,
                                 "shaft_fit": checks["shaft_fit_mm3"]}},
                         indent=2, ensure_ascii=False), flush=True)
        if dry:
            del kept, dropped, relieved, consumed, kinematics
            continue
        instem = F.OUT / ("paddle_launcher_feeder_a_prime_shared_staging_%s" % name)
        assy = cq.Assembly(name=instem.name)
        colors = {"feeder_shell_tray": cq.Color(0.20, 0.56, 0.84, 0.55),
                  "gecko_flywheel_": cq.Color(0.055, 0.06, 0.07),
                  "paddle_flex_tip_": cq.Color(0.96, 0.72, 0.18),
                  "paddle_rotor": cq.Color(0.92, 0.54, 0.12)}
        for nm, shape in kept.items():
            col = cq.Color(0.58, 0.62, 0.68)
            for pre, c in colors.items():
                if nm.startswith(pre):
                    col = c
                    break
            assy.add(shape, name=nm, color=col)
        print("[stage %s] export -> %s.step" % (name, instem.name), flush=True)
        assy.export(str(instem.with_suffix(".step")), exportType="STEP")
        if want_stl:
            exporters.export(cq.Compound.makeCompound(list(kept.values())),
                             str(instem.with_suffix(".stl")), tolerance=0.5,
                             angularTolerance=0.3)
        del assy, kept, dropped, relieved, consumed, kinematics
    (F.OUT / "paddle_launcher_feeder_a_prime_shared_staging_report.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print("[stage] report written", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
