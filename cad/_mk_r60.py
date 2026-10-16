# -*- coding: utf-8 -*-
"""Derive cad/paddle_launcher_shooter_assembly_r60.py from the R59 generator."""
import io, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

src = Path("cad/paddle_launcher_shooter_assembly_r59.py")
dst = Path("cad/paddle_launcher_shooter_assembly_r60.py")
s = src.read_text(encoding="utf-8")

def rep(old, new, tag, n=1):
    global s
    c = s.count(old)
    assert c == n, "REPLACE FAIL %s: found %d, expected %d" % (tag, c, n)
    s = s.replace(old, new)
    print("ok  %s" % tag)

# --- 1. module docstring ---------------------------------------------------
i0 = s.index(chr(34) * 3)
i1 = s.index(chr(34) * 3, i0 + 3) + 3
Q = chr(34) * 3
new_doc = Q + """T06 R60 -- R59 with a deeper rail sole and NO rail print split.

R60 (2026-10-16, user): "press it down; let the STEP contain every part that
has to be printed -- do NOT split the rail into two parts any more."

Changes versus R59 (cad/paddle_launcher_shooter_assembly_r59.py), nothing else:
  1. SOLE_ZB -7.0 -> -10.0.  cad/_r60_probe.py measures 0.0000 mm3 of frame
     interference over the whole x -170..210, y +-63..81 rail envelope for
     z -14..+2, so the sole can simply go deeper with no relief cut anywhere.
     The frame's lowest solid is unchanged at z = -3.51 (MEASURED), so the
     ground clearance becomes -3.51 - (-10.0) = 6.49 mm (R59: 3.49 mm) and the
     rails are still the only floor contact.  Rail thickness 23 -> 26 mm.
  2. The x = 114 print split is DELETED.  base_rail_+72 / base_rail_-72 are
     each ONE printed piece again, 380 mm long.  380 mm is 55 mm over the
     Bambu Lab H2D single-nozzle 325 mm limit: KNOWN deviation, accepted by
     the user on 2026-10-16 (DEC-0066) and still flagged TBD in the audit.
  3. New deliverable T06_print_set_R60_<variant>.step: every part that has to
     be 3D printed, as separate named bodies in one file -- the merged frame
     plus the two rails.  (The merged frame still needs its own 3D-print split,
     which cad/t06_print_split.py performs separately; the rails no longer do.)
  4. The M3 rail-joint bolts grow by the 3 mm of extra thickness: M3 x 58 at
     the x = 60 tabs, M3 x 63 at the x = 76 tabs.

Unchanged from R59: the frame body (identical to R56/R57), the four O4.6
chassis holes, the 7 x 7 x 2.5 captive-nut pockets, the four M3 rail joints,
vendor COTS bodies excluded from this version, R49 gate holes reserved,
durability / fatigue explicitly out of scope (prototype).

Run:
  .venv-cad/Scripts/python.exe -X utf8 cad/paddle_launcher_shooter_assembly_r60.py pollen --step
""" + Q + "\n"
s = s[:i0] + new_doc + s[i1:]
print("ok  docstring")

# --- 2. output dir ---------------------------------------------------------
rep('OUT = HERE / "output" / "_r59_frame"',
    'OUT = HERE / "output" / "_r60_frame"', "out dir")

# --- 3. sole + drop SPLIT_X ------------------------------------------------
rep('SOLE_ZB = -7.0                         # R59: new, and only, floor contact\n'
    'FRAME_LOWEST = -3.51                   # MEASURED (cad/_r57_floor_probe.py)\n'
    'SPLIT_X = 114.0                        # print split, 24 mm clear of x=90/x=138\n',
    'SOLE_ZB = -10.0                        # R60: only floor contact, 3 mm deeper\n'
    'FRAME_LOWEST = -3.51                   # MEASURED (cad/_r57_floor_probe.py)\n',
    "sole_z + no split")

# --- 4. rail naming --------------------------------------------------------
rep('''def rail_names(y):
    """R59 print-split names for the rail at y = +-76 (the `front` half is the
    one that carries the two M3 rail joints)."""
    t = "+" if y > 0 else "-"
    return ("base_rail_%s_front" % t, "base_rail_%s_rear" % t)


RAIL_PIECE_NAMES = tuple(n for y in (-1, 1) for n in rail_names(y))''',
    '''def rail_name(y):
    """R60: exactly one printed rail per side, named after its centre-line y."""
    return "base_rail_%+d" % (RAIL_CY if y > 0 else -RAIL_CY)


RAIL_PIECE_NAMES = tuple(rail_name(y) for y in (-1, 1))''', "rail_name")

rep('DRILLABLE = tuple(rail_names(y)[0] for y in (-1, 1))   # R59: pierces the rail front',
    'DRILLABLE = tuple(rail_name(y) for y in (-1, 1))      # R60: pierces the one rail',
    "drillable")

rep('FRAME_NAME = "shooter_frame_R59_merged"',
    'FRAME_NAME = "shooter_frame_R60_merged"', "frame name")

# --- 5. make_rail_soles ----------------------------------------------------
rep('''    """R59: keep base_rail_+72 / base_rail_-72 and thicken them DOWNWARDS.

    MEASURED (cad/_r59_probe.py): the box x -170..210, y +-63..81, z -8..2 is
    0.0000 mm3 against the R57 frame, so the sole needs no relief cut.  The
    frame's own lowest solid is z = -3.51, hence SOLE_ZB = -7.0 leaves 3.49 mm
    of air and makes the rails the only floor contact.  Each rail keeps its four
    O4.6 chassis holes (re-drilled through the new 23 mm thickness) and gains a
    7 x 7 x 2.5 nut pocket under each M3 rail joint.  Last step is the H2D print
    split at x = 114.
    """''',
    '''    """R60: keep base_rail_+72 / base_rail_-72 and thicken them DOWNWARDS.

    MEASURED (cad/_r60_probe.py): the box x -170..210, y +-63..81 is 0.0000 mm3
    against the R59/R57 frame over the entire z -14..+2 range, so the sole needs
    no relief cut at any depth we would want.  The frame's own lowest solid is
    z = -3.51, hence SOLE_ZB = -10.0 leaves 6.49 mm of air and makes the rails
    the only floor contact.  Each rail keeps its four O4.6 chassis holes
    (re-drilled through the new 26 mm thickness) and gains a 7 x 7 x 2.5 nut
    pocket under each M3 rail joint.  R60: one printed piece per side, no split.
    """''', "soles docstring")

rep('''        front, rear = rail_names(y)
        out[front] = rail.intersect(K.box(SPLIT_X - RAIL_X0, 900.0, 900.0,
                                         ((RAIL_X0 + SPLIT_X) / 2.0, y, 200.0))).clean()
        out[rear] = rail.intersect(K.box(RAIL_X1 - SPLIT_X, 900.0, 900.0,
                                        ((SPLIT_X + RAIL_X1) / 2.0, y, 200.0))).clean()
        print("[r59] %-22s %s | %-22s %s"
              % (front, bbox(out[front]), rear, bbox(out[rear])), flush=True)''',
    '''        name = rail_name(y)
        out[name] = rail
        print("[r60] %-18s %s" % (name, bbox(rail)), flush=True)''',
    "soles tail")

# --- 6. verify_joints ------------------------------------------------------
rep('        rf = rail_names(1 if y > 0 else -1)[0]',
    '        rf = rail_name(1 if y > 0 else -1)', "verify_joints rf")

# --- 7. run(): labels, meta, exports --------------------------------------
rep('''    print("[r59 %s] base rails KEPT and thickened downwards: %s"''',
    '''    print("[r60 %s] base rails KEPT, thickened downwards, NOT split: %s"''',
    "banner")

rep('''                      "thickened base rail (R59, front/rear H2D print split)"''',
    '''                      "printed thickened base rail (R60, one piece per side)"''',
    "role")

rep('''        "caliber": "T06 R59 prototype: merged printed frame + thickened base rails, plain M3 through-joints",''',
    '''        "caliber": "T06 R60 prototype: merged printed frame + one-piece thickened base "
                   "rails, plain M3 through-joints",''', "caliber")

rep('''            "reason": "R59 user decision: drop the floor plate, thicken the two "
                      "base rails instead so the shell never touches the ground",''',
    '''            "reason": "R59 user decision: drop the floor plate, thicken the two "
                      "base rails instead so the shell never touches the ground; "
                      "R60 pressed the sole 3 mm deeper and dropped the rail split",''',
    "superseded reason")

rep('''        "base_rail_r59": {''', '''        "base_rail_r60": {''', "meta rail key")
rep('''            "thickness_mm": RAIL_ZT - SOLE_ZB,''',
    '''            "length_mm": RAIL_X1 - RAIL_X0,
            "n_pieces": len(RAIL_PIECE_NAMES),
            "thickness_mm": RAIL_ZT - SOLE_ZB,''', "meta rail thickness")
rep('''                              "note": "re-drilled through the full 23 mm thickness"},''',
    '''                              "note": "re-drilled through the full %d mm thickness"
                                      % (RAIL_ZT - SOLE_ZB)},''', "chassis note")
rep('''            "print_split_x_mm": SPLIT_X,
            "pieces_mm": [round(SPLIT_X - RAIL_X0, 1), round(RAIL_X1 - SPLIT_X, 1)],
            "bolts": "M3 x 55 at x=60 tabs, M3 x 60 at x=76 tabs, M3 ISO 4762 socket head",''',
    '''            "print_split": None,
            "h2d_note": "single piece %.0f mm: %.0f mm over the H2D 325 mm limit, "
                        "user-accepted 2026-10-16 (DEC-0066), TBD"
                        % (RAIL_X1 - RAIL_X0, RAIL_X1 - RAIL_X0 - 325.0),
            "bolts": "M3 x 58 at x=60 tabs, M3 x 63 at x=76 tabs, M3 ISO 4762 socket head",''',
    "meta split removal")

rep('''                          "also_drilled": (rail_names(sy)[0],),''',
    '''                          "also_drilled": (rail_name(sy),),''', "also_drilled")

# --- 8. exports ------------------------------------------------------------
rep('''        stem = "T06_shooter_frame_R59_%s" % name''',
    '''        stem = "T06_shooter_frame_R60_%s" % name''', "stem")
rep('''        astem = "T06_shooter_assembly_R59_%s" % name''',
    '''        astem = "T06_shooter_assembly_R60_%s" % name''', "astem")
rep('''        rassy = cq.Assembly(name="T06_base_rail_R59_%s" % name)
        for n in RAIL_PIECE_NAMES:
            rassy.add(final[n], name=n, color=cq.Color(0.72, 0.74, 0.78, 1.0))
        rassy.export(str(OUT / ("T06_base_rail_R59_%s.step" % name)),
                     exportType="STEP")''',
    '''        rassy = cq.Assembly(name="T06_base_rail_R60_%s" % name)
        for n in RAIL_PIECE_NAMES:
            rassy.add(final[n], name=n, color=cq.Color(0.72, 0.74, 0.78, 1.0))
        rassy.export(str(OUT / ("T06_base_rail_R60_%s.step" % name)),
                     exportType="STEP")
        # R60: EVERY part that has to be 3D printed, as separate bodies, one STEP
        pstem = "T06_print_set_R60_%s" % name
        passy = cq.Assembly(name=pstem)
        passy.add(frame, name=FRAME_NAME, color=cq.Color(0.20, 0.56, 0.84, 1.0))
        for n in RAIL_PIECE_NAMES:
            passy.add(final[n], name=n, color=cq.Color(0.72, 0.74, 0.78, 1.0))
        pst = OUT / (pstem + ".step")
        passy.export(str(pst), exportType="STEP")
        meta["print_set_step"] = {"file": pst.name,
                                  "parts": [FRAME_NAME] + list(RAIL_PIECE_NAMES),
                                  "mb": round(pst.stat().st_size / 1e6, 2)}
        print("[r60 %s] print set -> %s (%.2f MB)"
              % (name, pst.name, meta["print_set_step"]["mb"]), flush=True)''',
    "print set export")

rep('''        print("[r55 %s] STEP frame %.2f MB / assembly %.1f MB"''',
    '''        print("[r60 %s] STEP frame %.2f MB / assembly %.1f MB"''', "step print tag")

# --- 9. section figures ----------------------------------------------------
rep('''                    SECT / ("r59_%s_section_y0.png" % name),
                    "R59 %s section y=0 (frame + thickened base rail)" % name)''',
    '''                    SECT / ("r60_%s_section_y0.png" % name),
                    "R60 %s section y=0 (frame + thickened base rail)" % name)''',
    "sect y0")
rep('''                    SECT / ("r59_%s_section_y76.png" % name),
                    "R59 %s section y=76 (rail joint / sole root)" % name)''',
    '''                    SECT / ("r60_%s_section_y76.png" % name),
                    "R60 %s section y=76 (rail joint / sole root)" % name)''',
    "sect y76")
rep('''        section_png(final, 0.0, SECT / ("r59_%s_assembly_y0.png" % name),
                    "R59 %s full assembly, y=0" % name)''',
    '''        section_png(final, 0.0, SECT / ("r60_%s_assembly_y0.png" % name),
                    "R60 %s full assembly, y=0" % name)''', "sect asm")

# --- 10. report writes -----------------------------------------------------
rep('''    (OUT / ("report_r57_%s.json" % name)).write_text(
        json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")
    lo = min(s_.BoundingBox().zmin for s_ in final.values())
    meta["lowest_point"] = {"z_mm": round(lo, 2), "part": [
        n for n, s_ in final.items() if abs(s_.BoundingBox().zmin - lo) < 0.01]}
    print("[r59 %s] lowest point z=%.2f in %s" % (name, lo, meta["lowest_point"]["part"]),
          flush=True)
    (OUT / ("report_r59_%s.json" % name)).write_text(
        json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")
    print("[r59 %s] done in %.1f s" % (name, time.time() - t0), flush=True)''',
    '''    lo = min(s_.BoundingBox().zmin for s_ in final.values())
    meta["lowest_point"] = {"z_mm": round(lo, 2), "part": [
        n for n, s_ in final.items() if abs(s_.BoundingBox().zmin - lo) < 0.01]}
    print("[r60 %s] lowest point z=%.2f in %s" % (name, lo, meta["lowest_point"]["part"]),
          flush=True)
    (OUT / ("report_r60_%s.json" % name)).write_text(
        json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")
    print("[r60 %s] done in %.1f s" % (name, time.time() - t0), flush=True)''',
    "report writes")

# --- 11. two leftover R59 comments ---------------------------------------
rep('# --- R59: base_rail_+72 / base_rail_-72 stay, thickened DOWNWARDS ----------',
    '# --- R60: base_rail_+72 / base_rail_-72 stay, thickened DOWNWARDS ----------',
    "rail header")
rep('    others.update(make_rail_soles(rails))      # R59: rail -> rail + sole',
    '    others.update(make_rail_soles(rails))      # R60: rail -> rail + sole',
    "update comment")

# --- sanity ---------------------------------------------------------------
for bad in ("rail_names", "SPLIT_X", "_r59_frame", "report_r57", "report_r59"):
    assert bad not in s, "leftover token: %s" % bad
assert s.count("rail_name(") >= 5
dst.write_text(s, encoding="utf-8")
print("written %s  (%d lines)" % (dst, s.count(chr(10))))
