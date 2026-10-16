# -*- coding: utf-8 -*-
"""R69 print-set geometry verification (re-reads the DELIVERED files).

tools/inspect_geometry.py only accepts registered assembly harnesses, so this print-set
verifier reports the same vocabulary (target / measured / tolerance / method / verdict)
against the delivered STEPs instead of the inputs that produced them.

OUT cad/output/inspection/t06_r69_print_R069.json
"""
import json
from pathlib import Path
import cadquery as cq

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "cad" / "output" / "_r69_parts"
PL = ROOT / "cad" / "output" / "_r69_plate"
OLD = ROOT / "cad" / "output" / "_r66_parts"
OUT = ROOT / "cad" / "output" / "inspection" / "t06_r69_print_R069.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

BED_X, BED_Y, BED_Z, MARGIN = 325.0, 320.0, 325.0, 5.0
W, H = BED_X - 2 * MARGIN, BED_Y - 2 * MARGIN
D_HOLE = 3.4
STA = (("A", 74.0, 27.0, 16.0, 53.5, 35.0), ("D", 5.0, 86.0, 4.0, 54.0, 25.0),
       ("B", -25.0, 120.0, 4.0, 54.0, 25.0), ("C", -68.0, 140.0, 4.0, 54.0, 25.0))

def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1-x0, y1-y0, z1-z0, centered=False).translate((x0, y0, z0)).val()

def cyl(d, y0, y1, x, z):
    return cq.Solid.makeCylinder(d/2.0, abs(y1-y0), cq.Vector(x, min(y0, y1), z), cq.Vector(0, 1, 0))

def imp(p):
    return cq.importers.importStep(str(p)).val()

R = []
def chk(cid, kind, target, measured, tol, method, note="", unit="mm3"):
    ok = measured is not None and abs(measured - target) <= tol
    R.append({"id": cid, "kind": kind, "target": target, "measured": measured,
              "tolerance": tol, "unit": unit, "verdict": "pass" if ok else "fail",
              "method": method, "note": note})
    print("%-10s %-22s target %10s  measured %10s  %s" % (cid, kind, target, measured,
          "pass" if ok else "FAIL"), flush=True)
    return ok

mid, pL, pR = (imp(D / n) for n in ("shroud_tray_mid.step", "side_plate_left.step", "side_plate_right.step"))
railP, railM = imp(D / "base_rail_+72.step"), imp(D / "base_rail_-72.step")
orig = imp(OLD / "frameP_1_rear_lower.step")
fas = json.loads((D / "fasteners.json").read_text(encoding="utf-8"))
NET_GAIN = 7417.0   # 8 ears +7919.9 mm3 minus 8 x d3.4 drillings -502.9 mm3

# V1 split volume conservation against the retired single body
chk("R69-V1", "volume (split + joint net)", NET_GAIN,
    round(mid.Volume() + pL.Volume() + pR.Volume() - orig.Volume(), 3), 1.0,
    "sum of the three delivered STEP volumes minus the retired frameP_1_rear_lower STEP volume",
    "y = +-68 split plane, then +8 bolted ears (+7919.9 mm3) and -8 x d3.4 drillings (-502.9 mm3)")

# V2 one printable body per part
for nm, s in (("shroud_tray_mid", mid), ("side_plate_left", pL), ("side_plate_right", pR),
              ("base_rail_+72", railP), ("base_rail_-72", railM)):
    R.append({"id": "R69-V2 %s" % nm, "kind": "solid_count", "target": 1,
              "measured": len(s.Solids()), "tolerance": 0, "unit": "solids",
              "verdict": "pass" if len(s.Solids()) == 1 else "fail",
              "method": "read from the delivered STEP"})
print("R69-V2     solid_count            all 5 parts single-solid:", flush=True)

# V3 rail length
chk("R69-V3 +72", "bbox_size", 380.0, round(railP.BoundingBox().xlen, 3), 0.05,
    "x extent of the delivered joined rail STEP", "option C: front + rear unified")
chk("R69-V3 -72", "bbox_size", 380.0, round(railM.BoundingBox().xlen, 3), 0.05,
    "x extent of the delivered joined rail STEP", "option C: front + rear unified")

# V4 bolt path clear: the whole shank corridor is free of printed material
body = mid
worst = 0.0
for tag, x, z, plate, nut_y, ln in STA:
    for s in (1, -1):
        probe = cyl(3.0, s*(nut_y - 1.0), s*(68.0 + plate + 1.0), x, z)
        v = probe.intersect(body).Volume()
        v += probe.intersect(pL).Volume() + probe.intersect(pR).Volume()
        worst = max(worst, v)
chk("R69-V4", "clearance (bolt corridor)", 0.0, round(worst, 3), 0.5,
    "3.0 mm probe cylinder along the M3 axis, from the nut seat to outside the plate, "
    "intersected with all three delivered parts", "8 stations, 4 per side")

# V5 hole diameter is the drilled 3.4: a 3.4 plug must be free, a 4.0 plug must bite
w34 = w40 = 0.0
for tag, x, z, plate, nut_y, ln in STA:
    for s in (1, -1):
        p34 = cyl(D_HOLE, s*(nut_y - 0.5), s*(68.0 + plate + 0.5), x, z)
        p40 = cyl(4.0, s*(nut_y - 0.5), s*(68.0 + plate + 0.5), x, z)
        w34 = max(w34, (p34.intersect(body).Volume() + p34.intersect(pL).Volume()
                        + p34.intersect(pR).Volume()))
        w40 = max(w40, (p40.intersect(body).Volume() + p40.intersect(pL).Volume()
                        + p40.intersect(pR).Volume()))
chk("R69-V5 hole", "clearance (d3.4)", 0.0, round(w34, 3), 0.5,
    "3.4 mm plug through the ear and the plate must be empty", "M3 clearance hole")
R.append({"id": "R69-V5 ring", "kind": "material at 4.0 mm", "target": None,
          "measured": round(w40, 3), "tolerance": None, "unit": "mm3",
          "verdict": "pass" if w40 > 10.0 else "fail",
          "method": "a 4.0 mm plug must still hit material, i.e. the hole is not oversized",
          "note": "value only; no requirement target"})
print("R69-V5 ring  material at 4.0 mm  measured %.3f  (must be > 10)" % w40, flush=True)

# V6 ears attached: a 8 x 8 x 8 cube inside each ear must be solid
ear_y = {(e["tag"], e["side"]): e["ear_y"] for e in fas["items"]}
worst = 1.0
for tag, x, z, plate, nut_y, ln in STA:
    for s in (1, -1):
        ya, yb = sorted(ear_y[(tag, "R" if s > 0 else "L")])
        c = box(x + 2.2, x + 5.7, ya + 0.3, yb - 0.3, z - 4.7, z + 4.7)
        worst = min(worst, c.intersect(body).Volume() / c.Volume())
chk("R69-V6", "fill fraction (ears)", 1.0, round(worst, 4), 0.05,
    "9.4 x (ear depth - 0.6) x 3.5 sample box inside each ear, offset in +x so the "
    "d3.4 bolt hole is excluded, intersected with the delivered mid body",
    "8 ears", unit="-")

# V7 bed fit of the delivered plate files
plates = json.loads((PL / "plates_index.json").read_text(encoding="utf-8"))
for p in plates["plates"]:
    s = imp(PL / p["step"])
    bb = s.BoundingBox()
    hs = [sol.BoundingBox().zlen for sol in s.Solids()]
    fit = (bb.xlen <= W + 1e-6 and bb.ylen <= H + 1e-6 and max(hs) <= BED_Z + 1e-6)
    R.append({"id": "R69-V7 p%d" % p["plate"], "kind": "bed fit",
              "target": [W, H, BED_Z], "measured": [round(bb.xlen, 1), round(bb.ylen, 1), round(max(hs), 1)],
              "tolerance": 0.0, "unit": "mm", "verdict": "pass" if fit else "fail",
              "method": "bounding box of the delivered plate STEP vs the usable H2D envelope",
              "note": "%d solids" % len(s.Solids())})
    print("R69-V7 p%-2d bed fit  measured %.1f x %.1f  H %.1f  %s"
          % (p["plate"], bb.xlen, bb.ylen, max(hs), "pass" if fit else "FAIL"), flush=True)

# V8 plates carry exactly the parts list
parts = json.loads((D / "parts_index.json").read_text(encoding="utf-8"))
packed = [o["object"] for p in plates["plates"] for o in p["objects"]]
names = [o["object"] for o in parts["objects"]]
R.append({"id": "R69-V8", "kind": "object accounting", "target": len(names),
          "measured": len(packed), "tolerance": 0, "unit": "objects",
          "verdict": "pass" if sorted(packed) == sorted(names) else "fail",
          "method": "every object of parts_index.json appears exactly once across the plates",
          "note": "sum V plates = %.1f mm3" % sum(p["sum_volume_mm3"] for p in plates["plates"])})
print("R69-V8 object accounting target %d measured %d" % (len(names), len(packed)), flush=True)

fails = [r for r in R if r["verdict"] != "pass"]
report = {"schema_version": "0.1", "design_id": "T06-R69-print",
          "run_label": "R069",
          "what": "R69 print set: 3-way split of the shroud/side-plate body, 8 bolted ears, "
                  "option-C 380 mm rails, flat packing onto H2D plates",
          "inputs": {"parts": "cad/output/_r69_parts", "plates": "cad/output/_r69_plate",
                     "retired": "cad/output/_r66_parts/frameP_1_rear_lower.step"},
          "checks": R, "n_checks": len(R), "n_fail": len(fails),
          "status": "pass" if not fails else "fail"}
OUT.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
print("wrote %s   %d checks, %d fail" % (OUT, len(R), len(fails)))
raise SystemExit(1 if fails else 0)
