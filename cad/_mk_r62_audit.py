# -*- coding: utf-8 -*-
"""Generate cad/_r62_audit.py from cad/_r61_audit.py (read-back only)."""
from pathlib import Path

src = Path("cad/_r61_audit.py").read_text(encoding="utf-8")
R = []


def rep(old, new, n=None):
    global src
    c = src.count(old)
    assert c >= 1, "not found: %r" % (old[:70],)
    if n is not None:
        assert c == n, "count %d != %d for %r" % (c, n, old[:70])
    src = src.replace(old, new)
    R.append("%s x%d" % (old[:44].replace("\n", " "), c))


# ---------------------------------------------------------- structural edits
rep('"""R61 audit: ONE joined base rail (left + right + 4 ribs = 1 solid) + frame.',
    '"""R62 audit: the R61 joined base rail CUT at x = -40 into 3 H2D-sized pieces.')
rep('''Everything below is MEASURED from the R60 STEP outputs that get delivered; the
R56/R57 reports are used only for the "is the frame unchanged" cross-check.
"""
import json''',
    '''Everything below is MEASURED from the R62 STEP outputs that get delivered; the
R56/R57 reports are used only for the "is the frame unchanged" cross-check, and
the R61 report only to prove the cut removed/added no material.
"""
import json
import math''')
rep('''r60 = json.loads((OUT / "report_r61_pollen.json").read_text(encoding="utf-8"))''',
    '''r62 = json.loads((OUT / "report_r62_pollen.json").read_text(encoding="utf-8"))
r61 = json.loads((HERE / "output" / "_r61_frame"
                  / "report_r61_pollen.json").read_text(encoding="utf-8"))''')
rep('''def cylz(r, z0, z1, x, y):''',
    '''def min_enclosing_square(dx, dy):
    """Exact side of the smallest square that holds a dx x dy rectangle."""
    best = max(dx, dy)
    for i in range(0, 91):
        th = math.radians(i / 2.0)
        best = min(best, max(dx * math.cos(th) + dy * math.sin(th),
                             dx * math.sin(th) + dy * math.cos(th)))
    return best


def cylz(r, z0, z1, x, y):''')

# 1. rail census: THREE pieces now
rep('''railparts = [n for n in names if n.startswith("base_rail_")]
splits = [n for n in names if n.endswith("_front") or n.endswith("_rear")
          or n.startswith("base_rail_-") or n.startswith("base_rail_+")]
add("base_rail_present", "1 joined base rail (left + right + 4 ribs)",
    "%d piece(s): %s" % (len(railparts), ",".join(railparts)), 0.0,
    "pass" if railparts == ["base_rail_joined"] else "fail",
    "R61 report part list")
add("rail_print_split_removed", "0 split rail pieces",
    "%d split pieces" % len(splits), 0.0, "pass" if not splits else "fail",
    "R61 report part list")''',
    '''railparts = sorted(n for n in names if n.startswith("base_rail_"))
want_rails = sorted(R61.RAIL_PIECE_NAMES)
add("base_rail_present", "3 H2D-sized rail pieces (rear block + 2 front bars)",
    "%d piece(s): %s" % (len(railparts), ",".join(railparts)), 0.0,
    "pass" if railparts == want_rails else "fail",
    "R61 report part list vs R61.RAIL_PIECE_NAMES")
add("rail_pre_split_piece_gone", "0 pieces left named base_rail_joined",
    "%d piece(s) named base_rail_joined" % names.count("base_rail_joined"), 0.0,
    "pass" if "base_rail_joined" not in names else "fail",
    "R61 report part list")''')
rep('''zmin = {"base_rail_joined": rb["z"][0],''',
    '''zmin = {"base_rail (3 pieces)": rb["z"][0],''')
rep('''add("lowest_point_of_assembly", "a base_rail_R60 piece @ z=%.2f" % SOLE_ZB,''',
    '''add("lowest_point_of_assembly", "a base_rail piece @ z=%.2f" % SOLE_ZB,''')

# 2. the four tab bolt holes pierce the two FRONT bars
rep('''    piece = R61.RAIL_JOIN_NAME''', '''    piece = R61.rail_front_name(y)''')

# 3. chassis holes: each rail line lives in its own piece now
rep('''holes = []
b = [p["bbox"] for p in r60["parts"] if p["part"] == "base_rail_joined"][0]
for yy in (R61.RAIL_CY, -R61.RAIL_CY):   # MEASURED: holes sit on each rail centre line
    for x in R61.RAIL_HOLE_X:
        if not (b["x"][0] + 3.0 < x < b["x"][1] - 3.0):
            continue
        h = cylz(1.9, SOLE_ZB - 1.0, R61.RAIL_ZT + 1.0, x, yy).intersect(rails).Volume()
        holes.append({"piece": "base_rail_joined", "x": x, "y": yy,
                      "material_mm3": round(h, 3)})''',
    '''holes = []
_pb = {p["part"]: p["bbox"] for p in r60["parts"]
       if p["part"].startswith("base_rail_")}
for nm in sorted(_pb):
    b = _pb[nm]
    # MEASURED: the chassis holes sit on each rail centre line
    if nm == R61.RAIL_REAR_NAME:
        sides = (-R61.RAIL_CY, R61.RAIL_CY)
    elif nm.endswith("%+d" % R61.RAIL_CY):
        sides = (R61.RAIL_CY,)
    else:
        sides = (-R61.RAIL_CY,)
    for yy in sides:
        for x in R61.RAIL_HOLE_X:
            if not (b["x"][0] + 3.0 < x < b["x"][1] - 3.0):
                continue
            h = cylz(1.9, SOLE_ZB - 1.0, R61.RAIL_ZT + 1.0, x, yy) \\
                .intersect(rails).Volume()
            holes.append({"piece": nm, "x": x, "y": yy,
                          "material_mm3": round(h, 3)})''')

# 4. sizes + H2D verdict per piece (the R61 exception is closed)
rep('''# 8. R60: one printed rail per side, and it knowingly exceeds the H2D box
pd = []
for n in [x for x in names if x.startswith("base_rail")]:
    b = [p["bbox"] for p in r60["parts"] if p["part"] == n][0]
    d = (b["x"][1] - b["x"][0], b["y"][1] - b["y"][0], b["z"][1] - b["z"][0])
    pd.append({"part": n, "dims_mm": d})
worst = max(max(p["dims_mm"]) for p in pd)
add("rail_single_piece_length", "380.0 mm x 162.0 mm x 26.0 mm, 1 piece",
    "%.1f x %.1f x %.1f mm, %d piece" % (pd[0]["dims_mm"] + (len(pd),)), 0.1,
    "pass" if (abs(pd[0]["dims_mm"][0] - 380.0) < 0.1 and len(pd) == 1) else "fail",
    "read-back AABB of the joined base rail (x -170..210, y +-81)")
_sq = (pd[0]["dims_mm"][0] + pd[0]["dims_mm"][1]) / 2.0 ** 0.5
add("rail_pieces_H2D_fit", "<= 325 mm min enclosing square (H2D single nozzle)",
    "min square %.1f mm = %.1f mm over" % (_sq, _sq - 325.0), 0.0,
    "pass" if _sq <= 325.0 else "fail",
    "min area enclosing square of the joined 380 x 162 footprint (45 deg) "
    "against single-nozzle 325 x 320 x 325",
    accepted="user, 2026-10-16: ONE rail piece is wanted, so the %.1f mm "
             "overshoot is a KNOWN, user-accepted deviation (DEC-0068); the "
             "joined rail is printed as two segments and bolted back, TBD"
             % (_sq - 325.0))
res["rail_pieces"] = pd
res["rail_min_enclosing_square_mm"] = round(_sq, 2)''',
    '''# 8. R62: three printed rail pieces, and every one of them fits the H2D box
_want_dim = {R61.RAIL_REAR_NAME: (130.0, 162.0, 26.0),
             R61.rail_front_name(-R61.RAIL_CY): (250.0, 18.0, 26.0),
             R61.rail_front_name(R61.RAIL_CY): (250.0, 18.0, 26.0)}
pd = []
for n in sorted(want_rails):
    b = [p["bbox"] for p in r60["parts"] if p["part"] == n][0]
    pd.append({"part": n,
               "dims_mm": [round(b[k][1] - b[k][0], 1) for k in "xyz"],
               "volume_mm3": [p["volume_mm3"] for p in r60["parts"]
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
res["rail_min_enclosing_square_mm"] = round(_worst_sq, 1)''')

# 5. COTS bucket text, drawn from the report instead of being hard-coded
rep('''    "%d COTS bodies excluded (36 no-SKU hardware + 29 vendor SKU)" % _ncots,
    0.0, "pass", "report print_set list vs both COTS buckets")''',
    '''    "%d COTS bodies excluded (%d no-SKU hardware + %d vendor SKU)"
    % (_ncots, len(r60["print_set"]["cots_hardware_not_printed"]),
       len(r60["excluded_from_this_version"]["vendor_cots_bodies"])),
    0.0, "pass", "report print_set list vs both COTS buckets")''')

# 6. rib band: the three rail pieces are what lives there
rep('''    if n in ("base_rail_joined", "shooter_frame_R61_merged"):''',
    '''    if n in tuple(R61.RAIL_PIECE_NAMES) + ("shooter_frame_R61_merged",):''')

# 7. solids + per-piece read-back regions + the pure-partition proof
rep('''add("rail_join_is_1_solid", "1 solid in the joined rail STEP",
    "%d solid(s)" % len(rails.Solids()), 0.0,
    "pass" if len(rails.Solids()) == 1 else "fail",
    "T06_base_rail_R61_pollen.step read back")''',
    '''add("rail_pieces_are_single_solids", "3 solids, one per printed rail piece",
    "%d solid(s)" % len(rails.Solids()), 0.0,
    "pass" if len(rails.Solids()) == 3 else "fail",
    "T06_base_rail_R61_pollen.step read back; 3 printed pieces must be 3 solids")

# 12. every piece sits exactly in the half-space the cut gave it
_reg_boxes = {
    R61.RAIL_REAR_NAME: (R61.RAIL_X0 - 0.5, R61.RAIL_SPLIT_X - 0.5,
                         -R61.RAIL_CY - 9.5, R61.RAIL_CY + 9.5),
    R61.rail_front_name(-R61.RAIL_CY): (R61.RAIL_SPLIT_X + 0.5, R61.RAIL_X1 + 0.5,
                                        -R61.RAIL_CY - 9.5, -0.5),
    R61.rail_front_name(R61.RAIL_CY): (R61.RAIL_SPLIT_X + 0.5, R61.RAIL_X1 + 0.5,
                                       0.5, R61.RAIL_CY + 9.5),
}
_reg = []
for n, (x0, x1, y0, y1) in _reg_boxes.items():
    v = box(x0, x1, y0, y1, SOLE_ZB - 0.5,
            R61.RAIL_ZT + 0.5).intersect(rails).Volume()
    want_v = [p["volume_mm3"] for p in r60["parts"] if p["part"] == n][0]
    _reg.append({"part": n, "material_mm3": round(v, 1), "report_mm3": want_v,
                 "pass": abs(v - want_v) < 1.0})
add("rail_pieces_where_expected", "each half-space holds exactly its own piece",
    "; ".join("%s %.1f/%.1f" % (r["part"], r["material_mm3"], r["report_mm3"])
              for r in _reg), 1.0,
    "pass" if all(r["pass"] for r in _reg) else "fail",
    "read-back material in the rear half-space x < -40 and the two front "
    "half-spaces x > -40 (y sign), each vs the R62 report volume")
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
for y in (R61.RAIL_CY, -R61.RAIL_CY):
    v = box(R61.RAIL_SPLIT_X - 0.5, R61.RAIL_SPLIT_X + 0.5, y - 9.0, y + 9.0,
            SOLE_ZB, R61.RAIL_ZT).intersect(rails).Volume()
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
    b = [p["bbox"] for p in r60["parts"] if p["part"] == n][0]
    got = b["x"][1] if n == R61.RAIL_REAR_NAME else b["x"][0]
    _splitf.append({"part": n, "face_mm": got,
                    "pass": abs(got - R61.RAIL_SPLIT_X) < 0.05})
add("rail_split_faces", "rear xmax = front xmin = %.1f mm" % R61.RAIL_SPLIT_X,
    "; ".join("%s %s" % (r["part"], r["face_mm"]) for r in _splitf), 0.05,
    "pass" if all(r["pass"] for r in _splitf) else "fail",
    "read-back AABB of every rail piece against the cut plane")
res["rail_split_faces"] = _splitf
res["rail_split"] = {"plane_x_mm": R61.RAIL_SPLIT_X,
                     "r61_joined_mm3": _r61v, "r62_pieces_mm3": _vsum,
                     "piece_volumes_mm3": {p["part"]: p["volume_mm3"] for p in pd},
                     "removed_mm3": round(_r61v - _vsum, 1)}''')

# ------------------------------------------------------- mechanical renames
rep('OUT = HERE / "output" / "_r61_frame"', 'OUT = HERE / "output" / "_r62_frame"')
rep('import paddle_launcher_shooter_assembly_r61 as R61   # noqa: E402',
    'import paddle_launcher_shooter_assembly_r62 as R62   # noqa: E402')
rep('R61.', 'R62.')
rep('r60[', 'r62[')
rep('T06_base_rail_R61_pollen.step', 'T06_base_rail_R62_pollen.step')
rep('T06_shooter_frame_R61_pollen.step', 'T06_shooter_frame_R62_pollen.step')
rep('T06_print_set_R61_pollen.step', 'T06_print_set_R62_pollen.step')
rep('"shooter_frame_R61_merged"', '"shooter_frame_R62_merged"')
rep('"audit_r61.json"', '"audit_r62.json"')
rep('R61 report part list', 'R62 report part list')

Path("cad/_r62_audit.py").write_text(src, encoding="utf-8")
print("wrote cad/_r62_audit.py  (%d replacements)" % len(R))
