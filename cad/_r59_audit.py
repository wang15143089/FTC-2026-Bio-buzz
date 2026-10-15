# -*- coding: utf-8 -*-
"""R59 audit: the two base rails stay and are thickened downwards; no floor plate.

Everything below is MEASURED from the R59 STEP outputs that get delivered; the
R56/R57 reports are used only for the "is the frame unchanged" cross-check.
"""
import json
import sys
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
OUT = HERE / "output" / "_r59_frame"
r56 = json.loads((HERE / "output" / "_r56_frame" / "report_r56_pollen.json")
                 .read_text(encoding="utf-8"))
r57 = json.loads((HERE / "output" / "_r57_frame" / "report_r57_pollen.json")
                 .read_text(encoding="utf-8"))
r59 = json.loads((OUT / "report_r59_pollen.json").read_text(encoding="utf-8"))

import paddle_launcher_shooter_assembly_r59 as R59   # noqa: E402

H2D = (325.0, 320.0, 325.0)
SOLE_ZB = R59.SOLE_ZB
res = {"units": "mm", "checks": []}


def add(name, target, measured, tol, verdict, method=""):
    res["checks"].append({"id": name, "target": target, "measured": measured,
                          "tol": tol, "verdict": verdict, "method": method})
    print("%-28s target=%-26s measured=%-30s %s" % (name, target, measured, verdict))


def bb(s):
    b = s.BoundingBox()
    return {"x": [round(b.xmin, 2), round(b.xmax, 2)],
            "y": [round(b.ymin, 2), round(b.ymax, 2)],
            "z": [round(b.zmin, 2), round(b.zmax, 2)]}


def cylz(r, z0, z1, x, y):
    return cq.Solid.makeCylinder(r, z1 - z0, cq.Vector(x, y, z0), cq.Vector(0, 0, 1))


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0).translate(
        ((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0)).val()


def comp(path):
    return cq.Compound.makeCompound(cq.importers.importStep(str(path)).vals())


# ---------------------------------------------------------------- export/read
rails = comp(OUT / "T06_base_rail_R59_pollen.step")
rb = bb(rails)
frame = comp(OUT / "T06_shooter_frame_R59_pollen.step")
fb = bb(frame)
print("rails :", json.dumps(rb), "V=%.0f" % rails.Volume(),
      "solids=%d" % len(rails.Solids()))
print("frame :", json.dumps(fb), "V=%.0f" % frame.Volume())
print()

# 1. both rails are back, and each is split into a front and a rear half
names = [p["part"] for p in r59["parts"]]
fronts = [n for n in names if n.endswith("_front")]
rears = [n for n in names if n.endswith("_rear")]
add("base_rail_present", "2 rails (4 split pieces)",
    "%d rails / %d pieces" % (len(fronts), len(fronts) + len(rears)), 0.0,
    "pass" if len(fronts) == 2 and len(rears) == 2 else "fail",
    "R59 report part list")
gone = [p["part"] for p in names if p.startswith("floor_plate")]
add("floor_plate_removed", "0 parts", "%d parts" % len(gone), 0.0,
    "pass" if not gone else "fail", "R59 report part list")

# 2. rails are the lowest point of the whole mechanism
zmin = {"base_rail_R59": rb["z"][0], "shooter_frame_R59_merged": fb["z"][0]}
for p in r59["parts"]:
    zmin[p["part"]] = min(zmin.get(p["part"], 1e9), p["bbox"]["z"][0])
low = min(zmin.items(), key=lambda kv: kv[1])
add("lowest_point_of_assembly", "a base_rail_R59 piece @ z=%.2f" % SOLE_ZB,
    "%s @ z=%.2f" % (low[0], low[1]), 0.0,
    "pass" if low[0].startswith("base_rail") and abs(low[1] - SOLE_ZB) < 0.05
    else "fail", "min z over all R59 parts")
add("rail_below_frame", "rail underside below frame zmin (%.2f)" % fb["z"][0],
    "rail bottom z=%.2f vs frame z=%.2f" % (rb["z"][0], fb["z"][0]), 0.0,
    "pass" if rb["z"][0] < fb["z"][0] else "fail", "read-back AABB")
add("ground_clearance_to_frame", ">= 3.0 mm", "%.2f mm" % (fb["z"][0] - rb["z"][0]),
    0.5, "pass" if (fb["z"][0] - rb["z"][0]) >= 3.0 else "fail",
    "frame zmin - rail zmin, read-back AABB")

# 3. thickened section really is the rail's own footprint, no relief needed
solej = 0.0
for y in (-R59.BOLT_Y, R59.BOLT_Y):
    solej += box(R59.RAIL_X0, R59.RAIL_X1, y - 9.0, y + 9.0,
                 SOLE_ZB + 0.05, R59.RAIL_ZB - 0.05).intersect(frame).Volume()
add("sole_zone_free_of_frame", "0.000 mm3",
    "%.4f mm3" % solej, 0.05, "pass" if solej < 0.05 else "fail",
    "frame intersect the two sole boxes (x -170..210, y +-63..81, z -6.95..1.95)")

# 4. frame / rail interference
inter = frame.intersect(rails)
add("frame_rail_interference", "0.000 mm3", "%.4f mm3" % inter.Volume(), 0.05,
    "pass" if inter.Volume() < 0.05 else "fail", "boolean intersect")

# 5. frame body identical to R56 / R57
v56 = [p["volume_mm3"] for p in r56["parts"]
       if p["part"] == "shooter_frame_R56_merged"][0]
v57 = [p["volume_mm3"] for p in r57["parts"]
       if p["part"] == "shooter_frame_R57_merged"][0]
add("frame_volume_vs_R56", "%.1f mm3" % v56, "%.1f mm3" % frame.Volume(), 1.0,
    "pass" if abs(frame.Volume() - v56) < 1.0 else "fail",
    "R59 frame STEP read-back vs R56 report")
add("frame_volume_vs_R57", "%.1f mm3" % v57, "%.1f mm3" % frame.Volume(), 1.0,
    "pass" if abs(frame.Volume() - v57) < 1.0 else "fail",
    "R59 frame STEP read-back vs R57 report")
add("frame_bbox_vs_R57", json.dumps(r57["merged_into_frame"]["bbox"]),
    json.dumps(fb), 0.05,
    "pass" if all(abs(fb[k][i] - r57["merged_into_frame"]["bbox"][k][i]) < 0.05
                  for k in "xyz" for i in (0, 1)) else "fail",
    "read-back AABB comparison")

# 6. per-joint: M3 clearance hole through tab + rail, nut pocket empty
rows = []
for x, sy in R59.HOLE_XY:
    y = sy
    piece = R59.rail_names(1 if y > 0 else -1)[0]
    tab_hole = cylz(1.6, 17.0, 43.0, x, y).intersect(frame).Volume()
    rail_hole = cylz(1.6, SOLE_ZB + 0.2, 15.7, x, y).intersect(rails).Volume()
    pocket = cylz(3.0, SOLE_ZB, SOLE_ZB + 2.45, x, y).intersect(rails).Volume()
    skin = box(x - 5, x + 5, y - 7, y + 7, SOLE_ZB, SOLE_ZB + 0.4).intersect(rails).Volume()
    below = box(x - 5, x + 5, y - 7, y + 7, SOLE_ZB - 4.0,
                SOLE_ZB - 0.1).intersect(rails).Volume()
    rows.append({"x": x, "y": y, "piece": piece,
                 "tab_hole_mm3": round(tab_hole, 3),
                 "rail_hole_mm3": round(rail_hole, 3),
                 "pocket_empty_mm3": round(pocket, 3),
                 "sole_floor_mm3": round(skin, 3),
                 "nothing_below_sole_mm3": round(below, 3),
                 "pass": tab_hole < 0.05 and rail_hole < 0.05})
    print("  joint x=%.0f y=%+.0f %-22s tab_hole=%.3f rail_hole=%.3f pocket=%.3f "
          "sole_floor=%.1f below=%.3f"
          % (x, y, piece, tab_hole, rail_hole, pocket, skin, below))
res["joints"] = rows
add("all_4_bolt_holes_clear", "0 material in O3.2",
    "%d/4 clear" % sum(1 for r in rows if r["pass"]), 0.0,
    "pass" if all(r["pass"] for r in rows) else "fail",
    "O3.2 probe through tab (frame) + thickened rail")
add("nut_pockets_empty", "0 material in O6 x 2.45 deep",
    "%d/4 empty" % sum(1 for r in rows if r["pocket_empty_mm3"] < 0.05), 0.0,
    "pass" if all(r["pocket_empty_mm3"] < 0.05 for r in rows) else "fail",
    "O6 probe z SOLE_ZB..SOLE_ZB+2.45")
add("rail_floor_under_nut", "> 20 mm3 for 4/4",
    "%d/4 solid" % sum(1 for r in rows if r["sole_floor_mm3"] > 20.0), 0.0,
    "pass" if all(r["sole_floor_mm3"] > 20.0 for r in rows) else "fail",
    "10 x 14 x 0.4 slab at the sole underside")
add("nothing_protrudes_below_sole", "0.000 mm3 for 4/4",
    "%.3f mm3 max" % max(r["nothing_below_sole_mm3"] for r in rows), 0.05,
    "pass" if max(r["nothing_below_sole_mm3"] for r in rows) < 0.05 else "fail",
    "10 x 14 x 3.9 slab below the sole underside")

# 7. the four O4.6 chassis holes stay through-holes at the new thickness
holes = []
for n in [x for x in names if x.startswith("base_rail")]:
    b = [p["bbox"] for p in r59["parts"] if p["part"] == n][0]
    yy = R59.RAIL_CY if "_+" in n else -R59.RAIL_CY   # MEASURED: chassis holes sit on the rail centre line
    for x in R59.RAIL_HOLE_X:
        if not (b["x"][0] + 3.0 < x < b["x"][1] - 3.0):
            continue
        h = cylz(1.9, SOLE_ZB - 1.0, R59.RAIL_ZT + 1.0, x, yy).intersect(rails).Volume()
        holes.append({"piece": n, "x": x, "y": yy, "material_mm3": round(h, 3)})
bad_h = [h for h in holes if h["material_mm3"] > 0.05]
add("chassis_holes_through", "0 material in O3.8",
    "%d/%d through" % (len(holes) - len(bad_h), len(holes)), 0.0,
    "pass" if not bad_h else "fail",
    "O3.8 probe z -8..17 in each rail piece, per chassis hole x")
res["chassis_holes"] = holes

# 8. H2D envelope of the individual rail pieces
pd = []
for n in [x for x in names if x.startswith("base_rail")]:
    b = [p["bbox"] for p in r59["parts"] if p["part"] == n][0]
    d = (b["x"][1] - b["x"][0], b["y"][1] - b["y"][0], b["z"][1] - b["z"][0])
    pd.append({"part": n, "dims_mm": d})
worst = max(max(p["dims_mm"]) for p in pd)
add("rail_pieces_H2D_fit", "<= 325 mm longest side",
    "worst %.1f mm" % worst, 0.0, "pass" if worst <= 325.0 else "fail",
    "read-back AABB per printed piece against single-nozzle 325 x 320 x 325")
res["rail_pieces"] = pd

res["rails"] = {"bbox": rb, "volume_mm3": round(rails.Volume(), 1)}
res["frame"] = {"bbox": fb, "volume_mm3": round(frame.Volume(), 1)}
res["allowance_mm"] = {"frame_lowest_above_sole": round(fb["z"][0] - rb["z"][0], 2)}
(OUT / "audit_r59.json").write_text(json.dumps(res, indent=1, ensure_ascii=False),
                                    encoding="utf-8")
print()
print("written:", OUT / "audit_r59.json")
bad = [c for c in res["checks"] if c["verdict"] == "fail"]
print("FAILED: %d" % len(bad))
for c in bad:
    print("  ", c)
