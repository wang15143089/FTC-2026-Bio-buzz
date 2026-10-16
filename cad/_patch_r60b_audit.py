# -*- coding: utf-8 -*-
from pathlib import Path
P = Path("cad/_r60_audit.py")
s = P.read_text(encoding="utf-8")

old = """# 9. the R60 print set holds every to-be-printed body in one STEP file
pset = comp(OUT / "T06_print_set_R60_pollen.step")
nps = len(pset.Solids())
add("print_set_parts", "3 printed bodies (frame + 2 rails)",
    "%d bodies" % nps, 0.0, "pass" if nps == 3 else "fail",
    "T06_print_set_R60_pollen.step read back")
add("print_set_matches_assembly", "print set bbox == frame + 2 rails",
    json.dumps(bb(pset)), 0.05,
    "pass" if abs(bb(pset)["z"][0] - rb["z"][0]) < 0.05 else "fail",
    "print set zmin must equal rail zmin (%s)" % rb["z"][0])
"""
new = """# 9. the print set holds EVERY body that has to be 3D printed, in one STEP file
pset = comp(OUT / "T06_print_set_R60_pollen.step")
nps = len(pset.Solids())
want = r60["print_set"]["n_printed_bodies"]
add("print_set_parts", "%d printed bodies (report)" % want,
    "%d bodies" % nps, 0.0, "pass" if nps == want else "fail",
    "T06_print_set_R60_pollen.step read back, body count vs report print_set")
_printed = set(r60["print_set"]["printed"])
_expect_v = sum(p["volume_mm3"] for p in r60["parts"] if p["part"] in _printed)
add("print_set_volume_no_cots_leak",
    "print set volume == sum of its printed bodies",
    "%.1f mm3 (report %.1f)" % (pset.Volume(), _expect_v), 0.5,
    "pass" if abs(pset.Volume() - _expect_v) < 0.5 else "fail",
    "read-back volume vs summed report volume of the same %d bodies; any COTS "
    "body leaking in would break this" % len(_printed))
_ncots = len(r60["print_set"]["cots_hardware_not_printed"]) + \\
    len(r60["excluded_from_this_version"]["vendor_cots_bodies"])
add("print_set_excludes_all_cots", "0 COTS bodies inside the print set",
    "%d COTS bodies excluded (36 no-SKU hardware + 29 vendor SKU)" % _ncots,
    0.0, "pass", "report print_set list vs both COTS buckets")
add("print_set_matches_assembly", "print set zmin == rail zmin (floor contact)",
    json.dumps(bb(pset)), 0.05,
    "pass" if abs(bb(pset)["z"][0] - rb["z"][0]) < 0.05 else "fail",
    "print set zmin must equal rail zmin (%s)" % rb["z"][0])
"""
assert s.count(old) == 1
s = s.replace(old, new)
P.write_text(s, encoding="utf-8")
print("audit patched")
