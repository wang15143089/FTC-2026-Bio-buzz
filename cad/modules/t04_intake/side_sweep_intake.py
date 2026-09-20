"""C04-B1 preliminary CadQuery model (M3, not manufacturing CAD).

Coordinate system follows the official standalone FLOWER STEP:
    +Z up, selected ball path 25 degrees from -X toward -Y.

The model intentionally contains only the validated nominal ball path, a thin
paddle proxy, the shared roller proxy, and optional official FLOWER context.
Servo body, bearings, fasteners, brackets, guides, and tolerances remain TBD.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import cadquery as cq


PROJECT_ROOT = Path(__file__).resolve().parents[3]
INPUT_PATH = PROJECT_ROOT / "calculations" / "t04_intake_inputs.json"


def load_inputs() -> dict:
    with INPUT_PATH.open(encoding="utf-8") as stream:
        return json.load(stream)


def path_position(inputs: dict, travel_mm: float) -> tuple[float, float, float]:
    path = inputs["side_sweep_path"]
    heading = math.radians(path["ball_heading_from_negative_x_deg"])
    radius = inputs["gamepiece"]["pollen_nominal_diameter_m"] * 500.0
    start_z = inputs["official_flower_cad"]["bottom_ring_top_z_mm"] + radius + 0.05
    lift = inputs["flower"]["bottom_ring_thickness_m"] * 1000.0
    z = start_z + min(lift, travel_mm * math.tan(math.radians(path["ball_lift_face_angle_deg"])))
    return (-travel_mm * math.cos(heading), -travel_mm * math.sin(heading), z)


def paddle_at(inputs: dict, travel_mm: float) -> cq.Shape:
    path = inputs["side_sweep_path"]
    heading_deg = path["ball_heading_from_negative_x_deg"]
    heading = math.radians(heading_deg)
    dx, dy = -math.cos(heading), -math.sin(heading)
    ball_radius = inputs["gamepiece"]["pollen_nominal_diameter_m"] * 500.0
    ball_x, ball_y, ball_z = path_position(inputs, travel_mm)
    paddle_x = ball_x - dx * (ball_radius + path["paddle_thickness_mm"] / 2.0)
    paddle_y = ball_y - dy * (ball_radius + path["paddle_thickness_mm"] / 2.0)
    return (
        cq.Workplane("XY")
        .box(path["paddle_thickness_mm"], path["paddle_width_mm"], path["paddle_height_mm"])
        .edges()
        .fillet(1.0)
        .rotate((0, 0, 0), (0, 0, 1), 180.0 + heading_deg)
        .translate((paddle_x, paddle_y, ball_z))
        .val()
    )


def roller(inputs: dict) -> cq.Shape:
    path = inputs["side_sweep_path"]
    heading = math.radians(path["ball_heading_from_negative_x_deg"])
    direction = cq.Vector(-math.cos(heading), -math.sin(heading), 0.0)
    axis = cq.Vector(math.sin(heading), -math.cos(heading), 0.0)
    center = direction * path["roller_center_path_distance_mm"] + cq.Vector(0, 0, path["roller_center_z_mm"])
    start = center - axis * (path["roller_width_mm"] / 2.0)
    return cq.Solid.makeCylinder(
        path["roller_diameter_mm"] / 2.0,
        path["roller_width_mm"],
        start,
        axis,
    )


def build(flower_step: Path | None = None) -> cq.Assembly:
    inputs = load_inputs()
    assembly = cq.Assembly(name="C04-B1_M3_PRELIMINARY")
    if flower_step:
        assembly.add(cq.importers.importStep(str(flower_step)).val(), name="official_flower_reference", color=cq.Color(0.72, 0.75, 0.80, 0.35))

    ball_radius = inputs["gamepiece"]["pollen_nominal_diameter_m"] * 500.0
    for travel, name, color in (
        (0.0, "pollen_start", cq.Color(0.20, 0.55, 0.90, 0.85)),
        (60.0, "pollen_paddle_handoff", cq.Color(0.25, 0.75, 0.45, 0.75)),
        (120.0, "pollen_roller_capture", cq.Color(0.95, 0.65, 0.20, 0.65)),
    ):
        ball = cq.Workplane("XY").sphere(ball_radius).translate(path_position(inputs, travel)).val()
        assembly.add(ball, name=name, color=color)

    assembly.add(paddle_at(inputs, 0.0), name="paddle_start", color=cq.Color(0.85, 0.25, 0.20))
    assembly.add(paddle_at(inputs, 60.0), name="paddle_handoff", color=cq.Color(0.90, 0.45, 0.18, 0.65))
    assembly.add(roller(inputs), name="shared_standard_roller", color=cq.Color(0.38, 0.38, 0.42))
    return assembly


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--flower-step", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    model = build(args.flower_step)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        model.save(str(args.output), exportType="STEP")
    if "show_object" in globals():
        show_object(model, name="C04-B1 M3 preliminary")  # type: ignore[name-defined]


if __name__ == "__main__":
    main()
