import json, pathlib
P = pathlib.Path("simulation/mujoco/out")
def travel(rows, label):
    print("\n== %s ==" % label)
    for nm in ("POLLEN", "NECTAR"):
        ts = []
        for r in rows:
            for k, e in enumerate(r["exit"]):
                if not e or r["mix"][k] != nm: continue
                tr = r["trace"][k]
                # 最后一次「静止」时刻 = 拾取时刻
                last_still = 0.0
                for s in tr:
                    if s["t"] > e["t"]: break
                    if s["v"] < 0.05: last_still = s["t"]
                ts.append(e["t"] - last_still)
        if ts:
            print("   %-7s n=%2d  实际运送 %5.2f~%5.2f  均 %5.2f s" % (nm, len(ts), min(ts), max(ts), sum(ts)/len(ts)))
def load(n):
    f = P/n
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else []
travel(load("_r38_v8long.json") + load("_r38_v8rest.json"), "基准 夹口82")
travel(load("_r38_v8n86.json"), "重算 夹口86")
