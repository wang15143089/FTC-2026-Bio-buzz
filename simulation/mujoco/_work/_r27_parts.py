import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
V = json.loads(Path("cad/output/paddle_launcher_feeder_a_prime_shared_report_nectar.json").read_text(encoding="utf-8"))["variants"]["nectar"]
for k in ("removed_from_parent", "relieved_from_parent", "consumed_by_rotor_drum", "kept_part_count"):
    print(k, "=", json.dumps(V.get(k), ensure_ascii=False))
print("kept parts =", json.dumps(sorted(V.get("kept_parts", [])), ensure_ascii=False))
