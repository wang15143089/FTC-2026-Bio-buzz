# -*- coding: utf-8 -*-
"""R63: pack the 45 non-frame printed parts of R62 onto ONE Bambu H2D plate.

READ-ONLY on delivered geometry: reads cad/output/_r62b_parts/*.step (themselves
read back from T06_print_set_R62_pollen.step). Each part keeps its ORIGINAL
orientation (pure XY translation, no rotation), min-Z resting on the bed.

Packing: MaxRects / best-short-side-fit with a gap inflation, no rotation.

Outputs -> cad/output/_r63_plate/
  T06_print_plate_R63_pollen.step   one body per part, already positioned
  packing_index.json
  plate_preview.png
"""
import json
from pathlib import Path
import cadquery as cq

PARTS = Path("cad/output/_r62b_parts")
DEST = Path("cad/output/_r63_plate")
DEST.mkdir(parents=True, exist_ok=True)

BED_X, BED_Y, BED_Z = 325.0, 320.0, 325.0          # Bambu Lab H2D
MARGIN = 5.0
GAP = 4.0
EXCLUDE_PREFIX = "shooter_frame"                    # split separately (DEC-0063)

idx = json.loads((PARTS / "parts_index.json").read_text(encoding="utf-8"))
items = []
for it in idx["parts"]:
    n = it["part"]
    if n.startswith(EXCLUDE_PREFIX):
        continue
    b = it["bbox"]
    items.append({"part": n, "file": it["file"], "vol": it["volume_mm3"],
                  "dx": b["x"][1] - b["x"][0], "dy": b["y"][1] - b["y"][0],
                  "dz": b["z"][1] - b["z"][0]})
W, H = BED_X - 2 * MARGIN, BED_Y - 2 * MARGIN


def maxrects(rects, W, H, gap):
    free = [(0.0, 0.0, W, H)]
    placed = []
    for r in sorted(rects, key=lambda e: (-e["dx"] * e["dy"], -e["dy"])):
        w, h = r["dx"] + gap, r["dy"] + gap          # inflate: enforces >= gap
        best = None
        for (fx, fy, fw, fh) in free:
            if fw + 1e-9 >= w and fh + 1e-9 >= h:
                lw, lh = fw - w, fh - h
                key = (min(lw, lh), max(lw, lh), fy, fx)
                if best is None or key < best[0]:
                    best = (key, fx, fy)
        if best is None:
            return None
        _, px, py = best
        placed.append((r, px, py))
        nxt = []
        for (fx, fy, fw, fh) in free:
            if px >= fx + fw or px + w <= fx or py >= fy + fh or py + h <= fy:
                nxt.append((fx, fy, fw, fh))
                continue
            if px > fx:
                nxt.append((fx, fy, px - fx, fh))
            if px + w < fx + fw:
                nxt.append((px + w, fy, fx + fw - (px + w), fh))
            if py > fy:
                nxt.append((fx, fy, fw, py - fy))
            if py + h < fy + fh:
                nxt.append((fx, py + h, fw, fy + fh - (py + h)))
        free = [a for i, a in enumerate(nxt)
                if not any(j != i and b[0] <= a[0] + 1e-9 and b[1] <= a[1] + 1e-9
                           and b[0] + b[2] >= a[0] + a[2] - 1e-9
                           and b[1] + b[3] >= a[1] + a[3] - 1e-9
                           for j, b in enumerate(nxt))]
    return placed


packed = maxrects(items, W, H, GAP)
assert packed is not None, "does not fit on one plate"

# no-overlap check on the real footprints (+gap)
for i, (a, ax, ay) in enumerate(packed):
    for (b, bx, by) in packed[i + 1:]:
        if not (ax + a["dx"] + GAP - 1e-6 <= bx or bx + b["dx"] + GAP - 1e-6 <= ax
                or ay + a["dy"] + GAP - 1e-6 <= by or by + b["dy"] + GAP - 1e-6 <= ay):
            raise AssertionError("overlap %s / %s" % (a["part"], b["part"]))

max_x = max(px + r["dx"] for r, px, py in packed)
max_y = max(py + r["dy"] for r, px, py in packed)
area = sum(r["dx"] * r["dy"] for r, _, _ in packed)
print("packed %d parts | extent %.1f x %.1f mm of %.1f x %.1f usable | bbox fill %.0f%%"
      % (len(packed), max_x, max_y, W, H, 100.0 * area / (max_x * max_y)))

# ---- build plate assembly
assy = cq.Assembly(name="T06_print_plate_R63_pollen")
palette = [(0.85, 0.35, 0.30), (0.30, 0.60, 0.85), (0.45, 0.75, 0.40),
           (0.90, 0.70, 0.25), (0.65, 0.45, 0.80), (0.35, 0.75, 0.75)]
placed = []
for i, (r, px, py) in enumerate(sorted(packed, key=lambda e: e[0]["part"])):
    s = cq.importers.importStep(str(PARTS / r["file"])).val()
    bb = s.BoundingBox()
    tv = (MARGIN + px - bb.xmin, MARGIN + py - bb.ymin, -bb.zmin)
    s = s.translate(tv)
    c = palette[i % len(palette)]
    assy.add(s, name=r["part"], color=cq.Color(c[0], c[1], c[2], 1.0))
    placed.append({"part": r["part"], "volume_mm3": r["vol"],
                   "plate_xy_mm": [round(MARGIN + px, 2), round(MARGIN + py, 2)],
                   "translate_mm": [round(v, 3) for v in tv],
                   "footprint_mm": [round(r["dx"], 1), round(r["dy"], 1)],
                   "height_mm": round(r["dz"], 1)})

out = DEST / "T06_print_plate_R63_pollen.step"
assy.export(str(out), exportType="STEP")
print("wrote %s (%.2f MB)" % (out, out.stat().st_size / 1e6))

# ---- readback verification
sol = list(cq.importers.importStep(str(out)).val().Solids())
sbb = cq.importers.importStep(str(out)).val().BoundingBox()
vol = sum(s.Volume() for s in sol)
want = sum(r["volume_mm3"] for r in placed)
ok_n = len(sol) == len(placed)
ok_v = abs(vol - want) < 1.0
ok_b = (sbb.xlen <= BED_X + 1e-6 and sbb.ylen <= BED_Y + 1e-6
        and sbb.zlen <= BED_Z + 1e-6 and abs(sbb.zmin) < 1e-6)
print("readback: %d solids (want %d) -> %s" % (len(sol), len(placed), "OK" if ok_n else "FAIL"))
print("readback: V=%.1f / want %.1f (d=%.2f) -> %s" % (vol, want, vol - want, "OK" if ok_v else "FAIL"))
print("readback: bbox %.1f x %.1f x %.1f, zmin=%.3f -> %s"
      % (sbb.xlen, sbb.ylen, sbb.zlen, sbb.zmin, "OK" if ok_b else "FAIL"))

(DEST / "packing_index.json").write_text(json.dumps({
    "units": "mm",
    "source": "cad/output/_r62b_parts/parts_index.json (R62 print set)",
    "excluded": ["shooter_frame_R62_merged: exceeds 325 mm bed, split by DEC-0063"],
    "bed_mm": [BED_X, BED_Y, BED_Z], "bed": "Bambu Lab H2D",
    "margin_mm": MARGIN, "gap_mm": GAP,
    "orientation": "unchanged (pure XY translation, no rotation)",
    "algorithm": "MaxRects best-short-side-fit, no rotation",
    "n_parts": len(placed), "sum_volume_mm3": round(vol, 1),
    "used_extent_mm": [round(max_x, 1), round(max_y, 1)],
    "readback": {"solids": len(sol), "solids_ok": ok_n, "volume_ok": ok_v, "bbox_ok": ok_b,
                 "bbox_mm": [round(sbb.xlen, 2), round(sbb.ylen, 2), round(sbb.zlen, 2)]},
    "parts": sorted(placed, key=lambda e: e["part"])}, ensure_ascii=False, indent=1),
    encoding="utf-8")

# ---- 2D preview
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
fig, ax = plt.subplots(figsize=(11, 10.8))
ax.add_patch(Rectangle((0, 0), BED_X, BED_Y, fill=False, ec="k", lw=2))
ax.add_patch(Rectangle((MARGIN, MARGIN), W, H, fill=False, ec="0.6", ls="--", lw=1))
for i, (r, px, py) in enumerate(sorted(packed, key=lambda e: e[0]["part"])):
    c = palette[i % len(palette)]
    ax.add_patch(Rectangle((MARGIN + px, MARGIN + py), r["dx"], r["dy"],
                           fc=c, ec="k", lw=0.6, alpha=0.75))
    if r["dx"] * r["dy"] > 1400:
        lab = r["part"].replace("carriage_clamp_seat_", "clamp_").replace("motor_bridge_", "bridge_")
        ax.text(MARGIN + px + r["dx"] / 2, MARGIN + py + r["dy"] / 2,
                lab.replace("_", "\n"), ha="center", va="center", fontsize=5.5)
ax.set_xlim(-12, BED_X + 12); ax.set_ylim(-12, BED_Y + 12)
ax.set_aspect("equal"); ax.invert_yaxis()
ax.set_title("R63 plate = 45 small parts on one Bambu H2D bed (325 x 320 mm)\n"
             "MaxRects, gap %.0f mm, margin %.0f mm, orientation unchanged; "
             "used %.1f x %.1f mm" % (GAP, MARGIN, max_x, max_y), fontsize=10)
ax.set_xlabel("X [mm]"); ax.set_ylabel("Y [mm]")
fig.tight_layout(); fig.savefig(DEST / "plate_preview.png", dpi=170)
print("wrote", DEST / "plate_preview.png")
