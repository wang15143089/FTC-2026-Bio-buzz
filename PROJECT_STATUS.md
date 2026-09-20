# PROJECT STATUS

最后更新：2026-09-19

## CURRENT OBJECTIVE

为 P2 FLOWER 与 P3 HIVE 分别建立至少两个 M1 机构概念，同时定义可共享的 T04/T05 物体链接口和粗资源预算；不进入详细 CAD。

## CURRENT MODULE

系统级 S00；下一步激活 T04/T05 共享链和 T06/T07 两个概念分支。T01/P1 为共同底座。

## CURRENT DESIGN MATURITY

S00：M0 关口通过，Requirements v0.1 与 Architecture v0.1 已批准；任务包筛选完成。T01：M0 共同底座。T04–T07：允许进入 M1，尚未生成机构概念；其余模块 M0。

## COMPLETED

- 检查工作目录；未发现既有仓库或工程资料。
- 初始化本地 Git 仓库和要求的目录骨架。
- 创建工程协作规则、需求/架构/接口/验证模板、参数主源和日志。
- 建立暂定模块分解、统一坐标约定和成熟度/验证关口。
- 登记并核验 BIOBUZZ Competition Manual TU01、官方场地 STEP、5203-2402-0051 电机 STEP 和 3209-0001-0007 底盘 STEP。
- 从规则建立合法包络、得分物体、计分、控制数量、执行器与电源约束。
- 根据 BIOBUZZ 任务将模块重组为 T04 获取、T05 输送/缓冲/路由、T06 HIVE 发射、T07 FLOWER 处理、T08 控制与自主。
- 建立 P1–P4 任务组合候选；尚未选择机构方案。
- 固化底盘不变量：保持轮距、轴距和四轮相对布局，只允许最低限度拆分重组。
- 将 5203-2402-0051 降级为通用 goBILDA 电机包络参考；实际电机由后续计算选型。
- 确认 REV-31-1595 Control Hub、REV-31-1153 Expansion Hub 和 goBILDA 3100-0012-0020 电池。
- 保存并核验电池尺寸图；建立往届 FTC/工业设计先例的使用与再验证规则。
- 用户批准 Requirements Baseline v0.1 和 Architecture Baseline v0.1。
- 完成 TS-S00-001 P1–P4 加权比较、四种权重敏感性分析及可复算 Python 脚本。
- 建立初始 FTC/系统工程设计先例目录，并记录可迁移原则与赛季差异。
- 形成首轮策略：P1 是共同底座；P2/P3 并行进入 M1；P4 暂缓且不进入详细集成 CAD。

## VALIDATED

- `KNOWN` 目录与最小文件框架已存在。
- `KNOWN` 未开始详细机械设计、最终 CAD 或完整仿真。
- `KNOWN` 必需路径检查通过；Git 已初始化并使用 `main` 分支。
- PDF 关键页面已完成文本与渲染图像交叉核验，范围记录于 SRC-001。
- STEP 压缩包、文件身份、架构版本和单位元数据已检查；尚未测量代理包络。
- `config/parameters.yaml` 已人工结构审查；当前环境仍无 YAML 解析库，机器解析测试保留为待办且未伪报通过。
- 电池图纸包络 124 × 47.8 × 43 mm、120 mm 线束、XT30、16 AWG 和 20 A 保险丝已目视核验。
- `calculations/task_package_trade.py` 已执行；权重总和、评分范围和向量长度断言通过。
- 脚本输出与 `calculations/task_package_trade_results.csv` 完全一致。
- 任务包敏感性结果：P3 仅在“得分优先”场景第一；P1 在其余三种场景第一；P4 在全部场景第四。

## OPEN QUESTIONS

无未关闭 CRITICAL 信息项。

方案比较权重、项目时间表、预算、性能目标、软件栈和维护目标仍为 IMPORTANT；当前可在明确假设下进入 M1，见 `docs/requirements.md` 与 ASM-004。

## KNOWN PROBLEMS

- 规则仅为 TU01；后续 Team Update 可能改变阈值或合法性要求。
- 底盘轮距/轴距及底盘、电机、Control Hub 代理包络尚未从 STEP/实物测量，不能用于尺寸承诺。
- 缺少性能目标、时间表、预算和方案比较权重。
- TS-S00-001 的评分为工程判断，不是测量；不能用来预测比赛成绩或冻结最终任务组合。
- FTC 先例多来自不同赛季和不同形状物体，所有机构原则必须针对 BIOBUZZ 重新验证。
- Git 仓库尚无首个提交；当前未配置 `user.name`/`user.email`，因此未擅自伪造提交身份。
- Git Credential Manager 2.7.3 已配置为 Windows Credential Manager (`wincredman`)；远程仓库地址、提交署名和自动推送时刻尚未提供，所以尚未触发登录或上传。

## ASSUMPTIONS

- ASM-004：首轮任务包采用中性权重和 1–5 序数评分，仅用于筛选 M1 分支。
- 坐标方向是可撤销的工程约定，见 `docs/module_interfaces.md`。

## FILES MODIFIED

- `AGENTS.md`
- `README.md`
- `PROJECT_STATUS.md`
- `docs/*.md`
- `config/parameters.yaml`
- `references/source_register.md`
- `references/gobilda_3100-0012-0020_dimensions.png`
- `references/design_precedents.md`
- `calculations/task_package_trade.py`
- `calculations/task_package_trade_results.csv`
- `.gitignore`

## LATEST DESIGN VERSION

Framework v0.3.0；Requirements v0.1 APPROVED；Architecture v0.1 APPROVED；TS-S00-001 v0.1；Robot design：M1 概念工作待开始。

## NEXT ACTION

为 P2 与 P3 各建立至少两个不绑定具体尺寸的 M1 机构概念；先定义 T04/T05 共享物体交接接口，再给出粗质量、体积、功率、执行器和主要失效模式预算。用 L1/L2/L3 方法筛选需制作的最小 L6 原型，仍不生成详细机构 CAD。
