import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pollen_launcher_sim as P
names = [n for n,_,_ in P.static_geoms()]
print("guide_floor_3 pieces in model:", sum(1 for n in names if n.startswith("guide_floor_3")))
print("guide_floor_2 pieces:", sum(1 for n in names if n.startswith("guide_floor_2")))
print("guide_floor_1 pieces:", sum(1 for n in names if n.startswith("guide_floor_1")))
print("guide_roof_3 pieces:", sum(1 for n in names if n.startswith("guide_roof_3")))
print("guide_roof_2 pieces:", sum(1 for n in names if n.startswith("guide_roof_2")))
print("all guide_* names:")
for n,_,_ in P.static_geoms():
    if n.startswith("guide_"):
        print("   ", n, "->", len(P.clip_drum(_) if False else [0]) if False else "")
