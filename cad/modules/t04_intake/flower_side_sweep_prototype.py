"""Printable C04-B1 capstan/slider validation hardware (M3 prototype).

This is a low-cost test article, not robot-release CAD.  Local coordinates:
    +X = paddle extension direction
    +Y = transverse direction
    +Z = up in the bench fixture

For FLOWER testing, align +X to the validated path that is 25 degrees from
FLOWER -X toward -Y.  The support uses mounting-hole datums measured from the
official REV-41-3336 STEP.  The Fusion 360 assembly embeds the official servo
and REV-41-1828 horn as named components; source hashes are checked before
export.  No printed spline is attempted.  Fasteners, cable, return elastic,
guards, and final robot mounting remain outside this M3 validation article.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import cadquery as cq


PROJECT_ROOT = Path(__file__).resolve().parents[3]
INPUT_PATH = PROJECT_ROOT / "calculations" / "t04_intake_inputs.json"
DEFAULT_SERVO_STEP = PROJECT_ROOT / "tmp" / "cad" / "REV-41-3336.STEP"
DEFAULT_HORN_STEP = PROJECT_ROOT / "tmp" / "cad" / "REV-41-1828.STEP"


def load_inputs() -> dict:
    with INPUT_PATH.open(encoding="utf-8") as stream:
        return json.load(stream)


def verify_sha256(path: Path, expected: str) -> None:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest.lower() != expected.lower():
        raise ValueError(f"source hash mismatch for {path}: {digest}")


def bracket_and_rail(inputs: dict) -> cq.Workplane:
    """One-piece bench base, official-hole servo towers, and open guide rail."""
    clearance = inputs["side_sweep_servo"]["prototype_printed_clearance_per_side_mm"]
    servo = inputs["side_sweep_servo"]
    datum = servo["official_step_datum"]
    assembly_datum = servo["prototype_assembly_datum"]

    base = (
        cq.Workplane("XY")
        .box(190.0, 85.0, 5.0, centered=(False, True, False))
        .translate((-55.0, 0.0, 0.0))
    )

    # Transform the official hole centers with the same -90 degree Y rotation
    # used for the vendor servo.  Two separated towers avoid intersecting the
    # servo body and leave the output spline/horn unobstructed.
    translate_x = (
        assembly_datum["target_spline_axis_x_mm"]
        - (-datum["spline_axis_z_mm"])
    )
    translate_z = (
        assembly_datum["target_spline_axis_z_mm"]
        - datum["spline_axis_x_mm"]
    )
    target_holes: list[tuple[float, float]] = []
    for source_x, source_z in datum["mount_hole_centers_xz_mm"]:
        target_holes.append((-source_z + translate_x, source_x + translate_z))

    # The official servo ear front surface reaches y~=12.55 mm after the
    # transform; the horn begins at y=16.50 mm.  This 3.8 mm tower sits in the
    # measured gap with about 0.05/0.10 mm nominal axial clearances.
    tower_y_min = 12.60
    tower_depth = 3.8
    fixture = base
    for tower_x in sorted({round(point[0], 4) for point in target_holes}):
        tower = (
            cq.Workplane("XY")
            .box(12.0, tower_depth, 36.0, centered=(True, False, False))
            .translate((tower_x, tower_y_min, 5.0))
        )
        fixture = fixture.union(tower)
    for hole_x, hole_z in target_holes:
        hole = (
            cq.Workplane("XZ")
            .center(hole_x, hole_z)
            .circle(datum["mount_hole_diameter_mm"] / 2.0 + clearance)
            .extrude(8.0, both=True)
        )
        fixture = fixture.cut(hole)

    # Open rectangular rail.  The slider has 0.3 mm nominal clearance per
    # side; gravity and the pull/return lines retain it during bench tests.
    rail = (
        cq.Workplane("XY")
        .box(120.0, 12.0, 3.0, centered=(False, True, False))
        .translate((12.0, assembly_datum["capstan_center_y_mm"], 5.0))
    )
    fixture = fixture.union(rail)

    # Four generic M4.5 bench/robot-interface holes.  Their mating interface is
    # intentionally not frozen; they are outside the servo/slider datums.
    for x in (50.0, 120.0):
        for y in (-35.0, 35.0):
            fixture = fixture.cut(
                cq.Workplane("XY").center(x, y).circle(2.25).extrude(5.0)
            )
    return fixture


def capstan(inputs: dict) -> cq.Workplane:
    """17 mm pitch-radius single-layer capstan for a REV-41-1828 horn."""
    servo = inputs["side_sweep_servo"]
    pitch_radius = servo["capstan_pitch_radius_m"] * 1000.0
    cable_radius = servo["capstan_cable_diameter_m"] * 500.0
    core_radius = pitch_radius - cable_radius
    flange_radius = pitch_radius + 2.0

    result = cq.Workplane("XY").circle(flange_radius).extrude(1.5)
    result = result.union(
        cq.Workplane("XY").workplane(offset=1.5).circle(core_radius).extrude(5.0)
    )
    result = result.union(
        cq.Workplane("XY").workplane(offset=6.5).circle(flange_radius).extrude(1.5)
    )
    result = result.cut(cq.Workplane("XY").circle(4.5).extrude(8.0))
    # REV Motion Interface: six M3 clearance holes on a 16 mm diameter circle.
    result = result.faces(">Z").workplane().polarArray(8.0, 30.0, 360.0, 6).circle(1.7).cutThruAll()
    # Radial cable anchor; thread/termination method remains an L6 choice.
    anchor = (
        cq.Workplane("XZ")
        .center(pitch_radius, 4.0)
        .circle(1.0)
        .extrude(flange_radius * 2.0, both=True)
    )
    return result.cut(anchor)


def paddle_slider(inputs: dict) -> cq.Workplane:
    """Open-rail slider with a 25 degree, 13 mm lift wedge."""
    path = inputs["side_sweep_path"]
    lift = inputs["flower"]["bottom_ring_thickness_m"] * 1000.0
    angle_deg = path["ball_lift_face_angle_deg"]
    run = lift / math.tan(math.radians(angle_deg))
    clearance = inputs["side_sweep_servo"]["prototype_printed_clearance_per_side_mm"]

    slider = cq.Workplane("XY").box(36.0, 26.0, 6.0, centered=(False, True, False))
    channel = (
        cq.Workplane("XY")
        .box(38.0, 12.0 + 2.0 * clearance, 3.4, centered=(False, True, False))
        .translate((-1.0, 0.0, 0.0))
    )
    slider = slider.cut(channel)

    # Moving +X: the thin leading edge is at +X; the ramp rises toward the rear.
    wedge = (
        cq.Workplane("XZ")
        .polyline([(3.0, 6.0), (3.0 + run, 6.0), (3.0, 6.0 + lift)])
        .close()
        .extrude(10.0, both=True)
    )
    slider = slider.union(wedge)

    # Rear cable lug.  In the assembly its hole center is z=8 mm, aligned with
    # the lower tangent of the 17 mm pitch-radius capstan at z=25 mm.
    cable_lug = (
        cq.Workplane("XY")
        .box(6.0, 6.0, 6.0, centered=(False, True, False))
        .translate((-5.0, -10.0, 0.0))
    )
    cable_hole = (
        cq.Workplane("YZ")
        .center(-10.0, 3.0)
        .circle(1.2)
        .extrude(7.0, both=True)
    )
    return slider.union(cable_lug).cut(channel).cut(cable_hole)


def servo_proxy(inputs: dict) -> cq.Workplane:
    """User/vendor body envelope only; ears, cable and spline are omitted."""
    length, width, height = inputs["side_sweep_servo"]["body_envelope_mm"]
    # Side-lying orientation used by the fixture: X=length, Y=height, Z=width.
    return cq.Workplane("XY").box(length, height, width, centered=(False, True, False))


def transformed_vendor_servo(inputs: dict, servo_step: Path) -> cq.Shape:
    datum = inputs["side_sweep_servo"]["official_step_datum"]
    target = inputs["side_sweep_servo"]["prototype_assembly_datum"]
    translate_x = target["target_spline_axis_x_mm"] - (-datum["spline_axis_z_mm"])
    translate_y = target["target_output_tip_y_mm"] - datum["output_tip_y_mm"]
    translate_z = target["target_spline_axis_z_mm"] - datum["spline_axis_x_mm"]
    return (
        cq.importers.importStep(str(servo_step))
        .rotate((0, 0, 0), (0, 1, 0), target["step_rotation_about_y_deg"])
        .translate((translate_x, translate_y, translate_z))
        .val()
    )


def transformed_vendor_horn(inputs: dict, horn_step: Path) -> cq.Shape:
    target = inputs["side_sweep_servo"]["prototype_assembly_datum"]
    return (
        cq.importers.importStep(str(horn_step))
        .translate(
            (
                target["target_spline_axis_x_mm"],
                target["horn_center_y_mm"],
                target["target_spline_axis_z_mm"],
            )
        )
        .val()
    )


def build_assembly(
    inputs: dict,
    servo_step: Path | None = None,
    horn_step: Path | None = None,
) -> cq.Assembly:
    assembly = cq.Assembly(name="T04_C04B1_CAPSTAN_FIXTURE_M3")
    assembly.add(bracket_and_rail(inputs), name="printed_bracket_rail", color=cq.Color(0.35, 0.40, 0.46))
    target = inputs["side_sweep_servo"]["prototype_assembly_datum"]
    if servo_step is not None:
        assembly.add(
            transformed_vendor_servo(inputs, servo_step),
            name="REV_41_3336_official",
            color=cq.Color(0.12, 0.12, 0.14, 0.9),
        )
    else:
        assembly.add(
            servo_proxy(inputs).translate((-40.2, -19.0, 15.0)),
            name="servo_body_envelope_fallback",
            color=cq.Color(0.12, 0.12, 0.14, 0.8),
        )
    if horn_step is not None:
        assembly.add(
            transformed_vendor_horn(inputs, horn_step),
            name="REV_41_1828_official",
            color=cq.Color(0.88, 0.55, 0.15),
        )
    drum = (
        capstan(inputs)
        .translate((0.0, 0.0, -4.0))
        .rotate((0, 0, 0), (1, 0, 0), -90.0)
        .translate(
            (
                target["target_spline_axis_x_mm"],
                target["capstan_center_y_mm"],
                target["target_spline_axis_z_mm"],
            )
        )
    )
    assembly.add(drum, name="printed_17mm_capstan", color=cq.Color(0.90, 0.45, 0.10))
    assembly.add(
        paddle_slider(inputs).translate((17.0, target["capstan_center_y_mm"], 5.0)),
        name="paddle_start",
        color=cq.Color(0.20, 0.60, 0.90),
    )
    return assembly


def render_preview(
    output_path: Path,
    servo_step: Path | None = None,
    horn_step: Path | None = None,
) -> None:
    """Render a lightweight tessellated engineering preview with matplotlib."""
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    inputs = load_inputs()
    target = inputs["side_sweep_servo"]["prototype_assembly_datum"]
    servo_shape = (
        transformed_vendor_servo(inputs, servo_step)
        if servo_step is not None
        else servo_proxy(inputs).translate((-40.2, -19.0, 15.0)).val()
    )
    items = [
        (bracket_and_rail(inputs).val(), "#596673", 1.0),
        (servo_shape, "#202226", 0.82),
        (
            capstan(inputs)
            .translate((0.0, 0.0, -4.0))
            .rotate((0, 0, 0), (1, 0, 0), -90.0)
            .translate(
                (
                    target["target_spline_axis_x_mm"],
                    target["capstan_center_y_mm"],
                    target["target_spline_axis_z_mm"],
                )
            )
            .val(),
            "#e87318",
            1.0,
        ),
        (
            paddle_slider(inputs)
            .translate((17.0, target["capstan_center_y_mm"], 5.0))
            .val(),
            "#248ed1",
            1.0,
        ),
    ]
    if horn_step is not None:
        items.insert(2, (transformed_vendor_horn(inputs, horn_step), "#d8a037", 0.95))
    fig = plt.figure(figsize=(12, 6.5), dpi=160)
    ax = fig.add_subplot(111, projection="3d")
    for shape, color, alpha in items:
        vertices, triangles = shape.tessellate(0.35)
        xyz = [(v.x, v.y, v.z) for v in vertices]
        faces = [[xyz[index] for index in triangle] for triangle in triangles]
        ax.add_collection3d(
            Poly3DCollection(faces, facecolor=color, edgecolor="none", alpha=alpha)
        )
    ax.set_xlim(-60, 140)
    ax.set_ylim(-45, 45)
    ax.set_zlim(0, 65)
    ax.set_box_aspect((200, 90, 65))
    ax.view_init(elev=25, azim=-60)
    ax.set_xlabel("sweep +X (mm)")
    ax.set_ylabel("transverse Y (mm)")
    ax.set_zlabel("Z (mm)")
    ax.set_title("T04 C04-B1 capstan/slider validation fixture - M3 preliminary")
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)


def export_parts(
    output_root: Path,
    servo_step: Path | None = None,
    horn_step: Path | None = None,
) -> None:
    inputs = load_inputs()
    if servo_step is None or not servo_step.is_file():
        raise FileNotFoundError("official REV-41-3336 STEP is required for assembly export")
    if horn_step is None or not horn_step.is_file():
        raise FileNotFoundError("official REV-41-1828 STEP is required for assembly export")
    verify_sha256(servo_step, inputs["side_sweep_servo"]["official_step_sha256"])
    verify_sha256(horn_step, inputs["side_sweep_servo"]["horn_adapter_step_sha256"])
    step_dir = output_root / "step"
    stl_dir = output_root / "stl"
    step_dir.mkdir(parents=True, exist_ok=True)
    stl_dir.mkdir(parents=True, exist_ok=True)
    parts = {
        "t04_c04b1_servo_rail_bracket_m3": bracket_and_rail(inputs),
        "t04_c04b1_17mm_capstan_m3": capstan(inputs),
        "t04_c04b1_25deg_paddle_slider_m3": paddle_slider(inputs),
    }
    for name, part in parts.items():
        cq.exporters.export(part, str(step_dir / f"{name}.step"))
        cq.exporters.export(
            part,
            str(stl_dir / f"{name}.stl"),
            tolerance=0.08,
            angularTolerance=0.12,
        )
    assembly = build_assembly(inputs, servo_step=servo_step, horn_step=horn_step)
    assembly.save(
        str(step_dir / "t04_c04b1_capstan_fixture_assembly_m3.step"),
        exportType="STEP",
    )
    assembly.save(
        str(step_dir / "t04_c04b1_fusion360_assembly_m3.step"),
        exportType="STEP",
    )
    render_preview(
        output_root / "drawings" / "t04_c04b1_capstan_fixture_m3_preview.png",
        servo_step=servo_step,
        horn_step=horn_step,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=PROJECT_ROOT / "exports")
    parser.add_argument("--servo-step", type=Path, default=DEFAULT_SERVO_STEP)
    parser.add_argument("--horn-step", type=Path, default=DEFAULT_HORN_STEP)
    args = parser.parse_args()
    export_parts(args.output_root, servo_step=args.servo_step, horn_step=args.horn_step)
    if "show_object" in globals():
        show_object(
            build_assembly(load_inputs(), args.servo_step, args.horn_step),
            name="C04-B1 capstan fixture M3",
        )  # type: ignore[name-defined]


if __name__ == "__main__":
    main()
