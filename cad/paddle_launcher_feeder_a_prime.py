"""a' variant (DEC-0028) of the T06 feeder redesign -- ball parks ON the carry circle.

Changes vs ``paddle_launcher_feeder_redesign.py`` (that file, the parent module
``paddle_launcher_constrained.py`` and the original STEP are all left untouched):

* the shell sector is extended from ``A_LIP = 225 deg`` to ``292 deg`` about the
  rotor axis, so the shell inner arc itself carries *past* the bottom of the
  carry circle (270 deg).  The wall becomes the ball's rest support and the ball
  centre sits on ``R_CARRY = 58.4 mm`` instead of 37.1 mm further out on a pad;
* the tray is shortened to ``TRAY_X0 = 56 mm`` -- the measured tangency point of
  the carry circle with the 5 deg tray surface -- so the tray no longer lifts
  the ball off the shell wall (formerly 1.1 mm of shell interference);
* nothing else moves: rotor axis, rotor geometry, shell end face at
  ``A_EXIT = 142 deg``, shell wall 7 mm, tray tilt 5 deg and the tray right end
  stay exactly as the v2 redesign had them.

Units: millimetres.  Chassis plane X-Y, +Z up, rotor/flywheel axes along Y.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import cadquery as cq
from cadquery import exporters

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import paddle_launcher_feeder_redesign as F  # noqa: E402

# ------------------------------------------------------- a' parameter override
F.A_LIP = 292.0          # was 225.0: shell now reaches past 270 deg
F.TRAY_X0 = 56.0         # was -56.0: tray stops at the carry-circle tangency


def _polar(r, angle):
    return (F.PADDLE_CX + r * math.cos(math.radians(angle)),
            F.PADDLE_CZ + r * math.sin(math.radians(angle)))


def feeder_shell_tray():
    """Shell annular sector (142..292 deg) fused with the shortened tray.

    Built as two solids and fused rather than as one closed profile, because the
    a' topology (tray ends mid-sector, at the tangency point) is not a simple
    single-loop polygon.
    """
    r_in = F.R_CARRY + F.BALL_R
    r_out = r_in + F.SHELL_WALL
    mid = 0.5 * (F.A_LIP + F.A_EXIT)
    lip_in, exit_in = _polar(r_in, F.A_LIP), _polar(r_in, F.A_EXIT)
    exit_out, lip_out = _polar(r_out, F.A_EXIT), _polar(r_out, F.A_LIP)
    mid_in, mid_out = _polar(r_in, mid), _polar(r_out, mid)

    wp = cq.Workplane("XZ").moveTo(*lip_in)
    wp = wp.threePointArc(mid_in, exit_in)          # inner wall = ball track
    wp = wp.lineTo(*exit_out)                       # exit end face
    wp = wp.threePointArc(mid_out, lip_out)         # outer wall
    wp = wp.close()
    shell = wp.extrude(F.FEEDER_W / 2.0, both=True).val()

    z_l = F._tray_top_z(F.TRAY_X0)
    z_r = F._tray_top_z(F.TRAY_X1)
    xm, zm = 0.5 * (F.TRAY_X0 + F.TRAY_X1), 0.5 * (z_l + z_r)
    ang = math.degrees(math.atan2(z_r - z_l, F.TRAY_X1 - F.TRAY_X0))
    length = math.hypot(F.TRAY_X1 - F.TRAY_X0, z_r - z_l)
    tray = cq.Solid.makeBox(length, F.FEEDER_W, F.TRAY_T,
                            cq.Vector(-length / 2.0, -F.FEEDER_W / 2.0, -F.TRAY_T / 2.0))
    tray = tray.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 1, 0), -ang)
    tray = tray.translate(cq.Vector(xm, 0.0, zm - F.TRAY_T / 2.0))
    return shell.fuse(tray).clean()


F.feeder_shell_tray = feeder_shell_tray          # F.build() picks this up


def main():
    kept, dropped, relieved, consumed, kinematics = F.build("pollen", 80.0)
    data = F.report(kept, dropped, relieved, consumed, kinematics)

    shell = kept["feeder_shell_tray"]
    nest = cq.Vector(F.PADDLE_CX, 0.0, F.PADDLE_CZ - F.R_CARRY)
    ball_nest = cq.Solid.makeSphere(F.BALL_R, nest)
    try:
        nest_clash = round(max(0.0, ball_nest.intersect(shell).Volume()), 4)
    except Exception:
        nest_clash = -1.0

    data["variant"] = "a' (DEC-0028) -- ball rests on the shell inner arc"
    data["shell_sector_deg"] = [F.A_EXIT, F.A_LIP]
    data["tray_x_range_mm"] = [F.TRAY_X0, F.TRAY_X1]
    data["rest_ball_centre_mm"] = [round(F.PADDLE_CX, 3),
                                   round(F.PADDLE_CZ - F.R_CARRY, 3)]
    data["rest_support"] = ("shell inner arc r_in=%.2f mm, sector %g..%g deg"
                            % (F.R_CARRY + F.BALL_R, F.A_EXIT, F.A_LIP))
    data["nest_ball_clash_with_shell_mm3"] = nest_clash
    data["tangency_of_tray_and_carry_circle_mm"] = round(F.TRAY_X0, 3)

    stem = F.OUT / "paddle_launcher_feeder_a_prime_pollen"
    assy = cq.Assembly(name="paddle_launcher_feeder_a_prime_pollen")
    colors = {
        "feeder_shell_tray": cq.Color(0.20, 0.56, 0.84, 0.55),
        "gecko_flywheel_": cq.Color(0.055, 0.06, 0.07),
        "paddle_flex_tip_": cq.Color(0.96, 0.72, 0.18),
        "paddle_arm_": cq.Color(0.92, 0.54, 0.12),
        "paddle_hub": cq.Color(0.72, 0.74, 0.78),
    }
    for name, shape in kept.items():
        col = cq.Color(0.58, 0.62, 0.68)
        for pre, c in colors.items():
            if name.startswith(pre):
                col = c
                break
        assy.add(shape, name=name, color=col)
    print("[a'] exporting STEP -> %s" % stem.with_suffix(".step").name, flush=True)
    assy.export(str(stem.with_suffix(".step")), exportType="STEP")
    exporters.export(cq.Compound.makeCompound(list(kept.values())),
                     str(stem.with_suffix(".stl")), tolerance=0.2, angularTolerance=0.15)
    (F.OUT / "paddle_launcher_feeder_a_prime_pollen_report.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
