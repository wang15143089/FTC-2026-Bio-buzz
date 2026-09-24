# FTC 2026–2027 BIOBUZZ 工程协作规则

本仓库使用 [Linear — FTC 2026 biobuzz](https://linear.app/keithschoolrobotic/project/ftc-2026-biobuzz-c4695fa110f5) 管理“还需要做什么”，使用 [Notion — FTC Robot Project](https://app.notion.com/p/3e27fc7bbcfb81159c11c41464b523fc) 保存“已经知道什么以及为什么”，GitHub 保存可复算、可生成和可审查的工程产物。

## 每次恢复工作的固定顺序

1. 完整阅读本文件、`README.md` 与 `PROJECT_STATUS.md`。
2. 检查 `git status`、最近提交和当前模块文件。
3. 搜索 Linear 项目中的既有问题，再搜索 Notion 中的约束、决策、失败和测试结果；不得重复创建或覆盖历史。
4. 从 `PROJECT_STATUS.md` 的 `NEXT ACTION` 恢复，不重复已完成且已验证的工作。
5. 开始修改前确认当前模块、成熟度、接口和待验证问题。
6. 有意义的工作结束时更新 `PROJECT_STATUS.md`、对应 Linear 问题和 Notion 知识页，再提交并推送 GitHub。

若 Linear 或 Notion 暂时不可用，先把结果保存在仓库，并在 Linear 留下缺失同步步骤；恢复连接后补齐。

## 工程事实标签

所有关键数据和结论必须标记为：

- `KNOWN`：来自已确认需求、官方资料或已接受的工程约定。
- `ASSUMED`：为推进工作采用、但尚未确认的假设。
- `CALCULATED`：可由记录的输入和方法复算。
- `SIMULATED`：来自注明模型、边界条件和版本的仿真。
- `MEASURED`：来自注明设备、样件和日期的实测。
- `TBD`：尚未确定，不得暗中补值。

优先级为 `MEASURED/官方 KNOWN > CALCULATED > SIMULATED > ASSUMED`；冲突必须记录并解决。

## 设计与变更规则

- 需求 ID、模块 ID、接口 ID、验证 ID 和决策 ID 必须稳定且可追踪。
- 关键尺寸只在 `config/parameters.yaml` 或明确的模块参数文件中定义一次。
- 默认几何单位为 mm；计算文件必须显式写单位，禁止无单位数值。
- 模块须能独立生成和验证；早期仅使用低细节代理几何。
- 不得跳过 M0–M8 阶段；确需跳过时写入 `docs/decision_log.md`。
- 不得因为 CAD 或首个样机存在就将子系统标为完成；必须准确写明已完成范围。
- 不覆盖用户未提交的修改；不删除被替代的方案，改用 superseded 记录和链接保留工程历史。
- Git 密码、令牌和私钥不得写入聊天、仓库、脚本或明文配置。
- CAD、计算、仿真和测试产物必须记录输入参数版本、生成脚本与结果状态。

## Linear 规则

- 非平凡问题必须包括目标、技术要求、依赖、预期输出、测试标准和当前状态。
- 工作流映射：Backlog = Backlog，Todo = Planned，In Progress = In Progress/Testing，Done = Completed。
- Bug、干涉、失败测试、缺失要求和证据支持的改进都应进入 Linear。
- 当前远端架构使用 T01–T10 模块编号；历史/外部记录中的 T02 Intake 必须明确标为导入参考，不得误写成当前架构的 T02 主承力结构。

## Notion 规则

- 记录耐久的尺寸、计算、选型、接口、证据、结果、失败、经验和决策，避免短暂过程笔记。
- 决策记录包含 Decision、Reason、Alternatives、Evidence、Risks、Next step、日期和关联 Linear 问题。
- 保留 superseded 记录并链接修订，不擦除历史。

## 文件职责

- `docs/requirements.md`：需求与验收条件的唯一主索引。
- `docs/system_architecture.md`：系统边界、模块划分与依赖。
- `docs/module_interfaces.md`：坐标系与接口控制记录（ICD）。
- `docs/validation_plan.md`：分级验证策略与验证矩阵。
- `docs/assumptions.md`：有责任人、风险和失效条件的临时假设。
- `docs/decision_log.md`：重要且可追溯的工程决策。
- `config/parameters.yaml`：全局参数的主数据源。
- `PROJECT_STATUS.md`：当前恢复点，不作为需求或参数的第二数据源。

## 生命周期与阶段关口

工程生命周期：Requirements → Concept → Calculation → CAD → Simulation → Prototype → Testing → Analysis → Redesign → Final design。

模块成熟度：M0 需求、M1 概念、M2 计算、M3 简化几何、M4 详细参数化 CAD、M5 隔离验证、M6 子系统集成、M7 整机集成、M8 制造发布。进入下一阶段前必须满足验证条件或记录获批例外。
