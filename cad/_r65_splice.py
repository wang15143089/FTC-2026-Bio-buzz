# -*- coding: utf-8 -*-
"""R65 generator (derived): add a side splice plate + 2x M3 cross-seam bolts per rail.

Reads R62 delivery files only (read-only), removes nothing but the 4 x O3.4 bolt holes,
adds 2 new printed parts. R62 products are untouched; output goes to _r65_splice/.
Units: mm.
"""
import json
from pathlib import Path
import cadquery as cq

SRC = Path("cad/output/_r62_frame/T06_print_set_R62_pollen.step")
PARTS = Path("cad/output/_r62b_parts")
DEST = Path("cad/output/_r65_splice")
DEST.mkdir(parents=True, exist_ok=True)
(DEST / "parts").mkdir(exist_ok=True)

RAILS = ("base_rail_rear_joined", "base_rail_front_+72", "base_rail_front_-72")
SEAM_X = -40.0
BACK_HOLE_X = -66.0      # rear side of the seam
FRONT_HOLE_X = -16.0     # front side of the seam
HOLE_Z = -3.0            # low in the 26 mm rail section: clears the frame web on BOTH sides
                         # (scanned: z=+3 is blocked by shooter_frame_R62_merged at x>=-20 on +Y)
R_HOLE = 3.4 / 2.0
PLATE_T = 5.0            # plate thickness along Y
PLATE_X = (-80.0, 0.0)   # 80 mm long, 40 mm each side of the seam
RAIL_Y = (63.0, 81.0)    # rail cross-section (KNOWN from R60/R61/R62)

# ---------- 1) read the R62 print set, name every body ----------
idx = json.loads((PARTS / "parts_index.json").read_text(encoding="utf-8"))
key_lut = {}
for p in idx["parts"]:
    k = (round(p["volume_mm3"], 1), tuple(round(v, 2) for v in
              (p["bbox"]["x"][0], p["bbox"]["x"][1], p["bbox"]["y"][0], p["bbox"]["y"][1],
               p["bbox"]["z"][0], p["bbox"]["z"][1])))
    assert k not in key_lut, "duplicate key %s" % (k,)
    key_lut[k] = p["part"]

src = cq.importers.importStep(str(SRC)).val()
bodies = list(src.Solids())
print("R62 print set: %d solids" % len(bodies))
named = {}
for s in bodies:
    bb = s.BoundingBox()
    k = (round(s.Volume(), 1), tuple(round(v, 2) for v in
              (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax)))
    assert k in key_lut, "unmatched body %s" % (k,)
    named[key_lut[k]] = s
print("matched %d / %d bodies to names" % (len(named), len(bodies)))
assert len(named) == len(bodies)

# ---------- 2) drill the 4 cross-seam holes ----------
def drill_cyl(x, ysign):
    y0 = 90.0 * ysign
    return cq.Solid.makeCylinder(R_HOLE, 45.0, cq.Vector(x, y0, HOLE_Z), cq.Vector(0, -ysign, 0))

drilled_removed = 0.0
for name in RAILS:
    s = cq.importers.importStep(str(PARTS / (name + ".step"))).val()
    xs = [BACK_HOLE_X] if "rear" in name else [FRONT_HOLE_X]
    ys = (1, -1) if "rear" in name else ((1,) if name.endswith("+72") else (-1,))
    for x in xs:
        for ys_ in ys:
            c = drill_cyl(x, ys_)
            before = s.Volume()
            s = s.cut(c)
            drilled_removed += before - s.Volume()
            named[name] = s
print("drilled: removed %.2f mm3 (expect ~%.2f for 4 holes x O3.4 x 18 mm)"
      % (drilled_removed, 4 * 3.141592653589793 * R_HOLE ** 2 * 18.0))

# ---------- 3) build the 2 splice plates ----------
def make_plate(ysign):
    y0, y1 = (RAIL_Y[1], RAIL_Y[1] + PLATE_T) if ysign > 0 else (-RAIL_Y[1] - PLATE_T, -RAIL_Y[1])
    p = cq.Workplane("XY").box(PLATE_X[1] - PLATE_X[0], y1 - y0, 26.0, centered=False) \
        .translate((PLATE_X[0], y0, -10.0)).val()
    for x in (BACK_HOLE_X, FRONT_HOLE_X):
        p = p.cut(drill_cyl(x, ysign))
    p = p.clean()
    assert len(p.Solids()) == 1, (ysign, len(p.Solids()))
    return p

plates = {"rail_splice_plate_+72": make_plate(1), "rail_splice_plate_-72": make_plate(-1)}
for n, p in plates.items():
    bb = p.BoundingBox()
    print("%-24s V=%.1f  x[%.1f,%.1f] y[%.1f,%.1f] z[%.1f,%.1f]  solids=%d"
          % (n, p.Volume(), bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax, len(p.Solids())))

# ---------- 4) export ----------
order = sorted(named) + sorted(plates)
assy = cq.Assembly(name="T06_print_set_R65_pollen")
for n in order:
    s = named.get(n) or plates[n]
    assy.add(s, name=n, color=cq.Color(0.55, 0.65, 0.85, 1.0))
out = DEST / "T06_print_set_R65_pollen.step"
assy.export(str(out), exportType="STEP")
print("wrote %s (%.2f MB, %d bodies)" % (out, out.stat().st_size / 1e6, len(order)))

for n in list(RAILS) + list(plates):
    s = named.get(n) or plates[n]
    cq.Assembly(name=n + "_single").add(s, name=n).export(str(DEST / "parts" / (n + ".step")), exportType="STEP")
print("wrote %d individual parts to %s" % (len(RAILS) + len(plates), DEST / "parts"))

# ---------- 5) readback ----------
rb = cq.importers.importStep(str(out)).val()
sol = list(rb.Solids())
vol = sum(x.Volume() for x in sol)
want = sum(s.Volume() for s in named.values()) + sum(p.Volume() for p in plates.values())
bb = rb.BoundingBox()
ok_n = len(sol) == 48
ok_v = abs(vol - want) < 1.0
print("readback: %d solids (want 48) -> %s" % (len(sol), "OK" if ok_n else "FAIL"))
print("readback: V=%.1f vs %.1f (d=%.2f) -> %s" % (vol, want, vol - want, "OK" if ok_v else "FAIL"))
print("readback: bbox x[%.1f,%.1f] y[%.1f,%.1f] z[%.1f,%.1f]"
      % (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax))
json.dumps  # noqa
(DEST / "report_r65_pollen.json").write_text(json.dumps({
    "units": "mm",
    "source": "cad/output/_r62_frame/T06_print_set_R62_pollen.step (read-only) + _r62b_parts/*.step",
    "what": "R65 = R62 print set + 4 x O3.4 cross-seam bolt holes - 4 hole volumes + 2 x rail_splice_plate",
    "seam_x": SEAM_X, "back_hole_x": BACK_HOLE_X, "front_hole_x": FRONT_HOLE_X,
    "hole_z": HOLE_Z, "hole_dia": 3.4, "plate_thickness_mm": PLATE_T,
    "plate_x_mm": list(PLATE_X), "plate_y_mm": [RAIL_Y[1], RAIL_Y[1] + PLATE_T],
    "removed_volume_mm3": round(drilled_removed, 2),
    "added_volume_mm3": round(sum(p.Volume() for p in plates.values()), 1),
    "n_parts": len(order), "total_volume_mm3": round(vol, 1),
    "readback": {"solids": len(sol), "solids_ok": ok_n, "volume_ok": ok_v,
                 "bbox": [round(v, 2) for v in (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax)]},
    "fasteners": "M3 x 30 socket cap + M3 nut + 1 washer, 2 per rail = 4 sets (CALCULATED)",
    "parts": order}, ensure_ascii=False, indent=1), encoding="utf-8")
print("wrote", DEST / "report_r65_pollen.json")
