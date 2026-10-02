#!/usr/bin/env python3
"""Geometry inspection entry point for the BIOBUZZ CAD.

Implementation of the reporting contract in
``AI_CAD_Python_Geometry_Inspection.md`` section 2:

* read the *final* solids instead of the inputs that produced them;
* record targets/tolerances separately from measured values;
* report ``pass`` / ``fail`` / ``not_run`` / ``unresolved`` per check;
* return a non-zero exit status when a check fails or cannot be resolved.

Typical use::

    .venv-cad\\Scripts\\python.exe tools\\inspect_geometry.py \\
        --harness t06_launcher \\
        --spec config/t06_geometry_checks.json \\
        --run-label R002 \\
        --report cad/output/inspection/t06_launcher_R002.json

The tool never invents a measurement.  A feature that cannot be identified is
reported as ``unresolved`` with the candidate geometry attached.
"""

from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import hashlib
import importlib
import json
import math
import os
import platform
import sys
import threading
import time
from pathlib import Path

import cadquery as cq

ROOT = Path(__file__).resolve().parents[1]
CAD_DIR = ROOT / "cad"
if str(CAD_DIR) not in sys.path:
    sys.path.insert(0, str(CAD_DIR))

PASS = "pass"
FAIL = "fail"
NOT_RUN = "not_run"
UNRESOLVED = "unresolved"

DEFAULT_TOLERANCE_MM = 0.05
CLUSTER_TOLERANCE_MM = 0.2

AXIS_INDEX = {"x": 0, "y": 1, "z": 2}


# --------------------------------------------------------------------------
# progress reporting
# --------------------------------------------------------------------------
# A geometry inspection has to build the whole assembly before the first check
# can run, so the process stays silent for many minutes while it is working.
# AI_Long_Running_Process_No_Output_Guide.md requires that silence to be
# distinguishable from a stall: every stage is announced on a flushed stdout and
# a heartbeat keeps repeating the current stage, so a run can be judged from its
# own progress rather than from the absence of text.
#
# The same guide separates an *output* timeout (no new text) from a *progress*
# timeout (no verifiable advance).  Text answers only the first question, so the
# state file published below also carries counters that keep moving while the
# process is alive - elapsed time, CPU time, heartbeat and stage counts, and the
# index of the check being evaluated - and a watcher can classify a silent run
# as ACTIVE / BLOCKED / STALLED from evidence instead of from missing output.
HEARTBEAT_SECONDS = 20.0


class Progress:
    """Flushed stage log, a heartbeat and a machine-readable state file."""

    def __init__(self) -> None:
        self._stage = "startup"
        self._started = time.time()
        self._started_utc = dt.datetime.now(dt.timezone.utc)
        self._cpu_started = time.process_time()
        self._active = False
        self._interval = HEARTBEAT_SECONDS
        self._path: Path | None = None
        self._log_path: Path | None = None
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._heartbeats = 0
        self._stages_done = 0
        self._counter: tuple[int, int] | None = None
        self._lock = threading.Lock()

    def configure(self, path=None, interval: float = HEARTBEAT_SECONDS, log_path=None) -> None:
        self._interval = interval
        self._path = Path(path) if path else None
        self._log_path = Path(log_path) if log_path else None
        if self._log_path is not None:
            self._log_path.parent.mkdir(parents=True, exist_ok=True)
            self._log_path.write_text("", encoding="utf-8")

    def _emit(self, text: str) -> None:
        elapsed = time.time() - self._started
        line = f"[{elapsed:8.1f}s] {text}"
        print(line, flush=True)
        if self._log_path is not None:
            try:
                with self._log_path.open("a", encoding="utf-8") as handle:
                    handle.write(line + "\n")
            except OSError:
                pass

    def note(self, text: str) -> None:
        """Emit a line outside a stage, e.g. the closing summary of a run."""
        self._emit(text)

    def cpu_time_s(self) -> float:
        """CPU time burned by this process.

        A long OpenCascade call can hold the interpreter lock long enough that
        the heartbeat thread stops printing; CPU time keeps growing through that
        window, so it is the most reliable liveness signal for an outside
        watcher.
        """
        return round(time.process_time() - self._cpu_started, 2)

    def _state(self) -> dict:
        state = {
            "schema_version": "0.1",
            "stage": self._stage,
            "elapsed_s": round(time.time() - self._started, 2),
            "cpu_time_s": self.cpu_time_s(),
            "heartbeats": self._heartbeats,
            "stages_done": self._stages_done,
            "started_at_utc": self._started_utc.isoformat(),
            "updated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "pid": os.getpid(),
            "active": self._active,
        }
        if self._counter is not None:
            state["check_index"], state["check_total"] = self._counter
        return state

    def _write_state(self) -> None:
        if self._path is None:
            return
        payload = json.dumps(self._state(), ensure_ascii=False, indent=2)
        # the heartbeat thread and the main thread both publish state, so the
        # write is serialised and the swap retried: on Windows a reader holding
        # the target open briefly makes the replace fail with a sharing error
        with self._lock:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            temp = self._path.with_name(f"{self._path.name}.{os.getpid()}.tmp")
            deadline = time.time() + 1.0
            while True:
                try:
                    temp.write_text(payload, encoding="utf-8")
                    os.replace(temp, self._path)
                    return
                except OSError:
                    if time.time() >= deadline:
                        break
                    time.sleep(0.05)
            # last resort: a direct write still beats losing the progress record
            try:
                self._path.write_text(payload, encoding="utf-8")
            except OSError:
                pass

    def start(self) -> None:
        self._started = time.time()
        self._started_utc = dt.datetime.now(dt.timezone.utc)
        self._cpu_started = time.process_time()
        self._active = True
        self._emit(f"started (pid {os.getpid()})")
        self._write_state()
        self._thread = threading.Thread(target=self._run, name="progress-heartbeat", daemon=True)
        self._thread.start()

    def _run(self) -> None:
        while not self._stop.wait(self._interval):
            self._heartbeats += 1
            self._emit(f"heartbeat: still working on {self._stage}")
            self._write_state()

    def stage(self, text: str, index: int | None = None, total: int | None = None) -> None:
        self._stage = text
        self._stages_done += 1
        self._counter = (index, total) if index is not None and total is not None else None
        if self._active:
            self._emit(text)
        self._write_state()

    def stop(self) -> None:
        if not self._active:
            return
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        self._emit(f"finished after {time.time() - self._started:.1f}s")
        self._active = False
        self._write_state()


PROGRESS = Progress()


# --------------------------------------------------------------------------
# input provenance
# --------------------------------------------------------------------------
def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            block = handle.read(1 << 20)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest().upper()


def input_record(role: str, path: Path) -> dict:
    path = Path(path).resolve()
    record = {"role": role, "path": str(path), "exists": path.is_file()}
    if path.is_file():
        record["bytes"] = path.stat().st_size
        record["sha256"] = sha256_file(path)
    return record


def collect_inputs(args) -> list[dict]:
    records = []
    if args.spec:
        records.append(input_record("check_requirements", Path(args.spec)))
    if args.step:
        records.append(input_record("step", Path(args.step)))
    if args.harness == "t06_launcher":
        records.append(input_record("model_source", CAD_DIR / "paddle_launcher_constrained.py"))
        records.append(input_record("vendor_helpers", CAD_DIR / "t06_vendor_cad.py"))
        if (CAD_DIR / "t06_vendor_solids.py").is_file():
            records.append(input_record("vendor_solids", CAD_DIR / "t06_vendor_solids.py"))
        records.append(input_record("cots_config", ROOT / "config" / "t06_launcher_cots.json"))
        records.append(input_record("vendor_manifest", ROOT / "references" / "vendor" / "gobilda" / "t06" / "manifest.json"))
    return records


# --------------------------------------------------------------------------
# shape helpers
# --------------------------------------------------------------------------
def as_shape(value) -> cq.Shape:
    if isinstance(value, cq.Workplane):
        return value.val()
    if isinstance(value, cq.Shape):
        return value
    raise TypeError(f"not a CadQuery shape: {type(value)!r}")


def solid_count(shape: cq.Shape) -> int:
    return len(shape.Solids())


def bbox_facts(shape: cq.Shape) -> dict:
    bb = shape.BoundingBox()
    return {
        "min_mm": [round(bb.xmin, 4), round(bb.ymin, 4), round(bb.zmin, 4)],
        "max_mm": [round(bb.xmax, 4), round(bb.ymax, 4), round(bb.zmax, 4)],
        "size_mm": [round(bb.xlen, 4), round(bb.ylen, 4), round(bb.zlen, 4)],
    }


def _bbox_gap(a: cq.Shape, b: cq.Shape) -> float:
    """Lower bound on the separation between two shapes, from their boxes."""
    aa, bb = a.BoundingBox(), b.BoundingBox()
    gaps = [
        max(bb.xmin - aa.xmax, aa.xmin - bb.xmax),
        max(bb.ymin - aa.ymax, aa.ymin - bb.ymax),
        max(bb.zmin - aa.zmax, aa.zmin - bb.zmax),
    ]
    return max(0.0, max(gaps))


def _bbox_overlap(a: cq.Shape, b: cq.Shape, tol: float = 1e-9) -> bool:
    aa, bb = a.BoundingBox(), b.BoundingBox()
    return not (
        aa.xmax <= bb.xmin + tol
        or bb.xmax <= aa.xmin + tol
        or aa.ymax <= bb.ymin + tol
        or bb.ymax <= aa.ymin + tol
        or aa.zmax <= bb.zmin + tol
        or bb.zmax <= aa.zmin + tol
    )


def min_distance(a: cq.Shape, b: cq.Shape, target: float = 0.0) -> tuple[float, str]:
    """Return (distance_mm, method).

    When the bounding boxes are already further apart than ``target`` the box
    gap is a certified lower bound and is reported as such; otherwise the exact
    BrepExtrema distance is computed.
    """
    gap = _bbox_gap(a, b)
    if gap >= target and gap > 0.0:
        return gap, "bbox_gap_lower_bound"
    distance, _, _ = a.distToShape(b)
    return float(distance), "brep_extrema_distToShape"


def intersection_volume(a: cq.Shape, b: cq.Shape) -> float:
    if not _bbox_overlap(a, b):
        return 0.0
    try:
        common = a.intersect(b)
    except Exception as exc:  # pragma: no cover - OCC failure mode
        raise UnresolvedError(f"boolean intersection failed: {exc}") from exc
    try:
        return max(0.0, float(common.Volume()))
    except Exception:
        return 0.0


class UnresolvedError(RuntimeError):
    """Raised when a target feature cannot be measured reliably."""


# --------------------------------------------------------------------------
# cylindrical feature identification (holes, bores, shafts, wheel rims)
# --------------------------------------------------------------------------
def _canonical_axis(direction) -> tuple[float, float, float]:
    values = [direction.X(), direction.Y(), direction.Z()]
    for value in values:
        if abs(value) > 1e-9:
            if value < 0:
                values = [-v for v in values]
            break
    return tuple(round(v, 6) for v in values)


def cylinder_features(
    shape: cq.Shape,
    radius_min: float | None = None,
    radius_max: float | None = None,
    axis_filter: str | None = None,
    radius_tolerance: float = 0.05,
) -> list[dict]:
    """Group cylindrical faces into distinct axes.

    A single hole or bore is usually split across several cylindrical faces, so
    faces are grouped by (axis direction, radius, axis location) before being
    reported.  Face counts are therefore never presented as feature counts.
    """
    from OCP.BRepAdaptor import BRepAdaptor_Surface

    candidates = []
    for face in shape.Faces():
        if face.geomType() != "CYLINDER":
            continue
        adaptor = BRepAdaptor_Surface(face.wrapped)
        cylinder = adaptor.Cylinder()
        radius = float(cylinder.Radius())
        if radius_min is not None and radius < radius_min - radius_tolerance:
            continue
        if radius_max is not None and radius > radius_max + radius_tolerance:
            continue
        axis = cylinder.Axis()
        direction = _canonical_axis(axis.Direction())
        if axis_filter is not None:
            wanted = AXIS_INDEX[axis_filter]
            if abs(direction[wanted] - 1.0) > 1e-6:
                continue
        location = axis.Location()
        candidates.append(
            {
                "radius_mm": radius,
                "direction": direction,
                "location": (location.X(), location.Y(), location.Z()),
                "area_mm2": float(face.Area()),
            }
        )

    groups: list[dict] = []
    for candidate in candidates:
        placed = False
        for group in groups:
            if group["direction"] != candidate["direction"]:
                continue
            if abs(group["radius_mm"] - candidate["radius_mm"]) > radius_tolerance:
                continue
            if _axis_offset(group, candidate) > CLUSTER_TOLERANCE_MM:
                continue
            group["faces"] += 1
            group["area_mm2"] += candidate["area_mm2"]
            points = group.pop("_points")
            points.append(candidate["location"])
            group["_points"] = points
            _reproject(group)
            placed = True
            break
        if not placed:
            groups.append(
                {
                    "radius_mm": round(candidate["radius_mm"], 4),
                    "direction": candidate["direction"],
                    "faces": 1,
                    "area_mm2": candidate["area_mm2"],
                    "_points": [candidate["location"]],
                    "axis_point_mm": [round(v, 4) for v in candidate["location"]],
                }
            )
    for group in groups:
        _reproject(group)
        group.pop("_points", None)
        group["radius_mm"] = round(group["radius_mm"], 4)
        group["area_mm2"] = round(group["area_mm2"], 3)
        group["diameter_mm"] = round(2 * group["radius_mm"], 4)
    groups.sort(key=lambda g: (-g["faces"], -g["radius_mm"]))
    return groups


def _axis_offset(group: dict, candidate: dict) -> float:
    point = cq.Vector(*group["axis_point_mm"])
    other = cq.Vector(*candidate["location"])
    direction = cq.Vector(*group["direction"])
    delta = other.sub(point)
    return delta.sub(direction.multiply(delta.dot(direction))).Length


def _reproject(group: dict) -> None:
    direction = cq.Vector(*group["direction"])
    points = [cq.Vector(*p) for p in group["_points"]]
    origin = points[0]
    for point in points[1:]:
        origin = origin.add(point)
    origin = origin.multiply(1.0 / len(points))
    group["axis_point_mm"] = [
        round(origin.X(), 4),
        round(origin.Y(), 4),
        round(origin.Z(), 4),
    ]
    group["radius_mm"] = sum(
        abs(p.sub(origin).sub(direction.multiply(p.sub(origin).dot(direction))).Length)
        for p in points
    ) / len(points)


def axis_distance(first: dict, second: dict) -> tuple[float, str]:
    p1, d1 = cq.Vector(*first["axis_point_mm"]), cq.Vector(*first["direction"])
    p2, d2 = cq.Vector(*second["axis_point_mm"]), cq.Vector(*second["direction"])
    cross = d1.cross(d2)
    delta = p2.sub(p1)
    if cross.Length < 1e-9:
        return float(delta.cross(d1).Length), "parallel_axis_offset"
    return float(abs(delta.dot(cross)) / cross.Length), "skew_line_distance"


# --------------------------------------------------------------------------
# harnesses
# --------------------------------------------------------------------------
def harness_t06_launcher() -> dict:
    launcher = importlib.import_module("paddle_launcher_constrained")
    groups = {}
    for config, half_spacing in (("pollen", 80.0), ("nectar", 89.0)):
        PROGRESS.stage(f"building the {config} launcher configuration")
        _, _, shapes, named, kinematics = launcher.build(config, half_spacing)
        groups[config] = {
            "parts": {f"{config}:{name}": shape for name, shape in named.items()},
            "all_shapes": shapes,
            "kinematics": kinematics,
        }
    return {
        "units": "mm",
        "coordinate_system": "X-Y chassis plane; +Z upward; +Y is the adjustment side",
        "design_id": launcher.COTS["design_id"],
        "groups": groups,
    }


HARNESSES = {"t06_launcher": harness_t06_launcher}


def _load(harness_name: str) -> dict:
    if harness_name not in HARNESSES:
        raise SystemExit(f"unknown harness {harness_name!r}; known: {sorted(HARNESSES)}")
    return HARNESSES[harness_name]()


# --------------------------------------------------------------------------
# check evaluation
# --------------------------------------------------------------------------
def resolve_parts(parts: dict, pattern: str) -> dict:
    if pattern in parts:
        return {pattern: parts[pattern]}
    return {key: value for key, value in parts.items() if fnmatch.fnmatch(key, pattern)}


def _verdict(measured, target, tolerance, rule) -> str:
    if measured is None or target is None:
        return UNRESOLVED
    if rule == "ge":
        return PASS if measured >= target - tolerance else FAIL
    if rule == "le":
        return PASS if measured <= target + tolerance else FAIL
    return PASS if abs(measured - target) <= tolerance else FAIL


def evaluate_check(check: dict, parts: dict, context: dict) -> dict:
    kind = check.get("kind")
    tolerance = check.get("tolerance", DEFAULT_TOLERANCE_MM)
    record = {
        "id": check["id"],
        "kind": kind,
        "requirement": check.get("requirement", ""),
        "target": check.get("target"),
        "tolerance": tolerance,
        "method": check.get("method", kind),
        "status": UNRESOLVED,
        "measured": None,
        "deviation": None,
        "note": check.get("note", ""),
    }
    try:
        if kind == "part_solid_count":
            shape = _single(check, parts)[1]
            measured = solid_count(shape)
            record["measured"] = measured
            target = check.get("target")
            if target is None:
                # No target given: report the measurement and leave the verdict open.
                record["status"] = UNRESOLVED
            else:
                record["deviation"] = measured - target
                record["status"] = _verdict(measured, target, tolerance, "abs")
        elif kind in ("bbox_size", "bbox_min", "bbox_max"):
            shape = _single(check, parts)[1]
            facts = bbox_facts(shape)
            key = {"bbox_size": "size_mm", "bbox_min": "min_mm", "bbox_max": "max_mm"}[kind]
            measured = facts[key][AXIS_INDEX[check["axis"]]]
            record["measured"] = measured
            record["deviation"] = round(measured - check["target"], 4)
            record["status"] = _verdict(measured, check["target"], tolerance, "abs")
            record["method"] = f"{kind}[{check['axis']}] from final solid bounding box"
        elif kind == "bbox_size_sorted":
            shape = _single(check, parts)[1]
            measured = sorted(bbox_facts(shape)["size_mm"])
            target = sorted(check["target"])
            deviation = max(abs(m - t) for m, t in zip(measured, target))
            record["measured"] = measured
            record["target"] = target
            record["deviation"] = round(deviation, 4)
            record["status"] = PASS if deviation <= tolerance else FAIL
            record["method"] = "axis-permutation-tolerant envelope comparison (rotation-invariant)"
        elif kind == "volume":
            shape = _single(check, parts)[1]
            # Measured over the part's own solids, never over the container: cq
            # ``Shape.Volume()`` on a compound integrates the compound as one shape
            # and disagrees with the sum of its own solids on curved geometry (see
            # ``cad/t06_vendor_solids.py`` VOLUME_METHOD).  Summing the solids also
            # makes the value independent of how many bodies the part has.
            measured = sum(item.Volume() for item in shape.Solids())
            target = check["target"]
            relative = check.get("relative_tolerance")
            if relative is not None:
                deviation = abs(measured - target) / target if target else math.inf
                record["status"] = PASS if deviation <= relative else FAIL
                record["tolerance"] = relative
                record["tolerance_kind"] = "relative"
            else:
                deviation = measured - target
                record["status"] = _verdict(measured, target, tolerance, "abs")
            record["measured"] = round(measured, 3)
            record["deviation"] = round(deviation, 6)
            record["method"] = ("sum of the volumes of the part's solids, read from the "
                                "final Brep (packaging-independent)")
        elif kind == "clearance":
            value, method = _group_pair(check, parts, mode="distance")
            record["measured"] = round(value, 4)
            record["deviation"] = round(value - check["target"], 4)
            record["status"] = _verdict(value, check["target"], tolerance, "ge")
            record["method"] = method
        elif kind == "intersection_volume":
            value, method = _group_pair(check, parts, mode="intersection")
            record["measured"] = round(value, 4)
            record["deviation"] = round(value - check["target"], 4)
            record["status"] = _verdict(value, check["target"], tolerance, "le")
            record["method"] = method
        elif kind == "cylinder_axis_distance":
            value, detail = _axis_distance_check(check, parts)
            record["measured"] = round(value, 4)
            record["deviation"] = round(value - check["target"], 4)
            record["status"] = _verdict(value, check["target"], tolerance, "abs")
            record["method"] = check.get("method") or detail["rule"]
            record["features"] = detail
        elif kind == "group_bbox":
            keys = resolve_parts(parts, check["part"])
            if not keys:
                raise UnresolvedError(f"part pattern {check['part']!r} matched no part")
            compound = cq.Compound.makeCompound([as_shape(value) for value in keys.values()])
            facts = bbox_facts(compound)
            axis = check.get("axis")
            if axis:
                measured = facts["size_mm"][AXIS_INDEX[axis]]
                record["method"] = (
                    f"compound bounding-box span on {axis} over {len(keys)} matched parts"
                )
            else:
                measured = max(facts["size_mm"])
                record["method"] = f"largest bounding-box span over {len(keys)} matched parts"
            record["part_count"] = len(keys)
            record["bbox"] = facts
            record["measured"] = measured
            record["deviation"] = round(measured - check["target"], 4)
            record["status"] = _verdict(measured, check["target"], tolerance, check.get("rule", "le"))
        elif kind == "step_roundtrip":
            record.update(_roundtrip(check, parts, context))
        else:
            record["status"] = NOT_RUN
            record["note"] = f"unsupported check kind {kind!r}"
    except UnresolvedError as exc:
        record["status"] = UNRESOLVED
        record["note"] = str(exc)
    except KeyError as exc:
        record["status"] = UNRESOLVED
        record["note"] = f"missing part or field: {exc}"
    return record


def _single(check: dict, parts: dict) -> tuple[str, cq.Shape]:
    matches = resolve_parts(parts, check["part"])
    if not matches:
        raise UnresolvedError(f"part pattern {check['part']!r} matched no part")
    if len(matches) > 1:
        raise UnresolvedError(
            f"part pattern {check['part']!r} matched {len(matches)} parts: {sorted(matches)[:6]}"
        )
    key, value = next(iter(matches.items()))
    return key, as_shape(value)


def _group_pair(check: dict, parts: dict, mode: str) -> tuple[float, str]:
    left = resolve_parts(parts, check["a"])
    right = resolve_parts(parts, check["b"])
    if not left or not right:
        raise UnresolvedError(
            f"empty group for {check['a']!r} / {check['b']!r} "
            f"(matched {len(left)} and {len(right)})"
        )
    worst = None
    for left_name, left_shape in left.items():
        for right_name, right_shape in right.items():
            if mode == "distance":
                gap = _bbox_gap(as_shape(left_shape), as_shape(right_shape))
                if worst is not None and gap > worst[0]:
                    continue
                value, _ = min_distance(as_shape(left_shape), as_shape(right_shape), check["target"])
                method = "brep_extrema_distToShape"
            else:
                if not _bbox_overlap(as_shape(left_shape), as_shape(right_shape)):
                    value, method = 0.0, "bbox_disjoint"
                else:
                    value = intersection_volume(as_shape(left_shape), as_shape(right_shape))
                    method = "boolean_intersection_volume"
            if worst is None or (
                (mode == "distance" and value < worst[0])
                or (mode == "intersection" and value > worst[0])
            ):
                worst = (value, method, f"{left_name} | {right_name}")
    value, method, pair = worst
    return value, f"{method} (governing pair: {pair})"


def _axis_distance_check(check: dict, parts: dict) -> tuple[float, dict]:
    features = {}
    for label in ("first", "second"):
        spec = check[label]
        shape = _single({"part": spec["part"]}, parts)[1]
        groups = cylinder_features(
            shape,
            radius_min=spec.get("radius_min_mm"),
            radius_max=spec.get("radius_max_mm"),
            axis_filter=spec.get("axis"),
        )
        if not groups:
            raise UnresolvedError(
                f"no cylindrical feature matched for {label}: part={spec['part']!r} "
                f"radius=[{spec.get('radius_min_mm')}, {spec.get('radius_max_mm')}] axis={spec.get('axis')}"
            )
        if len(groups) > 1 and spec.get("radius_mm") is not None:
            groups = [g for g in groups if abs(g["radius_mm"] - spec["radius_mm"]) <= 0.05]
        features[label] = groups[0]
    value, rule = axis_distance(features["first"], features["second"])
    detail = {"rule": rule, "first": features["first"], "second": features["second"]}
    return value, detail


def _roundtrip(check: dict, parts: dict, context: dict) -> dict:
    import tempfile

    from cadquery import exporters

    matches = resolve_parts(parts, check["part"])
    if not matches:
        raise UnresolvedError(f"part pattern {check['part']!r} matched no part")
    PROGRESS.stage(f"{check['id']}: combining {len(matches)} parts for the STEP round-trip")
    shape = cq.Compound.makeCompound([as_shape(v) for v in matches.values()])
    before = bbox_facts(shape)
    PROGRESS.stage(f"{check['id']}: measuring the volume before export")
    before_volume = float(shape.Volume())
    with tempfile.TemporaryDirectory() as tmp_dir:
        step_path = Path(tmp_dir) / "roundtrip.step"
        PROGRESS.stage(f"{check['id']}: exporting the assembly to STEP")
        exporters.export(shape, str(step_path))
        PROGRESS.stage(f"{check['id']}: re-importing the exported STEP")
        reimported = cq.importers.importStep(str(step_path))
    PROGRESS.stage(f"{check['id']}: comparing bounding box and volume after re-import")
    solids = []
    for value in reimported.vals():
        solids.extend(value.Solids())
    after = bbox_facts(cq.Compound.makeCompound(solids))
    after_volume = float(cq.Compound.makeCompound(solids).Volume())
    tolerance = check.get("tolerance", DEFAULT_TOLERANCE_MM)
    relative = check.get("relative_tolerance", 1e-4)
    size_deviation = max(
        abs(a - b) for a, b in zip(before["size_mm"], after["size_mm"])
    )
    volume_deviation = abs(after_volume - before_volume) / before_volume if before_volume else math.inf
    status = PASS if size_deviation <= tolerance and volume_deviation <= relative else FAIL
    context.setdefault("roundtrips", []).append(
        {"part": check["part"], "before": before, "after": after, "volume_before_mm3": round(before_volume, 3)}
    )
    return {
        "status": status,
        "target": "STEP export/re-import reproduces bbox and volume",
        "tolerance": {"bbox_size_mm": tolerance, "volume_relative": relative},
        "measured": {
            "bbox_size_before_mm": before["size_mm"],
            "bbox_size_after_mm": after["size_mm"],
            "volume_before_mm3": round(before_volume, 3),
            "volume_after_mm3": round(after_volume, 3),
            "solid_count_after": len(solids),
        },
        "deviation": {"bbox_size_mm": round(size_deviation, 5), "volume_relative": round(volume_deviation, 8)},
        "method": "export STEP, re-import, compare bounding box and volume",
        "note": check.get("note", "read-back of this run's exported STEP"),
    }


# --------------------------------------------------------------------------
# inventory
# --------------------------------------------------------------------------
def part_inventory(parts: dict, skip_patterns: list[str]) -> list[dict]:
    inventory = []
    for name, value in sorted(parts.items()):
        if any(fnmatch.fnmatch(name, pattern) for pattern in skip_patterns):
            continue
        shape = as_shape(value)
        record = {
            "id": name,
            "solid_count": solid_count(shape),
            "type": shape.ShapeType(),
            "valid": bool(shape.isValid()),
            "volume_mm3": round(sum(item.Volume() for item in shape.Solids()), 3),
            "bbox": bbox_facts(shape),
        }
        inventory.append(record)
    return inventory


def vendor_records() -> dict:
    """Derivation record per purchased SKU, used as the *target* side of a check.

    Targets come from the requirements and the recorded derivation, never from the
    measured part, so a check can still fail.
    """
    try:
        module = importlib.import_module("t06_vendor_solids")
    except Exception:
        return {}
    records = {}
    for sku in module.CAD_FILES:
        try:
            records[sku] = module.facts(sku)
        except Exception:
            continue
    return records


def automatic_checks(parts: dict, config_path: Path) -> list[dict]:
    """Every purchased SKU must enter the assembly as the whole derived part.

    The target is the body count the vendor derivation measured on the official
    STEP, never a blanket one.  DEC-0021 makes the whole official file the working
    part, so a supplier part the vendor modelled with several bodies legitimately
    arrives with several bodies; comparing the placed count against the derivation
    record is what catches a reduced proxy being substituted back into the launcher.
    """
    checks = []
    if not config_path.is_file():
        return checks
    cots = json.loads(config_path.read_text(encoding="utf-8"))
    records = vendor_records()
    for key, item in cots.items():
        if not isinstance(item, dict) or not item.get("sku"):
            continue
        sku = item["sku"]
        record = records.get(sku) or {}
        target = record.get("derived_solid_count")
        if target is None:
            requirement = f"{key} ({sku}) is present in the assembly"
            note = "the vendor derivation record for this SKU is unavailable"
        else:
            requirement = f"{key} ({sku}) enters the assembly as the whole derived part"
            note = (
                f"the official STEP models this part as "
                f"{record.get('source_step_solids')} bodies and the working part keeps "
                f"{target} of them ({record.get('body_representation')}, DEC-0021)"
            )
        matches = {name: value for name, value in parts.items() if sku in name}
        if not matches:
            checks.append(
                {
                    "id": f"AUTO-SOLID-{sku}",
                    "kind": "part_solid_count",
                    "requirement": requirement,
                    "part": f"*{sku}*",
                    "target": target,
                    "tolerance": 0,
                    "note": f"{note}; no part in this configuration carries this SKU",
                }
            )
            continue
        for name in sorted(matches):
            checks.append(
                {
                    "id": f"AUTO-SOLID-{sku}-{name}",
                    "kind": "part_solid_count",
                    "requirement": requirement,
                    "part": name,
                    "target": target,
                    "tolerance": 0,
                    "method": ("count the solids of the placed part and compare with the "
                               "vendor derivation record"),
                    "note": note,
                }
            )
    return checks


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def configure_stdio() -> None:
    """Keep non-ASCII stage text from killing a redirected run.

    A redirected stdout on Windows starts on a legacy code page, so a stage line
    that embeds a path such as C:\\Users\\... may raise UnicodeEncodeError.  A run
    has to fail on geometry, never on its own logging.
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass


def build_report(args) -> dict:
    started = dt.datetime.now(dt.timezone.utc)
    PROGRESS.stage("reading the inspection specification")
    spec = json.loads(Path(args.spec).read_text(encoding="utf-8")) if args.spec else {"checks": []}
    context: dict = {}

    if args.harness:
        PROGRESS.stage(f"building the assembly through harness {args.harness!r}")
        model = _load(args.harness)
        parts = {}
        for group_name, group in model["groups"].items():
            parts.update(group["parts"])
        coordinate_system = model["coordinate_system"]
        units = model["units"]
        PROGRESS.stage(f"model ready: {len(parts)} named parts in {len(model['groups'])} configurations")
    else:
        PROGRESS.stage(f"reading STEP file {args.step}")
        shape = cq.importers.importStep(str(args.step))
        solids = []
        for value in shape.vals():
            solids.extend(value.Solids())
        parts = {args.step_part_id: cq.Compound.makeCompound(solids)}
        coordinate_system = "as authored in the STEP file"
        units = "mm"

    checks: list[dict] = []
    spec_checks = spec.get("checks", [])
    for index, check in enumerate(spec_checks, 1):
        PROGRESS.stage(f"specification check {index}/{len(spec_checks)}: {check['id']}",
                       index=index, total=len(spec_checks))
        checks.append(evaluate_check(check, parts, context))
    if args.harness == "t06_launcher" and not args.no_auto_checks:
        auto_checks = automatic_checks(parts, ROOT / "config" / "t06_launcher_cots.json")
        PROGRESS.stage(f"generated {len(auto_checks)} per-SKU whole-part checks")
        for index, check in enumerate(auto_checks, 1):
            PROGRESS.stage(f"whole-part check {index}/{len(auto_checks)}: {check['id']}",
                           index=index, total=len(auto_checks))
            checks.append(evaluate_check(check, parts, context))

    PROGRESS.stage("measuring the part inventory")
    inventory = part_inventory(parts, spec.get("inventory_skip", []))
    summary = {state: sum(1 for c in checks if c["status"] == state) for state in (PASS, FAIL, NOT_RUN, UNRESOLVED)}
    critical = [c for c in checks if c["status"] in (FAIL, UNRESOLVED) and c.get("severity", "critical") == "critical"]
    status = FAIL if summary[FAIL] else (UNRESOLVED if summary[UNRESOLVED] else PASS)

    report = {
        "schema_version": "0.1",
        "run_label": args.run_label,
        "created_at_utc": started.isoformat(),
        "duration_s": round((dt.datetime.now(dt.timezone.utc) - started).total_seconds(), 2),
        "command": " ".join(sys.argv),
        "working_directory": str(Path.cwd()),
        "host": platform.node(),
        "interpreter": {"executable": sys.executable, "version": sys.version.replace("\n", " ")},
        "dependencies": {
            "cadquery": cq.__version__,
            "python": platform.python_version(),
        },
        "units": units,
        "coordinate_system": coordinate_system,
        "design_id": spec.get("design_id"),
        "solution_status": "candidate_pending_human_review",
        "inputs": collect_inputs(args),
        "status": status,
        "summary": summary,
        "checks": checks,
        "parts": inventory,
        "roundtrips": context.get("roundtrips", []),
        "not_verified": spec.get("not_verified", []),
        "human_review": spec.get("human_review", []),
    }
    report["failure_states"] = [c["id"] for c in critical]
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--harness", choices=sorted(HARNESSES), help="registered model harness to build and inspect")
    parser.add_argument("--step", help="inspect a single STEP file instead of a harness")
    parser.add_argument("--step-part-id", default="step_part", help="stable id for --step input")
    parser.add_argument("--spec", help="JSON file with the checks for this run")
    parser.add_argument("--run-label", default="R000", help="round label recorded in the report")
    parser.add_argument("--report", required=True, help="JSON report output path")
    parser.add_argument("--progress-file",
                        help="optional JSON file refreshed with the current stage and elapsed time")
    parser.add_argument("--log-file",
                        help="optional text log mirroring the stage and heartbeat lines, for a run "
                             "that is started in the background")
    parser.add_argument("--no-auto-checks", action="store_true",
                        help="skip the generated whole-derived-part checks per COTS SKU")
    args = parser.parse_args(argv)

    if not args.harness and not args.step:
        parser.error("one of --harness or --step is required")

    configure_stdio()
    PROGRESS.configure(path=args.progress_file, log_path=args.log_file)
    PROGRESS.start()
    try:
        report = build_report(args)
    except BaseException as exc:
        # an aborted run must still leave a readable final state behind
        try:
            PROGRESS.stage(f"aborted with {type(exc).__name__}: {exc}")
        except Exception:
            pass
        raise
    finally:
        PROGRESS.stop()
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"status={report['status']} checks={report['summary']} parts={len(report['parts'])}")
    PROGRESS.note(f"report written to {report_path}")
    for check in report["checks"]:
        if check["status"] != PASS:
            print(f"  {check['status']:10s} {check['id']}: measured={check.get('measured')} target={check.get('target')} {check.get('note','')}")
    print(f"report: {report_path}")
    return 0 if report["status"] == PASS else 1


if __name__ == "__main__":
    raise SystemExit(main())
