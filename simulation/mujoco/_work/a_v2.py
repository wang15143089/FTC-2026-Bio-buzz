import json, math, glob, os, sys
sys.stdout.reconfigure(encoding="utf-8")
for f in sorted(glob.glob(r"simulation/mujoco/out/trace_v2_rest_p*.json"), key=lambda p:int(p.split("p")[-1].split(".")[0])):
    tr=json.load(open(f,encoding="utf-8"))
    peak=max(tr,key=lambda s:s["v"])
    angs=[s["ang"] for s in tr]; rs=[s["r"] for s in tr]
    entered=[s for s in tr if s["ang"]<224 and 40<=s["r"]<=75]
    exit_=[s for s in tr if s["ang"]<=143 and 40<=s["r"]<=75]
    lx=[s["lx"] for s in tr]
    print(os.path.basename(f), "n=%d"%len(tr))
    print("   start=(%.2f,%.2f) end=(%.2f,%.2f) t_end=%.2f"%(tr[0]["x"],tr[0]["z"],tr[-1]["x"],tr[-1]["z"],tr[-1]["t"]))
    print("   peak v=%.3f @t=%.2f  pos=(%.1f,%.1f)"%(peak["v"],peak["t"],peak["x"],peak["z"]))
    print("   ang range=%.1f..%.1f  r range=%.1f..%.1f"%(min(angs),max(angs),min(rs),max(rs)))
    print("   min_ang=%.2f  entered=%s  exit142=%s  max_lx=%.1f  max_z=%.1f"%(min(angs),bool(entered),bool(exit_),max(lx),max(s["z"] for s in tr)))
    # first time crossing 225
    for thr in (226,225,224,200,160,145,143):
        cs=[s for s in tr if s["ang"]<=thr]
        if cs: print("      first ang<=%d : t=%.3f pos=(%.1f,%.1f) v=%.3f r=%.1f"%(thr,cs[0]["t"],cs[0]["x"],cs[0]["z"],cs[0]["v"],cs[0]["r"]))
    print()
