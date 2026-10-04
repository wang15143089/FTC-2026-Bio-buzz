import math, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import opt_lib as ol
import r23
pv2 = ol.pv2
pv2.paddle_parts = r23.parts_hub(12.0)
xml, ctrl = pv2.build_xml(0.0, -1, 0.0, 100.0, 60.0)
print("--- r23.parts_hub(12) ---")
for ln in xml.splitlines():
    if "paddle_" in ln and "geom" in ln:
        import re
        nm = re.search(r'name="([^"]+)"', ln).group(1)
        sz = re.search(r'size="([^"]+)"', ln).group(1)
        ps = re.search(r'pos="([^"]+)"', ln)
        s = [float(x)*1000 for x in sz.split()]
        print("%-16s MuJoCo half(mm)=%s  -> full(mm)=%s  pos=%s" % (nm, [round(x,2) for x in s], [round(2*x,2) for x in s], ps.group(1) if ps else "-"))
print("--- original pollen_v2 paddle_parts ---")
pv2.paddle_parts = ol.ORIG_PARTS
xml, ctrl = pv2.build_xml(0.0, -1, 0.0, 100.0, 60.0)
import re
for ln in xml.splitlines():
    if "paddle_" in ln and "geom" in ln:
        nm = re.search(r'name="([^"]+)"', ln).group(1)
        s = [float(x)*1000 for x in re.search(r'size="([^"]+)"', ln).group(1).split()]
        print("%-16s half(mm)=%s -> full(mm)=%s" % (nm, [round(x,2) for x in s], [round(2*x,2) for x in s]))
