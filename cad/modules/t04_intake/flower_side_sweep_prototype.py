"""Printable C04-B1 capstan/slider validation hardware (M3 prototype).

This is a low-cost test article, not robot-release CAD.  Local coordinates:
    +X = paddle extension direction
    +Y = transverse direction
    +Z = up in the bench fixture

For FLOWER testing, align +X to the validated path that is 25 degrees from
FLOWER -X toward -Y.  The servo is held on its side in a cable-tie cradle; the
printed capstan bolts to a REV-41-1828 aluminum horn.  No printed spline is
attempted.  The open rail intentionally favors fast inspection over retention;
the operator must use a low-force return elastic and a physical 60 mm stop.
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


def bracket_and_rail(inputs: dict) -> cq.Workplane:
    """One-piece bench base, side-lying servo cradle, and open guide rail."""
    clearance = inputs["side_sweep_servo"]["prototype_printed_clearance_per_side_mm"]
    body_length, body_width, body_height = inputs["side_sweep_servo"]["body_envelope_mm"]

    base = (
        cq.Workplane("XY")
        .box(185.0, 70.0, 5.0, centered=(False, True, False))
        .translate((-55.0, 0.0, 0.0))
    )

    # Servo lies on its 40.2 x 38 mm side.  A 10 mm local riser places the
    # 17 mm capstan lower tangent near the slider cable height.
    cradle_length = body_length + 2.0 * clearance + 6.0
    cradle_depth = body_height + 2.0 * clearance + 6.0
    cradle_x0 = -body_length - clearance - 3.0
    floor = (
        cq.Workplane("XY")
        .box(cradle_length, cradle_depth, 10.0, centered=(False, True, False))
        .translate((cradle_x0, 0.0, 5.0))
    )
    wall_thickness = 3.0
    wall_height = 12.0
    wall_y = body_height / 2.0 + clearance + wall_thickness / 2.0
    side_a = (
        cq.Workplane("XY")
        .box(cradle_length, wall_thickness, wall_height, centered=(False, True, False))
        .translate((cradle_x0, wall_y, 15.0))
    )
    side_b = side_a.mirror("XZ")
    end_stop = (
        cq.Workplane("XY")
        .box(wall_thickness, cradle_depth, wall_height, centered=(False, True, False))
        .translate((cradle_x0, 0.0, 15.0))
    )

    # Two transverse tie channels accept nominal 4 mm cable ties.  They are
    # deliberately generous and do not claim a printer-specific snap fit.
    fixture = base.union(floor).union(side_a).union(side_b).union(end_stop)
    for x in (-31.0, -7.0):
        slot = (
            cq.Workplane("XY")
            .box(4.8, cradle_depth + 2.0, 15.2, centered=(True, True, False))
            .translate((x, 0.0, 0.0))
        )
        fixture = fixture.cut(slot)

    # Open rectangular rail.  The slider has 0.3 mm nominal clearance per
    # side; gravity and the pull/return lines retain it during bench tests.
    rail = (
        cq.Workplane("XY")
        .box(120.0, 12.0, 3.0, centered=(False, True, False))
        .translate((8.0, 22.0, 5.0))
    )
    fixture = fixture.union(rail)

    # Four generic M4.5 bench/robot-interface holes.  Their mating interface is
    # intentionally not frozen; they are outside the servo/slider datums.
    for x in (45.0, 112.0):
        for y in (-27.5, 27.5):
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
    result = result.faces(">Z").workplane().polarArray(8.0, 0.0, 360.0, 6).circle(1.7).cutThruAll()
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
        .translate((-5.0, 0.0, 0.0))
    )
    cable_hole = (
        cq.Workplane("YZ")
        .center(0.0, 3.0)
        .circle(1.2)
        .extrude(7.0, both=True)
    )
    return slider.union(cable_lug).cut(cable_hole)


def servo_proxy(inputs: dict) -> cq.Workplane:
    """User/vendor body envelope only; ears, cable and spline are omitted."""
    length, width, height = inputs["side_sweep_servo"]["body_envelope_mm"]
    # Side-lying orientation used by the fixture: X=length, Y=height, Z=width.
    return cq.Workplane("XY").box(length, height, width, centered=(False, True, False))


def build_assembly(inputs: dict) -> cq.Assembly:
    assembly = cq.Assembly(name="T04_C04B1_CAPSTAN_FIXTURE_M3")
    assembly.add(bracket_and_rail(inputs), name="printed_bracket_rail", color=cq.Color(0.35, 0.40, 0.46))
    assembly.add(
        servo_proxy(inputs).translate((-40.2, 0.0, 15.0)),
        name="servo_body_envelope",
        color=cq.Color(0.12, 0.12, 0.14, 0.8),
    )
    drum = (
        capstan(inputs)
        .translate((0.0, 0.0, -4.0))
        .rotate((0, 0, 0), (1, 0, 0), -90.0)
        .translate((-9.5, 24.0, 25.0))
    )
    assembly.add(drum, name="printed_17mm_capstan", color=cq.Color(0.90, 0.45, 0.10))
    assembly.add(
        paddle_slider(inputs).translate((10.0, 22.0, 5.0)),
        name="paddle_start",
        color=cq.Color(0.20, 0.60, 0.90),
    )
    assembly.add(
        paddle_slider(inputs).translate((70.0, 22.0, 5.0)),
        name="paddle_end_ghost",
        color=cq.Color(0.25, 0.80, 0.45, 0.45),
    )
    return assembly


def render_preview(output_path: Path) -> None:
    """Render a lightweight tessellated engineering preview with matplotlib."""
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    inputs = load_inputs()
    items = (
        (bracket_and_rail(inputs).val(), "#596673", 1.0),
        (servo_proxy(inputs).translate((-40.2, 0.0, 15.0)).val(), "#202226", 0.75),
        (
            capstan(inputs)
            .translate((0.0, 0.0, -4.0))
            .rotate((0, 0, 0), (1, 0, 0), -90.0)
            .translate((-9.5, 24.0, 25.0))
            .val(),
            "#e87318",
            1.0,
        ),
        (paddle_slider(inputs).translate((10.0, 22.0, 5.0)).val(), "#248ed1", 1.0),
        (paddle_slider(inputs).translate((70.0, 22.0, 5.0)).val(), "#48b96a", 0.35),
    )
    fig = plt.figure(figsize=(12, 6.5), dpi=160)
    ax = fig.add_subplot(111, projection="3d")
    for shape, color, alpha in items:
        vertices, triangles = shape.tessellate(0.35)
        xyz = [(v.x, v.y, v.z) for v in vertices]
        faces = [[xyz[index] for index in triangle] for triangle in triangles]
        ax.add_collection3d(
            Poly3DCollection(faces, facecolor=color, edgecolor="none", alpha=alpha)
        )
    ax.set_xlim(-60, 135)
    ax.set_ylim(-40, 50)
    ax.set_zlim(0, 50)
    ax.set_box_aspect((195, 90, 50))
    ax.view_init(elev=25, azim=-60)
    ax.set_xlabel("sweep +X (mm)")
    ax.set_ylabel("transverse Y (mm)")
    ax.set_zlabel("Z (mm)")
    ax.set_title("T04 C04-B1 capstan/slider validation fixture - M3 preliminary")
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)


def export_parts(output_root: Path) -> None:
    inputs = load_inputs()
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
    build_assembly(inputs).save(
        str(step_dir / "t04_c04b1_capstan_fixture_assembly_m3.step"),
        exportType="STEP",
    )
    render_preview(output_root / "drawings" / "t04_c04b1_capstan_fixture_m3_preview.png")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=PROJECT_ROOT / "exports")
    args = parser.parse_args()
    export_parts(args.output_root)
    if "show_object" in globals():
        show_object(build_assembly(load_inputs()), name="C04-B1 capstan fixture M3")  # type: ignore[name-defined]


if __name__ == "__main__":
    main()
