import json, pathlib
cfg = pathlib.Path("config")
meta = {
    "hub": ("t06_feeder_aprime_nectar_hub_checks.json",
            "t06_feeder_aprime_shared_hub_checks.json",
            "paddle_hub"),
    "shell": ("t06_feeder_aprime_nectar_shell_checks.json",
              "t06_feeder_aprime_shared_shell_checks.json",
              "feeder_shell_tray"),
}
note_extra = ("  Round R026: the SAME hub / shell+tray part is used for BOTH balls "
              "(DEC-0030). Targets are unchanged from DEC-0029 because the shared "
              "geometry set was inherited from the accepted NECTAR R25 part; only the "
              "rotor now carries TWO blades (330/150 deg) instead of three. Delivered "
              "files: cad/output/inspection/_r26_shared_{hub,feeder_shell_tray}.step.")
for key, (src, dst, part) in meta.items():
    d = json.loads((cfg / src).read_text(encoding="utf-8"))
    d["design_id"] = "C06B-FEEDER-A-PRIME-SHARED-R26"
    d["note"] = d["note"] + note_extra
    for c in d["checks"]:
        c["id"] = c["id"].replace("-APN-", "-APS-")
        if c.get("part"):
            c["part"] = part
    (cfg / dst).write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8")
    print("wrote", dst, "checks:", len(d["checks"]))
