"""R66 paddle_rotor orthographic views + face table (read-only)."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

import cadquery as cq
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRep import BRep_Tool
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.TopLoc import TopLoc_Location
from pathlib import Path

SRC = Path("cad/output/_r66_parts/paddle_rotor.step")
DEST = Path("cad/output/_r66_plate")


def mesh(shape, tol=0.3):
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
print("=== big planar faces: area, normal, face bbox ===")
ex = TopExp_Explorer(shape.wrapped, TopAbs_FACE)
rows = []
while ex.More():
    f = TopoDS.Face_s(ex.Current())
    ad = cq.Shape.cast(f)
    try:
        n = ad.normalAt()
        p = (n.x, n.y, n.z)
    except Exception:
        p = None
    bb = ad.BoundingBox()
    if p is not None and ad.Area() > 900:
        rows.append((ad.Area(), p, (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax)))
    ex.Next()
for a, p, b in sorted(rows, key=lambda t: -t[0]):
    print("  A=%7.1f n=(%+.2f,%+.2f,%+.2f)  X[%6.1f,%6.1f] Y[%6.1f,%6.1f] Z[%6.1f,%6.1f]" % (a, p[0], p[1], p[2], b[0], b[1], b[2], b[3], b[4], b[5]))

v, t = mesh(shape)
tri = v[t]
fig, axes = plt.subplots(1, 3, figsize=(16, 5.4))
asets = [(1, 2, "front  (look along +Y)  axes X-Z"),
         (0, 2, "side   (look along +X)  axes Y-Z"),
         (0, 1, "top    (look along -Z)  axes X-Y")]
for ax, (i, j, ttl) in zip(axes, asets):
    polys = tri[:, :, [i, j]]
    ax.add_collection(PolyCollection(polys, facecolors="#8ecf6a", edgecolors="#2e6b1e", linewidths=0.25))
    ax.autoscale()
    ax.set_aspect("equal")
    ax.grid(True, lw=0.3, alpha=0.5)
    ax.set_title(ttl, fontsize=9)
    ax.set_xlabel(["X", "Y", "X"][i])
    ax.set_ylabel(["Y", "Z", "Z"][j - 1] if j == 2 else ["Y", "Z", "Y"][j])
axes[2].plot([(v[:, 0].min() + v[:, 0].max()) / 2], [(v[:, 1].min() + v[:, 1].max()) / 2], "r+", ms=10)
fig.tight_layout()
fig.savefig(DEST / "paddle_ortho.png", dpi=150)
print("wrote", DEST / "paddle_ortho.png")