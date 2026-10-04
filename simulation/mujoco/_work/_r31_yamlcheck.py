import yaml, pathlib
d = yaml.safe_load(pathlib.Path("config/parameters.yaml").read_text(encoding="utf-8"))
s = d["t06_feeder_a_prime_shared"]
print("shared keys:", len(s))
print("blade_phase:", s["shared_paddle_blade_phase"]["value"])
print("sweep:", s["index_drive_sweep"]["value"])
print("nectar:", {k: v["value"] for k, v in s["variants"]["nectar"].items()})
print("pollen:", {k: v["value"] for k, v in s["variants"]["pollen"].items()})
print("nectar section status:", d["t06_feeder_a_prime_nectar"]["status_note"]["status"])
print("total top-level keys:", len(d))
