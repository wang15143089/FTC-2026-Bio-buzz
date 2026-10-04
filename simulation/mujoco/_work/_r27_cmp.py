import json
from pathlib import Path
N = json.loads(Path("cad/output/paddle_launcher_feeder_a_prime_shared_report_nectar.json").read_text(encoding="utf-8"))["variants"]["nectar"]
P = json.loads(Path("cad/output/paddle_launcher_feeder_a_prime_shared_report_pollen.json").read_text(encoding="utf-8"))["variants"]["pollen"]
for tag, V in (("NECTAR", N), ("POLLEN", P)):
    rl = V["shell_relief"]
    print(tag, "bbox_after =", rl["shell_bbox_after_mm"])
    print(tag, "clash_hits =", V["shell_tray_clash_hits"], "| sum =", V["shell_tray_clash_with_kept_parts_mm3"])
    print(tag, "relief =", rl["relief_targets_removed_mm3"], rl["relief_clearance_mm"])
    print(tag, "vol", rl["shell_volume_before_mm3"], "->", rl["shell_volume_after_mm3"], "removed", rl["shell_volume_removed_mm3"])
    print(tag, "sweep clash", V["sweep_ball_clash_with_shell_max_mm3"], "samples", V["sweep_ball_clash_samples"],
          "| nest shell/hub", V["nest_ball_clash_with_shell_mm3"], V["nest_ball_clash_with_hub_mm3"],
          "| nip", V["flywheel_nip_measured_mm"], "| hub-shell", V["paddle_hub_to_shell_inner_arc_measured_mm"])
    print()
print("SAME SHELL VOLUME:", N["shell_relief"]["shell_volume_after_mm3"] == P["shell_relief"]["shell_volume_after_mm3"])
print("SAME SHELL BBOX  :", N["shell_relief"]["shell_bbox_after_mm"] == P["shell_relief"]["shell_bbox_after_mm"])
print("SAME RELIEF      :", N["shell_relief"]["relief_targets_removed_mm3"] == P["shell_relief"]["relief_targets_removed_mm3"])
