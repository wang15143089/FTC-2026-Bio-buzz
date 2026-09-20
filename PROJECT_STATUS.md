# PROJECT STATUS

最后更新：2026-09-19

## CURRENT OBJECTIVE

关闭 P3 M1 发射概念关口缺口：补齐底盘/射位 L3 几何、模块质量/体积/持续电流预算和 L6 共用台架规格；不进入详细 CAD。

## CURRENT MODULE

T06 HIVE 主分支，关联 T04/T05/T08；T07 FLOWER 仍仅作为 P4 增量接口研究。

## CURRENT DESIGN MATURITY

S00：M0 通过。T06：M1 ACTIVE，已有三个概念、初筛选择、接口草案及部分 L2 计算，但质量/体积/持续功率预算未关闭，因此尚未通过 M1、也未正式进入 M2。T04/T05：M1 接口草案。T07：M0 增量研究。

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
- 曾形成 TS-S00-001 v0.1 首轮策略（P2/P3 并行、P4 暂缓）；该策略已由 v0.2/DEC-0010 明确取代，保留本条仅作变更历史。
- 配置仓库本地提交署名 `yutian <wagnyutian923@126.com>`、GitHub `origin` 和 `main` 上游分支；首个工程基线已安全推送。
- Git Credential Manager 使用 Windows Credential Manager 保存认证；已启用每天 20:00（America/Chicago）的安全检查点自动化，重要验证节点立即推送。
- 按用户要求把战略总权重从 25% 提高到 70%，并用 TU01 分值、RP、时间窗口与解锁关系重建 TS-S00-001 v0.2。
- 修订任务包方向：P3 为主 M1、P4 为资源关口约束的扩展、P2 为 HIVE 风险回退；P1 仅作为共同底座。
- 建立 P3-M1 v0.1：C06-A 单飞轮曲面压板、C06-B 对置双飞轮、C06-C 可调弹射器三个概念及失效模式。
- 完成 P3-BAL-0.1 真空弹道扫参、P3-MOT-0.1 电机/轮速初筛和 P3-TS-001 概念比较；输入、脚本、CSV 和测试均已落盘。
- 建立 IF-T05-T06-01、IF-T02-T06-01、IF-T03-T06-01、IF-T08-T06-01、IF-T06-ENV-01 草案。
- 初步选择 C06-B/C06-A 进入共用可调台架，C06-C 作为风险回退；未冻结最终机构。

## VALIDATED

- `KNOWN` 目录与最小文件框架已存在。
- `KNOWN` 未开始详细机械设计、最终 CAD 或完整仿真。
- `KNOWN` 必需路径检查通过；Git 已初始化并使用 `main` 分支。
- PDF 关键页面已完成文本与渲染图像交叉核验，范围记录于 SRC-001。
- STEP 压缩包、文件身份、架构版本和单位元数据已检查；尚未测量代理包络。
- `config/parameters.yaml` 已人工结构审查；当前环境仍无 YAML 解析库，机器解析测试保留为待办且未伪报通过。
- 电池图纸包络 124 × 47.8 × 43 mm、120 mm 线束、XT30、16 AWG 和 20 A 保险丝已目视核验。
- TS-S00-001 v0.2 的脚本输出与保存 CSV 完全一致；权重总和、战略默认权重 70%、评分范围和半分增量断言通过。
- 战略权重为 60%、70%、80% 时，P3 均为第一、P4 均为第二；默认得分 P3 84.8、P4 78.2、P2 55.7、P1 55.4。
- PDF 文本与已渲染 pp.83–91 交叉核验了比赛阶段、HIVE/FLOWER/GARDEN 规则及 Table 10-2/10-3。
- PDF 文本与渲染 pp.71–72、87 交叉核验 HIVE/CELL 几何和合法 TIP 方法。
- P3 计算测试 6/6 通过；生成 CSV 与脚本重生成结果一致。
- `CALCULATED` 1.5 m、55°、400–700 mm 出射高度需要约 4.92–5.56 m/s；模型忽略阻力/旋转，未伪报为实测。
- `CALCULATED` 312/1150 RPM 直驱未通过；1620 RPM + 120 mm 进入原型范围，6000 RPM 需减速/限速。
- `ASSUMED` 概念初筛为 C06-B 76、C06-A 69、C06-C 66；仅用于原型排序。

## OPEN QUESTIONS

无未关闭 CRITICAL 信息项。

项目时间表、预算、命中率/周期目标、软件栈和维护目标仍为 IMPORTANT。POLLEN/NECTAR 质量、尺寸分布和飞轮传递系数需实测；不阻塞台架设计，但阻塞最终电机/惯量选择。

## KNOWN PROBLEMS

- 规则仅为 TU01；后续 Team Update 可能改变阈值或合法性要求。
- 底盘轮距/轴距及底盘、电机、Control Hub 代理包络尚未从 STEP/实物测量，不能用于尺寸承诺。
- 缺少性能目标、时间表和预算。
- TS-S00-001 v0.2 的战略输入来自规则，但工程评分仍是证据锚定的假设，不是测量；不能用来预测比赛成绩或冻结最终机构。
- FTC 先例多来自不同赛季和不同形状物体，所有机构原则必须针对 BIOBUZZ 重新验证。
- P3 真空弹道未包含轻质开孔球的阻力、Magnus 效应、球体变形或动态 HIVE；结果只作为台架起始窗口。
- 还没有实物球质量、轮速—球速传递系数、命中散布、连续射击恢复和温升数据。
- 定时上传依赖本机在线、GitHub 凭据有效且当前任务可运行；认证、验证、远程领先或分叉时自动化将停止上传并请求人工处理。

## ASSUMPTIONS

- ASM-005：默认战略总权重 70%，工程评分在无台架数据时采用规则/几何锚定判断，并用 60%–80% 敏感性检查。
- ASM-006..008：P3 采用真空弹道、0.65 轮面传递比及 0.75–2.0 m/50–60° 参数扫参，均待 L3/L6 证据替换。
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
- `docs/p3_hive_concept.md`
- `calculations/p3_launcher_inputs.json`
- `calculations/p3_ballistics.py` / `p3_ballistics_results.csv`
- `calculations/p3_motor_screen.py` / `p3_motor_screen_results.csv`
- `calculations/p3_concept_trade.py` / `p3_concept_trade_results.csv`
- `tests/test_p3_ballistics.py`
- `.gitignore`

## LATEST DESIGN VERSION

Framework v0.4.0；Requirements v0.1 APPROVED；Architecture v0.1 APPROVED；TS-S00-001 v0.2；P3-M1 v0.1 ACTIVE；P3-BAL/MOT/TS v0.1。

## NEXT ACTION

从底盘/场地 STEP 建立低细节 L3 侧视射位与遮挡模型，补齐 C06-A/C06-B 的粗质量、体积、持续电流和维护包络；形成共用 L6 台架 BOM/测试矩阵。取得实物球后优先测质量与尺寸分布；仍不生成详细机构 CAD。
