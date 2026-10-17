# -*- coding: utf-8 -*-
from pathlib import Path

root = Path(r"C:\FTC design\FTC 2026 biobuzz")

# 1) PRINT_README: add Bambu import section right after the 目录 block
p = root / "deliverables/R69_print_package/PRINT_README.md"
t = p.read_text(encoding="utf-8")
anchor = "- `parts_index.json` / `plates_index.json` / `fasteners.json` — 清单、排版与紧固记录，可复算\n"
add = anchor + """
## Bambu Studio 导入（2026-10-16 补）

- **推荐**：`parts_flat/` — 54 个文件，每个 = 1 个单实体零件，已放平、min-Z = 0、XY 居中。
  导入后直接「自动摆放」，不会出现「超出盘边界 / 超高」。
- 整板文件 `plates/*.step` 的装配变换已烘焙进几何，回读 bbox 全部 ≤ 307 x 307 x 136 mm 也合格；
  若 Bambu 把多实体并成一个对象，右键 →「拆分对象」即可。
- **不要导入** `cad/output/_r69_split/` 或 `_r69_p1/`：那是裁切前的中间件
  （外罩 403.7 mm、侧板 361 x 385 mm），必然超界/超高。已移入
  `cad/output/_superseded/` 并加 `_SUPERSEDED` 后缀。
"""
assert anchor in t
p.write_text(t.replace(anchor, add, 1), encoding="utf-8")
print("readme ok")

# 2) decision log
d = root / "docs/decision_log.md"
t = d.read_text(encoding="utf-8").rstrip() + """

## DEC-0077 — Bambu Studio 报“超界 / 超高”：旧中间件被误用；补出单件平放 STEP

- 日期：2026-10-16
- 状态：ACTIVE（R69 补充，不改动 R69 几何）
- 现象（USER）：Bambu Studio 导入两个 STEP 报「物体位于盘的边界上或超过了高度限制」：
  - 对象 1：403.691 x 136 x 232.835 mm，V 537 144 mm³
  - 对象 2：361.064 x 31 x 385.024 mm，V 312 153 mm³
- 根因（MEASURED，回读 STEP）：这两个对象**不是** R69 的交付件，而是 R69 拆分过程中的**裁切前中间件**：
  - `cad/output/_r69_split/mid.step` → **403.7 x 136.0 x 232.8 mm，V 537 144.3 mm³**（与截图 1 一致）
  - `cad/output/_r69_split/plate_R.step` → **361.1 x 31.0 x 385.0 mm，V 312 150.0 mm³**（与截图 2 一致，差值来自网格化）
  - 最终件分别是 `shroud_tray_mid`（248.4 x 136.0 x 232.8，V 414 543.1）与 `side_plate_right`（262.2 x 31.0 x 284.0，V 199 554.9）。
- 处置：
  1. 把 `_r69_split/`、`_r69_p1/` 移入 `cad/output/_superseded/` 并加 `_SUPERSEDED` 后缀 + README，防止再次误用。
  2. 新增 `cad/_r69_parts_flat.py`：从**已验收的整板 STEP** 里取每个实体（变换已烘焙），
     平移到 min-Z = 0、XY 居中，逐件导出到 `deliverables/R69_print_package/parts_flat/`。
  3. 生成 `parts_flat_index.json` 与 `previews/bambu_fix_dimensions.png`。
- 方法（MEASURED）：`cad/_r69_parts_flat.py`（导出）+ `cad/_r69_parts_flat_verify.py`（逐件回读）。
- 结果（MEASURED）：
  - 54/54 件全部**单实体**、`zmin = 0.000`、bbox ≤ **315 x 310 x 325 mm**；
  - 最大高度 **136.0 mm**（`shroud_tray_mid`），最大平面尺寸 **287.09 mm**（`base_rail_±72`）；
  - ΣV **1 766 184.4 mm³**，与 R69 验收值完全一致（无几何变动）。
- 判定：**pass**（问题为文件误用，几何本身无缺陷）。
- 未验证（TBD）：Bambu Studio 实机切片未跑（本机无切片器自动化）。
"""

d.write_text(t, encoding="utf-8")
print("decision log ok")
