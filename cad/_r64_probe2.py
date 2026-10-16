# -*- coding: utf-8 -*-
from pathlib import Path
import cadquery as cq
P = Path("cad/output/_r62b_parts")
frame = cq.importers.importStep(str(Path("cad/output/_r62_frame/T06_shooter_frame_R62_pollen.step"))).val()
def box(x0,y0,z0,x1,y1,z1):
    return cq.Workplane("XY").box(x1-x0,y1-y0,z1-z0,centered=False).translate((x0,y0,z0)).val()
def vol(a,b):
    try: return a.intersect(b).Volume()
    except Exception as e: return -1.0

print("=== frame material that sits directly on the rail top (z 16..22), per region ===")
for lab,(x0,x1,y0,y1) in {"rear  x[-170,-40]":(-170,-40,63,81),
                          "rear  x[-170,-40] neg":(-170,-40,-81,-63),
                          "front x[-40,210]":(-40,210,63,81),
                          "front x[-40,210] neg":(-40,210,-81,-63)}.items():
    print("  %-24s frame_on_rail = %9.2f mm3" % (lab, vol(frame, box(x0,y0,16,x1,y1,22))))

print()
print("=== rail-tab columns O8 at x=60/76, y=+/-76 (tab walls around the O3.4) ===")
for x in (60.0, 76.0):
    for y in (76.0, -76.0):
        print("  x=%5.1f y=%6.1f : frame 16..52 in O8 column = %8.2f mm3  (O3.4 column = %6.2f)"
              % (x, y, vol(frame, cq.Workplane("XY").circle(4.0).extrude(36.0).translate((x,y,16)).val()),
                 vol(frame, cq.Workplane("XY").circle(1.7).extrude(36.0).translate((x,y,16)).val())))

print()
print("=== what the rear piece touches: frame vs rear piece, in the overlap z band ===")
rear = cq.importers.importStep(str(P/"base_rail_rear_joined.step")).val()
print("  frame & rear intersection (any) = %.4f mm3" % vol(frame, rear))
front = cq.importers.importStep(str(P/"base_rail_front_+72.step")).val()
print("  frame & front_+72 intersection   = %.4f mm3" % vol(frame, front))
