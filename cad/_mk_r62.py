# -*- coding: utf-8 -*-
"""Build cad/paddle_launcher_shooter_assembly_r62.py from the R61 generator.

R62 (2026-10-16, user): "尝试把超限该零件，拆成符合尺寸的" -- the R61 joined base
rail (380 x 162 x 26, min enclosing square 383.3 mm) exceeds the H2D bed, so it
is cut at x = -40 into a rear cross-tied block plus two front bars.  Pure
partition: nothing is added, nothing is removed, every joint/hole is untouched.
"""
import io
from pathlib import Path

SRC = Path("cad/paddle_launcher_shooter_assembly_r61.py")
DST = Path("cad/paddle_launcher_shooter_assembly_r62.py")
s = io.open(SRC, encoding="utf-8").read()
n = 0

def rep(old, new):
    global s, n
    assert s.count(old) == 1, "count=%d for %r" % (s.count(old), old[:70])
    s = s.replace(old, new)
    n += 1

# 0. mechanical rename r61 -> r62 everywhere (stems, section titles, report name)
assert s.count("r61") > 0 and s.count("R61") > 0
s = s.replace("r61", "r62").replace("R61", "R62")

# 1. header
rep('''"""T06 R62 -- the left and right base rails are joined into ONE piece.

R62 (2026-10-16, user): "要把左右两条滑轨合成一件" -- option 2 of the clarification:''',
'''"""T06 R62 -- the R61 joined base rail, cut into H2D-sized printed pieces.

R62 (2026-10-16, user): "尝试把超限该零件，拆成符合尺寸的" -- the R61 joined base
rail is 380 x 162 x 26 mm (minimum enclosing square 383.3 mm) and does NOT fit
the Bambu Lab H2D single-nozzle 325 x 320 x 325 bed, so it is cut into pieces
that do.  The cut is a PURE PARTITION of the R61 body: no material is added or
removed, so both halves of every face keep the R61 geometry exactly and every
hole / rib / nut pocket is inherited unchanged.

  base_rail_rear_joined   x -170 .. -40   130 x 162 x 26   both rail stubs +
                          the same four ribs, 1 solid
  base_rail_front_+72     x  -40 .. 210   250 x  18 x 26   right rail front bar
  base_rail_front_-72     x  -40 .. 210   250 x  18 x 26   left  rail front bar

  Why x = -40 and not further forward (MEASURED, cad/_r62_probe.py): from x = -40
  on, the merged frame itself owns the whole band between the two rails
  (|y| <= 62, z -3.5 .. +20), so no cross rib can live there; x -170 .. -40 is
  the only clear band and it already carries the four R61 ribs.  The join can
  therefore only survive in the rear segment, and the two 250 mm front bars ship
  as separate printed bodies.  Printed body count 44 (R61) -> 46 (R62).

  H2D verdict (CALCULATED): min enclosing square 206.5 mm (rear block) and
  189.5 mm (front bars, 45 deg) -> all three <= 325 mm, so the print exception
  recorded as DEC-0068 is closed by DEC-0069.

R61 (2026-10-16, user): "要把左右两条滑轨合成一件" -- option 2 of the clarification:''')

# 2. constants
rep('''RAIL_RIB_WY = 66.0                     # rib half width in y -> 3 mm bite per rail
''',
'''RAIL_RIB_WY = 66.0                     # rib half width in y -> 3 mm bite per rail

# --- R62: cut that joined body into H2D-sized printed pieces -----------------
RAIL_SPLIT_X = -40.0                   # cut plane; the frame owns every x > -40
RAIL_REAR_NAME = "base_rail_rear_joined"
H2D_LIMIT = 325.0                      # KNOWN, H2D single nozzle, x/y bed 325x320


def rail_front_name(y):
    """R62: the front bar of one side, named after its centre-line y."""
    return "base_rail_front_%+d" % (RAIL_CY if y > 0 else -RAIL_CY)
''')

rep("RAIL_PIECE_NAMES = (RAIL_JOIN_NAME,)      # R62: ONE joined base rail",
    """RAIL_PIECE_NAMES = (RAIL_REAR_NAME, rail_front_name(-RAIL_CY),
                    rail_front_name(RAIL_CY))   # R62: 3 printed rail bodies""")
rep("DRILLABLE = (RAIL_JOIN_NAME,)                        # R62: pierces the joined base",
    "DRILLABLE = (rail_front_name(-RAIL_CY), rail_front_name(RAIL_CY))\n"
    "# R62: the four M3 rail joints sit in the FRONT bars (x = 60 / 76)")
rep("        rf = RAIL_JOIN_NAME", "        rf = rail_front_name(y)")
rep('"also_drilled": (RAIL_JOIN_NAME,),',
    '"also_drilled": (rail_front_name(1), rail_front_name(-1)),')

# 3. helpers
rep("def is_vendor(name):",
'''def region(x0, x1, y0, y1, z0, z1):
    """Axis-aligned box from two corners, used as a boolean half-space."""
    return K.box(x1 - x0, y1 - y0, z1 - z0,
                 ((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0))


def min_enclosing_square(dx, dy):
    """Side of the smallest square a dx x dy rectangle fits in (45 deg)."""
    return (dx + dy) / 2.0 ** 0.5


def rail_piece_report(pieces):
    """R62: per-piece size + H2D verdict for the report."""
    out = {}
    for nm in RAIL_PIECE_NAMES:
        b = pieces[nm].BoundingBox()
        dx, dy, dz = b.xmax - b.xmin, b.ymax - b.ymin, b.zmax - b.zmin
        sq = min_enclosing_square(dx, dy)
        out[nm] = {"bbox": bbox(pieces[nm]),
                   "dims_mm": [round(dx, 1), round(dy, 1), round(dz, 1)],
                   "volume_mm3": round(pieces[nm].Volume(), 1),
                   "min_enclosing_square_mm": round(sq, 1),
                   "h2d_pass": bool(sq <= H2D_LIMIT)}
    return out


def is_vendor(name):''')

# 4. join_rails -> split_rails
rep('''def join_rails(soles):
    """R62: the left and right rail become ONE printed piece, tied by 4 ribs.

    The rib envelope is probed free of frame material by cad/_r62_probe.py, so
    each rib touches the two rails and nothing else.  All four chassis holes and
    the four nut pockets are already cut in `soles`, so fusing cannot fill them.
    """
    assert len(soles) == 2, "expected the two side rails, got %d" % len(soles)
    ribs = [K.box(RAIL_RIB_T, 2 * RAIL_RIB_WY, RAIL_ZT - SOLE_ZB,
                  (x, 0.0, (RAIL_ZT + SOLE_ZB) / 2.0)) for x in RAIL_RIB_X]
    joined = fuse_all(list(soles.values()) + ribs)
    ns = n_solids(joined)
    assert ns == 1, "R62 ribs must tie the rails into ONE solid, got %d" % ns''',
'''def split_rails(soles):
    """R62: build the R61 joined body, then cut it into H2D-sized pieces.

    Step 1 is R61 unchanged: the two soles + four ribs fuse into ONE solid.
    Step 2 cuts that body at x = RAIL_SPLIT_X and then splits the front part at
    y = 0.  Both steps are pure partitions, asserted by volume, so the R62 pieces
    together are bit-for-bit the R61 body (no material added, none removed).
    """
    assert len(soles) == 2, "expected the two side rails, got %d" % len(soles)
    ribs = [K.box(RAIL_RIB_T, 2 * RAIL_RIB_WY, RAIL_ZT - SOLE_ZB,
                  (x, 0.0, (RAIL_ZT + SOLE_ZB) / 2.0)) for x in RAIL_RIB_X]
    joined = fuse_all(list(soles.values()) + ribs)
    ns = n_solids(joined)
    assert ns == 1, "R62 ribs must tie the rails into ONE solid, got %d" % ns''')

rep('''    print("[r62] joined base: %d solid, V=%.0f mm3, %s"
          % (ns, joined.Volume(), bbox(joined)), flush=True)
    return {RAIL_JOIN_NAME: joined}''',
'''    print("[r62] joined base: %d solid, V=%.0f mm3, %s"
          % (ns, joined.Volume(), bbox(joined)), flush=True)

    # --- R62 cut: one plane at x = RAIL_SPLIT_X, then split the front by side
    big = 400.0
    rear = joined.intersect(region(RAIL_X0 - big, RAIL_SPLIT_X,
                                   -big, big, -big, big))
    front = joined.intersect(region(RAIL_SPLIT_X, RAIL_X1 + big,
                                    -big, big, -big, big))
    out = {RAIL_REAR_NAME: rear}
    for y in (-RAIL_CY, RAIL_CY):
        out[rail_front_name(y)] = front.intersect(
            region(RAIL_X0 - big, RAIL_X1 + big,
                   (-big if y < 0 else 0.0), (0.0 if y < 0 else big),
                   -big, big))
    for nm_, s_ in out.items():
        assert n_solids(s_) == 1, "R62 %s is not one solid" % nm_
    tot = sum(s_.Volume() for s_ in out.values())
    assert abs(tot - joined.Volume()) < 1.0, \\
        "R62 split is not a partition: %.3f vs %.3f mm3" % (tot, joined.Volume())
    for nm_, s_ in sorted(out.items()):
        b = s_.BoundingBox()
        dx, dy, dz = b.xmax - b.xmin, b.ymax - b.ymin, b.zmax - b.zmin
        sq = min_enclosing_square(dx, dy)
        print("[r62] %-24s %.1f x %.1f x %.1f mm  min square %.1f mm  %s"
              % (nm_, dx, dy, dz, sq,
                 "H2D pass" if sq <= H2D_LIMIT else "H2D FAIL"), flush=True)
        assert sq <= H2D_LIMIT, "R62 %s still exceeds the H2D bed" % nm_
    print("[r62] split is a pure partition: %.1f mm3 -> %.1f mm3, 0 added/removed"
          % (joined.Volume(), tot), flush=True)
    return out''')

# 5. run() wiring
rep("    others.update(join_rails(make_rail_soles(rails)))   # R62: 2 rails -> 1 piece",
    "    others.update(split_rails(make_rail_soles(rails)))  # R62: 2 rails -> 3 pieces")
rep('''    print("[r62 %s] base rails KEPT, thickened downwards, then JOINED by %d ribs "
          "into ONE piece: %s" % (name, len(RAIL_RIB_X), sorted(rails)), flush=True)''',
'''    print("[r62 %s] base rails KEPT, thickened downwards, JOINED by %d ribs, then "
          "CUT at x = %.0f into %d H2D-sized print pieces: %s"
          % (name, len(RAIL_RIB_X), RAIL_SPLIT_X, len(RAIL_PIECE_NAMES),
             sorted(rails)), flush=True)''')

# 6. roles / meta
rep('''        if n in RAIL_PIECE_NAMES:
            return "printed thickened base rail (R62, left+right JOINED, 1 piece)"''',
'''        if n == RAIL_REAR_NAME:
            return "printed base rail REAR segment (both sides + 4 ribs, 1 piece)"
        if n in RAIL_PIECE_NAMES:
            return "printed base rail FRONT bar (R62 H2D split, 1 piece)"''')
rep('''        "caliber": "T06 R62 prototype: merged printed frame + ONE joined thickened "
                   "base rail (left/right tied by 4 ribs), plain M3 through-joints",''',
'''        "caliber": "T06 R62 prototype: merged printed frame + the R61 joined base "
                   "rail cut at x = -40 into 3 H2D-sized pieces (rear cross-tied "
                   "block + 2 front bars), plain M3 through-joints",''')
rep('''                      "R62 joined the left and right rail into one printed piece",''',
'''                      "R62 joined the left and right rail into one printed piece; "
                      "R62 (this version) cuts that joined piece at x = -40 into "
                      "three H2D-sized printed pieces",''')
rep("        \"base_rail_r62\": {", "        \"base_rail_r62\": {")
rep("            \"pieces\": {n: bbox(final[n]) for n in RAIL_PIECE_NAMES},",
    "            \"pieces\": rail_piece_report(final),")
rep('''            "print_split": None,
            "h2d_note": "joined piece %.0f x %.0f x %.0f mm: minimum enclosing square "
                        "370.5 mm > H2D 325 mm, so it must be printed in two segments "
                        "and bolted back together (not modelled; user: no CAD split)"
                        % (RAIL_X1 - RAIL_X0, 2 * (RAIL_CY + RAIL_WY / 2.0),
                           RAIL_ZT - SOLE_ZB),''',
'''            "print_split": {
                "kind": "pure partition, one plane x = %.1f + the y = 0 gap"
                        % RAIL_SPLIT_X,
                "plane_x_mm": RAIL_SPLIT_X,
                "pieces": list(RAIL_PIECE_NAMES),
                "reason": "x > -40 has no clear band between the rails (the merged "
                          "frame owns |y| <= 62 there from z -3.5 to +20), so the "
                          "left/right join can only live in the rear segment",
                "h2d_limit_mm": H2D_LIMIT,
                "material_added_or_removed_mm3": 0.0,
            },
            "h2d_note": "R61 joined piece 380 x 162 x 26 mm had a minimum enclosing "
                        "square of 383.3 mm > H2D 325 mm; R62 cuts it at x = %.1f into "
                        "a 130 x 162 x 26 mm rear block and two 250 x 18 x 26 mm front "
                        "bars, worst min square %.1f mm <= %.0f mm"
                        % (RAIL_SPLIT_X,
                           min_enclosing_square(RAIL_X1 - RAIL_X0, 162.0), H2D_LIMIT),''')

# 7. section titles
rep('"R62 %s section y=0 (frame + thickened base rail)"',
    '"R62 %s section y=0 (frame + base rail, cut at x = %.0f)" % (name, RAIL_SPLIT_X)')
rep('"R62 %s section y=76 (rail joint / sole root)"',
    '"R62 %s section y=76 (rail joint / sole root, front bar)" % name')

io.open(DST, "w", encoding="utf-8", newline="\n").write(s)
print("wrote %s (%d replacements, %d lines)" % (DST, n, s.count("\n") + 1))
import ast
ast.parse(s)
print("ast OK")
left = [(i + 1, ln) for i, ln in enumerate(s.splitlines())
        if ("JOIN_NAME" in ln or "join_rails" in ln)]
print("stale R61 references: %d" % len(left))
for i, ln in left:
    print("  %4d | %s" % (i, ln.strip()[:110]))

