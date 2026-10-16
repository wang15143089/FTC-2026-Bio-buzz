# -*- coding: utf-8 -*-
"""R69 step 1: split the big shroud / side-plate body into 3 bolted parts, and join the
split base rail into one 380 mm body per side (option C).

IN  cad/output/_r66_parts/    (R67 delivered print set, read-only)
OUT cad/output/_r69_parts/    one STEP per printable object + parts_index.json
    cad/output/_r69_parts/fasteners.json

Split plane y = +-68 : the side plates' inner faces (MEASURED on the R62 frame).
Joint, each side: 4 x M3 hex bolt through an ear that bridges the cavity between the
shroud wall (|y| 54..57, tray band 53.5..63) and the plate inner face (|y| 68) +
hex nut + 2 washers; epoxy on every abutting face.  No zip ties: they would need
slots through the plates and add nothing to a bolted + bonded joint.
"""
import json
import math
from pathlib import Path

import cadquery as cq
import numpy as np

SRC = Path("cad/output/_r66_parts")
DEST = Path("cad/output/_r69_parts")
DEST.mkdir(parents=True, exist_ok=True)
BIG = 1500.0
Y_CUT = 68.0            # side plate inner face
Y_EAR = 67.8            # ear outer face -> 0.2 mm bond gap
D_HOLE = 3.4            # M3 clearance
Y_BITE = 3.0            # ear bite into the shroud wall
EAR_X, EAR_Z = 6.0, 5.0

# (tag, x, z, bolt) : chosen on the real solids.  A sits on the 16 mm front-lower plate
# flange, D/B/C on the plain 4 mm plate walls.
STATIONS = (
    ("A", 74.0, 27.0, "M3x35"),
    ("D", 5.0, 86.0, "M3x25"),
    ("B", -25.0, 120.0, "M3x25"),
    ("C", -68.0, 140.0, "M3x25"),
)


def box(x0, x1, y0, y1, z0, z1):
    return (cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False)
            .translate((x0, y0, z0)).val())


def cyl_y(r, y0, y1, x, z):
    return cq.Solid.makeCylinder(r, abs(y1 - y0),
                                 cq.Vector(x, min(y0, y1), z), cq.Vector(0, 1, 0))


def rep(name, shape):
    b = shape.BoundingBox()
    print("%-20s V=%11.1f solids=%d x[%7.1f,%7.1f] y[%7.1f,%7.1f] z[%7.1f,%7.1f]  dims %.1f x %.1f x %.1f"
          % (name, shape.Volume(), len(shape.Solids()), b.xmin, b.xmax, b.ymin, b.ymax,
             b.zmin, b.zmax, b.xlen, b.ylen, b.zlen), flush=True)
    return b


class Tess:
    """fast y-interval probe: which y bands are solid at a given (x, z)."""

    def __init__(self, shape, tol=0.2):
        vs, ts = shape.tessellate(tol)
        P = np.array([[v.x, v.y, v.z] for v in vs])
        F = np.array(ts)
        self.A, self.B, self.C = P[F[:, 0]], P[F[:, 1]], P[F[:, 2]]

    def yruns(self, x, z, r=0.6):
        a, b, c = self.A, self.B, self.C
        m = ((np.minimum(np.minimum(a[:, 0], b[:, 0]), c[:, 0]) <= x + r)
             & (np.maximum(np.maximum(a[:, 0], b[:, 0]), c[:, 0]) >= x - r)
             & (np.minimum(np.minimum(a[:, 2], b[:, 2]), c[:, 2]) <= z + r)
             & (np.maximum(np.maximum(a[:, 2], b[:, 2]), c[:, 2]) >= z - r))
        a, b, c = a[m], b[m], c[m]
        if len(a) == 0:
            return []
        d = (b[:, 2] - c[:, 2]) * (a[:, 0] - c[:, 0]) + (c[:, 0] - b[:, 0]) * (a[:, 2] - c[:, 2])
        ok = np.abs(d) > 1e-12
        dd = np.where(ok, d, 1.0)
        l0 = np.where(ok, ((b[:, 2] - c[:, 2]) * (x - c[:, 0]) + (c[:, 0] - b[:, 0]) * (z - c[:, 2])) / dd, -9)
        l1 = np.where(ok, ((c[:, 2] - a[:, 2]) * (x - c[:, 0]) + (a[:, 0] - c[:, 0]) * (z - c[:, 2])) / dd, -9)
        l2 = 1 - l0 - l1
        hit = ok & (l0 >= -1e-6) & (l1 >= -1e-6) & (l2 >= -1e-6)
        vals = np.sort((l0 * a[:, 1] + l1 * b[:, 1] + l2 * c[:, 1])[hit])
        u = []
        for v in vals:
            v = round(float(v), 1)
            if not u or abs(v - u[-1]) > 0.25:
                u.append(v)
        return [(u[i], u[i + 1]) for i in range(0, len(u) - 1, 2)]


# ================================================================ 1. three-way split
P1 = cq.importers.importStep(str(SRC / "frameP_1_rear_lower.step")).val()
v0 = P1.Volume()
print("frameP_1_rear_lower V=%.1f solids=%d" % (v0, len(P1.Solids())), flush=True)
mid = P1.intersect(box(-BIG, BIG, -Y_CUT, Y_CUT, -BIG, BIG))
pl_L = P1.intersect(box(-BIG, BIG, -BIG, -Y_CUT, -BIG, BIG))
pl_R = P1.intersect(box(-BIG, BIG, Y_CUT, BIG, -BIG, BIG))
delta = mid.Volume() + pl_L.Volume() + pl_R.Volume() - v0
print("split volume delta = %.3f mm3  (must be 0)" % delta, flush=True)
assert abs(delta) < 1.0, delta
rep("mid", mid); rep("plate_L", pl_L); rep("plate_R", pl_R)

# ================================================================ 2. ear stations
TM, TL, TR = Tess(mid), Tess(pl_L), Tess(pl_R)
ears = {1: [], -1: []}
ear_report = []
for tag, x, z, bolt in STATIONS:
    outer = 0.0
    for dx in (-EAR_X, 0.0, EAR_X):
        for dz in (-EAR_Z, 0.0, EAR_Z):
            for (a, b) in TM.yruns(x + dx, z + dz):
                if 52.0 <= a <= 56.0 and b > outer:
                    outer = b
    assert outer > 0.0, "no shroud wall at %s" % tag
    y_in = max(53.0, outer - Y_BITE)
    for side in (1, -1):
        T = TR if side > 0 else TL
        run = T.yruns(x, z)
        assert len(run) == 1, "station %s side %+d plate runs %s" % (tag, side, run)
        p_in, p_out = (run[0] if side > 0 else (run[0][1], run[0][0]))
        assert abs(p_in - side * Y_CUT) < 0.6, "station %s side %+d inner face %.1f" % (tag, side, p_in)
        ya, yb = sorted((side * y_in, side * Y_EAR))
        e = box(x - EAR_X, x + EAR_X, ya, yb, z - EAR_Z, z + EAR_Z)
        ov = e.intersect(mid).Volume()
        assert ov > 30.0, "ear %s%+d bites only %.1f" % (tag, side, ov)
        ears[side].append(e)
        thk = abs(p_out - p_in)
        nut_in = min([a for (a, b) in TM.yruns(x, z) if a - 0.5 <= y_in <= b + 0.5] or [y_in])
        clamp = abs(p_out - side * nut_in)
        stack = 5.0 * math.ceil((clamp + 4.0) / 5.0)
        bolt = 'M3x%d' % int(stack)
        ear_report.append({"tag": tag, "side": "R" if side > 0 else "L", "x": x, "z": z,
                           "bolt": bolt, "ear_y": [round(ya, 1), round(yb, 1)],
                           "bite_mm3": round(ov, 1), "plate_mm": thk,
                           "clamp_mm": round(clamp, 1), "bolt_len_mm": stack})
        print("  %s %s: shroud wall outer %.1f -> ear %.1f..%.1f (bite %5.1f mm3) | plate %.1f..%.1f (%.1f mm) | clamp %.1f | bolt %s"
              % (tag, "R" if side > 0 else "L", outer, ya, yb, ov, p_in, p_out, thk, clamp, bolt), flush=True)

# ================================================================ 3. union + drill holes
mid2 = mid
for e in ears[1] + ears[-1]:
    mid2 = mid2.fuse(e)
mid2 = mid2.clean()
pl_L2, pl_R2 = pl_L, pl_R
hole_v = {}
for tag, x, z, _b in STATIONS:
    v_before = (mid2.Volume(), pl_L2.Volume(), pl_R2.Volume())
    mid2 = mid2.cut(cyl_y(D_HOLE / 2, 40.0, Y_EAR + 20.0, x, z))
    mid2 = mid2.cut(cyl_y(D_HOLE / 2, -Y_EAR - 20.0, -40.0, x, z))
    pl_L2 = pl_L2.cut(cyl_y(D_HOLE / 2, -120.0, 120.0, x, z))
    pl_R2 = pl_R2.cut(cyl_y(D_HOLE / 2, -120.0, 120.0, x, z))
    hole_v[tag] = tuple(round(v_before[i] - (mid2.Volume(), pl_L2.Volume(), pl_R2.Volume())[i], 1)
                        for i in range(3))
mid2 = mid2.clean(); pl_L2 = pl_L2.clean(); pl_R2 = pl_R2.clean()
PARTS = {}
rep("shroud_tray_mid", mid2); PARTS["shroud_tray_mid"] = mid2
rep("side_plate_left", pl_L2); PARTS["side_plate_left"] = pl_L2
rep("side_plate_right", pl_R2); PARTS["side_plate_right"] = pl_R2
for n, s in PARTS.items():
    assert len(s.Solids()) == 1, "%s is not one solid" % n
print("drilled per station (mid / plate_L / plate_R):", hole_v, flush=True)
for tag, x, z, _b in STATIONS:
    plug = cyl_y(D_HOLE / 2, -120.0, 120.0, x, z)
    for nm, sh in (("mid", mid2), ("plate_L", pl_L2), ("plate_R", pl_R2)):
        rest = sh.intersect(plug).Volume()
        assert rest < 1.0, "hole %s in %s not clear (%.1f mm3 left)" % (tag, nm, rest)
print("mid gain = %.1f (ears) | plates lost = %.1f" %
      (mid2.Volume() - mid.Volume(), (pl_L.Volume() - pl_L2.Volume()) + (pl_R.Volume() - pl_R2.Volume())),
      flush=True)
for er in ear_report:
    x, z = er["x"], er["z"]
    ya, yb = er["ear_y"]
    c = box(x + 2.2, x + EAR_X - 0.3, ya + 0.3, yb - 0.3, z - EAR_Z + 0.3, z + EAR_Z - 0.3)
    fill = c.intersect(mid2).Volume() / c.Volume()
    assert fill > 0.98, "ear %s%s floating (fill %.3f)" % (er["tag"], er["side"], fill)
print("all 8 ears present and attached", flush=True)

# ================================================================ 4. rails, option C
front_R = cq.importers.importStep(str(SRC / "base_rail_front_+72.step")).val()
front_L = cq.importers.importStep(str(SRC / "base_rail_front_-72.step")).val()
rear = cq.importers.importStep(str(SRC / "base_rail_rear_joined.step")).val()
rail_R = front_R.fuse(rear.intersect(box(-BIG, BIG, 63.0, BIG, -BIG, BIG))).clean()
rail_L = front_L.fuse(rear.intersect(box(-BIG, BIG, -BIG, -63.0, -BIG, BIG))).clean()
for n, s in (("base_rail_+72", rail_R), ("base_rail_-72", rail_L)):
    rep(n, s)
    assert len(s.Solids()) == 1, "%s is not one solid" % n
    assert abs(s.BoundingBox().xlen - 380.0) < 0.05, n
PARTS["base_rail_+72"] = rail_R
PARTS["base_rail_-72"] = rail_L

# ================================================================ 5. collision check
idx = json.loads((SRC / "parts_index.json").read_text(encoding="utf-8"))
KEEP = [o for o in idx["objects"] if o["object"] not in (
    "frameP_1_rear_lower", "base_rail_front_+72", "base_rail_front_-72",
    "base_rail_rear_joined", "rail_splice_plate_+72", "rail_splice_plate_-72")]
others = []
for o in KEEP:
    others.append((o["object"], cq.importers.importStep(str(SRC / o["file"])).val()))
print("collision check against %d kept objects" % len(others), flush=True)
clash = []
for tag, x, z, bolt in STATIONS:
    for side in (1, -1):
        # full bolt corridor: through the plate, 6 mm of head/nut + washer space
        ya, yb = sorted((side * 40.0, side * 90.0))
        corridor = box(x - 5.0, x + 5.0, ya, yb, z - 5.0, z + 5.0)
        for nm, s in others:
            b = s.BoundingBox()
            if not (b.xmax > x - 5 and b.xmin < x + 5 and b.zmax > z - 5 and b.zmin < z + 5):
                continue
            v = corridor.intersect(s).Volume()
            if v > 0.5:
                clash.append((tag, side, nm, round(v, 2)))
print("bolt-corridor clashes:", clash if clash else "none", flush=True)

# ears themselves must not touch any other part
ear_clash = []
for side in (1, -1):
    for e in ears[side]:
        for nm, s in others:
            b = s.BoundingBox()
            eb = e.BoundingBox()
            if not (b.xmax > eb.xmin and b.xmin < eb.xmax and b.zmax > eb.zmin and b.zmin < eb.zmax
                    and b.ymax > eb.ymin and b.ymin < eb.ymax):
                continue
            v = e.intersect(s).Volume()
            if v > 0.5:
                ear_clash.append((nm, round(v, 2)))
print("ear clashes:", ear_clash if ear_clash else "none", flush=True)

# ================================================================ 6. write out
rows = []
for name in ("base_rail_+72", "base_rail_-72", "shroud_tray_mid", "side_plate_left", "side_plate_right"):
    s = PARTS[name]
    cq.exporters.export(cq.Workplane(obj=s), str(DEST / (name + ".step")))
    b = s.BoundingBox()
    rows.append({"object": name, "group": "r69", "file": name + ".step",
                 "source": "cad/output/_r69_build.py",
                 "volume_mm3": round(s.Volume(), 1), "solids": len(s.Solids()),
                 "bbox": {"x": [round(b.xmin, 3), round(b.xmax, 3)],
                          "y": [round(b.ymin, 3), round(b.ymax, 3)],
                          "z": [round(b.zmin, 3), round(b.zmax, 3)]},
                 "dims_mm": [round(b.xlen, 1), round(b.ylen, 1), round(b.zlen, 1)]})
for o in KEEP:
    rows.append(dict(o, group=o["group"] + "+r69"))
rows.sort(key=lambda r: r["object"])
out = {"units": "mm",
       "what": "T06 R69 printable set: 3-way split of the shroud/side-plate body (bolted) + "
               "one 380 mm base rail per side (option C); R67 objects otherwise untouched",
       "groups": {"r69": "new R69 object (split part with ear + hole, or joined full rail)",
                  "r62+r69": "unchanged R62 print part", "r65+r69": "unchanged R65 part",
                  "frame+r69": "unchanged DEC-0063 frame split lump"},
       "n_objects": len(rows), "sum_volume_mm3": round(sum(r["volume_mm3"] for r in rows), 1),
       "objects": rows}
(DEST / "parts_index.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
(DEST / "fasteners.json").write_text(json.dumps(
    {"bolt": "M3 hex head, stainless; nut = M3 hex nut; washer 2 per bolt",
     "items": ear_report,
     "note": "2 flat washers per bolt (under head and under nut); epoxy (2-part) on every abutting face; head outside the plate, hex nut inside on the shroud wall inner face"},
    ensure_ascii=False, indent=1), encoding="utf-8")
print("wrote %d objects, sum V = %.1f mm3" % (len(rows), out["sum_volume_mm3"]), flush=True)
