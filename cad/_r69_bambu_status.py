from pathlib import Path
p = Path(r"C:\FTC design\FTC 2026 biobuzz\PROJECT_STATUS.md")
t = p.read_text(encoding="utf-8")
old = "# PROJECT STATUS\n\n最后更新："
assert t.startswith(old)
new = """# PROJECT STATUS

最后更新：2026-10-16（**R69-Bambu 补丁：两份 STEP 报“超界/超高”已定位为旧中间件误用，补出 54 件单件平放 STEP（DEC-0077 / V-0077）**：①判据（KNOWN）= 用户 2026-10-16 两张 Bambu Studio 报错截图「物体位于盘的边界上或超过了高度限制」，对象 A 403.691 x 136 x 232.835、V 537 144 mm³，对象 B 361.064 x 31 x 385.024、V 312 153 mm³。②根因（MEASURED）：两者**不是** R69 交付件，而是拆分过程的**裁切前中间件** —— `_r69_split/mid.step` 回读 403.7 x 136.0 x 232.8、V **537 144.3**；`_r69_split/plate_R.step` 回读 361.1 x 31.0 x 385.0、V **312 150.0**，与截图逐项吻合。最终件 `shroud_tray_mid` 248.4 x 136.0 x 232.8（V 414 543.1）、`side_plate_right` 262.2 x 31.0 x 284.0（V 199 554.9）均在 H2D 可用区 315 x 310 x 325 内。③处置：`_r69_split/` 与 `_r69_p1/` 移入 `cad/output/_superseded/` + `_SUPERSEDED` 后缀 + README（防误用）；新增 `cad/_r69_parts_flat.py` 从已验收整板 STEP 逐件烘焙导出。④验收（MEASURED，`cad/_r69_parts_flat_verify.py`）：**54/54 单实体、zmin = 0.000、bbox ≤ 315 x 310 x 325**，最大高 136.0（`shroud_tray_mid`）、最大平面 287.09（`base_rail_±72`），ΣV **1 766 184.4 mm³** = R69 验收值，几何零变动。⑤交付：`deliverables/R69_print_package/parts_flat/`（54 STEP + README + `parts_flat_index.json`）、`previews/bambu_fix_dimensions.png`。**导入用 `parts_flat/`，不要用 `_r69_split/`。** 遗留：Bambu 实机切片未跑。DEC-0077 / V-0077）

上一状态："""
p.write_text(t.replace(old, new, 1), encoding="utf-8")
print("ok")
