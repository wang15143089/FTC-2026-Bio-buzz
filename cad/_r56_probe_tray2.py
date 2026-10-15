import math, cadquery as cq
t = cq.importers.importBrep(r"cad/output/_r56_frame/cache/pollen__feeder_shell_tray.brep").val()
b = t.BoundingBox()
print("tray bbox x[%.2f,%.2f] y[%.2f,%.2f] z[%.2f,%.2f] V=%.1f solids=%d" % (b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax,t.Volume(),len(t.Solids())))
def box(x0,x1,y0,y1,z0,z1):
    return cq.Workplane("XY").box(x1-x0,y1-y0,z1-z0,centered=False).translate((x0,y0,z0)).val()
zt = lambda x: 17.50 + (x+2.30)*math.tan(math.radians(5.0))
print(" x     ztop_pred   col@y=0 z-range (vol)")
for x in range(-90, 291, 10):
    col = t.intersect(box(x-0.5,x+0.5,-0.75,0.75,-10,60))
    v = col.Volume()
    if v > 0.01:
        bb = col.BoundingBox()
        print("%5d  %8.2f   z[%7.2f,%7.2f]  v=%8.2f" % (x, zt(x), bb.zmin, bb.zmax, v))
    else:
        print("%5d  %8.2f   --" % (x, zt(x)))
