# -*- coding: utf-8 -*-
"""R57 audit: floor plate replaces the two base rails (user decision 2026-10-14).

Everything below is MEASURED from the R57 STEP outputs that get delivered; the
R56 report is used only for the "is the frame unchanged" cross-check.
"""
import json
import sys
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
OUT = HERE / "output" / "_r57_frame"
r56 = json.loads((HERE / "output" / "_r56_frame" / "report_r56_pollen.json")
                 .read_text(encoding="utf-8"))
r57 = json.loads((OUT / "report_r57_pollen.json").read_text(encoding="utf-8"))

import paddle_launcher_shooter_assembly_r57 as R57   # noqa: E402

H2D = (325.0, 320.0, 325.0)
res = {"units": "mm", "checks": []}


def add(name, target, measured, tol, verdict, method=""):
    res["checks"].append({"id": name, "target": target, "measured": measured,
                          "tol": tol, "verdict": verdict, "method": method})
    print("%-26s target=%-22s measured=%-22s %s"
          % (name, target, measured, verdict))


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


# ---------------------------------------------------------------- export/read
plate_path = OUT / "T06_floor_plate_R57_pollen.step"   # as delivered by the generator
plate = cq.Compound.makeCompound(cq.importers.importStep(str(plate_path)).vals())
pb = bb(plate)
frame = cq.Compound.makeCompound(
    cq.importers.importStep(str(OUT / "T06_shooter_frame_R57_pollen.step")).vals())
fb = bb(frame)

print("plate :", json.dumps(pb), "V=%.0f" % plate.Volume(), "solids=%d" % len(plate.Solids()))
print("frame :", json.dumps(fb), "V=%.0f" % frame.Volume())
print()

# 1. plate envelope inside the H2D single-nozzle box
pd = (pb["x"][1] - pb["x"][0], pb["y"][1] - pb["y"][0], pb["z"][1] - pb["z"][0])
add("plate_H2D_fit", "<= %.0f x %.0f x %.0f" % H2D,
    "%.1f x %.1f x %.1f" % pd, 0.0,
    "pass" if all(d <= l for d, l in zip(pd, H2D)) else "fail",
    "read back T06_floor_plate_R57_pollen.step, AABB")

# 2. plate is the lowest point of the whole mechanism
zmin = {"floor_plate_R57": pb["z"][0], "shooter_frame_R57_merged": fb["z"][0]}
for p in r57["parts"]:
    zmin[p["part"]] = min(zmin.get(p["part"], 1e9), p["bbox"]["z"][0])
low = min(zmin.items(), key=lambda kv: kv[1])
add("lowest_point_of_assembly", "floor_plate_R57", "%s @ z=%.2f" % low, 0.0,
    "pass" if low[0] == "floor_plate_R57" else "fail", "min z over all R57 parts")
add("plate_below_frame", "plate underside below frame zmin (-3.51)",
    "plate bottom z=%.2f vs frame z=%.2f" % (pb["z"][0], fb["z"][0]), 0.0,
    "pass" if pb["z"][0] < fb["z"][0] else "fail", "read-back AABB")

# 3. base rails really gone
left = [p["part"] for p in r57["parts"] if "base_rail" in p["part"]]
add("base_rail_deleted", "0 parts", "%d parts" % len(left), 0.0,
    "pass" if not left else "fail", "R57 report part list")

# 4. frame body identical to R56 (tabs kept, nothing else touched)
v56 = [p["volume_mm3"] for p in r56["parts"]
       if p["part"] == "shooter_frame_R56_merged"][0]
add("frame_volume_vs_R56", "%.1f mm3" % v56, "%.1f mm3" % frame.Volume(), 1.0,
    "pass" if abs(frame.Volume() - v56) < 1.0 else "fail",
    "R57 frame STEP read-back vs R56 report")

# 5. frame / plate interference
inter = frame.intersect(plate)
add("frame_plate_interference", "0.000 mm3", "%.4f mm3" % inter.Volume(), 0.05,
    "pass" if inter.Volume() < 0.05 else "fail", "boolean intersect")

# 6. per-joint column: tab hole, pillar hole, nut pocket, pillar top
rows = []
for x, sy in R57.HOLE_XY:
    y = sy
    tab_hole = cylz(1.6, 17.0, 43.0, x, y).intersect(frame).Volume()
    pil_hole = cylz(1.6, -8.0, 15.5, x, y).intersect(plate).Volume()
    pocket = cylz(3.0, -11.5, -9.05, x, y).intersect(plate).Volume()
    top = box(x - 5, x + 5, y - 7, y + 7, 15.0, 15.9).intersect(plate).Volume()
    skin = box(x - 5, x + 5, y - 7, y + 7, -9.0, -8.6).intersect(plate).Volume()
    rows.append({"x": x, "y": y, "tab_hole_mm3": round(tab_hole, 3),
                 "pillar_hole_mm3": round(pil_hole, 3),
                 "pocket_empty_mm3": round(pocket, 3),
                 "pillar_top_mm3": round(top, 3),
                 "nut_ceiling_mm3": round(skin, 3),
                 "pass": tab_hole < 0.05 and pil_hole < 0.05})
    print("  joint x=%.0f y=%+.0f tab_hole=%.3f pillar_hole=%.3f pocket=%.3f "
          "pillar_top=%.1f nut_ceiling=%.1f"
          % (x, y, tab_hole, pil_hole, pocket, top, skin))
res["joints"] = rows
add("all_4_bolt_holes_clear", "0 material in O3.2", "%d/4 clear"
    % sum(1 for r in rows if r["pass"]), 0.0,
    "pass" if all(r["pass"] for r in rows) else "fail",
    "O3.2 probe through tab + pillar + plate")
add("nut_pockets_empty", "0 material in O6 x 2.45 deep",
    "%d/4 empty" % sum(1 for r in rows if r["pocket_empty_mm3"] < 0.05), 0.0,
    "pass" if all(r["pocket_empty_mm3"] < 0.05 for r in rows) else "fail",
    "O6 probe z -11.5..-9.05")
add("pillar_tops_flush_with_tab_bottom", "z = 16.0 for 4/4",
    "%d/4 at 15..15.9" % sum(1 for r in rows if r["pillar_top_mm3"] > 10.0), 0.1,
    "pass" if all(r["pillar_top_mm3"] > 10.0 for r in rows) else "fail",
    "10 x 14 x 0.9 slab just under the tab")

# 7. print notes
add("plate_print_note", "single printed part, no joint",
    "%.0f cm3, PETG ~%.0f g" % (plate.Volume() / 1000.0,
                                plate.Volume() / 1000.0 * 1.27), None,
    "info", "volume x 1.27 g/cm3")
res["plate"] = {"bbox": pb, "volume_mm3": round(plate.Volume(), 1), "dims_mm": pd}
res["frame"] = {"bbox": fb, "volume_mm3": round(frame.Volume(), 1)}
res["allowance_mm"] = {"plate_top_to_frame_lowest": round(pb["z"][1] - fb["z"][0], 2)}
(OUT / "audit_r57.json").write_text(json.dumps(res, indent=1, ensure_ascii=False),
                                    encoding="utf-8")
print()
print("written:", OUT / "audit_r57.json")
bad = [c for c in res["checks"] if c["verdict"] == "fail"]
print("FAILED: %d" % len(bad))
for c in bad:
    print("  ", c)
