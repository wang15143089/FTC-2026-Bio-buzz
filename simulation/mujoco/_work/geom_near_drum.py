import sys, math, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pollen_launcher_sim as P
pc = P.PADDLE_CENTER
rows = []
for name, panel, cls in P.static_geoms():
    pieces = P.clip_drum(panel) if name.startswith(("guide_floor", "guide_roof")) else [panel]
    for k, (c, s, rot) in enumerate(pieces):
        d = math.hypot(c[0]-pc[0], c[2]-pc[2])
        half = max(s[0], s[2]) / 2
        if d - half < 75:
            rows.append((d, f"{name}_{k}", tuple(round(v,1) for v in c), tuple(round(v,1) for v in s), rot))
for d, n, c, s, rot in sorted(rows):
    print(f"d={d:6.1f}  {n:18s} pos={c} size={s} rot={rot}")
print()
print("paddle centre", pc, "hub R=18, blade R 46..58, flex 56..60, sweep", P.PADDLE_SWEEP_R)
print("ball R", P.BALL_R, "=> centre must be >= 18+35.56 = 53.6 from axis to clear hub")
