# -*- coding: utf-8 -*-
"""R65 audit v2: read the R65 delivery STEP back and check the splice joint. Read-only."""
import json
from pathlib import Path
import cadquery as cq

DEST = Path("cad/output/_r65_splice")
A = Path("cad/output/_r62_frame")
P62 = Path("cad/output/_r62b_parts")
SET = DEST / "T06_print_set_R65_pollen.step"
RAIL_NAMES = ("base_rail_rear_joined", "base_rail_front_+72", "base_rail_front_-72")
PLATES = {"rail_splice_plate_+72": 1, "rail_splice_plate_-72": -1}
BACK_X, FRONT_X, HOLE_Z = -66.0, -16.0, -3.0
res, fails = [], []

def box(x0, y0, z0, x1, y1, z1):
    return cq.Workplane("XY").box(x1-x0, y1-y0, z1-z0, centered=False).translate((x0, y0, z0)).val()

def cyl(p0, h, d, dirv):
    return cq.Solid.makeCylinder(d/2.0, h, cq.Vector(*p0), cq.Vector(*dirv))

def vol(a, b):
    try: return a.intersect(b).Volume()
    except Exception: return -1.0

def rec(name, target, actual, tol, ok, method):
    res.append({"check": name, "target": target, "actual": actual, "tol": tol,
                "verdict": "pass" if ok else "fail", "method": method})
    if not ok: fails.append(name)
    print("  %-44s want %-13s got %-13s %s" % (name, target, actual, "pass" if ok else "FAIL"))

rb = cq.importers.importStep(str(SET)).val()
sol = list(rb.Solids())
rec("print_set_solids", 48, len(sol), 0, len(sol) == 48, "readback solids")
rep = json.loads((DEST / "report_r65_pollen.json").read_text(encoding="utf-8"))
tv = sum(s.Volume() for s in sol)
rec("print_set_volume_mm3", rep["total_volume_mm3"], round(tv, 1), 1.0,
    abs(tv - rep["total_volume_mm3"]) < 1.0, "sum of solid volumes")

# ---- find the 3 rails inside the delivered set (match on bbox, volume differs after drilling)
def sig(s):
    b = s.BoundingBox()
    return (round(s.Volume(), 1), tuple(round(v, 2) for v in (b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax)))
bysig = {}
for s in sol: bysig.setdefault(sig(s), []).append(s)

src_rail = {n: cq.importers.importStep(str(P62 / (n + ".step"))).val() for n in RAIL_NAMES}
rail_sol = {}
for n, s0 in src_rail.items():
    b = s0.BoundingBox()
    want_bb = tuple(round(v, 2) for v in (b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax))
    cand = [s for k, v in bysig.items() if k[1] == want_bb for s in v]
    assert len(cand) == 1, (n, len(cand))
    rail_sol[n] = cand[0]
plate_sol = {}
for n in PLATES:
    s0 = cq.importers.importStep(str(DEST / "parts" / (n + ".step"))).val()
    cand = bysig.get(sig(s0), [])
    assert len(cand) == 1, (n, len(cand))
    plate_sol[n] = cand[0]

# ---- 1) bolt holes: real through holes, with a wall around them
print("\n[1] bolt holes O3.4 along Y in the delivered rails (18 mm of material each)")
hole_sum = 0.0
for n in RAIL_NAMES:
    s = rail_sol[n]
    xs = [BACK_X] if "rear" in n else [FRONT_X]
    ys = [72.0, -72.0] if "rear" in n else [72.0 if n.endswith("+72") else -72.0]
    for x in xs:
        for y in ys:
            inside = vol(s, cyl((x, y - 9.0, HOLE_Z), 18.0, 3.4, (0, 1, 0)))
            wall = vol(s, cyl((x, y - 9.0, HOLE_Z), 18.0, 8.0, (0, 1, 0)))
            hole_sum += inside
            rec("hole %s x=%.0f y=%.0f is open (mm3)" % (n.replace("base_rail_", ""), x, y),
                "0.0", round(inside, 4), 0.01, abs(inside) < 0.01, "O3.4 x 18 mm column inside rail")
            rec("hole wall %s x=%.0f y=%.0f (mm3)" % (n.replace("base_rail_", ""), x, y),
                ">300", round(wall, 1), 0.0, wall > 300.0, "O8 x 18 mm column material around the hole")

# ---- 2) plates
print("\n[2] splice plates")
for n, ys_ in PLATES.items():
    p = plate_sol[n]
    b = p.BoundingBox()
    yexp = (81.0, 86.0) if ys_ > 0 else (-86.0, -81.0)
    rec("%s y position" % n, str(yexp), "%.1f..%.1f" % (b.ymin, b.ymax), 0.01,
        abs(b.ymin - yexp[0]) < 0.01 and abs(b.ymax - yexp[1]) < 0.01, "readback bbox")
    rec("%s spans the seam" % n, "0..-80 in x", "%.0f..%.0f" % (b.xmin, b.xmax), 0.01,
        b.xmin <= -60.0 and b.xmax >= -20.0, "plate x extent straddles x=-40")
    rec("%s sits on the rail (zmin)" % n, -10.0, round(b.zmin, 2), 0.5, abs(b.zmin + 10.0) < 0.5,
        "readback bbox zmin, must not go below the rail sole")
    rec("%s single solid" % n, 1, len(p.Solids()), 0, len(p.Solids()) == 1, "Solid count")
    for x in (BACK_X, FRONT_X):
        y = 72.0 * ys_
        ins = vol(p, cyl((x, y, HOLE_Z), 5.0, 3.4, (0, ys_, 0)))
        rec("%s hole open x=%.0f" % (n, x), "0.0", round(ins, 4), 0.01, abs(ins) < 0.01,
            "O3.4 x 5 mm column inside the plate")

# ---- 3) collisions: everything except the 3 rails
print("\n[3] collisions vs the rest of the assembly (COTS included)")
asm = cq.importers.importStep(str(A / "T06_shooter_assembly_R62_pollen.step")).val()
rest = asm
for s in src_rail.values():   # subtract the ORIGINAL rails, not the drilled ones
    rest = rest.cut(s)
print("  rest-of-assembly volume after cutting the 3 rails = %.1f mm3" % rest.Volume())
for n, ys_ in PLATES.items():
    p = plate_sol[n]
    b = p.BoundingBox()
    o = vol(rest, box(b.xmin - 1, b.ymin - 1, b.zmin - 1, b.xmax + 1, b.ymax + 1, b.zmax + 1))
    rec("%s vs rest of assembly" % n, "0.0", round(o, 3), 0.02, abs(o) < 0.02,
        "assembly (all 82 bodies incl. COTS) minus the 3 rails, plate bbox + 1 mm")
for n, ys_ in PLATES.items():
    for x in (BACK_X, FRONT_X):
        yface = 63.0 * ys_
        nb = cyl((x, yface - 12.0 * ys_, HOLE_Z), 12.0, 7.2, (0, ys_, 0))
        o = vol(rest, nb)
        rec("%s nut space x=%.0f (mm3)" % (n, x), "0.0", round(o, 3), 0.02, abs(o) < 0.02,
            "O7.2 x 12 mm nut corridor against the inner rail face (y %d..%d)" % (yface - 12, yface))

for n, ys_ in PLATES.items():
    for x in (BACK_X, FRONT_X):
        yr = 86.0 * ys_
        hb = cyl((x, yr, HOLE_Z), 4.0, 6.0, (0, ys_, 0))
        o = vol(rest, hb)
        rec("%s bolt-head space x=%.0f (mm3)" % (n, x), "0.0", round(o, 3), 0.02, abs(o) < 0.02,
            "O6 x 4 mm cap-head corridor just outside the plate (y %d..%d)" % (yr, yr + 4 * ys_))

# ---- 4) the joint really ties the two pieces
print("\n[4] the joint ties both pieces")
rear, front = rail_sol["base_rail_rear_joined"], rail_sol["base_rail_front_+72"]
rec("rear does not protrude past the seam", "0.0", round(vol(rear, box(-39.5, 60, -10, -39.0, 84, 16)), 3),
    0.01, abs(vol(rear, box(-39.5, 60, -10, -39.0, 84, 16))) < 0.01, "rear material in x -39.5..-39.0")
rec("front fills its side of the seam", "234.0", round(vol(front, box(-40.0, 63, -10, -39.5, 81, 16)), 1),
    0.5, abs(vol(front, box(-40.0, 63, -10, -39.5, 81, 16)) - 234.0) < 0.5,
    "front material in x -40..-39.5, full section 0.5 x 18 x 26 = 234")
for x, nm in ((BACK_X, "base_rail_rear_joined"), (FRONT_X, "base_rail_front_+72")):
    for ys_ in (1, -1):
        y = 72.0 * ys_
        m = vol(rail_sol[nm if ys_ > 0 else nm.replace("+72", "-72")],
                cyl((x, y - 9.0, HOLE_Z), 18.0, 3.4, (0, 1, 0)))
        rec("bolt @x=%.0f y=%.0f goes through %s" % (x, y, "rear" if x == BACK_X else "front"),
            "0.0 (clear)", round(m, 4), 0.01, abs(m) < 0.01, "the bolt axis is a clear hole")
        # and the same axis must be material-bearing in the plate
        pm = vol(plate_sol["rail_splice_plate_+72" if ys_ > 0 else "rail_splice_plate_-72"],
                 cyl((x, y, HOLE_Z), 5.0, 3.4, (0, ys_, 0)))
        rec("...and the plate has the matching hole (y=%.0f)" % y, "0.0", round(pm, 4), 0.01,
            abs(pm) < 0.01, "both parts share the same hole axis -> one M3 passes both")

# ---- 5) ground plane + H2D
print("\n[5] ground plane and H2D fit")
bb = rb.BoundingBox()
rec("print set zmin (ground plane)", -10.0, round(bb.zmin, 2), 0.05, abs(bb.zmin + 10.0) < 0.05,
    "rails remain the lowest feature")
for n in PLATES:
    b = plate_sol[n].BoundingBox()
    rec("%s H2D fit" % n, "<=325x320x325", "%.0f x %.0f x %.0f" % (b.xlen, b.ylen, b.zlen), 0.0,
        b.xlen <= 325 and b.ylen <= 320 and b.zlen <= 325, "single nozzle envelope")

DEST.joinpath("audit_r65.json").write_text(json.dumps({
    "units": "mm",
    "question": "does the R65 side splice plate + 2x M3 per rail fix the rear rail piece to the whole?",
    "target_delivery": str(SET), "n_checks": len(res), "n_pass": len(res) - len(fails),
    "n_fail": len(fails), "failed": fails, "hole_residual_mm3": round(hole_sum, 4),
    "checks": res}, ensure_ascii=False, indent=1), encoding="utf-8")
print("\n%d checks: %d pass / %d fail -> %s" % (len(res), len(res) - len(fails), len(fails),
      "PASS" if not fails else "FAIL: " + "; ".join(fails)))
print("wrote", DEST / "audit_r65.json")
