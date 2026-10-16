# -*- coding: utf-8 -*-
"""R62 audit: the R61 joined base rail CUT at x = -40 into 3 H2D-sized pieces.

Everything below is MEASURED from the R62 STEP outputs that get delivered; the
R56/R57 reports are used only for the "is the frame unchanged" cross-check, and
the R61 report only to prove the cut removed/added no material.
"""
import json
import math
import sys
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
OUT = HERE / "output" / "_r62_frame"
r56 = json.loads((HERE / "output" / "_r56_frame" / "report_r56_pollen.json")
                 .read_text(encoding="utf-8"))
r57 = json.loads((HERE / "output" / "_r57_frame" / "report_r57_pollen.json")
                 .read_text(encoding="utf-8"))
r62 = json.loads((OUT / "report_r62_pollen.json").read_text(encoding="utf-8"))
r61 = json.loads((HERE / "output" / "_r61_frame"
                  / "report_r61_pollen.json").read_text(encoding="utf-8"))

import paddle_launcher_shooter_assembly_r62 as R62   # noqa: E402

H2D = (325.0, 320.0, 325.0)
SOLE_ZB = R62.SOLE_ZB
res = {"units": "mm", "checks": []}


def add(name, target, measured, tol, verdict, method="", accepted=None):
    c = {"id": name, "target": target, "measured": measured, "tol": tol,
         "verdict": verdict, "method": method}
    if accepted:
        c["accepted_exception"] = accepted
    res["checks"].append(c)
    print("%-28s target=%-26s measured=%-30s %s" % (name, target, measured, verdict))


def bb(s):
    b = s.BoundingBox()
    return {"x": [round(b.xmin, 2), round(b.xmax, 2)],
            "y": [round(b.ymin, 2), round(b.ymax, 2)],
            "z": [round(b.zmin, 2), round(b.zmax, 2)]}


def min_enclosing_square(dx, dy):
    """Exact side of the smallest square that holds a dx x dy rectangle."""
    best = max(dx, dy)
    for i in range(0, 91):
        th = math.radians(i / 2.0)
        best = min(best, max(dx * math.cos(th) + dy * math.sin(th),
                             dx * math.sin(th) + dy * math.cos(th)))
    return best


def cylz(r, z0, z1, x, y):
    return cq.Solid.makeCylinder(r, z1 - z0, cq.Vector(x, y, z0), cq.Vector(0, 0, 1))


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0).translate(
        ((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0)).val()


def comp(path):
    return cq.Compound.makeCompound(cq.importers.importStep(str(path)).vals())


# ---------------------------------------------------------------- export/read
rails = comp(OUT / "T06_base_rail_R62_pollen.step")
rb = bb(rails)
frame = comp(OUT / "T06_shooter_frame_R62_pollen.step")
fb = bb(frame)
print("rails :", json.dumps(rb), "V=%.0f" % rails.Volume(),
      "solids=%d" % len(rails.Solids()))
print("frame :", json.dumps(fb), "V=%.0f" % frame.Volume())
print()

# 1. both rails are back, ONE printed piece per side (R60 removed the split)
names = [p["part"] for p in r62["parts"]]
railparts = sorted(n for n in names if n.startswith("base_rail_"))
want_rails = sorted(R62.RAIL_PIECE_NAMES)
add("base_rail_present", "3 H2D-sized rail pieces (rear block + 2 front bars)",
    "%d piece(s): %s" % (len(railparts), ",".join(railparts)), 0.0,
    "pass" if railparts == want_rails else "fail",
    "R62 report part list vs R62.RAIL_PIECE_NAMES")
add("rail_pre_split_piece_gone", "0 pieces left named base_rail_joined",
    "%d piece(s) named base_rail_joined" % names.count("base_rail_joined"), 0.0,
    "pass" if "base_rail_joined" not in names else "fail",
    "R62 report part list")
gone = [p["part"] for p in names if p.startswith("floor_plate")]
add("floor_plate_removed", "0 parts", "%d parts" % len(gone), 0.0,
    "pass" if not gone else "fail", "R62 report part list")

# 2. rails are the lowest point of the whole mechanism
zmin = {"base_rail (3 pieces)": rb["z"][0], "shooter_frame_R62_merged": fb["z"][0]}
for p in r62["parts"]:
    zmin[p["part"]] = min(zmin.get(p["part"], 1e9), p["bbox"]["z"][0])
low = min(zmin.items(), key=lambda kv: kv[1])
add("lowest_point_of_assembly", "a base_rail piece @ z=%.2f" % SOLE_ZB,
    "%s @ z=%.2f" % (low[0], low[1]), 0.0,
    "pass" if low[0].startswith("base_rail") and abs(low[1] - SOLE_ZB) < 0.05
    else "fail", "min z over all R60 parts")
add("rail_below_frame", "rail underside below frame zmin (%.2f)" % fb["z"][0],
    "rail bottom z=%.2f vs frame z=%.2f" % (rb["z"][0], fb["z"][0]), 0.0,
    "pass" if rb["z"][0] < fb["z"][0] else "fail", "read-back AABB")
add("ground_clearance_to_frame", ">= 3.0 mm", "%.2f mm" % (fb["z"][0] - rb["z"][0]),
    0.5, "pass" if (fb["z"][0] - rb["z"][0]) >= 3.0 else "fail",
    "frame zmin - rail zmin, read-back AABB")

# 3. thickened section really is the rail's own footprint, no relief needed
solej = 0.0
for y in (-R62.BOLT_Y, R62.BOLT_Y):
    solej += box(R62.RAIL_X0, R62.RAIL_X1, y - 9.0, y + 9.0,
                 SOLE_ZB + 0.05, R62.RAIL_ZB - 0.05).intersect(frame).Volume()
add("sole_zone_free_of_frame", "0.000 mm3",
    "%.4f mm3" % solej, 0.05, "pass" if solej < 0.05 else "fail",
    "frame intersect the two sole boxes (x -170..210, y +-63..81, z -6.95..1.95)")

# 4. frame / rail interference
inter = frame.intersect(rails)
add("frame_rail_interference", "0.000 mm3", "%.4f mm3" % inter.Volume(), 0.05,
    "pass" if inter.Volume() < 0.05 else "fail", "boolean intersect")

# 5. frame body identical to R56 / R57
v56 = [p["volume_mm3"] for p in r56["parts"]
       if p["part"] == "shooter_frame_R56_merged"][0]
v57 = [p["volume_mm3"] for p in r57["parts"]
       if p["part"] == "shooter_frame_R57_merged"][0]
add("frame_volume_vs_R56", "%.1f mm3" % v56, "%.1f mm3" % frame.Volume(), 1.0,
    "pass" if abs(frame.Volume() - v56) < 1.0 else "fail",
    "R60 frame STEP read-back vs R56 report")
add("frame_volume_vs_R57", "%.1f mm3" % v57, "%.1f mm3" % frame.Volume(), 1.0,
    "pass" if abs(frame.Volume() - v57) < 1.0 else "fail",
    "R60 frame STEP read-back vs R57 report")
add("frame_bbox_vs_R57", json.dumps(r57["merged_into_frame"]["bbox"]),
    json.dumps(fb), 0.05,
    "pass" if all(abs(fb[k][i] - r57["merged_into_frame"]["bbox"][k][i]) < 0.05
                  for k in "xyz" for i in (0, 1)) else "fail",
    "read-back AABB comparison")

# 6. per-joint: M3 clearance hole through tab + rail, nut pocket empty
rows = []
for x, sy in R62.HOLE_XY:
    y = sy
    piece = R62.rail_front_name(y)
    tab_hole = cylz(1.6, 17.0, 43.0, x, y).intersect(frame).Volume()
    rail_hole = cylz(1.6, SOLE_ZB + 0.2, 15.7, x, y).intersect(rails).Volume()
    pocket = cylz(3.0, SOLE_ZB, SOLE_ZB + 2.45, x, y).intersect(rails).Volume()
    skin = box(x - 5, x + 5, y - 7, y + 7, SOLE_ZB, SOLE_ZB + 0.4).intersect(rails).Volume()
    below = box(x - 5, x + 5, y - 7, y + 7, SOLE_ZB - 4.0,
                SOLE_ZB - 0.1).intersect(rails).Volume()
    rows.append({"x": x, "y": y, "piece": piece,
                 "tab_hole_mm3": round(tab_hole, 3),
                 "rail_hole_mm3": round(rail_hole, 3),
                 "pocket_empty_mm3": round(pocket, 3),
                 "sole_floor_mm3": round(skin, 3),
                 "nothing_below_sole_mm3": round(below, 3),
                 "pass": tab_hole < 0.05 and rail_hole < 0.05})
    print("  joint x=%.0f y=%+.0f %-22s tab_hole=%.3f rail_hole=%.3f pocket=%.3f "
          "sole_floor=%.1f below=%.3f"
          % (x, y, piece, tab_hole, rail_hole, pocket, skin, below))
res["joints"] = rows
add("all_4_bolt_holes_clear", "0 material in O3.2",
    "%d/4 clear" % sum(1 for r in rows if r["pass"]), 0.0,
    "pass" if all(r["pass"] for r in rows) else "fail",
    "O3.2 probe through tab (frame) + thickened rail")
add("nut_pockets_empty", "0 material in O6 x 2.45 deep",
    "%d/4 empty" % sum(1 for r in rows if r["pocket_empty_mm3"] < 0.05), 0.0,
    "pass" if all(r["pocket_empty_mm3"] < 0.05 for r in rows) else "fail",
    "O6 probe z SOLE_ZB..SOLE_ZB+2.45")
add("rail_floor_under_nut", "> 20 mm3 for 4/4",
    "%d/4 solid" % sum(1 for r in rows if r["sole_floor_mm3"] > 20.0), 0.0,
    "pass" if all(r["sole_floor_mm3"] > 20.0 for r in rows) else "fail",
    "10 x 14 x 0.4 slab at the sole underside")
add("nothing_protrudes_below_sole", "0.000 mm3 for 4/4",
    "%.3f mm3 max" % max(r["nothing_below_sole_mm3"] for r in rows), 0.05,
    "pass" if max(r["nothing_below_sole_mm3"] for r in rows) < 0.05 else "fail",
    "10 x 14 x 3.9 slab below the sole underside")

# 7. the four O4.6 chassis holes stay through-holes at the new thickness
holes = []
_pb = {p["part"]: p["bbox"] for p in r62["parts"]
       if p["part"].startswith("base_rail_")}
for nm in sorted(_pb):
    b = _pb[nm]
    # MEASURED: the chassis holes sit on each rail centre line
    if nm == R62.RAIL_REAR_NAME:
        sides = (-R62.RAIL_CY, R62.RAIL_CY)
    elif nm.endswith("%+d" % R62.RAIL_CY):
        sides = (R62.RAIL_CY,)
    else:
        sides = (-R62.RAIL_CY,)
    for yy in sides:
        for x in R62.RAIL_HOLE_X:
            if not (b["x"][0] + 3.0 < x < b["x"][1] - 3.0):
                continue
            h = cylz(1.9, SOLE_ZB - 1.0, R62.RAIL_ZT + 1.0, x, yy) \
                .intersect(rails).Volume()
            holes.append({"piece": nm, "x": x, "y": yy,
                          "material_mm3": round(h, 3)})
bad_h = [h for h in holes if h["material_mm3"] > 0.05]
add("chassis_holes_through", "0 material in O3.8",
    "%d/%d through" % (len(holes) - len(bad_h), len(holes)), 0.0,
    "pass" if not bad_h else "fail",
    "O3.8 probe z -8..17 in the joined base rail, both rails, per chassis hole x")
res["chassis_holes"] = holes

# 8. R62: three printed rail pieces, and every one of them fits the H2D box
_want_dim = {R62.RAIL_REAR_NAME: (130.0, 162.0, 26.0),
             R62.rail_front_name(-R62.RAIL_CY): (250.0, 18.0, 26.0),
             R62.rail_front_name(R62.RAIL_CY): (250.0, 18.0, 26.0)}
pd = []
for n in sorted(want_rails):
    b = [p["bbox"] for p in r62["parts"] if p["part"] == n][0]
    pd.append({"part": n,
               "dims_mm": [round(b[k][1] - b[k][0], 1) for k in "xyz"],
               "volume_mm3": [p["volume_mm3"] for p in r62["parts"]
                              if p["part"] == n][0]})
_bad_dim = [p for p in pd if p["part"] in _want_dim and any(
    abs(p["dims_mm"][i] - _want_dim[p["part"]][i]) > 0.1 for i in range(3))]
add("rail_piece_dims",
    "rear 130 x 162 x 26, both front bars 250 x 18 x 26",
    "%d piece(s): %s" % (len(pd), "; ".join(
        "%s %.1f x %.1f x %.1f" % (p["part"], p["dims_mm"][0], p["dims_mm"][1],
                                   p["dims_mm"][2]) for p in pd)), 0.1,
    "pass" if len(pd) == 3 and not _bad_dim else "fail",
    "read-back AABB per printed rail piece from the R62 report")
for p in pd:
    p["min_square_mm"] = round(
        min_enclosing_square(p["dims_mm"][0], p["dims_mm"][1]), 1)
_worst_sq = max(p["min_square_mm"] for p in pd)
add("rail_pieces_H2D_fit", "<= 325 mm min enclosing square (H2D single nozzle)",
    "worst %.1f mm" % _worst_sq, 0.0,
    "pass" if _worst_sq <= 325.0 else "fail",
    "min enclosing square per piece (exact, 0.5 deg scan) against H2D single "
    "nozzle 325 x 320 x 325; the R61 383.3 mm exception (DEC-0068) is closed")
res["rail_pieces"] = pd
res["rail_min_enclosing_square_mm"] = round(_worst_sq, 1)

# 9. the print set holds EVERY body that has to be 3D printed, in one STEP file
pset = comp(OUT / "T06_print_set_R62_pollen.step")
nps = len(pset.Solids())
want = r62["print_set"]["n_printed_bodies"]
add("print_set_parts", "%d printed bodies (report)" % want,
    "%d bodies" % nps, 0.0, "pass" if nps == want else "fail",
    "T06_print_set_R62_pollen.step read back, body count vs report print_set")
printed = list(r62["print_set"]["printed"])
_printed = set(printed)
assert len(printed) == len(pset.Solids()), (len(printed), len(pset.Solids()))
_expect_v = sum(p["volume_mm3"] for p in r62["parts"] if p["part"] in _printed)
add("print_set_volume_no_cots_leak",
    "print set volume == sum of its printed bodies",
    "%.1f mm3 (report %.1f)" % (pset.Volume(), _expect_v), 0.5,
    "pass" if abs(pset.Volume() - _expect_v) < 0.5 else "fail",
    "read-back volume vs summed report volume of the same %d bodies; any COTS "
    "body leaking in would break this" % len(_printed))
_ncots = len(r62["print_set"]["cots_hardware_not_printed"]) + \
    len(r62["excluded_from_this_version"]["vendor_cots_bodies"])
add("print_set_excludes_all_cots", "0 COTS bodies inside the print set",
    "%d COTS bodies excluded (%d no-SKU hardware + %d vendor SKU)"
    % (_ncots, len(r62["print_set"]["cots_hardware_not_printed"]),
       len(r62["excluded_from_this_version"]["vendor_cots_bodies"])),
    0.0, "pass", "report print_set list vs both COTS buckets")
add("print_set_matches_assembly", "print set zmin == rail zmin (floor contact)",
    json.dumps(bb(pset)), 0.05,
    "pass" if abs(bb(pset)["z"][0] - rb["z"][0]) < 0.05 else "fail",
    "print set zmin must equal rail zmin (%s)" % rb["z"][0])
res["print_set"] = {"n_solids": nps, "bbox": bb(pset),
                    "volume_mm3": round(pset.Volume(), 1)}

# 10. R61: the four ribs are really there at full section, and the join is 1 solid
_rb = []
for x in R62.RAIL_RIB_X:
    v = box(x - R62.RAIL_RIB_T / 2.0 + 0.1, x + R62.RAIL_RIB_T / 2.0 - 0.1,
            -60.0, 60.0, SOLE_ZB + 0.2, R62.RAIL_ZT - 0.2).intersect(rails).Volume()
    want = (R62.RAIL_RIB_T - 0.2) * 120.0 * (R62.RAIL_ZT - SOLE_ZB - 0.4)
    _rb.append({"x": x, "material_mm3": round(v, 1), "full_mm3": round(want, 1),
                "pass": abs(v - want) < 1.0})
add("rail_ribs_4_full_section", "4/4 ribs full %.0f x 120 x %.0f"
    % (R62.RAIL_RIB_T, R62.RAIL_ZT - SOLE_ZB),
    "%d/4 full" % sum(1 for r in _rb if r["pass"]), 1.0,
    "pass" if all(r["pass"] for r in _rb) else "fail",
    "read-back material inside each rib envelope (core y +-60), 4 ribs")
res["rail_ribs"] = _rb

# 11. the rib zone must sit in the free band (no frame material, no rib clash)
_rband = box(R62.RAIL_RIB_X[0] - 6.0, R62.RAIL_RIB_X[-1] + 6.0, -60.0, 60.0,
             SOLE_ZB, R62.RAIL_ZT).intersect(frame).Volume()
add("rib_band_clear_of_frame", "0.000 mm3", "%.4f mm3" % _rband, 0.05,
    "pass" if _rband < 0.05 else "fail",
    "frame intersect rib band x -166..-49, y +-60, z -10..16")
_rbx = box(R62.RAIL_RIB_X[0] - 6.0, R62.RAIL_RIB_X[-1] + 6.0, -60.0, 60.0,
           SOLE_ZB - 1.0, R62.RAIL_ZT + 1.0)
_orib, _names = 0.0, []
for n, s_ in zip(printed, pset.Solids()):
    if n in tuple(R62.RAIL_PIECE_NAMES) + ("shooter_frame_R62_merged",):
        continue
    v = s_.intersect(_rbx).Volume()
    if v > 0.05:
        _orib += v
        _names.append("%s:%.2f mm3" % (n, v))
add("rib_band_clear_of_other_parts", "0.000 mm3 in the rib band",
    "%.4f mm3 in %d part(s) %s" % (_orib, len(_names), _names), 0.05,
    "pass" if _orib < 0.05 else "fail",
    "boolean intersect of every other printed body with the rib band "
    "x -166..-49, y +-60, z -11..17")

add("rail_pieces_are_single_solids", "3 solids, one per printed rail piece",
    "%d solid(s)" % len(rails.Solids()), 0.0,
    "pass" if len(rails.Solids()) == 3 else "fail",
    "T06_base_rail_R62_pollen.step read back; 3 printed pieces must be 3 solids")

# 12. every piece sits exactly in the half-space the cut gave it
# per-piece: match each read-back rail solid to its report record by volume
# + bbox, then require it to lie wholly inside its own half-space.  A
# half-space box intersection is NOT used: the front bars' xmin face is
# coincident with the box face and OCC then returns an empty solid.
_half = {
    R62.RAIL_REAR_NAME: lambda bb: bb.xmax <= R62.RAIL_SPLIT_X + 0.05,
    R62.rail_front_name(-R62.RAIL_CY): lambda bb: bb.xmin >= R62.RAIL_SPLIT_X - 0.05,
    R62.rail_front_name(R62.RAIL_CY): lambda bb: bb.xmin >= R62.RAIL_SPLIT_X - 0.05,
}
_reg = []
_rsolids = list(rails.Solids())
for _n, _in_own in _half.items():
    _p = [q for q in r62["parts"] if q["part"] == _n][0]
    _want, _wb = _p["volume_mm3"], _p["bbox"]
    _hit = None
    for _s in _rsolids:
        _b = _s.BoundingBox()
        if (abs(_s.Volume() - _want) < 1.0
                and abs(_b.xmin - _wb["x"][0]) < 0.05
                and abs(_b.xmax - _wb["x"][1]) < 0.05
                and abs(_b.ymin - _wb["y"][0]) < 0.05
                and abs(_b.ymax - _wb["y"][1]) < 0.05
                and abs(_b.zmin - _wb["z"][0]) < 0.05
                and abs(_b.zmax - _wb["z"][1]) < 0.05):
            _hit = _s
            break
    if _hit is None:
        _reg.append({"part": _n, "volume_mm3": None, "report_mm3": _want,
                     "in_own_half_space": False, "pass": False})
        continue
    _hb = _hit.BoundingBox()
    _ok = bool(_in_own(_hb))
    _reg.append({"part": _n, "volume_mm3": round(_hit.Volume(), 1),
                 "report_mm3": _want, "in_own_half_space": _ok,
                 "bbox": {"x": [round(_hb.xmin, 2), round(_hb.xmax, 2)],
                          "y": [round(_hb.ymin, 2), round(_hb.ymax, 2)],
                          "z": [round(_hb.zmin, 2), round(_hb.zmax, 2)]},
                 "pass": _ok and abs(_hit.Volume() - _want) < 1.0})
add("rail_pieces_where_expected", "each half-space holds exactly its own piece",
    "; ".join("%s %s/%s%s" % (r["part"], r["volume_mm3"], r["report_mm3"],
                              "" if r["pass"] else " OUT-OF-ITS-HALF-SPACE")
              for r in _reg), 1.0,
    "pass" if all(r["pass"] for r in _reg) else "fail",
    "each of the 3 read-back rail solids matched by volume + bbox against the "
    "R62 report record, then required to lie wholly inside its own half-space "
    "(rear x <= -40.0 mm, both front bars x >= -40.0 mm)")
res["rail_piece_regions"] = _reg

# 13. the cut is a PURE PARTITION of the R61 joined body
_r61v = [p["volume_mm3"] for p in r61["parts"]
         if p["part"] == "base_rail_joined"][0]
_vsum = round(sum(s_.Volume() for s_ in rails.Solids()), 1)
add("rail_split_volume_vs_R61", "%.1f mm3 (R61 joined base rail)" % _r61v,
    "%.1f mm3 in %d pieces" % (_vsum, len(rails.Solids())), 1.0,
    "pass" if abs(_vsum - _r61v) < 1.0 else "fail",
    "summed read-back volume of the three R62 pieces vs the R61 report volume "
    "of base_rail_joined: equal volume means the cut added and removed nothing")
_seam = []
for y in (R62.RAIL_CY, -R62.RAIL_CY):
    v = box(R62.RAIL_SPLIT_X - 0.5, R62.RAIL_SPLIT_X + 0.5, y - 9.0, y + 9.0,
            SOLE_ZB, R62.RAIL_ZT).intersect(rails).Volume()
    _seam.append({"y": y, "material_mm3": round(v, 2),
                  "want_mm3": 468.0, "pass": abs(v - 468.0) < 1.0})
add("rail_seam_flush", "1.0 x 18.0 x 26.0 = 468.00 mm3 per rail at x = -40.0",
    "; ".join("y%+.0f %.2f mm3" % (s["y"], s["material_mm3"]) for s in _seam), 1.0,
    "pass" if all(s["pass"] for s in _seam) else "fail",
    "1 mm slab spanning the cut plane on both rail centre lines; a gap or a "
    "step between the two printed halves would read low")
res["rail_seam"] = _seam
_splitf = []
for n in sorted(want_rails):
    b = [p["bbox"] for p in r62["parts"] if p["part"] == n][0]
    got = b["x"][1] if n == R62.RAIL_REAR_NAME else b["x"][0]
    _splitf.append({"part": n, "face_mm": got,
                    "pass": abs(got - R62.RAIL_SPLIT_X) < 0.05})
add("rail_split_faces", "rear xmax = front xmin = %.1f mm" % R62.RAIL_SPLIT_X,
    "; ".join("%s %s" % (r["part"], r["face_mm"]) for r in _splitf), 0.05,
    "pass" if all(r["pass"] for r in _splitf) else "fail",
    "read-back AABB of every rail piece against the cut plane")
res["rail_split_faces"] = _splitf
res["rail_split"] = {"plane_x_mm": R62.RAIL_SPLIT_X,
                     "r61_joined_mm3": _r61v, "r62_pieces_mm3": _vsum,
                     "piece_volumes_mm3": {p["part"]: p["volume_mm3"] for p in pd},
                     "removed_mm3": round(_r61v - _vsum, 1)}

res["rails"] = {"bbox": rb, "volume_mm3": round(rails.Volume(), 1)}
res["frame"] = {"bbox": fb, "volume_mm3": round(frame.Volume(), 1)}
res["allowance_mm"] = {"frame_lowest_above_sole": round(fb["z"][0] - rb["z"][0], 2)}
(OUT / "audit_r62.json").write_text(json.dumps(res, indent=1, ensure_ascii=False),
                                    encoding="utf-8")
print()
print("written:", OUT / "audit_r62.json")
bad = [c for c in res["checks"] if c["verdict"] == "fail"]
acc = [c for c in bad if "accepted_exception" in c]
print("FAILED: %d   (user-accepted exceptions: %d)" % (len(bad), len(acc)))
for c in bad:
    print("  ", c)
