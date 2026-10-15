# -*- coding: utf-8 -*-
"""Derive R57 from R56: delete both base rails, add one floor plate."""
src = open("cad/paddle_launcher_shooter_assembly_r56.py", encoding="utf-8").read()

def rep(old, new, n=1):
    global src
    assert src.count(old) == n, ("NOT FOUND x%d: %r" % (src.count(old), old[:70]))
    src = src.replace(old, new)

# 1. docstring
rep('"""T06 R56 -- R55 assembly-friendly frame with the intake tray lengthened.',
    '"""T06 R57 -- R56 frame/tray, but the two base rails become ONE floor plate.')
rep('''Run:
  .venv-cad/Scripts/python.exe -X utf8 cad/paddle_launcher_shooter_assembly_r55.py pollen --step
"""''',
    '''R57 (2026-10-14, user): "不要这根轨道, 改为一个可以放在地上的平面, 确保这是整个
机构最低点".  MEASURED (cad/_r57_floor_probe.py): the frame's own lowest solid is
z = -3.51 (tray underside, x 20..40), so a FLAT plate top at z = -5.5 clears the
whole frame by 2.0 mm -> no window/relief needed.  MEASURED
(cad/_r57_column_probe.py): the four columns under the rail tabs (x 60/76,
y +-76) are empty, so a pillar can be raised there.  Result: one floor plate
(315 x 210 x 6, single H2D-sized print) + 4 pillars to z = 16; the plate bottom
z = -11.5 is the new lowest point of the whole mechanism.  Frame body itself is
byte-identical to R56 (tabs kept, only DRILL_LEN extended past the plate).

Run:
  .venv-cad/Scripts/python.exe -X utf8 cad/paddle_launcher_shooter_assembly_r57.py pollen --step
"""''')

# 2. output dir + reuse the R56 brep cache
rep('OUT = HERE / "output" / "_r56_frame"', 'OUT = HERE / "output" / "_r57_frame"')
rep('''CACHE = OUT / "cache"
CACHE.mkdir(parents=True, exist_ok=True)''',
    '''# R57: identical upstream chain, so reuse the R56 BREP cache (no 165 s rebuild)
CACHE = HERE / "output" / "_r56_frame" / "cache"
CACHE.mkdir(parents=True, exist_ok=True)''')

# 3. floor-plate constants (before DRILLABLE, which now names the plate)
rep('''# --- M3 bolted joints -------------------------------------------------------''',
    '''# --- R57 floor plate (replaces base_rail_+72 / base_rail_-72) ---------------
PLATE_X0, PLATE_X1 = -137.0, 178.0     # 315 mm  (H2D 325, margin 10)
PLATE_Y0, PLATE_Y1 = -105.0, 105.0     # 210 mm  (H2D 320)
PLATE_ZT, PLATE_T = -5.5, 6.0          # top face z, thickness (MEASURED -3.51)
PLATE_ZB = PLATE_ZT - PLATE_T          # -11.5 = lowest point of the mechanism
PIL_DX, PIL_DY = 12.0, 16.0            # pillar = tab footprint (x 54..66 / 70..82)
TAB_BOTTOM = 16.0                      # tabs land here (unchanged from R55/R56)
NUT_POCKET, NUT_DEPTH = 7.0, 2.5       # square captive-nut pocket in the underside
PLATE_NAME = "floor_plate_R57"

# --- M3 bolted joints -------------------------------------------------------''')

rep('DRILLABLE = ("base_rail_+72", "base_rail_-72")   # joint bolts pierce these too',
    'DRILLABLE = ("floor_plate_R57",)   # R57: the rail joint bolt pierces the plate')
rep('''DRILL_LEN = 60.0           # z 26 +- 30 = -4..56: through tab + rail, exits free
DRILL_ZC = 26.0''',
    '''# R57: z 20 +- 36 = -16..56 -> through tab + pillar + floor plate, exits free
DRILL_LEN = 72.0
DRILL_ZC = 20.0''')

rep('FRAME_NAME = "shooter_frame_R56_merged"', 'FRAME_NAME = "shooter_frame_R57_merged"')

# 3b. delete both base rails from this version (user decision, R57)
rep('''    print("[r55 %s] keep %d / vendor %d / gate %d"
          % (name, len(keep), len(vendor), len(gate)), flush=True)''',
    '''    print("[r55 %s] keep %d / vendor %d / gate %d"
          % (name, len(keep), len(vendor), len(gate)), flush=True)
    rails = {n: keep.pop(n) for n in ("base_rail_+72", "base_rail_-72") if n in keep}
    print("[r57 %s] base rails DELETED: %s" % (name, sorted(rails)), flush=True)''')

# 4. plate builder
rep('''def drill_holes(frame, specs, keep_others):''',
    '''def make_floor_plate():
    """R57: one flat plate on the ground + one pillar under each rail tab.

    Numbers are MEASURED from the R56 STEP, not assumed:
      frame lowest solid      z = -3.51   -> plate top -5.5 (2.0 mm clearance)
      tab bottom / footprint  z = 16, 12 x 16 at x 60 & 76, y +-76
      column below each tab   0.000 mm3   -> a pillar there hits nothing
    The nut stays inside a 7 x 7 x 2.5 pocket in the underside, so nothing at
    all protrudes below z = -11.5 (the plate stays the lowest point).
    """
    solids = [K.box(PLATE_X1 - PLATE_X0, PLATE_Y1 - PLATE_Y0, PLATE_T,
                    ((PLATE_X0 + PLATE_X1) / 2.0, 0.0, PLATE_ZT - PLATE_T / 2.0))]
    solids += [K.box(PIL_DX, PIL_DY, TAB_BOTTOM - PLATE_ZT,
                     (x, sy, (TAB_BOTTOM + PLATE_ZT) / 2.0)) for x, sy in HOLE_XY]
    plate = fuse_all(solids)
    plate = plate.cut(*[K.box(NUT_POCKET, NUT_POCKET, NUT_DEPTH,
                              (x, sy, PLATE_ZB + NUT_DEPTH / 2.0))
                        for x, sy in HOLE_XY]).clean()
    return {PLATE_NAME: plate}


def drill_holes(frame, specs, keep_others):''')

rep('''    tabs = make_rail_tabs(others, bbs)
    frame = fuse_all(''',
    '''    tabs = make_rail_tabs(others, bbs)
    others.update(make_floor_plate())          # R57: rail -> floor plate
    frame = fuse_all(''')

# 5. nut-space probe must look BELOW the plate now
rep('''        below = [(n, round(cyl("z", 2.6, 9.0, (x, y, -3.5)).intersect(s).Volume(), 2))
                 for n, s in others.items()
                 if cyl("z", 2.6, 9.0, (x, y, -3.5)).intersect(s).Volume() > 0.5]''',
    '''        below = [(n, round(cyl("z", 2.6, 6.0, (x, y, -16.0)).intersect(s).Volume(), 2))
                 for n, s in others.items()
                 if cyl("z", 2.6, 6.0, (x, y, -16.0)).intersect(s).Volume() > 0.5]''')

# 6. role of the new part + meta note
rep('''             "role": ("printed frame (merged)" if n == FRAME_NAME else "kept")}''',
    '''             "role": ("printed frame (merged)" if n == FRAME_NAME else
                      "floor plate + 4 pillars (R57, replaces base_rail)"
                      if n == PLATE_NAME else "kept")}''')
rep('''        "m3_joints": done,''',
    '''        "removed_from_this_version": {
            "parts": ["base_rail_+72", "base_rail_-72"],
            "reason": "R57 user decision: delete the rails, stand the assembly on "
                      "ONE floor plate whose underside is the lowest point",
            "detail": "base_rail was 380 x 18 x 14 at y = +-72, z 2..16 (over the "
                      "H2D 325 mm limit); floor_plate_R57 is %d x %d x %.1f mm"
                      % (PLATE_X1 - PLATE_X0, PLATE_Y1 - PLATE_Y0, PLATE_T)},
        "floor_plate": {
            "name": PLATE_NAME,
            "bbox_mm": {"x": [PLATE_X0, PLATE_X1], "y": [PLATE_Y0, PLATE_Y1],
                        "z": [PLATE_ZB, TAB_BOTTOM]},
            "plate_top_z": PLATE_ZT, "plate_bottom_z": PLATE_ZB,
            "clearance_to_frame_mm": round(PLATE_ZT - (-3.51), 2),
            "pillars": [{"x": x, "y": sy, "dx": PIL_DX, "dy": PIL_DY,
                         "top_z": TAB_BOTTOM} for x, sy in HOLE_XY],
            "nut_pocket": {"square_mm": NUT_POCKET, "depth_mm": NUT_DEPTH,
                           "note": "M3 hex nut 5.5 A/F x 2.4 sits inside, nothing "
                                   "protrudes below the plate bottom"},
            "bolts": "M3 x 55 at x=60 tabs, M3 x 60 + 1.5 washer at x=76 tabs"},
        "m3_joints": done,''')

# 7. exports / reports / sections
rep('stem = "T06_shooter_frame_R56_%s" % name', 'stem = "T06_shooter_frame_R57_%s" % name')
rep('astem = "T06_shooter_assembly_R56_%s" % name', 'astem = "T06_shooter_assembly_R57_%s" % name')
rep('("report_r56_%s.json" % name)', '("report_r57_%s.json" % name)')
rep('"R56 %s section y=0 (frame + kept parts)" % name',
    '"R57 %s section y=0 (frame + floor plate)" % name')
rep('"R56 %s section y=64 (plate-to-tray gusset zone)" % name',
    '"R57 %s section y=64 (plate-to-tray gusset zone)" % name')
rep('"R56 %s full kept assembly, y=0" % name', '"R57 %s full assembly, y=0" % name')
rep('r56_%s_section_y0.png', 'r57_%s_section_y0.png')
rep('r56_%s_section_y64.png', 'r57_%s_section_y64.png')
rep('r56_%s_assembly_y0.png', 'r57_%s_assembly_y0.png')
rep('"caliber": "T06 R55 prototype: merged printed frame + plain M3 through-joints",',
    '"caliber": "T06 R57 prototype: merged printed frame + floor plate, plain M3 through-joints",')

# 8. HOLE_XY helper (shared by the plate, the drill specs and the joint check)
rep('''def bbox(shape):''',
    '''# R57: the four rail-joint columns, (x, y) -- one pillar/hole each
HOLE_XY = ((60.0, -BOLT_Y), (60.0, BOLT_Y), (76.0, -BOLT_Y), (76.0, BOLT_Y))


def bbox(shape):''')
rep('''R57 floor plate (replaces base_rail_+72 / base_rail_-72) ---------------''',
    '''R57 floor plate (replaces base_rail_+72 / base_rail_-72) ---------------''')

# 9. post-review fixes (2026-10-14, found by cad/_r57_audit.py on the first build)
#    a) the M3 joint must pierce the floor plate as well
rep('''            specs.append({"axis": "z", "len": DRILL_LEN,
                          "center": (x, sy * BOLT_Y, DRILL_ZC),
                          "need": 20.0,
                          "joint": "rail tab -> base rail (M3 bolt + nut, through both)",
                          "id": "rail_x%.0f_%+d" % (x, sy)})''',
    '''            specs.append({"axis": "z", "len": DRILL_LEN,
                          "center": (x, sy * BOLT_Y, DRILL_ZC),
                          "need": 20.0,
                          "joint": "rail tab -> floor plate pillar (M3 bolt + nut, through both)",
                          "also_drilled": (PLATE_NAME,),
                          "id": "rail_x%.0f_%+d" % (x, sy)})''')
#    b) verify the joints AFTER cutting, otherwise the probe measures the tab body
rep('''    done, skipped = drill_holes(frame, specs, others)
    joint_check = verify_joints(frame, done, others, tabs)
    for h in done:
        c = cyl(h["axis"], M3_CLR_R, h["len"], tuple(h["center"]))
        frame = frame.cut(c)
        for n in h.get("also_drilled", ()):
            others[n] = others[n].cut(c)
''',
    '''    done, skipped = drill_holes(frame, specs, others)
    for h in done:
        c = cyl(h["axis"], M3_CLR_R, h["len"], tuple(h["center"]))
        frame = frame.cut(c)
        for n in h.get("also_drilled", ()):
            others[n] = others[n].cut(c)
    joint_check = verify_joints(frame, done, others, tabs)
''')
#    c) nothing may stick out below the plate, and the nut must sit in its pocket
rep('''        below = [(n, round(cyl("z", 2.6, 6.0, (x, y, -16.0)).intersect(s).Volume(), 2))
                 for n, s in others.items()
                 if cyl("z", 2.6, 6.0, (x, y, -16.0)).intersect(s).Volume() > 0.5]
        row = {"id": h["id"], "axis_y": y, "tab_top_z": ztop,
               "axis_material_mm3": axis, "wall_in_mm3": wall_in,
               "wall_out_mm3": wall_out, "side_plate_probe_mm3": plate,
               "nut_side_blockers": below,
               "through_hole": axis < 0.05 and wall_in > 1.0 and wall_out > 1.0,
               "plate_intact": plate > 1.0, "nut_space_clear": not below}''',
    '''        below = [(n, round(cyl("z", 2.6, 6.0, (x, y, -17.0)).intersect(s).Volume(), 2))
                 for n, s in others.items()
                 if cyl("z", 2.6, 6.0, (x, y, -17.0)).intersect(s).Volume() > 0.5]
        pocket = round(cyl("z", 3.0, 2.4, (x, y, PLATE_ZB + 1.2))
                       .intersect(others[PLATE_NAME]).Volume(), 2)
        row = {"id": h["id"], "axis_y": y, "tab_top_z": ztop,
               "axis_material_mm3": axis, "wall_in_mm3": wall_in,
               "wall_out_mm3": wall_out, "side_plate_probe_mm3": plate,
               "below_plate_blockers": below, "nut_pocket_material_mm3": pocket,
               "through_hole": axis < 0.05 and wall_in > 1.0 and wall_out > 1.0,
               "plate_intact": plate > 1.0,
               "nut_space_clear": (not below) and pocket < 0.05}''')
rep('''        print("[r55] joint %-14s axis_empty=%.3f walls in/out=%.2f/%.2f "
              "plate=%.2f nut_clear=%s pass=%s"
              % (row["id"], axis, wall_in, wall_out, plate, not below,''',
    '''        print("[r55] joint %-14s axis_empty=%.3f walls in/out=%.2f/%.2f "
              "plate=%.2f nut_pocket=%.2f nut_clear=%s pass=%s"
              % (row["id"], axis, wall_in, wall_out, plate, pocket, row["nut_space_clear"],''')
#    d) meta: the plate top is BELOW the frame, so the gap is positive downwards
rep('''            "clearance_to_frame_mm": round(PLATE_ZT - (-3.51), 2),''',
    '''            "gap_to_frame_lowest_mm": round(-3.51 - PLATE_ZT, 2),
            "floor_plate_is_lowest": True,''')
#    e) also ship the floor plate on its own (for print/assembly)
rep('''        meta["assembly_step_mb"] = round(dst.stat().st_size / 1e6, 1)''',
    '''        cq.exporters.export(cq.Workplane(obj=final[PLATE_NAME]),
                        str(OUT / ("T06_floor_plate_R57_%s.step" % name)))
        meta["assembly_step_mb"] = round(dst.stat().st_size / 1e6, 1)''')

open("cad/paddle_launcher_shooter_assembly_r57.py", "w", encoding="utf-8").write(src)
print("written cad/paddle_launcher_shooter_assembly_r57.py", len(src), "chars")
