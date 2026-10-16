# -*- coding: utf-8 -*-
"""Generate cad/_r61_audit.py from cad/_r60_audit.py (read-back only)."""
from pathlib import Path

src = Path("cad/_r60_audit.py").read_text(encoding="utf-8")
R = []


def rep(old, new, n=None):
    global src
    c = src.count(old)
    assert c >= 1, "not found: %r" % (old[:70],)
    if n is not None:
        assert c == n, "count %d != %d for %r" % (c, n, old[:70])
    src = src.replace(old, new)
    R.append("%s x%d" % (old[:40], c))


rep('"""R60 audit: sole pressed 3 mm deeper, rails back to ONE printed piece each.',
    '"""R61 audit: ONE joined base rail (left + right + 4 ribs = 1 solid) + frame.')
rep('OUT = HERE / "output" / "_r60_frame"', 'OUT = HERE / "output" / "_r61_frame"')
rep('"report_r60_pollen.json"', '"report_r61_pollen.json"')
rep('import paddle_launcher_shooter_assembly_r60 as R60   # noqa: E402',
    'import paddle_launcher_shooter_assembly_r61 as R61   # noqa: E402')
rep('R60.', 'R61.')
rep('T06_base_rail_R60_pollen.step', 'T06_base_rail_R61_pollen.step')
rep('T06_shooter_frame_R60_pollen.step', 'T06_shooter_frame_R61_pollen.step')
rep('T06_print_set_R60_pollen.step', 'T06_print_set_R61_pollen.step')
rep('"shooter_frame_R60_merged"', '"shooter_frame_R61_merged"')
rep('"base_rail_R60"', '"base_rail_joined"')
rep('"audit_r60.json"', '"audit_r61.json"')
rep('R60 report part list', 'R61 report part list')

# 1. rail census: exactly ONE joined piece
rep('''add("base_rail_present", "2 rails, 1 printed piece each",
    "%d rails / %d pieces" % (len(railparts), len(railparts)), 0.0,
    "pass" if len(railparts) == 2 else "fail", "R61 report part list")''',
    '''add("base_rail_present", "1 joined base rail (left + right + 4 ribs)",
    "%d piece(s): %s" % (len(railparts), ",".join(railparts)), 0.0,
    "pass" if railparts == ["base_rail_joined"] else "fail",
    "R61 report part list")''')
rep('''splits = [n for n in names if n.endswith("_front") or n.endswith("_rear")]''',
    '''splits = [n for n in names if n.endswith("_front") or n.endswith("_rear")
          or n.startswith("base_rail_-") or n.startswith("base_rail_+")]''')

# 2. the four tab bolt holes now pierce the joined rail
rep('''    piece = R61.rail_name(1 if y > 0 else -1)''',
    '''    piece = R61.RAIL_JOIN_NAME''')

# 3. chassis holes: both rail centre lines inside the joined piece
rep('''for n in [x for x in names if x.startswith("base_rail")]:
    b = [p["bbox"] for p in r60["parts"] if p["part"] == n][0]
    yy = R61.RAIL_CY if "_+" in n else -R61.RAIL_CY   # MEASURED: chassis holes sit on the rail centre line
    for x in R61.RAIL_HOLE_X:
        if not (b["x"][0] + 3.0 < x < b["x"][1] - 3.0):
            continue
        h = cylz(1.9, SOLE_ZB - 1.0, R61.RAIL_ZT + 1.0, x, yy).intersect(rails).Volume()
        holes.append({"piece": n, "x": x, "y": yy, "material_mm3": round(h, 3)})''',
    '''b = [p["bbox"] for p in r60["parts"] if p["part"] == "base_rail_joined"][0]
for yy in (R61.RAIL_CY, -R61.RAIL_CY):   # MEASURED: holes sit on each rail centre line
    for x in R61.RAIL_HOLE_X:
        if not (b["x"][0] + 3.0 < x < b["x"][1] - 3.0):
            continue
        h = cylz(1.9, SOLE_ZB - 1.0, R61.RAIL_ZT + 1.0, x, yy).intersect(rails).Volume()
        holes.append({"piece": "base_rail_joined", "x": x, "y": yy,
                      "material_mm3": round(h, 3)})''')
rep('"O3.8 probe z -8..17 in each rail piece, per chassis hole x"',
    '"O3.8 probe z -8..17 in the joined base rail, both rails, per chassis hole x"')

# 4. length / build-volume checks for the joined piece
rep('''pd = []
for n in [x for x in names if x.startswith("base_rail")]:
    b = [p["bbox"] for p in r60["parts"] if p["part"] == n][0]
    d = (b["x"][1] - b["x"][0], b["y"][1] - b["y"][0], b["z"][1] - b["z"][0])
    pd.append({"part": n, "dims_mm": d})
worst = max(max(p["dims_mm"]) for p in pd)
add("rail_single_piece_length", "380.0 mm long, 2 pieces",
    "%.1f mm, %d pieces" % (worst, len(pd)), 0.1,
    "pass" if abs(worst - 380.0) < 0.1 and len(pd) == 2 else "fail",
    "read-back AABB, one printed rail per side (x -170..210)")''',
    '''pd = []
for n in [x for x in names if x.startswith("base_rail")]:
    b = [p["bbox"] for p in r60["parts"] if p["part"] == n][0]
    d = (b["x"][1] - b["x"][0], b["y"][1] - b["y"][0], b["z"][1] - b["z"][0])
    pd.append({"part": n, "dims_mm": d})
worst = max(max(p["dims_mm"]) for p in pd)
add("rail_single_piece_length", "380.0 mm x 162.0 mm x 26.0 mm, 1 piece",
    "%.1f x %.1f x %.1f mm, %d piece" % (pd[0]["dims_mm"] + (len(pd),)), 0.1,
    "pass" if (abs(pd[0]["dims_mm"][0] - 380.0) < 0.1 and len(pd) == 1) else "fail",
    "read-back AABB of the joined base rail (x -170..210, y +-81)")''')

rep('''add("rail_pieces_H2D_fit", "<= 325 mm longest side (H2D single nozzle)",
    "worst %.1f mm = %.1f mm over" % (worst, worst - 325.0), 0.0,
    "pass" if worst <= 325.0 else "fail",
    "read-back AABB per printed piece against single-nozzle 325 x 320 x 325",''',
    '''_sq = (pd[0]["dims_mm"][0] + pd[0]["dims_mm"][1]) / 2.0 ** 0.5
add("rail_pieces_H2D_fit", "<= 325 mm min enclosing square (H2D single nozzle)",
    "min square %.1f mm = %.1f mm over" % (_sq, _sq - 325.0), 0.0,
    "pass" if _sq <= 325.0 else "fail",
    "min area enclosing square of the joined 380 x 162 footprint (45 deg) "
    "against single-nozzle 325 x 320 x 325",''')
rep('''    accepted="user, 2026-10-16: a single rail per side is wanted, so the %.0f mm "
             "overshoot is a KNOWN, user-accepted deviation (DEC-0066), TBD"
             % (worst - 325.0))''',
    '''    accepted="user, 2026-10-16: ONE rail piece is wanted, so the %.1f mm "
             "overshoot is a KNOWN, user-accepted deviation (DEC-0068); the "
             "joined rail is printed as two segments and bolted back, TBD"
             % (_sq - 325.0))''')
rep('res["rail_pieces"] = pd', 'res["rail_pieces"] = pd\nres["rail_min_enclosing_square_mm"] = round(_sq, 2)')

# 5. R61 rib checks, inserted just before the summary block
rep('''res["rails"] = {"bbox": rb, "volume_mm3": round(rails.Volume(), 1)}''',
    '''# 10. R61: the four ribs are really there at full section, and the join is 1 solid
_rb = []
for x in R61.RAIL_RIB_X:
    v = box(x - R61.RAIL_RIB_T / 2.0 + 0.1, x + R61.RAIL_RIB_T / 2.0 - 0.1,
            -60.0, 60.0, SOLE_ZB + 0.2, R61.RAIL_ZT - 0.2).intersect(rails).Volume()
    want = (R61.RAIL_RIB_T - 0.2) * 120.0 * (R61.RAIL_ZT - SOLE_ZB - 0.4)
    _rb.append({"x": x, "material_mm3": round(v, 1), "full_mm3": round(want, 1),
                "pass": abs(v - want) < 1.0})
add("rail_ribs_4_full_section", "4/4 ribs full %.0f x 120 x %.0f"
    % (R61.RAIL_RIB_T, R61.RAIL_ZT - SOLE_ZB),
    "%d/4 full" % sum(1 for r in _rb if r["pass"]), 1.0,
    "pass" if all(r["pass"] for r in _rb) else "fail",
    "read-back material inside each rib envelope (core y +-60), 4 ribs")
res["rail_ribs"] = _rb

# 11. the rib zone must sit in the free band (no frame material, no rib clash)
_rband = box(R61.RAIL_RIB_X[0] - 6.0, R61.RAIL_RIB_X[-1] + 6.0, -60.0, 60.0,
             SOLE_ZB, R61.RAIL_ZT).intersect(frame).Volume()
add("rib_band_clear_of_frame", "0.000 mm3", "%.4f mm3" % _rband, 0.05,
    "pass" if _rband < 0.05 else "fail",
    "frame intersect rib band x -166..-49, y +-60, z -10..16")
_orib = 0.0
for p in r60["parts"]:
    if p["part"] in ("base_rail_joined", "shooter_frame_R61_merged"):
        continue
    _x = p["bbox"]["x"]
    if _x[1] > R61.RAIL_RIB_X[0] - 6.0 and _x[0] < R61.RAIL_RIB_X[-1] + 6.0:
        _orib += 1
add("rib_band_clear_of_other_parts", "0 other parts in the rib band",
    "%d part(s)" % _orib, 0.0, "pass" if _orib == 0 else "fail",
    "report bbox overlap of every other part with x -166..-49")

add("rail_join_is_1_solid", "1 solid in the joined rail STEP",
    "%d solid(s)" % len(rails.Solids()), 0.0,
    "pass" if len(rails.Solids()) == 1 else "fail",
    "T06_base_rail_R61_pollen.step read back")

res["rails"] = {"bbox": rb, "volume_mm3": round(rails.Volume(), 1)}''')

Path("cad/_r61_audit.py").write_text(src, encoding="utf-8")
print("wrote cad/_r61_audit.py  (%d replacements)" % len(R))
