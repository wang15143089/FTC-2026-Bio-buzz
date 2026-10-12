import json, pathlib
P = pathlib.Path("simulation/mujoco/out")
rows = json.loads((P/"_r38_v8n86.json").read_text(encoding="utf-8"))
r = [x for x in rows if x["ph0"] == 150.0][0]
for k in (1, 3):          # 两颗 NECTAR
    tr = r["trace"][k]
    print("\n--- 球%d %s (轮内 %.2f s, v=%.2f) ---" % (k+1, r["mix"][k], r["exit"][k]["cyc_t"], r["exit"][k]["v"]))
    prev = None; segs = []
    for s in tr:
        st = "P" if s["v"] < 0.05 else ("S" if s["v"] < 0.5 else "F")
        if prev is None or st != prev[0]:
            segs.append([st, s["t"], s["t"], s["v"], s["ang"], s["lx"], s["ln"]])
        else:
            segs[-1][2] = s["t"]; segs[-1][3] = max(segs[-1][3], s["v"])
        prev = (st, s)
    names = {"P": "停住", "S": "慢爬", "F": "快速"}
    for st, t0, t1, vm, ang, lx, ln in segs:
        if t1 - t0 < 0.15: continue
        print("   %s %6.2f~%6.2f (%5.2f s) vmax=%5.2f  末端 ang=%6.1f lx=%7.1f ln=%6.1f"
              % (names[st], t0, t1, t1-t0, vm, ang, lx, ln))
print("\n--- 对照 POLLEN 球1 ---")
tr = r["trace"][0]
prev=None; segs=[]
for s in tr:
    st = "P" if s["v"] < 0.05 else ("S" if s["v"] < 0.5 else "F")
    if prev is None or st != prev[0]:
        segs.append([st, s["t"], s["t"], s["v"], s["ang"], s["lx"], s["ln"]])
    else:
        segs[-1][2]=s["t"]; segs[-1][3]=max(segs[-1][3], s["v"])
    prev=(st,s)
names={"P":"停住","S":"慢爬","F":"快速"}
for st,t0,t1,vm,ang,lx,ln in segs:
    if t1-t0 < 0.15: continue
    print("   %s %6.2f~%6.2f (%5.2f s) vmax=%5.2f  末端 ang=%6.1f lx=%7.1f ln=%6.1f"
          % (names[st], t0, t1, t1-t0, vm, ang, lx, ln))
