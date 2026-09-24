"""Render deployed and stowed intake STL assemblies with VTK."""

from pathlib import Path
import subprocess
import sys

import vtk


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"


def render(state: str) -> None:
    reader = vtk.vtkSTLReader()
    reader.SetFileName(str(OUT / f"biobuzz_single_motor_flipout_intake_{state}.stl"))
    reader.Update()

    normals = vtk.vtkPolyDataNormals()
    normals.SetInputConnection(reader.GetOutputPort())
    normals.SetFeatureAngle(45)
    normals.SplittingOn()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(normals.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(0.72, 0.78, 0.86)
    actor.GetProperty().SetMetallic(0.20)
    actor.GetProperty().SetRoughness(0.58)

    floor = vtk.vtkPlaneSource()
    floor.SetOrigin(-260, -250, -20)
    floor.SetPoint1(280, -250, -20)
    floor.SetPoint2(-260, 250, -20)
    floor_mapper = vtk.vtkPolyDataMapper()
    floor_mapper.SetInputConnection(floor.GetOutputPort())
    floor_actor = vtk.vtkActor()
    floor_actor.SetMapper(floor_mapper)
    floor_actor.GetProperty().SetColor(0.16, 0.34, 0.22)
    floor_actor.GetProperty().SetOpacity(0.28)

    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.035, 0.045, 0.065)
    renderer.AddActor(actor)
    renderer.AddActor(floor_actor)

    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(1)
    window.SetSize(1600, 1000)
    window.AddRenderer(renderer)

    camera = renderer.GetActiveCamera()
    camera.SetPosition(-610, -720, 440)
    camera.SetFocalPoint(10, 0, 105)
    camera.SetViewUp(0, 0, 1)
    renderer.ResetCameraClippingRange()
    window.Render()

    capture = vtk.vtkWindowToImageFilter()
    capture.SetInput(window)
    capture.SetInputBufferTypeToRGBA()
    capture.ReadFrontBufferOff()
    capture.Update()
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(OUT / f"biobuzz_single_motor_flipout_intake_{state}_preview.png"))
    writer.SetInputConnection(capture.GetOutputPort())
    writer.Write()


def main():
    subprocess.run([sys.executable, str(ROOT / "biobuzz_single_motor_flipout_intake.py")], check=True)
    for state in ("deployed", "stowed"):
        render(state)


if __name__ == "__main__":
    main()
