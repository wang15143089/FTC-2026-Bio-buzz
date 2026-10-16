# -*- coding: utf-8 -*-
from pathlib import Path
import cadquery as cq
A = Path("cad/output/_r62_frame")
def box(x0,y0,z0,x1,y1,z1):
    return cq.Workplane("XY").box(x1-x0,y1-y0,z1-z0,centered=False).translate((x0,y0,z0)).val()
def cyl(p0,h,d,dirv):
    return cq.Solid.makeCylinder(d/2.0,h,cq.Vector(*p0),cq.Vector(*dirv))
def vol(a,b):
    try: return a.intersect(b).Volume()
    except Exception: return -1.0
fr = cq.importers.importStep(str(A/"T06_shooter_frame_R62_pollen.step")).val()
small = fr.intersect(box(-50,45,-12,10,70,24))
ZS = (-1.0,-3.0,-5.0,-7.0)
print("frame material in the +Y nut corridor (y 51..63, O7.2 x 12) at low z:")
print("        " + "".join("z=%5.1f " % z for z in ZS))
for x in (-70.0,-66.0,-60.0,-50.0,-40.0,-32.0,-24.0,-20.0,-16.0,-12.0,-8.0,-4.0,0.0):
    small2 = small if x>-50 else fr.intersect(box(-80,45,-12,-40,70,24))
    row = [vol(small2, cyl((x,51.0,z),12.0,7.2,(0,1,0))) for z in ZS]
    print("x=%6.1f" % x + "".join("%7.2f " % v for v in row))
print()
print("same on -Y (y -63..-51):")
for x in (-70.0,-66.0,-60.0,-40.0,-32.0,-16.0,0.0):
    small2 = small if x>-50 else fr.intersect(box(-80,-70,-12,-40,-45,24))
    row = [vol(small2, cyl((x,-63.0,z),12.0,7.2,(0,1,0))) for z in ZS]
    print("x=%6.1f" % x + "".join("%7.2f " % v for v in row))
