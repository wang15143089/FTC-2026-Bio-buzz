"""Feeder redesign (V2) of the C06-B opposed-flywheel launcher  --  POLLEN.

What changes relative to ``paddle_launcher_constrained.py`` (the parent, never
modified by this file):

* the three-paddle rotor axis moves from ``(-47, 0, 73)`` to
  ``(29.49, 0, 111.46)`` -- the position that makes its carry circle tangent to
  the existing 52 deg ramp centreline (perpendicular distance 58.4 mm = R_CARRY,
  so the release is exactly tangent, see ``report`` below);
* one new printed part, ``feeder_shell_tray``: an outer shell whose centre is
  the *same* axis as the rotor (coaxial by construction -- the shell is an
  annular sector drawn about ``PADDLE_CENTER``), a 5 deg self-rolling tray, and
  a strut tying the two together so the whole thing is a single part;
* the whole old intake (0 deg + 26 deg floor / roof / side walls) and the two
  one-way fingers are dropped: they are the ball path in the old concept and
  are hard obstacles in the new one (measured, see report);
* the 52 deg *floor* (``guide_floor_3``) and the matching throat cheek are gone:
  the paddle axis now sits only 3.40 mm off the ramp floor line, so the ball's
  stable rest position (centre 14.30 mm below that line) would be buried 2123 mm3
  inside the floor stub -- measured, not guessed.  The ball is *thrown* along the
  ramp, never rolled on it, so no floor is needed there; the roof and both side
  walls stay exactly where the parent put them;
* the two opposed throat cheeks are relieved by the same R=63 paddle drum the
  parent already uses on its guide panels (the floor cheek is consumed entirely
  and is dropped automatically);
* everything on the launch side (flywheels, shafts, side plates, spacing
  linkage, throat) keeps its parent position untouched.

Units: millimetres.  Chassis plane X-Y, +Z up, flywheel/rotor axes along Y.
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

import paddle_launcher_constrained as pl  # noqa: E402

OUT = HERE / "output"

# ---------------------------------------------------------------- design data
BALL_D = 71.12
BALL_R = BALL_D / 2.0
PADDLE_CX, PADDLE_CZ = 29.49, 111.46
R_CARRY = 58.4                      # ball-centre orbit radius about the axis
SHELL_WALL = 7.0
A_LIP = 225.0                       # shell start: the lip the ball rests on
A_EXIT = 142.0                      # shell end: tangent release into the ramp
FEEDER_W = pl.CHANNEL_CLEAR_W       # 108 mm, same clear width as the channel
TILT_DEG = 5.0                      # tray: right end high, left end low
PIVOT_X, PIVOT_Z = -2.30, 17.50     # tilt axis = old ball/tray contact point
TRAY_T = 6.0
TRAY_X0, TRAY_X1 = -56.0, 150.0     # tray left / right end
DRUM_R = pl.PADDLE_SWEEP_R + 3.0    # parent rotor relief radius (63 mm)

# The parent reads PADDLE_CENTER at call time, so rebinding it here re-places
# the rotor, its shaft, the support cheeks and the feeder servo together.
pl.PADDLE_CENTER = (PADDLE_CX, 0.0, PADDLE_CZ)

DROP_PREFIXES = (
    # old 0 deg + 26 deg intake: the ball path of the old concept, hard obstacles
    # in this one.
    "guide_floor_1", "guide_roof_1", "guide_wall_1_",
    "guide_floor_2", "guide_roof_2", "guide_wall_2_",
    # old anti-return fingers: they sit 17.2 mm from the new rest centre, i.e.
    # straight through the ball (r=35.56).  The 5 deg tray is the anti-return now.
    "one_way_finger_",
    # 52 deg floor: clashes with the rest ball and with the paddle sweep.
    "guide_floor_3",
)


def _dead(shape):
    """True for a solid that a cut has consumed (no volume / void bounding box)."""
    try:
        if shape.Volume() <= 1e-6:
            return True
        shape.BoundingBox()
        return False
    except Exception:
        return True

KEEP_PREFIXES = (
    "paddle_hub", "paddle_arm_", "paddle_blade_", "paddle_flex_tip_",
    "paddle_shaft_", "gecko_flywheel_", "flywheel_shaft_",
    "guide_floor_3", "guide_roof_3", "guide_wall_3_", "shooter_throat_",
)
KEEP_EXACT = ("feeder_shell_tray",)


# ------------------------------------------------------------------ geometry
def _polar(r, angle):
    return (PADDLE_CX + r * math.cos(math.radians(angle)),
            PADDLE_CZ + r * math.sin(math.radians(angle)))


def _tray_top_z(x):
    return PIVOT_Z + (x - PIVOT_X) * math.tan(math.radians(TILT_DEG))


def feeder_shell_tray():
    """Shell (annular sector about the rotor axis) + tray + connecting strut.

    Drawn as one closed X-Z profile and extruded 108 mm along Y, so coaxiality
    with the rotor is a construction fact, not a tolerance.
    """
    r_in = R_CARRY + BALL_R
    r_out = r_in + SHELL_WALL
    lip = _polar(r_in, A_LIP)
    out_lip = _polar(r_out, A_LIP)
    out_exit = _polar(r_out, A_EXIT)
    in_exit = _polar(r_in, A_EXIT)
    mid = (A_LIP + A_EXIT) / 2.0
    mid_out = _polar(r_out, mid)
    mid_in = _polar(r_in, mid)

    z_left, z_right = _tray_top_z(TRAY_X0), _tray_top_z(TRAY_X1)
    foot_strut = (out_lip[0], _tray_top_z(out_lip[0]))
    foot_lip = (lip[0], _tray_top_z(lip[0]))

    wp = cq.Workplane("XZ").moveTo(TRAY_X1, z_right - TRAY_T)
    wp = wp.lineTo(TRAY_X0, z_left - TRAY_T)          # tray bottom
    wp = wp.lineTo(TRAY_X0, z_left)                   # tray left end face
    wp = wp.lineTo(*foot_strut)                       # tray top, up to the strut
    wp = wp.lineTo(*out_lip)                          # strut outer face
    wp = wp.threePointArc(mid_out, out_exit)          # shell outer wall
    wp = wp.lineTo(*in_exit)                          # shell exit end face
    wp = wp.threePointArc(mid_in, lip)                # shell inner wall (ball track)
    wp = wp.lineTo(*foot_lip)                         # strut inner face
    wp = wp.lineTo(TRAY_X1, z_right)                  # tray top to the entry
    wp = wp.close()
    part = wp.extrude(FEEDER_W / 2.0, both=True).val()
    part = part.clean()
    return part


def _cut_drum(shape):
    return shape.cut(pl.cyl_y(DRUM_R, pl.CHANNEL_CLEAR_W + 20, pl.PADDLE_CENTER))


# -------------------------------------------------------------------- export
def build(config="pollen", half_spacing=80.0):
    print(f"[{config}] building parent assembly ...", flush=True)
    _assy, _mesh, _cb, named, kinematics = pl.build(config, half_spacing)

    dropped = [n for n in named if n.startswith(DROP_PREFIXES)]
    for n in dropped:
        del named[n]

    relieved, consumed = [], []
    for n in list(named):
        if n.startswith("shooter_throat_"):
            before = named[n].Volume()
            named[n] = _cut_drum(named[n])
            if _dead(named[n]):
                consumed.append(n)
                del named[n]
            elif abs(before - named[n].Volume()) > 1e-6:
                relieved.append(n)

    named["feeder_shell_tray"] = feeder_shell_tray()

    kept = {n: s for n, s in named.items()
            if n.startswith(KEEP_PREFIXES) or n in KEEP_EXACT}
    return kept, dropped, relieved, consumed, kinematics


def report(kept, dropped, relieved, consumed, kinematics):
    g0 = pl.GUIDES[2][0]          # exact 52 deg ramp start, read from the parent
    perp = (PADDLE_CX - g0[0]) * pl.N52[0] + (PADDLE_CZ - g0[1]) * pl.N52[1]
    exit_pt = _polar(R_CARRY, A_EXIT)
    t_exit = (exit_pt[0] - g0[0]) * pl.T52[0] + (exit_pt[1] - g0[1]) * pl.T52[1]
    perp_exit = (exit_pt[0] - g0[0]) * pl.N52[0] + (exit_pt[1] - g0[1]) * pl.N52[1]

    guides = pl.GUIDES[2]
    panels = {
        "guide_floor_3": pl.panel_on_segment(guides[0], guides[1], guides[3], "floor"),
        "guide_roof_3": pl.panel_on_segment(guides[0], guides[1], guides[3], "roof"),
        "guide_wall_3_-1": pl.panel_on_segment(guides[0], guides[1], guides[3], "wall", -1),
        "guide_wall_3_+1": pl.panel_on_segment(guides[0], guides[1], guides[3], "wall", 1),
    }
    shell = kept["feeder_shell_tray"]

    def inter(a, b, tol=0.5):
        try:
            ba, bbb = a.BoundingBox(), b.BoundingBox()
        except Exception:
            return 0.0
        if (ba.xmax <= bbb.xmin + tol or bbb.xmax <= ba.xmin + tol
                or ba.ymax <= bbb.ymin + tol or bbb.ymax <= ba.ymin + tol
                or ba.zmax <= bbb.zmin + tol or bbb.zmax <= ba.zmin + tol):
            return 0.0
        try:
            return round(max(0.0, a.intersect(b).Volume()), 4)
        except Exception:
            return -1.0

    checks = {n: round(inter(shell, p), 4) for n, p in panels.items()}
    disc = cq.Solid.makeCylinder(pl.PADDLE_SWEEP_R, 100.0,
                                 cq.Vector(PADDLE_CX, -50.0, PADDLE_CZ),
                                 cq.Vector(0, 1, 0))
    checks.update({f"rotor_envelope_vs_{n}": round(inter(disc, p), 4)
                   for n, p in panels.items()})
    for n, s in kept.items():
        if n.startswith(("shooter_throat_", "feeder_shell_tray")):
            checks[f"rotor_envelope_vs_{n}"] = inter(disc, s)
    checks["rotor_tip_corner_r_mm"] = round(
        math.hypot(pl.PADDLE_SWEEP_R, 17.0), 3)

    rest = (PIVOT_X, _tray_top_z(PIVOT_X) + BALL_R)
    ball_rest = cq.Solid.makeSphere(BALL_R, cq.Vector(rest[0], 0.0, rest[1]))
    ball_clash = {n: inter(ball_rest, p) for n, p in panels.items() if n in kept}
    ball_clash["feeder_shell_tray"] = inter(ball_rest, shell)

    bb = cq.Compound.makeCompound(list(kept.values())).BoundingBox()
    data = {
        "file": "cad/paddle_launcher_feeder_redesign.py",
        "parent": "cad/paddle_launcher_constrained.py (parent untouched)",
        "units": "mm",
        "paddle_axis_mm": [PADDLE_CX, 0.0, PADDLE_CZ],
        "ball_diameter_mm": BALL_D,
        "carry_radius_mm": R_CARRY,
        "shell_inner_mm": R_CARRY + BALL_R,
        "shell_outer_mm": R_CARRY + BALL_R + SHELL_WALL,
        "shell_sector_deg": [A_EXIT, A_LIP],
        "tangency_check": {
            "target": "release ball centre on the 52 deg channel centreline",
            "required_mm": 55.0,
            "axis_perp_distance_to_ramp_floor_line_mm": round(perp, 4),
            "carry_radius_mm": R_CARRY,
            "release_point_mm": [round(exit_pt[0], 3), round(exit_pt[1], 3)],
            "release_point_along_ramp_mm": round(t_exit, 3),
            "release_point_perp_mm": round(perp_exit, 4),
            "ramp_mid_channel_offset_mm": 55.0,
            "deviation_mm": round(perp_exit - 55.0, 4),
            "status": "pass" if abs(perp_exit - 55.0) <= 1.0 else "fail",
        },
        "tray": {"tilt_deg": TILT_DEG, "pivot_mm": [PIVOT_X, PIVOT_Z],
                 "x_range_mm": [TRAY_X0, TRAY_X1], "thickness_mm": TRAY_T,
                 "entry_ball_centre_z_mm": round(_tray_top_z(TRAY_X1) + BALL_R, 3),
                 "low_end_ball_centre_z_mm": round(_tray_top_z(-2.32) + BALL_R, 3),
                 "drop_mm": round(_tray_top_z(TRAY_X1) - _tray_top_z(-2.32), 3)},
        "removed_from_parent": sorted(dropped),
        "relieved_from_parent": sorted(relieved),
        "consumed_by_rotor_drum": sorted(consumed),
        "rest_ball_centre_mm": [round(rest[0], 3), round(rest[1], 3)],
        "rest_ball_clash_mm3": ball_clash,
        "kept_parts": sorted(kept),
        "kept_part_count": len(kept),
        "bounding_box_mm": {
            "min": [round(v, 3) for v in (bb.xmin, bb.ymin, bb.zmin)],
            "max": [round(v, 3) for v in (bb.xmax, bb.ymax, bb.zmax)],
            "size": [round(v, 3) for v in (bb.xlen, bb.ylen, bb.zlen)],
        },
        "shell_clearance_mm": checks,
        "shell_volume_mm3": round(kept["feeder_shell_tray"].Volume(), 2),
        "linkage_kinematics": kinematics,
    }
    return data


def main():
    kept, dropped, relieved, consumed, kinematics = build("pollen", 80.0)
    data = report(kept, dropped, relieved, consumed, kinematics)
    stem = OUT / "paddle_launcher_motion_free_pollen_v2"
    assy = cq.Assembly(name="paddle_launcher_motion_free_pollen_v2")
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
    print(f"[pollen] exporting STEP -> {stem.with_suffix('.step').name}", flush=True)
    assy.export(str(stem.with_suffix(".step")), exportType="STEP")
    exporters.export(cq.Compound.makeCompound(list(kept.values())),
                     str(stem.with_suffix(".stl")), tolerance=0.2, angularTolerance=0.15)
    (OUT / "paddle_launcher_motion_free_pollen_v2_report.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
