import sys, math
from pathlib import Path
HERE = Path(r"C:\Users\admin\OneDrive\文档\ChatGPT\FTC 2026 biobuzz\cad")
sys.path.insert(0, str(HERE))
import cadquery as cq
import paddle_launcher_constrained as pl

BALL_R = 35.56
C = (29.49, 0.0, 111.46)
pl.PADDLE_CENTER = C
R_CARRY = 58.4
R_IN = R_CARRY + BALL_R
A_IN, A_OUT = 225.0, 142.0
W_Y = 108.0

def sector(r_in, r_out, a0, a1, width):
    pts = []
    n = 96
    for i in range(n+1):
        a = math.radians(a0 + (a1-a0)*i/n)
        pts.append((C[0]+r_out*math.cos(a), C[2]+r_out*math.sin(a)))
    for i in range(n+1):
        a = math.radians(a1 + (a0-a1)*i/n)
        pts.append((C[0]+r_in*math.cos(a), C[2]+r_in*math.sin(a)))
    return cq.Workplane("XZ").polyline(pts).close().extrude(width/2.0, both=True).val()

def bb(s):
    b=s.BoundingBox()
    return tuple(round(v,2) for v in (b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax))

shell = sector(R_IN, R_IN+7.0, A_IN, A_OUT, W_Y)
print("shell bbox", bb(shell), "vol", round(shell.Volume(),1))

guides = pl.GUIDES
seg3 = guides[2]
panels = {}
panels["floor3"] = pl.panel_on_segment(seg3[0], seg3[1], seg3[3], "floor")
panels["roof3"]  = pl.panel_on_segment(seg3[0], seg3[1], seg3[3], "roof")
for s in (-1,1):
    panels[f"wall3_{s:+d}"] = pl.panel_on_segment(seg3[0], seg3[1], seg3[3], "wall", s)
for n in (-55.0, 55.0):
    panels[f"throat_{n:+.0f}"] = pl.to_world(pl.box(83.0, pl.CHANNEL_CLEAR_W+6, 3, (-135+83.0/2, 0, n)))

def vol(a,b):
    ba, bbb = a.BoundingBox(), b.BoundingBox()
    if ba.xmax<=bbb.xmin or bbb.xmax<=ba.xmin or ba.ymax<=bbb.ymin or bbb.ymax<=ba.ymin or ba.zmax<=bbb.zmin or bbb.zmax<=ba.zmin:
        return 0.0
    return max(0.0, a.intersect(b).Volume())

print("=== shell vs panels ===")
for k,v in panels.items():
    print(f"  {k:12s} {vol(shell,v):12.3f}  wonly_bbox {bb(v)}")
disc = cq.Solid.makeCylinder(60.0, 100.0, cq.Vector(C[0], -50.0, C[2]), cq.Vector(0,1,0))
print("=== paddle disc r60 vs panels ===")
for k,v in panels.items():
    print(f"  {k:12s} {vol(disc,v):12.3f}")
