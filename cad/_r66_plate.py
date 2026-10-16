# -*- coding: utf-8 -*-
"""R66 step 2: lay every printable object FLAT and pack the prints onto as many Bambu H2D
plates as it takes. Several print runs are explicitly acceptable, so the packer is
deliberately NOT tuned for maximum density: a plate is closed as soon as the next part no
longer fits comfortably.

Orientation rule (simple, mechanical, checked on the real solid):
  among the 64 poses reachable by 0/90/180/270 deg turns about X, Y and Z that still fit
  the usable bed, pick the SMALLEST height (i.e. the largest face on the bed); tie-break by
  the larger bed footprint, then by the fewest 90 deg turns away from the as-modeled pose.

READ-ONLY on delivered geometry: reads cad/output/_r66_parts/*.step + parts_index.json.

Writes -> cad/output/_r66_plate/
  T06_print_plate_R66_pollen_p<N>.step   one body per part, already oriented + positioned
  plate_p<N>_preview.png                 top view footprint plot of that plate
  r66_plates_overview.png                all plates in one figure
  plates_index.json                      every part's pose, placement and readback numbers
"""
import json
import random
from pathlib import Path

import cadquery as cq

SRC = Path("cad/output/_r66_parts")
DEST = Path("cad/output/_r66_plate")
DEST.mkdir(parents=True, exist_ok=True)

# a previous run may have needed more plates: drop its stale plate files first, so the
# folder always matches this run
for stale in (list(DEST.glob("T06_print_plate_R66_pollen_p*.step"))
              + list(DEST.glob("plate_p*_preview.png"))):
    stale.unlink()

BED_X, BED_Y, BED_Z = 325.0, 320.0, 325.0          # Bambu Lab H2D, single nozzle
MARGIN = 5.0
GAP = 3.0
ANGLES = (0, 90, 180, 270)
W, H = BED_X - 2 * MARGIN, BED_Y - 2 * MARGIN       # usable bed


def posed(shape, a, b, c):
    """the solid turned a deg about X, then b deg about Y, then c deg about Z."""
    s = shape
    if a:
        s = s.rotate((0, 0, 0), (1, 0, 0), a)
    if b:
        s = s.rotate((0, 0, 0), (0, 1, 0), b)
    if c:
        s = s.rotate((0, 0, 0), (0, 0, 1), c)
    return s


def choose_pose(shape):
    best = None
    for a in ANGLES:
        for b in ANGLES:
            for c in ANGLES:
                s = posed(shape, a, b, c)
                bb = s.BoundingBox()
                fits = bb.xlen <= W + 1e-6 and bb.ylen <= H + 1e-6
                key = (0 if fits else 1, round(bb.zlen, 2),
                       -round(bb.xlen * bb.ylen, 1), (a + b + c) // 90, a, b, c)
                if best is None or key < best[0]:
                    best = (key, (a, b, c), s, bb)
    return best


def sort_by_area(e):
    return (-e["area"], -max(e["dx"], e["dy"]))


def maxrects_plate(rects, W, H, gap, keyf=sort_by_area):
    """Pack as many of `rects` as will fit on ONE plate and return them placed.

    MaxRects with the best-area-fit rule. Each part may also be turned 90 deg in the plate
    plane (printing is in-plane rotation invariant, and it packs far better).
    Returns (placed, skipped); placed entries are (rect, px, py, swapped).
    """
    free = [(0.0, 0.0, W, H)]
    placed = []
    skipped = []
    for r in sorted(rects, key=keyf):
        opts = [(r["dx"], r["dy"], False)]
        if abs(r["dx"] - r["dy"]) > 1e-6:
            opts.append((r["dy"], r["dx"], True))
        best = None
        for (w0, h0, sw) in opts:
            w, h = w0 + gap, h0 + gap
            for (fx, fy, fw, fh) in free:
                if fw + 1e-9 >= w and fh + 1e-9 >= h:
                    key = (round(fw * fh - w * h, 3), round(min(fw - w, fh - h), 3), fy, fx)
                    if best is None or key < best[0]:
                        best = (key, fx, fy, w, h, sw)
        if best is None:
            skipped.append(r)
            continue
        _, px, py, w, h, sw = best
        placed.append((r, px, py, sw))
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
    return placed, skipped


def repair(plates, W, H, gap, keyf=sort_by_area):
    """Drop a near-empty plate by moving its parts into earlier plates when they still fit."""
    i = len(plates) - 1
    while i >= 1:
        cur = [list(p) for p in plates]
        ok_all = True
        for (r, _px, _py, _sw) in sorted(plates[i], key=lambda e: -e[0]["area"]):
            moved = False
            for j in range(i):
                placed, skipped = maxrects_plate([x[0] for x in cur[j]] + [r], W, H, gap, keyf)
                if not skipped:
                    cur[j] = sorted(placed, key=lambda e: e[0]["object"])
                    moved = True
                    break
            if not moved:
                ok_all = False
                break
        if ok_all:
            del cur[i]
            plates = cur
        i -= 1
    return plates


def greedy_layout(rects, W, H, gap, keyf=sort_by_area):
    """plate by plate, as many parts per plate as fit."""
    plates = []
    remaining = list(rects)
    while remaining:
        placed, skipped = maxrects_plate(remaining, W, H, gap, keyf)
        assert placed, "nothing fits an empty plate: %s" % [r["object"] for r in remaining]
        plates.append(sorted(placed, key=lambda e: e[0]["object"]))
        remaining = skipped
    return repair(plates, W, H, gap, keyf)


idx = json.loads((SRC / "parts_index.json").read_text(encoding="utf-8"))

work = []
for o in idx["objects"]:
    raw = cq.importers.importStep(str(SRC / o["file"])).val()
    key, (a, b, c), s, bb = choose_pose(raw)
    work.append({"object": o["object"], "group": o["group"], "file": o["file"],
                 "shape": s, "angles": [a, b, c],
                 "dx": bb.xlen, "dy": bb.ylen, "dz": bb.zlen,
                 "vol": o["volume_mm3"], "as_drawn_dims": o["dims_mm"],
                 "area": bb.xlen * bb.ylen,
                 "fits": key[0] == 0})
    print("%-46s as-drawn %6.1f x %6.1f x %6.1f -> flat %6.1f x %6.1f x H %5.1f "
          "(X%+d Y%+d Z%+d)%s"
          % (o["object"], o["dims_mm"][0], o["dims_mm"][1], o["dims_mm"][2],
             bb.xlen, bb.ylen, bb.zlen, a, b, c, "" if key[0] == 0 else "  !! DOES NOT FIT"),
          flush=True)

def rect_dims(r, sw):
    return (r["dy"], r["dx"]) if sw else (r["dx"], r["dy"])


def plate_extent(packed):
    mx = max(px + rect_dims(r, sw)[0] for r, px, py, sw in packed)
    my = max(py + rect_dims(r, sw)[1] for r, px, py, sw in packed)
    return (mx, my)


# ---- one plate at a time: try a few orderings, keep the best -----------------
N_SEEDS = 160


def jitter_key(seed):
    """A deterministic perturbation of the packer's own area sort key.

    MaxRects is order sensitive, so a multi-start search over that order is the cheap way
    to shave a plate off. The seed list is fixed, so the chosen layout is reproducible.
    """
    rnd = random.Random(seed)
    w = [0.55 + 0.9 * rnd.random() for _ in range(512)]
    return lambda e: (-(e["area"] ** (0.55 + 0.9 * w[int(e["area"]) % 512])),)


def layout_score(pl):
    """fewest plates first, then fewest near-empty plates (a whole print run for 1-4 parts
    is wasteful); the seed is the final tie-break so the result stays reproducible."""
    return (len(pl), sum(1 for p in pl if len(p) < 5))


best = None
for seed in range(N_SEEDS):
    keyf = sort_by_area if seed == 0 else jitter_key(seed)
    pl = greedy_layout(work, W, H, GAP, keyf)
    sc = layout_score(pl) + (seed,)
    if best is None or sc < best[0]:
        best = (sc, pl, seed)
    if seed < 3 or seed % 40 == 0:
        print("  trial seed %3d -> %d plates %s" % (seed, len(pl), [len(p) for p in pl]),
              flush=True)

plates = best[1]
packed_seed = best[2]
print("layout chosen: seed %d -> %d plates %s"
      % (packed_seed, len(plates), [len(p) for p in plates]), flush=True)

# ---- export, verify, plot ---------------------------------------------------
report = {"units": "mm", "what": "every printable object of the T06 launcher, laid flat",
          "source": "cad/output/_r66_parts", "bed": "Bambu Lab H2D, single nozzle",
          "bed_mm": [BED_X, BED_Y, BED_Z], "margin_mm": MARGIN, "gap_mm": GAP,
          "orientation_rule": "smallest height among bed-fitting 90 deg poses (largest face "
                              "down); tie-break larger footprint, then fewest 90 deg turns",
          "algorithm": "MaxRects best-area-fit with in-plane 90 deg turns, then a "
                       "deterministic %d-seed multi-start over the packer sort key, then a "
                       "plate-merge repair pass" % N_SEEDS,
          "packing_seed": packed_seed,
          "n_objects": len(work), "n_plates": len(plates), "plates": []}

PALETTE = [(0.85, 0.35, 0.30), (0.30, 0.60, 0.85), (0.45, 0.75, 0.40),
           (0.90, 0.70, 0.25), (0.65, 0.45, 0.80), (0.35, 0.75, 0.75)]

for pi, packed in enumerate(plates, start=1):
    assy = cq.Assembly(name="T06_print_plate_R66_pollen_p%d" % pi)
    rows = []
    for i, (r, px, py, sw) in enumerate(packed):
        s = r["shape"] if not sw else r["shape"].rotate((0, 0, 0), (0, 0, 1), 90)
        bb = s.BoundingBox()
        tv = (MARGIN + px - bb.xmin, MARGIN + py - bb.ymin, -bb.zmin)
        s = s.translate(tv)
        col = PALETTE[i % len(PALETTE)]
        assy.add(s, name=r["object"], color=cq.Color(col[0], col[1], col[2], 1.0))
        fdx, fdy = rect_dims(r, sw)
        rows.append({"object": r["object"], "group": r["group"],
                     "volume_mm3": r["vol"],
                     "angles_deg_XYZ": [r["angles"][0], r["angles"][1],
                                        (r["angles"][2] + 90) % 360 if sw else r["angles"][2]],
                     "in_plane_90_deg_turn": sw,
                     "as_drawn_dims_mm": r["as_drawn_dims"],
                     "footprint_mm": [round(fdx, 1), round(fdy, 1)],
                     "height_mm": round(r["dz"], 1),
                     "bed_xy_mm": [round(MARGIN + px, 2), round(MARGIN + py, 2)],
                     "translate_mm": [round(v, 3) for v in tv]})
    out = DEST / ("T06_print_plate_R66_pollen_p%d.step" % pi)
    assy.export(str(out), exportType="STEP")

    # no-overlap check on the placed footprints (+ gap)
    for i, (a, ax, ay, asw) in enumerate(packed):
        for (b, bx, by, bsw) in packed[i + 1:]:
            adx, ady = rect_dims(a, asw)
            bdx, bdy = rect_dims(b, bsw)
            if not (ax + adx + GAP - 1e-6 <= bx or bx + bdx + GAP - 1e-6 <= ax
                    or ay + ady + GAP - 1e-6 <= by or by + bdy + GAP - 1e-6 <= ay):
                raise AssertionError("overlap %s / %s" % (a["object"], b["object"]))

    sol = list(cq.importers.importStep(str(out)).val().Solids())
    sbb = cq.importers.importStep(str(out)).val().BoundingBox()
    vol = sum(s.Volume() for s in sol)
    want = sum(r["volume_mm3"] for r in rows)
    mx, my = plate_extent(packed)
    area = sum(rect_dims(r, sw)[0] * rect_dims(r, sw)[1] for r, _, _, sw in packed)
    max_h = max(r["dz"] for r, _, _, _ in packed)
    print("p%d: %2d parts | solids %d (want %d) | V %.1f / %.1f (d=%.2f) | extent %.1f x %.1f "
          "of %.1f x %.1f | fill %.0f%% | max H %.1f"
          % (pi, len(rows), len(sol), len(rows), vol, want, vol - want, mx, my, W, H,
             100.0 * area / (mx * my), max_h), flush=True)
    assert len(sol) == len(rows), ("solids", pi)
    assert abs(vol - want) < 1.0, ("volume", pi, vol, want)
    assert mx <= W + 1e-6 and my <= H + 1e-6, ("extent", pi, mx, my)
    assert sbb.zlen <= BED_Z + 1e-6 and abs(sbb.zmin) < 1e-6, ("bed", pi, sbb.zmin, sbb.zlen)

    report["plates"].append({
        "plate": pi, "step": out.name, "n_objects": len(rows),
        "sum_volume_mm3": round(vol, 1), "max_height_mm": round(max_h, 1),
        "used_extent_mm": [round(mx, 1), round(my, 1)],
        "fill_percent": round(100.0 * area / (mx * my), 1),
        "readback": {"solids": len(sol), "solids_ok": len(sol) == len(rows),
                     "volume_ok": abs(vol - want) < 1.0,
                     "bbox_mm": [round(sbb.xlen, 2), round(sbb.ylen, 2), round(sbb.zlen, 2)]},
        "objects": rows})

report["sum_volume_mm3"] = round(sum(p["sum_volume_mm3"] for p in report["plates"]), 1)
(DEST / "plates_index.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
print("wrote", DEST / "plates_index.json", flush=True)

# ---- previews ---------------------------------------------------------------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def draw_plate(ax, pidx, packed, title):
    ax.add_patch(Rectangle((0, 0), BED_X, BED_Y, fill=False, ec="k", lw=1.6))
    ax.add_patch(Rectangle((MARGIN, MARGIN), W, H, fill=False, ec="0.65", ls="--", lw=0.8))
    for i, (r, px, py, sw) in enumerate(sorted(packed, key=lambda e: e[0]["object"])):
        c = PALETTE[i % len(PALETTE)]
        fdx, fdy = rect_dims(r, sw)
        ax.add_patch(Rectangle((MARGIN + px, MARGIN + py), fdx, fdy,
                               fc=c, ec="k", lw=0.5, alpha=0.78))
        if fdx * fdy > 900:
            lab = (r["object"].replace("carriage_clamp_seat_", "clamp_")
                   .replace("motor_bridge_", "bridge_").replace("shooter_", "")
                   .replace("_", "\n"))
            ax.text(MARGIN + px + fdx / 2, MARGIN + py + fdy / 2, lab,
                    ha="center", va="center", fontsize=4.6)
    ax.set_xlim(-10, BED_X + 10)
    ax.set_ylim(-10, BED_Y + 10)
    ax.set_aspect("equal")
    ax.invert_yaxis()
    ax.set_title(title, fontsize=8)
    ax.tick_params(labelsize=6)


for pi, packed in enumerate(plates, start=1):
    fig, ax = plt.subplots(figsize=(7.2, 7.1))
    ext = report["plates"][pi - 1]["used_extent_mm"]
    draw_plate(ax, pi, packed,
               "R66 plate %d/%d - %d parts, max height %.0f mm\nused %.0f x %.0f mm of "
               "%.0f x %.0f mm usable | gap %.0f, margin %.0f"
               % (pi, len(plates), len(packed), report["plates"][pi - 1]["max_height_mm"],
                  ext[0], ext[1], W, H, GAP, MARGIN))
    ax.set_xlabel("X [mm]", fontsize=7)
    ax.set_ylabel("Y [mm]", fontsize=7)
    fig.tight_layout()
    fig.savefig(DEST / ("plate_p%d_preview.png" % pi), dpi=160)
    plt.close(fig)
print("wrote per-plate previews", flush=True)

n = len(plates)
cols = 2 if n > 1 else 1
rows_n = (n + cols - 1) // cols
fig, axes = plt.subplots(rows_n, cols, figsize=(7.4 * cols, 7.3 * rows_n), squeeze=False)
for pi, packed in enumerate(plates, start=1):
    ax = axes[(pi - 1) // cols][(pi - 1) % cols]
    ext = report["plates"][pi - 1]["used_extent_mm"]
    draw_plate(ax, pi, packed,
               "plate %d: %d parts, max H %.0f mm, used %.0f x %.0f mm"
               % (pi, len(packed), report["plates"][pi - 1]["max_height_mm"], ext[0], ext[1]))
for k in range(n, rows_n * cols):
    axes[k // cols][k % cols].axis("off")
tot_parts = report["n_objects"]
fig.suptitle("R66 - all %d printable objects laid flat on %d Bambu H2D plate(s) "
             "(bed %.0f x %.0f x %.0f mm, gap %.0f mm, margin %.0f mm)"
             % (tot_parts, n, BED_X, BED_Y, BED_Z, GAP, MARGIN), fontsize=11)
fig.tight_layout(rect=(0, 0, 1, 0.97))
fig.savefig(DEST / "r66_plates_overview.png", dpi=150)
print("wrote", DEST / "r66_plates_overview.png", flush=True)
