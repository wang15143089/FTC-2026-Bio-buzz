import json
from pathlib import Path
r = json.loads(Path("cad/output/paddle_launcher_feeder_a_prime_shared_report_pollen.json").read_text(encoding="utf-8"))
def walk(o, pre=""):
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, (dict, list)):
                print(pre + k)
                walk(v, pre + "  ")
            else:
                print(pre + k, "=", v)
walk(r)
