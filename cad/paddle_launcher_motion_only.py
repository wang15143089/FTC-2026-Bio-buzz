"""Motion-only extract of the C06-B opposed-flywheel launcher.

Purpose
-------
Give the dynamics / structural simulation a clean geometry set that contains
only the parts that actually move or drive motion:

* launch side  -- flywheel motors, 8 mm REX shaft couplers, flywheel shafts,
                  Gecko flywheels and their Sonic hubs;
* feed side    -- continuous-rotation feeder servo, servo-to-REX coupler,
                  feeder shaft and the three-paddle rotor.

Every static part (guide/channel panels, base rails, support cheeks, throat,
one-way fingers, slotted side plates, bearing carriages and their rails, motor
clamps and bridges, and the whole gap-adjust servo + crosshead + link chain) is
dropped.

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
REPORT = OUT / "paddle_launcher_motion_only_report.json"

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
    if name.startswith(("flywheel_shaft_", "paddle_shaft_")):
        return cq.Color(0.58, 0.62, 0.68)
    return cq.Color(0.72, 0.74, 0.78)


def build(config: str, half_spacing: float, hardware: bool = True):
    _assy, _mesh, _shapes, named, kinematics = pl.build(config, half_spacing)
    kept = {n: s for n, s in named.items() if keep(n, hardware)}
    dropped = sorted(n for n in named if n not in kept)
    assembly = cq.Assembly(name=f"paddle_launcher_motion_only_{config}")
    for name, shape in kept.items():
        assembly.add(shape, name=name, color=color_for(name))
    return assembly, kept, dropped, kinematics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", choices=("nectar", "pollen", "both"), default="both")
    parser.add_argument("--suffix", default="motion_only")
    parser.add_argument("--no-hardware", action="store_true",
                        help="also drop the shaft couplers and wheel hubs")
    parser.add_argument("--list-only", action="store_true",
                        help="build and print the keep/drop split, export nothing")
    parser.add_argument("--no-mesh", action="store_true", help="skip the STL export")
    args = parser.parse_args()

    hardware = not args.no_hardware
    configs = (("pollen", 80.0), ("nectar", 89.0)) if args.config == "both" \
        else ((args.config, 80.0 if args.config == "pollen" else 89.0),)

    report = {
        "tool": "cad/paddle_launcher_motion_only.py",
        "source_assembly": "cad/paddle_launcher_constrained.py (C06B-COTS-0.3)",
        "parent_files_overwritten": False,
        "units": "mm",
        "coordinate_system": "X-Y chassis plane; +Z upward",
        "hardware_included": hardware,
        "configurations": {},
        "config_files": {},
    }

    for config, half_spacing in configs:
        print(f"[{config}] building parent assembly ...", flush=True)
        assembly, kept, dropped, kinematics = build(config, half_spacing, hardware)
        files = {}
        if args.list_only:
            print(f"[{config}] keep {len(kept)} / drop {len(dropped)}", flush=True)
            for name in sorted(kept):
                print(f"    KEEP {name}", flush=True)
            for name in dropped:
                print(f"    drop {name}", flush=True)
        else:
            stem = OUT / f"paddle_launcher_{args.suffix}_{config}"
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
        REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"report -> {REPORT.name}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
