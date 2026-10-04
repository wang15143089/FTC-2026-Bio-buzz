import cadquery as cq, math
P = r"C:\Users\admin\Downloads\am-5851_yellow Pollen.STEP"
N = r"C:\Users\admin\Downloads\am-5852_blue Blue Alliance Nectar.STEP"
for tag, path in (("POLLEN", P), ("NECTAR", N)):
    s = cq.importers.importStep(path)
    sol = s.solids().vals()
    bb = s.val().BoundingBox()
    vol = sum(x.Volume() for x in sol)
    cx = 0.5*(bb.xmin+bb.xmax); cy = 0.5*(bb.ymin+bb.ymax); cz = 0.5*(bb.zmin+bb.zmax)
    R = 0.5*max(bb.xlen, bb.ylen, bb.zlen)
    print("%s  solids=%d  bbox=%.3f x %.3f x %.3f  R=%.3f  D=%.3f  vol=%.1f mm^3  centre=(%.3f, %.3f, %.3f)" % (tag, len(sol), bb.xlen, bb.ylen, bb.zlen, R, 2*R, vol, cx, cy, cz))
    print("   shell thickness if hollow sphere: %.3f mm ; solid-sphere mass at 1.0 g/cc = %.1f g, at 1.4 = %.1f g" % (vol/(4*math.pi*R*R), vol/1000.0, 1.4*vol/1000.0))
    for x in sol:
        b = x.BoundingBox()
        print("   solid vol=%.1f mm^3 bbox=%.2f/%.2f/%.2f" % (x.Volume(), b.xlen, b.ylen, b.zlen))
