import json, io
a = json.load(io.open("cad/output/_r60_frame/report_r60_pollen.json", encoding="utf-8"))
b = json.load(io.open("cad/output/_r61_frame/report_r61_pollen.json", encoding="utf-8"))
print("R60 merged_into_frame:", json.dumps(a["merged_into_frame"], ensure_ascii=False)[:300])
print("R61 merged_into_frame:", json.dumps(b["merged_into_frame"], ensure_ascii=False)[:300])
ra = {r["part"]: (r["volume_mm3"], r["bbox"]) for r in a["parts"]}
rb = {r["part"]: (r["volume_mm3"], r["bbox"]) for r in b["parts"]}
print("n_parts R60", a["n_parts"], "R61", b["n_parts"])
only_a = sorted(set(ra) - set(rb)); only_b = sorted(set(rb) - set(ra))
print("only R60:", only_a)
print("only R61:", only_b)
diff = [(k, ra[k][0], rb[k][0]) for k in sorted(set(ra) & set(rb)) if abs(ra[k][0] - rb[k][0]) > 0.05]
print("volume diffs (%d):" % len(diff))
for k, x, y in diff:
    print("   %-34s R60 %12.1f  R61 %12.1f  d=%+.1f" % (k, x, y, y - x))
print("base_rail_r60:", json.dumps(a.get("base_rail_r60"), ensure_ascii=False)[:200])
print("base_rail_r61:", json.dumps(b.get("base_rail_r61"), ensure_ascii=False)[:400])
print("print_set R61:", b["print_set_step"]["n_parts"], b["print_set_step"]["mb"])
