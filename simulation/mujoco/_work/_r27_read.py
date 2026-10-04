import json
from pathlib import Path
r = json.loads(Path("cad/output/paddle_launcher_feeder_a_prime_shared_report_pollen.json").read_text(encoding="utf-8"))
for k in ("shell_relief", "shell_tray_clash_hits", "shell_tray_clash_with_kept_parts_mm3",
          "nest_ball_clash_with_shell_mm3", "nest_ball_clash_with_hub_mm3",
          "sweep_ball_clash_with_shell_max_mm3", "sweep_ball_clash_samples",
          "flywheel_nip_measured_mm", "paddle_hub_to_shell_inner_arc_measured_mm",
          "shell_bbox_after_mm", "shell_volume_mm3"):
    print(k, "=", json.dumps(r.get(k, "<absent>"), ensure_ascii=False))
