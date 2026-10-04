import json,sys
sys.stdout.reconfigure(encoding="utf-8")
tr=json.load(open(r"simulation/mujoco/out/trace_v2_tray_static.json",encoding="utf-8"))
for s in tr:
    if abs(s["t"]*10-round(s["t"]*10))<0.001:
        print("t=%5.2f x=%8.2f z=%7.2f v=%.4f vx=%.4f vz=%.4f r=%7.2f ang=%7.2f"%(s["t"],s["x"],s["z"],s["v"],s["vx"],s["vz"],s["r"],s["ang"]))
