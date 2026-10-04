import json,math,sys
sys.stdout.reconfigure(encoding="utf-8")
tr=json.load(open(r"simulation/mujoco/out/trace_v2_tray_p200.json",encoding="utf-8"))
seg=[s for s in tr if -185<=s["lx"]<=40]
print("通道段：lx %.1f -> %.1f   lz %.1f -> %.1f   v %.3f -> %.3f"%(seg[0]["lx"],seg[-1]["lx"],seg[0]["lz"],seg[-1]["lz"],seg[0]["v"],seg[-1]["v"]))
print("lz 范围 %.1f .. %.1f  (喉道法向 +55 在 lz=55)"%(min(s["lz"] for s in seg),max(s["lz"] for s in seg)))
for s in seg[::20]: print("   t=%.3f lx=%8.2f lz=%7.2f v=%.3f"%(s["t"],s["lx"],s["lz"],s["v"]))
print()
# release point: first sample with lx>-180
r=seg[0]; print("释放点: t=%.3f 世界(%.2f,%.2f) lx=%.2f lz=%.2f r=%.2f ang=%.2f v=%.3f"%(r["t"],r["x"],r["z"],r["lx"],r["lz"],r["r"],r["ang"],r["v"]))
# nip: lx crosses 0
for a,b in zip(seg,seg[1:]):
    if a["lx"]<0<=b["lx"]:
        print("进夹口: t=%.3f lx=%7.2f lz=%7.2f v=%.3f"%(a["t"],a["lx"],a["lz"],a["v"])); break
print("夹口最大速度 %.3f m/s @t=%.3f lx=%.1f"%(max(s["v"] for s in tr),max(tr,key=lambda s:s["v"])["t"],max(tr,key=lambda s:s["v"])["lx"]))
print("轮缘线速度(1620rpm, R48) = %.3f m/s ; 比值 %.3f"%(1620/60*2*math.pi*0.048, max(s["v"] for s in tr)/(1620/60*2*math.pi*0.048)))
