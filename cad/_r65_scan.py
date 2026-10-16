# -*- coding: utf-8 -*-
"""R65 scan: find a clear (x,z) for the front nut on both sides."""
from pathlib import Path
import cadquery as cq
A = Path("cad/output/_r62_frame")
def box(x0, y0, z0, x1, y1, z1):
    return cq.Workplane("XY").box(x1-x0, y1-y0, z1-z0, centered=False).translate((x0, y0, z0)).val()
def cyl(p0, h, d, dirv):
    return cq.Solid.makeCylinder(d/2.0, h, cq.Vector(*p0), cq.Vector(*dirv))
def vol(a, b):
    try: return a.intersect(b).Volume()
    except Exception: return -1.0

fr = cq.importers.importStep(str(A / "T06_shooter_frame_R62_pollen.step")).val()
zone = box(-50, 45, -6, 10, 70, 24)
small = fr.intersect(zone)
print("frame inside the zone: %.1f mm3" % small.Volume())
print()
print("frame material in a O7.2 x 12 nut corridor against the +Y inner rail face (y 51..63):")
print("      " + "".join("z=%5.1f " % z for z in (1.0, 3.0, 5.0, 7.0, 9.0, 11.0, 13.0)))
for x in [v * 4.0 for v in range(-12, 3)]:
    row = []
    for z in (1.0, 3.0, 5.0, 7.0, 9.0, 11.0, 13.0):
        row.append(vol(small, cyl((x, 51.0, z), 12.0, 7.2, (0, 1, 0))))
    print("x=%5.1f " % x + "".join("%6.2f " % v for v in row))
print()
print("same on the -Y side (y -63..-51):")
for x in [v * 4.0 for v in range(-12, 3)]:
    row = [vol(small, cyl((x, -63.0, z), 12.0, 7.2, (0, 1, 0))) for z in (1.0, 3.0, 5.0, 7.0, 9.0, 11.0, 13.0)]
    print("x=%5.1f " % x + "".join("%6.2f " % v for v in row))
print()
print("bbox of the offending frame lump inside the zone:")
bb = small.BoundingBox()
print("  x[%.1f,%.1f] y[%.1f,%.1f] z[%.1f,%.1f]  solids=%d" % (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax, len(small.Solids())))
