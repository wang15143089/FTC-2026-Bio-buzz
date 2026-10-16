# -*- coding: utf-8 -*-
import sys
from pathlib import Path
HERE = Path("cad").resolve()
sys.path.insert(0, str(HERE))
import paddle_launcher_shooter_assembly_r60 as A
parts = A.build_parts("pollen", fresh=False)
keep, vendor, gate = A.split_parts(parts)
print("total", len(parts), "keep", len(keep), "vendor", len(vendor), "gate", len(gate))
rows = []
for n, s in sorted(parts.items()):
    b = s.BoundingBox()
    rows.append((n, (b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax), s.Volume()))
for n, bb, v in rows:
    print("%-52s V=%9.1f  x[%7.2f,%7.2f] y[%7.2f,%7.2f] z[%7.2f,%7.2f]"
          % (n, v, bb[0], bb[1], bb[2], bb[3], bb[4], bb[5]))
