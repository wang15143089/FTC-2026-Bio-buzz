"""Adapter that presents the derived T06 vendor solids to the launcher.

``t06_vendor_solids`` derives exactly one complete working part per purchased
goBILDA SKU from the official supplier STEP recorded in
``references/vendor/gobilda/t06/manifest.json``; a part the supplier models with
real internal air gaps keeps its body split and is never force-merged.  This module is the thin
adapter the launcher imports.  It keeps the function names the assembly code
already called, so replacing the early low-detail proxies with the derived
geometry moved no launcher datum.

Placement contract shared by every function here:

* the derived solid carries the measured functional axis on the local origin
  (X = 0, Z = 0) and an axial datum from ``config/t06_vendor_derivation.json``;
* an argument that names a position is the world position of *that datum*,
  never of the part bounding box, so two purchased parts that must stay coaxial
  simply receive the same X/Z.

``official_shape`` is kept for audit work only: it returns every solid of the
supplier assembly and is never the working model.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import cadquery as cq

from t06_vendor_solids import (
    CAD_FILES,
    derived,
    facts,
    from_face,
    placed,
    policy_for,
    solid_counts,
    summary,
)

__all__ = [
    "CAD_FILES",
    "official_shape",
    "bbox_center",
    "centered_y_axis_part",
    "facts",
    "sonic_hub",
    "motor_with_output_tip",
    "servo_with_output_face",
    "solid_counts",
    "summary",
]

ROOT = Path(__file__).resolve().parents[1]

MOTOR_SKU = "5203-2402-0003"
SONIC_HUB_SKU = "1309-0016-4008"
SERVO_SKUS = ("2000-0025-0002", "2000-0025-0003")


@lru_cache(maxsize=None)
def official_shape(sku: str, largest_solid_only: bool = False) -> cq.Shape:
    """Return the supplier geometry as a compound, preserving all solids."""
    path = CAD_FILES[sku]
    if not path.is_file():
        raise FileNotFoundError(f"Missing official CAD for {sku}: {path}")
    imported = cq.importers.importStep(str(path))
    solids = []
    for value in imported.vals():
        solids.extend(value.Solids())
    if not solids:
        raise ValueError(f"Official CAD for {sku} contains no solids: {path}")
    if largest_solid_only:
        return max(solids, key=lambda solid: solid.Volume())
    return cq.Compound.makeCompound(solids)


def bbox_center(shape: cq.Shape) -> tuple[float, float, float]:
    bb = shape.BoundingBox()
    return ((bb.xmin + bb.xmax) / 2, (bb.ymin + bb.ymax) / 2, (bb.zmin + bb.zmax) / 2)


def centered_y_axis_part(sku: str, center, *, largest_solid_only: bool = False) -> cq.Shape:
    """Derived working model of ``sku`` with its measured datum on ``center``.

    ``largest_solid_only`` is kept for call-site compatibility.  Which supplier
    solids survive into the working model is a property of
    ``config/t06_vendor_derivation.json`` (``keep``), so the flag is checked
    against that policy rather than silently changing the shape.
    """
    keep = policy_for(sku).get("keep")
    if largest_solid_only and keep != "largest_solid":
        raise ValueError(
            f"{sku}: caller asked for largest_solid_only but the derivation policy "
            f"has keep={keep!r}. Record the change in "
            f"config/t06_vendor_derivation.json instead of the call site."
        )
    return placed(sku, center)


def sonic_hub(center) -> cq.Shape:
    """Whole 1309-0016-4008 Sonic Hub with its bore axis on the local origin."""
    return placed(SONIC_HUB_SKU, center)


def motor_with_output_tip(center_xz, output_tip_y: float) -> cq.Shape:
    """Place the 5203-2402-0003 gearmotor with its output shaft tip on ``output_tip_y``.

    The derivation puts the gearmotor axis on the local origin and takes the
    output-shaft tip as the axial datum, so the tip is the maximum-Y face.
    """
    return from_face(MOTOR_SKU, center_xz, output_tip_y, 1)


def servo_with_output_face(
    sku: str,
    center_xz,
    output_face_y: float,
    output_direction: int,
) -> cq.Shape:
    """Place a goBILDA 25T servo with its spline pointing along ``output_direction``.

    The spline tip is the extreme face on the output side and lands on
    ``output_face_y``; the spline axis lands on ``center_xz``.  ``output_direction``
    is +1 when the spline points toward +Y and -1 when it points toward -Y.

    The derived servo keeps the supplier orientation, so its spline sits on +Y.
    A servo that has to drive toward -Y is turned end for end about the X axis:
    that leaves the 54.3 mm mounting-flange direction unchanged and mirrors only
    the 20.15 mm case thickness.
    """
    if output_direction not in (-1, 1):
        raise ValueError("output_direction must be -1 or +1")
    if sku not in SERVO_SKUS:
        raise KeyError(f"No derived servo working model is defined for {sku}")
    body = derived(sku)
    if output_direction < 0:
        body = body.rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 180.0)
    bounding = body.BoundingBox()
    edge = bounding.ymax if output_direction > 0 else bounding.ymin
    return body.translate(cq.Vector(center_xz[0], output_face_y - edge, center_xz[1]))
