# -*- coding: utf-8 -*-
"""T06 R53f -- R53b + 定长限位环：把锁紧件预载从「靠手感」变成「靠几何」。

用户判据（2026-10-13）：保留调隙舵机 + 加锁紧件，且锁紧件**不得影响正常位置改变**。

R53b 的弹簧预载 = k x (自由长 - 装好长)，而「装好长」由操作者拧尼龙锁紧螺母决定。
拧过头（或换个人装）预载就变大，摩擦力按比例涨；R53g 量到 mu = 0.60 时预载涨到
12 N 就把 25-2 顶停 —— 那正好违反用户判据。R53f 只加一个件消掉这条路径：

  * 每根 M4 螺柱上、耳板外面套一个 **Ø8.0 / Ø5.7 x 6.0 的刚性限位环**（套在弹簧外面）；
  * 弹簧（Ø5.5 外 / 自由 8.4）在环内，被压到 6.0 mm => 预载 1.24 x 2.4 = 2.98 N；
  * 螺母把平垫压到**限位环端面**上就到底了：再拧只压环（刚性），**预载不再增长**；
  * 唯一失效方向是螺母松脱（掉预载、掉夹紧），不伤换档 => 尼龙锁紧螺母 + 螺纹胶 243。

为什么不是「套在螺柱上的细套筒」：M4 螺柱 Ø4.0 与弹簧内径 Ø4.5 之间只有 0.25 mm
径向间隙，套筒壁厚最多 0.25 mm（截面 1.38 mm2，PET 压缩屈服约 50 MPa => 只能扛
约 69 N），手拧很容易压溃；改成套在弹簧**外面**的环，截面 24.8 mm2（约 1.24 kN），
同样的 6.0 mm 定长，且限位环就是一根 Ø8 x Ø6 管切 6 mm（成品件也能买）。
限位环占用的径向空间到半径 4.0，平垫半径 5.0，仍完整压住环端面。

Run:  .venv-cad/Scripts/python.exe -X utf8 cad/paddle_launcher_shooter_lock_r53f.py pollen nectar --step
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import time
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import paddle_launcher_constrained as K                      # noqa: E402
import paddle_launcher_shooter_lock_r53b as B                 # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = HERE / "output" / "_r53f_lock"
OUT.mkdir(parents=True, exist_ok=True)
B.OUT = OUT                       # keep the R53b evidence directory untouched
DESKTOP = Path(os.path.expanduser("~")) / "OneDrive" / "Desktop"

_ORIG_CLAMP = B.clamp_parts       # capture before patching
_ORIG_BUILD = B.build
CAPTURED = {}

SEAT_OD_R = 4.00                  # O8.0 outer  (washer R5.0 still presses the whole face)
SEAT_BORE_R = 2.85                # O5.7 bore   (clears the O5.5 spring by 0.1 mm)
SEAT_L = B.SPRING_INSTALLED       # 6.0 mm -- the spring cannot be compressed further


def clamp_parts_with_seat(half_spacing):
    out = dict(_ORIG_CLAMP(half_spacing))
    ear_outer = B.PLATE_HALF_T + B.EAR_GAP + B.EAR_T          # 5.3
    for label, sign in (("upper", 1), ("lower", -1)):
        n = sign * half_spacing
        for side in (-1, 1):
            y = side * B.PLATE_Y
            cy = y + side * (ear_outer + SEAT_L / 2.0)
            for u in (-B.CLAMP_U, B.CLAMP_U):
                for dz in (-B.CLAMP_Z, B.CLAMP_Z):
                    z = n + dz
                    ring = K.cyl_y(SEAT_OD_R, SEAT_L, (u, cy, z))
                    ring = ring.cut(K.cyl_y(SEAT_BORE_R, SEAT_L + 2.0, (u, cy, z)))
                    out["carriage_clamp_seat_%s_%+d_%+.0f_%+.0f" % (label, side, u, dz)] = \
                        K.to_world(ring)
    return out


def build_capture(name, half):
    res = _ORIG_BUILD(name, half)
    CAPTURED["parts"] = res[0]
    return res


B.clamp_parts = clamp_parts_with_seat
B.build = build_capture


def run(name, export=False):
    t0 = time.time()
    meta = B.run(name, export=False)
    deps = OUT / ("report_r53b_%s.json" % name)
    if deps.exists():
        deps.replace(OUT / ("report_r53f_deps_r53b_module_%s.json" % name))
    seats = sorted(r["part"] for r in meta["parts"] if "clamp_seat" in r["part"])
    preload = B.SPRING_RATE * (B.SPRING_FREE - SEAT_L)
    seat_area = 3.141592653589793 * (SEAT_OD_R ** 2 - SEAT_BORE_R ** 2)
    meta["caliber"] = "T06 R53f = R53b + rigid length stop ring (preload set by geometry)"
    meta["changes_vs_r53b"] = meta["changes_vs_r52"] + [
        "%d rigid length stop rings O%.1f/O%.1f x %.1f mm, one per stud, around the spring"
        % (len(seats), 2.0 * SEAT_OD_R, 2.0 * SEAT_BORE_R, SEAT_L),
        "preload is now k x (free - ring) = %.2f N per stud, whatever torque the nut sees"
        % preload,
        "ring wall 1.15 mm / section %.1f mm2 (~1.2 kN in PET) => a thin sleeve inside the "
        "spring (0.25 mm wall, ~69 N) was rejected" % seat_area,
        "off-the-shelf equivalent: 6.0 mm slice of an O8 x O6 nylon/PU tube",
    ]
    meta["seat"] = {
        "count_per_variant": len(seats), "od_mm": 2.0 * SEAT_OD_R,
        "bore_mm": 2.0 * SEAT_BORE_R, "length_mm": SEAT_L,
        "section_mm2": round(seat_area, 2),
        "preload_n_per_stud_geometric": round(preload, 3),
        "print_tolerance_effect_n": round(B.SPRING_RATE * 0.2, 3),
        "why": "平垫压到限位环端面就到底（6.0 mm）；再拧只压环，预载不再增长。"
               "反向失效是螺母松脱（掉预载、掉夹紧），不伤换档 => 尼龙锁紧螺母 + 螺纹胶 243。"
               "3D 打印 +/-0.2 mm 直接换算成 +/-0.25 N（名义 2.98 N）。",
        "parts": seats,
    }
    clamp = B.clamp_calc()
    clamp["preload_n_per_stud"] = round(preload, 3)
    clamp["preload_source"] = ("geometric: SPRING_RATE x (SPRING_FREE - ring length); "
                              "the build-time nut torque no longer sets it")
    for mu in (0.30, 0.60):
        f_car = mu * 2.0 * 8 * preload
        clamp["mu_%.2f" % mu] = {
            "friction_per_carriage_n": round(f_car, 1),
            "friction_total_n": round(2.0 * f_car, 1),
            "servo_can_still_slide_it": bool(2.0 * f_car < 0.6 * 112.0),
        }
    meta["clamp_calc"] = clamp
    (OUT / ("report_r53f_%s.json" % name)).write_text(
        json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")

    print("[r53f %s] parts %d (seats %d)" % (name, meta["n_parts"], len(seats)), flush=True)
    print("[r53f %s] ear-plate min gap %s"
          % (name, json.dumps(meta["ear_to_plate_min_gap_mm"])), flush=True)
    print("[r53f %s] lock_travel %s" % (name, json.dumps(meta["lock_travel"])), flush=True)
    print("[r53f %s] lock vs rest %d / vs carriage %d / axle hits %d"
          % (name, len(meta["lock_vs_rest_clashes"]), len(meta["lock_vs_carriage_clashes"]),
             len(meta["axle_isolation_hits"])), flush=True)
    for h in meta["lock_vs_rest_clashes"]:
        print("   !", json.dumps(h, ensure_ascii=False), flush=True)
    for h in meta["lock_vs_carriage_clashes"]:
        print("   ~", json.dumps(h, ensure_ascii=False), flush=True)

    if export:
        stem = "T06_shooter_assembly_R53f_%s" % name
        assy = cq.Assembly(name=stem)
        for n, s in CAPTURED["parts"].items():
            assy.add(s, name=n, color=cq.Color(0.72, 0.74, 0.78, 1.0))
        dst = OUT / (stem + ".step")
        assy.export(str(dst), exportType="STEP")
        meta["step_mb"] = round(dst.stat().st_size / 1e6, 1)
        desk = DESKTOP / (stem + ".step")
        try:
            if desk.exists():
                desk.unlink()
            os.link(dst, desk)
        except Exception:
            shutil.copyfile(dst, desk)
        (OUT / ("report_r53f_%s.json" % name)).write_text(
            json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")
        print("[r53f %s] STEP -> %.1f MB" % (name, meta["step_mb"]), flush=True)

    print("[r53f %s] done in %.1f s" % (name, time.time() - t0), flush=True)
    return meta


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    names = [a for a in argv if not a.startswith("-")] or ["pollen"]
    for n in names:
        run(n, export="--step" in argv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
