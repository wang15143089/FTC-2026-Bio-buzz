# -*- coding: utf-8 -*-
"""R60b patch: print set = EVERY body that has to be 3D printed."""
from pathlib import Path

P = Path("cad/paddle_launcher_shooter_assembly_r60.py")
s = P.read_text(encoding="utf-8")

def rep(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:80])
    s = s.replace(old, new)

# 1) rules: COTS hardware that carries no catalog SKU, and printed standoffs
old1 = 'GATE_PREFIX = "gate_"\n'
new1 = ('GATE_PREFIX = "gate_"\n'
        '# R60b: bodies that are BOUGHT hardware but carry no goBILDA SKU, so\n'
        '# is_vendor() cannot see them.  They must never enter the print set.\n'
        'HARDWARE_PREFIX = ("carriage_clamp_stud_",     # M4 stud + washer + nyloc\n'
        '                   "carriage_clamp_spring_",   # compression spring\n'
        '                   "carriage_link_pin_",\n'
        '                   "crosshead_through_pin",\n'
        '                   "servo_crank_joint_pin")\n'
        '# R60b: the four gap-servo mounting standoffs are CUSTOM printed structure\n'
        '# (constrained.py adds them with C["structure"]); is_vendor() catches the\n'
        '# "gap_servo_" prefix, so they are pulled back out of the vendor bucket.\n'
        'BRING_BACK_PRINTED = ("gap_servo_standoff_",)\n')
rep(old1, new1)

# 2) run(): move the printed standoffs out of the vendor bucket
old2 = """    keep, vendor, gate = split_parts(parts)
    print("[r55 %s] keep %d / vendor %d / gate %d"
"""
new2 = """    keep, vendor, gate = split_parts(parts)
    for _n in sorted(vendor):
        if _n.startswith(BRING_BACK_PRINTED):
            keep[_n] = vendor.pop(_n)
    print("[r55 %s] keep %d / vendor %d / gate %d"
"""
rep(old2, new2)

# 3) rows: three-way role
old3 = """    rows = [{"part": n, "volume_mm3": round(s.Volume(), 1), "bbox": bbox(s),
             "role": ("printed frame (merged)" if n == FRAME_NAME else
                      "printed thickened base rail (R60, one piece per side)"
                      if n in RAIL_PIECE_NAMES else "kept")}
            for n, s in sorted(final.items())]
"""
new3 = """    printed_set = sorted(n for n in final if n != FRAME_NAME
                         and n not in RAIL_PIECE_NAMES
                         and not n.startswith(HARDWARE_PREFIX))
    printed_names = [FRAME_NAME] + list(RAIL_PIECE_NAMES) + printed_set
    hardware = sorted(n for n in final if n.startswith(HARDWARE_PREFIX))

    def _role(n):
        if n == FRAME_NAME:
            return "printed frame (merged)"
        if n in RAIL_PIECE_NAMES:
            return "printed thickened base rail (R60, one piece per side)"
        if n.startswith(HARDWARE_PREFIX):
            return "COTS hardware, NOT printed"
        return "printed, separate part (in the print set)"

    rows = [{"part": n, "volume_mm3": round(s.Volume(), 1), "bbox": bbox(s),
             "role": _role(n)}
            for n, s in sorted(final.items())]
"""
rep(old3, new3)

# 4) meta: explicit print-set block + hardware bucket
old4 = """        "excluded_from_this_version": {
            "vendor_cots_bodies": sorted(vendor),
            "gate_solids": sorted(gate),
            "note": "gate geometry not modelled; its mounting holes are reserved instead",
        },
"""
new4 = """        "print_set": {
            "n_printed_bodies": len(printed_names),
            "printed": printed_names,
            "cots_hardware_not_printed": hardware,
            "note": "every body that has to be 3D printed, one named body each",
        },
        "excluded_from_this_version": {
            "vendor_cots_bodies": sorted(vendor),
            "cots_hardware_bodies": hardware,
            "gate_solids": sorted(gate),
            "note": "gate geometry not modelled; its mounting holes are reserved instead",
        },
"""
rep(old4, new4)

# 5) export: the whole printed set, not just frame + rails
old5 = """        pstem = "T06_print_set_R60_%s" % name
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
              % (name, pst.name, meta["print_set_step"]["mb"]), flush=True)
"""
new5 = """        pstem = "T06_print_set_R60_%s" % name
        passy = cq.Assembly(name=pstem)
        passy.add(frame, name=FRAME_NAME, color=cq.Color(0.20, 0.56, 0.84, 1.0))
        for n in printed_names:
            if n == FRAME_NAME:
                continue
            col = cq.Color(0.72, 0.74, 0.78, 1.0) if n in RAIL_PIECE_NAMES \\
                else cq.Color(0.70, 0.76, 0.84, 1.0)
            passy.add(final[n], name=n, color=col)
        pst = OUT / (pstem + ".step")
        passy.export(str(pst), exportType="STEP")
        meta["print_set_step"] = {"file": pst.name,
                                  "parts": printed_names,
                                  "n_parts": len(printed_names),
                                  "mb": round(pst.stat().st_size / 1e6, 2)}
        print("[r60 %s] print set -> %s (%d printed bodies, %.2f MB)"
              % (name, pst.name, len(printed_names),
                 meta["print_set_step"]["mb"]), flush=True)
"""
rep(old5, new5)

# 6) header docstring: say what the print set really is
old6 = """  3. New deliverable T06_print_set_R60_<variant>.step: every part that has to
     be 3D printed, as separate named bodies in one file -- the merged frame
     plus the two rails.  (The merged frame still needs its own 3D-print split,
     which cad/t06_print_split.py performs separately; the rails no longer do.)
"""
new6 = """  3. Deliverable T06_print_set_R60_<variant>.step: EVERY body that has to be
     3D printed, as separate named bodies in one file.  R60 first shipped this
     as frame + rails only (3 bodies); R60b corrected it to the whole printed
     set -- frame + two rails + the 42 custom bodies that were merely "kept"
     (bearing carriages, link spacers, main spacing links, crosshead and its
     guides/stops, motor bridges, servo crank + drag link, paddle rotor +
     flex tips, and the 16 rigid clamp seats) plus the four printed gap-servo
     standoffs.  Bought hardware with no catalog SKU (M4 stud / spring / nyloc
     and the three pins) is excluded and listed in the report.
"""
rep(old6, new6)

P.write_text(s, encoding="utf-8")
print("patched OK")
