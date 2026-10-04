import json, pathlib

shell_p = pathlib.Path("config/t06_feeder_aprime_shared_shell_checks.json")
d = json.loads(shell_p.read_text(encoding="utf-8"))
d["design_id"] = "C06B-FEEDER-A-PRIME-SHARED-R27"
d["note"] = (
    "Round R027, delivered part file cad/output/inspection/_r27_shared_feeder_shell_tray.step, "
    "read back from STEP via --step --step-part-id feeder_shell_tray. Targets come from "
    "config/parameters.yaml (t06_feeder_a_prime_shared) and DEC-0029/DEC-0030, never from the part "
    "under test. Geometry: annular sector 142..275 deg about the paddle axis (29.49, 111.46) with "
    "r_in = 107.974 and r_out = 114.974 mm, extruded +-54 mm in Y (FEEDER_W = 108), fused to the 5 deg "
    "tilted tray. Round R026 froze this one part for BOTH balls (NECTAR and POLLEN differ only in the "
    "flywheel nip). Round R027 adds the exit-side RELIEF (DEC-0031): the shell is notched where the "
    "retained parent structure -- shooter_throat_+55 and guide_roof_3 -- physically runs through it, "
    "with a 0.5 mm offset gap, which is what removes the R026 assembly clash (5717.5 + 126.5 mm3, "
    "re-measured to 0 after the cut). The notch is on the OUTER side (r > R_IN) and the ball track "
    "reaches only to R_IN, so the fed ball never sees it; the generator re-proves that by sampling the "
    "ball along the whole 142..275 deg carry arc (sweep max 0 mm3, 19 samples). Consequence for this "
    "spec: the un-notched 142 deg outer corner (max z 182.245) is relieved to 180.043, so "
    "T06-APS-SHELL-004 is restated as an envelope check -- the shell must stay INSIDE the DEC-0029 "
    "sector envelope on z (span <= 185.759 mm = 182.245 - (-3.514), rule le) rather than reach the "
    "corner exactly. All other targets are unchanged from R026."
)
for c in d["checks"]:
    if c["id"] == "T06-APS-SHELL-004":
        c.clear()
        c.update({
            "id": "T06-APS-SHELL-004",
            "kind": "group_bbox",
            "axis": "z",
            "rule": "le",
            "requirement": ("DEC-0029 + DEC-0031: the shell stays inside the 142..275 deg sector "
                            "envelope on z; the exit-side outer corner itself is relieved by the "
                            "retained throat guide"),
            "part": "feeder_shell_tray",
            "target": 185.759,
            "tolerance": 0.05,
            "method": ("z span of the part bounding box, compared to the un-notched sector envelope "
                       "182.245 - (-3.514) with rule le"),
        })
shell_p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

hub_p = pathlib.Path("config/t06_feeder_aprime_shared_hub_checks.json")
h = json.loads(hub_p.read_text(encoding="utf-8"))
h["design_id"] = "C06B-FEEDER-A-PRIME-SHARED-R27"
h["note"] = h["note"].replace(
    "Delivered files: cad/output/inspection/_r26_shared_{hub,feeder_shell_tray}.step.",
    "Delivered files: cad/output/inspection/_r27_shared_{hub,feeder_shell_tray}.step. "
    "Round R027 changed ONLY the shell (exit-side relief, DEC-0031); the hub is unchanged, so every "
    "hub target below is carried over from R026.")
hub_p.write_text(json.dumps(h, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

print("shell checks:", [(c["id"], c["kind"]) for c in
                        json.loads(shell_p.read_text(encoding="utf-8"))["checks"]])
print("hub design_id:", json.loads(hub_p.read_text(encoding="utf-8"))["design_id"])
