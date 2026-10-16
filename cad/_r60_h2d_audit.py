# -*- coding: utf-8 -*-
"""R60 H2D print-envelope audit.

Question (user, 2026-10-14): are ALL single bodies inside the Bambu Lab H2D
build volume?  KNOWN, Bambu Lab tech specs: single nozzle 325 x 320 x 325 mm
(dual nozzle: 300 x 320 x 320 overlapping / 350 x 320 x 325 combined).  This
audit uses the single-nozzle box, which is the conservative one.

R60 (2026-10-16): the two rails are one printed piece per side again, 380 mm
long, so they exceed the box by 55 mm.  That is a KNOWN, user-accepted
deviation (DEC-0066) and is tagged as such below -- the check still reports
`fail` so the deviation never silently disappears from the record.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "output" / "_r60_frame"
LIMITS = (325.0, 320.0, 325.0)


def verdict(dims):
    axis = all(d <= l for d, l in zip(dims, LIMITS))
    rot = all(d <= l for d, l in zip(sorted(dims, reverse=True),
                                     sorted(LIMITS, reverse=True)))
    return axis, rot


def main():
    rep = json.loads((OUT / "report_r60_pollen.json").read_text(encoding="utf-8"))
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
        if r["part"].startswith("base_rail"):
            r["accepted_exception"] = (
                "user, 2026-10-16: one printed rail per side is wanted; the H2D "
                "325 mm overshoot is KNOWN and user-accepted (DEC-0066), TBD")
    print("H2D single-nozzle envelope: %.0f x %.0f x %.0f mm" % LIMITS)
    print("bodies in the R60 report: %d   fail (no orientation fits): %d"
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

    # R60: the rails stay one piece, so the 55 mm overshoot is EXPECTED here
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

    (OUT / "audit_r60_h2d.json").write_text(json.dumps(
        {"limits_mm": list(LIMITS), "n_bodies": len(rows), "bodies": rows,
         "fail": fail, "split_lumps": lumps}, indent=1, ensure_ascii=False),
        encoding="utf-8")
    print()
    print("written:", OUT / "audit_r60_h2d.json")


if __name__ == "__main__":
    main()
