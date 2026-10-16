# -*- coding: utf-8 -*-
"""R65 diag: which part sits in the plate / nut-space corridor?"""
import json
from pathlib import Path
import cadquery as cq
A = Path("cad/output/_r62_frame"); P = Path("cad/output/_r62b_parts")

def box(x0, y0, z0, x1, y1, z1):
    return cq.Workplane("XY").box(x1-x0, y1-y0, z1-z0, centered=False).translate((x0, y0, z0)).val()
def cyl(p0, h, d, dirv):
    return cq.Solid.makeCylinder(d/2.0, h, cq.Vector(*p0), cq.Vector(*dirv))
def vol(a, b):
    try: return a.intersect(b).Volume()
    except Exception: return -1.0

RAILS = ("base_rail_rear_joined", "base_rail_front_+72", "base_rail_front_-72")
src = {n: cq.importers.importStep(str(P / (n + ".step"))).val() for n in RAILS}

plate_zone = box(-81, 80, -11, 1, 87, 17)                       # plate bbox + 1 mm
nut_zone = cyl((-16, 51, 3), 12, 7.2, (0, 1, 0))
nut_zone_neg = cyl((-16, -63, 3), 12, 7.2, (0, 1, 0))

print("--- per printed part (R62 individual STEPs) ---")
for f in sorted(P.glob("*.step")):
    s = cq.importers.importStep(str(f)).val()
    v1, v2 = vol(s, plate_zone), vol(s, nut_zone)
    v3 = vol(s, nut_zone_neg)
    if max(v1, v2, v3) > 0.001:
        print("  %-28s plate_zone=%9.3f  nut+16=%8.3f  nut-16=%8.3f" % (f.stem, v1, v2, v3))

print("--- assembly minus ORIGINAL rails, total in each zone ---")
asm = cq.importers.importStep(str(A / "T06_shooter_assembly_R62_pollen.step")).val()
rest = asm
for s in src.values():
    rest = rest.cut(s)
print("  rest volume = %.1f" % rest.Volume())
print("  rest in plate_zone      = %.3f" % vol(rest, plate_zone))
print("  rest in nut+16 corridor = %.3f" % vol(rest, nut_zone))
print("  rest in nut-16 corridor = %.3f" % vol(rest, nut_zone_neg))

print("--- which assembly bodies touch the nut+16 corridor ---")
for i, s in enumerate(asm.Solids()):
    v = vol(s, nut_zone)
    if v > 0.001:
        b = s.BoundingBox()
        print("  body %2d V=%10.1f x[%.1f,%.1f] y[%.1f,%.1f] z[%.1f,%.1f]  hit=%.3f"
              % (i, s.Volume(), b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax, v))
print("--- which assembly bodies touch the plate zone ---")
for i, s in enumerate(asm.Solids()):
    v = vol(s, plate_zone)
    if v > 0.001:
        b = s.BoundingBox()
        print("  body %2d V=%10.1f x[%.1f,%.1f] y[%.1f,%.1f] z[%.1f,%.1f]  hit=%.3f"
              % (i, s.Volume(), b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax, v))
