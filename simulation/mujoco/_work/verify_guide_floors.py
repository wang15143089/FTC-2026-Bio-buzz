import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(r"C:\Users\admin\OneDrive\文档\ChatGPT\FTC 2026 biobuzz\cad")))
import paddle_launcher_constrained as pl
print("paddle centre", pl.PADDLE_CENTER, "sweep R", pl.PADDLE_SWEEP_R, "clear H", pl.CHANNEL_CLEAR_H)
for i, (s, e, L, ang) in enumerate(pl.GUIDES, 1):
    for kind in ("floor", "roof"):
        sh = pl.panel_on_segment(s, e, ang, kind)
        v = sh.Volume() if sh is not None else 0.0
        bb = sh.BoundingBox() if sh is not None else None
        print(f"guide_{kind}_{i}  seg={ang:4.0f}deg  vol={v/1000:9.3f} cm3  "
              f"bbox_x=({bb.xmin:.1f},{bb.xmax:.1f}) bbox_z=({bb.zmin:.1f},{bb.zmax:.1f})"
              if bb else f"guide_{kind}_{i} EMPTY")
