# -*- coding: utf-8 -*-
"""R64: after the x=-40 split, is every rail piece still fixed to the frame?
Read-only geometry probe."""
from pathlib import Path
import cadquery as cq

P = Path("cad/output/_r62b_parts")
frame = cq.importers.importStep(str(Path("cad/output/_r62_frame/T06_shooter_frame_R62_pollen.step"))).val()
pieces = {n: cq.importers.importStep(str(P / (n + ".step"))).val()
          for n in ("base_rail_rear_joined", "base_rail_front_+72", "base_rail_front_-72")}
print("frame bbox x[%.1f, %.1f] y[%.1f, %.1f] z[%.1f, %.1f]"
      % (frame.BoundingBox().xmin, frame.BoundingBox().xmax, frame.BoundingBox().ymin,
         frame.BoundingBox().ymax, frame.BoundingBox().zmin, frame.BoundingBox().zmax))


def col(x, y, z0, z1, d):
    return cq.Workplane("XY").circle(d / 2.0).extrude(z1 - z0).translate((x, y, z0)).val()


def vol(a, b):
    try:
        return a.intersect(b).Volume()
    except Exception:
        return -1.0


def mat(shape, x, y, z0, z1, d):
    return vol(col(x, y, z0, z1, d), shape)


CH = {"base_rail_rear_joined": [(-150.0, 72.0), (-150.0, -72.0), (-102.0, 72.0), (-102.0, -72.0),
                                (-54.0, 72.0), (-54.0, -72.0)],
      "base_rail_front_+72": [(-6.0, 72.0), (42.0, 72.0), (90.0, 72.0), (138.0, 72.0), (186.0, 72.0)],
      "base_rail_front_-72": [(-6.0, -72.0), (42.0, -72.0), (90.0, -72.0), (138.0, -72.0), (186.0, -72.0)]}

print()
print("per chassis hole O4.6: rail bore material | frame material in three z bands at that (x,y)")
print("%-24s %8s %6s | %8s %8s %8s %8s" % ("piece", "x", "y", "rail -10..16",
                                           "frame 16..45", "frame 45..120", "frame -12..-10"))
for name, pts in CH.items():
    s = pieces[name]
    for x, y in pts:
        hollow = mat(s, x, y, -10.0, 16.0, 4.6)
        print("%-24s %8.1f %6.1f | %12.2f %8.2f %8.2f %8.2f"
              % (name, x, y, hollow, mat(frame, x, y, 16.0, 45.0, 4.6),
                 mat(frame, x, y, 45.0, 120.0, 4.6), mat(frame, x, y, -12.0, -10.0, 4.6)))

print()
print("per frame rail-tab M3 joint O3.4 (x=60/76): tab material above rail, and nut room below sole")
for name in ("base_rail_front_+72", "base_rail_front_-72"):
    for x, ztop in ((60.0, 44.0), (76.0, 48.0)):
        for y in (76.0, -76.0):
            print("%-24s x=%5.1f y=%6.1f | tab_mat 16..%.0f = %7.2f | below_sole(-13..-10) = %6.2f"
                  % (name, x, y, ztop, mat(frame, x, y, 16.0, ztop, 3.4),
                     mat(frame, x, y, -13.0, -10.0, 5.0)))
