"""Load, inspect, and simplify the official goBILDA CAD used by T06.

The downloaded STEP files retain their supplier coordinate systems.  This
module retains a loader for audit work, but the launcher deliberately uses one
connected solid per purchased SKU.  Those solids use dimensions measured from
the official CAD and avoid expanding motors, servos, bearings, and hardware
into dozens of assembly-tree bodies.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[1]
VENDOR_ROOT = ROOT / "references" / "vendor" / "gobilda" / "t06" / "step"

CAD_FILES = {
    "1309-0016-4008": VENDOR_ROOT / "1309-0016-4008" / "1309-0016-4008 assembly.STEP",
    "1401-0043-0036": VENDOR_ROOT / "1401-0043-0036" / "1401-0043-0036 assembly.STEP",
    "1611-0514-4008": VENDOR_ROOT / "1611-0514-4008" / "1611-0514-4008.STEP",
    "1802-0043-0001": VENDOR_ROOT / "1802-0043-0001" / "1802-0043-0001 assembly.STEP",
    "1908-0025-0032": VENDOR_ROOT / "1908-0025-0032" / "1908-0025-0032.STEP",
    "2000-0025-0002": VENDOR_ROOT / "2000-0025-0002" / "2000-0025-0002.step",
    "2000-0025-0003": VENDOR_ROOT / "2000-0025-0003" / "2000-0025-0003.step",
    "2106-4008-1680": VENDOR_ROOT / "2106-4008-1680" / "2106-4008-1680 assembly.STEP",
    "2106-4008-1920": VENDOR_ROOT / "2106-4008-1920" / "2106-4008-1920 assembly.STEP",
    "3613-0014-0096": VENDOR_ROOT / "3613-0014-0096" / "3613-0014-0096.step",
    "4001-0025-4008": VENDOR_ROOT / "4001-0025-4008" / "4001-0025-4008 assembly.STEP",
    "4007-4008-4008": VENDOR_ROOT / "4007-4008-4008" / "4007-4008-4008 assembly.STEP",
    "5203-2402-0003": VENDOR_ROOT / "5203-2402-0003" / "5203-2402-0003 assembly" / "5203-2402-0003 assembly.STEP",
}


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


def _box(l: float, w: float, h: float, center: tuple[float, float, float]) -> cq.Shape:
    return cq.Workplane("XY").box(l, w, h, centered=(True, True, True)).translate(center).val()


def _cyl_y(radius: float, length: float, center: tuple[float, float, float]) -> cq.Shape:
    x, y, z = center
    return cq.Solid.makeCylinder(radius, length, cq.Vector(x, y - length / 2, z), cq.Vector(0, 1, 0))


def _gecko_one_solid(center: tuple[float, float, float]) -> cq.Shape:
    x, y, z = center
    tread = _cyl_y(48, 24, center).cut(_cyl_y(40, 26, center))
    core = _cyl_y(15, 24, center).cut(_cyl_y(7.1, 26, center))
    wheel = tread.fuse(core)
    for angle in range(0, 360, 30):
        spoke = _box(28, 21, 5.5, (x + 27, y, z)).rotate(center, (x, y + 1, z), angle)
        wheel = wheel.fuse(spoke)
    return wheel.clean()


def _shaft_one_solid(length: float, center: tuple[float, float, float]) -> cq.Shape:
    x, y, z = center
    shaft = _cyl_y(4, length, center)
    clip_y = y - length / 2 + 4.0
    return shaft.fuse(_cyl_y(6.15, 1.2, (x, clip_y, z))).clean()


def centered_y_axis_part(sku: str, center: tuple[float, float, float], *, largest_solid_only: bool = False) -> cq.Shape:
    """Create one connected validation/assembly solid from official CAD dimensions."""
    x, y, z = center
    if sku == "3613-0014-0096":
        return _gecko_one_solid(center)
    if sku == "2106-4008-1680":
        return _shaft_one_solid(168.0, center)
    if sku == "2106-4008-1920":
        return _shaft_one_solid(192.0, center)
    if sku == "1611-0514-4008":
        bearing = _cyl_y(7.0, 5.0, center).fuse(_cyl_y(7.5, 1.0, (x, y - 2.0, z)))
        return bearing.cut(_cyl_y(4.1, 7.0, center)).clean()
    if sku == "1401-0043-0036":
        clamp = _box(43.0, 8.0, 49.0, center).cut(_cyl_y(18.1, 10.0, center))
        return clamp.cut(_box(4.0, 10.0, 13.0, (x, y, z + 24.5))).clean()
    if sku == "4007-4008-4008":
        return _cyl_y(20.495 / 2, 21.0, center).cut(_cyl_y(4.1, 23.0, center)).clean()
    if sku == "1802-0043-0001":
        frame = _box(62.75, 6.0, 43.0, center)
        return frame.cut(_box(43.0, 8.0, 25.0, center)).clean()
    if sku == "1908-0025-0032":
        return _cyl_y(15.99, 8.0, center).cut(_cyl_y(3.0, 10.0, center)).clean()
    if sku == "4001-0025-4008":
        return _cyl_y(16.531 / 2, 17.0, center).cut(_cyl_y(4.1, 19.0, center)).clean()
    raise KeyError(f"No one-solid T06 representation is defined for {sku}")


def sonic_hub(center: tuple[float, float, float]) -> cq.Shape:
    """One-solid hub body using the official 32 mm diameter and 10 mm width."""
    return _cyl_y(16.0, 10.0, center).cut(_cyl_y(4.1, 12.0, center)).clean()


def motor_with_output_tip(center_xz: tuple[float, float], output_tip_y: float) -> cq.Shape:
    """One connected motor solid spanning the official 131.17 mm CAD length."""
    cx, cz = center_xz
    shaft_length = 24.0
    body_length = 131.17 - shaft_length
    body = _cyl_y(18.75, body_length, (cx, output_tip_y - shaft_length - body_length / 2, cz))
    shaft = _cyl_y(4.0, shaft_length + 0.5, (cx, output_tip_y - shaft_length / 2 - 0.25, cz))
    return body.fuse(shaft).clean()


def servo_with_output_face(
    sku: str,
    center_xz: tuple[float, float],
    output_face_y: float,
    output_direction: int,
) -> cq.Shape:
    """Place a standard servo with its spline axis on Y.

    output_direction is +1 when the spline points toward +Y and -1 when it
    points toward -Y.  The extreme supplier-CAD face is used as a repeatable
    packaging datum; spline engagement remains a physical-verification item.
    """
    if output_direction not in (-1, 1):
        raise ValueError("output_direction must be -1 or +1")
    if sku not in ("2000-0025-0002", "2000-0025-0003"):
        raise KeyError(f"No one-solid servo representation is defined for {sku}")
    cx, cz = center_xz
    length_y = 44.1
    center_y = output_face_y - output_direction * length_y / 2
    return _box(54.3, length_y, 20.15, (cx, center_y, cz))

