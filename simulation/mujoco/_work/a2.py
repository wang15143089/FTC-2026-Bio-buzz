import json, math, sys
sys.stdout.reconfigure(encoding="utf-8")
tr=json.load(open(r"simulation/mujoco/out/trace_v2_rest_p200.json",encoding="utf-8"))
print("t      x        z       v      vx     vz     r      ang     lx      lz")
for s in tr:
    if 3.15 <= s["t"] <= 3.80 and abs(s["t"]*1000 - round(s["t"]*1000))<1 :
        print("%.3f %9.2f %8.2f %7.3f %7.3f %7.3f %7.2f %7.2f %8.1f %8.1f"%(s["t"],s["x"],s["z"],s["v"],s["vx"],s["vz"],s["r"],s["ang"],s["lx"],s["lz"]))
print()
# where is max speed, and exit condition around lx=40..200
print("--- lx vs t ---")
for s in tr:
    if -30 < s["lx"] < 300:
        print("t=%.3f lx=%8.2f lz=%8.2f v=%.3f vx=%.3f vz=%.3f"%(s["t"],s["lx"],s["lz"],s["v"],s["vx"],s["vz"]))
