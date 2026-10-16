# -*- coding: utf-8 -*-
"""R69 rails: what was removed (offset view)."""
import math
from pathlib import Path
import cadquery as cq
import vtk
D = Path("cad/output/_r69_parts"); R66 = Path("cad/output/_r66_parts"); BIG = 1500.0
def box(x0,x1,y0,y1,z0,z1):
    return cq.Workplane("XY").box(x1-x0,y1-y0,z1-z0,centered=False).translate((x0,y0,z0)).val()
def stl(p, sh):
    cq.exporters.export(cq.Workplane(obj=sh), str(p)); return str(p)
def act(src, color, alpha=1.0):
    if not isinstance(src, (str, Path)):
        src = stl(D/("_v_rail_%d.stl" % act.i), src); act.i += 1
    r = vtk.vtkSTLReader(); r.SetFileName(str(src)); r.Update()
    n = vtk.vtkPolyDataNormals(); n.SetInputConnection(r.GetOutputPort()); n.SetFeatureAngle(35); n.Update()
    m = vtk.vtkPolyDataMapper(); m.SetInputConnection(n.GetOutputPort())
    a = vtk.vtkActor(); a.SetMapper(m); a.GetProperty().SetColor(*color); a.GetProperty().SetOpacity(alpha)
    if alpha < 1.0: a.GetProperty().SetBackfaceCulling(0)
    return a
act.i = 0
def render(out, items, cam_dir, size=(1600,1100), focus=None, dist=None, up=(0,0,1), note=None):
    ren = vtk.vtkRenderer(); ren.SetBackground(1,1,1)
    for it in items: ren.AddActor(it)
    cam = ren.GetActiveCamera(); ren.ResetCamera()
    c = focus if focus is not None else cam.GetFocalPoint()
    if focus is not None: cam.SetFocalPoint(*focus)
    d = dist if dist is not None else cam.GetDistance()
    o = cam_dir; nn = math.sqrt(sum(v*v for v in o))
    cam.SetPosition(c[0]+o[0]/nn*d, c[1]+o[1]/nn*d, c[2]+o[2]/nn*d)
    cam.SetViewUp(*up); ren.ResetCameraClippingRange()
    w = vtk.vtkRenderWindow(); w.SetOffScreenRendering(1); w.AddRenderer(ren); w.SetSize(*size)
    if note:
        t = vtk.vtkTextActor(); t.SetInput(note); p = t.GetTextProperty()
        p.SetFontSize(24); p.SetColor(0.05,0.05,0.05); p.SetFontFamilyToCourier()
        p.SetJustificationToLeft(); p.SetVerticalJustificationToTop(); t.SetTextScaleModeToNone()
        t.SetPosition(16, size[1]-10); ren.AddActor(t)
    w.Render()
    f = vtk.vtkWindowToImageFilter(); f.SetInput(w); f.Update()
    wr = vtk.vtkPNGWriter(); wr.SetFileName(str(out)); wr.SetInputConnection(f.GetOutputPort()); wr.Write()
    print("wrote", out, flush=True)
GRAY=(0.58,0.62,0.70); RED=(0.86,0.22,0.22); ORG=(0.95,0.55,0.10)
railP = cq.importers.importStep(str(D/"base_rail_+72.step")).val()
railM = cq.importers.importStep(str(D/"base_rail_-72.step")).val()
rear = cq.importers.importStep(str(R66/"base_rail_rear_joined.step")).val()
spec = [cq.importers.importStep(str(R66/("rail_splice_plate_%s72.step" % s))).val() for s in ("+","-")]
bridge = rear.intersect(box(-BIG,BIG,-63.0,63.0,-BIG,BIG))
UP = (0,0,75)
render(D/"r69_rails_compare.png",
       [act(railP,GRAY), act(railM,GRAY), act(bridge.translate(UP), RED, 0.55),
        act(spec[0].translate(UP), ORG, 0.85), act(spec[1].translate(UP), ORG, 0.85)],
       (0.9,-1.05,0.75), focus=(20.0,0.0,60.0), dist=560.0,
       note="R69 option C: one 380 mm rail body per side (grey)\n"
            "raised: parts removed from R67 -- cross-rib bridge (red) + 2 splice plates (orange) + 4 x M3x30")
render(D/"r69_rails_new.png", [act(railP,GRAY), act(railM,GRAY)],
       (0.9,-1.05,0.75), focus=(20.0,0.0,3.0), dist=560.0,
       note="option C: front + rear joined into one 380 mm rail per side (no splice plate, no cross ribs)")
