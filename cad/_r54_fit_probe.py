# -*- coding: utf-8 -*-
"""T06 R54 -- focused fit probe (read-only, no part file is written)."""
import json, sys, time
from pathlib import Path
import cadquery as cq

HERE = Path(__file__).resolve().parent
OUT = HERE / "output" / "_r54_frame"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
FRAME = OUT / "T06_shooter_frame_R54_pollen.step"
ASSY = OUT / "T06_shooter_assembly_R54_pollen.step"

def cyl(r, p0, d, h):
    return cq.Solid.makeCylinder(r, h, cq.Vector(*p0), cq.Vector(*d))

def scan(shape, axis, fixed, lo, hi, r, label):
    p0 = {"x": (lo, fixed[0], fixed[1]), "y": (fixed[0], lo, fixed[1]),
          "z": (fixed[0], fixed[1], lo)}[axis]
    d = {"x": (1,0,0), "y": (0,1,0), "z": (0,0,1)}[axis]
    i = "xyz".index(axis)
    it = cyl(r, p0, d, hi-lo).intersect(shape)
    rows = []
    for s in it.Solids():
        bb = s.BoundingBox()
        a = (bb.xmin, bb.ymin, bb.zmin)[i]; b = (bb.xmax, bb.ymax, bb.zmax)[i]
        if s.Volume() > 0.02:
            rows.append([round(a,2), round(b,2), round(s.Volume(),2)])
    rows.sort()
    print("  %-42s -> %s" % (label, rows))
    return rows

def boxvol(shape, x0,x1,y0,y1,z0,z1):
    x0,x1 = sorted((x0,x1)); y0,y1 = sorted((y0,y1)); z0,z1 = sorted((z0,z1))
    b = cq.Workplane("XY").box(x1-x0, y1-y0, z1-z0).translate(
        ((x0+x1)/2, (y0+y1)/2, (z0+z1)/2)).val()
    it = b.intersect(shape)
    v = 0.0; zs = []
    for s in it.Solids():
        v += s.Volume(); bb = s.BoundingBox(); zs.append([round(bb.zmin,2), round(bb.zmax,2)])
    return round(v,2), sorted(zs)

t0 = time.time()
frame = cq.importers.importStep(str(FRAME)).val()
print("frame imported in %.1fs" % (time.time()-t0))
rep = {"units":"mm","source":FRAME.name,"probes":{},"free_space":{}}

print("== 1. hole axis z-scan, printed frame (r=0.3) ==")
ax = {}
for x in (60.0, 76.0):
    for sy in (-1, 1):
        k = "x%.0f_y%+d" % (x, sy*70.0)
        ax[k] = scan(frame, "z", (x, sy*70.0), -12.0, 80.0, 0.3, "frame z @ x=%.0f y=%+.0f" % (x, sy*70.0))
rep["probes"]["frame_hole_axis_z"] = ax

print("== 2. leg cross-section ==")
leg = {}
for z in (20.0, 27.0, 35.0, 45.0):
    leg["x-scan z=%.0f" % z] = scan(frame, "x", (70.0, z), 40.0, 100.0, 0.3, "frame x @ y=70 z=%.0f" % z)
leg["y-scan x=60 z=27"] = scan(frame, "y", (60.0, 27.0), 40.0, 100.0, 0.3, "frame y @ x=60 z=27")
leg["y-scan x=60 z=45"] = scan(frame, "y", (60.0, 45.0), 40.0, 100.0, 0.3, "frame y @ x=60 z=45")
leg["y-scan x=76 z=45"] = scan(frame, "y", (76.0, 45.0), 40.0, 100.0, 0.3, "frame y @ x=76 z=45")
leg["z-scan x=70 y=72"] = scan(frame, "z", (70.0, 72.0), 5.0, 60.0, 0.3, "frame z @ x=70 y=72")
leg["z-scan x=70 y=60"] = scan(frame, "z", (70.0, 60.0), 5.0, 60.0, 0.3, "frame z @ x=70 y=60")
rep["probes"]["leg_cross_section"] = leg

print("== 3. leg column over the rail: box x 50..86, y 63..81 ==")
for sy in (-1, 1):
    v, zs = boxvol(frame, 50, 86, sy*63, sy*81, 16.5, 80)
    print("   frame in band y%+d: %.2f mm3, z spans %s" % (sy, v, zs))
    rep["probes"]["leg_over_rail_y%+d" % sy] = {"vol": v, "z": zs}
    scan(frame, "z", (70.0, sy*72.0), 10.0, 60.0, 0.3, "  frame z @ x=70 y=%+.0f" % (sy*72.0))

print("== 4. free space, printed frame ==")
fs = {}
fs["outboard_y85_115"] = boxvol(frame, 40, 100, 85, 115, -5, 30)
fs["outboard_y83_120_wide"] = boxvol(frame, 20, 120, 83, 120, -5, 30)
fs["under_rail_z_-12_1"] = boxvol(frame, 45, 90, 60, 84, -12, 1.0)
fs["above_leg_z48_75"] = boxvol(frame, 50, 86, 60, 80, 48, 75)
for k, val in fs.items():
    print("   frame %-24s vol=%.2f z=%s" % (k, val[0], val[1]))
rep["free_space"]["frame"] = {k: {"vol": v[0], "zs": v[1]} for k, v in fs.items()}

t1 = time.time()
assy = cq.importers.importStep(str(ASSY)).val()
print("assembly imported in %.1fs, %d solids, vol %.0f mm3" % (time.time()-t1, len(assy.Solids()), assy.Volume()))
print("== 5. hole axis z-scan, FULL assembly ==")
axa = {}
for x in (60.0, 76.0):
    for sy in (-1, 1):
        k = "x%.0f_y%+d" % (x, sy*70.0)
        axa[k] = scan(assy, "z", (x, sy*70.0), -20.0, 80.0, 0.3, "assy z @ x=%.0f y=%+.0f" % (x, sy*70.0))
rep["probes"]["assy_hole_axis_z"] = axa
print("== 6. free space, FULL assembly ==")
fsa = {}
fsa["outboard_y85_115"] = boxvol(assy, 40, 100, 85, 115, -5, 30)
fsa["outboard_y83_120_wide"] = boxvol(assy, 20, 120, 83, 120, -5, 30)
fsa["under_rail_x54_82"] = boxvol(assy, 54, 82, 63, 81, -20, 1.0)
fsa["under_rail_x45_92"] = boxvol(assy, 45, 92, 60, 84, -20, 1.0)
fsa["above_leg_z50_80"] = boxvol(assy, 50, 86, 60, 80, 50, 80)
for k, val in fsa.items():
    print("   assy  %-24s vol=%.2f z=%s" % (k, val[0], val[1]))
rep["free_space"]["assembly"] = {k: {"vol": v[0], "zs": v[1]} for k, v in fsa.items()}

(OUT / "report_r54_fit_probe.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
print("wrote report_r54_fit_probe.json  (total %.0fs)" % (time.time()-t0))
