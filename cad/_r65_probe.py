# -*- coding: utf-8 -*-
"""R65 probe: where can a splice plate + M3 cross-seam fastener live near x=-40?"""
from pathlib import Path
import cadquery as cq

A = Path("cad/output/_r62_frame")
P = Path("cad/output/_r62b_parts")
asm = cq.importers.importStep(str(A / "T06_shooter_assembly_R62_pollen.step")).val()
rails = [cq.importers.importStep(str(P / (n + ".step"))).val()
         for n in ("base_rail_rear_joined", "base_rail_front_+72", "base_rail_front_-72")]

def box(x0, y0, z0, x1, y1, z1):
    return cq.Workplane("XY").box(x1-x0, y1-y0, z1-z0, centered=False).translate((x0, y0, z0)).val()

def col(x, y, z0, z1, d):
    return cq.Workplane("XY").circle(d/2.0).extrude(z1-z0).translate((x, y, z0)).val()

def vol(a, b):
    try: return a.intersect(b).Volume()
    except Exception: return -1.0

bb = asm.BoundingBox()
print("assembly bbox x[%.1f,%.1f] y[%.1f,%.1f] z[%.1f,%.1f]" % (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax))
print("assembly volume = %.1f mm3" % asm.Volume())

# rails volume inside the probe boxes, so we can subtract them out
def other(x0, y0, z0, x1, y1, z1, label):
    bx = box(x0, y0, z0, x1, y1, z1)
    total = vol(asm, bx)
    rail = sum(vol(r, bx) for r in rails)
    print("  %-42s all=%9.2f  rails=%9.2f  OTHER=%9.2f" % (label, total, rail, total - rail))

print()
print("=== (1) outer side band, right of y=81 (plate candidate), also mirror ===")
other(-90, 81, -10, 10, 88, 16, "y 81..88 z -10..16 x -90..10 (+Y)")
other(-90, -88, -10, 10, -81, 16, "y -88..-81 z -10..16 x -90..10 (-Y)")
print("=== (2) inner band y 55..63 (nut side) ===")
other(-90, 55, -10, 10, 63, 16, "y 55..63 z -10..16 x -90..10 (+Y)")
other(-90, -63, -10, 10, -55, 16, "y -63..-55 z -10..16 x -90..10 (-Y)")
print("=== (3) straight below the rails z -20..-10 ===")
other(-90, 60, -20, 10, 84, -10, "y 60..84 z -20..-10 x -90..10 (+Y)")
print("=== (4) above rail top z 16..26 ===")
other(-90, 63, 16, 10, 81, 26, "y 63..81 z 16..26 x -90..10 (+Y)")
other(-90, -81, 16, 10, -63, 26, "y -81..-63 z 16..26 x -90..10 (-Y)")

print()
print("=== (5) cylinder probes O7 x O7 around candidate M3 axes (frame/other material) ===")
print("   %-22s %10s %10s %10s" % ("axis", "outer y81..90", "inner y54..63", "top z16..27"))
for x in (-70, -66, -60, -55, -50, -45, -35, -30, -25, -20, -15, -10, -5, 0):
    for sy, ylbl in ((1, "+Y"), (-1, "-Y")):
        y = 72.0 * sy
        o = col(x, y + 12.0*sy, -10, 16, 7.0)
        i = col(x, y - 12.0*sy, -10, 16, 7.0)
        t = col(x, y, 16.5, 27, 7.0)
        vo = vol(asm, o) - sum(vol(r, o) for r in rails)
        vi = vol(asm, i) - sum(vol(r, i) for r in rails)
        vt = vol(asm, t) - sum(vol(r, t) for r in rails)
        print("   x=%6.1f y=%5.1f %s %10.2f %10.2f %10.2f" % (x, y, ylbl, vo, vi, vt))
