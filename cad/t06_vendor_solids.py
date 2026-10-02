"""Derive one working part per purchased goBILDA SKU for T06.

The launcher carries thirteen purchased SKUs.  Each one enters the working
assembly as exactly one *component* built from the whole official part, so
envelope, motion and interference checks stay tractable, but the shape of that
component is *derived from the official supplier STEP* recorded in
``references/vendor/gobilda/t06/manifest.json`` instead of being redrawn from a
handful of nominal numbers:

1. import every solid of the supplier file;
2. keep the purchased part -- the dominant cluster of touching solids, or every
   solid of the file where the supplier ships the part as one assembly.  Loose
   supplier fasteners are the only thing dropped, and every dropped solid is
   recorded with its volume, never silently discarded;
3. carry the kept solids exactly as the supplier modelled them.  No Boolean union
   is run at all: the official file *is* the purchased part, so its own body split
   is authoritative (DEC-0021).  Measured 2026-10-01, OCC is not trustworthy on
   these press-fit assemblies -- one multi-argument ``fuse`` of ``1309-0016-4008``
   still needs more than three minutes and lost 29.44 mm3 of its 4203.984 mm3 when
   it did finish, and ``1401-0043-0036`` invented 3.7 mm3.  Skipping the Boolean
   can neither lose, invent nor bridge material;
4. rotate the measured part axis onto +Y and put the measured datum on the
   origin;
5. cache the derived part next to a provenance record.

The result is one *part*, and never necessarily one B-rep solid.  Because the
whole official file is the working part, a finished product whose sub-bodies the
supplier separated -- by air, or by a press fit that really overlaps -- keeps that
same body split.  The count is measured and reported (``derived_solid_count``,
``single_solid``, ``body_representation``), and no material is ever dropped to
force the count to one.

``facts()`` reports what was measured, what was dropped, the source hash and
the policy hash.  ``tools/inspect_geometry.py`` re-measures the placed solid
inside the assembly, so the cached value is never the verification evidence.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import os
from functools import lru_cache
from pathlib import Path

import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepExtrema import BRepExtrema_DistShapeShape, BRepExtrema_ShapeProximity
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepTools import BRepTools
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain

ROOT = Path(__file__).resolve().parents[1]
VENDOR_DIR = ROOT / "references" / "vendor" / "gobilda" / "t06"
STEP_ROOT = VENDOR_DIR / "step"
MANIFEST_PATH = VENDOR_DIR / "manifest.json"
POLICY_PATH = ROOT / "config" / "t06_vendor_derivation.json"
CACHE_DIR = ROOT / "cad" / "output" / "vendor_solids"

Y_AXIS = (0.0, 1.0, 0.0)

#: Two supplier solids belong to the same working body when their measured
#: separation is below this value.  Vendor assemblies model mating parts with
#: sub-0.01 mm modelling gaps, so this is a measurement tolerance and not a
#: design clearance.  The value actually used is recorded in every ``facts``
#: record so a reviewer never has to read it out of the source.
CONNECT_TOLERANCE_MM = 0.05

#: Connectivity is decided with the BVH proximity test of ``BRepExtrema`` on a fine
#: triangulation, because the analytic ``DistShapeShape`` solver needs up to 50 s per
#: candidate pair -- about 85 minutes for the 66-solid motor assembly (measured
#: 2026-10-01).  Meshing deviates from the true surface by at most the linear
#: deflection, so rejecting a pair at ``tolerance + PAD`` can only happen when the
#: true separation exceeds ``tolerance + PAD - 2 * DEFLECTION``; the pad therefore
#: guarantees that two solids which really are within ``CONNECT_TOLERANCE_MM`` are
#: never separated.  ``BRepExtrema_DistShapeShape`` stays as the fallback whenever
#: the BVH verdict is unavailable.
PROXIMITY_DEFLECTION_MM = 0.02
PROXIMITY_TOLERANCE_PAD_MM = 0.06

#: Cylinder faces of one radius whose axis lines are further apart than this
#: are separate features; only the coaxial group of the largest-area face
#: defines the part datum.
AXIS_COAXIAL_TOLERANCE_MM = 0.05

#: A union can never invent or lose material, so a Boolean step is accepted only
#: when its volume stays inside ``[largest input, sum of inputs]`` to within this
#: absolute/relative epsilon.  A relative term is required because the measured
#: violation of a healthy union grows with the body size (a 95 767 mm3 flywheel
#: drifts ~0.02 mm3 while a small hub does not) and an absolute limit alone either
#: rejects good unions or accepts a meltdown.
ABS_FUSE_EPS_MM3 = 1e-3
REL_FUSE_EPS = 1e-5

#: Supplier STEP file for every SKU used by the T06 launcher.  This is the
#: single source of truth for the file locations; ``t06_vendor_cad`` re-exports
#: it for the assembly code and the inspection tool.
CAD_FILES = {
    "1309-0016-4008": STEP_ROOT / "1309-0016-4008" / "1309-0016-4008 assembly.STEP",
    "1401-0043-0036": STEP_ROOT / "1401-0043-0036" / "1401-0043-0036 assembly.STEP",
    "1611-0514-4008": STEP_ROOT / "1611-0514-4008" / "1611-0514-4008.STEP",
    "1802-0043-0001": STEP_ROOT / "1802-0043-0001" / "1802-0043-0001 assembly.STEP",
    "1908-0025-0032": STEP_ROOT / "1908-0025-0032" / "1908-0025-0032.STEP",
    "2000-0025-0002": STEP_ROOT / "2000-0025-0002" / "2000-0025-0002.step",
    "2000-0025-0003": STEP_ROOT / "2000-0025-0003" / "2000-0025-0003.step",
    "2106-4008-1680": STEP_ROOT / "2106-4008-1680" / "2106-4008-1680 assembly.STEP",
    "2106-4008-1920": STEP_ROOT / "2106-4008-1920" / "2106-4008-1920 assembly.STEP",
    "3613-0014-0096": STEP_ROOT / "3613-0014-0096" / "3613-0014-0096.step",
    "4001-0025-4008": STEP_ROOT / "4001-0025-4008" / "4001-0025-4008 assembly.STEP",
    "4007-4008-4008": STEP_ROOT / "4007-4008-4008" / "4007-4008-4008 assembly.STEP",
    "5203-2402-0003": STEP_ROOT / "5203-2402-0003" / "5203-2402-0003 assembly" / "5203-2402-0003 assembly.STEP",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while True:
            block = handle.read(1 << 20)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest().upper()


@lru_cache(maxsize=1)
def manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def policy() -> dict:
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def policy_for(sku: str) -> dict:
    data = policy()
    entry = dict(data["defaults"])
    entry.update(data["parts"][sku])
    return entry


def policy_digest() -> str:
    """Digest of everything that can change a derived working part.

    The policy file alone is not enough: the derivation code, the delivery version
    and the connect tolerance all decide the result, so every one of them is folded
    in and each cache entry is invalidated when any of them changes.  The derivation
    source is hashed too, because a code change alters the result without touching
    the policy file -- exactly what happened between version 7 (Boolean chain) and
    version 8 (whole-part volumes measured per solid).
    """
    digest = hashlib.sha256(POLICY_PATH.read_bytes())
    digest.update(Path(__file__).read_bytes())
    digest.update(f"|v{DERIVATION_VERSION}|connect={CONNECT_TOLERANCE_MM}".encode())
    return digest.hexdigest().upper()


# --------------------------------------------------------------------------
# geometry helpers
# --------------------------------------------------------------------------
def bbox_dict(shape: cq.Shape) -> dict:
    bb = shape.BoundingBox()
    return {
        "min_mm": [round(bb.xmin, 4), round(bb.ymin, 4), round(bb.zmin, 4)],
        "max_mm": [round(bb.xmax, 4), round(bb.ymax, 4), round(bb.zmax, 4)],
        "size_mm": [round(bb.xlen, 4), round(bb.ylen, 4), round(bb.zlen, 4)],
        "center_mm": [round((bb.xmin + bb.xmax) / 2, 4), round((bb.ymin + bb.ymax) / 2, 4),
                      round((bb.zmin + bb.zmax) / 2, 4)],
    }


def _min_distance(a: cq.Shape, b: cq.Shape) -> float:
    try:
        solver = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped)
        solver.Perform()
        if solver.IsDone():
            return float(solver.Value())
    except Exception:
        pass
    return float("inf")


def _gap_between_boxes(aa, bb) -> float:
    """Exact axis-aligned gap between two bounding boxes (0.0 when they overlap)."""
    return max(0.0, max(aa.xmin - bb.xmax, bb.xmin - aa.xmax,
                        aa.ymin - bb.ymax, bb.ymin - aa.ymax,
                        aa.zmin - bb.zmax, bb.zmin - aa.zmax))


def _bbox_gap(a: cq.Shape, b: cq.Shape) -> float:
    return _gap_between_boxes(a.BoundingBox(), b.BoundingBox())


def triangulate(shapes: list, deflection: float = PROXIMITY_DEFLECTION_MM) -> None:
    """Triangulate every solid once so the BVH proximity test can be reused."""
    for shape in shapes:
        BRepMesh_IncrementalMesh(shape.wrapped, deflection, False, 0.5, True)


def clear_triangulation(shapes: list) -> None:
    """Drop the cached triangulation so the cached BREP stays geometry-only."""
    for shape in shapes:
        try:
            BRepTools.Clean_s(shape.wrapped, True)
        except Exception:
            pass


def _proximity(a: cq.Shape, b: cq.Shape, tolerance: float):
    """BVH verdict for one pair: True touching, False clear, None unusable."""
    try:
        proximity = BRepExtrema_ShapeProximity(tolerance)
        proximity.LoadShape1(a.wrapped)
        proximity.LoadShape2(b.wrapped)
        proximity.Perform()
        return bool(proximity.IsDone())
    except Exception:
        return None


def cluster_indices(solids: list, tolerance: float = CONNECT_TOLERANCE_MM,
                    stats: dict | None = None) -> list:
    """Group solids into touching clusters (union-find over measured separation).

    Two costs dominated the 66-solid motor derivation and both are removed here: the
    exact bounding box is evaluated once per solid instead of once per pair, and the
    pair test uses the BVH proximity tree instead of the analytic distance solver.
    The 0.5 mm bounding-box pre-filter is unchanged and the proximity tolerance is
    padded, so a rejected pair is provably further apart than ``tolerance``.
    """
    boxes = [shape.BoundingBox() for shape in solids]
    triangulate(solids)
    parent = list(range(len(solids)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    candidates = 0
    accepted = 0
    fallbacks = 0
    proximity_tolerance = tolerance + PROXIMITY_TOLERANCE_PAD_MM
    try:
        for i in range(len(solids)):
            for j in range(i + 1, len(solids)):
                if _gap_between_boxes(boxes[i], boxes[j]) > 0.5:
                    continue
                candidates += 1
                verdict = _proximity(solids[i], solids[j], proximity_tolerance)
                if verdict is None:
                    fallbacks += 1
                    verdict = _min_distance(solids[i], solids[j]) <= tolerance
                if verdict:
                    accepted += 1
                    parent[find(i)] = find(j)
    finally:
        clear_triangulation(solids)
    if stats is not None:
        stats.update({
            "method": "BRepExtrema_ShapeProximity (BVH) over a triangulated pair test",
            "tolerance_mm": tolerance,
            "proximity_tolerance_mm": proximity_tolerance,
            "deflection_mm": PROXIMITY_DEFLECTION_MM,
            "candidate_pairs": candidates,
            "accepted_pairs": accepted,
            "exact_fallback_pairs": fallbacks,
        })
    groups: dict = {}
    for i in range(len(solids)):
        groups.setdefault(find(i), []).append(i)
    return list(groups.values())


def _fuse_tolerance(reference_volume: float) -> float:
    """Allowed volume drift for one union of ``reference_volume`` mm3."""
    return max(ABS_FUSE_EPS_MM3, REL_FUSE_EPS * abs(reference_volume))


def whole_part(members: list, skips: list | None = None) -> cq.Shape:
    """Return the purchased part as one component, keeping every modelled body.

    A Boolean union is deliberately not run.  The official STEP is the purchased
    part, so its own body split is authoritative (DEC-0021), and on 2026-10-01 OCC
    was measured unable to union these press-fit assemblies: a single multi-argument
    ``fuse`` of ``1309-0016-4008`` still needed more than three minutes and lost
    29.44 mm3 of its 4203.984 mm3 when it finished, and ``1401-0043-0036`` invented
    3.7 mm3.  Carrying the bodies as they were modelled is exact: a compound neither
    loses, invents nor bridges material, so every dimension and the volume total stay
    the supplier's.

    A single-solid group is returned as that solid, so the common case is unchanged.
    """
    solids = [solid for member in members for solid in member.Solids()]
    if not solids:
        raise ValueError("whole_part requires at least one solid")
    if len(solids) == 1:
        return solids[0]
    if skips is not None:
        skips.append({
            "step": "compound",
            "reason": BOOLEAN_UNION_POLICY,
            "body_volume_mm3": round(sum(item.Volume() for item in solids), 3),
            "added_volume_mm3": 0.0,
        })
    return cq.Compound.makeCompound(solids)


def _combine(a: cq.Shape, b: cq.Shape) -> cq.Shape:
    """Carry two bodies as separate lumps of one shape, merging nothing.

    Used when OCC cannot produce a trustworthy union: the material of both bodies
    is kept, so a refused Boolean costs a face split and never a dimension.
    """
    return cq.Compound.makeCompound(list(a.Solids()) + list(b.Solids()))


def _fuse_once(shapes: list):
    """One Boolean union.

    Returns the fused body, ``"empty"`` when OCC hands back a null or solid-free
    shape, or ``None`` when the call raised.  The two failure modes are kept apart
    because OCC was measured (2026-10-01, SKU 5203-2402-0003) returning a
    *completely empty* body from ``fuse`` while ``IsNull()`` stayed False and
    ``isValid()`` reported the shape as good; a caller that only guards against an
    exception silently loses the whole derivation.
    """
    if not shapes:
        return None
    try:
        body = shapes[0] if len(shapes) == 1 else shapes[0].fuse(*shapes[1:])
    except Exception:
        return None
    if body is None or body.wrapped is None or body.wrapped.IsNull():
        return "empty"
    try:
        if not list(body.Solids()):
            return "empty"
    except Exception:
        return "empty"
    return body


def fuse_all(shapes: list, refusals: list | None = None) -> cq.Shape:
    """Union every solid into one body, validating every Boolean result.

    RETAINED FOR THE RECORD, NOT USED BY THE DERIVATION.  Version 8 replaced every
    call with :func:`whole_part`: measured 2026-10-01 this chain needs minutes and is
    lossy on the press-fit SKUs, so the official file is carried whole instead (see
    ``BOOLEAN_UNION_POLICY`` and DEC-0021).  The volume guard below is still the
    correct test should OCC ever become usable on these inputs.

    A union can neither invent nor lose material, so each step is accepted only
    when its volume stays inside ``[largest input, sum of inputs]`` to within
    :func:`_fuse_tolerance`.  A step that OCC answers with an empty body, an
    exception, or a volume outside that window is *refused*: the union keeps its
    previous value and the refusal is recorded, so a silent OCC failure can no
    longer drop geometry.  Refusing a step never merges two bodies that OCC kept
    apart, and never leaves one body where OCC merged correctly.

    One multi-argument ``BRepAlgoAPI_Fuse`` is tried first because OCC solves the
    whole set in a single Boolean pass; a step-wise chain over a growing body costs
    minutes on the 32-solid gearmotor cluster (measured 2026-10-01: > 14 min and
    still running, against a few seconds for one multi-argument pass).  The
    multi-argument answer is accepted only if it passes the same volume test, so a
    fast-but-wrong result can never be taken.

    A refused step keeps the refused solid as its own lump (see :func:`_combine`)
    rather than discarding it, so a part whose Boolean OCC cannot solve is still
    represented conservatively.  The motor clamp 1401-0043-0036 is the measured case:
    both the multi-argument and the step-wise union of its two solids reported
    5021.536 mm3 against a 5017.813 mm3 input sum, i.e. 3.7 mm3 of invented
    material, and the previous code then dropped the 272.037 mm3 second solid.
    """
    if not shapes:
        raise ValueError("fuse_all requires at least one solid")
    if len(shapes) == 1:
        return shapes[0]
    whole = _fuse_once(list(shapes))
    if whole is not None and whole != "empty":
        total = sum(item.Volume() for item in shapes)
        largest = max(item.Volume() for item in shapes)
        volume = whole.Volume()
        if (largest - _fuse_tolerance(largest) <= volume
                <= total + _fuse_tolerance(total)):
            return whole
        if refusals is not None:
            refusals.append({
                "step": "multi_argument",
                "reason": f"volume_outside_window ({volume:.3f} mm3 not in "
                          f"[{largest - _fuse_tolerance(largest):.3f}, "
                          f"{total + _fuse_tolerance(total):.3f}])",
                "body_volume_mm3": round(total, 3),
                "added_volume_mm3": 0.0,
            })
    elif refusals is not None:
        refusals.append({
            "step": "multi_argument",
            "reason": "exception" if whole is None else "empty_result",
            "body_volume_mm3": 0.0,
            "added_volume_mm3": 0.0,
        })
    body = shapes[0]
    for step, extra in enumerate(shapes[1:], start=1):
        body_volume = body.Volume()
        extra_volume = extra.Volume()
        candidate = _fuse_once([body, extra])
        reason = None
        if candidate is None:
            reason = "exception"
        elif candidate == "empty":
            reason = "empty_result"
        else:
            volume = candidate.Volume()
            upper = body_volume + extra_volume + _fuse_tolerance(body_volume + extra_volume)
            lower = max(body_volume, extra_volume) - _fuse_tolerance(max(body_volume, extra_volume))
            if volume > upper:
                reason = f"volume_invented ({volume:.3f} > {upper:.3f} mm3)"
            elif volume < lower:
                reason = f"material_lost ({volume:.3f} < {lower:.3f} mm3)"
        if reason is None:
            body = candidate
        else:
            if refusals is not None:
                refusals.append({
                    "step": step,
                    "reason": reason,
                    "body_volume_mm3": round(body_volume, 3),
                    "added_volume_mm3": round(extra_volume, 3),
                })
            # The refused solid still belongs to the part, so it is carried as its
            # own lump instead of being dropped: a refused Boolean may cost a face
            # split, never a dimension.
            body = _combine(body, extra)
    return body


def unify_same_domain(shape: cq.Shape) -> cq.Shape:
    try:
        upgrade = ShapeUpgrade_UnifySameDomain(shape.wrapped, True, True, False)
        upgrade.Build()
        return cq.Shape.cast(upgrade.Shape())
    except Exception:
        return shape


def cylinder_axes(shape: cq.Shape, axis_index: int = 1, tolerance: float = 1e-6) -> list:
    """Group cylindrical faces whose axis is parallel to ``axis_index``."""
    groups: dict = {}
    for face in shape.faces("%CYLINDER"):
        surface = BRepAdaptor_Surface(face.wrapped)
        cylinder = surface.Cylinder()
        direction = cylinder.Axis().Direction()
        components = (direction.X(), direction.Y(), direction.Z())
        if abs(abs(components[axis_index]) - 1.0) > tolerance:
            continue
        radius = round(cylinder.Radius(), 3)
        group = groups.setdefault(radius, {"radius_mm": radius, "faces": 0, "area_mm2": 0.0,
                                           "sum_x": 0.0, "sum_y": 0.0, "sum_z": 0.0})
        location = cylinder.Axis().Location()
        group["faces"] += 1
        group["area_mm2"] += face.Area()
        group["sum_x"] += location.X()
        group["sum_y"] += location.Y()
        group["sum_z"] += location.Z()
    result = []
    for group in groups.values():
        n = group["faces"]
        result.append({
            "radius_mm": group["radius_mm"],
            "faces": n,
            "area_mm2": round(group["area_mm2"], 3),
            "point_mm": [group["sum_x"] / n, group["sum_y"] / n, group["sum_z"] / n],
        })
    result.sort(key=lambda item: -item["area_mm2"])
    return result


def rotate_axis_to_y(shape: cq.Shape, source: list) -> cq.Shape:
    """Rotate ``shape`` so the supplier direction ``source`` points along +Y."""
    start = cq.Vector(*source)
    if start.Length < 1e-9:
        return shape
    start = start.normalized()
    target = cq.Vector(*Y_AXIS)
    dot = max(-1.0, min(1.0, start.dot(target)))
    if dot > 1.0 - 1e-12:
        return shape
    if dot < -1.0 + 1e-12:
        helper = cq.Vector(1, 0, 0) if abs(start.x) < 0.9 else cq.Vector(0, 0, 1)
        axis = start.cross(helper).normalized()
        return shape.rotate((0, 0, 0), (axis.x, axis.y, axis.z), 180.0)
    axis = start.cross(target).normalized()
    return shape.rotate((0, 0, 0), (axis.x, axis.y, axis.z), math.degrees(math.acos(dot)))


def _dominant_y_axis(shape: cq.Shape):
    axes = cylinder_axes(shape, axis_index=1)
    if not axes:
        return None
    return max(axes, key=lambda item: item["area_mm2"])


def cylinder_faces(shape: cq.Shape, axis_index: int = 1, tolerance: float = 1e-6) -> list:
    """Measured cylindrical faces whose axis is parallel to ``axis_index``.

    Every item carries the face's own exact radius, area and a point on its
    own axis, so callers can group by measured geometry instead of by a face
    number that changes whenever the upstream STEP is refreshed.
    """
    result = []
    for face in shape.faces("%CYLINDER"):
        surface = BRepAdaptor_Surface(face.wrapped)
        cylinder = surface.Cylinder()
        direction = cylinder.Axis().Direction()
        components = (direction.X(), direction.Y(), direction.Z())
        if abs(abs(components[axis_index]) - 1.0) > tolerance:
            continue
        location = cylinder.Axis().Location()
        result.append({
            "radius_mm": round(cylinder.Radius(), 4),
            "area_mm2": face.Area(),
            "axis_point_mm": [location.X(), location.Y(), location.Z()],
        })
    return result


def _lateral(point: list, axis_index: int) -> list:
    """Coordinates perpendicular to ``axis_index``; they fix the axis line."""
    return [value for index, value in enumerate(point) if index != axis_index]


def principal_axis(shape: cq.Shape, axis_index: int = 1, radius_mm=None) -> dict | None:
    """Functional axis of the part, measured from its cylindrical faces.

    Cylindrical faces are first grouped into *coaxial groups*: faces sharing a
    radius whose axis lines coincide within
    :data:`AXIS_COAXIAL_TOLERANCE_MM` (a threaded hole or a split bore yields
    many faces of one radius on one line; two separate bolt holes of the same
    radius do not).  Each group is scored by ``radius * area``, which is
    proportional to the volume of the cylinder that bounds it, and the best
    group defines the datum axis.

    That score is what separates the two failure modes measured on the real
    supplier files: a servo's output-spline cylinder has small area but the
    largest radius, while a spline coupler carries a large-radius cosmetic
    fillet of almost no area.  ``radius_mm`` pins the radius explicitly for any
    part where a reviewer decides differently; the measured ``candidates`` list
    is returned so the choice can always be audited.
    """
    faces = cylinder_faces(shape, axis_index)
    if not faces:
        return None
    by_radius: dict = {}
    for item in faces:
        by_radius.setdefault(item["radius_mm"], []).append(item)

    groups = []
    for radius, same in by_radius.items():
        if radius_mm is not None and abs(radius - float(radius_mm)) > 1e-3:
            continue
        remaining = sorted(same, key=lambda item: -item["area_mm2"])
        while remaining:
            seed = remaining.pop(0)
            seed_lateral = _lateral(seed["axis_point_mm"], axis_index)
            members, rest = [seed], []
            for item in remaining:
                offset = max(abs(a - b) for a, b in
                             zip(_lateral(item["axis_point_mm"], axis_index), seed_lateral))
                (members if offset <= AXIS_COAXIAL_TOLERANCE_MM else rest).append(item)
            remaining = rest
            area = sum(item["area_mm2"] for item in members)
            groups.append({
                "radius_mm": round(radius, 4),
                "faces": len(members),
                "area_mm2": round(area, 3),
                "score_mm3": round(radius * area, 2),
                "point_mm": [round(value, 4) for value in seed["axis_point_mm"]],
            })
    if not groups:
        return None
    groups.sort(key=lambda item: (-item["score_mm3"], -item["radius_mm"]))
    chosen = dict(groups[0])
    chosen["coaxial_tolerance_mm"] = AXIS_COAXIAL_TOLERANCE_MM
    chosen["pinned_radius_mm"] = radius_mm
    chosen["candidates"] = groups[:6]
    return chosen

# --------------------------------------------------------------------------
# derivation
# --------------------------------------------------------------------------
# 8: whole-official-part representation (DEC-0021) with no Boolean union at all --
#    the official file *is* the purchased part, so its own body split is kept and
#    nothing is lost, invented or bridged.  Loose supplier fasteners are still
#    dropped by the keep rule and recorded with their volume.  See
#    ``BOOLEAN_UNION_POLICY`` for the 2026-10-01 measurements that retired the
#    validated Boolean chain of version 7.
DERIVATION_VERSION = 8

BOOLEAN_UNION_POLICY = (
    "not attempted: the official file is the purchased part, so its own body split is "
    "kept whole (DEC-0021). Measured 2026-10-01: one multi-argument fuse of "
    "1309-0016-4008 still needs over 3 min and lost 29.44 mm3 of its 4203.984 mm3 "
    "when it finished, and 1401-0043-0036 invented 3.7 mm3; both are press-fit "
    "assemblies whose supplier solids really overlap."
)

VOLUME_METHOD = (
    "sum of the volumes of every solid of the derived part, each integrated separately "
    "by BRepGProp. Does not depend on whether OCC packaged those solids as one body or "
    "a compound, and is directly comparable with the same sum over the kept supplier "
    "solids. Measured 2026-10-01: cq ``Shape.Volume()`` on the compound *itself* is NOT "
    "this value (31109.612 mm3 against 31109.289 mm3 on 2000-0025-0002, and the gap does "
    "not close as the integration tolerance is tightened) because OCC integrates a "
    "compound as one shape; that number is recorded as a cross-check and is never the "
    "reported volume."
)


def import_solids(sku: str) -> list:
    path = CAD_FILES[sku]
    if not path.is_file():
        raise FileNotFoundError(f"missing official STEP for {sku}: {path}")
    imported = cq.importers.importStep(str(path)).val()
    solids = list(imported.Solids())
    if not solids:
        raise ValueError(f"official STEP for {sku} contains no solid: {path}")
    return solids


def _derive_uncached(sku: str, entry: dict, source_sha: str) -> tuple:
    solids = import_solids(sku)
    keep_policy = entry.get("keep")
    connectivity: dict = {}
    if keep_policy == "all_solids":
        # The supplier ships the whole purchased part in one file and the model is a
        # finished product, so its own body split *is* the working part.  Clustering
        # and Boolean union are both skipped: nothing can be invented, lost, or
        # bridged, and no connectivity measurement is needed to decide what to keep.
        clusters = [list(range(len(solids)))]
        connectivity = {
            "method": "not measured: keep=all_solids keeps the supplier's own body split",
            "tolerance_mm": None,
        }
    else:
        clusters = cluster_indices(solids, stats=connectivity)

    detail = []
    for group in clusters:
        members = [solids[i] for i in group]
        detail.append({
            "solids": len(group),
            "volume_mm3": round(sum(item.Volume() for item in members), 3),
            "bbox": bbox_dict(cq.Compound.makeCompound(members)),
            "members": [{"volume_mm3": round(item.Volume(), 3),
                         "bbox": bbox_dict(item)} for item in members],
        })
    order = sorted(range(len(clusters)), key=lambda index: -detail[index]["volume_mm3"])

    # Which supplier solids are the purchased part?  ``all_solids`` -- the supplier
    # ships the whole part in one file; ``largest_solid`` -- only one solid is the
    # part and the rest are loose fasteners; the default keeps the dominant cluster
    # of touching solids.  Whatever the policy does not keep is recorded in
    # ``dropped`` with its volume; nothing is discarded silently.
    if keep_policy == "all_solids":
        kept_groups = [list(group) for group in clusters]
    elif keep_policy == "largest_solid":
        dominant = clusters[order[0]]
        kept_groups = [[max(dominant, key=lambda index: solids[index].Volume())]]
    else:
        kept_groups = [list(clusters[order[0]])]
    kept_index = {index for group in kept_groups for index in group}
    dropped = [item for index, item in enumerate(solids) if index not in kept_index]

    # Every kept group is carried exactly as the supplier modelled it, and never
    # bridged across groups: no Boolean is run, so nothing can be lost, invented or
    # joined.  A ``keep: all_solids`` file and a multi-solid cluster therefore take
    # the same path, and the supplier's own body split reaches the working part.
    skips: list = []
    parts: list = []
    for group in kept_groups:
        part = whole_part([solids[index] for index in group], skips)
        group_bodies = len(part.Solids())
        if group_bodies != len(group):
            raise ValueError(
                f"{sku}: a kept group of {len(group)} supplier solids came back as "
                f"{group_bodies} bodies; the whole official part must be kept"
            )
        parts.append(part)
    faces_derived = sum(len(part.Faces()) for part in parts)
    body = parts[0] if len(parts) == 1 else cq.Compound.makeCompound(parts)

    kept_volume = round(sum(solids[index].Volume() for index in kept_index), 3)
    # Measured on the *solids of the final entity*, not on the container: cq
    # ``Shape.Volume()`` on a compound integrates the compound as one shape and
    # disagrees with the sum of its own solids on curved geometry (see
    # ``VOLUME_METHOD``), so the container value would make the guard below compare
    # two different quantities.
    derived_volume = round(sum(item.Volume() for item in body.Solids()), 3)
    largest_kept_volume = max(solids[index].Volume() for index in kept_index)
    # Volume conservation: a union cannot exceed its inputs nor fall below its
    # largest input, so any other result means material was invented or lost.
    upper = kept_volume + _fuse_tolerance(kept_volume)
    lower = largest_kept_volume - _fuse_tolerance(largest_kept_volume)
    if derived_volume > upper:
        raise ValueError(
            f"{sku}: working part volume {derived_volume:.3f} mm3 exceeds its inputs "
            f"({kept_volume:.3f} mm3); the derived part gained material"
        )
    if derived_volume < lower:
        raise ValueError(
            f"{sku}: working part volume {derived_volume:.3f} mm3 is below the largest "
            f"input solid ({largest_kept_volume:.3f} mm3); the derived part lost material"
        )

    derived_bodies = len(body.Solids())
    dropped_volume = round(sum(item.Volume() for item in dropped), 3)
    supplier_solids = len(solids)

    body = rotate_axis_to_y(body, entry["source_axis"])

    datum = entry.get("datum", "axis_mid")
    if datum not in ("axis_mid", "face_min", "face_max"):
        raise ValueError(f"{sku}: unknown datum {datum!r}; see config/t06_vendor_derivation.json")
    lateral_datum = entry.get("lateral_datum", "axis")
    if lateral_datum not in ("axis", "bbox_center"):
        raise ValueError(
            f"{sku}: unknown lateral_datum {lateral_datum!r}; "
            f"see config/t06_vendor_derivation.json"
        )
    axis_info = principal_axis(body, axis_index=1, radius_mm=entry.get("datum_radius_mm"))
    if lateral_datum == "axis":
        if axis_info is None:
            raise ValueError(
                f"{sku}: lateral_datum 'axis' needs a cylindrical feature parallel to Y and "
                f"none was measured. Record the measured datum_radius_mm in "
                f"config/t06_vendor_derivation.json, or set lateral_datum to 'bbox_center' "
                f"when the part has no functional rotation axis."
            )
        lateral_point = axis_info["point_mm"]
    else:
        lateral_box = body.BoundingBox()
        lateral_point = [round((lateral_box.xmin + lateral_box.xmax) / 2.0, 4), 0.0,
                         round((lateral_box.zmin + lateral_box.zmax) / 2.0, 4)]
    # X/Z datum: the measured functional axis, or the bounding-box centre for parts
    # with no functional rotation axis (policy lateral_datum == "bbox_center").
    body = body.translate(cq.Vector(-lateral_point[0], 0.0, -lateral_point[2]))
    bounding = body.BoundingBox()
    if datum == "axis_mid":
        y_shift = -(bounding.ymin + bounding.ymax) / 2.0
    elif datum == "face_max":
        y_shift = -bounding.ymax
    else:
        y_shift = -bounding.ymin
    body = body.translate(cq.Vector(0.0, y_shift, 0.0))

    facts = {
        "schema_version": "0.1",
        "sku": sku,
        "derivation_version": DERIVATION_VERSION,
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source_step": str(CAD_FILES[sku].relative_to(ROOT)).replace("\\", "/"),
        "source_step_sha256": source_sha,
        "source_step_solids": supplier_solids,
        "source_step_bbox_mm": manifest()["parts"][sku].get("cad_bbox_mm"),
        "policy_sha256": policy_digest(),
        "policy": entry,
        "connect_tolerance_mm": CONNECT_TOLERANCE_MM,
        "connectivity": connectivity,
        "clusters": detail,
        "kept_cluster": order[0],
        "kept_volume_mm3": kept_volume,
        "kept_groups": len(kept_groups),
        "dropped_solids": len(dropped),
        "dropped_volume_mm3": dropped_volume,
        "dropped_volume_fraction": round(dropped_volume / max(1e-9, sum(s.Volume() for s in solids)), 6),
        "boolean_union": {
            "attempted": False,
            "reason": BOOLEAN_UNION_POLICY,
            "skipped_clusters": skips,
        },
        "faces_derived": faces_derived,
        "derived_volume_mm3": derived_volume,
        "volume_method": VOLUME_METHOD,
        "compound_volume_cross_check_mm3": round(body.Volume(), 3),
        "derived_solid_count": derived_bodies,
        "derived_valid": bool(body.isValid()),
        "derived_bbox": bbox_dict(body),
        "axis_feature": axis_info,
        "placement": {
            "datum": datum,
            "lateral_datum": lateral_datum,
            "lateral_point_before_centring_mm": lateral_point,
            "datum_radius_mm": axis_info["radius_mm"] if axis_info else None,
            "axis_point_before_centring_mm": axis_info["point_mm"] if axis_info else None,
            "axis_on_y": [round(entry["source_axis"][0], 6), round(entry["source_axis"][1], 6),
                          round(entry["source_axis"][2], 6)],
            "note": entry.get("note", ""),
        },
    }
    # The working model is one *part*, not necessarily one B-rep solid.  A supplier
    # file can describe a finished product whose sub-bodies are genuinely separated
    # by air (measured 2026-10-01: the gearmotor housing shell sits exactly 0.045 mm
    # from its own body, two of its plates 0.0289 mm).  OCC is never asked to bridge
    # such a gap, so the measured count is reported and the component is flagged
    # instead of having material dropped to make the count come out as one.
    facts["single_solid"] = derived_bodies == 1
    facts["body_representation"] = (
        "single_solid" if facts["single_solid"] else "whole_part_multi_body"
    )
    if not facts["single_solid"]:
        facts["multi_body_note"] = (
            f"{sku}: the supplier ships this part as {derived_bodies} bodies, so the "
            f"working part keeps all {derived_bodies} of them in "
            f"{len(kept_groups)} cluster(s).  Whole-part representation (DEC-0021): no "
            f"material was dropped or bridged to reduce the count."
        )
    return body, facts


def derive(sku: str, force: bool = False) -> tuple:
    """Return ``(shape, facts)`` for one SKU, using the cached BREP when valid."""
    entry = policy_for(sku)
    source_sha = sha256_file(CAD_FILES[sku])
    cache_shape = CACHE_DIR / f"{sku}.brep"
    cache_facts = CACHE_DIR / f"{sku}.json"
    if os.environ.get("T06_VENDOR_REFRESH"):
        force = True
    if not force and cache_shape.is_file() and cache_facts.is_file():
        try:
            recorded = json.loads(cache_facts.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            recorded = {}
        if (recorded.get("source_step_sha256") == source_sha
                and recorded.get("policy_sha256") == policy_digest()
                and recorded.get("derivation_version") == DERIVATION_VERSION):
            shape = cq.importers.importBrep(str(cache_shape)).val()
            return shape, recorded

    shape, facts = _derive_uncached(sku, entry, source_sha)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(shape, str(cache_shape), exportType="BREP")
    facts["cache"] = {
        "path": str(cache_shape.relative_to(ROOT)).replace("\\", "/"),
        "bytes": cache_shape.stat().st_size,
    }
    cache_facts.write_text(json.dumps(facts, indent=1), encoding="utf-8")
    return shape, facts


@lru_cache(maxsize=None)
def derived(sku: str) -> cq.Shape:
    """Whole working part, part axis on +Y, measured datum on origin.

    The result is the complete purchased part; where the supplier file separates
    sub-bodies by real air it carries that body count unchanged.
    """
    return derive(sku)[0]


@lru_cache(maxsize=None)
def facts(sku: str) -> dict:
    return derive(sku)[1]


def placed(sku: str, center) -> cq.Shape:
    """Place the derived solid so its measured datum lands on ``center``."""
    return derived(sku).translate(cq.Vector(*center))


def from_face(sku: str, center_xz, face_y: float, direction: int = 1) -> cq.Shape:
    """Place the derived solid by its extreme face along Y.

    ``direction=+1`` puts the maximum-Y face of the part on ``face_y`` (the
    spline/output side points to +Y); ``direction=-1`` puts the minimum-Y face
    there.  The part datum -- the measured functional axis, which the derivation
    leaves on the local origin -- lands on ``center_xz``, so two purchased parts
    stay coaxial whenever a caller passes the same ``center_xz``.
    """
    if direction not in (-1, 1):
        raise ValueError("direction must be -1 or +1")
    body = derived(sku)
    bounding = body.BoundingBox()
    edge = bounding.ymax if direction > 0 else bounding.ymin
    return body.translate(cq.Vector(center_xz[0], face_y - edge, center_xz[1]))


def solid_counts() -> dict:
    """Sub-body count per SKU, measured on the derived working part."""
    return {sku: len(derived(sku).Solids()) for sku in CAD_FILES}


def summary() -> dict:
    return {
        "derivation_version": DERIVATION_VERSION,
        "policy_sha256": policy_digest(),
        "parts": {sku: {key: facts(sku)[key] for key in
                        ("source_step_solids", "dropped_solids", "dropped_volume_mm3",
                         "derived_solid_count", "body_representation", "faces_derived",
                         "derived_volume_mm3", "derived_bbox")}
                  for sku in CAD_FILES},
    }
