import json, pathlib
P = pathlib.Path("simulation/mujoco/out")
def load(name):
    f = P / name
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else []
def summarise(rows, label):
    if not rows: print(label, "缺失"); return
    n = sum(len(r["mix"]) for r in rows)
    print("\n== %s ==   %d 轮 %d 颗" % (label, len(rows), n))
    print("   全清轮 %d/%d   真出膛(v>=3) %d/%d" % (
        sum(1 for r in rows if r["n_launched"] == len(r["mix"])), len(rows),
        sum(1 for r in rows for e in r["exit"] if e and e["v"] >= 3.0), n))
    for nm in ("POLLEN", "NECTAR"):
        v, ct, imp, pk = [], [], [], []
        for r in rows:
            for k, e in enumerate(r["exit"]):
                if e and r["mix"][k] == nm:
                    v.append(e["v"]); ct.append(e["cyc_t"])
                    imp.append(r["wheel_imp"][k]); pk.append(r["wheel_peak"][k])
        if not v: continue
        print("   %-7s n=%2d  v %5.2f~%5.2f 均%5.2f | 轮内 %5.2f~%5.2f 均%5.2f | 冲量均%6.2f N*s | 峰力均%6.1f N" %
              (nm, len(v), min(v), max(v), sum(v)/len(v), min(ct), max(ct), sum(ct)/len(ct),
               sum(imp)/len(imp), sum(pk)/len(pk)))
    tt = [r.get("t_total_s") for r in rows if r.get("t_total_s")]
    if tt: print("   清空时间 均%.2f 最慢%.2f s   拨杆扭矩峰 %.3f N*m" % (sum(tt)/len(tt), max(tt), max(r["tq_peak"] for r in rows)))
    jf = [r["jam_frac"] for r in rows]
    if jf: print("   驱动卡滞占比 均%.0f%% 最差%.0f%%" % (100*sum(jf)/len(jf), 100*max(jf)))
base = load("_r38_v8long.json") + load("_r38_v8rest.json")
summarise(base, "基准 重算前：NECTAR 夹口 82")
summarise(load("_r38_v8n86.json"), "重算后：NECTAR 夹口 86")
