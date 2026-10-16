# -*- coding: utf-8 -*-
"""Generate cad/_r62_fig.py from cad/_r61_fig.py."""
from pathlib import Path

src = Path("cad/_r61_fig.py").read_text(encoding="utf-8")
R = []


def rep(old, new, n=None):
    global src
    c = src.count(old)
    assert c >= 1, "not found: %r" % (old[:70],)
    if n is not None:
        assert c == n, "count %d != %d for %r" % (c, n, old[:70])
    src = src.replace(old, new)
    R.append("%s x%d" % (old[:40].replace("\n", " "), c))


rep('OUT = Path("cad/output/_r61_frame")\nrep = json.loads((OUT / "report_r61_pollen.json").read_text(encoding="utf-8"))',
    'OUT = Path("cad/output/_r62_frame")\nrep = json.loads((OUT / "report_r62_pollen.json").read_text(encoding="utf-8"))')
rep('''    if n.startswith("base_rail"):     return "base rail (1, JOINED L+R+4 ribs)"''',
    '''    if n.startswith("base_rail_rear"): return "base rail REAR block (1, L+R+4 ribs)"
    if n.startswith("base_rail_front"): return "base rail FRONT bar (2, H2D split)"''')
rep('''fig.suptitle("R61 print set - %d bodies, V = %.1f mm3, 3.14 MB STEP (COTS excluded, rails JOINED)"''',
    '''fig.suptitle("R62 print set - %d bodies, V = %.1f mm3 (COTS excluded, base rail cut at x=-40 into 3)"''')
rep('''dst = Path("cad/output/_r61_frame/sections/r61_print_set_45.png")''',
    '''dst = Path("cad/output/_r62_frame/sections/r62_print_set_46.png")''')

# ------------------------------------------------------- rail split detail
rep('''# ---------------------------------------------------------------- rail join detail
rail = [s for n, s in zip(names, solids) if n.startswith("base_rail")][0]
import json as _j
_rep = json.loads((OUT / "report_r61_pollen.json").read_text(encoding="utf-8"))
ribs = _rep["base_rail_r61"]["ribs"]["x_mm"]
fig2, ax2 = plt.subplots(1, 3, figsize=(22, 7.5))
_cfg = [("Top  X-Y  (ribs across the gap)", 0, 1),
        ("Front X-Z", 0, 2),
        ("Side  Y-Z", 1, 2)]
vs, ts = rail.tessellate(1.0)
P = np.array([[v.x, v.y, v.z] for v in vs])
for ax, (t, i1, i2) in zip(ax2, _cfg):
    polys = [P[np.asarray(k, dtype=int)][:, [i1, i2]] for k in ts]
    ax.add_collection(PatchCollection([MPoly(p, closed=True) for p in polys],
                                      facecolor=(0.72, 0.74, 0.78), edgecolor="none"))
    ax.autoscale_view()
    ax.set_aspect("equal")
    ax.grid(True, lw=0.3, alpha=0.4)
    ax.set_title(t, fontsize=13)
    ax.set_xlabel(["X", "X", "Y"][_cfg.index((t, i1, i2))] + " (mm)")
    ax.set_ylabel(["Y", "Z", "Z"][_cfg.index((t, i1, i2))] + " (mm)")
for x in ribs:
    for ax in ax2[:2]:
        ax.axvline(x, color="crimson", lw=1.2, ls="--", alpha=0.8)
ax2[0].set_title("Top  X-Y  (ribs across the gap) - red = rib centres at x = %s"
                 % ", ".join("%.0f" % x for x in ribs), fontsize=12)
b = rail.BoundingBox()
fig2.suptitle("R61 joined base rail: 1 solid, %.1f x %.1f x %.1f mm, V=%.1f mm3"
              % (b.xmax - b.xmin, b.ymax - b.ymin, b.zmax - b.zmin, rail.Volume()),
              fontsize=15)
fig2.tight_layout(rect=[0, 0, 1, 0.94])
dst2 = Path("cad/output/_r61_frame/sections/r61_rail_join_detail.png")
fig2.savefig(dst2, dpi=130)
print("saved", dst2, dst2.stat().st_size / 1e3, "KB")''',
    '''# -------------------------------------------------------- rail split detail
_rep = json.loads((OUT / "report_r62_pollen.json").read_text(encoding="utf-8"))
info = _rep["base_rail_r62"]
ribs = info["ribs"]["x_mm"]
xsplit = info["print_split"]["plane_x_mm"]
pieces = [(n, s) for n, s in zip(names, solids) if n.startswith("base_rail")]
_rcol = {"base_rail_rear_joined": (0.85, 0.55, 0.35),
         "base_rail_front_+72": (0.35, 0.60, 0.85),
         "base_rail_front_-72": (0.45, 0.78, 0.50)}
fig2, ax2 = plt.subplots(1, 3, figsize=(22, 7.5))
_cfg = [("Top  X-Y  (x = -40 cut plane)", 0, 1),
        ("Front X-Z  (cut plane + rib centres)", 0, 2),
        ("Side  Y-Z  (front bar section)", 1, 2)]
for ax, (t, i1, i2) in zip(ax2, _cfg):
    for n, s in pieces:
        vs, ts = s.tessellate(1.0)
        P = np.array([[v.x, v.y, v.z] for v in vs])
        polys = [P[np.asarray(k, dtype=int)][:, [i1, i2]] for k in ts]
        ax.add_collection(PatchCollection([MPoly(p, closed=True) for p in polys],
                                          facecolor=_rcol[n], edgecolor="none"))
    ax.autoscale_view()
    ax.set_aspect("equal")
    ax.grid(True, lw=0.3, alpha=0.4)
    ax.set_title(t, fontsize=13)
    ax.set_xlabel(["X", "X", "Y"][_cfg.index((t, i1, i2))] + " (mm)")
    ax.set_ylabel(["Y", "Z", "Z"][_cfg.index((t, i1, i2))] + " (mm)")
for ax in ax2[:2]:
    ax.axvline(xsplit, color="crimson", lw=1.8, ls="-", alpha=0.9)
    for x in ribs:
        ax.axvline(x, color="black", lw=0.9, ls=":", alpha=0.7)
ax2[2].axhline(0.0, color="crimson", lw=1.2, ls=":", alpha=0.9)
ax2[0].set_title("Top X-Y - red = cut plane x = %.0f, black dotted = rib centres"
                 % xsplit, fontsize=12)
_txt = "; ".join("%s %.1f x %.1f x %.1f mm  min square %.1f"
                 % (n, info["pieces"][n]["dims_mm"][0],
                    info["pieces"][n]["dims_mm"][1],
                    info["pieces"][n]["dims_mm"][2],
                    info["pieces"][n]["min_enclosing_square_mm"])
                 for n, _s in pieces)
fig2.suptitle("R62 base rail cut at x = %.0f mm, pure partition, V = %.1f mm3 "
              "(3 solids)\\n%s"
              % (xsplit, sum(s.Volume() for _n, s in pieces), _txt), fontsize=13)
fig2.tight_layout(rect=[0, 0, 1, 0.90])
dst2 = Path("cad/output/_r62_frame/sections/r62_rail_split_detail.png")
fig2.savefig(dst2, dpi=130)
print("saved", dst2, dst2.stat().st_size / 1e3, "KB")''')

Path("cad/_r62_fig.py").write_text(src, encoding="utf-8")
print("wrote cad/_r62_fig.py  (%d replacements)" % len(R))
