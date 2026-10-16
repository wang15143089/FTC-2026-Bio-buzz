import json, io
a = json.load(io.open("cad/output/_r60_frame/report_r60_pollen.json", encoding="utf-8"))
b = json.load(io.open("cad/output/_r61_frame/report_r61_pollen.json", encoding="utf-8"))
ma, mb = a["merged_into_frame"], b["merged_into_frame"]
for k in ("members", "gussets", "tie_pads", "rail_tabs"):
    sa, sb = set(ma[k]), set(mb[k])
    print("%-10s R60 %2d  R61 %2d   onlyR60=%s onlyR61=%s"
          % (k, len(ma[k]), len(mb[k]), sorted(sa - sb), sorted(sb - sa)))
print("frame volume  R60 %.1f  R61 %.1f  delta %+.1f" % (ma["volume_mm3"], mb["volume_mm3"], mb["volume_mm3"] - ma["volume_mm3"]))
print("frame bbox    R60", ma["bbox"])
print("              R61", mb["bbox"])
print("solids_after_fuse", ma["solids_after_fuse"], mb["solids_after_fuse"])
ga = {r["id"]: r for r in a["m3_joints"]}
gb = {r["id"]: r for r in b["m3_joints"]}
print("m3 joint ids R60", sorted(ga), "\n            R61", sorted(gb))
for k in sorted(set(ga) | set(gb)):
    if ga.get(k, {}).get("material_mm3") != gb.get(k, {}).get("material_mm3"):
        print("  joint %s material R60 %s R61 %s" % (k, ga.get(k, {}).get("material_mm3"), gb.get(k, {}).get("material_mm3")))
va = {r["id"]: r for r in a["joint_verification"]}
vb = {r["id"]: r for r in b["joint_verification"]}
for k in sorted(set(va) | set(vb)):
    if va.get(k) != vb.get(k):
        print("  verify %s:\n    R60 %s\n    R61 %s" % (k, va.get(k), vb.get(k)))
