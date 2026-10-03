"""Motion-only extract of the C06-B opposed-flywheel launcher.

Purpose
-------
Give the dynamics / structural simulation a clean geometry set that contains
only the parts that actually move or drive motion:

* launch side  -- flywheel motors, 8 mm REX shaft couplers, flywheel shafts,
                  Gecko flywheels and their Sonic hubs;
* feed side    -- continuous-rotation feeder servo, servo-to-REX coupler,
                  feeder shaft and the three-paddle rotor.

Every static part that is not named below (base rails, support cheeks, slotted
side plates, bearing carriages and their rails, motor clamps and bridges, and
the whole gap-adjust servo + crosshead + link chain) is dropped.

Profiles
--------
``--profile motion_only`` (default)
    Everything that moves or drives motion: motors, shaft couplers, shafts,
    Sonic hubs, Gecko flywheels and the whole feeder drivetrain incl. the
    three-paddle rotor.  No static structure, no ball path.

``--profile motion_free`` -- the "motion version"
    Moving parts plus the ball path, with no actuators:

    * paddle rotor -- ``paddle_hub``, ``paddle_arm_*``, ``paddle_blade_*``,
      ``paddle_flex_tip_*``.  The three ``paddle_hinge_*`` pins that ring the
      rotor (10 mm x 100 mm rods at r = 46 mm, 120 deg apart) are removed on
      request;
    * flywheels -- ``gecko_flywheel_*`` plus their mounting shafts
      (``flywheel_shaft_*``, ``paddle_shaft_*``) unless ``--no-shafts``;
    * the paddle-to-flywheel ramp, identical to the parent file -- the 0 deg /
      26 deg / 52 deg guide panels (``guide_floor_*``, ``guide_roof_*``,
      ``guide_wall_*``) and the two opposed throat cheeks (``shooter_throat_*``);
      ``--with-fingers`` also keeps ``one_way_finger_*``.

    Motors, servos, servo frame, shaft couplers, Sonic hubs and the paddle
    hinge pins are all gone.

The extractor never re-derives a placement.  It calls the existing
``paddle_launcher_constrained.build`` and copies the already-world-placed shapes
verbatim, so the relative physical position of every retained part is exactly
the parent assembly position.  The parent ``paddle_launcher_feasible_*`` files
are never written to.

Units: millimetres.  Chassis plane is X-Y, +Z is up.

Usage
-----
    python cad/paddle_launcher_motion_only.py --list-only
    python cad/paddle_launcher_motion_only.py --config nectar
    python cad/paddle_launcher_motion_only.py --profile motion_free --config both
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import cadquery as cq
from cadquery import exporters

import paddle_launcher_constrained as pl

OUT = HERE / "output"

# Parts whose name must start with one of these prefixes to be kept.
LAUNCH_PREFIXES = (
    "motor_upper_",
    "motor_lower_",
    "motor_coupler_upper_",
    "motor_coupler_lower_",
    "flywheel_shaft_",
    "gecko_flywheel_",
    "sonic_hub_",
)
FEED_PREFIXES = (
    "paddle_cr_servo_",
    "paddle_servo_coupler_",
    "paddle_arm_",
    "paddle_hinge_",
    "paddle_blade_",
    "paddle_flex_tip_",
)
FEED_EXACT = (
    "paddle_hub",
    f"paddle_shaft_{pl.COTS['feeder_shaft']['sku']}",
)

LAUNCH_EXTRA_PREFIXES = ("sonic_hub_", "motor_coupler_upper_", "motor_coupler_lower_")
FEED_EXTRA_PREFIXES = ("paddle_servo_coupler_",)

# --- motion_free profile ("motion version") ------------------------------
# Paddle rotor body.  paddle_hinge_* is excluded on purpose: those are the
# three 10 x 100 mm pins that ring the rotor.
ROTOR_PREFIXES = ("paddle_arm_", "paddle_blade_", "paddle_flex_tip_")
ROTOR_EXACT = ("paddle_hub",)
ROTOR_EXCLUDED_PREFIXES = ("paddle_hinge_",)
# Flywheels and the shafts they spin on.
WHEEL_PREFIXES = ("gecko_flywheel_", "flywheel_shaft_")
# The ball path from the paddle up to the flywheel gap.
RAMP_PREFIXES = ("guide_floor_", "guide_roof_", "guide_wall_", "shooter_throat_")
FINGER_PREFIXES = ("one_way_finger_",)
FEEDER_SHAFT = f"paddle_shaft_{pl.COTS['feeder_shaft']['sku']}"


def is_hardware(name: str) -> bool:
    """Couplers and hubs: spinning drivetrain parts, not structure."""
    return name.startswith(LAUNCH_EXTRA_PREFIXES) or name.startswith(FEED_EXTRA_PREFIXES)


def keep(name: str, hardware: bool = True) -> bool:
    if not hardware and is_hardware(name):
        return False
    if name.startswith(LAUNCH_PREFIXES):
        return True
    if name.startswith(FEED_PREFIXES):
        return True
    if name in FEED_EXACT:
        return True
    return False


def keep_free(name: str, shafts: bool = True, fingers: bool = False) -> bool:
    """motion_free profile: rotor body + flywheels + the ball path only."""
    if name.startswith(ROTOR_EXCLUDED_PREFIXES):
        return False
    if name in ROTOR_EXACT or name.startswith(ROTOR_PREFIXES):
        return True
    if name.startswith(WHEEL_PREFIXES):
        return True
    if name.startswith(RAMP_PREFIXES):
        return True
    if fingers and name.startswith(FINGER_PREFIXES):
        return True
    if shafts and name == FEEDER_SHAFT:
        return True
    return False


def color_for(name: str):
    if name.startswith("gecko_flywheel_"):
        return cq.Color(0.055, 0.06, 0.07)
    if name.startswith(("motor_upper_", "motor_lower_")):
        return cq.Color(0.82, 0.36, 0.12)
    if name.startswith("paddle_cr_servo_"):
        return cq.Color(0.58, 0.30, 0.74)
    if name.startswith(("paddle_flex_tip_",)):
        return cq.Color(0.96, 0.72, 0.18)
    if name.startswith(("paddle_arm_", "paddle_blade_")):
        return cq.Color(0.92, 0.54, 0.12)
    if name.startswith("paddle_hinge_"):
        return cq.Color(0.25, 0.27, 0.30)
    if name.startswith(("flywheel_shaft_", "paddle_shaft_")):
        return cq.Color(0.58, 0.62, 0.68)
    if name.startswith(("guide_", "shooter_throat_")):
        return cq.Color(0.20, 0.56, 0.84, 0.48)
    if name.startswith("one_way_finger_"):
        return cq.Color(0.76, 0.88, 0.96)
    return cq.Color(0.72, 0.74, 0.78)


def build(config: str, half_spacing: float, profile: str = "motion_only",
          hardware: bool = True, shafts: bool = True, fingers: bool = False):
    _assy, _mesh, _shapes, named, kinematics = pl.build(config, half_spacing)
    if profile == "motion_free":
        kept = {n: s for n, s in named.items() if keep_free(n, shafts, fingers)}
    else:
        kept = {n: s for n, s in named.items() if keep(n, hardware)}
    dropped = sorted(n for n in named if n not in kept)
    assembly = cq.Assembly(name=f"paddle_launcher_{profile}_{config}")
    for name, shape in kept.items():
        assembly.add(shape, name=name, color=color_for(name))
    return assembly, kept, dropped, kinematics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", choices=("nectar", "pollen", "both"), default="both")
    parser.add_argument("--profile", choices=("motion_only", "motion_free"),
                        default="motion_only",
                        help="motion_only = drivetrain; motion_free = moving "
                             "parts + ball path, no motors/servos/hubs")
    parser.add_argument("--suffix", default=None,
                        help="output stem; defaults to the profile name")
    parser.add_argument("--no-hardware", action="store_true",
                        help="motion_only: also drop the shaft couplers and wheel hubs")
    parser.add_argument("--no-shafts", action="store_true",
                        help="motion_free: also drop the flywheel/feeder shafts")
    parser.add_argument("--with-fingers", action="store_true",
                        help="motion_free: also keep one_way_finger_*")
    parser.add_argument("--list-only", action="store_true",
                        help="build and print the keep/drop split, export nothing")
    parser.add_argument("--no-mesh", action="store_true", help="skip the STL export")
    args = parser.parse_args()

    hardware = not args.no_hardware
    suffix = args.suffix or args.profile
    report_path = OUT / f"paddle_launcher_{suffix}_report.json"
    configs = (("pollen", 80.0), ("nectar", 89.0)) if args.config == "both" \
        else ((args.config, 80.0 if args.config == "pollen" else 89.0),)

    report = {
        "tool": "cad/paddle_launcher_motion_only.py",
        "source_assembly": "cad/paddle_launcher_constrained.py (C06B-COTS-0.3)",
        "parent_files_overwritten": False,
        "units": "mm",
        "coordinate_system": "X-Y chassis plane; +Z upward",
        "profile": args.profile,
        "output_suffix": suffix,
        "hardware_included": hardware,
        "mounting_shafts_included": not args.no_shafts,
        "one_way_fingers_included": args.with_fingers,
        "configurations": {},
        "config_files": {},
    }

    for config, half_spacing in configs:
        print(f"[{config}] building parent assembly ...", flush=True)
        assembly, kept, dropped, kinematics = build(
            config, half_spacing, args.profile, hardware,
            not args.no_shafts, args.with_fingers)
        files = {}
        if args.list_only:
            print(f"[{config}] keep {len(kept)} / drop {len(dropped)}", flush=True)
            for name in sorted(kept):
                print(f"    KEEP {name}", flush=True)
            for name in dropped:
                print(f"    drop {name}", flush=True)
        else:
            stem = OUT / f"paddle_launcher_{suffix}_{config}"
            print(f"[{config}] keep {len(kept)} / drop {len(dropped)}", flush=True)
            for name in sorted(kept):
                print(f"    KEEP {name}", flush=True)
            print(f"[{config}] exporting STEP -> {stem.with_suffix('.step').name}", flush=True)
            assembly.export(str(stem.with_suffix(".step")), exportType="STEP")
            files["step"] = str(stem.with_suffix(".step"))
            if not args.no_mesh:
                print(f"[{config}] exporting STL ...", flush=True)
                exporters.export(cq.Compound.makeCompound(list(kept.values())), str(stem.with_suffix(".stl")),
                                 tolerance=0.18, angularTolerance=0.14)
                files["stl"] = str(stem.with_suffix(".stl"))

        bb = cq.Compound.makeCompound(list(kept.values())).BoundingBox()
        report["configurations"][config] = {
            "half_axle_spacing_mm": half_spacing,
            "axle_center_distance_mm": 2 * half_spacing,
            "kept_part_count": len(kept),
            "dropped_part_count": len(dropped),
            "kept_parts": sorted(kept),
            "dropped_parts": sorted(dropped),
            "solid_count": len(cq.Compound.makeCompound(list(kept.values())).Solids()),
            "bounding_box_mm": {
                "min": [round(bb.xmin, 3), round(bb.ymin, 3), round(bb.zmin, 3)],
                "max": [round(bb.xmax, 3), round(bb.ymax, 3), round(bb.zmax, 3)],
                "size": [round(bb.xlen, 3), round(bb.ylen, 3), round(bb.zlen, 3)],
            },
            "linkage_kinematics": kinematics,
            "files": files,
        }
        report["config_files"][config] = pl.CONFIG.as_posix()

    if not args.list_only:
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"report -> {report_path.name}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
