import sys, json
from pathlib import Path
HERE = Path("cad").resolve()
sys.path.insert(0, str(HERE))
import cadquery as cq
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

for r in ("r56", "r57", "r59", "r60"):
    p = HERE / "output" / ("_%s_frame" % r) / ("report_%s_pollen.json" % r)
    if not p.exists():
        print(r, "no report"); continue
    m = json.loads(p.read_text(encoding="utf-8"))
    fr = [e for e in m["parts"] if e["part"].startswith("shooter_frame")]
    print(r, [ (e["part"], e["volume_mm3"], e["bbox"]) for e in fr])

a = cq.importers.importStep(str(HERE/"output"/"_r59_frame"/"T06_shooter_frame_R59_pollen.step")).val()
b = cq.importers.importStep(str(HERE/"output"/"_r60_frame"/"T06_shooter_frame_R60_pollen.step")).val()
print("R59 frame V=%.1f  R60 frame V=%.1f  dV=%.1f" % (a.Volume(), b.Volume(), b.Volume()-a.Volume()))
sym = (a.cut(b)).Volume() + (b.cut(a)).Volume()
print("symmetric difference V=%.3f mm3" % sym)
ba, bb2 = a.BoundingBox(), b.BoundingBox()
print("R59 bb", [(round(v,2)) for v in (ba.xmin,ba.xmax,ba.ymin,ba.ymax,ba.zmin,ba.zmax)])
print("R60 bb", [(round(v,2)) for v in (bb2.xmin,bb2.xmax,bb2.ymin,bb2.ymax,bb2.zmin,bb2.zmax)])
