import json, pathlib
p = pathlib.Path("simulation/mujoco/out")
g = json.loads((p/"_r29_grid.json").read_text(encoding="utf-8"))
m = json.loads((p/"_r30_margin.json").read_text(encoding="utf-8"))
print("r29 n=", len(g)); print("sample:", json.dumps(g[0], ensure_ascii=False)[:600])
print("r30 n=", len(m)); print("sample:", json.dumps(m[0], ensure_ascii=False)[:600])
def tab(rows, title):
    print("=====", title)
    for r in rows:
        print("  ", json.dumps(r, ensure_ascii=False)[:260])
tab(m, "R30 margin rows")
