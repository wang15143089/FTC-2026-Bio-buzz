import sys
from pathlib import Path
sys.path.insert(0, str(Path("simulation/mujoco").resolve()))
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import plot_jam as J
xs, zs, om = J.trace(-95.0, 1, 120.0, ("guide_roof",), sec=1.0)
for i in range(0, len(xs), 25):
    print(i, round(xs[i],1), round(zs[i],1))
print("last", round(xs[-1],1), round(zs[-1],1))
