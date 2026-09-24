"""Cutaway preview for the paddle-feeder opposed-flywheel launcher."""

from pathlib import Path
import vtk

OUT = Path(__file__).resolve().parent / "output"

reader = vtk.vtkSTLReader()
reader.SetFileName(str(OUT / "paddle_feeder_opposed_flywheel_launcher.stl"))

plane = vtk.vtkPlane()
plane.SetOrigin(0, -7, 0)
plane.SetNormal(0, 1, 0)
clip = vtk.vtkClipPolyData()
clip.SetInputConnection(reader.GetOutputPort())
clip.SetClipFunction(plane)
clip.InsideOutOff()

normals = vtk.vtkPolyDataNormals()
normals.SetInputConnection(clip.GetOutputPort())
normals.SetFeatureAngle(44)

mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(normals.GetOutputPort())
actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetColor(0.72, 0.79, 0.88)
actor.GetProperty().SetMetallic(0.20)
actor.GetProperty().SetRoughness(0.50)

ground = vtk.vtkPlaneSource()
ground.SetOrigin(-225, -150, 0)
ground.SetPoint1(285, -150, 0)
ground.SetPoint2(-225, 150, 0)
gm = vtk.vtkPolyDataMapper()
gm.SetInputConnection(ground.GetOutputPort())
ga = vtk.vtkActor()
ga.SetMapper(gm)
ga.GetProperty().SetColor(0.18, 0.52, 0.30)
ga.GetProperty().SetOpacity(0.16)

axes = vtk.vtkAxesActor()
axes.SetTotalLength(85, 85, 85)
axes.SetShaftTypeToCylinder()
axes.SetCylinderRadius(0.013)

ren = vtk.vtkRenderer()
ren.SetBackground(0.035, 0.045, 0.065)
ren.AddActor(actor)
ren.AddActor(ga)
ren.AddActor(axes)

win = vtk.vtkRenderWindow()
win.SetOffScreenRendering(1)
win.SetSize(1600, 1000)
win.AddRenderer(ren)
cam = ren.GetActiveCamera()
cam.SetPosition(560, -720, 460)
cam.SetFocalPoint(15, 0, 155)
cam.SetViewUp(0, 0, 1)
ren.ResetCameraClippingRange()
win.Render()

capture = vtk.vtkWindowToImageFilter()
capture.SetInput(win)
capture.SetInputBufferTypeToRGBA()
capture.ReadFrontBufferOff()
capture.Update()
writer = vtk.vtkPNGWriter()
writer.SetFileName(str(OUT / "paddle_feeder_opposed_flywheel_launcher_preview.png"))
writer.SetInputConnection(capture.GetOutputPort())
writer.Write()
