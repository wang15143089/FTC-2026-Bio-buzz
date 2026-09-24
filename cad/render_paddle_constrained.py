"""Render overview and linkage-side inspection previews."""

from pathlib import Path
import vtk

OUT = Path(__file__).resolve().parent / "output"
STL = OUT / "paddle_launcher_feasible_nectar.stl"


def clipped_actor(y_cut):
    reader = vtk.vtkSTLReader()
    reader.SetFileName(str(STL))
    plane = vtk.vtkPlane()
    plane.SetOrigin(0, y_cut, 0)
    plane.SetNormal(0, 1, 0)
    clip = vtk.vtkClipPolyData()
    clip.SetInputConnection(reader.GetOutputPort())
    clip.SetClipFunction(plane)
    clip.InsideOutOff()
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputConnection(clip.GetOutputPort())
    normals.SetFeatureAngle(42)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(normals.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(0.71, 0.79, 0.89)
    actor.GetProperty().SetMetallic(0.18)
    actor.GetProperty().SetRoughness(0.52)
    return actor


def render(filename, label_text, y_cut, camera_position, focal_point):
    actor = clipped_actor(y_cut)
    ground = vtk.vtkPlaneSource()
    ground.SetOrigin(-180, -150, 0)
    ground.SetPoint1(245, -150, 0)
    ground.SetPoint2(-180, 150, 0)
    gm = vtk.vtkPolyDataMapper()
    gm.SetInputConnection(ground.GetOutputPort())
    ga = vtk.vtkActor()
    ga.SetMapper(gm)
    ga.GetProperty().SetColor(0.16, 0.50, 0.29)
    ga.GetProperty().SetOpacity(0.14)
    axes = vtk.vtkAxesActor()
    axes.SetTotalLength(75, 75, 75)
    axes.SetShaftTypeToCylinder()
    axes.SetCylinderRadius(0.013)
    label = vtk.vtkTextActor()
    label.SetInput(label_text)
    label.SetPosition(35, 945)
    label.GetTextProperty().SetFontSize(25)
    label.GetTextProperty().SetColor(0.90, 0.94, 1.00)
    ren = vtk.vtkRenderer()
    ren.SetBackground(0.030, 0.042, 0.063)
    for item in (actor, ga, axes):
        ren.AddActor(item)
    ren.AddActor2D(label)
    win = vtk.vtkRenderWindow()
    win.SetOffScreenRendering(1)
    win.SetSize(1600, 1000)
    win.AddRenderer(ren)
    cam = ren.GetActiveCamera()
    cam.SetPosition(*camera_position)
    cam.SetFocalPoint(*focal_point)
    cam.SetViewUp(0, 0, 1)
    ren.ResetCameraClippingRange()
    win.Render()
    capture = vtk.vtkWindowToImageFilter()
    capture.SetInput(win)
    capture.SetInputBufferTypeToRGBA()
    capture.ReadFrontBufferOff()
    capture.Update()
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(OUT / filename))
    writer.SetInputConnection(capture.GetOutputPort())
    writer.Write()


render("paddle_launcher_feasible_overview.png", "FEASIBLE NECTAR CONFIG  |  52 deg  |  X-Y CHASSIS PLANE", -8, (570, -720, 470), (15, 0, 190))
render("paddle_launcher_feasible_linkage.png", "GAP LINKAGE: SERVO > CROSSHEAD > TWO LINKS > AXLE CARRIAGES", 66, (470, 720, 420), (-25, 82, 205))
