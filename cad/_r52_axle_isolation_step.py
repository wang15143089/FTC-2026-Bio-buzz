# -*- coding: utf-8 -*-
"""R52 axle isolation, re-measured from the DELIVERED STEP (not the generator).

Why this exists: the R52 generator screens "does any part reach both sliding
carriages" but puts ``shooter_side_plate_`` on its skip list, so the plate --
the one big part that spans both axles on purpose -- was never boolean-tested
in R52.  R51 tested it (its skip list has no plate) and got zero, but the goal
claim is about the delivered R52 file, so measure it there.

Read only.  Writes cad/output/_r52_drive/axle_isolation_step_r52.json

  .venv-cad/Scripts/python.exe -X utf8 cad/_r52_axle_isolation_step.py [variant]
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import cadquery as cq

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "cad" / "output" / "_r52_drive"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Parts that legitimately live between / around the two axles and cannot be
# judged by "does it reach both carriages":
#   the carriages themselves, the two shafts, the wheels, the hubs.
SKIP_BOTH = ("bearing_carriage_", "flywheel_shaft_", "gecko_flywheel_",
             "sonic_hub_")
HEAVY = ("flywheel_motor_", "paddle_servo_", "gap_servo_", "gate_servo_")
THR = 0.5


def bbox_of(shape):
    return shape.BoundingBox()


def overlap(ba, bb, eps=1e-6):
    return (ba.xmax > bb.xmin + eps and bb.xmax > ba.xmin + eps
            and ba.ymax > bb.ymin + eps and bb.ymax > ba.ymin + eps
            and ba.zmax > bb.zmin + eps and bb.zmax > ba.zmin + eps)


def vol(a, b):
    try:
        return round(a.intersect(b).Volume(), 3)
    except Exception as exc:                                   # pragma: no cover
        return {"error": str(exc)[:90]}


def reach(shape, bbox, others):
    """Max intersect volume of ``shape`` against a group, bbox-screened."""
    best = 0.0
    for name, other, obb in others:
        if not overlap(bbox, obb):
            continue
        v = vol(shape, other)
        if isinstance(v, dict):
            return v
        best = max(best, v)
    return round(best, 3)


def run(variant):
    step = OUT / ("T06_shooter_assembly_R52_%s.step" % variant)
    row = {"step": step.name, "size_mb": round(step.stat().st_size / 1e6, 1)}
    t0 = time.time()
    assy = cq.Assembly.load(str(step))
    row["load_s"] = round(time.time() - t0, 1)
    print("[%s] loaded %.1f s, %d children" % (variant, row["load_s"],
                                               len(assy.children)), flush=True)
    names = {ch.name: ch.obj for ch in assy.children}
    boxes = {n: bbox_of(s) for n, s in names.items()}
    row["n_parts"] = len(names)

    def group(sub):
        return [(n, names[n], boxes[n]) for n in sorted(names) if sub in n]

    upper, lower = group("bearing_carriage_upper_"), group("bearing_carriage_lower_")
    row["carriage_upper"] = [n for n, _, _ in upper]
    row["carriage_lower"] = [n for n, _, _ in lower]

    # 1) the screen r52 skipped: does the side plate reach either carriage?
    plates = group("shooter_side_plate_")
    plate_rows = {}
    for n, s, bb in plates:
        plate_rows[n] = {
            "to_upper_mm3": reach(s, bb, upper),
            "to_lower_mm3": reach(s, bb, lower),
        }
    row["side_plate_vs_carriages"] = plate_rows
    row["side_plate_reaches_any_carriage"] = any(
        isinstance(v["to_upper_mm3"], (int, float)) and v["to_upper_mm3"] > THR
        or isinstance(v["to_lower_mm3"], (int, float)) and v["to_lower_mm3"] > THR
        for v in plate_rows.values())

    # 2) the general screen, plate included this time
    cand, rigid, heavy = [], [], []
    for n, s in sorted(names.items()):
        if n.startswith(SKIP_BOTH):
            continue
        bb = boxes[n]
        if not (any(overlap(bb, b) for _, _, b in upper)
                and any(overlap(bb, b) for _, _, b in lower)):
            continue
        cand.append(n)
        if n.startswith(HEAVY):
            heavy.append(n)
            continue
        vu = reach(s, bb, upper)
        vl = reach(s, bb, lower)
        if (isinstance(vu, (int, float)) and isinstance(vl, (int, float))
                and vu > THR and vl > THR):
            rigid.append({"part": n, "to_upper_mm3": vu, "to_lower_mm3": vl})
    row["bbox_screen_candidates"] = cand
    row["rigid_link_between_axles"] = rigid
    row["bbox_only_heavy"] = heavy

    # 3) the two axles must not touch each other either
    row["carriages_touch"] = vol(names[row["carriage_upper"][0]],
                                 names[row["carriage_lower"][0]])
    up_shaft = [n for n in names if n.startswith("flywheel_shaft_upper")]
    lo_shaft = [n for n in names if n.startswith("flywheel_shaft_lower")]
    row["shafts_touch"] = vol(names[sorted(up_shaft)[0]],
                              names[sorted(lo_shaft)[0]])
    row["total_s"] = round(time.time() - t0, 1)
    return row


def main():
    want = sys.argv[1:] or ["pollen", "nectar"]
    path = OUT / "axle_isolation_step_r52.json"
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    for v in want:
        data[v] = run(v)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=1),
                        encoding="utf-8")
        print("== %s: rigid_link=%s plate_reaches_carriage=%s cand=%d (%.1f s)"
              % (v, data[v]["rigid_link_between_axles"],
                 data[v]["side_plate_reaches_any_carriage"],
                 len(data[v]["bbox_screen_candidates"]), data[v]["total_s"]),
              flush=True)
    print("wrote", path, flush=True)


if __name__ == "__main__":
    main()
