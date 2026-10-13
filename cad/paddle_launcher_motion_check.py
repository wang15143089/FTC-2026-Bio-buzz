# -*- coding: utf-8 -*-
"""T06 motion-part geometry cross-check + desktop delivery.

Baseline sources (see cad/output/_motion_check/motion_check_report.md):
  R37 staging  DEC-0035 / DEC-0036  tray right end 215, one-piece paddle rotor,
                                    hot-diameter shaft spacing
  R39 liner    DEC-0039             printing variant (shell/tray pre-shrunk 0.5)
  R47 tape     DEC-0044             low-friction tape on shell inner arc 135-258
                                    and on the tray top face
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path

import cadquery as cq
from cadquery import exporters

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import paddle_launcher_feeder_a_prime_shared as SH
import paddle_launcher_feeder_a_prime_shared_staging as ST
import paddle_launcher_feeder_a_prime_liner as LI

F, pl = SH.F, SH.pl

DESKTOP = Path(os.path.expanduser("~")) / "OneDrive" / "Desktop"
OUT = F.OUT.parent / "_motion_check"
OUT.mkdir(parents=True, exist_ok=True)

TAPE_A0, TAPE_A1 = 135.0, 258.0
TAPE_W, TAPE_T = 88.0, 0.5


def _polar(r, ang):
    return (F.PADDLE_CX + r * math.cos(math.radians(ang)),
            F.PADDLE_CZ + r * math.sin(math.radians(ang)))


def tape_arc_declared():
    r_in, r_out = SH.R_IN, SH.R_IN + TAPE_T
    a_lo, a_hi = TAPE_A1, TAPE_A0
    a_mid = 0.5 * (TAPE_A0 + TAPE_A1)
    wp = cq.Workplane("XZ").moveTo(*_polar(r_in, a_lo))
    wp = wp.threePointArc(_polar(r_in, a_mid), _polar(r_in, a_hi))
    wp = wp.lineTo(*_polar(r_out, a_hi))
    wp = wp.threePointArc(_polar(r_out, a_mid), _polar(r_out, a_lo))
    return wp.close().extrude(TAPE_W / 2.0, both=True).val()


def dump(parts):
    rows = []
    for n, s in parts.items():
        bb = s.BoundingBox()
        c = s.Center()
        rows.append({
            "part": n,
            "n_solids": len(s.Solids()),
            "volume_mm3": round(s.Volume(), 2),
            "bbox_mm": [round(v, 3) for v in (bb.xmin, bb.ymin, bb.zmin,
                                              bb.xmax, bb.ymax, bb.zmax)],
            "centre_mm": [round(v, 3) for v in (c.x, c.y, c.z)],
        })
    return rows


COLORS = (("liner_tape", cq.Color(0.90, 0.10, 0.10, 1.0)),
          ("feeder_shell_tray", cq.Color(0.20, 0.56, 0.84, 0.60)),
          ("gecko_flywheel_", cq.Color(0.05, 0.06, 0.07, 1.0)),
          ("paddle_flex_tip_", cq.Color(0.96, 0.72, 0.18, 1.0)),
          ("paddle_rotor", cq.Color(0.92, 0.54, 0.12, 1.0)))


def colour_of(name):
    for pre, col in COLORS:
        if name.startswith(pre):
            return col
    return cq.Color(0.58, 0.62, 0.68, 1.0)


def run(name):
    t0 = time.time()
    (kept, dropped, relieved, consumed, kinematics, half,
     relief, cleanup) = ST.build_variant_stage(name)
    print("[check %s] CAD build %.1f s, parts=%d" % (name, time.time() - t0, len(kept)),
          flush=True)
    parts = dict(kept)
    parts["liner_tape_arc"] = tape_arc_declared()
    parts["liner_tape_tray"] = LI.tray_tape()

    stem = "T06_motion_%s" % name
    assy = cq.Assembly(name=stem)
    for n, s in parts.items():
        assy.add(s, name=n, color=colour_of(n))
    dst = DESKTOP / (stem + ".step")
    t1 = time.time()
    assy.export(str(dst), exportType="STEP")
    assy.export(str(OUT / (stem + ".step")), exportType="STEP")
    print("[check %s] export %.1f s -> %s" % (name, time.time() - t1, dst), flush=True)

    data = {
        "variant": name,
        "half_spacing_mm": round(half, 4),
        "ball_r_mm": round(F.BALL_R, 4),
        "nip_mm": SH.VARIANTS[name]["nip"],
        "paddle_axis_mm": [F.PADDLE_CX, 0.0, F.PADDLE_CZ],
        "shell_inner_r_mm": SH.R_IN,
        "shell_outer_r_mm": SH.R_IN + F.SHELL_WALL,
        "shell_sector_deg": [F.A_EXIT, F.A_LIP],
        "feeder_width_mm": F.FEEDER_W,
        "tray_x_range_mm": [round(F.TRAY_X0, 3), round(F.TRAY_X1, 3)],
        "tray_tilt_deg": F.TILT_DEG,
        "blade_phase_deg": list(SH.BLADE_PHASE),
        "tape_sector_deg": [TAPE_A0, TAPE_A1],
        "delivered_step": str(dst),
        "parts": dump(parts),
        "kinematics_keys": sorted(list(kinematics.keys())) if hasattr(
            kinematics, "keys") else str(type(kinematics)),
        "kinematics": kinematics if isinstance(kinematics, dict) else None,
        "dropped": list(dropped) if dropped is not None else None,
    }
    (OUT / ("parts_%s.json" % name)).write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    del assy, kept, parts
    return data


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    names = [a for a in argv if not a.startswith("-")] or ["pollen", "nectar"]
    for name in names:
        d = run(name)
        for r in d["parts"]:
            print("  %-34s solids=%d  vol=%10.1f  bbox=%s"
                  % (r["part"], r["n_solids"], r["volume_mm3"], r["bbox_mm"]), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())