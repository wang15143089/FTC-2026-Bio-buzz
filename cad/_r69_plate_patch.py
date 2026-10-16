# -*- coding: utf-8 -*-
"""one-shot patch for cad/_r69_plate.py: (1) parts longer than the bed may lie diagonally,
(2) the print must also fit under the nozzle (H <= 325), (3) reuse R66 STEPs for the
carried-over objects."""
from pathlib import Path
p = Path("cad/_r69_plate.py")
s = p.read_text(encoding="utf-8")

old1 = """    cands += normal_candidates(shape)
    best = None
    for s, bb, tag, meta in cands:
        fits = bb.xlen <= W + 1e-6 and bb.ylen <= H + 1e-6
        key = (0 if fits else 1, round(bb.zlen, 2), -round(bb.xlen * bb.ylen, 1),
               0 if tag == "axis" else 1, str(meta))
        if best is None or key < best[0]:
            best = (key, meta, s, bb, tag)
    return best
"""
new1 = """    cands += normal_candidates(shape)

    def best_of(cs):
        b = None
        for s, bb, tag, meta in cs:
            fits = (bb.xlen <= W + 1e-6 and bb.ylen <= H + 1e-6 and bb.zlen <= BED_Z + 1e-6)
            key = (0 if fits else 1, round(bb.zlen, 2), -round(bb.xlen * bb.ylen, 1),
                   0 if tag == "axis" else 1, str(meta))
            if b is None or key < b[0]:
                b = (key, meta, s, bb, tag)
        return b

    best = best_of(cands)
    if best[0][0] != 0:
        extra = []
        for s, bb, tag, meta in cands:
            for ang in (30, 35, 40, 45, 50, 55, 60):
                s2 = s.rotate((0, 0, 0), (0, 0, 1), ang)
                m2 = dict(meta)
                m2["in_plane_deg"] = ang
                extra.append((s2, s2.BoundingBox(), tag, m2))
        b2 = best_of(extra)
        if b2[0] < best[0]:
            best = b2
    return best
"""
assert old1 in s
s = s.replace(old1, new1)

old2 = """    raw = cq.importers.importStep(str(SRC / o["file"])).val()"""
new2 = """    f = SRC / o["file"]
    if not f.exists():
        f = R66 / o["file"]
    raw = cq.importers.importStep(str(f)).val()"""
assert old2 in s
s = s.replace(old2, new2)

old3 = """DEST = Path("cad/output/_r69_plate")"""
new3 = """DEST = Path("cad/output/_r69_plate")
R66 = Path("cad/output/_r66_parts")"""
assert old3 in s
s = s.replace(old3, new3)

old4 = """    if tag == "axis":
        note = "X%+d Y%+d Z%+d" % tuple(meta["angles_deg_XYZ"])
    else:
        note = "face %s -> bed | axis %s %+.1f deg" % (
            meta["face_normal"], meta["rot_axis"], meta["rot_deg"])"""
new4 = """    if tag == "axis":
        note = "X%+d Y%+d Z%+d" % tuple(meta["angles_deg_XYZ"])
    else:
        note = "face %s -> bed | axis %s %+.1f deg" % (
            meta["face_normal"], meta["rot_axis"], meta["rot_deg"])
    if "in_plane_deg" in meta:
        note += " | in-plane %d deg" % meta["in_plane_deg"]"""
assert old4 in s
s = s.replace(old4, new4)
p.write_text(s, encoding="utf-8")
print("patched")
