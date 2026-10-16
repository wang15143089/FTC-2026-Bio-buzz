from pathlib import Path

src = Path("cad/_mk_r60b_fig.py").read_text(encoding="utf-8")
r = []


def rep(old, new):
    global src
    c = src.count(old)
    assert c >= 1, old[:60]
    src = src.replace(old, new)
    r.append(old[:40])


rep('OUT = Path("cad/output/_r60_frame")', 'OUT = Path("cad/output/_r61_frame")')
rep('report_r60_pollen.json', 'report_r61_pollen.json')
rep('return "base rail (2)"', 'return "base rail (1, JOINED L+R+4 ribs)"')
rep('fig.suptitle("R60B print set - %d bodies, V = %.1f mm3, 3.08 MB STEP (COTS excluded)"',
    'fig.suptitle("R61 print set - %d bodies, V = %.1f mm3, 3.14 MB STEP (COTS excluded, rails JOINED)"')
rep('dst = Path("cad/output/_r60_frame/sections/r60b_print_set_45.png")',
    'dst = Path("cad/output/_r61_frame/sections/r61_print_set_45.png")')

src += '''

# ---------------------------------------------------------------- rail join detail
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
print("saved", dst2, dst2.stat().st_size / 1e3, "KB")
'''
Path("cad/_r61_fig.py").write_text(src, encoding="utf-8")
print("wrote cad/_r61_fig.py (%d reps)" % len(r))
