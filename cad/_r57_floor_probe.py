# -*- coding: utf-8 -*-
import cadquery as cq
STEP = "cad/output/_r56_frame/T06_shooter_frame_R56_pollen.step"
wp = cq.importers.importStep(STEP)
f = cq.Compound.makeCompound(wp.vals())
bb = f.BoundingBox()
print("frame bbox x[%.2f,%.2f] y[%.2f,%.2f] z[%.2f,%.2f] V=%.0f"
      % (bb.xmin,bb.xmax,bb.ymin,bb.ymax,bb.zmin,bb.zmax,f.Volume()))

def slab(z0, z1, x0=-400, x1=400, y0=-200, y1=200):
    b = (cq.Workplane("XY").box(x1-x0, y1-y0, z1-z0)
         .translate(((x0+x1)/2.0, (y0+y1)/2.0, (z0+z1)/2.0)))
    s = f.intersect(b.val())
    if s.Volume() < 1e-6:
        print("z[%6.2f,%6.2f]  EMPTY" % (z0,z1)); return
    sb = s.BoundingBox()
    print("z[%6.2f,%6.2f]  V=%8.0f  x[%7.2f,%7.2f] y[%7.2f,%7.2f]"
          % (z0,z1,s.Volume(),sb.xmin,sb.xmax,sb.ymin,sb.ymax))

print()
print("=== z slabs (whole footprint) ===")
for z0 in (-4.0, -2.0, 0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0):
    slab(z0, z0+2.0)

print()
print("=== bottom profile: min z in each x bin, y split ===")
for xa in range(-160, 300, 20):
    row = []
    for ys, ytag in ((-1,"-y"), (1,"+y")):
        y0, y1 = (0.0, 110.0) if ys > 0 else (-110.0, 0.0)
        b = (cq.Workplane("XY").box(20.0, y1-y0, 500.0)
             .translate((xa+10.0, (y0+y1)/2.0, 246.0)))
        s = f.intersect(b.val())
        if s.Volume() < 1e-6:
            row.append("%s:----" % ytag); continue
        sb = s.BoundingBox()
        row.append("%s:%7.2f" % (ytag, sb.zmin))
    print("x[%5d,%5d] %s" % (xa, xa+20, "  ".join(row)))
