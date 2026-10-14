# -*- coding: utf-8 -*-
"""T06 R55 -- interference / fit probe (read-only, writes only a JSON report)."""
import json, sys, time
from pathlib import Path
import cadquery as cq

HERE = Path(__file__).resolve().parent
OUT = HERE / "output" / "_r55_frame"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
FRAME = OUT / "T06_shooter_frame_R55_pollen.step"
ASSY = OUT / "T06_shooter_assembly_R55_pollen.step"

def scan(shape, axis, fixed, lo, hi, r, label):
    p0 = {"x": (lo, fixed[0], fixed[1]), "y": (fixed[0], lo, fixed[1]),
          "z": (fixed[0], fixed[1], lo)}[axis]
    d = {"x": (1,0,0), "y": (0,1,0), "z": (0,0,1)}[axis]
    i = "xyz".index(axis)
    it = cq.Solid.makeCylinder(r, hi-lo, cq.Vector(*p0), cq.Vector(*d)).intersect(shape)
    rows = []
    for s in it.Solids():
        bb = s.BoundingBox()
        a = (bb.xmin, bb.ymin, bb.zmin)[i]; b = (bb.xmax, bb.ymax, bb.zmax)[i]
        if s.Volume() > 0.02:
            rows.append([round(a,2), round(b,2), round(s.Volume(),2)])
    rows.sort()
    print("  %-40s -> %s" % (label, rows))
    return rows

def boxvol(shape, x0,x1,y0,y1,z0,z1):
    x0,x1 = sorted((x0,x1)); y0,y1 = sorted((y0,y1)); z0,z1 = sorted((z0,z1))
    b = cq.Workplane("XY").box(x1-x0, y1-y0, z1-z0).translate(
        ((x0+x1)/2, (y0+y1)/2, (z0+z1)/2)).val()
    it = b.intersect(shape)
    v = 0.0; bb = []
    for s in it.Solids():
        v += s.Volume(); g = s.BoundingBox()
        bb.append([round(g.xmin,1), round(g.xmax,1), round(g.ymin,1), round(g.ymax,1),
                   round(g.zmin,1), round(g.zmax,1), round(s.Volume(),2)])
    return round(v,2), sorted(bb)

t0 = time.time()
frame = cq.importers.importStep(str(FRAME)).val()
print("frame imported %.1fs, %d solids, V=%.0f mm3" % (time.time()-t0, len(frame.Solids()), frame.Volume()))
rep = {"units":"mm","source":FRAME.name,"method":"read-only probe of the exported STEPs"}

print("== 1. new tab material: y-scan through the leg at z=30 (was 68..80, now 68..84) ==")
rep["leg_y_scan_z30"] = {}
for x in (60.0, 76.0):
    rep["leg_y_scan_z30"]["x=%.0f" % x] = scan(frame, "y", (x, 30.0), 40.0, 105.0, 0.3, "frame y @ x=%.0f z=30" % x)

print("== 2. leg column in the widened strip ==")
rep["widened_strip"] = {}
for x in (60.0, 76.0):
    rep["widened_strip"]["x=%.0f z-scan y=82" % x] = scan(frame, "z", (x, 82.0), 5.0, 60.0, 0.3, "frame z @ x=%.0f y=82" % x)
    rep["widened_strip"]["x=%.0f x-scan y=82 z=30" % x] = scan(frame, "x", (82.0, 30.0), 40.0, 105.0, 0.3, "frame x @ y=82 z=30 (leg x=%.0f)" % x)

print("== 3. leg top: what is above the tab within the leg footprint ==")
rep["above_tab"] = {}
for (x, ztop) in ((60.0, 44.0), (76.0, 48.0)):
    v, bb = boxvol(frame, x-6.5, x+6.5, -84, 84, ztop+0.1, ztop+8)
    print("   frame above tab x=%.0f (z %.1f..%.1f): %.2f mm3" % (x, ztop+0.1, ztop+8, v))
    rep["above_tab"]["x=%.0f" % x] = {"vol": v, "solids": bb}

print("== 4. tab corner columns (12 x 16) volume sanity: expect ~ 12*16*(28 / 32) ==")
rep["tab_volume"] = {}
for (x, ztop) in ((60.0, 44.0), (76.0, 48.0)):
    for sy in (-1, 1):
        v, bb = boxvol(frame, x-6.0, x+6.0, sy*68.0, sy*84.0, 16.0, ztop)
        print("   frame tab x=%.0f y%+d: %.1f mm3 (ideal 5376 / 6144)" % (x, sy, v))
        rep["tab_volume"]["x=%.0f y%+d" % (x, sy)] = round(v,1)

t1 = time.time()
assy = cq.importers.importStep(str(ASSY)).val()
print("assembly imported %.1fs, %d solids, V=%.0f mm3" % (time.time()-t1, len(assy.Solids()), assy.Volume()))

print("== 5. INTERFERENCE: frame vs every other solid in the assembly ==")
other = assy.cut(frame)
ov = frame.intersect(other)
ovv = 0.0; ovb = []
for s in ov.Solids():
    if s.Volume() > 0.01:
        g = s.BoundingBox(); ovv += s.Volume()
        ovb.append([round(g.xmin,2), round(g.xmax,2), round(g.ymin,2), round(g.ymax,2),
                    round(g.zmin,2), round(g.zmax,2), round(s.Volume(),3)])
print("   frame cap (assy minus frame) = %.0f mm3 in %d solids" % (other.Volume(), len(other.Solids())))
print("   OVERLAP frame n other = %.3f mm3  %s" % (ovv, ovb if ovb else ""))
rep["interference"] = {"frame_volume": round(frame.Volume(),1),
                       "others_volume": round(other.Volume(),1),
                       "other_solid_count": len(other.Solids()),
                       "overlap_mm3": round(ovv,3), "overlap_solids": ovb,
                       "pass": ovv < 0.01}

print("== 6. risk boxes: widened strip / tab footprint, material from other parts ==")
rep["risk_boxes"] = {}
risks = {
  "strip_y80_84_z16_48_x54_82": (54, 82, 80, 84, 16, 48),
  "strip_y80_84_full":          (0, 220, 80, 84, 0, 60),
  "tab_footprint_x60":          (54, 66, 68, 84, 16, 44),
  "tab_footprint_x76":          (70, 82, 68, 84, 16, 48),
  "outboard_under_rail_y84_100":(40, 100, 84, 100, -12, 20),
}
for k,(x0,x1,y0,y1,z0,z1) in risks.items():
    vf, bf = boxvol(frame, x0,x1,y0,y1,z0,z1)
    vo, bo = boxvol(other, x0,x1,y0,y1,z0,z1)
    print("   %-30s frame=%8.2f  other=%8.2f mm3" % (k, vf, vo))
    if bo: print("      other solids: %s" % bo)
    rep["risk_boxes"][k] = {"frame_mm3": vf, "other_mm3": vo, "other_solids": bo}

print("== 7. headroom above the tab in the FULL assembly (screwdriver + head) ==")
rep["headroom_assy"] = {}
for (x, ztop) in ((60.0, 44.0), (76.0, 48.0)):
    for sy in (-1, 1):
        v, bb = boxvol(assy, x-3.0, x+3.0, sy*76-3.0, sy*76+3.0, ztop+0.3, ztop+22.0)
        print("   assy 6x6 col above tab x=%.0f y%+d: %.2f mm3 %s" % (x, sy, v, bb if bb else ""))
        rep["headroom_assy"]["x=%.0f y%+d" % (x, sy)] = {"vol": v, "solids": bb}

(OUT / "report_r55_fit_probe.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
print("wrote report_r55_fit_probe.json  (total %.0fs)" % (time.time()-t0))
