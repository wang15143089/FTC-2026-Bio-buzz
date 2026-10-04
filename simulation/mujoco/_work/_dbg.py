import sys, math
from pathlib import Path
sys.path.insert(0, str(Path("simulation/mujoco").resolve()))
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import plot_jam as J
for tag, pref in (("base", ()), ("open", ("guide_roof",))):
    xs, zs, om = J.trace(-95.0, 1, 120.0, pref)
    print(tag, "n=", len(xs))
    print("  first 6:", [(round(x,1), round(z,1)) for x,z in list(zip(xs,zs))[:6]])
    print("  last 4:", [(round(x,1), round(z,1)) for x,z in list(zip(xs,zs))[-4:]])
    print("  zmax at:", [(round(xs[i],1), round(zs[i],1)) for i in range(len(zs)) if zs[i] > max(zs)-1][:3])
    print("  |omega| last:", round(abs(om[-1]),3), "target", round(120*2*math.pi/60,3))
