import json, pathlib
P = pathlib.Path("simulation/mujoco/out")
def load(name):
    f = P / name
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else None
def summarise(rows, label):
    if not rows: print(label, "缺失"); return
    n = sum(len(r["mix"]) for r in rows)
    print("\n== %s：%d 轮 %d 颗 ==" % (label, len(rows), n))
    print("  全清轮 %d/%d   真出膛 %d/%d" % (sum(1 for r in rows if r["n_launched"]==len(r["mix"])), len(rows),
          sum(1 for r in rows for e in r["exit"] if e and e["v"]>=3.0), n))
    for nm in ("POLLEN","NECTAR"):
        es = [e for r in rows for k,e in enumerate(r["exit"]) if e and r["mix"][k]==nm]
        if not es: continue
        v = [e["v"] for e in es]; ct = [e["cyc_t"] for e in es]
        im = [e.get("imp") for e in es]; pk = [e.get("fmax") for e in es]
        print("  %-7s n=%2d  v %5.2f~%5.2f (均%5.2f)  轮内 %5.2f~%5.2f (均%5.2f)  冲量均 %5.2f  峰力均 %6.1f" %
              (nm, len(es), min(v), max(v), sum(v)/len(v), min(ct), max(ct), sum(ct)/len(ct),
               sum(x for x in im if x)/max(1,len([x for x in im if x])),
               sum(x for x in pk if x)/max(1,len([x for x in pk if x]))))
    tt = [r.get("t_total_s") for r in rows if r.get("t_total_s")]
    if tt: print("  清空时间 均 %.2f s  最慢 %.2f s" % (sum(tt)/len(tt), max(tt)))
for name,lab in (("_r38_v8n86.json","重算：NECTAR 夹口 86"),("_r38_v8mix.json","基准：NECTAR 夹口 82")):
    summarise(load(name), lab)
