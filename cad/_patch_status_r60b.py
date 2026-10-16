import io, sys
p = "PROJECT_STATUS.md"
s = open(p, encoding="utf-8").read()
reps = []

reps.append((
 "③新增**打印件全集**交付 `T06_print_set_R60_pollen.step`（1.14 MB，**3 个具名实体** = `shooter_frame_R60_merged` + `base_rail_-72` + `base_rail_+72`），一份文件即含全部需打印件；",
 "③新增**打印件全集**交付 `T06_print_set_R60_pollen.step`（3.08 MB，**45 个具名实体** = `shooter_frame_R60_merged` + `base_rail_-72` + `base_rail_+72` + 42 个自制件，一份文件即含全部需打印件；36 件无 SKU COTS 硬件（M4 螺柱 / 压簧 / 销）已明确排除）；",
))

reps.append((
 "⑥`cad/_r60_audit.py` **19/20 PASS**",
 "⑥`cad/_r60_audit.py` **21/22 PASS**",
))

reps.append((
 "`cad/_r60_h2d_audit.py` **77 单体 74 可用**（frame 由 DEC-0063 拆分为最差 lump 303.5 mm PASS；两条 rail 标 accepted_exception））",
 "`cad/_r60_h2d_audit.py` **81 单体 78 可用**（frame 由 DEC-0063 拆分为最差 lump 303.5 mm PASS；两条 rail 标 accepted_exception））",
))

reps.append((
 "T06-R60-PRINT-SET-1.0（R60 打印件全集 STEP：3 个具名实体 = merged frame + 2 条单件加厚滑轨；几何审计 19/20 PASS，唯一未消解项 = 用户已接受的 380 mm 单件滑轨，DEC-0066 / V-0065；候选，待人工接受）。",
 "T06-R60B-PRINT-SET-1.1（R60B 打印件全集 STEP：**45 个具名实体** = merged frame + 2 条单件加厚滑轨 + 42 个自制件，一份文件即含全部需打印件；36 件无 SKU COTS 硬件已排除；几何审计 21/22 PASS，唯一未消解项 = 用户已接受的 380 mm 单件滑轨，DEC-0066 / V-0065；候选，待人工接受）。",
))

reps.append((
 "### 0.10（当前主任务，2026-10-16 起）R60 滑轨下压 + 打印件单件化 + 打印件全集 STEP（DEC-0066 / V-0065）",
 "### 0.10（当前主任务，2026-10-16 起）R60B 滑轨下压 + 打印件单件化 + 打印件全集 STEP（45 件，DEC-0066 / V-0065）",
))

reps.append((
 "**`T06_print_set_R60_pollen.step`（1.14 MB，3 个具名实体 = 全部打印件）**、`T06_shooter_assembly_R60_pollen.step`（4.1 MB，77 件）",
 "**`T06_print_set_R60_pollen.step`（3.08 MB，45 个具名实体 = 全部打印件）**、`T06_shooter_assembly_R60_pollen.step`（4.1 MB，81 件）",
))

reps.append((
 "- **打印件全集（KNOWN，本轮新增交付）**: `T06_print_set_R60_pollen.step` 一份文件里 3 个具名实体 —— `shooter_frame_R60_merged`（V 1 103 726.2）+ `base_rail_-72` + `base_rail_+72`（V 各 173 711.5），共 **1 451 149.3 mm³**、包络 x[-170, 285.26] y[-84, 99] z[-10, 401.02]；`print_set_matches_assembly` PASS。",
 "- **打印件全集（KNOWN，本轮修正交付 / R60B）**: `T06_print_set_R60_pollen.step` 一份文件里 **45 个具名实体**（一件一 body，各带 name 标签）—— `shooter_frame_R60_merged`（V 1 103 726.2）+ `base_rail_-72` / `base_rail_+72`（V 各 173 711.5）+ **42 个自制件**：`bearing_carriage_*` 4、`carriage_clamp_seat_*` 16、`carriage_link_spacer_*` 2、`crosshead` 1、`crosshead_guide_*` 2、`crosshead_guide_stop_*` 2、`gap_servo_standoff_*` 4、`main_spacing_link_*` 2、`motor_bridge_*` 4、`paddle_flex_tip_1/2` 2、`paddle_rotor` 1、`servo_crank` 1、`servo_drag_link` 1；合计 **1 738 472.4 mm³**、包络 x[-170, 285.26] y[-112, 142] z[-10, 401.02]；`print_set_matches_assembly` / `print_set_parts`（45）/ `print_set_volume_no_cots_leak` / `print_set_excludes_all_cots` 全 PASS。\n- **COTS 排除（KNOWN，本轮修正）**: 36 件无 SKU 硬件按 `HARDWARE_PREFIX` 明确排除、不打印 —— `carriage_clamp_stud_*` 16（M4 螺柱）+ `carriage_clamp_spring_*` 16（压缩弹簧）+ `carriage_link_pin_*` 2 + `crosshead_through_pin` + `servo_crank_joint_pin`（销）；另有 29 件有 SKU 采购件（`vendor_cots_bodies`）同样不入打印集。**修正**：`gap_servo_standoff_*` 4 件由 `constrained.py` 用 `C[chr(34)+chr(34)]` 生成，原被 `is_vendor()` 按 `gap_servo_` 前缀误判为采购件，本轮以 `BRING_BACK_PRINTED` 移回打印集。",
))

reps.append((
 "- **审计（MEASURED）**: `cad/_r60_audit.py` **19/20 PASS**，唯一 FAIL",
 "- **审计（MEASURED）**: `cad/_r60_audit.py` **21/22 PASS**（新增 `print_set_parts` / `print_set_volume_no_cots_leak` / `print_set_excludes_all_cots` 三项，`print_set_parts` 改为动态取 `report.print_set.n_printed_bodies`），唯一 FAIL",
))

reps.append((
 "`cad/_r60_h2d_audit.py` **77 单体 74 可用**：`shooter_frame_R60_merged`（432.5 x 183.0 x 404.5）由 DEC-0063 拆分消解",
 "`cad/_r60_h2d_audit.py` **81 单体 78 可用**：`shooter_frame_R60_merged`（432.5 x 183.0 x 404.5）由 DEC-0063 拆分消解",
))

reps.append((
 "- **NEXT ACTION**: 按用户指令**停在此处**，等用户确认「完全合格」后，再把 `.STEP` 里的各打印件拆成独立 `.STEP` 文件放入一个文件夹（预计 3 件：frame + 2 条滑轨；frame 若需进 H2D 仍按 DEC-0063 的 3 块方案）。",
 "- **NEXT ACTION**: 按用户指令**停在此处**，等用户确认「完全合格」后，再把 `.STEP` 里的各打印件拆成独立 `.STEP` 文件放入一个文件夹（预计 **45 件** = merged frame + 2 条单件滑轨 + 42 个自制件；frame 若需进 H2D 仍按 DEC-0063 的 3 块方案）。**用户确认前不得分件。**",
))

for old, new in reps:
    assert s.count(old) == 1, ("COUNT %d for: %r" % (s.count(old), old[:70]))
    s = s.replace(old, new)
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("PROJECT_STATUS.md patched, %d replacements" % len(reps))
