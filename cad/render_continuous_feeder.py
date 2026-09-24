"""Cutaway preview renderer for the detailed continuous feeder."""

from pathlib import Path
import vtk

OUT = Path(__file__).resolve().parent / "output"

reader = vtk.vtkSTLReader()
reader.SetFileName(str(OUT / "continuous_servo_feeder.stl"))

plane = vtk.vtkPlane()
plane.SetOrigin(0, -8, 0)
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
actor.GetProperty().SetColor(0.72, 0.79, 0.88)
actor.GetProperty().SetMetallic(0.20)
actor.GetProperty().SetRoughness(0.52)

ground = vtk.vtkPlaneSource()
ground.SetOrigin(-155, -140, 0)
ground.SetPoint1(190, -140, 0)
ground.SetPoint2(-155, 140, 0)
ground.SetResolution(14, 10)
gm = vtk.vtkPolyDataMapper()
gm.SetInputConnection(ground.GetOutputPort())
ga = vtk.vtkActor()
ga.SetMapper(gm)
ga.GetProperty().SetColor(0.18, 0.52, 0.30)
ga.GetProperty().SetOpacity(0.18)

axes = vtk.vtkAxesActor()
axes.SetTotalLength(65, 65, 65)
axes.SetShaftTypeToCylinder()
axes.SetCylinderRadius(0.014)

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
cam.SetPosition(410, -480, 325)
cam.SetFocalPoint(5, 0, 85)
cam.SetViewUp(0, 0, 1)
ren.ResetCameraClippingRange()
win.Render()

capture = vtk.vtkWindowToImageFilter()
capture.SetInput(win)
capture.SetInputBufferTypeToRGBA()
capture.ReadFrontBufferOff()
capture.Update()
writer = vtk.vtkPNGWriter()
writer.SetFileName(str(OUT / "continuous_servo_feeder_preview.png"))
writer.SetInputConnection(capture.GetOutputPort())
writer.Write()
