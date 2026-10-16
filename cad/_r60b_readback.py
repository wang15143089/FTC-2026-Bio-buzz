# -*- coding: utf-8 -*-
import json
from pathlib import Path
import cadquery as cq
OUT = Path("cad/output/_r60_frame")
rep = json.loads((OUT / "report_r60_pollen.json").read_text(encoding="utf-8"))
ps = OUT / rep["print_set_step"]["file"]
rd = cq.importers.importStep(str(ps))
sol = rd.val().Solids()
print("print_set : %s" % ps.name)
print("  solids : %d   V=%.1f mm3   MB=%.2f"
      % (len(sol), sum(s.Volume() for s in sol), ps.stat().st_size / 1e6))
exp = sum(p["volume_mm3"] for p in rep["parts"]
          if p["part"] in set(rep["print_set"]["printed"]))
print("  expected bodies %d, sum V=%.1f mm3"
      % (rep["print_set"]["n_printed_bodies"], exp))
print("  hardware excluded: %d | vendor excluded: %d | gate excluded: %d"
      % (len(rep["print_set"]["cots_hardware_not_printed"]),
         len(rep["excluded_from_this_version"]["vendor_cots_bodies"]),
         len(rep["excluded_from_this_version"]["gate_solids"])))
for stem in ("T06_shooter_frame_R60_pollen.step", "T06_base_rail_R60_pollen.step",
             "T06_shooter_assembly_R60_pollen.step"):
    print("%-38s %9.1f KB" % (stem, (OUT / stem).stat().st_size / 1e3))
