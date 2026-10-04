import copy, json, pathlib
out = pathlib.Path("cad/output")
files = {n: out / ("paddle_launcher_feeder_a_prime_shared_report_%s.json" % n)
         for n in ("nectar", "pollen")}
merged = None
for n, f in files.items():
    d = json.loads(f.read_text(encoding="utf-8"))
    if merged is None:
        merged = copy.deepcopy(d)
        merged["variants"] = {}
        merged["merged_from"] = sorted(str(p).replace("\\", "/") for p in files.values())
    merged["variants"][n] = d["variants"][n]
merged["variants_order"] = ["nectar", "pollen"]
merged["shared_check"] = {
    "note": "Both variants must agree on every shared, ball-independent number.",
    "shell_volume_equal": merged["variants"]["nectar"]["shell_volume_mm3"]
    == merged["variants"]["pollen"]["shell_volume_mm3"],
    "hub_to_shell_equal": merged["variants"]["nectar"]["paddle_hub_to_shell_inner_arc_measured_mm"]
    == merged["variants"]["pollen"]["paddle_hub_to_shell_inner_arc_measured_mm"],
    "shell_bbox_equal": merged["variants"]["nectar"]["measured_from_final_solids"]["shell_bbox_min_mm"]
    == merged["variants"]["pollen"]["measured_from_final_solids"]["shell_bbox_min_mm"],
    "only_nip_differs_mm": {
        n: merged["variants"][n]["flywheel_nip_measured_mm"] for n in ("nectar", "pollen")},
    "carry_radius_mm": {n: merged["variants"][n]["carry_radius_mm"] for n in ("nectar", "pollen")},
}
p = out / "paddle_launcher_feeder_a_prime_shared_report.json"
p.write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding="utf-8")
print("wrote", p)
print(json.dumps(merged["shared_check"], indent=2, ensure_ascii=False))
