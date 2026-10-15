# -*- coding: utf-8 -*-
import cadquery as cq
STEP = "cad/output/_r56_frame/T06_shooter_frame_R56_pollen.step"
f = cq.Compound.makeCompound(cq.importers.importStep(STEP).vals())

def probe(x0,x1,y0,y1,z0,z1,tag):
    b = cq.Workplane("XY").box(x1-x0,y1-y0,z1-z0).translate(((x0+x1)/2,(y0+y1)/2,(z0+z1)/2)).val()
    s = f.intersect(b)
    sb = s.BoundingBox() if s.Volume()>1e-6 else None
    print("%-28s V=%9.3f %s" % (tag, s.Volume(),
          ("x[%.2f,%.2f] y[%.2f,%.2f] z[%.2f,%.2f]" % (sb.xmin,sb.xmax,sb.ymin,sb.ymax,sb.zmin,sb.zmax)) if sb else ""))

print("=== pillar/bolt columns must be empty below the tabs (z -18..16) ===")
for x in (60.0, 76.0):
    for sy in (-1, 1):
        probe(x-7, x+7, sy*76-9, sy*76+9, -18, 16, "below tab x=%.0f y=%+d" % (x, sy*76))
print()
print("=== tab bottoms (z 15..17 slab at tab footprint) ===")
for x in (60.0, 76.0):
    for sy in (-1, 1):
        probe(x-6, x+6, sy*76-8, sy*76+8, 15.0, 17.5, "tab x=%.0f y=%+.0f" % (x, sy*76))
print()
print("=== plate sky-line: any frame material below z=-5.5 ? ===")
probe(-400,400,-200,200,-60,-5.5,"frame below -5.5")
