# PROJECT STATUS

最后更新：2026-10-04

## CURRENT OBJECTIVE

按用户最新指令完成 T06/C06-B 官方采购件 CAD 导入，并将电机、舵机等采购总成在工作装配中按「每个 SKU 的整个官方部件」处理（多实体保持多实体，不做布尔并集，DEC-0021）；下一步用实物关闭轴向紧固与高速动态风险。

## CURRENT MODULE

当前工作对象是 Architecture v0.1 的 T06/C06-B 主发射原型；回滚后的 `paddle_launcher_constrained.py` 已升级为 `C06B-COTS-0.3`。T04、T05、T07 和 KEI-16 历史均保留，未被本次修改覆盖。

## CURRENT DESIGN MATURITY

S00：M0通过。T06：C06-B维持 M3 COTS-CONSTRAINED PACKAGING；目录映射、13 个官方 STEP 回读、每 SKU 整体部件表示（多实体保持多实体）、轴向名义计算和端点干涉已通过，实物公差与旋转测试未关闭。KEI-16导入参考和T04 C04-B1维持各自M3状态；T05为M1共享动力接口，T07为M0增量研究。

## COMPLETED

- `C06B-COTS-0.1` 已淘汰 Ø38 无 SKU 电机夹具、16 × 7 mm 轴承、194 mm 轴和无 SKU 联轴器占位，替换为 goBILDA `5203-2402-0003`、`1401-0043-0036`、`4007-4008-4008`、`2106-4008-1680` 和 `1611-0514-4008`。
- 双飞轮轴继续各自直驱，外置齿轮数量为0；两台电机统一移至−Y侧，+Y双连杆调隙侧保持无遮挡。
- 侧板改为8.4 mm轴槽（17.4 mm总长），轴承留在外置滑座；POLLEN/NECTAR两端点的COTS干涉检查通过。
- `C06B-COTS-0.3` 已下载、哈希登记并保留 13 个 goBILDA 官方 STEP；工作装配按 DEC-0021 把每个采购 SKU 的整个官方部件带入装配（9 个多实体、4 个单实体），布尔并集链已按实测否决并退役，原始供应商多实体文件不被覆盖。
- 官方 CAD 回读关闭了先前电机、夹具、联轴器和舵机包络假设；按整体官方部件几何回读，总包络更新为约 383.849 × 364.776 × 400.024 mm。
- 修正送料支撑颊板轴孔误切在 Y=0 的穿模缺陷；孔现分别与 Y=±62 mm 颊板和送料轴同心。
- T06 报告 16/16 检查通过（含新增“未对任何采购件执行布尔并集”检查）；13 个采购件工作模型按 DEC-0021 整体带入，9 个多实体、4 个单实体；项目自动测试 40/40 通过。
- `tools/inspect_geometry.py` 几何检验达到全通过：`R004` 共 77 项（23 项规格检查 + 54 项逐 SKU 整体部件检查）全部 `pass`，0 `fail`、0 `unresolved`，退出码 0，用时 1483 s；报告见 `cad/output/inspection/t06_launcher_R004.json`。
- `R003` 暴露的 3 项 `unresolved` 根因是 `gecko_flywheel_*`、`sonic_hub_*`、`bearing_insert_*` 三类采购件的装配命名未携带 SKU，自动检查按 SKU 匹配落空（顺带导致 `1908-0025-0032` 只被检查到一个放置位）；已把 SKU 补进这三类命名并同步更新规格引用，自动检查由 33 项增至 54 项，每个 SKU 的全部放置位都被覆盖。
- 几何检验工具按 `AI_Long_Running_Process_No_Output_Guide.md` 改造：阶段日志、20 s 心跳、`--progress-file` 进度文件与显式 flush，STEP 回读检查细分导出/回读/比对子阶段，使长时间无输出的运行可被判为 ACTIVE 而非卡死。

- `KEI16-FLIPOUT-COTS-0.2` 已把占位传动替换为 goBILDA/REV COTS 规格：312 rpm 单电机、24T:24T 斜齿轮、两段 14T/38 节链、16T:24T/460 mm HTD5 前轴带路、双弹簧/双棘爪/双硬止挡。
- 新增可复算输入、脚本、结果和6项单元测试；重新生成展开/收纳 STEP、STL、GLB、PNG 与 JSON 报告。
- `DEC-0018` 明确一次性弹出、手动收纳边界，并保留当前 T04 编号和 C04-B1 历史。

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
- 将目标舵机确认为REV-41-3336 Smart Robot Servo V2 - UltraSpeed；核验官方规格、单页尺寸图和STEP，并登记REV-41-1828铝舵盘接口。
- 用严格角度/力双边界比较3.2:1圆弧回退与卷线鼓直线驱动；首轮原型改用17 mm节圆半径单层卷线鼓，保留已验证的60 mm直线路径。
- 生成三件可打印验证件：舵机夹持/开式导轨支架、卷线鼓和25°楔形滑块；同时生成组合STEP、预览、清单和制造边界说明。
- 以REV-41-3336官方STEP替换代理舵机，加入REV-41-1828官方舵盘，并按官方4×Ø4.5孔位重建支架；输出保留5个命名组件的Fusion 360装配STEP。
- 导入并保留单电机翻转 Intake、连续 feeder 和 launcher 的参数化 CAD/STEP/STL/GLB/PNG/JSON 参考资产；其中翻转 Intake 以视频可见结构为证据，20T:28T、178 mm 翻臂、24T:36T 前轴和部署锁扣均为待实体验证的项目基线，不取代当前 T04 C04-B1 决策。
- 合并 GitHub、Linear 与 Notion 的接手语义：当前架构 Intake 编号为 T04；Linear KEI-16/Notion 页面中的“T02 Intake”保留为导入参考记录，后续 AI 不得混淆为当前 T02 主承力结构。
- 2026-09-27 重新核对本地 `main`、GitHub、Linear KEI-16 和 Notion Intake/System Architecture；未发现新的未同步工程文件或重复事项。README 增加面向未来 AI 的直接启动提示、数据权威顺序、最小验证命令与需要请求实物数据的停止条件。

## VALIDATED

- `CALCULATED` 两段 38 节、14T、8 mm pitch 链的中心距均为 96.000 mm；460 mm HTD5 配 16T:24T 的中心距为 179.887 mm，小带轮啮合 7.82 齿。
- `CALCULATED_FROM_VENDOR_SPEC` 固定 Ø60 roller 空载表面速度 0.980 m/s；前端 73 mm 指尖空载速度 1.590 m/s。
- `CALCULATED_FROM_ASSUMPTIONS` 双弹簧在收纳/展开端提供 2.146/1.852 N·m 部署力矩；REV锁扣舵机静态解锁估算仅需其6 V目录堵转扭矩的5.6%。
- `VALIDATED_GEOMETRY` 新版展开/收纳 CAD 均成功导出；包络约 451.58 × 444.00 × 224.71 mm 和 320.97 × 444.00 × 269.01 mm，当前方向几何筛查通过。
- `VALIDATED_CALCULATION` `tests/test_kei16_flipout_drive.py` 6/6 通过；所有注册设计检查为 true。

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
- 项目单元测试现为40/40通过；T01/T04生成CSV与脚本可重复生成；相关 M3 STEP均已回读。
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
- `CALCULATED_FROM_VENDOR_SPEC` 目标舵机6/7.4 V堵转力矩为0.549/0.608 N·m；70 mm圆弧回退在6 V、80%效率、50%堵转运动边界要求3.187:1，3.2:1可提供10.04 N；60 mm端点弦长需舵机162.41°、理想无负载0.116 s，但有6.75 mm弓高偏差。
- `KNOWN_VENDOR_VERIFIED` 目标舵机为REV-41-3336：默认270°、可编程最大280°、500–2500 µs、25T、中心M3×0.5最大6 mm深；官方STEP回读1实体且总包络20.151 × 43.550 × 54.000 mm。
- `CALCULATED` 17 mm卷线鼓完成60 mm直线行程需要202.220°；居中端点751.0/2249.0 µs；6 V理想无负载时间0.145 s。可行半径区间为12.73–19.10 mm。
- `CALCULATED_FROM_ASSUMPTIONS` 6 V、80%效率、50%堵转、1.5 N回位载荷下，17 mm卷线鼓可提供11.42 N外载；短时结构边界24.34 N，分别超过10/20 N原型门槛。
- `VALIDATED_GEOMETRY` 三个打印件STEP均回读为单一有效实体；组合STEP为5实体；三个STL均为封闭流形，边界边/非流形边计数为0。
- `VALIDATED_ASSEMBLY` Fusion 360 STEP回读5个有效实体、190 × 85 × 45 mm包络；保留支架、官方舵机、官方舵盘、卷线鼓和拨片5个产品名称；非配合件两两实体交叠为0。

## OPEN QUESTIONS

无未关闭 CRITICAL 信息项。

项目时间表、预算、命中率/周期目标、软件栈和维护目标仍为IMPORTANT。KEI-16还需底盘/T05接口、轴向堆叠、弹簧料号、打滑器结构和实测堵转/碰撞数据；C04-A/B1仍需实际POLLEN尺寸、FLOWER夹具和取出力。两条分支均未达到M4冻结条件。

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
- 新验证支架是官方孔位舵机安装+开式重力导轨，适合低成本台架，不具备整机姿态保持、护罩或最终机器人安装接口；不得直接作为比赛零件发布。
- 17 mm卷线鼓计算假设单层、不打滑和1.5 N最大回位载荷；绳叠层或弹性会改变实际行程/输出力，必须用机械止挡和实测关闭。
- 单电机共驱roller与短预输送可能在闸门关闭时压缩球列；需要打滑张紧、舵机离合或其他卸载设计和混合球循环试验。
- 定时上传依赖本机在线、GitHub 凭据有效且当前任务可运行；认证、验证、远程领先或分叉时自动化将停止上传并请求人工处理。
- 平铺 `cad/*.py` 与 `cad/output/` 中包含导入的参考/早期设计资产；它们尚未映射到 `config/parameters.yaml` 和当前模块接口，不能仅因已生成 CAD 就视为 Architecture v0.1 已采用。
- KEI-16的3.4 A/200 ms保护、0.8 ±0.1 N·m打滑、15–30 N/侧弹簧和250 N/侧硬止挡均是台架起始假设；没有 `MEASURED` 证据前不得发布制造图。
- KEI-16 CAD总宽444 mm距457.2 mm包络只剩约13.2 mm总余量，尚未计入全部真实紧固件、护罩和公差。

## ASSUMPTIONS

- ASM-005：默认战略总权重 70%，工程评分在无台架数据时采用规则/几何锚定判断，并用 60%–80% 敏感性检查。
- ASM-006..008：P3 采用真空弹道、0.65 轮面传递比及 0.75–2.0 m/50–60° 参数扫参，均待 L3/L6 证据替换。
- P3-LAUNCHER-CMP-0.3的无滑移双平面接触模型只用于证明拓扑运动学；实际球速、自旋和散布必须按方案分别实测。
- T04-INTAKE-0.1采用10 N原型限力、4 mm拨叉、60 mm roller和80–160 rpm FLOWER速度；均须由L3/L6替换或确认。
- ASM-009：SRC-016已把C04-B1收敛到25°斜向、60 mm拨片行程/120 mm球验证行程；名义几何关闭，实体摩擦/公差/堆载待VAL-T04-005。
- ASM-010：REV-41-3336按6 V、17 mm卷线鼓、80%传动效率、50%堵转运动边界和≤1.5 N回位载荷推进；3.2:1圆弧方案只作回退，7.4 V未默认批准。
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
- `calculations/kei16_flipout_drive_inputs.json` / `kei16_flipout_drive.py` / `kei16_flipout_drive_results.json`
- `tests/test_kei16_flipout_drive.py`
- `tests/test_t04_flower_sweep.py`
- `cad/modules/t04_intake/side_sweep_intake.py`
- `cad/modules/t04_intake/model_manifest.json`
- `cad/modules/t04_intake/flower_side_sweep_prototype.py`
- `cad/modules/t04_intake/prototype_manifest.json`
- `exports/step/t04_c04b1_*capstan*_m3.step` / `*paddle*_m3.step` / `*bracket*_m3.step`
- `exports/step/t04_c04b1_fusion360_assembly_m3.step`
- `exports/stl/t04_c04b1_*_m3.stl`
- `exports/drawings/t04_c04b1_capstan_fixture_m3_preview.png`
- `.gitignore`
- `cad/README.md`、`cad/*.py`、`cad/output/*` 和 `docs/engineering/*`（2026-09-24 导入参考基线）

## LATEST DESIGN VERSION

Framework v0.7.2；Requirements v0.1 APPROVED；Architecture v0.1 APPROVED；T01-DRIVE-TRADE-0.1；T04-INTAKE-0.4 / T04-INTAKE-CMP-0.3；T04-C04B1-M3-0.3 FUSION360 ASSEMBLY VALIDATED；KEI16-FLIPOUT-COTS-0.2 M3 PACKAGING/CALC VALIDATED；C06B-COTS-0.3 M3 OFFICIAL-CAD-DERIVED WHOLE-OFFICIAL-PART PACKAGING VALIDATED（候选，待人工接受）；P3-LAUNCHER-CMP-0.3。

## MOTION-ONLY SIMULATION EXTRACT?2026-10-02?

- ????????????????????????????????? + ? + ??????????? + ???????????????????????
- ?? `cad/paddle_launcher_motion_only.py`??? `paddle_launcher_constrained.build()` ???????????????????????????????????? 2026-10-02 ???????????????????
- ?????????? `.gitignore` ???????`cad/output/paddle_launcher_motion_only_nectar.step/.stl`?`paddle_launcher_motion_only_pollen.step/.stl`????? `cad/output/paddle_launcher_motion_only_report.json` ? `paddle_launcher_motion_only_nectar_overview.png`?
- ???????? 30 ???? 68 ??185 ????POLLEN ?? 266.3 ? 364.8 ? 312.5 mm?NECTAR 273.4 ? 364.8 ? 318.1 mm?? 160/178 mm ????????
- ???POLLEN?MEASURED????? 185 ??????????????? 0.009 mm?????????? 383.849 ? 364.776 ? 400.024 mm ??NECTAR ?????????????? `not_run`?
- `paddle_launcher_feasible_*` ??????????????

## MOTION VERSION EXTRACT（运动版，2026-10-03）

- 用户要求出「运动版」：去除马达、舵机、轮毂（Sonic hub）与联轴器，只保留拨杆（paddle rotor）和飞轮（Gecko flywheel），并加回小球从拨杆到飞轮的斜坡（与原文件逐件完全一致）；同时去掉拨杆周围的三根轴。
- 三根「轴」经几何判定为 `paddle_hinge_1/2/3`：每根 10 mm x 100 mm 销轴，半径 r = 46.0 mm、相位 138° / 258° / 18°，与用户截图量测的圆环位置一致（KNOWN）；本轮一并剔除。
- `cad/paddle_launcher_motion_only.py` 新增 `--profile motion_free` 档案（另有 `--no-shafts`、`--with-fingers`）。依旧复用 `paddle_launcher_constrained.build()`，逐件复制已定位实体、不重新求解位置，故相对物理位置与原文件一致。
- 产物（KNOWN，2026-10-03 12:47–12:51）：
  - `cad/output/paddle_launcher_motion_free_pollen.step` (169.5 MB) / `.stl` (728.1 MB)
  - `cad/output/paddle_launcher_motion_free_nectar.step` (169.6 MB) / `.stl` (728.0 MB)
  - `cad/output/paddle_launcher_motion_free_report.json`
- 筛选结果：保留 31 件 / 剔除 67 件，共 38 实体。保留清单为 `gecko_flywheel_*` x4、`flywheel_shaft_*` x2、`paddle_hub`、`paddle_arm_*` x3、`paddle_blade_*` x3、`paddle_flex_tip_*` x3、送料轴 `paddle_shaft_2106-4008-1920`、`guide_floor_*` x3、`guide_roof_*` x3、`guide_wall_*` x6、`shooter_throat_*` x2。
- 包络（CALCULATED）：POLLEN 313.352 x 192.115 x 318.275 mm；NECTAR 320.444 x 192.115 x 323.816 mm。Y 向由 364.8 mm 缩至 192.1 mm，因为支撑侧板与底轨已去除，只剩导槽（宽 114 mm）与轴（长 192 mm）。
- STL 二进制头三角形数：POLLEN 15,268,330 / NECTAR 15,267,968，均与文件长度精确吻合（MEASURED）。
- 回读校验脚本 `tmp/verify_motion_free.py`（临时，未入库）。
- `paddle_launcher_feasible_*` 与 `paddle_launcher_motion_only_*` 时间戳未变，原文件未被覆盖。
- `.gitignore` 已追加忽略 `cad/output/paddle_launcher_motion_free_*.step/.stl/.glb`。

## MOTION VERSION + BACKFLOW FINGERS（2026-10-03 追加）

- 追加导出含止回指的版本（`--with-fingers`）：`cad/output/paddle_launcher_motion_free_fingers_{pollen,nectar}.step/.stl` 与 `paddle_launcher_motion_free_fingers_report.json`；保留 33 件 / 40 实体，包络与不含指版本一致（指件落在原包络内）。STL 三角形数 15,268,354（POLLEN）/ 15,267,992（NECTAR），与文件长度吻合。
- 止回方式（KNOWN）：52 度导槽入口的两片单向弹性指 `one_way_finger_+1 / _-1`，位于 Y = ±38 mm，各为 38 x 1.2 x 44 mm 板片、绕 -52 度贴合斜坡（`cad/paddle_launcher_constrained.py:302-307`）。小球上行时需挤开两指，反向被指端拦住。
- 材料决策（`docs/decision_log.md` 的 DEC-0022，ASSUMED）：实物按**标准尼龙扎带（zip tie，尼龙 6/6）**实现，仿真以悬臂薄片建模。参数记入 `config/parameters.yaml` 的 `materials.backflow_finger`：E = 2.7 GPa、nu = 0.39、rho = 1150 kg/m3、截面 4.7 x 1.14 mm，全部为 ASSUMED 通用取值，采购后须实测替换，不得据此发布结论。
- 待验证（TBD）：两指内表面净距 74.8 mm —— POLLEN 球（名义 71 mm）约余 3.8 mm，NECTAR 球（名义 91 mm）约过盈 16 mm；指端是否真正拦到两种球的包络尚未确认，须在 T03.2 台架验证。

## T06 POLLEN 送球段 V2 重做（2026-10-03）

- 用户指令（KNOWN）："进行重做吧。拨杆，外罩按照你的设想进行调整，使其保持同轴度，与倾斜托板适配"；硬约束为不得覆盖原文档、且先生成示意图。示意图已出（`simulation/mujoco/out/redesign_v2_overview_zh.png`、`redesign_v2_feed_zh.png`、`redesign_v2_coax_zh.png`，生成脚本 `simulation/mujoco/_work/redesign_v2_sections_zh.py`）。
- 生成器（新增）：`cad/paddle_launcher_feeder_redesign.py`，复用父级 `paddle_launcher_constrained.build()` 后逐件保留/剔除/挖空，再合成新的送球段零件；**父模块一行未改**。
- 关键改动（CALCULATED）：外罩圆弧以**拨杆轴 C = (29.49, 0.0, 111.46) mm 为圆心**直接画出，并把 5° 倾斜托板与唇口连接筋并入**同一条闭合 XZ 轮廓**，再沿 Y 挤出 108 mm —— 外罩、托板、拨杆三者同轴是**构造事实**，不再依赖装配公差。
- 几何基准（CALCULATED）：球心轨迹 R58.40；外罩内壁 R93.96 / 外壁 R100.96（壁厚 7）；扇形 142° → 225°；托板 X −56 → 150 mm、厚 6 mm、倾角 5°。
- 出口校核（MEASURED）：出口 142° 球心 (−16.53, 147.415)，到 52° 地板线 55.0022 mm，通道中线 55.00 mm → **偏差 0.0022 mm，`pass`**。
- 进料与止回（CALCULATED）：入口到停位落差 13.326 mm，托板自滚 206 mm、落差 18 mm，落位速度约 0.43 m/s；停位球心 (−2.30, 53.06) 到唇口 35.57 mm ≈ 球半径 35.56 mm（楔紧自锁）。
- 产物（KNOWN）：`cad/output/paddle_launcher_motion_free_pollen_v2.step`（169.4 MiB / 177,628,316 B，30 实体）、`.stl`（537.1 MiB）、`paddle_launcher_motion_free_pollen_v2_report.json`。父级 `paddle_launcher_motion_free_fingers_pollen.step` 及其余既有导出时间戳未变，原文档未被覆盖。
- STEP 回读（MEASURED，`n_solids = 30`）：包围盒 281.773 × 192.0 × 325.964 mm，与报告完全一致；总体积 970,754.4 mm³；外罩＋托板单体 255,347.1 mm³（报告 255,347.07）且 Y 向 ±54 mm = 108 mm 宽。
- 干涉（MEASURED）：新外罩 vs `guide_floor_3 / guide_roof_3 / guide_wall_3_±1` 全为 0；拨杆扫掠包络 vs 喉道/外罩/导板全为 0（扫掠尖角半径 62.362 mm < 鼓半径 63 mm）；停位球 vs 全部保留零件全为 0。
- 更正上一轮记录（KNOWN）：先前报告的 `guide_wall_3_-1` 2133 mm³ 干涉是当时外罩挤出方向写错造成的**误报**，本轮实测为 0，侧板不必删除。
- 删除清单：`guide_floor_1/2/3`、`guide_roof_1/2`、`guide_wall_1_±1`、`guide_wall_2_±1`、`one_way_finger_±1`；`shooter_throat_-55` 被拨杆扫掠鼓挖空至体积归零而自动丢弃。保留 23 件，含 `guide_roof_3`、`guide_wall_3_±1`、`shooter_throat_+55`。
- 决策（`docs/decision_log.md`）：DEC-0023（同轴构造化、外罩与托板合并为单一零件）、DEC-0024（删 52° 地板与两片止回指，止回改由 5° 自滚 + 唇口楔紧承担；取代 DEC-0022 中止回指作为 V2 零件的用法，zip-tie 材料记录保留为历史）。参数记入 `config/parameters.yaml` 的 `t06_feeder_v2`。
- 待验证（TBD）：V2 是否真能把球送进 52° 夹口并被对置双飞轮发射 → 已由本轮全流程仿真关闭，见下节。

## T06 POLLEN 送球段 V2 全流程仿真（2026-10-03）

- 用户指令（KNOWN）：好，跑新版全流程仿真吧。
- 方法（SIMULATED）：新增 `simulation/mujoco/pollen_v2_sim.py`（几何常量取自 `cad/paddle_launcher_feeder_redesign.py` 与 V2 报告，不依赖 CadQuery）；MuJoCo 3.14.0，timestep 2e-4 s，implicitfast，外罩以 24 段 box 链近似曲面。
- 结论（SIMULATED）：**V2 几何具备完整送球—发射能力**。球从托板右端滚入 → 叶片在 x ≈ 113 mm 接球 → 沿内壁 241° → 142°（约 99°）→ 142° 切向出罩（球心距 52° 通道中线 ≈ 4 mm）→ 进夹口 → 出射 **6.53 m/s @ 50.2°**，同高度射程 **4.28 m**（飞轮 1620 rpm，拨杆 200 rpm）。旧几何的 52° 顶板卡点未复现。
- 发射阶梯（SIMULATED）：810 / 1620 / 2430 rpm → 3.60 / 6.53 / 8.67 m/s，射程 1.29 / 4.28 / 7.49 m；出口速度/轮缘线速度 = 0.80，与 V1 的 `FINDINGS_zh.md` 一致 → V2 未损失发射性能。
- 拨杆转速门槛（SIMULATED，本轮关键新发现）：球已在唇口停位时 ≥ 105 rpm（100 rpm 卡在 182°）；球从托板进料时 140 rpm 仅 2/8 成功、**200 rpm 8/8 成功** → **推荐拨杆 ≥ 200 rpm（3.3 rev/s）**。
- 风险（ASSUMED，必须关闭）：拨杆力矩用 forcerange ±1.5 N·m 的速度执行器近似，是转速门槛结论的最大不确定来源；叶片按刚体建模，未含 zip-tie 弹性。舵机在 200 rpm 处的可用扭矩未经确认前，不得把送球可靠性写入制造结论。
- 产物（KNOWN）：`simulation/mujoco/out/FINDINGS_v2_zh.md`、`v2_fullflow_zh.png`、`v2_flywheel_ladder_zh.png`、`trace_v2_*.json`、`summary_v2_*.json`。父级 CAD 与既有导出均未改动。

## T06 POLLEN V2 舵机选型校核与接触几何分析（2026-10-03）

> （SUPERSEDED by DEC-0026 — 以下内容为 7 s 预算下的旧口径，保留供上溯，不作为当前结论。）


- 用户指令（KNOWN）：核对 REV SRS V2 舵机规格是否满足 V2 送球段要求；若不满足，给出改善接触几何的方法。
- 舵机规格（KNOWN，用户提供规格图）：SRS V2 Balanced 6 V / 7.4 V → 13.5 / 16.7 kg·cm，0.14 / 0.12 s/60°；SRS V2 UltraSpeed 6 V / 7.4 V → 5.6 / 6.2 kg·cm，0.043 / 0.035 s/60°。换算 @7.4 V：Balanced 堵转 1.638 N·m、空载 83.3 rpm；UltraSpeed 堵转 0.608 N·m、空载 285.7 rpm。
- 送球需求（SIMULATED，本轮实测）：拨杆力矩门槛 ≈ **1.0 N·m**，且在 140–200 rpm 区间**基本不随转速变化**（105 rpm 即使给 1.5 N·m 也不发射，属转速受限，不是 torque 受限）→ 该需求是"球被夹住后的起步/突破力"，不是惯性力。
- 峰值扭矩（SIMULATED）：200 rpm 自由跑峰值 1.71 N·m，恰等于执行器 `kv·ω = 0.08 × 20.94 = 1.675`，即**拨杆在接球瞬间被完全卡停**；峰值与叶尖形状无关（5 种叶尖方案实测 1.69–1.72 N·m），说明缩短叶尖不能降低需求。
- 卡停机理（SIMULATED，接触对实测）：球在停位仅由 `tray` + `shell_lip_face` 支撑（V 形硬窝，球底距托板仅 0.07 mm）；峰值帧球同时接触 `paddle_blade`、`paddle_flex`、`tray`、`shell`、`shell_lip_face`、`strut` → 球被"叶片 + 固定件"多面夹持。
- 判定（CALCULATED）：**两型号均不满足直接驱动**。Balanced 扭矩够（1.638 > 1.0，余量 1.6×），但在该扭矩下转速仅约 22 rpm，远低于 105 rpm 下限；UltraSpeed 转速够（286 > 105），但堵转 0.608 < 1.0。所需机械功率 ≈ 1.0 N·m × 105 rpm ≈ 11 W（200 rpm 时 ≈ 21 W），该级别舵机理论极限（堵转 × 空载）仅 14–18 W、可用值约 5 W → 单只 SRS V2 无法直接驱动该送球段；需求点落在舵机扭矩—转速线段之外，减速比也无法解决。
- 改善接触几何方案（ASSUMED，待仿真验证）：A 225° 挡墙改斜楔/圆弧过渡，让球平滑导入外罩；B 托板末端缩进 10–15 mm 并下倾，使球窝下方让空；C 叶片前缘卸载（球还在托板上的 300°–330° 区段外缘半径 ≤ 58.4）+ 端角倒圆；D 球窝改单侧斜坡"逃逸窝"，只留托板 + 与出球方向相切的斜面。
- 产物（KNOWN）：`simulation/mujoco/out/servo_verdict_zh.png`、`contact_fix_options_zh.png`、`summary_v2_torque_detail.json`、`summary_v2_servo_req.json`、`summary_v2_blade_variants.json`。

## T06 POLLEN V2 送球门槛重测与舵机选型（2026-10-03，DEC-0026 口径）

> 本节结论取代下方早先的「T06 POLLEN V2 舵机选型校核与接触几何分析（2026-10-03）」段落；该段落基于 7 s 仿真预算，混入了送料耗时假象，其原结论已标 SUPERSEDED 保留供上溯。

- 口径修正（KNOWN）：送球门槛仿真预算由 7 s / 单入口 x=145，统一改为 **12 s / 双入口 x=145 与 x=138**（取较坏值），二分容差 ±0.03 N·m。
- 修正原因（SIMULATED）：7 s 预算下 30/40/60/70/75/145 rpm 即使给到 3.0 N·m 也判失败；延长到 12 s 后全部成功发射。机理是**球在球窝蠕动**——球停在球窝边缘 r≈83–95.5 mm（θ≈322–328°），要等指片转到才被抓住，70 rpm 首抓约 4.2 s。旧门槛把送料耗时混进了发动力矩。
- R5 门槛（SIMULATED，`simulation/mujoco/out/_r2r5_speed_req12.json`，单位 N·m）：40/50 ≤0.24（扫描下限）、60 → 0.339、75 → 0.439、90 → 0.24、105 → 0.24、120 → 0.289、130 → 0.356、**145 → 0.472（最坏点）**、160 → 0.323、200 → 0.273、290 → 0.306。
- 几何取舍（SIMULATED）：推荐 **R5**（二指 θ=350/170 + D 球窝垫 6.8 mm）；90/105 rpm 门槛仅 0.24，优于 R2。DEC-0025 的 A 有效 / D 有效 / B 无效 / C 恶化的相对排序保留有效。
- 舵机判定（CALCULATED，7.4 V，厂家堵转值线性插值到空载）：**25-4 Super Speed 0.530 N·m / 290 rpm → 可直驱窗口 30–70、80–122 rpm，推荐**（唯一能上 120 rpm；90–105 rpm 余量 >40%；避开 70–80 rpm 缺口）；25-3 Speed 1.059 / 145 → 30–110；Axon MAX MK2 3.825 / 100 → 30–94（低速余量最大）；25-2 Torque 与 25-2 5-Turn 2.471 / 60 → 30–53（可用但慢，约 1.2 s/球）；REV SRS V2 UltraSpeed 0.608 / 285.7 → 30–125（**此前误判不可行，现同样可用**）。图：`simulation/mujoco/out/servo_envelope_zh.png`。
- 仍开放（TBD）：送球**相位敏感**（相邻 10 rpm 即可翻转结论），拨杆转速必须锁在窗口内稳态运行；根因未解决——球停 r≈95.5 mm 而设计轨道 R=58.4 mm，**差 37.1 mm**，送球靠叶尖拖拽而非输送轨道；R5 尚未进 CAD；刚性（非扎带）指片与 ASSUMED 0.060 kg 球质量仍未验证。

## T06 POLLEN V2 送球段「平滑曲面」优化与蠕动根因（2026-10-03，DEC-0027）

- 用户指令：采用 goBILDA **25-4 Super Speed（0.530 N·m / 290 rpm）** 作送球舵机，尝试把**外罩与球窝垫用平滑曲面连接**，看能否减少球的「蠕动」。
- 新增候选 **R6**（SIMULATED）：取消 R5 的 30×108×12.8 平垫块，外罩内弧（r = 93.96 mm）从 225° 沿同一半径平滑延伸到 **260.2°**，终点与托板顶面在 x = 13.5 mm 处相切（抬升 0.0 mm）。**R5 保留**，两者并列；R6 标为**候选待接受**。两者都仅在 MuJoCo 中，**均尚未进入 CAD**。
- **直接回答：平滑曲面不能消除蠕动。** 抓球前等待 2.98 s → 2.93 s（−1.7%，噪声量级）；全程 7.49 s → 7.38 s（−1.5%）；R6c（弧面止于 256°、半径收窄 2 mm）→ 7.23 s（−3.5%）。三者均**一次通过**全流程，出口球速 6.67 m/s、飞轮 1620 rpm，没有失败工况可区分优劣。
- 判定口径（KNOWN/SIMULATED）：拨杆改用 25-4 的真实线性扭矩—转速模型驱动（kv = 0.017452、限幅 ±0.530、ctrl = 空载 290 rpm），球从托板 x = 145 mm 滚入，12 s 预算。运载段实测：R5 3.95 rpm / 0.523 N·m，R6 4.05 rpm / 0.523 N·m，R6c 4.36 rpm / 0.522 N·m。
- **根因（SIMULATED，独立复测）**：蠕动发生在球停稳后的**停位球窝**——球停在 r ≈ 83–95 mm、角 ≈ 322–329°，被指片楔住，把拨杆拖到几 rpm，约 2.3 s 后楔口松脱才被带入运载轨道。用刚性速度源（±5 N·m 不限幅）复测同一 R5 几何，该段拨杆仍只有约 **6.8 rpm、出力约 1.16 N·m**（球心 r 实测 59.4 mm），说明是**卡滞**而不是「扭矩差一点」。接合处的台阶在该时段根本不参与接触，因此**改接合处形状无效**。
- 产物的图：`simulation/mujoco/out/r5_vs_r6_smooth_zh.png`（4 面板：R5 剖面 / R6 剖面 / 接合处放大 / 结果表与结论）；脚本 `_work/r6_fig_zh.py`、`_work/r6_motor.py`、`_work/r6_summary.py`、`_work/r7_loadprobe2.py`；数据 `out/_r6_summary.json`、`out/_r6_fig_data.json`。
- **重新打开的开放项（TBD）**：DEC-0026 的 `paddle_torque_threshold_12s_by_rpm`（90/105 rpm ≤ 0.24 N·m）由 kv = 0.08 的假执行器取得，其中「通过」只表示在限幅内 12 s 跑完，**不等于**真实电机有相应扭矩余量；25-4 全油门模型下运载段出力 0.523 N·m 已贴 0.530 N·m 堵转，**余量很薄**。两种口径不可直接相除比较，但都指向「运载段余量薄」→ 舵机余量复核重开。卡滞力矩对接触正则化与到达相位敏感（同一几何 0.52 与 1.16 N·m 两个读数），绝对值只能当量级参考。

## T06 POLLEN V2 球摩擦系数估算与送球能力判定（2026-10-04，DEC-0028）

> 本节结论将上方「R5 可行」限定在 μ≥1.0 的假摩擦输入下，并指出实物磨擦下 R5 送球失败。

- 用户指令（KNOWN）：塑料球是光面的，外罩是一般 3D 打印层高 0.4 mm 的 PET，估摩擦系数后跑仿真。
- 摩擦取值（**ASSUMED**）：μ = **0.40**，合理区间 **0.30–0.50**。依据：光面塑料对光面塑料干摩擦 μ≈0.2–0.3；FDM 0.4 mm 层高在 45° 壁面上形成峰谷 0.1–0.2 mm 层纹，把表观 μ 抬到 0.35–0.55；对本设计而言最坏情况是低端 0.30。**未台架实测前不得升为 MEASURED。**
- 口径（SIMULATED）：R5 几何 + 托板延长到 x=185 mm 、止挡板 x=188 mm（避免球被弹出后丢失），球从 x=145 mm 自然入料，飞轮 1620 rpm，拨杆 25-4 真实线性模型（kv=0.017452，限幅 ±0.530 N·m），**20 s** 预算。
- **结果：实物摩擦下送球失败。** μ=0.40/0.50/0.60 均**未发射**；μ=0.70 才能发射但要 15.69 s且拨杆只有 3.3 rpm（≈堵转）；μ=0.80/1.00 分别 8.54 s / 7.50 s。**门槛 μ ≈ 0.65 ≈ 实物取值的 1.6倍。**
- 失败机理（SIMULATED）：球从 x=145 滚到 **r≈95.9 mm**（t=0.328 s）时，只能被 **paddle_flex 指尖**（半径 58 mm）擦打——接触点在指尖末端，是掠过式撞击而非铲起。低 μ 时球被弹回，在 x≈100–150 mm / r≈86–128 mm 之间来回摆动，永远接近不了设计运载半径 58.4 mm；μ=1.00 时同一撞击被“咬住”，t=2.088 s 时球心已到 r=56.0 mm 并进入运载。这就是 DEC-0025 记录的 **37.1 mm 半径差**的直接影响。
- 飞轮发射能力（SIMULATED）：μ=0.70–1.00 下出球速度 6.35–6.67 m/s、角度 50.6–52.6°，**几乎不随摩擦变化**；逐对摩擦模型（飞轮保留自身高摩擦， priority=2）与全局 μ=0.40 逐位相同 → **瓶颈 100% 在送球段，不在发射轮**。
- 误差记录（KNOWN）：第一版止挡板放在 x=153 mm，球心在 x=145 mm 时球尾已到 x≈180.6 mm，挡板在 t=0 贯穿球导致该批数据不可用；已用正确口径重跑，新口径包含 t=0 无接触自检（`t0_contacts=tray`）。
- 产物：图 `simulation/mujoco/out/r9_mu_verdict_zh.png`（3 面板：剖面判定 / 球走向 / 摩擦门槛）；脚本 `_work/r9_strike_zh2.py`、`_work/r9_clean.py`、`_work/r9_diag.py`；数据 `out/_r9_clean.json`。
- **新增开放项（TBD）**：(1) 台架实测球对打印外罩的摩擦系数（不测就无法把 μ 从 ASSUMED 升级）；(2) 送球段几何改为「把球停位抬到 r≈58.4 mm 运载半径」，让叶片用法向力推球；(3) 即使拖拽成功运载段也只有 3.3–8.5 rpm / 卡滞 76–77%，舵机余量复核（DEC-0027 已重开）仍未关闭。

## T06 共用送球段 R26：一套机构兼容两种球（2026-10-04，DEC-0030）

- 用户指令（KNOWN）：NECTAR 与 POLLEN 使用**同一个装置**，**只有飞轮间隙会改变**；确保修改后的输送部分能兼容两种尺寸的球，并把它们高效送入发射部分。
- 共用几何（CALCULATED，一套、与球无关）：外罩内弧 `R_IN = 107.974 mm`（由大球定：12 + 45.974 + 4.026）、扇区 **142–275°**、壁 7 mm、宽 108 mm、5° 托盘与内弧**精确相切**（切点 x = 38.901 mm、右端 x = 150 mm）、桨毂 **Ø24**、桨臂 r = 10..46、叶片 r = 46..58、TPU 尖 r = 56..60。两球的静止球心半径不同（同一条内弧）：NECTAR r = 62.000、POLLEN r = 72.414。
- 唯一随球改变的量（KNOWN）：飞轮轴距 `half_spacing = nip/2 + 48` → NECTAR **89**（夹口 82，取自 nectar 文件）、POLLEN **80**（夹口 64）。共用性核验（KNOWN）：`cad/paddle_launcher_constrained.py` 全文不含球径参数，外罩/托盘/拨杆都不引用 `BALL_R` / `BALL_D` → **两版实体只差飞轮夹口**。
- 拨杆口径变更（SIMULATED，DEC-0030）：由三叶 18/138/258 改为 **两叶 330°/150°**。R28 对照：三叶时 **NECTAR 卡死**（球停在 r = 67.3 mm / 295°，堵转时间占比 80 %）——258° 那片叶正落在 275° 唇口/入料口前缘，把大球推回托盘；两叶把 275°→142° 的入料走廊让开，两种球都先自流到球窝再被扫掠。
- 索引式循环（SIMULATED）：停 ≥ 1.2 s → 一次扫掠 **240–260°**（25-4，290 rpm）→ 释放。R29（48 组）：330/150 且扫掠 ≥ 248° 的 16 组两球全部通过，扫掠 180/200° 一律失败。R30（12 组，停时 3.0/5.0 s、入料 x = 98/128、扫掠 240/248/260°）：**12/12 全通过** —— NECTAR t = 4.00/6.00 s、v ≈ 4.65 m/s、卡滞 10 %；POLLEN t = 3.40/5.40 s、v ≈ 6.0 m/s、卡滞 0 %。**连续旋转不可用**（会撞上飞轮室里尚未离开的球）。
- 产物（KNOWN）：图 `cad/output/_t06_shared_feeder_zh.png`（四联：共用剖面 + 两球静止半径 / 叶片布置 vs 入料走廊 / 两球半径历程 / 鲁棒性网格）；STEP `cad/output/paddle_launcher_feeder_a_prime_shared_{nectar,pollen}.step`；报告 `cad/output/paddle_launcher_feeder_a_prime_shared_report.json`；单件 `cad/output/inspection/_r26_shared_{paddle_hub,feeder_shell_tray}.step`；检验 spec `config/t06_feeder_aprime_shared_{hub,shell}_checks.json`。大 STEP/STL 已加入 `.gitignore`（可再生成）。
- 作废（SUPERSEDED）：`cad/paddle_launcher_feeder_a_prime_nectar.py`（R25 三叶生成器）已改为运行即退出的指针；其 STEP/STL 只作历史保留。DEC-0029 的叶数与相位被 DEC-0030 取代（相切托盘 / 唇口 275° / 桨毂 Ø24 继续有效）。
- 仍开放（TBD）：μ = 0.40 仍是 `ASSUMED`（台架实测未做）；索引式舵机控制未实现；球质量 0.130 / 0.060 kg 仍是 `ASSUMED`；9.9 mm 夹口过盈无结构/球变形校核。
- CAD 导出实测（MEASURED，2026-10-04，全部读自导出前的最终实体）：
  - 夹口 `flywheel_nip_measured_mm` = **NECTAR 82.000 / POLLEN 64.000**，与目标 `2·half_spacing − WHEEL_OD` 逐对完全一致（4 对飞轮全 82.000 / 64.000）。量法：飞轮缘部三角化点云沿 52° 通道法线投影取间隙（容差 0.5 mm）——飞轮的精确 B-rep 距离在辐条轮上**病理级慢**（单次 > 6 min 不收敛），已弃用，脚本内注明。
  - 毂—外罩内弧 `paddle_hub_to_shell_inner_arc_measured_mm` = **95.974**（两变体相同，目标 95.974），毂与外罩交集体积 **0**。
  - 停位球 vs 外罩 / vs 毂：**两球均为 0 mm³**（球窝落在运载圆上，与外罩内弧相切）。
  - 两变体一致性（KNOWN，充要证据）：外罩体积 **267723.34 mm³ 完全相同**、外罩 bbox 完全相同、毂—外罩 95.974 相同 → 差异**只剩**飞轮轴距（89 vs 80，即夹口 82 vs 64）与由此决定的运载半径（62.000 vs 72.414）。
  - 单件导出：`cad/output/inspection/_r26_shared_paddle_hub.step`、`cad/output/inspection/_r26_shared_feeder_shell_tray.step`；整机 `paddle_launcher_feeder_a_prime_shared_{nectar,pollen}.step`。
- 几何检验（MEASURED，`tools/inspect_geometry.py`）：`cad/output/inspection/t06_shared_R026_hub.json` = **pass 6/6**；`t06_shared_R026_shell.json` = **pass 7/7**。目标值取自 `config/parameters.yaml` 与 DEC-0029/0030，未取自被测件。
- 新测出的**既有**干涉（MEASURED，待用户决策，未关闭）：共用外罩与**保留的父级结构**仍有交叠 —— `shooter_throat_+55` **5717.5 mm³**、`guide_roof_3` **126.5 mm³**（两变体数值相同）。这是**继承而非回归**：R25 的 NECTAR 外罩对 `guide_roof_3` 就是 1727.2 mm³（R26 降到 126.5 mm³），而外罩对 `shooter_throat_+55` 此前从未测过（该键本轮才加入）。送球功能不受影响（R29/R30 就用这套几何跑通），但**实物装配时外罩会与喉道上导板相碰**。可选处理：让外罩对这一对静态件做布尔让位（不改球道，因为交叠在球道外侧 r > 108 mm）。

## T06 共用外罩让位 R27：削掉与保留父级结构交叠的料（2026-10-04，DEC-0031）

- 用户指令（KNOWN）：按上一轮报告的建议做布尔让位，消除外罩与保留父级结构的既有干涉。
- 做法（KNOWN）：对 `shooter_throat_+55` 与 `guide_roof_3` 各自**外扩 0.5 mm**，再用外扩体对 `feeder_shell_tray` 做布尔差；常量 `RELIEF_PARTS`、`RELIEF_CLEARANCE_MM = 0.5`，报告键 `shell_relief`。切削区全部在球道**外侧**（r > 107.974 mm），球实际接触的内弧面完全不动。
- 实测（MEASURED，读自导出前最终实体，NECTAR / POLLEN **逐位相同**）：`relief_targets_removed_mm3` = throat **5717.5021** / roof **90.8564**；`relief_clearance_mm` 两者均 **0.5**（外扩真的生效，没有静默回退成零间隙切割）；外罩体积 **267723.34 → 260374.21 mm³**（净削 7349.13 mm³）。
- 干涉归零（MEASURED）：`shell_tray_clash_with_kept_parts_mm3` = **0**、`shell_tray_clash_hits` = **{}**（R26 的 5717.5 / 126.5 mm³ 归零）→ R26 记录的那项“待用户决策的既有干涉”**已关闭**。
- 球道与接口未受影响（MEASURED）：新增球道扫描自检（沿 142°→275° 运载弧取 **19 个球心**，逐点求 球∩外罩 体积取最大）`sweep_ball_clash_with_shell_max_mm3` = **0**；`nest_ball_clash_with_shell_mm3` = 0、`nest_ball_clash_with_hub_mm3` = 0、`paddle_hub_to_shell_inner_arc_measured_mm` = **95.974**（不变）、`flywheel_nip_measured_mm` = NECTAR 82.000 / POLLEN 64.000（不变）。`shell_bbox_after_mm` 只有 **zmax 182.245 → 180.043**（−2.202 mm，挖掉的是外罩上缘伸到导板上方的那一小块），其余 5 个分界值全部不变。
- 几何检验（MEASURED，`tools/inspect_geometry.py`，目标取自 `config/parameters.yaml`）：`cad/output/inspection/t06_shared_R027_hub.json` = **pass 6/6**；`t06_shared_R027_shell.json` = **pass 7/7**。其中 `T06-APS-SHELL-004` 由 `bbox_max` 改为 `group_bbox` + `axis=z` + `rule=le` + `target=185.759`（脚本的 `bbox_max` 硬编码绝对值比较，无法表达 `le`）。
- 产物（KNOWN）：图 `cad/output/_t06_shared_relief_r27_zh.png`（(a) 让位上下文 3D；(b) 中截面俯视 + 球道弧）；单件 `cad/output/inspection/_r27_shared_{paddle_hub,feeder_shell_tray,relief_context}.step`；整机 `cad/output/paddle_launcher_feeder_a_prime_shared_{nectar,pollen}.step` 已按 R27 重导；报告 `cad/output/paddle_launcher_feeder_a_prime_shared_report_{nectar,pollen}.json`。R26 的单件与检验 JSON 保留为历史。
- 教训（KNOWN）：`BRepOffsetAPI_MakeOffsetShape.PerformByJoin` 必须**逐 solid** 调用。把部件当 compound 喂进去，OCCT 会当成“外表面偏移”而返回**更小**的实体（实测 38596 → 20737 mm³），第一版 R27 因此静默回退成零间隙切割。`_grow()` 现在逐 solid 外扩并校验 `fused.Volume() > shape.Volume()`，报告里的 `relief_clearance_mm` 就是“外扩生效”的证据。
- 仍开放（TBD）：与 R26 相同 —— μ = 0.40 仍是 `ASSUMED`（台架实测未做）；索引式舵机控制未实机实现；球质量 0.130 / 0.060 kg 仍是 `ASSUMED`。

## T06 R32 全流程仿真复核：R27 几何下两球各自正确夹口（2026-10-04）

- 用户指令（KNOWN）：对 R27 新版跑全流程仿真，**POLLEN 和 NECTAR 都要做**，各自使用**正确的飞轮间隙**；确认没有问题后交用户自己复核。
- 口径（KNOWN）：几何 = R27（DEC-0031）。R27 相对 R26 的唯一差异是外罩球道**外侧**（r > 107.974 mm）的 0.5 mm 让位，球实际接触的内弧面完全未变 → 仿真的接触几何与 R26 逐点相同；让位不侵入球道另有 CAD 的 19 点球道扫描（0 mm³）独立证明。
- 唯一随球改变的输入（KNOWN）：飞轮半轴距 `half_spacing = nip/2 + 48` → NECTAR 89（夹口 **82**）、POLLEN 80（夹口 **64**）。
- 共用输入（KNOWN/CALCULATED）：`R_IN` 107.974 mm、运载半径 = `R_IN − r_ball`（NECTAR 62.000 / POLLEN 72.414）、托盘 5° / pivot (−0.806, 0.423) / x 38.901–150、拨杆两叶 330°/150°、毂 Ø24、叶片 r 46–58、TPU 尖 56–60、出口 142°、唇口 275°。
- 驱动与发射（ASSUMED）：索引式（停 hold → 一次扫掠 sw → 释放）；舵机 25-4 Super Speed 线性模型（堵转 0.530 N·m / 290 rpm → kv = 0.017452）；飞轮 1620 rpm；μ = 0.40；t_end 8 s。
- 结果（SIMULATED，**6/6 通过**，全程 17 s）：

| 球 | 工况 | 夹口 (mm) | 出口 t (s) | 出口 v (m/s) | 出口角 (°) | 最高点 (mm) | 平射程 (m) | 卡滞 (%) | 峰值扭矩 (N·m) | 最小 r (mm) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NECTAR | A 停 1.2 s / 扫 248° | 82 | 2.18 | 4.81 | 50.5 | 702 | 2.3 | 10 | 0.530 | 61.97 |
| NECTAR | B 停 3.0 s / 扫 248° | 82 | 3.97 | 4.79 | 51.7 | 722 | 2.3 | 10 | 0.530 | 61.96 |
| NECTAR | C 停 3.0 s / 扫 260° | 82 | 3.97 | 4.82 | 51.8 | 732 | 2.3 | 10 | 0.530 | 61.96 |
| POLLEN | A 停 1.2 s / 扫 248° | 64 | 1.83 | 6.20 | 51.8 | 1206 | 3.8 | 3 | 0.530 | 72.40 |
| POLLEN | B 停 3.0 s / 扫 248° | 64 | 3.38 | 6.18 | 51.6 | 1194 | 3.8 | 0 | 0.530 | 72.43 |
| POLLEN | C 停 3.0 s / 扫 260° | 64 | 3.37 | 6.18 | 51.8 | 1204 | 3.8 | 0 | 0.530 | 72.43 |

- 球路（SIMULATED）：球由右端托板借 5° 自流滚入，先停在 r ≈ 93 mm / α ≈ 323° 的通道口，再自行落到运载半径 r = 62 mm（球外表面贴住 r = 107.974 mm 的内弧面）；扫掠开始后 α 由 323° 单调递减到出口 142°，**共 181°**。
- 让位区核验（SIMULATED）：球在外罩扇区（142–275°）内的最大外缘半径 NECTAR **108.474 mm** / POLLEN **108.650 mm**，只比内弧面 107.974 mm 多 0.5–0.7 mm —— 这是球被叶片压在内弧面上的接触压入量，**不是**让位面被触及；让位面在球道外侧（r > 107.974 mm），全程无球接触。
- 与 DEC-0030 的 R29/R30 一致性（SIMULATED）：NECTAR v = 4.79–4.82 m/s（R30 为 4.64–4.68）、POLLEN v = 6.18–6.20 m/s（R30 为 5.87–6.13）；卡滞 NECTAR 10 %、POLLEN 0–3 %，同为索引式口径 —— R27 的让位**没有改变送球与发射行为**。
- 产物（KNOWN）：脚本 `simulation/mujoco/_work/r32.py`；数据 `simulation/mujoco/out/_r32_r27_full.json`（含 6 个工况的全量 trace 与逐工况接触集合）；图 `cad/output/_t06_r32_fullflow_zh.png`（两球 r(t)/α(t) 历程 + 俯视剖面 + 球轮廓轨迹 + 结果表）。
- 仍开放（TBD）：与 R27 相同 —— μ = 0.40 仍是 `ASSUMED`（台架实测未做）；索引式舵机控制未实机实现；球质量 0.130 / 0.060 kg 仍是 `ASSUMED`；9.9 mm 夹口过盈无结构/球变形校核。

## T06 可视化：看球被送球、发射、飞出的全过程（2026-10-04）

- 用户请求（KNOWN）：需要能"运行脚本并看到可视化的小球飞出"。
- 做法（KNOWN）：新增 `simulation/mujoco/view_r32.py`，复用 `_work/r32.py` 的同一套模型构造。为便于复用，本轮把 `r32.py` 里的 `run()` 机械拆出 `build()`（返回模型/数据/ID/控制），**未改任何物理口径**；重跑 `r32.py` 逐项数值与提交版一致（NECTAR A 出口 2.18 s / 4.81 m/s、POLLEN B 3.38 s / 6.18 m/s，仍 6/6 通过）。
- 两种查看方式（KNOWN）：(1) 交互窗口 `mujoco.viewer` —— 实时但默认 4 倍慢放（`--speed`），空格暂停/继续，鼠标转视角，跑完自动重播；(2) `--gif` 无头渲染成 GIF —— 出射前镜头固定看机构，出射后自动把"出射点 + 球"一起框住并拉远，橙色点串显示飞行轨迹。
- 产物（KNOWN）：`cad/output/_t06_r32_launch_nectar.gif`（107 帧 / 2.68 s，出口 t=2.18 s、v=4.81 m/s）、`cad/output/_t06_r32_launch_pollen.gif`（93 帧 / 2.33 s，出口 t=1.83 s、v=6.20 m/s），40 fps / 480x360。
- 结论（SIMULATED）：与 R32 复核同源同结果，本轮只增加可视化入口，几何、驱动与判定口径均未改动。

## T06 飞轮硅胶离心膨胀计算 + 热态配间距仿真循环 R33/R34/R35（2026-10-04，DEC-0032 / V-0034）

- 用户指令（KNOWN）：按飞轮图纸算离心膨胀量 → 重跑仿真 → 确认膨胀后的飞轮**不会与拨杆接触**；若接触则进入「改送球设计—仿真—识别问题」循环，直到 POLLEN 与 NECTAR 都通过；最后把新图纸导出到桌面。
- 膨胀计算（CALCULATED）：`calculations/t06_flywheel_silicone_centrifugal.py` / `.txt`。飞轮 = goBILDA `3613-0014-0096`，Ø96 × 24，105 g，实测 J = 1.2844e-4 kg·m²，图纸实体体积 **95767.311 mm³**（实心环的 62 %，12 条波形减重槽，Ø32 轮毂孔 / Ø14 轴孔 / 6×Ø4 螺孔）。30A 硅胶 E = 0.7–1.5 MPa（**ASSUMED**）、ν = 0.48、ρ = 1150 kg/m³。三模型 @1620 rpm：**M1 自由薄环 2.44–5.23 mm（上界）/ M2 厚环自由 0.55–1.19 mm / M3 厚环固支 0.26–0.55 mm（下界）**；周向应力仅 0.008–0.017 MPa（弹性范围内，模型成立）。
- 设计取值（ASSUMED）：真实膨胀 **0.5–1.8 mm** → 取 `dr_hot = 0.8 mm`；模型绝对上界 **3.7 mm** 用作边缘复核工况。
- 飞轮转速（KNOWN）：**1620 rpm**（`simulation/mujoco/_work/r32.py` 的 `build_xml(1620.0, …)`），轮缘线速度 8.14 m/s。存能：单轮 **1.85 J**、两轮 **3.70 J**；NECTAR 需 1.50 J（41 %）、POLLEN 需 1.15 J（31 %）。
- 关键几何（MEASURED）：拨杆真实叶片轮廓外切半径 **Rmax = 62.36 mm**；飞轮轴心→拨杆轴心 NECTAR 下轮 **115.91 mm**（36.7°）、POLLEN 下轮 **113.87 mm**（41.1°），上轮 185.00 / 177.91 mm。→ **冷态间隙 NECTAR 5.55 mm / POLLEN 3.51 mm**。
- **膨胀后是否接触（结论）**：设计取值 dr = 0.8 mm → 剩余间隙 **NECTAR 4.75 mm / POLLEN 2.71 mm**；即使取绝对上界 dr = 3.7 mm，NECTAR 仍留 **1.86 mm**；POLLEN 的接触门槛是 **dr ≈ 3.51 mm**（= 冷态间隙），即设计值有 **4.4 倍余量** → **膨胀后的飞轮不会碰到拨杆，送球设计无需改动**。
- R33 冷态装配（SIMULATED）：`simulation/mujoco/_work/r33.py` —— 安装间距按冷态 Ø96 定（`half_spacing = nip/2 + 48`），运行夹口被动变成 `nip − 2·dr`。**26/36 通过**：dr ≤ 2.7 时 NECTAR 全 OK；**dr = 3.7 时 NECTAR 3 例全 FAIL**；POLLEN 从 dr ≥ 1.0 起出现 FAIL。飞轮—拨杆接触 3 起，**全部只在 POLLEN dr = 3.7**（contacts 2121 / 150 / 150，间隙 0.001 mm）。FAIL 机理不是飞轮挡球，而是**夹口缩小改变了出手相位**，小球掉进拨杆毂—叶片夹角卡死。数据 `simulation/mujoco/out/_r33_expansion.json`。
- R34 热态配间距（SIMULATED）：`simulation/mujoco/_work/r34.py` —— 装配意图改为**按热态外径配轮轴间距**（`half_spacing = nip/2 + 48 + dr`），运行夹口恒为设计值 82 / 64。**30/30 通过、零接触、最小间隙 1.351 mm**（POLLEN dr = 2.7）；dr = 0.5 / 1.0 / 1.5 / 2.0 / 2.7 逐档最小间隙 3.109 / 2.708 / 2.304 / 1.905 / 1.351 mm。数据 `simulation/mujoco/out/_r34_expansion_hot.json`。
- 边缘复核（SIMULATED）：dr = **3.0 / 3.7** 两档 **12/12 通过、零接触**。dr = 3.7 时 POLLEN 最小间隙 **0.567 mm**、NECTAR **2.884 mm**；dr = 3.0 时 POLLEN 1.117 mm、NECTAR 3.383 mm。数据 `simulation/mujoco/out/_r34_edge.json`。
- 产物（KNOWN）：图 `cad/output/_t06_r34_expansion_zh.png`（膨胀量 vs rpm 三模型 + 间隙 vs dr + 三轮通过率对照）、`cad/output/_t06_r34_geometry_zh.png`（两球前视剖面：送球扇区、拨杆真实轮廓与外切包络、球窝轨道、冷/热飞轮圆、最小间隙表）；热态 CAD 生成器 `cad/paddle_launcher_feeder_a_prime_shared_hot.py`（`DR_HOT_MM = 0.8`，只改轮轴间距，送球段几何与 R27 逐点相同，产物写 `cad/output/_r35_hot/`，不覆盖 R27）。
- R35 图纸导出实测（MEASURED，读自导出前最终实体）：热态夹口 `flywheel_nip_measured_mm` = **NECTAR 83.6**（= 2×89.8 − 96）/ **POLLEN 65.6**（= 2×80.8 − 96），即按热态配间距后夹口比冷态大 2×0.8 mm，轮子转起来正好回到设计夹口 82 / 64。外罩体积 **260374.21 mm³**、毂—外罩 **95.974 mm**、外罩∩保留父级件 **0 mm³**、19 点球道扫描 **0 mm³** —— 与 R27 **逐位相同**，证明本轮只动了飞轮轴位，送球几何未变（两变体之间也逐位相同 → 「同一装置」结论不变）。
- R35 交付（KNOWN）：`cad/output/_r35_hot/paddle_launcher_feeder_a_prime_shared_{nectar,pollen}.step`（178 MB / 177 MB，大件按 `.gitignore` 本地规则不入库，可用 `cad/paddle_launcher_feeder_a_prime_shared_hot.py` 重生成）+ 两份 `_report.json`；已复制到桌面 `T06_R35_hot_nectar.step` / `T06_R35_hot_pollen.step`。R27 的源文件与产物全部保留未动。
- 教训（KNOWN）：R27 的「半轴距 = nip/2 + 48」是**冷态**口径。硅胶飞轮在转速上会变大，若按冷态配间距，运行夹口会比设计值小 2·dr，R33 实测这足以把 POLLEN 的送球相位打乱。**要求：垫片长度按热态外径配**，即 `half_spacing = nip/2 + 48 + dr_hot`。
- 仍开放（TBD）：硅胶 E 值 0.7–1.5 MPa 与 `dr_hot = 0.8 mm` 均为 **ASSUMED**（无台架测量/高速摄影）；其余同 R27 —— μ = 0.40 `ASSUMED`、球质量 0.130 / 0.060 kg `ASSUMED`、索引式舵机控制未实机实现、9.9 mm 夹口过盈无结构/球变形校核。

## NEXT ACTION

> **R35 已交付（2026-10-04，DEC-0032 / V-0034）**：飞轮硅胶离心膨胀 dr_hot = 0.8 mm（上界 3.7 mm），**膨胀后飞轮与拨杆不接触**（POLLEN 余 2.71 mm、NECTAR 余 4.75 mm；上界处仍余 1.86 / 0.57 mm 且零接触）→ **送球几何不改**，只把飞轮垫片长度改为按热态外径配（`half_spacing = nip/2 + 48 + dr_hot`）。仿真：R33 冷态配间距 26/36（接触 3 起全在 POLLEN dr 3.7）→ R34 热态配间距 **30/30 零接触**、边缘档 **12/12 零接触**。R35 图纸已导出到桌面。
> **R32 已复核（2026-10-04）**：R27 几何下两球各自正确夹口全流程仿真 **6/6 通过**（NECTAR 夹口 82 / POLLEN 夹口 64），让位未进入球道、未改变送球与发射行为，结果与 DEC-0030 的 R29/R30 一致。
>
> **R27 已落地（2026-10-04，DEC-0031）**：共用外罩完成 0.5 mm 让位，`shooter_throat_+55` 5717.5 mm³ / `guide_roof_3` 126.5 mm³ 的交叠实测归零，几何检验 hub 6/6 + shell 7/7 通过 → 下面第 0 项里“待用户决策的既有干涉”已关闭；其余 (a)(b)(c) 三项不变。

0. （当前）DEC-0030 已落实"一套机构兼容两种球"：共用送球段 CAD（R26）已导出、几何检验 spec 已就绪、两球全流程仿真 12/12 通过。按序推进：(a) **台架实测**球—打印外罩摩擦系数，把 μ 从 `ASSUMED` 升为 `MEASURED`（DEC-0028 的开放项，未关闭）；(b) 实现**索引式舵机控制**（停 ≥ 1.2 s → 一次 240–260° 扫掠 → 释放），连续旋转模式禁止使用；(c) 用索引式重跑舵机余量（NECTAR 实测堵转占比 10 %），复核 DEC-0026/0027 的余量口径。

1. （立即，等用户决策）**DEC-0028 取代本项的前提**：实物摩擦（μ≈0.40）下 R5 送球失败，门槛 μ≈0.65。请用户选一条：
   (a') 改**停位半径**：把球的停位抬到 r≈58.4 mm（球外表面贴外罩内弧 93.96 mm），让叶片用法向力推球而不靠指尖摩擦拖拽（推荐；这是唯一能绕开摩擦门槛的方向）；
   (b') 不改几何，改**提高接触摩擦**（拓杆/托板加橡胶或防滑贴）并同步换大扭矩舵机——成本低但会把厂商不可控的磨损引入设计；
   (c') 先做**台架摩擦实测**（同一批球 + 同一台打印件），把 μ 从 ASSUMED 升为 MEASURED 再定方向。
   旧的 (a)/(b) 两条（接受 R6 / 改球窝）仍有效但已不足以解决摩擦门槛，保留供上溯。
   任何改 CAD 前必须先用 `simulation/mujoco/_work/opt_lib.py` 复核门槛；**不得改** `cad/paddle_launcher_constrained.py`、不得覆盖原 STEP。

1b. （旧项，仅作历史）DEC-0027 的两条路线：
   (a) 接受 **R6** 作为送球段几何（少一个平垫块、无台阶、全程快 1.5%），据此改 `cad/paddle_launcher_feeder_redesign.py` 出候选 STEP（**不得改** `cad/paddle_launcher_constrained.py`、不得覆盖原 STEP）；
   (b) 先不动几何，改做**停位球窝**改型（让球停在指片扫掠范围之外，例如加深/缩进球窝或调整停位半径），这是唯一被证明能缩短蠕动时间的方向。
   两条路线都需在改 CAD 前用 `simulation/mujoco/_work/opt_lib.py` 复核门槛；舵机余量复核（真实电机模型口径）与本项并行。

2. （并行阻塞项）按 KEI-12 制作带护罩双轴安全旋转台架，用实物确认垫片/卡簧/螺钉、REX/花键夹持、打印滑座配合和线束弯曲空间，再记录转速恢复、电流、温升、振动及 POLLEN/NECTAR 两个间隙端点。未完成前不得进入 M4 或发布制造图。
