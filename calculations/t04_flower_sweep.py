"""T04-FLOWER-SWEEP-0.1 nominal STEP collision validation for C04-B1.

CadQuery is imported only inside ``run_geometry`` so the project's lightweight
analytical unit tests remain runnable without the optional CAD environment.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Iterable


INPUT_PATH = Path(__file__).with_name("t04_intake_inputs.json")
FIELDNAMES = ("claim_id", "metric", "value", "unit", "status", "boundary")


def load_inputs(path: Path = INPUT_PATH) -> dict:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def ray_circle_clearance_mm(
    heading_deg: float,
    support_x_mm: float,
    support_y_mm: float,
    support_radius_mm: float,
    ball_radius_mm: float,
) -> float:
    """Minimum planar clearance from a ray to a cylindrical support."""
    heading = math.radians(heading_deg)
    direction = (-math.cos(heading), -math.sin(heading))
    projection = support_x_mm * direction[0] + support_y_mm * direction[1]
    if projection <= 0:
        center_distance = math.hypot(support_x_mm, support_y_mm)
    else:
        cross = direction[0] * support_y_mm - direction[1] * support_x_mm
        center_distance = abs(cross)
    return center_distance - support_radius_mm - ball_radius_mm


def _row(claim: str, metric: str, value: float, unit: str, status: str, boundary: str) -> dict[str, str]:
    return {
        "claim_id": claim,
        "metric": metric,
        "value": f"{value:.6f}",
        "unit": unit,
        "status": status,
        "boundary": boundary,
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_geometry(step_path: Path, inputs: dict) -> list[dict[str, str]]:
    import cadquery as cq

    expected = inputs["official_flower_cad"]
    actual_hash = _sha256(step_path)
    if actual_hash.lower() != expected["sha256"].lower():
        raise ValueError(f"FLOWER STEP hash mismatch: {actual_hash}")

    flower = cq.importers.importStep(str(step_path)).val()
    solids = flower.Solids()
    box = flower.BoundingBox()
    if len(solids) != expected["solid_count"]:
        raise ValueError(f"Expected {expected['solid_count']} solids, found {len(solids)}")

    ring_candidates = [
        solid for solid in solids
        if solid.BoundingBox().zmax < 40.0
        and solid.BoundingBox().xlen > 140.0
        and solid.BoundingBox().ylen > 100.0
    ]
    plate_candidates = [
        solid for solid in solids
        if 100.0 < solid.BoundingBox().zmin < 130.0
        and solid.BoundingBox().xlen > 140.0
        and solid.BoundingBox().ylen > 100.0
    ]
    supports = [
        solid for solid in solids
        if 30.0 < solid.BoundingBox().xlen < 35.0
        and 30.0 < solid.BoundingBox().ylen < 35.0
        and 90.0 < solid.BoundingBox().zlen < 100.0
    ]
    if len(ring_candidates) != 1 or len(plate_candidates) != 1 or len(supports) != 2:
        raise ValueError("Could not uniquely identify bottom ring, upper plate, and two short supports")

    ring_box = ring_candidates[0].BoundingBox()
    plate_box = plate_candidates[0].BoundingBox()
    support_boxes = sorted((solid.BoundingBox() for solid in supports), key=lambda item: item.center.x)
    ring_top = ring_box.zmax
    opening_height = plate_box.zmin - ring_top
    ball_radius = inputs["gamepiece"]["pollen_nominal_diameter_m"] * 500.0
    start_z = ring_top + ball_radius + 0.05
    lift = inputs["flower"]["bottom_ring_thickness_m"] * 1000.0
    path = inputs["side_sweep_path"]
    swept_region_solids = [
        solid for solid in solids
        if solid.BoundingBox().zmax >= ring_box.zmin
        and solid.BoundingBox().zmin <= plate_box.zmin
    ]
    swept_region = cq.Compound.makeCompound(swept_region_solids)

    def ball_overlap(heading_deg: float, travel_step_mm: int = 5) -> tuple[float, float]:
        heading = math.radians(heading_deg)
        worst_travel = 0.0
        worst_overlap = 0.0
        for travel in range(0, int(path["ball_total_validation_travel_mm"]) + 1, travel_step_mm):
            x = -travel * math.cos(heading)
            y = -travel * math.sin(heading)
            z = start_z + min(lift, travel * math.tan(math.radians(path["ball_lift_face_angle_deg"])))
            ball = cq.Workplane("XY").sphere(ball_radius).translate((x, y, z)).val()
            overlap = ball.intersect(swept_region).Volume()
            if overlap > worst_overlap:
                worst_travel, worst_overlap = float(travel), overlap
        return worst_travel, worst_overlap

    lateral_travel, lateral_overlap = ball_overlap(0.0)
    selected_travel, selected_overlap = ball_overlap(path["ball_heading_from_negative_x_deg"])

    heading = math.radians(path["ball_heading_from_negative_x_deg"])
    dx, dy = -math.cos(heading), -math.sin(heading)
    paddle_worst = 0.0
    for travel in range(0, int(path["paddle_powered_travel_mm"]) + 1, 5):
        ball_x, ball_y = dx * travel, dy * travel
        ball_z = start_z + min(lift, travel * math.tan(math.radians(path["ball_lift_face_angle_deg"])))
        paddle_x = ball_x - dx * (ball_radius + path["paddle_thickness_mm"] / 2.0)
        paddle_y = ball_y - dy * (ball_radius + path["paddle_thickness_mm"] / 2.0)
        paddle = (
            cq.Workplane("XY")
            .box(path["paddle_thickness_mm"], path["paddle_width_mm"], path["paddle_height_mm"])
            .rotate((0, 0, 0), (0, 0, 1), 180.0 + path["ball_heading_from_negative_x_deg"])
            .translate((paddle_x, paddle_y, ball_z))
            .val()
        )
        paddle_worst = max(paddle_worst, paddle.intersect(swept_region).Volume())

    tangent = (-dy, dx, 0.0)
    roller_center = cq.Vector(
        dx * path["roller_center_path_distance_mm"],
        dy * path["roller_center_path_distance_mm"],
        path["roller_center_z_mm"],
    )
    roller_axis = cq.Vector(*tangent)
    roller_start = roller_center - roller_axis * (path["roller_width_mm"] / 2.0)
    roller = cq.Solid.makeCylinder(
        path["roller_diameter_mm"] / 2.0,
        path["roller_width_mm"],
        roller_start,
        roller_axis,
    )
    roller_overlap = roller.intersect(swept_region).Volume()

    left_support = support_boxes[0]
    support_radius = left_support.xlen / 2.0
    pure_lateral_clearance = ray_circle_clearance_mm(
        0.0, left_support.center.x, left_support.center.y, support_radius, ball_radius
    )
    selected_clearance = ray_circle_clearance_mm(
        path["ball_heading_from_negative_x_deg"],
        left_support.center.x,
        left_support.center.y,
        support_radius,
        ball_radius,
    )
    lifted_top_clearance = plate_box.zmin - (start_z + lift + ball_radius)

    return [
        _row("SWP-001", "official FLOWER solid count", len(solids), "count", "MEASURED_FROM_CAD", "Hash-locked user-supplied STEP"),
        _row("SWP-002", "official FLOWER X envelope", box.xlen, "mm", "MEASURED_FROM_CAD", "Nominal CAD, not physical field measurement"),
        _row("SWP-003", "official FLOWER Y envelope", box.ylen, "mm", "MEASURED_FROM_CAD", "Nominal CAD, not physical field measurement"),
        _row("SWP-004", "official FLOWER Z envelope", box.zlen, "mm", "MEASURED_FROM_CAD", "Nominal CAD, not physical field measurement"),
        _row("SWP-005", "Retrieval Opening clear height", opening_height, "mm", "MEASURED_FROM_CAD", "Bottom-ring top to upper-plate bottom"),
        _row("SWP-006", "lifted nominal ball top clearance", lifted_top_clearance, "mm", "CALCULATED_FROM_CAD", "13 mm lift; excludes ball and field tolerance"),
        _row("SWP-007", "pure lateral -X support clearance", pure_lateral_clearance, "mm", "CALCULATED_FROM_CAD", "Negative predicts collision with left short support"),
        _row("SWP-008", "pure lateral -X maximum overlap", lateral_overlap, "mm^3", "SIMULATED_NOMINAL_STEP_BOOLEAN", f"5 mm samples, peak at {lateral_travel:.0f} mm"),
        _row("SWP-009", "selected 25 degree planar support clearance", selected_clearance, "mm", "CALCULATED_FROM_CAD", "Nominal cylindrical support boundary"),
        _row("SWP-010", "selected 25 degree ball maximum overlap", selected_overlap, "mm^3", "SIMULATED_NOMINAL_STEP_BOOLEAN", "5 mm samples over 0-120 mm; nominal rigid ball"),
        _row("SWP-011", "selected paddle maximum overlap", paddle_worst, "mm^3", "SIMULATED_NOMINAL_STEP_BOOLEAN", "3x20x32 mm paddle, 5 mm samples over powered travel"),
        _row("SWP-012", "standard roller maximum overlap", roller_overlap, "mm^3", "SIMULATED_NOMINAL_STATIC_BOOLEAN", "60x120 mm roller proxy at 116 mm path distance"),
        _row("SWP-013", "solids included in swept-region collision model", len(swept_region_solids), "count", "CALCULATED_FROM_CAD", "All official solids spanning bottom-ring bottom through upper-plate bottom"),
    ]


def write_csv(rows: Iterable[dict[str, str]], output: Path) -> None:
    with output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--flower-step", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("t04_flower_sweep_results.csv"))
    args = parser.parse_args()
    rows = run_geometry(args.flower_step, load_inputs())
    write_csv(rows, args.output)


if __name__ == "__main__":
    main()
