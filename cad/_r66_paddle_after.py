"""before / after picture of paddle_rotor print pose (read-only)."""
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
from pathlib import Path

DEST = Path("cad/output/_r66_plate")


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


shape = cq.importers.importStep("cad/output/_r66_parts/paddle_rotor.step").val()
NEW = shape.rotate((0, 0, 0), (0, -1, 0), 150)


def put(ax, s, title):
    bb = s.BoundingBox()
    s = s.translate((-bb.xmin, -bb.ymin, -bb.zmin))
    bb = s.BoundingBox()
    v, t = mesh(s)
    tri = v[t]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    ln = np.linalg.norm(n, axis=1)
    ln[ln == 0] = 1.0
    n = n / ln[:, None]
    li = np.array([0.4, 0.5, 0.75])
    li = li / np.linalg.norm(li)
    sh = np.clip(np.abs(n @ li), 0.12, 1.0)
    cols = np.zeros((len(tri), 4))
    cols[:, 0] = 0.15 + 0.55 * sh
    cols[:, 1] = 0.42 + 0.35 * sh
    cols[:, 2] = 0.18 + 0.28 * sh
    cols[:, 3] = 1.0
    ax.add_collection3d(Poly3DCollection(tri, facecolors=cols, edgecolors="none"))
    R = max(bb.xlen, bb.ylen, bb.zlen) * 0.55
    ax.set_xlim(bb.xmin - 6, bb.xmin + 2 * R + 6)
    ax.set_ylim(bb.ymin - 6, bb.ymin + 2 * R + 6)
    ax.set_zlim(0, 2 * R)
    ax.set_box_aspect((1, 1, 1))
    ax.set_axis_off()
    ax.set_title(title, fontsize=10)
    ax.view_init(elev=22, azim=-60)


fig = plt.figure(figsize=(13, 5.6))
axes = [fig.add_subplot(1, 2, 1, projection="3d"), fig.add_subplot(1, 2, 2, projection="3d")]
put(axes[0], shape, "BEFORE  as-drawn = old pose\n115.5 x 96.0  bed footprint,  H 84.0 mm")
put(axes[1], NEW, "AFTER  rotor plane laid on bed\n116.0 x 96.0  bed footprint,  H 30.0 mm")
fig.suptitle("T06 paddle_rotor - print orientation (R67)", fontsize=12)
fig.tight_layout(rect=(0, 0, 1, 0.94))
fig.savefig(DEST / "paddle_before_after.png", dpi=150)
print("wrote", DEST / "paddle_before_after.png")