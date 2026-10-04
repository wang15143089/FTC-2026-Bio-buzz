"""SUPERSEDED by cad/paddle_launcher_feeder_a_prime_shared.py (DEC-0030).

Do not build or cite this module's rotor.  It produced the R25 NECTAR artifact
recorded by DEC-0029 with a THREE-blade rotor (arms at 18 / 138 / 258 deg).
MuJoCo round R28 shows the 258 deg plate sits across the 275 deg shell lip,
inside the entry corridor: the 91.9 mm NECTAR ball is pushed back out along the
tray and jams for 80 % of the run at stall torque (ball stuck at r = 67.3 mm,
295 deg).  A TWO-blade rotor at 330 / 150 deg leaves the corridor clear and both
the NECTAR and the POLLEN ball feed and launch (R29 grid / R30 margin: 12 of 12
combinations pass).

DEC-0030 retired this generator.  The feeder is now built by
cad/paddle_launcher_feeder_a_prime_shared.py, which emits BOTH ball variants
from ONE geometry source and varies only the flywheel nip (NECTAR 82 mm /
POLLEN 64 mm).  Kept for engineering history: the R25 STEP/STL artifact, its
report, and DEC-0029 (its tangency / lip 275 deg / hub O24 content still stands;
only the blade count and phase were superseded).

Running this file is a no-op that prints the pointer below.

--- original R25 header -------------------------------------------------

a' cradle, NECTAR ball (D = 91.948 mm) -- R25 geometry set (DEC-0029).

Built on the untouched a' module (``paddle_launcher_feeder_a_prime.py``); only
ball-dependent and NECTAR-specific parameters are overridden.  The parent
``cad/paddle_launcher_constrained.py`` and the original STEP are not modified.

Geometry set fixed by the R23/R24 MuJoCo gravity hand-off study:

* BALL_D     71.120 -> 91.948  (MEASURED from the NECTAR STEP)
* BALL_R     35.560 -> 45.974
* R_CARRY    58.400 -> 62.000  (hub r=12 + ball r -> 4.03 mm hub clearance)
* A_LIP     292.000 -> 275.000 (tangency angle, independent of ball size)
* TRAY_X0    56.000 -> 38.901  (tangency point x of tray top face)
* PIVOT     (-2.30, 17.50) -> (-0.806, 0.423): the whole tray drops delta =
  17.142 mm along the tray normal, so the tray top face is EXACTLY tangent to
  the r_in = R_CARRY + BALL_R = 107.974 mm shell inner arc.  Without this drop
  the ball leaves the tray 13 mm above the carry circle and jams (R20-R22).
* paddle hub radius 18 -> 12 mm (O24), arm rebuilt to r=10..46 so it still
  overlaps the smaller hub.

SIMULATED (R24 H3, MuJoCo 3.14, 60 rpm CCW, mu=0.40, nip 82 mm, 25 s):
launch=True, exit t=3.264 s, exit speed 4.740 m/s at 51.9 deg, jam 8 %.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import cadquery as cq
from cadquery import exporters

import paddle_launcher_feeder_a_prime as AP  # noqa: E402

F = AP.F
pl = F.pl

# ------------------------------------------------- NECTAR geometry set (R25)
HUB_R = 12.0                     # paddle hub radius (O24)
R_CARRY = 62.0                   # ball-centre orbit radius
BALL_D = 91.948
BALL_R = 45.974
A_LIP = 275.0                    # = atan2(-cos(tilt), sin(tilt))

SIN_T = math.sin(math.radians(F.TILT_DEG))
COS_T = math.cos(math.radians(F.TILT_DEG))
R_IN = R_CARRY + BALL_R
D0 = (F.PADDLE_CZ - F.PIVOT_Z) * COS_T - (F.PADDLE_CX - F.PIVOT_X) * SIN_T
DELTA = R_IN - D0
CUT_X = F.PADDLE_CX + R_IN * SIN_T
F_TANGENT = (CUT_X, F.PADDLE_CZ - R_IN * COS_T)
PIVOT_NEW = (F.PIVOT_X + DELTA * SIN_T, F.PIVOT_Z - DELTA * COS_T)

F.BALL_D = BALL_D
F.BALL_R = BALL_R
F.R_CARRY = R_CARRY
F.A_LIP = A_LIP
F.TRAY_X0 = CUT_X
F.PIVOT_X = PIVOT_NEW[0]
F.PIVOT_Z = PIVOT_NEW[1]

_ARM_PHASE = {1: 18.0, 2: 138.0, 3: 258.0}
_orig_paddle_parts = pl.paddle_parts


def paddle_parts_r25():
    """Parent paddle with a O24 hub and arms extended inboard to r=10."""
    cx, _, cz = pl.PADDLE_CENTER
    out = []
    for name, shape, col in _orig_paddle_parts():
        if name == "paddle_hub":
            shape = pl.cyl_y(HUB_R, 34.0, pl.PADDLE_CENTER).cut(
                pl.cyl_y(4.1, 38.0, pl.PADDLE_CENTER))
        elif name.startswith("paddle_arm_"):
            a = _ARM_PHASE[int(name.rsplit("_", 1)[1])]
            shape = pl.box(36, 18, 10, (cx + 28, 0, cz)).rotate(
                pl.PADDLE_CENTER, (cx, 1, cz), a)
        out.append((name, shape, col))
    return out


pl.paddle_parts = paddle_parts_r25        # F.build() -> pl.build() picks this up


def _clash(shape, others, tol=0.0):
    hits = {}
    for n, s in others.items():
        try:
            v = shape.intersect(s).Volume()
        except Exception:
            v = -1.0
        if v > tol:
            hits[n] = round(v, 4)
    return hits


def main():
    print(__doc__.split("\n--- original R25 header")[0].strip(), file=sys.stderr)
    return 2

    kept, dropped, relieved, consumed, kinematics = F.build("nectar", 89.0)
    data = F.report(kept, dropped, relieved, consumed, kinematics)

    shell = kept["feeder_shell_tray"]
    nest = cq.Vector(F.PADDLE_CX, 0.0, F.PADDLE_CZ - R_CARRY)
    ball_nest = cq.Solid.makeSphere(BALL_R, nest)
    hub = pl.cyl_y(HUB_R, 34.0, pl.PADDLE_CENTER)
    data["nest_ball_clash_with_shell_mm3"] = round(
        max(0.0, ball_nest.intersect(shell).Volume()), 4)
    data["nest_ball_clash_with_hub_mm3"] = round(
        max(0.0, ball_nest.intersect(hub).Volume()), 4)

    others = {n: s for n, s in kept.items() if n != "feeder_shell_tray"}
    clash_hits = _clash(shell, others)
    data["shell_tray_clash_with_kept_parts_mm3"] = (
        round(max(clash_hits.values()), 4) if clash_hits else 0.0)
    data["shell_tray_clash_hits"] = clash_hits

    bb = cq.Compound.makeCompound(list(kept.values())).BoundingBox()
    # ---- single-part exports + on-geometry measurements for the inspection round
    insp = F.OUT / "inspection"
    insp.mkdir(parents=True, exist_ok=True)
    shell_bb = shell.BoundingBox()
    hub_bb = hub.BoundingBox()
    try:
        nest_to_shell = round(
            shell.distance(cq.Vertex.makeVertex(*nest.toTuple())), 4)
    except Exception:
        nest_to_shell = -1.0
    try:
        hub_to_ball = round(hub.distance(ball_nest), 4)
    except Exception:
        hub_to_ball = -1.0

    # Two-place measurements the single-file ``--step`` inspection runs cannot
    # see: the opposed-flywheel nip (the user hard constraint for this round)
    # and the hub-to-shell-inner-arc gap.  cadquery Shape has ``distance``, not
    # ``dist``/``distToShape`` in this build.
    wheels_up = sorted(n for n in kept if n.startswith("gecko_flywheel_upper_"))
    wheels_lo = sorted(n for n in kept if n.startswith("gecko_flywheel_lower_"))
    nip = min((kept[u].distance(kept[l]), u, l) for u in wheels_up for l in wheels_lo)
    hub_to_shell = kept["paddle_hub"].distance(shell)

    data["pair_clearances_from_final_solids"] = {
        "method": "BRepExtrema DistShapeShape between the placed final solids",
        "flywheel_nip_measured_mm": round(nip[0], 4),
        "flywheel_nip_governing_pair": [nip[1], nip[2]],
        "flywheel_nip_target_mm": round(2.0 * 89.0 - pl.WHEEL_OD, 4),
        "flywheel_nip_status": "KNOWN (user 2026-10-04: nectar clearance uses "
                               "the nectar file; 82 = 2*89 - WHEEL_OD 96)",
        "paddle_hub_to_shell_inner_arc_measured_mm": round(hub_to_shell, 4),
        "paddle_hub_to_shell_inner_arc_target_mm": round(R_IN - HUB_R, 4),
    }
    data["measured_from_final_solids"] = {
        "hub_bbox_mm": [round(v, 3) for v in (hub_bb.xlen, hub_bb.ylen, hub_bb.zlen)],
        "hub_radius_from_bbox_mm": round(0.5 * hub_bb.xlen, 3),
        "hub_solid_count": len(hub.Solids()),
        "shell_bbox_min_mm": [round(v, 3) for v in (shell_bb.xmin, shell_bb.ymin, shell_bb.zmin)],
        "shell_bbox_max_mm": [round(v, 3) for v in (shell_bb.xmax, shell_bb.ymax, shell_bb.zmax)],
        "shell_solid_count": len(shell.Solids()),
        "shell_volume_mm3": round(shell.Volume(), 2),
        "nest_ball_centre_to_shell_surface_mm": nest_to_shell,
        "hub_to_nest_ball_surface_mm": hub_to_ball,
    }
    for nm in ("paddle_hub", "feeder_shell_tray"):
        if nm in kept:
            exporters.export(kept[nm], str(insp / ("_r25_nectar_%s.step" % nm)))

    data.update({
        "variant": "a' NECTAR R25 -- tray tangent to carry circle, O24 hub",
        "status": "geometry_fit__feed_SIMULATED_R24_H3",
        "hub_radius_mm": HUB_R,
        "carry_radius_mm": R_CARRY,
        "shell_inner_mm": R_IN,
        "shell_outer_mm": R_IN + F.SHELL_WALL,
        "shell_sector_deg": [F.A_EXIT, A_LIP],
        "tray_x_range_mm": [round(F.TRAY_X0, 3), F.TRAY_X1],
        "tray_pivot_mm": [round(PIVOT_NEW[0], 3), round(PIVOT_NEW[1], 3)],
        "tray_tangency": {
            "tray_plane_to_axis_before_mm": round(D0, 4),
            "required_r_in_mm": round(R_IN, 4),
            "tray_normal_drop_delta_mm": round(DELTA, 4),
            "tangency_point_mm": [round(F_TANGENT[0], 3), round(F_TANGENT[1], 3)],
            "shell_lip_angle_deg": round(A_LIP, 3),
            "status": "pass",
        },
        "hub_clearance_mm": round(R_CARRY - HUB_R - BALL_R, 3),
        "nest_ball_centre_mm": [round(F.PADDLE_CX, 3),
                                round(F.PADDLE_CZ - R_CARRY, 3)],
        "tray_entry_ball_centre_mm": [F.TRAY_X1,
                                      round(F._tray_top_z(F.TRAY_X1) + BALL_R, 3)],
        "bounding_box_mm": {
            "min": [round(v, 3) for v in (bb.xmin, bb.ymin, bb.zmin)],
            "max": [round(v, 3) for v in (bb.xmax, bb.ymax, bb.zmax)],
        },
        "flywheel_nip_target_mm": round(2.0 * 89.0 - pl.WHEEL_OD, 4),
    })
    data["tangency_check"] = {
        "note": "parent ramp-release check is not applicable to the NECTAR set; "
                "the tray-to-carry-circle tangency below is the governing one",
        "status": "not_run",
    }

    stem = F.OUT / "paddle_launcher_feeder_a_prime_nectar"
    assy = cq.Assembly(name="paddle_launcher_feeder_a_prime_nectar")
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
    print("[a' nectar R25] exporting STEP -> %s" % stem.with_suffix(".step").name,
          flush=True)
    assy.export(str(stem.with_suffix(".step")), exportType="STEP")
    exporters.export(cq.Compound.makeCompound(list(kept.values())),
                     str(stem.with_suffix(".stl")), tolerance=0.2,
                     angularTolerance=0.15)
    (F.OUT / "paddle_launcher_feeder_a_prime_nectar_report.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

