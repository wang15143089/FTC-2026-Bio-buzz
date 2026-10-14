import sys, itertools
sys.path.insert(0, "cad")
import cadquery as cq
import paddle_launcher_gate_drive_r48 as R

def as_solid(shp):
    if isinstance(shp, dict):
        ss = []
        for v in shp.values():
            ss += as_solid(v) if not isinstance(v, cq.Workplane) else list(v.Solids())
        return ss
    if isinstance(shp, (list, tuple)):
        ss = []
        for v in shp:
            ss += as_solid(v)
        return ss
    return list(shp.Solids())

def vol(shp):
    return sum(s.Volume() for s in as_solid(shp))

for phi in (20.0, 160.0):
    parts = {
        "blade": R.gate_blade(R.blade_centre(phi)),
        "yoke": R.gate_yoke(R.yoke_pin_z(phi)),
        "frame": R.gate_frame(),
        "bracket": R.gate_bracket(),
        "servo": R.servo(),
        "crank": R.crank(phi),
        "rod": R.connecting_rod(phi),
        "dowels": R.dowels(phi),
    }
    print("=== phi", phi, {k: round(vol(v), 1) for k, v in parts.items()})
    for k1, k2 in itertools.combinations(parts, 2):
        try:
            r = cq.Workplane("XY").newObject(as_solid(parts[k1])).intersect(cq.Workplane("XY").newObject(as_solid(parts[k2])))
            v = sum(s.Volume() for s in r.Solids())
        except Exception as e:
            v, e = -1.0, str(e)[:50]
        if v > 0.5:
            print("  HIT %-8s x %-8s = %.1f mm3" % (k1, k2, v))
print("=== balls")
for i, s in enumerate(as_solid(R.balls(4))):
    b = s.BoundingBox()
    print("  ball%d x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f vol %.0f" % (i, b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax, s.Volume()))
