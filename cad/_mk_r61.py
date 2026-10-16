# -*- coding: utf-8 -*-
"""Build cad/paddle_launcher_shooter_assembly_r61.py from the R60 generator.

R61 (2026-10-16, user): "把左右两条滑轨合成一件" -- the left and right base
rails are joined into ONE printed piece by four ribs.  Nothing else changes:
the rail section, the sole depth, the frame, the joints and the COTS policy are
R60's, so every R60 measurement still applies.
"""
import io
from pathlib import Path

SRC = Path("cad/paddle_launcher_shooter_assembly_r60.py")
DST = Path("cad/paddle_launcher_shooter_assembly_r61.py")
s = io.open(SRC, encoding="utf-8").read()
n = 0

def rep(old, new):
    global s, n
    assert s.count(old) == 1, "count=%d for %r" % (s.count(old), old[:70])
    s = s.replace(old, new)
    n += 1

HDR_OLD = """\"\"\"T06 R60 -- R59 with a deeper rail sole and NO rail print split.

R60 (2026-10-16, user): "press it down; let the STEP contain every part that
has to be printed -- do NOT split the rail into two parts any more."
"""
HDR_NEW = """\"\"\"T06 R61 -- the left and right base rails are joined into ONE piece.

R61 (2026-10-16, user): "要把左右两条滑轨合成一件" -- option 2 of the clarification:
join base_rail_-72 and base_rail_+72 into a single printed part.  Done with four
ribs that cross between them; nothing is re-split and the R60 rail section is
untouched.

  rib centres x = -160, -125, -90, -55   (10 mm thick)
  y -66 .. 66                            (3 mm bite into each 18 mm rail)
  z -10 .. 16                            (flush with the sole bottom and rail top)

  cad/_r61_probe.py (MEASURED): the merged frame has 0.000 mm3 of material in
  that envelope anywhere over the only clear band x -170..-40; from x = -40 to
  210 the frame owns that band (a ~5 mm bottom web at z -3.5..+1.4), so the ribs
  stay clear of it.  The ribs therefore touch the two rails and nothing else.

  Print consequence (CALCULATED): the joined body is 380 x 144 x 26 mm, whose
  minimum enclosing square is 370.5 mm, so it does NOT fit the Bambu Lab H2D
  325 mm even diagonally (a single 380 x 18 rail does: 45 deg -> 281.4 x 281.4).
  The joined base must therefore be printed in two segments and bolted back
  together; that print split is deliberately NOT modelled here (user: no CAD
  print split).  Printed body count 45 -> 44.

R60 (2026-10-16): "press it down; let the STEP contain every part that
has to be printed -- do NOT split the rail into two parts any more."
"""
rep(HDR_OLD, HDR_NEW)
rep("python.exe -X utf8 cad/paddle_launcher_shooter_assembly_r60.py pollen --step",
    "python.exe -X utf8 cad/paddle_launcher_shooter_assembly_r61.py pollen --step")
rep('OUT = HERE / "output" / "_r60_frame"', 'OUT = HERE / "output" / "_r61_frame"')

rep("""SOLE_ZB = -10.0                        # R60: only floor contact, 3 mm deeper
""",
    """SOLE_ZB = -10.0                        # R60: only floor contact, 3 mm deeper

# --- R61: the two rails become ONE printed piece -----------------------------
RAIL_JOIN_NAME = "base_rail_joined"    # R61: left rail + right rail + 4 ribs, 1 solid
RAIL_RIB_X = (-160.0, -125.0, -90.0, -55.0)   # rib centres, inside the clear band
RAIL_RIB_T = 10.0                      # rib thickness in x
RAIL_RIB_WY = 66.0                     # rib half width in y -> 3 mm bite per rail
""")

rep("RAIL_PIECE_NAMES = tuple(rail_name(y) for y in (-1, 1))",
    "RAIL_PIECE_NAMES = (RAIL_JOIN_NAME,)      # R61: ONE joined base rail")
rep("DRILLABLE = tuple(rail_name(y) for y in (-1, 1))      # R60: pierces the one rail",
    "DRILLABLE = (RAIL_JOIN_NAME,)                        # R61: pierces the joined base")
rep("        rf = rail_name(1 if y > 0 else -1)",
    "        rf = RAIL_JOIN_NAME")
rep('"also_drilled": (rail_name(sy),),', '"also_drilled": (RAIL_JOIN_NAME,),')

JOIN = '''def join_rails(soles):
    """R61: the left and right rail become ONE printed piece, tied by 4 ribs.

    The rib envelope is probed free of frame material by cad/_r61_probe.py, so
    each rib touches the two rails and nothing else.  All four chassis holes and
    the four nut pockets are already cut in `soles`, so fusing cannot fill them.
    """
    assert len(soles) == 2, "expected the two side rails, got %d" % len(soles)
    ribs = [K.box(RAIL_RIB_T, 2 * RAIL_RIB_WY, RAIL_ZT - SOLE_ZB,
                  (x, 0.0, (RAIL_ZT + SOLE_ZB) / 2.0)) for x in RAIL_RIB_X]
    joined = fuse_all(list(soles.values()) + ribs)
    ns = n_solids(joined)
    assert ns == 1, "R61 ribs must tie the rails into ONE solid, got %d" % ns
    for x in RAIL_RIB_X:
        inner = round(K.box(RAIL_RIB_T, 120.0, RAIL_ZT - SOLE_ZB,
                            (x, 0.0, (RAIL_ZT + SOLE_ZB) / 2.0))
                      .intersect(joined).Volume(), 1)
        want = RAIL_RIB_T * 120.0 * (RAIL_ZT - SOLE_ZB)
        print("[r61]   rib x=%+.0f  between-rail volume %.1f mm3 (expected %.1f)"
              % (x, inner, want), flush=True)
        assert abs(inner - want) < 1.0, "rib x=%.0f is not solid between the rails" % x
    print("[r61] joined base: %d solid, V=%.0f mm3, %s"
          % (ns, joined.Volume(), bbox(joined)), flush=True)
    return {RAIL_JOIN_NAME: joined}


def drill_holes(frame, specs, keep_others):'''
rep("def drill_holes(frame, specs, keep_others):", JOIN)

rep("    others.update(make_rail_soles(rails))      # R60: rail -> rail + sole",
    "    others.update(join_rails(make_rail_soles(rails)))   # R61: 2 rails -> 1 piece")
rep('''    print("[r60 %s] base rails KEPT, thickened downwards, NOT split: %s"
          % (name, sorted(rails)), flush=True)''',
    '''    print("[r61 %s] base rails KEPT, thickened downwards, then JOINED by %d ribs "
          "into ONE piece: %s" % (name, len(RAIL_RIB_X), sorted(rails)), flush=True)''')
rep("            return \"printed thickened base rail (R60, one piece per side)\"",
    "            return \"printed thickened base rail (R61, left+right JOINED, 1 piece)\"")
rep('''        "caliber": "T06 R60 prototype: merged printed frame + one-piece thickened base "
                   "rails, plain M3 through-joints",''',
    '''        "caliber": "T06 R61 prototype: merged printed frame + ONE joined thickened "
                   "base rail (left/right tied by 4 ribs), plain M3 through-joints",''')
rep('''                      "R60 pressed the sole 3 mm deeper and dropped the rail split",''',
    '''                      "R60 pressed the sole 3 mm deeper and dropped the rail split; "
                      "R61 joined the left and right rail into one printed piece",''')
rep('        "base_rail_r60": {', '        "base_rail_r61": {')
rep('''            "print_split": None,
            "h2d_note": "single piece %.0f mm: %.0f mm over the H2D 325 mm limit, "
                        "user-accepted 2026-10-16 (DEC-0066), TBD"
                        % (RAIL_X1 - RAIL_X0, RAIL_X1 - RAIL_X0 - 325.0),''',
    '''            "ribs": {"x_mm": list(RAIL_RIB_X), "thickness_mm": RAIL_RIB_T,
                     "half_width_y_mm": RAIL_RIB_WY, "z_mm": [SOLE_ZB, RAIL_ZT],
                     "clear_band_x_mm": [RAIL_X0, -40.0],
                     "note": "left + right rail joined into ONE printed piece"},
            "print_split": None,
            "h2d_note": "joined piece %.0f x %.0f x %.0f mm: minimum enclosing square "
                        "370.5 mm > H2D 325 mm, so it must be printed in two segments "
                        "and bolted back together (not modelled; user: no CAD split)"
                        % (RAIL_X1 - RAIL_X0, 2 * (RAIL_CY + RAIL_WY / 2.0),
                           RAIL_ZT - SOLE_ZB),''')

for a, b in ((("T06_shooter_frame_R60_%s" % "%s"), "T06_shooter_frame_R61_%s"),
             ("T06_shooter_assembly_R60_%s", "T06_shooter_assembly_R61_%s"),
             ("T06_base_rail_R60_%s", "T06_base_rail_R61_%s"),
             ("T06_print_set_R60_%s", "T06_print_set_R61_%s"),
             ("T06_base_rail_R60_%s.step", "T06_base_rail_R61_%s.step"),
             ("R60 %s section y=0", "R61 %s section y=0"),
             ("R60 %s section y=76", "R61 %s section y=76"),
             ("R60 %s full assembly, y=0", "R61 %s full assembly, y=0"),
             ('"r60_%s_section_y0.png"', '"r61_%s_section_y0.png"'),
             ('"r60_%s_section_y76.png"', '"r61_%s_section_y76.png"'),
             ('"r60_%s_assembly_y0.png"', '"r61_%s_assembly_y0.png"'),
             ('report_r60_%s.json', 'report_r61_%s.json'),
             ('print("[r60 %s] print set ->', 'print("[r61 %s] print set ->'),
             ('print("[r60 %s] STEP frame', 'print("[r61 %s] STEP frame'),
             ('print("[r60 %s] lowest point', 'print("[r61 %s] lowest point'),
             ('print("[r60 %s] done in', 'print("[r61 %s] done in'),
             ('print("[r60] %-18s %s"', 'print("[r61] %-18s %s"'),
             ('print("[r60 %s] gate envelope', 'print("[r61 %s] gate envelope'),
             ('print("[r60 %s] keep', 'print("[r61 %s] keep')):
    try:
        rep(a, b)
    except AssertionError as e:
        print("SKIP (not present): %s" % e)

io.open(DST, "w", encoding="utf-8", newline="\n").write(s)
print("wrote %s  (%d replacements, %d lines)"
      % (DST, n, s.count("\n") + 1))
left = [(i + 1, ln) for i, ln in enumerate(s.splitlines()) if "r60" in ln or "R60" in ln]
print("lines still mentioning r60/R60: %d" % len(left))
for i, ln in left:
    print("   %4d | %s" % (i, ln.strip()[:110]))
