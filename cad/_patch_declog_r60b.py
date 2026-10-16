BT = chr(96)
p = "docs/decision_log.md"
s = open(p, encoding="utf-8").read()
reps = []

reps.append((
 "## DEC-0066 - 决策：R60 滑轨底面再下压至 z = -10（厚 26 mm）",
 "## DEC-0066（决策 3 部分 SUPERSEDED by DEC-0067，2026-10-16） - 决策：R60 滑轨底面再下压至 z = -10（厚 26 mm）",
))

reps.append((
 "- 决策 3 - 新增打印件全集 STEP（KNOWN）: 导出 " + BT + "T06_print_set_R60_pollen.step" + BT + "，一份文件 3 个具名实体（" + BT + "shooter_frame_R60_merged" + BT + " + " + BT + "base_rail_-72" + BT + " + " + BT + "base_rail_+72" + BT + "）= 全部需打印件，省去从装配件里挑件。",
 "- 决策 3 - 新增打印件全集 STEP（KNOWN，**部分 SUPERSEDED by DEC-0067**）: 导出 " + BT + "T06_print_set_R60_pollen.step" + BT + "，一份文件 3 个具名实体（" + BT + "shooter_frame_R60_merged" + BT + " + " + BT + "base_rail_-72" + BT + " + " + BT + "base_rail_+72" + BT + "）。**该集合经复审认定不完整**：漏了 42 个自制打印件（轴承座 / 夹座 / 十字头 / 马达桥 / 拨杆 / 支撑柱 …）=> DEC-0067 已把确权规则改为「非 COTS 即打印件」，全集扩为 **45 件**。",
))

reps.append((
 "## V-0065 - 验证记录（非决策）：R60「滑轨下压 3 mm + 单件滑轨 + 打印件全集 STEP」复核",
 "## V-0065（打印全集 / 审计计数两项 SUPERSEDED by V-0066） - 验证记录（非决策）：R60「滑轨下压 3 mm + 单件滑轨 + 打印件全集 STEP」复核",
))

reps.append((
 "  - 打印件全集: " + BT + "print_set_parts" + BT + " = 3 具名实体、" + BT + "print_set_matches_assembly" + BT + " PASS；总 V = 1 451 149.3 mm³、包络 x[-170, 285.26] y[-84, 99] z[-10, 401.02]。",
 "  - 打印件全集: " + BT + "print_set_parts" + BT + " = 3 具名实体、" + BT + "print_set_matches_assembly" + BT + " PASS；总 V = 1 451 149.3 mm³、包络 x[-170, 285.26] y[-84, 99] z[-10, 401.02]。（**不完整集合，已被 V-0066 取代：应为 45 件 / 1 738 472.4 mm³**）",
))

reps.append((
 "  - 审计: 几何 **19/20 PASS**，唯一 FAIL = ",
 "  - 审计: 几何 **19/20 PASS**（**已被 V-0066 取代，新版 21/22 PASS**），唯一 FAIL = ",
))

reps.append((
 "；H2D **77 单体 74 可用**（frame 由 DEC-0063 拆分消解",
 "；H2D **77 单体 74 可用**（**已被 V-0066 取代：81 单体 78 可用**）（frame 由 DEC-0063 拆分消解",
))

for old, new in reps:
    assert s.count(old) == 1, ("COUNT %d : %r" % (s.count(old), old[:60]))
    s = s.replace(old, new)

s = s.rstrip("\n") + "\n\n" + "\n".join([
 "## DEC-0067 - 决策：R60B 打印件全集确权规则改为「非 COTS 即打印件」，全集由 3 件扩为 45 件",
 "",
 "- 判据（KNOWN）: 用户 2026-10-16 指令「让 .STEP 文件包含所有需要打印的部分（不要再把滑轨分成两部分）」。DEC-0066 的交付只含 3 个实体（frame + 2 条滑轨），**不满足「所有需要打印的部分」**：结构里的轴承座、夹座、十字头、马达桥、拨杆、支撑柱等 42 个自制件同样是必须打印的件，却只在装配件里、不在打印集里。",
 "- 决策 1 - 确权规则（KNOWN）: 打印集 = 装配件里**除 COTS 采购件与厂商件以外的全部实体**，一件一个具名 body。否决「白名单挑件」写法（漏件不可见）；改为**黑名单排除**，任何新加的自制件自动进打印集。",
 "- 决策 2 - COTS 黑名单（KNOWN）: 新增 `HARDWARE_PREFIX`，排除 36 件无 SKU 硬件 —— `carriage_clamp_stud_*` 16（M4 螺柱）、`carriage_clamp_spring_*` 16（压缩弹簧）、`carriage_link_pin_*` 2、`crosshead_through_pin`、`servo_crank_joint_pin`（销）。另有 29 件有 SKU 采购件（`vendor_cots_bodies`）本来就排除。=> 打印集 45 件，COTS 65 件（36 无 SKU + 29 有 SKU）明确不打印。",
 "- 决策 3 - 误判修正（MEASURED）: `gap_servo_standoff_*` 4 件（调隙舵机支撑柱）由 `cad/paddle_launcher_constrained.py` 用 `C[\"structure\"]` 生成，属于**自制打印件**，但旧 `is_vendor()` 按 `gap_servo_` 前缀把它误判成采购件 => 新增 `BRING_BACK_PRINTED` 把这 4 件移回打印集。",
 "- 决策 4 - 审计同步（KNOWN）: `cad/_r60_audit.py` 的 `print_set_parts` 改为**动态**取 `report.print_set.n_printed_bodies`（不再硬编码 3），并新增 `print_set_volume_no_cots_leak`（打印集体积必须等于各打印件体积之和，无 COTS 渗入）与 `print_set_excludes_all_cots`（打印集与 COTS 名单交集为空）。",
 "- 影响: 打印集 3 -> **45 件**，STEP 1.14 -> **3.08 MB**，V 1 451 149.3 -> **1 738 472.4 mm³**；装配件报告 `n_parts` 77 -> **81**（`keep` 名单把 4 个支撑柱从 vendor 移回 printed）；主体与滑轨几何**零改动**（frame V 1 103 726.2 与 bbox 逐位不变）。",
 "- Alternatives（已否决）: ①保留 3 件全集、把其余打印件留给用户从装配件里自己挑 —— 直接违背本轮指令，否决；②按「有 SKU = 采购件」自动判定 —— `gap_servo_standoff_*` 反例证明前缀不可靠，否决。",
 "- 未验证项（TBD）: ①380 mm 单件滑轨如何进 H2D（沿用 DEC-0066 TBD ①，用户已接受现状）；②45 件各自的打印朝向 / 支撑 / 排版；③PET 收缩对 Ø3.2 打印孔与 Ø6 螺母窝的影响（本轮未测）。",
 "- Date/version: 2026-10-16 / 产物 `cad/paddle_launcher_shooter_assembly_r60.py`（经 `cad/_patch_r60b.py` 改造）、`cad/_r60_printset_probe.py`（逐件实探）、`cad/_r60b_readback.py`（回读）、`cad/_patch_r60b_audit.py` -> `cad/output/_r60_frame/T06_print_set_R60_pollen.step`（45 solids, 3.08 MB）、`report_r60_pollen.json`、`audit_r60.json`、`audit_r60_h2d.json`；关联 Linear KEI-24、Notion Mechanical Design - Scoring Mechanism 页",
 "",
 "## V-0066 - 验证记录（非决策）：R60B「打印件全集 = 45 件」复核",
 "",
 "- 目的（KNOWN）: ①证明打印集含「所有需要打印的部分」且不含任何 COTS 件；②证明扩集后几何零改动；③证明交付 STEP 与装配件一致。",
 "- 方法（MEASURED，只回读）: ①`cad/_r60_printset_probe.py` 对 `report_r60_pollen.json` 的 77 个 `kept` 件**逐件实探**，按生成来源分成「打印件 / COTS 硬件 / 厂商件」三类；②重跑生成器 `.venv-cad\\Scripts\\python.exe -X utf8 cad\\paddle_launcher_shooter_assembly_r60.py pollen --step`（41.1 s）；③`cad/_r60b_readback.py` 回读打印集 STEP 数体、称重、取包络；④`cad/_r60_audit.py`（22 项）与 `cad/_r60_h2d_audit.py`（81 单体）。",
 "- 实测（MEASURED）:",
 "  - 打印集: `T06_print_set_R60_pollen.step` **45 solids**、3.08 MB、V **1 738 472.4 mm³**（报告求和 1 738 472.5，差 0.1 mm³ = 求和舍入）、包络 x[-170, 285.26] y[-112, 142] z[-10, 401.02]；`print_set_parts` 45 / `print_set_volume_no_cots_leak` PASS / `print_set_excludes_all_cots` PASS / `print_set_matches_assembly` PASS。",
 "  - 45 件构成: `shooter_frame_R60_merged` 1 + `base_rail_-72` / `base_rail_+72` 2 + 42 个自制件（`bearing_carriage_*` 4、`carriage_clamp_seat_*` 16、`carriage_link_spacer_*` 2、`crosshead` 1、`crosshead_guide_*` 2、`crosshead_guide_stop_*` 2、`gap_servo_standoff_*` 4、`main_spacing_link_*` 2、`motor_bridge_*` 4、`paddle_flex_tip_1/2` 2、`paddle_rotor` 1、`servo_crank` 1、`servo_drag_link` 1）。",
 "  - COTS 排除: 36 件无 SKU 硬件 + 29 件有 SKU 采购件 = **65 件明确不打印**；打印集与 COTS 名单交集 = 0。",
 "  - 几何零改动（回归判据）: `T06_shooter_frame_R60_pollen.step` V **1 103 726.2 mm³**、bbox 与 R60 **逐位相同**（R60B vs R60 主体差 = 0）。",
 "  - 报告 diff: `n_parts` 77 -> 81，逐键 diff 只落在预期项（`print_set` 新增、`cots_hardware_bodies` 新增、vendor 33 -> 29、`print_set_step.parts` 3 -> 45、mb 1.14 -> 3.08）。",
 "  - 审计: `cad/_r60_audit.py` **21/22 PASS**，唯一 FAIL = `rail_pieces_H2D_fit`（380.0 mm，超 325 共 55.0 mm，`accepted_exception`，DEC-0066）；`cad/_r60_h2d_audit.py` **81 单体 78 可用**（3 个 FAIL：frame 由 DEC-0063 拆分消解、两条 rail 标 `accepted_exception`；单体内最差 lump 303.5 mm PASS）。",
 "- 判定: 用户「包含所有需要打印的部分」**pass**（45 件，无 COTS 渗入）；滑轨单件保持不变；唯一未消解项仍是用户已接受的单件滑轨 380 mm。",
 "- 未验证项（TBD）: 见 DEC-0067（单件滑轨进 H2D / 45 件打印排版 / PET 收缩）。",
 "- Date/version: 2026-10-16 / 产物 `cad/output/_r60_frame/audit_r60.json`、`cad/output/_r60_frame/audit_r60_h2d.json`、`cad/output/_r60_frame/report_r60_pollen.json`",
]) + "\n"

open(p, "w", encoding="utf-8", newline="\n").write(s)
print("decision_log.md patched + appended")
