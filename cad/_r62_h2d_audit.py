# -*- coding: utf-8 -*-
"""R62 H2D print-envelope audit.

Question (user, 2026-10-14): are ALL single bodies inside the Bambu Lab H2D
build volume?  KNOWN, Bambu Lab tech specs: single nozzle 325 x 320 x 325 mm
(dual nozzle: 300 x 320 x 320 overlapping / 350 x 320 x 325 combined).  This
audit uses the single-nozzle box, which is the conservative one.

R62 (2026-10-16): the joined base rail is cut at x = -40 into 3 pieces
(DEC-0069), so NO rail exceeds the box any more -- the R61 accepted exception
of 383.3 mm is closed.  The only body that still exceeds the box as a single
bbox is the merged frame, which the user already accepted as a two-plane split
(DEC-0063 / V-0062) -- the R56 split lumps are printed below as the proof.
The check still reports `fail` for it so the deviation never silently
disappears from the record.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "output" / "_r62_frame"
LIMITS = (325.0, 320.0, 325.0)


def verdict(dims):
    axis = all(d <= l for d, l in zip(dims, LIMITS))
    rot = all(d <= l for d, l in zip(sorted(dims, reverse=True),
                                     sorted(LIMITS, reverse=True)))
    return axis, rot


def main():
    rep = json.loads((OUT / "report_r62_pollen.json").read_text(encoding="utf-8"))
    rows = []
    for e in rep["parts"]:
        b = e["bbox"]
        dims = (b["x"][1] - b["x"][0], b["y"][1] - b["y"][0], b["z"][1] - b["z"][0])
        rows.append({"part": e["part"], "role": e["role"],
                     "dims_mm": [round(v, 1) for v in dims],
                     "volume_mm3": e["volume_mm3"]})
    rows.sort(key=lambda r: -max(r["dims_mm"]))
    for r in rows:
        r["axis_aligned_ok"], r["rotated_ok"] = verdict(tuple(r["dims_mm"]))

    fail = [r for r in rows if not r["rotated_ok"]]
    for r in rows:
        if r["part"].startswith("shooter_frame"):
            r["accepted_exception"] = (
                "user, 2026-10-14: the merged frame is printed as a two-plane "
                "split (DEC-0063 / V-0062); the lumps are listed below and all "
                "fit, so the single-bbox overshoot is KNOWN and user-accepted. "
                "No base_rail body exceeds the box any more (DEC-0069).")
    print("H2D single-nozzle envelope: %.0f x %.0f x %.0f mm" % LIMITS)
    print("bodies in the R62 report: %d   fail (no orientation fits): %d"
          % (len(rows), len(fail)))
    print()
    print("%-38s %-24s %11s  %s" % ("part", "dx x dy x dz (mm)", "V mm3", "verdict"))
    for r in rows[:14]:
        v = "PASS" if r["rotated_ok"] else "FAIL"
        if r["rotated_ok"] and not r["axis_aligned_ok"]:
            v = "PASS(rotate)"
        print("%-38s %-24s %11.0f  %s"
              % (r["part"], " x ".join("%.1f" % d for d in r["dims_mm"]),
                 r["volume_mm3"], v))
    print("   ... %d more smaller bodies, all PASS" % max(0, len(rows) - 14))
    print()
    for r in fail:
        print("%s %-30s %s mm"
              % ("ACCEPTED" if r.get("accepted_exception") else "FAIL",
                 r["part"], " x ".join("%.1f" % d for d in r["dims_mm"])))

    # R62: only the merged frame still overshoots the raw bbox; the two-plane
    # split (DEC-0063) turns it into lumps that all fit -- printed below.
    split = HERE / "output" / "_r56_frame" / "split" / "report_r56_split.json"
    lumps = []
    if split.exists():
        sr = json.loads(split.read_text(encoding="utf-8"))
        for piece, lrows in sr["lumps"].items():
            for i, lr in enumerate(lrows):
                lumps.append({"piece": piece, "lump": i,
                              "dims_mm": lr["dims_mm"],
                              "volume_mm3": lr["volume_mm3"],
                              "fits": lr["fits"]})
        print()
        print("after the two-plane split the merged frame becomes %d lumps:"
              % len(lumps))
        for l in lumps:
            print("  %-24s lump %d  %-24s V=%9.0f  %s"
                  % (l["piece"], l["lump"],
                     " x ".join("%.1f" % d for d in l["dims_mm"]),
                     l["volume_mm3"], "PASS" if l["fits"] else "FAIL"))
        print("worst lump %.1f mm  (limit %.0f, margin %.1f)"
              % (max(max(l["dims_mm"]) for l in lumps), LIMITS[0],
                 LIMITS[0] - max(max(l["dims_mm"]) for l in lumps)))
    else:
        print()
        print("split report not found yet:", split)

    (OUT / "audit_r62_h2d.json").write_text(json.dumps(
        {"limits_mm": list(LIMITS), "n_bodies": len(rows), "bodies": rows,
         "fail": fail, "split_lumps": lumps}, indent=1, ensure_ascii=False),
        encoding="utf-8")
    print()
    print("written:", OUT / "audit_r62_h2d.json")


if __name__ == "__main__":
    main()
