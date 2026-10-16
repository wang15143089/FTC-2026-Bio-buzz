"""R66 paddle_rotor print-orientation study (read-only)."""
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

import cadquery as cq
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRep import BRep_Tool
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.TopLoc import TopLoc_Location

SRC = Path("cad/output/_r66_parts/paddle_rotor.step")
DEST = Path("cad/output/_r66_plate")
DEST.mkdir(parents=True, exist_ok=True)


def posed(shape, a, b, c):
    s = shape
    if a:
        s = s.rotate((0, 0, 0), (1, 0, 0), a)
    if b:
        s = s.rotate((0, 0, 0), (0, 1, 0), b)
    if c:
        s = s.rotate((0, 0, 0), (0, 0, 1), c)
    return s


def face_report(shape):
    """list of (area, normal, is_planar) for every face."""
    out = []
    ex = TopExp_Explorer(shape.wrapped, TopAbs_FACE)
    while ex.More():
        f = TopoDS.Face_s(ex.Current())
        ad = cq.Shape.cast(f)
        try:
            n = ad.normalAt()
            p = (n.x, n.y, n.z)
        except Exception:
            p = None
        out.append((ad.Area(), p))
        ex.Next()
    return out


def mesh(shape, tol=0.35):
    BRepMesh_IncrementalMesh(shape.wrapped, tol, False, 0.7, True)
    verts, tris = [], []
    ex = TopExp_Explorer(shape.wrapped, TopAbs_FACE)
    while ex.More():
        f = TopoDS.Face_s(ex.Current())
        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(f, loc)
        if tri is not None:
            trsf = loc.Transformation()
            off = len(verts)
            for i in range(1, tri.NbNodes() + 1):
                p = tri.Node(i).Transformed(trsf)
                verts.append((p.X(), p.Y(), p.Z()))
            for i in range(1, tri.NbTriangles() + 1):
                t = tri.Triangle(i)
                tris.append((off + t.Value(1) - 1, off + t.Value(2) - 1, off + t.Value(3) - 1))
        ex.Next()
    return np.array(verts), np.array(tris)


shape = cq.importers.importStep(str(SRC)).val()
print("as-drawn dims:", [round(v, 2) for v in (shape.BoundingBox().xlen, shape.BoundingBox().ylen, shape.BoundingBox().zlen)])

fr = face_report(shape)
print("n_faces", len(fr), "total_area", round(sum(a for a, _ in fr), 1))
big = sorted([(a, p) for a, p in fr if p is not None], key=lambda t: -t[0])[:8]
for a, p in big:
    print("  planar area %8.2f  normal (%+.3f, %+.3f, %+.3f)" % (a, p[0], p[1], p[2]))

ANGLES = (0, 90, 180, 270)
rows = []
for a in ANGLES:
    for b in ANGLES:
        for c in ANGLES:
            s = posed(shape, a, b, c)
            bb = s.BoundingBox()
            down = 0.0
            for fa, p in face_report(s):
                if p is not None and p[2] < -0.999:
                    down += fa
            rows.append(dict(ang=(a, b, c), dims=[round(bb.xlen, 2), round(bb.ylen, 2), round(bb.zlen, 2)],
                             height=round(bb.zlen, 2), down_area=round(down, 1)))
uniq = {}
for r in rows:
    k = tuple(r["dims"])
    if k not in uniq or r["ang"] < uniq[k]["ang"]:
        uniq[k] = r
cand = sorted(uniq.values(), key=lambda r: (-r["down_area"], r["height"]))
print("--- unique orientations (24) sorted by bed-contact area ---")
for r in cand:
    print("  ang=%s  footprint=%s x %s  height=%6.2f  contact_area=%9.1f" % (r["ang"], r["dims"][0], r["dims"][1], r["height"], r["down_area"]))
json.dump(cand, open(DEST / "paddle_orient_study.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def draw(ax, s, title):
    v, t = mesh(s)
    bb = s.BoundingBox()
    tri = v[t]
    c = tri.mean(axis=1)
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    ln = np.linalg.norm(n, axis=1)
    ln[ln == 0] = 1.0
    n = n / ln[:, None]
    li = np.array([0.4, 0.5, 0.75])
    li = li / np.linalg.norm(li)
    sh = np.clip(np.abs(n @ li), 0.15, 1.0)
    cols = np.zeros((len(tri), 4))
    cols[:, 0] = 0.16 + 0.55 * sh
    cols[:, 1] = 0.45 + 0.35 * sh
    cols[:, 2] = 0.20 + 0.25 * sh
    cols[:, 3] = 1.0
    order = np.argsort(c[:, 0] + c[:, 1] - c[:, 2])
    ax.add_collection3d(Poly3DCollection(tri[order], facecolors=cols[order], edgecolors="none"))
    cx, cy = (bb.xmin + bb.xmax) / 2, (bb.ymin + bb.ymax) / 2
    r = max(bb.xlen, bb.ylen, bb.zlen) * 0.62
    ax.set_xlim(cx - r, cx + r)
    ax.set_ylim(cy - r, cy + r)
    ax.set_zlim(max(bb.zmin, -1), r * 1.6)
    ax.set_box_aspect((1, 1, 1))
    ax.set_axis_off()
    ax.set_title(title, fontsize=9)
    ax.view_init(elev=26, azim=-52)


def pick(key):
    return sorted(uniq.values(), key=key)[0]

A_now = pick(lambda r: (r["height"], -r["dims"][0] * r["dims"][1]))
A_flat = cand[0]
A_min = A_now
picks = [("current rule: min height", A_now), ("max bed-contact (FLAT)", A_flat)]
extra = [r for r in cand if r["ang"] not in (A_now["ang"], A_flat["ang"])][:2]
picks += [("alt %s" % (r["ang"],), r) for r in extra]
fig = plt.figure(figsize=(15, 4.2))
for i, (lab, r) in enumerate(picks, 1):
    ax = fig.add_subplot(1, len(picks), i, projection="3d")
    s = posed(shape, *r["ang"])
    draw(ax, s, "%s\nfootprint %s x %s  H=%s\ncontact %s mm2" % (lab, r["dims"][0], r["dims"][1], r["height"], r["down_area"]))
fig.tight_layout()
fig.savefig(DEST / "paddle_orient_study.png", dpi=150)
print("wrote", DEST / "paddle_orient_study.png")