# -*- coding: utf-8 -*-
"""R69 views: 3-way split of the shroud/side-plate body, the 8 bolted joints, and
option-C base rails (one 380 mm body per side).  ASCII labels only."""
import math
from pathlib import Path
import cadquery as cq
import vtk

D = Path("cad/output/_r69_parts"); D.mkdir(parents=True, exist_ok=True)
R66 = Path("cad/output/_r66_parts")
BIG, CUT = 1500.0, 68.0

def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1-x0, y1-y0, z1-z0, centered=False).translate((x0, y0, z0)).val()

def cyl(d, y0, y1, x, z):
    return cq.Solid.makeCylinder(d/2.0, abs(y1-y0), cq.Vector(x, min(y0, y1), z), cq.Vector(0, 1, 0))

L = lambda n: cq.importers.importStep(str(D/(n+".step"))).val()
mid, pL, pR = L("shroud_tray_mid"), L("side_plate_left"), L("side_plate_right")
railP, railM = L("base_rail_+72"), L("base_rail_-72")

# tag, x, z, plate thickness, nut seating face |y|, bolt length  (from _r69_build.py)
STA = (("A", 74.0, 27.0, 16.0, 53.5, 35.0, "53.5..63"),
       ("D", 5.0, 86.0, 4.0, 54.0, 25.0, "54..57"),
       ("B", -25.0, 120.0, 4.0, 54.0, 25.0, "54..57"),
       ("C", -68.0, 140.0, 4.0, 54.0, 25.0, "54..57"))

def bolt_solids(x, z, plate, nut_y, ln, side=1):
    yo = side*(CUT+plate)
    return [("bolt", cyl(3.0, yo - side*ln, yo, x, z)),
            ("wash", cyl(6.5, yo, yo + side*1.0, x, z)),
            ("bolt", cyl(5.5, yo + side*1.0, yo + side*3.0, x, z)),
            ("wash", cyl(6.5, side*nut_y, side*nut_y - side*1.0, x, z)),
            ("nut",  cyl(5.5, side*nut_y - side*1.0, side*nut_y - side*3.4, x, z))]

def stl(path, sh):
    cq.exporters.export(cq.Workplane(obj=sh), str(path)); return str(path)
def act(src, color, alpha=1.0):
    if not isinstance(src, (str, Path)):
        src = stl(D/("_v_tmp_%d.stl" % act.i), src); act.i += 1
    r = vtk.vtkSTLReader(); r.SetFileName(str(src)); r.Update()
    n = vtk.vtkPolyDataNormals(); n.SetInputConnection(r.GetOutputPort()); n.SetFeatureAngle(35); n.Update()
    m = vtk.vtkPolyDataMapper(); m.SetInputConnection(n.GetOutputPort())
    a = vtk.vtkActor(); a.SetMapper(m)
    a.GetProperty().SetColor(*color); a.GetProperty().SetOpacity(alpha)
    if alpha < 1.0: a.GetProperty().SetBackfaceCulling(0)
    return a
act.i = 0

def render(out, items, cam_dir, size=(1500,1080), focus=None, dist=None, up=(0,0,1), note=None):
    ren = vtk.vtkRenderer(); ren.SetBackground(1,1,1)
    for it in items: ren.AddActor(it)
    cam = ren.GetActiveCamera()
    c = focus if focus is not None else ren.ComputeVisiblePropBounds()[0:3]
    ren.ResetCamera()
    if focus is not None: cam.SetFocalPoint(*focus)
    d = dist if dist is not None else cam.GetDistance()
    o = cam_dir; nn = math.sqrt(sum(v*v for v in o))
    cam.SetPosition(c[0]+o[0]/nn*d, c[1]+o[1]/nn*d, c[2]+o[2]/nn*d)
    cam.SetViewUp(*up); ren.ResetCameraClippingRange()
    w = vtk.vtkRenderWindow(); w.SetOffScreenRendering(1); w.AddRenderer(ren); w.SetSize(*size)
    if note:
        t = vtk.vtkTextActor(); t.SetInput(note)
        p = t.GetTextProperty(); p.SetFontSize(26); p.SetColor(0.05,0.05,0.05)
        p.SetFontFamilyToCourier(); t.SetPosition(18, size[1]-14)
        t.SetTextScaleModeToNone(); p.SetJustificationToLeft(); p.SetVerticalJustificationToTop()
        w.Render()  # size the window before measuring
        ren.AddActor(t)
    w.Render()
    f = vtk.vtkWindowToImageFilter(); f.SetInput(w); f.Update()
    wr = vtk.vtkPNGWriter(); wr.SetFileName(str(out)); wr.SetInputConnection(f.GetOutputPort()); wr.Write()
    print("wrote", out, flush=True)

GRAY=(0.60,0.64,0.72); GRN=(0.30,0.66,0.36); BLU=(0.28,0.48,0.84); ORG=(0.95,0.50,0.10)
YEL=(0.88,0.72,0.10); RED=(0.85,0.25,0.25)

HEAD = ("right side shown; left side mirrored\ngap 0.2 mm -> epoxy on all abutting faces\n"
        "head + washer outside plate, washer + hex nut inside\ngrey = shroud/tray   blue = side plate   orange/yellow = M3")

# 1. three pieces -----------------------------------------------------------
render(D/"r69_iso_split.png", [act(pL, GRN, 0.42), act(pR, BLU, 0.42), act(mid, GRAY)],
       (1.0,-1.25,0.75))
render(D/"r69_iso_explode.png",
       [act(pL.translate((0,-70,0)), GRN, 0.55), act(pR.translate((0,70,0)), BLU, 0.55), act(mid, GRAY)],
       (1.0,-1.30,0.75), note="R69 exploded: left plate / shroud-tray / right plate")
render(D/"r69_iso_explode2.png",
       [act(pL.translate((0,-70,0)), GRN, 0.55), act(pR.translate((0,70,0)), BLU, 0.55), act(mid, GRAY)],
       (-0.75,1.15,0.60), note="R69 exploded, seen from the other side")
allb = [act(mid, GRAY)]
allb += [act(sh, ORG if k=="bolt" else YEL) for s in (1,-1) for t,x,z,pl,ny,ln,wr in STA
         for k, sh in bolt_solids(x, z, pl, ny, ln, s)]
render(D/"r69_iso_fasteners.png", allb, (1.0,-1.25,0.50), note="8 x M3 joints (4 per side): A=M3x35, B/C/D=M3x25")
render(D/"r69_iso_fasteners2.png", allb, (-0.85,-1.25,0.50), note="same, from the other side")
render(D/"r69_iso3_all.png", [act(pL, GRN, 0.22), act(pR, BLU, 0.22)] + allb,
       (1.0,-1.25,0.75), note="assembled: 2 plates + mid, 8 bolts (plates shown translucent)")

# 2. joint details ---------------------------------------------------------
for tag, x, z, pl, ny, ln, wr in STA:
    note = ("JOINT %s   x=%.0f  z=%.0f\nplate  68..%.0f   (t=%.1f)\near    54..67.8   bite 3.0  (wall %s)\nM3x%d   2 washers"
            % (tag, x, z, 68+pl, pl, wr, ln))
    for s, nm in ((1, ""), (-1, "_L")):
        sl = box(x-10.0, x+10.0, 42.0, 94.0, z-0.6, z+0.6)
        its = []
        for sh, c in ((mid.intersect(sl), GRAY), (pR.intersect(sl), BLU), (pL.intersect(sl), GRN)):
            if sh.Volume() > 0.2: its.append(act(sh, c))
        for k, b in bolt_solids(x, z, pl, ny, ln, s):
            t = b.intersect(sl)
            if t.Volume() > 0.1: its.append(act(t, ORG if k=="bolt" else YEL))
        if its:
            render(D/("r69_joint_%s%s_plan.png" % (tag, nm)), its, (0,0,1), size=(1000,1000),
                   focus=(x, 60.0, z), dist=105.0, up=(0,1,0), note=note+"\nplan section (cut across z)")
        sl2 = box(x-10.0, x+10.0, 42.0, 94.0, z-16.0, z+16.0)
        its2 = []
        for sh, c in ((mid.intersect(sl2), GRAY), (pR.intersect(sl2), BLU), (pL.intersect(sl2), GRN)):
            if sh.Volume() > 0.2: its2.append(act(sh, c))
        for k, b in bolt_solids(x, z, pl, ny, ln, s):
            t = b.intersect(sl2)
            if t.Volume() > 0.1: its2.append(act(t, ORG if k=="bolt" else YEL))
        if its2:
            render(D/("r69_joint_%s%s_side.png" % (tag, nm)), its2, (0,1,0), size=(1100,900),
                   focus=(x, 60.0, z), dist=105.0, up=(0,0,1), note=note+"\nelevation, looking along y from outside (bolt head side)")
        if nm: break

# 3. rails, option C -------------------------------------------------------
render(D/"r69_rails_new.png", [act(railP, GRAY), act(railM, GRAY)], (0.9,-1.1,0.8),
       note="option C: one 380 mm rail body per side (front + rear joined)")
old = [cq.importers.importStep(str(R66/(n+".step"))).val() for n in
       ("base_rail_front_+72", "base_rail_front_-72", "base_rail_rear_joined",
        "rail_splice_plate_+72", "rail_splice_plate_-72")]
render(D/"r69_rails_old.png", [act(o, RED, 0.75) for o in old], (0.9,-1.1,0.8),
       note="R67: 3 rail bodies + 2 splice plates (red)  ->  removed")
render(D/"r69_rails_compare.png", [act(o, RED, 0.32) for o in old] + [act(railP, GRAY), act(railM, GRAY)],
       (0.9,-1.1,0.8), note="red = parts dropped in R69 (2 splice plates + 4 cross ribs + 2 pads, 4 x M3x30)")
print("done", flush=True)
