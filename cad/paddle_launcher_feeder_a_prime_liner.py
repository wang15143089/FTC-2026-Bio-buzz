# -*- coding: utf-8 -*-
"""R39 / DEC-0039：T06 送球道低摩擦内衬（PTFE 带 0.5 mm）。

根因（SIMULATED，V-0039）：送球节拍瓶颈不在拨杆形状，而在**球与球道内表面
（外罩内弧 + 托板顶面）的滑动摩擦**。R38 口径下（球 mu = 0.60）球被夹在托板与
叶片之间、外罩弧面法向力 5-6.5 N x 2-3 处，驱动扭矩全程 0.53 N.m 削平，
单球 11.6 s 才送达；把这两处有效 mu 降到 0.05-0.10 后单球 0.16 s、全流程
清空 41.3 -> 4.0 s（6/6 全清、24/24 真出膛、卡滞 69% -> 4%）。

本模块把该方案落成可制造几何（**不覆盖任何原文件**）：
  1) 打印件按内衬厚度**预缩**：外罩内弧打印半径 R_IN + 0.5（外径不变，
     壁厚 7.0 -> 6.5）；托板顶面下沉 0.5（底面不动，厚度 6.0 -> 5.5）。
     贴 0.5 mm PTFE 带后，球看到的有效表面 = 原设计表面 ⇒ 仿真所用的
     球道几何原样保留，轨迹不变。
  2) 生成 PTFE 带下料实体（球道弧带 + 托板带），导出 STEP 供裁带用。

用法: python cad/paddle_launcher_feeder_a_prime_liner.py [nectar] [pollen]
产物: cad/output/_r39_liner/
"""
from __future__ import annotations

import json
import math
import struct
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import cadquery as cq
import numpy as np
from cadquery import exporters

import paddle_launcher_feeder_a_prime_shared as SH
import paddle_launcher_feeder_a_prime_shared_staging as ST

T_LINER = 0.5        # PTFE 带厚度 (mm)
TAPE_W = 88.0        # 带宽度；球接触带宽 <= 球径 91.9，取 88 覆盖两种球
OUT_DIR = SH.F.OUT.parent / "_r39_liner"
OUT_DIR.mkdir(parents=True, exist_ok=True)

F = SH.F
pl = SH.pl


def _polar(r, ang):
    return (F.PADDLE_CX + r * math.cos(math.radians(ang)),
            F.PADDLE_CZ + r * math.sin(math.radians(ang)))


def arc_tape():
    """球道弧内衬：设计内弧 R_IN 与打印弧面 R_IN+0.5 之间的 0.5 mm 带。"""
    r_in = SH.R_IN                 # 贴带后的有效（设计）内弧
    r_out = SH.R_IN + T_LINER      # 打印内弧
    mid = 0.5 * (F.A_LIP + F.A_EXIT)
    lip_in, exit_in = _polar(r_in, F.A_LIP), _polar(r_in, F.A_EXIT)
    exit_out, lip_out = _polar(r_out, F.A_EXIT), _polar(r_out, F.A_LIP)
    mid_in, mid_out = _polar(r_in, mid), _polar(r_out, mid)
    wp = cq.Workplane("XZ").moveTo(*lip_in)
    wp = wp.threePointArc(mid_in, exit_in)
    wp = wp.lineTo(*exit_out)
    wp = wp.threePointArc(mid_out, lip_out)
    return wp.close().extrude(TAPE_W / 2.0, both=True).val()


def tray_tape():
    """托板面内衬：贴在预缩后的托板顶面上，上表面 = 设计托板面。"""
    z_l = F._tray_top_z(F.TRAY_X0)
    z_r = F._tray_top_z(F.TRAY_X1)
    xm, zm = 0.5 * (F.TRAY_X0 + F.TRAY_X1), 0.5 * (z_l + z_r)
    ang = math.degrees(math.atan2(z_r - z_l, F.TRAY_X1 - F.TRAY_X0))
    length = math.hypot(F.TRAY_X1 - F.TRAY_X0, z_r - z_l)
    tape = cq.Solid.makeBox(length, TAPE_W, T_LINER,
                            cq.Vector(-length / 2.0, -TAPE_W / 2.0, -T_LINER / 2.0))
    tape = tape.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 1, 0), -ang)
    return tape.translate(cq.Vector(xm, 0.0, zm + T_LINER / 2.0))


def build_shrunk(name):
    """按内衬厚度预缩后的打印件（外罩 + 托板）。"""
    v = SH.VARIANTS[name]
    ball_r, nip = v["ball_r"], v["nip"]
    half = nip / 2.0 + pl.WHEEL_OD / 2.0 + ST.DR_HOT_MM
    keep = {k: getattr(F, k) for k in
            ("R_CARRY", "SHELL_WALL", "TRAY_T", "PIVOT_Z", "BALL_D", "BALL_R")}
    F.BALL_D, F.BALL_R = 2.0 * ball_r, ball_r
    F.R_CARRY = (SH.R_IN - ball_r) + T_LINER      # 打印内弧 = R_IN + 0.5
    F.SHELL_WALL = keep["SHELL_WALL"] - T_LINER   # 外径不变
    F.TRAY_T = keep["TRAY_T"] - T_LINER           # 托板底面不动，顶面降 0.5
    F.PIVOT_Z = keep["PIVOT_Z"] - T_LINER         # 托板面整体降 0.5
    t0 = time.time()
    kept, dropped, relieved, consumed, kinematics = F.build(name, half)
    SH._relieve_shell(kept)
    ST._cleanup(kept)
    z0 = F._tray_top_z(F.TRAY_X0) - T_LINER
    z1 = F._tray_top_z(F.TRAY_X1) - T_LINER
    for k, x in keep.items():
        setattr(F, k, x)
    print("[liner %s] %.1f s  printed R_in=%.3f  printed tray top z(x0)=%.3f/z(x1)=%.3f"
          % (name, time.time() - t0, SH.R_IN + T_LINER, z0, z1),
          flush=True)
    return kept, ball_r, nip


# ---------------------------------------------------------------- 独立量具
# 不能拿 OCC 的 ``Shape.distance`` 当量具：对"大球 vs 旋转外罩"这一对，它给出
# 的净距与实体本身矛盾（270 deg 处实测 31.29 mm，而同一实体自上而下的射线与
# 网格回读都指向 108.47/114.95 的内外弧），可信度不足。这里改用**导出细网格
# STL + numpy 射线求交**，量具与造型器解耦，量的是交付几何本身。


def _load_stl(path):
    raw = path.read_bytes()
    if raw[:5] == b"solid":
        vals = []
        for token in raw.decode("ascii", "ignore").split():
            try:
                vals.append(float(token))
            except ValueError:
                continue
        pts = np.asarray(vals, dtype=float).reshape(-1, 9)
        return pts[:, [0, 1, 2, 3, 4, 5, 6, 7, 8]].reshape(-1, 3, 3)
    count = struct.unpack_from("<I", raw, 80)[0]
    block = np.frombuffer(raw, dtype=np.uint8, count=count * 50, offset=84)
    return block.reshape(count, 50)[:, 12:48].copy().view("<f4").reshape(count, 3, 3).astype(float)


def _ray_hits(origin, direction, triangles):
    v0, v1, v2 = triangles[:, 0], triangles[:, 1], triangles[:, 2]
    e1, e2 = v1 - v0, v2 - v0
    pvec = np.cross(direction, e2)
    det = np.einsum("ij,ij->i", e1, pvec)
    ok = np.abs(det) > 1e-12
    inv = np.zeros_like(det)
    inv[ok] = 1.0 / det[ok]
    tvec = origin - v0
    u = np.einsum("ij,ij->i", tvec, pvec) * inv
    qvec = np.cross(tvec, e1)
    v = np.einsum("j,ij->i", direction, qvec) * inv
    hit = ok & (u >= 0.0) & (v >= 0.0) & (u + v <= 1.0)
    dist = np.einsum("ij,ij->i", e2, qvec) * inv
    return dist[hit & (dist > 1e-9)]


def measure_wall(shell, name, ball_r):
    """量出打印件与"设计球道面"的偏差：内弧 +0.5、外弧 0、托板面 -0.5。"""
    mesh = OUT_DIR / ("_measure_%s.stl" % name)
    exporters.export(cq.Compound.makeCompound([shell]), str(mesh),
                     tolerance=0.01, angularTolerance=0.05)
    triangles = _load_stl(mesh)
    origin = np.array([F.PADDLE_CX, 0.0, F.PADDLE_CZ])
    spans = {}
    for ang in np.arange(130.0, 291.0, 1.0):
        a = math.radians(float(ang))
        hits = np.sort(_ray_hits(origin, np.array([math.cos(a), 0.0, math.sin(a)]), triangles))
        hits = hits[hits > 1e-6]
        if len(hits) >= 2:
            spans[float(ang)] = (float(hits[0]), float(hits[-1]))
    arc = {a: s for a, s in spans.items() if F.A_EXIT <= a <= F.A_LIP}
    inner = [s[0] for s in arc.values()]
    outer = [s[1] for s in arc.values()]
    tray = []
    for x in np.arange(F.TRAY_X0 + 5.0, F.TRAY_X1 - 5.0, 15.0):
        z_ref = F._tray_top_z(float(x))
        hits = _ray_hits(np.array([float(x), 0.0, 320.0]), np.array([0.0, 0.0, -1.0]), triangles)
        if len(hits) == 0:
            continue
        zs = 320.0 - hits
        tray.append(float(zs[np.argmin(np.abs(zs - z_ref))]) - z_ref)
    return {
        "instrument": "mesh ray-casting on the exported STL (tolerance 0.01 mm)",
        "mesh_file": str(mesh.relative_to(HERE.parent)).replace("\\", "/"),
        "mesh_triangles": int(len(triangles)),
        "inner_arc_min_mm": round(min(inner), 4),
        "inner_arc_max_mm": round(max(inner), 4),
        "outer_arc_min_mm": round(min(outer), 4),
        "outer_arc_max_mm": round(max(outer), 4),
        "inner_arc_offset_mm": round(min(inner) - SH.R_IN, 4),
        "outer_arc_offset_mm": round(max(outer) - (SH.R_IN + F.SHELL_WALL), 4),
        "tray_top_offset_mm": round(float(np.mean(tray)), 4) if tray else None,
        "tray_top_offset_max_abs_mm": round(max(abs(t) for t in tray), 4) if tray else None,
        "sector_deg": [round(min(arc), 1), round(max(arc), 1)],
        "ball_clearance_min_mm": round(min(inner) - SH.R_IN, 4),
        "ball_r_mm": round(ball_r, 3),
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    names = [a for a in argv if not a.startswith("-")] or ["nectar", "pollen"]
    report = {"units": "mm", "round": "R39 / DEC-0039 送球道低摩擦内衬",
              "liner_thickness_mm": T_LINER, "tape_width_mm": TAPE_W,
              "design_shell_inner_r_mm": SH.R_IN,
              "printed_shell_inner_r_mm": SH.R_IN + T_LINER,
              "printed_shell_wall_mm": 7.0 - T_LINER,
              "printed_tray_thickness_mm": 6.0 - T_LINER,
              "liner_mu_assumed": [0.05, 0.10],
              "variants": {}}

    tape_arc = arc_tape()
    tape_tray = tray_tape()
    dash = math.radians(F.A_LIP - F.A_EXIT)
    tape = {"arc_developed_length_mm": round(SH.R_IN * dash, 2),
            "arc_sector_deg": [F.A_EXIT, F.A_LIP],
            "arc_width_mm": TAPE_W,
            "tray_length_mm": round(math.hypot(F.TRAY_X1 - F.TRAY_X0,
                                               F._tray_top_z(F.TRAY_X1) - F._tray_top_z(F.TRAY_X0)), 2),
            "tray_x_range_mm": [round(F.TRAY_X0, 3), round(F.TRAY_X1, 3)],
            "tray_width_mm": TAPE_W,
            "tape_volume_mm3": round(tape_arc.Volume() + tape_tray.Volume(), 2)}
    report["tape"] = tape
    print("[liner] tape arc 开发长度 %.1f mm，托板带长 %.1f mm，宽 %.0f mm"
          % (tape["arc_developed_length_mm"], tape["tray_length_mm"], TAPE_W), flush=True)
    exporters.export(cq.Compound.makeCompound([tape_arc]),
                     str(OUT_DIR / "liner_tape_arc.step"))
    exporters.export(cq.Compound.makeCompound([tape_tray]),
                     str(OUT_DIR / "liner_tape_tray.step"))

    for name in names:
        kept, ball_r, nip = build_shrunk(name)
        shell = kept["feeder_shell_tray"]
        part = OUT_DIR / ("feeder_shell_tray_liner_%s.step" % name)
        exporters.export(cq.Compound.makeCompound([shell]), str(part))
        exporters.export(cq.Compound.makeCompound([shell]),
                         str(part.with_suffix(".stl")), tolerance=0.05,
                         angularTolerance=0.2)
        # --- 关键尺寸实测：量交付给打印机的那个实体
        wall = measure_wall(shell, name, ball_r)
        report["variants"][name] = {
            "ball_r_mm": round(ball_r, 3), "nip_mm": nip,
            "printed_solid_count": len(shell.Solids()),
            "printed_volume_mm3": round(shell.Volume(), 2),
            **wall,
            "step": str(part.relative_to(HERE.parent)).replace("\\", "/"),
        }
        print("[liner %s] 实体 %d，体积 %.1f mm3" % (name, len(shell.Solids()), shell.Volume()))
        print("   内弧 %.3f..%.3f mm（设计 %.3f，偏移 %+.3f）  外弧 %.3f mm（设计 %.3f，偏移 %+.3f）"
              % (wall["inner_arc_min_mm"], wall["inner_arc_max_mm"], SH.R_IN,
                 wall["inner_arc_offset_mm"], wall["outer_arc_max_mm"],
                 SH.R_IN + F.SHELL_WALL, wall["outer_arc_offset_mm"]))
        print("   托板面偏移 %+.3f mm（最大 %.3f）  扇区 %s  球面净距 %.3f mm  三角形 %d"
              % (wall["tray_top_offset_mm"], wall["tray_top_offset_max_abs_mm"],
                 wall["sector_deg"], wall["ball_clearance_min_mm"], wall["mesh_triangles"]),
              flush=True)

    (OUT_DIR / "r39_liner_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("[liner] report -> %s" % (OUT_DIR / "r39_liner_report.json"), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
