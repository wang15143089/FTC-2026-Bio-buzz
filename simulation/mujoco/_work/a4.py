import json,sys
sys.stdout.reconfigure(encoding="utf-8")
for tag in ("v2_xsweep_150","v2_xsweep_160"):
    tr=json.load(open(f"simulation/mujoco/out/trace_{tag}.json",encoding="utf-8"))
    print(tag,"n=",len(tr))
    for s in tr[::250]:
        print("   t=%5.2f x=%8.2f z=%7.2f v=%.4f vx=%7.4f r=%7.2f ang=%7.2f"%(s["t"],s["x"],s["z"],s["v"],s["vx"],s["r"],s["ang"]))
    print("   tail t=%5.2f x=%8.2f z=%7.2f v=%.4f r=%.2f ang=%.2f"%(tr[-1]["t"],tr[-1]["x"],tr[-1]["z"],tr[-1]["v"],tr[-1]["r"],tr[-1]["ang"]))
    xs=[abs(s["x"]-tr[-1]["x"]) for s in tr if s["t"]>5.0]
    print("   5s 后 x 波动 %.3f mm"%max(xs))
