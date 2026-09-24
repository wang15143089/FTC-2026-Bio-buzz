"""Render quick PNG previews of the generated STL meshes with VTK."""

from pathlib import Path
import vtk


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"


def render(mode: str) -> None:
    reader = vtk.vtkSTLReader()
    reader.SetFileName(str(OUT / f"biobuzz_launcher_horizontal_feed_{mode}.stl"))
    reader.Update()

    # Remove the camera-side half (Y < -6 mm) to expose the horizontal belt,
    # elbow rollers and the inclined ball path in the preview.
    cut_plane = vtk.vtkPlane()
    cut_plane.SetOrigin(0, -6, 0)
    cut_plane.SetNormal(0, 1, 0)
    clip = vtk.vtkClipPolyData()
    clip.SetInputConnection(reader.GetOutputPort())
    clip.SetClipFunction(cut_plane)
    clip.InsideOutOff()
    clip.Update()

    normals = vtk.vtkPolyDataNormals()
    normals.SetInputConnection(clip.GetOutputPort())
    normals.SetFeatureAngle(45)
    normals.SplittingOn()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(normals.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(0.72, 0.78, 0.86)
    actor.GetProperty().SetMetallic(0.25)
    actor.GetProperty().SetRoughness(0.55)

    # Transparent X-Y chassis reference plane (Z=0).
    plane = vtk.vtkPlaneSource()
    plane.SetOrigin(-130, -180, 0)
    plane.SetPoint1(510, -180, 0)
    plane.SetPoint2(-30, 180, 0)
    plane.SetResolution(18, 12)
    plane_mapper = vtk.vtkPolyDataMapper()
    plane_mapper.SetInputConnection(plane.GetOutputPort())
    plane_actor = vtk.vtkActor()
    plane_actor.SetMapper(plane_mapper)
    plane_actor.GetProperty().SetColor(0.20, 0.48, 0.28)
    plane_actor.GetProperty().SetOpacity(0.20)
    plane_actor.GetProperty().SetRepresentationToSurface()

    axes = vtk.vtkAxesActor()
    axes.SetTotalLength(130, 130, 130)
    axes.SetShaftTypeToCylinder()
    axes.SetCylinderRadius(0.012)
    axes.GetXAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(16)
    axes.GetYAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(16)
    axes.GetZAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(16)

    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.035, 0.045, 0.065)
    renderer.AddActor(actor)
    renderer.AddActor(plane_actor)
    renderer.AddActor(axes)

    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(1)
    window.SetSize(1600, 1000)
    window.AddRenderer(renderer)

    camera = renderer.GetActiveCamera()
    camera.SetPosition(650, -760, 520)
    camera.SetFocalPoint(95, 0, 175)
    camera.SetViewUp(0, 0, 1)
    renderer.ResetCameraClippingRange()

    window.Render()
    capture = vtk.vtkWindowToImageFilter()
    capture.SetInput(window)
    capture.SetScale(1)
    capture.SetInputBufferTypeToRGBA()
    capture.ReadFrontBufferOff()
    capture.Update()

    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(OUT / f"biobuzz_launcher_horizontal_feed_{mode}_preview.png"))
    writer.SetInputConnection(capture.GetOutputPort())
    writer.Write()


if __name__ == "__main__":
    render("pollen")
    render("nectar")
