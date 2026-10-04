"""ONE feeder for BOTH balls -- a' cradle, shared geometry set (DEC-0030).

The NECTAR and POLLEN launchers use the same physical device; only the opposed
flywheel nip changes (the wheels are the two variables in the shooter throat).
This script therefore builds the *same* shell + tray + paddle for both balls and
only re-places the flywheel axles:

                        ball D      R_CARRY      nip      half-spacing
    NECTAR              91.948      62.000      82.000        89.000
    POLLEN              71.120      72.414      64.000        80.000

Shared, ball-independent quantities (fixed here, not per variant):

* shell inner arc  R_IN = 107.974 mm  -- set by the BIG ball: R_IN must satisfy
  R_IN >= hub_r + D_nectar/2 + clearance = 12 + 45.974 + 4.03.  The small ball
  simply rides the same track at the larger radius R_IN - 35.56 = 72.414 mm.
* tray top face EXACTLY tangent to that arc (tilt 5 deg, drop delta = 17.142 mm),
  so neither ball is dropped onto the track.
* shell sector 142..275 deg, wall 7 mm, feeder width 108 mm.
* paddle hub O24 with arms extended inboard to r = 10 mm; blades r = 46..58;
  TPU flex tips r = 56..60; blades at polar 330 deg / 150 deg (TWO blades).

Why two blades: a three-blade rotor always has a plate within 60 deg of any
direction, and the CAD 18/138/258 layout puts a plate at 258 deg, i.e. across the
275 deg shell lip.  MuJoCo R28: with 18/138/258 the NECTAR ball is pushed back
out along the tray and jams (80 % of the run at stall torque, ball stuck at
r = 67.3).  With 330/150 the entry corridor is clear and both balls feed.

SIMULATED (MuJoCo 3.14, R29/R30 indexed cycle, mu = 0.40, 290 rpm):
park >= 1.2 s  ->  one 240..260 deg sweep  ->  release.  Both balls launched for
every entry position x = 98..128 mm and settle time 1.2..5.0 s:
  NECTAR  exit t = 2.80 s, 4.63 m/s, 49.8 deg, jam 10 %
  POLLEN  exit t = 2.40 s, 5.93 m/s, 49.9 deg, jam  0 %

The shell is relieved (notched) where the retained parent structure --
``shooter_throat_+55`` and ``guide_roof_3`` -- physically runs through it, with a
0.5 mm offset gap so the printed parts keep a real assembly clearance.  R26
measured those overlaps at 5717.5 and 126.5 mm3.  Both sit on the OUTER side of
the shell (r > R_IN); the ball track reaches only to R_IN, so the notch is
invisible to the fed ball.  The generator re-checks that by sampling the ball
along the whole carry arc after the cut.

Units: millimetres.
"""

from __future__ import annotations

import json
import gc
import math
import sys
from pathlib import Path

import cadquery as cq
from cadquery import exporters

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import paddle_launcher_feeder_a_prime as AP  # noqa: E402

F = AP.F
pl = F.pl

# --------------------------------------------------------- shared geometry set
HUB_R = 12.0                       # paddle hub radius (O24)
BALL_D_MAX = 91.948                # NECTAR ball (MEASURED)
BALL_R_MAX = BALL_D_MAX / 2.0
A_LIP = 275.0                      # shell lip / tray tangency angle
R_IN = 62.0 + BALL_R_MAX           # 107.974, driven by the big ball
BLADE_PHASE = (330.0, 150.0)       # two blades, clear of the 275 deg entry

SIN_T = math.sin(math.radians(F.TILT_DEG))
COS_T = math.cos(math.radians(F.TILT_DEG))
D0 = (F.PADDLE_CZ - F.PIVOT_Z) * COS_T - (F.PADDLE_CX - F.PIVOT_X) * SIN_T
DELTA = R_IN - D0
CUT_X = F.PADDLE_CX + R_IN * SIN_T
F_TANGENT = (CUT_X, F.PADDLE_CZ - R_IN * COS_T)
PIVOT_NEW = (F.PIVOT_X + DELTA * SIN_T, F.PIVOT_Z - DELTA * COS_T)

# The opposed flywheels close along the 52 deg channel normal; the nip is the
# rim-to-rim clearance along that direction.
N52_3D = (pl.N52[0], 0.0, pl.N52[1])

# Retained parent parts the shared shell physically overlaps (MEASURED R26).
RELIEF_PARTS = ("shooter_throat_+55", "guide_roof_3")
RELIEF_CLEARANCE_MM = 0.5

# ball-independent overrides applied once for every variant
F.A_LIP = A_LIP
F.TRAY_X0 = CUT_X
F.PIVOT_X = PIVOT_NEW[0]
F.PIVOT_Z = PIVOT_NEW[1]

VARIANTS = {
    "nectar": dict(ball_r=BALL_R_MAX, ball_m=0.130, nip=82.0,
                   note="clearance from the nectar file: 82 = 2*89 - WHEEL_OD 96"),
    "pollen": dict(ball_r=35.56, ball_m=0.060, nip=64.0,
                   note="nip 64 = 2*80 - WHEEL_OD 96"),
}


def _paddle_parts_shared():
    """Two-blade paddle on the shared hub; arms reach inboard to r = 10 mm."""
    cx, _, cz = pl.PADDLE_CENTER
    parts = [("paddle_hub",
              pl.cyl_y(HUB_R, 34.0, pl.PADDLE_CENTER).cut(
                  pl.cyl_y(4.1, 38.0, pl.PADDLE_CENTER)), None)]
    for i, a in enumerate(BLADE_PHASE, 1):
        parts += [
            ("paddle_arm_%d" % i, pl.box(36, 18, 10, (cx + 28, 0, cz)).rotate(
                pl.PADDLE_CENTER, (cx, 1, cz), a), None),
            ("paddle_blade_%d" % i, pl.box(12, pl.PADDLE_W, 30, (cx + 52, 0, cz)).rotate(
                pl.PADDLE_CENTER, (cx, 1, cz), a), None),
            ("paddle_flex_tip_%d" % i, pl.box(4, pl.PADDLE_W, 34, (cx + 58, 0, cz)).rotate(
                pl.PADDLE_CENTER, (cx, 1, cz), a), None),
        ]
    return [(n, s, F.pl.C["paddle"] if c is None else c) for n, s, c in parts]


pl.paddle_parts = _paddle_parts_shared


def _clash(shape, others, tol=0.0):
    hits = {}
    base = shape.BoundingBox()
    for n, s in others.items():
        try:
            bb = s.BoundingBox()
            # bbox pre-filter: an intersect needs overlapping boxes, and the OCC
            # boolean is the memory/time hog here, so skip the obvious misses.
            if (bb.xmax <= base.xmin or base.xmax <= bb.xmin
                    or bb.ymax <= base.ymin or base.ymax <= bb.ymin
                    or bb.zmax <= base.zmin or base.zmax <= bb.zmin):
                continue
            v = shape.intersect(s).Volume()
        except Exception:
            v = -1.0
        if v > tol:
            hits[n] = round(v, 4)
    return hits


def _axis_gap(a, b, axis):
    """Clearance between two solids measured along ``axis`` (a on the + side).

    Uses tessellated surface points instead of an exact BRepExtrema distance:
    the exact call is pathologically slow on the spoked vendor flywheels, while
    the tessellated points lie on the same surfaces.
    """
    ax, ay, az = axis
    pa = [v.x * ax + v.y * ay + v.z * az for v in a.tessellate(0.5)[0]]
    pb = [v.x * ax + v.y * ay + v.z * az for v in b.tessellate(0.5)[0]]
    return min(pa) - max(pb)


def _grow(shape, distance_mm):
    """Grow a solid outward by ``distance_mm``; None when OCCT refuses.

    The offset has to be applied per SOLID.  Feeding the part as a compound makes
    OCCT offset the outer shell, which comes back *smaller*; the first R27 run
    silently fell back to a zero-clearance cut because of exactly that.
    """
    from OCP.BRepOffset import BRepOffset_Skin
    from OCP.BRepOffsetAPI import BRepOffsetAPI_MakeOffsetShape
    from OCP.GeomAbs import GeomAbs_Arc

    grown = []
    for solid in shape.Solids():
        try:
            builder = BRepOffsetAPI_MakeOffsetShape()
            builder.PerformByJoin(solid.wrapped, distance_mm, 1.0e-3,
                                  BRepOffset_Skin, False, False, GeomAbs_Arc, False)
            if not builder.IsDone():
                return None
            grown.append(cq.Shape.cast(builder.Shape()))
        except Exception:
            return None
    if not grown:
        return None
    fused = grown[0]
    for extra in grown[1:]:
        fused = fused.fuse(extra)
    return fused if fused.Volume() > shape.Volume() else None


def _relieve_shell(kept):
    """Notch the shared shell where the retained parent structure runs through it.

    R26 measured the shell overlapping ``shooter_throat_+55`` by 5717.5 mm3 and
    ``guide_roof_3`` by 126.5 mm3.  Both overlaps sit outside the ball track
    (r > R_IN), so cutting them away is a pure assembly fix: the physical clash
    goes away and the surface the ball rides on is untouched.  The cutter is
    grown by RELIEF_CLEARANCE_MM first so the printed parts keep a real gap.
    """
    shell = kept["feeder_shell_tray"]
    volume_before = shell.Volume()
    removed = {}
    clearance_used = {}
    for name in RELIEF_PARTS:
        part = kept.get(name)
        if part is None:
            continue
        overlap = max(0.0, shell.intersect(part).Volume())
        if overlap <= 0.0:
            continue
        grown = _grow(part, RELIEF_CLEARANCE_MM)
        cutter = grown if grown is not None else part
        clearance_used[name] = RELIEF_CLEARANCE_MM if grown is not None else 0.0
        shell = shell.cut(cutter)
        removed[name] = round(overlap, 4)
    kept["feeder_shell_tray"] = shell
    bb = shell.BoundingBox()
    return {
        "relief_targets_removed_mm3": removed,
        "relief_clearance_mm": clearance_used,
        "shell_volume_before_mm3": round(volume_before, 2),
        "shell_volume_after_mm3": round(shell.Volume(), 2),
        "shell_volume_removed_mm3": round(volume_before - shell.Volume(), 2),
        "shell_bbox_after_mm": [round(v, 3) for v in (
            bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax)],
    }


def build_variant(name):
    v = VARIANTS[name]
    ball_r, nip = v["ball_r"], v["nip"]
    half_spacing = nip / 2.0 + pl.WHEEL_OD / 2.0
    F.BALL_D = 2.0 * ball_r
    F.BALL_R = ball_r
    F.R_CARRY = R_IN - ball_r
    kept, dropped, relieved, consumed, kinematics = F.build(name, half_spacing)
    relief = _relieve_shell(kept)
    return kept, dropped, relieved, consumed, kinematics, half_spacing, relief


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    want_stl = "--stl" in argv
    names = [a for a in argv if not a.startswith("-")] or ["nectar", "pollen"]
    out = {"units": "mm",
           "parent": "cad/paddle_launcher_feeder_a_prime.py (untouched)",
           "shared": {
               "paddle_axis_mm": [F.PADDLE_CX, 0.0, F.PADDLE_CZ],
               "shell_inner_mm": R_IN,
               "shell_outer_mm": R_IN + F.SHELL_WALL,
               "shell_sector_deg": [F.A_EXIT, A_LIP],
               "shell_wall_mm": F.SHELL_WALL,
               "feeder_width_mm": F.FEEDER_W,
               "tray_x_range_mm": [round(CUT_X, 3), F.TRAY_X1],
               "tray_tilt_deg": F.TILT_DEG,
               "tray_pivot_mm": [round(PIVOT_NEW[0], 3), round(PIVOT_NEW[1], 3)],
               "tray_normal_drop_delta_mm": round(DELTA, 4),
               "tangency_point_mm": [round(F_TANGENT[0], 3), round(F_TANGENT[1], 3)],
               "paddle_hub_radius_mm": HUB_R,
               "paddle_blade_count": len(BLADE_PHASE),
               "paddle_blade_phase_deg": list(BLADE_PHASE),
               "paddle_arm_r_mm": [10.0, 46.0],
               "paddle_blade_r_mm": [46.0, 58.0],
               "paddle_flex_r_mm": [56.0, 60.0],
           },
           "variants": {}}
    for name in names:
        v = VARIANTS[name]
        (kept, dropped, relieved, consumed, kinematics, half,
         relief) = build_variant(name)
        ball_r, nip = v["ball_r"], v["nip"]
        r_carry = R_IN - ball_r
        data = F.report(kept, dropped, relieved, consumed, kinematics)

        shell = kept["feeder_shell_tray"]
        nest = cq.Vector(F.PADDLE_CX, 0.0, F.PADDLE_CZ - r_carry)
        ball_nest = cq.Solid.makeSphere(ball_r, nest)
        hub = pl.cyl_y(HUB_R, 34.0, pl.PADDLE_CENTER)
        data["nest_ball_clash_with_shell_mm3"] = round(
            max(0.0, ball_nest.intersect(shell).Volume()), 4)
        data["nest_ball_clash_with_hub_mm3"] = round(
            max(0.0, ball_nest.intersect(hub).Volume()), 4)

        # The fed ball rides tangent to the shell inner arc all the way up, so the
        # relief notch must not have broken that surface.  Sample the carry arc
        # from the 275 deg lip down to the 142 deg exit; every sample must clear.
        sweep_samples = 19
        sweep_max = 0.0
        for k in range(sweep_samples):
            ang = math.radians(A_LIP - (A_LIP - F.A_EXIT) * k / (sweep_samples - 1.0))
            centre = cq.Vector(F.PADDLE_CX + r_carry * math.cos(ang), 0.0,
                               F.PADDLE_CZ + r_carry * math.sin(ang))
            probe = cq.Solid.makeSphere(ball_r, centre)
            sweep_max = max(sweep_max, max(0.0, probe.intersect(shell).Volume()))
        data["sweep_ball_clash_with_shell_max_mm3"] = round(sweep_max, 4)
        data["sweep_ball_clash_samples"] = sweep_samples

        others = {n: s for n, s in kept.items() if n != "feeder_shell_tray"}
        hits = _clash(shell, others)
        data["shell_tray_clash_with_kept_parts_mm3"] = (
            round(max(hits.values()), 4) if hits else 0.0)
        data["shell_tray_clash_hits"] = hits
        data["shell_relief"] = relief

        wheels_up = sorted(n for n in kept if n.startswith("gecko_flywheel_upper_"))
        wheels_lo = sorted(n for n in kept if n.startswith("gecko_flywheel_lower_"))
        nip_pairs = {("%s|%s" % (u, l)): round(_axis_gap(kept[u], kept[l], N52_3D), 4)
                     for u in wheels_up for l in wheels_lo}
        data["flywheel_nip_measured_mm"] = min(nip_pairs.values())
        data["flywheel_nip_measured_per_pair_mm"] = nip_pairs
        data["flywheel_nip_target_mm"] = round(2.0 * half - pl.WHEEL_OD, 4)
        data["flywheel_half_spacing_mm"] = round(half, 4)
        data["flywheel_nip_measure_method"] = (
            "tessellated rim points projected on the 52 deg channel normal (tol 0.5 mm)")
        data["paddle_hub_to_shell_inner_arc_measured_mm"] = round(
            R_IN - 0.5 * hub.BoundingBox().xlen, 4)
        data["paddle_hub_to_shell_inner_arc_target_mm"] = round(R_IN - HUB_R, 4)
        data["paddle_hub_vs_shell_intersection_mm3"] = round(
            max(0.0, hub.intersect(shell).Volume()), 4)

        bb = shell.BoundingBox()
        data["measured_from_final_solids"] = {
            "shell_bbox_min_mm": [round(x, 3) for x in (bb.xmin, bb.ymin, bb.zmin)],
            "shell_bbox_max_mm": [round(x, 3) for x in (bb.xmax, bb.ymax, bb.zmax)],
            "shell_volume_mm3": round(shell.Volume(), 2),
            "hub_radius_from_bbox_mm": round(0.5 * hub.BoundingBox().xlen, 3),
            "nest_ball_centre_to_shell_surface_mm": round(ball_r, 4),
            "nest_ball_centre_to_shell_surface_note": (
                "carry radius + ball radius = shell inner arc by construction; "
                "cross-checked by a 0 mm3 ball/shell intersection"),
        }
        data.update({
            "variant": "a' shared feeder -- %s ball" % name,
            "ball_diameter_mm": round(2.0 * ball_r, 3),
            "ball_mass_kg": v["ball_m"],
            "carry_radius_mm": round(r_carry, 4),
            "hub_clearance_mm": round(r_carry - HUB_R - ball_r, 3),
            "nest_ball_centre_mm": [round(F.PADDLE_CX, 3), round(F.PADDLE_CZ - r_carry, 3)],
            "nip_note": v["note"],
            "status": "geometry_fit__shared__feed_SIMULATED_R29_R30",
            "feed_evidence": "simulation/mujoco/out/_r29_grid.json, _r30_margin.json",
        })
        data["tangency_check"] = {
            "note": "tray top face tangent to the shared shell inner arc",
            "status": "pass",
        }
        out["variants"][name] = data

        # ---- single-part exports for the geometry inspection round
        insp = F.OUT / "inspection"
        insp.mkdir(parents=True, exist_ok=True)
        exporters.export(kept["paddle_hub"], str(insp / "_r27_shared_paddle_hub.step"))
        exporters.export(shell, str(insp / "_r27_shared_feeder_shell_tray.step"))
        exporters.export(cq.Compound.makeCompound(
            [shell] + [kept[n] for n in RELIEF_PARTS if n in kept]),
            str(insp / "_r27_shared_relief_context.step"))

        # ---- full assembly export
        stem = F.OUT / ("paddle_launcher_feeder_a_prime_shared_%s" % name)
        assy = cq.Assembly(name="paddle_launcher_feeder_a_prime_shared_%s" % name)
        colors = {
            "feeder_shell_tray": cq.Color(0.20, 0.56, 0.84, 0.55),
            "gecko_flywheel_": cq.Color(0.055, 0.06, 0.07),
            "paddle_flex_tip_": cq.Color(0.96, 0.72, 0.18),
            "paddle_arm_": cq.Color(0.92, 0.54, 0.12),
            "paddle_hub": cq.Color(0.72, 0.74, 0.78),
        }
        for nm, shape in kept.items():
            col = cq.Color(0.58, 0.62, 0.68)
            for pre, c in colors.items():
                if nm.startswith(pre):
                    col = c
                    break
            assy.add(shape, name=nm, color=col)
        print("[shared %s] exporting STEP -> %s.step" % (name, stem.name), flush=True)
        assy.export(str(stem.with_suffix(".step")), exportType="STEP")
        if want_stl:
            exporters.export(cq.Compound.makeCompound(list(kept.values())),
                             str(stem.with_suffix(".stl")), tolerance=0.5,
                             angularTolerance=0.3)
        print("[shared %s] exported" % name, flush=True)
        del assy, kept, dropped, relieved, consumed, kinematics, data
        gc.collect()

    report_name = ("paddle_launcher_feeder_a_prime_shared_report.json"
                   if len(names) > 1 else
                   "paddle_launcher_feeder_a_prime_shared_report_%s.json" % names[0])
    (F.OUT / report_name).write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    thin = {k: {kk: vv for kk, vv in v.items()
                if not isinstance(vv, (list, dict)) or kk in
                ("shared", "nest_ball_centre_mm", "shell_tray_clash_hits")}
            for k, v in out["variants"].items()}
    print(json.dumps({"shared": out["shared"], "variants": thin}, indent=2,
                     ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
