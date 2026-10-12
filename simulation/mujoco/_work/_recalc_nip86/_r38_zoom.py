import json, pathlib
P = pathlib.Path("simulation/mujoco/out")
rows = json.loads((P/"_r38_v8n86.json").read_text(encoding="utf-8"))
r = [x for x in rows if x["ph0"] == 150.0][0]
for k in range(4):
    e = r["exit"][k]; tr = r["trace"][k]
    seg = [s for s in tr if e["t"] - 3.2 <= s["t"] <= e["t"] + 0.2]
    print("\n--- 球%d %s 出膛 t=%.2f v=%.2f ---" % (k+1, r["mix"][k], e["t"], e["v"]))
    print("  " + " | ".join("t=%.2f v=%.2f lx=%6.1f ln=%6.1f J=%5.1f" %
          (s["t"], s["v"], s["lx"], s["ln"], s["J"]) for s in seg[::2]))
