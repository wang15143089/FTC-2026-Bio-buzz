# PROJECT STATUS

最后更新：2026-09-20

## CURRENT OBJECTIVE

完成C04-B1官方FLOWER STEP扫掠、6 V舵机传动校核与M3低细节初模；下一步制作同一1:1夹具并随机比较C04-A/B1，不进入最终制造CAD。

## CURRENT MODULE

T04 intake 主模块，C04-B1 25°斜向侧拨为首个L6原型、C04-A为回退，关联T05/T06/T08；T06继续采用C06-B双飞轮主原型。T07顶部放球仍仅作P4增量接口研究。

## CURRENT DESIGN MATURITY

S00：M0通过。T04：C04-B1 M3 PRELIMINARY，官方STEP名义几何与初模完成，实体公差/力/循环未关闭；C04-A维持M1回退。T06：M1 ACTIVE，C06-B为主原型。T05：M1共享动力接口。T07：M0增量研究。

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
- 完成 P3-LAUNCHER-CMP-0.2 约束优先比较：解析证明单轮静止压板和等速对置双轮的平移/自旋关系、20 mm 球径差的压缩变化及单侧/对称调隙中心线差异。
- 选择 C06-B 对置双飞轮为主原型，C06-A 单飞轮曲面压板作为同台对照和资源回退；旧 P3-TS-001 主观加权分不再承担选择理由。
- 定义共享 intake 的 FLOWER 边界：底部逐个取出 POLLEN 纳入基线且不增加电机；顶部低速放球仅保留安装/控制接口。
- 建立 IF-T04-FLOWER-01、IF-T04-T07-01 和 VAL-T06-005/VAL-T04-001/VAL-T07-001。
- 完成T01-DRIVE-TRADE-0.1：量化四电机麦克纳姆、四电机差速和两电机差速的端口、质量、理想功率/牵引力、等工况电力与横移路径边界；当前保留四电机麦克纳姆。
- 建立C04-A上方薄拨叉+末端落钩+顺从分段roller方案；FLOWER功能使用2舵机但不增加直流电机。
- 将T04 roller与短预输送合并为1个带编码器电机动力源，单球节拍由舵机闸门承担；与四电机底盘、双飞轮合计7个电机，保留1端口。
- 建立T04-INTAKE-0.1输入、复算脚本、CSV、单元测试、IF-T04-FLOWER-01 v0.2、IF-T04-T05-01及VAL-T04-002/003。
- 建立可交互的FLOWER取球动作侧视示意，覆盖对位、上方伸入、落钩、回拉和roller接管五个状态。
- 按用户草图把C04-B定义为标准roller之外的FLOWER补充拨杆，并拆分为只经底部Retrieval Opening离开的C04-B1与规则排除的真实侧出口C04-B2。
- 完成T04-INTAKE-0.2名义台阶/斜面运动学、舵机力矩和资源复算；建立C04-A/B1证据评分、规则硬门槛和预登记A/B夹具方案。
- 将C04-B1提升为首个L3/L6原型，C04-A保留回退；更新IF-T04-FLOWER-01 v0.3、VAL-T04-004/005和DEC-0015。
- 建立C04-B1双通道、底部边界和抬升动作交互示意。
- 登记SRC-016独立FLOWER STEP并以SHA-256锁定；CadQuery测得34实体和169.380 × 156.559 × 595.211 mm名义包络。
- 完成T04-FLOWER-SWEEP-0.1：纯−X横移因左后短支柱干涉淘汰；从−X朝−Y偏25°后，完整球、3×20×32 mm拨片和Ø60×120 mm roller名义实体交叠均为0。
- 将目标舵机用户参数纳入T04-INTAKE-0.3；6 V直驱不满足，初模采用3.2:1减速并保留2.9 A堵转/电源瞬态开放项。
- 生成并回读C04-B1 M3参数化CadQuery初模：机构独立STEP 6实体，组合STEP 40实体；未建模舵机未知外形、紧固件或制造细节。

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
- P3-LAUNCHER-CMP-0.3复算通过；v0.2的运动学证明保持不变，v0.3把C04-A共享动力纳入资源预算。
- `CALCULATED_IDEAL` 5.5557 m/s 基准球速下，120 mm 单轮+静止压板理想轮速为 1768.4 rpm 并产生自旋；等速对置双轮为 884.2 rpm/轮且理想净自旋为零。该结论不代表真实效率或精度。
- `CALCULATED` 两球名义直径差 20 mm；固定间隙的压缩量相差 20 mm；单侧调隙的局部球心移动 10 mm，对称调隙保持名义中心线。
- `CALCULATED_NOMINAL` FLOWER 顶口对 POLLEN/NECTAR 径向余量为 15.25/5.25 mm；底部取 POLLEN 的名义高度余量为 19 mm；只证明名义几何未排除，不替代实体试验。
- `KNOWN` TU01 G418 已核对：得分物体只能从顶部进入 FLOWER，且只能从底部取出 POLLEN；G410 禁止最后 60 秒前让 NECTAR 进入 FLOWER 计分体积。
- 项目单元测试现为26/26通过；T01/T04生成CSV与脚本可重复生成；M3两个STEP均已回读。
- `CALCULATED` C04-A的4 mm拨叉从名义Ø71 mm POLLEN上方通过90 mm开口时剩余15 mm总间隙；名义Ø91 mm NECTAR比开口高1 mm，控制与几何均排除底部取NECTAR。
- `CALCULATED` Ø60 mm roller在80–160 rpm FLOWER模式表面速度为0.251–0.503 m/s；10 N假设回拉力对应0.30 N·m轴矩和约1.38 A线性模型电流。
- `CALCULATED` 10 N、80 mm力臂和2.0结构安全系数要求1.6 N·m拨叉校核力矩；0.5 N/mm×20 mm串联弹簧把刚性接触限制在约10 N。
- `CALCULATED` 两电机差速相对当前底盘释放2端口/移除874 g电机，但理想峰值轴功率和电机限制牵引力均减半；C04-A共享动力已使换底盘不再是释放shooter端口的必要条件。
- `KNOWN` G418规则门槛已用于区分侧向运动与侧面出口：C04-B1必须在球完全离开FLOWER前保持于底部Retrieval Opening边界；C04-B2不进入设计。
- `CALCULATED_IDEAL_STEP` 名义Ø71 mm球跨越13 mm理想环唇需要27.46 mm水平行程，初始无摩擦水平推力为球重的1.22倍；20–30°工作面提供13 mm抬升需要26.00–38.01 mm理想路径。
- `CALCULATED_FROM_ASSUMED_LOAD` C04-B1按10 N、70 mm力臂和2.0安全系数校核为1.40 N·m；不增加直流电机，名义使用1个专用舵机。
- `MEASURED_FROM_CAD` SRC-016 Retrieval Opening净高90.170 mm；13 mm抬升后Ø71 mm球对上球托仍有6.120 mm名义间隙。
- `REJECTED_GEOMETRY` 纯−X横移对短支柱净空−5.437 mm，最大实体交叠590.763 mm³；不得继续作为候选路径。
- `SIMULATED_NOMINAL` 25°斜向路径支柱解析余量3.680 mm，球/拨片/roller名义实体交叠均为0；仅批准M3初模，不代表实物通过。
- `CALCULATED_FROM_USER_SPEC` 目标舵机6/7.4 V堵转力矩为0.549/0.608 N·m；6 V、80%效率、50%堵转运动边界要求3.187:1，选3.2:1后名义10.04 N、144.1°、0.103 s无负载下界。

## OPEN QUESTIONS

无未关闭 CRITICAL 信息项。

项目时间表、预算、命中率/周期目标、软件栈和维护目标仍为IMPORTANT。C04-A/B1都需要实际POLLEN尺寸、FLOWER夹具和取出力；B1还需目标舵机型号/尺寸/实际行程以及REV电源瞬态能力。它们阻塞M4详细CAD，不阻塞1:1夹具。

## KNOWN PROBLEMS

- 规则仅为 TU01；后续 Team Update 可能改变阈值或合法性要求。
- 底盘轮距/轴距及底盘、电机、Control Hub 代理包络尚未从 STEP/实物测量，不能用于尺寸承诺。
- 缺少性能目标、时间表和预算。
- TS-S00-001 v0.2 的战略输入来自规则，但工程评分仍是证据锚定的假设，不是测量；不能用来预测比赛成绩或冻结最终机构。
- FTC 先例多来自不同赛季和不同形状物体，所有机构原则必须针对 BIOBUZZ 重新验证。
- P3 真空弹道未包含轻质开孔球的阻力、Magnus 效应、球体变形或动态 HIVE；结果只作为台架起始窗口。
- 还没有实物球质量、轮速—球速传递系数、命中散布、连续射击恢复和温升数据。
- C06-B配合C04-A共享intake/prefeed动力后使用7个电机并保留1端口；该余量尚未分配。相对C06-A至少增加的396 g只含电机，不含第二轮组、支架和护罩。
- FLOWER 名义尺寸为约数且场地存在制造变化；5.25 mm NECTAR 顶口径向余量不足以支持未测量的可靠性承诺。
- C04-A的40 mm拨叉宽度、70–105 mm伸入范围、12 mm落钩和10 N限力均为原型参数，不是制造尺寸；必须从官方STEP/实体夹具验证管件和环避让。
- C04-B1的20–30°工作面、40–70 mm侧扫、10 N限力和单舵机假设均为原型参数；完整球体若穿越FLOWER侧边界即违反方案定义，理想台阶计算不能替代STEP与实物证明。
- C04-B1 25°路径只有3.680 mm名义支柱余量，不能覆盖未知场地公差、球非圆度或机器人对位误差；初模没有舵机真实外形、安装架、轴承、导板、传动件和制造公差。
- 单电机共驱roller与短预输送可能在闸门关闭时压缩球列；需要打滑张紧、舵机离合或其他卸载设计和混合球循环试验。
- 定时上传依赖本机在线、GitHub 凭据有效且当前任务可运行；认证、验证、远程领先或分叉时自动化将停止上传并请求人工处理。

## ASSUMPTIONS

- ASM-005：默认战略总权重 70%，工程评分在无台架数据时采用规则/几何锚定判断，并用 60%–80% 敏感性检查。
- ASM-006..008：P3 采用真空弹道、0.65 轮面传递比及 0.75–2.0 m/50–60° 参数扫参，均待 L3/L6 证据替换。
- P3-LAUNCHER-CMP-0.3的无滑移双平面接触模型只用于证明拓扑运动学；实际球速、自旋和散布必须按方案分别实测。
- T04-INTAKE-0.1采用10 N原型限力、4 mm拨叉、60 mm roller和80–160 rpm FLOWER速度；均须由L3/L6替换或确认。
- ASM-009：SRC-016已把C04-B1收敛到25°斜向、60 mm拨片行程/120 mm球验证行程；名义几何关闭，实体摩擦/公差/堆载待VAL-T04-005。
- ASM-010：目标舵机按6 V、3.2:1、80%传动效率和50%堵转运动边界推进；7.4 V未默认批准。
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
- `docs/p3_launcher_comparison.md`
- `calculations/p3_launcher_comparison.py` / `p3_launcher_comparison_results.csv`
- `tests/test_p3_ballistics.py`
- `docs/t01_drive_trade_study.md`
- `calculations/t01_drive_trade_inputs.json` / `t01_drive_trade.py` / `t01_drive_trade_results.csv`
- `tests/test_t01_drive_trade.py`
- `docs/t04_intake_concept.md`
- `docs/t04_intake_side_sweep_trade.md`
- `calculations/t04_intake_inputs.json` / `t04_intake.py` / `t04_intake_results.csv`
- `tests/test_t04_intake.py`
- `calculations/t04_flower_sweep.py` / `t04_flower_sweep_results.csv`
- `tests/test_t04_flower_sweep.py`
- `cad/modules/t04_intake/side_sweep_intake.py`
- `cad/modules/t04_intake/model_manifest.json`
- `.gitignore`

## LATEST DESIGN VERSION

Framework v0.7.0；Requirements v0.1 APPROVED；Architecture v0.1 APPROVED；T01-DRIVE-TRADE-0.1；T04-INTAKE-0.3 / T04-INTAKE-CMP-0.2；T04-C04B1-M3-0.1 PRELIMINARY；P3-M1 v0.2 ACTIVE；P3-LAUNCHER-CMP-0.3。

## NEXT ACTION

取得目标舵机型号、外形尺寸和可用行程；制作透明1:1 FLOWER底部夹具，以25°为中心加入可调角度与横向柔顺，先测实际取出力/峰值电流，再按VAL-T04-005随机比较C04-A/B1。只有实体门槛通过才增加支架、导板和传动细节并进入M4。
