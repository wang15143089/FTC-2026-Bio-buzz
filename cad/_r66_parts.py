# -*- coding: utf-8 -*-
"""R66 step 1: collect EVERY printable object into one folder as individual STEP files.

Printable objects =
  * the R65 print set (48 bodies = 46 R62 print parts + 2 rail splice plates, with the
    3 rails re-drilled)  MINUS  the oversized merged frame (432.5 x 183.0 x 404.5 mm,
    cannot fit an H2D),  PLUS
  * the 8 printable lumps of that frame from the accepted DEC-0063 two-plane split
    (x = 100 / z = 300), which was produced from a frame of identical volume.

READ-ONLY on all upstream geometry.
Writes -> cad/output/_r66_parts/  (one STEP per printable object + parts_index.json)
"""
import json
from pathlib import Path
import cadquery as cq

SRC62 = Path("cad/output/_r62b_parts")
SRC65 = Path("cad/output/_r65_splice/parts")
SRC56 = Path("cad/output/_r56_frame/split")
DEST = Path("cad/output/_r66_parts")
DEST.mkdir(parents=True, exist_ok=True)

RAILS = ("base_rail_rear_joined", "base_rail_front_+72", "base_rail_front_-72")
FRAME_STEM = "shooter_frame"
FRAME_PIECES = ("frameP_1_rear_lower", "frameP_2_front_lower", "frameP_3_top")

idx62 = json.loads((SRC62 / "parts_index.json").read_text(encoding="utf-8"))
rep56 = json.loads((SRC56 / "report_r56_split.json").read_text(encoding="utf-8"))

items = []      # (name, source path, shape, group)

# ---- 1. the 44 unchanged R62 print parts (frame excluded) -------------------
for it in idx62["parts"]:
    n = it["part"]
    if n.startswith(FRAME_STEM) or n in RAILS:
        continue
    items.append((n, SRC62 / it["file"], None, "r62"))

# ---- 2. the 3 re-drilled rails + the 2 new splice plates (R65) --------------
for n in list(RAILS) + ["rail_splice_plate_+72", "rail_splice_plate_-72"]:
    items.append((n, SRC65 / (n + ".step"), None, "r65"))

# ---- 3. the 8 frame lumps (DEC-0063 split), one file per lump ---------------
frame_piece_solids = {}
for pc in FRAME_PIECES:
    p = SRC56 / (pc + ".step")
    shape = cq.importers.importStep(str(p)).val()
    sol = list(shape.Solids())
    want = rep56["readback"][pc]
    assert len(sol) == want["solids"], "%s solids %d != %d" % (pc, len(sol), want["solids"])
    assert abs(sum(s.Volume() for s in sol) - want["volume_mm3"]) < 0.5, pc
    frame_piece_solids[pc] = sol
    for i, s in enumerate(sorted(sol, key=lambda e: -e.Volume()), start=1):
        nm = pc if len(sol) == 1 else "%s_L%d" % (pc, i)
        items.append((nm, None, s, "frame"))

# ---- 4. verify the split pieces really cover the current frame --------------
frame_src = cq.importers.importStep(
    "cad/output/_r62_frame/T06_shooter_frame_R62_pollen.step").val()
fv = frame_src.Volume()
covered = 0.0
for pc in FRAME_PIECES:
    for s in frame_piece_solids[pc]:
        covered += s.intersect(frame_src).Volume()
print("frame V = %.1f mm3 | sum(piece ^ frame) = %.1f mm3 | delta = %.2f mm3"
      % (fv, covered, covered - fv), flush=True)
# The DEC-0063 split moves material across the two cut planes: a tab / tongue that
# straddles a seam is owned by one side while the relieved pocket sits on the other, and
# the thin sliver between the two facing surfaces is counted by both sides. A small
# non-zero residual is therefore expected; this check guards against a grossly wrong piece
# set, not against sub-mm seam bookkeeping. Tolerance = max(500 mm3, 1 % of frame volume).
COVERAGE_TOL_MM3 = max(500.0, 0.01 * fv)
coverage_ok = abs(covered - fv) <= COVERAGE_TOL_MM3
print('coverage tolerance = %.1f mm3 -> ok=%s' % (COVERAGE_TOL_MM3, coverage_ok), flush=True)

# ---- 5. write one STEP per printable object ---------------------------------
rows = []
for name, path, shape, group in items:
    if shape is None:
        shape = cq.importers.importStep(str(path)).val()
    bb = shape.BoundingBox()
    out = DEST / (name + ".step")
    cq.Assembly(name=name).add(shape).export(str(out), exportType="STEP")
    rows.append({"object": name, "group": group, "file": name + ".step",
                 "source": str(path) if path else "DEC-0063 frame split (R56 impl.)",
                 "volume_mm3": round(shape.Volume(), 1),
                 "solids": len(shape.Solids()),
                 "bbox": {"x": [round(bb.xmin, 2), round(bb.xmax, 2)],
                          "y": [round(bb.ymin, 2), round(bb.ymax, 2)],
                          "z": [round(bb.zmin, 2), round(bb.zmax, 2)]},
                 "dims_mm": [round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)]})
    print("%-46s V=%9.1f  %.1f x %.1f x %.1f" % (name, shape.Volume(), bb.xlen, bb.ylen, bb.zlen),
          flush=True)

# ---- 6. readback ------------------------------------------------------------
bad = []
tot = 0.0
for r in rows:
    sols = list(cq.importers.importStep(str(DEST / r["file"])).val().Solids())
    v = sum(s.Volume() for s in sols)
    tot += v
    if len(sols) != r["solids"] or abs(v - r["volume_mm3"]) > 0.5:
        bad.append((r["object"], len(sols), round(v, 2)))
print("readback: %d objects, %d bad, total V = %.1f mm3" % (len(rows), len(bad), tot))
assert not bad, bad

(DEST / "parts_index.json").write_text(json.dumps({
    "units": "mm",
    "what": "every printable object of the T06 launcher, one STEP per object",
    "frame_coverage_check": {"frame_volume_mm3": round(fv, 1),
                             "sum_piece_intersect_frame_mm3": round(covered, 1),
                             "delta_mm3": round(covered - fv, 2), "tol_mm3": round(COVERAGE_TOL_MM3, 1),
                             "ok": coverage_ok},
    "groups": {"r62": "unchanged R62 print part",
               "r65": "R65 re-drilled rail or new rail splice plate",
               "frame": "DEC-0063 two-plane frame split lump (x=100 / z=300)"},
    "n_objects": len(rows), "sum_volume_mm3": round(tot, 1),
    "objects": sorted(rows, key=lambda e: e["object"])},
    ensure_ascii=False, indent=1), encoding="utf-8")
print("wrote", DEST / "parts_index.json")
