# 工程决策日志

## DEC-0001 — 工程框架与工具路线

- Decision: 采用文件化检查点、稳定 ID、集中 YAML 参数、模块化 CadQuery 优先及分级验证流程。
- Reason: 支持低资源电脑、长周期协作、重启恢复和可追溯变更。
- Alternatives considered: 单体 CAD；仅依靠对话状态；早期高保真仿真。
- Evidence/calculation: 用户给定的过程要求与电脑资源边界；本决策不涉及机器人性能计算。
- Impact: 后续设计必须通过成熟度和验证关口；增加少量文档维护成本。
- Reversible?: 部分可逆；ID 与参数主源形成后应保持兼容。
- Date/version: 2026-09-19 / Framework v0.1.0

## DEC-0002 — 全局坐标方向

- Decision: 使用右手系，+X 前、+Y 左、+Z 上；原点暂定为驱动接触平面轮迹包络几何中心。
- Reason: 易用于车辆运动、俯视布局、重心和场地坐标变换。
- Alternatives considered: 原点位于后左下角；+Y 向右。
- Evidence/calculation: 工程约定，无性能计算；原点实体实现仍为 TBD。
- Impact: 所有模块、接口和导出必须遵循同一方向。
- Reversible?: 方向在首个 CAD 前可逆；冻结后变更成本高。
- Date/version: 2026-09-19 / Framework v0.1.0

## DEC-0003 — 先比较任务包，再比较机构

- Decision: 不预设必须完成的得分任务；先比较 P1 基础移动、P2 FLOWER 专项、P3 HIVE 专项和 P4 双目标混合，再为入选任务包生成机构概念。
- Reason: 用户明确没有必须完成的任务；任务范围决定模块数量、风险和资源预算。
- Alternatives considered: 直接选择全功能机器人；直接从某个机构开始。
- Evidence/calculation: 用户输入 2026-09-19；TU01 §10.5 的计分结构。
- Impact: 当前保持 T04–T07 为条件模块，不进入详细 CAD。
- Reversible?: 是；任务包可在概念比较后组合或缩减。
- Date/version: 2026-09-19 / Requirements v0.1-draft

## DEC-0004 — 商业件采用包络代理

- Decision: 场地保留官方 STEP 作为几何权威；3209-0001-0007 底盘和 5203-2402-0051 电机在早期 CAD 中使用带安装基准的低细节包络代理，不直接装入完整供应商模型。
- Reason: 原始 STEP 分别约 157 MB 和 17 MB，细节会增加重建、显示和版本库存储成本。
- Alternatives considered: 全细节供应商模型；仅手工填写尺寸且不保留来源。
- Evidence/calculation: 压缩包与 STEP 文件检查；用户明确建议简化。
- Impact: 代理生成前必须核验包络、轴线、安装面和必要孔位；原模型只用于参考验证。
- Reversible?: 是；最终集成可按需换入详细模型做局部核验。
- Date/version: 2026-09-19 / Framework v0.2.0

## DEC-0005 — BIOBUZZ 模块重组

- Decision: 将输送、缓冲和路由暂合并为 T05；将 HIVE 发射与 FLOWER 处理拆为 T06/T07；新增 T08 控制与自主；不设置独立末局机构。
- Reason: 两种得分目标的几何和规则接口明显不同；控制物体上限为 4；PARK 不需要独立末局机械功能。
- Alternatives considered: 保留原 T04–T09 通用模板；将所有得分机构合并为一个模块。
- Evidence/calculation: G407、G417、G418；TU01 §10.5。
- Impact: 后续按任务包启用条件模块，并分别验证。
- Reversible?: 是，架构尚未冻结。
- Date/version: 2026-09-19 / Architecture v0.1-draft

## DEC-0006 — 底盘不变量与电机代理策略

- Decision: 保持 3209-0001-0007 的四轮相对布局、轮距和轴距，只允许最低限度拆分重组；5203-2402-0051 仅作为 goBILDA 同类齿轮电机的包络参考，具体速比和型号由工程计算选择。
- Reason: 保留成熟底盘运动学和装配可靠性，同时避免把示意电机错误冻结为机构电机。
- Alternatives considered: 任意重构底盘；强制所有机构使用 117 RPM 电机；直接使用全细节供应商 CAD。
- Evidence/calculation: 用户输入 2026-09-19；SRC-003、SRC-004。
- Impact: T01 轮系布局成为接口约束；各机构必须在 M2 完成电机选型计算。
- Reversible?: 底盘不变量需用户批准才能变更；电机选型在 M2 前可逆。
- Date/version: 2026-09-19 / Requirements v0.1-rc1

## DEC-0007 — 先例驱动但独立验证

- Decision: 允许参考往届优胜 FTC 机器人和成熟工业设计，但只继承经当前规则、载荷、空间和制造验证的设计原则。
- Reason: 利用成熟经验降低风险，同时避免赛季差异、幸存者偏差和不可追溯复制。
- Alternatives considered: 完全从零构思；直接复刻获胜机器人。
- Evidence/calculation: 用户输入 2026-09-19；PRJ-003、PRJ-009。
- Impact: 后续每个概念必须附来源与适用性说明，最终选择仍由本项目计算和测试决定。
- Reversible?: 是。
- Date/version: 2026-09-19 / Architecture v0.1-rc1

## DEC-0008 — 批准需求与架构基线

- Decision: 将 Requirements v0.1 和 Architecture v0.1 设为首个批准基线，允许开始任务包量化比较和 M1 概念筛选。
- Reason: 用户已明确批准开始执行；所有 CRITICAL 输入项已关闭。
- Alternatives considered: 继续保留候选基线；在任务包选择前冻结具体机构。
- Evidence/calculation: 用户批准 2026-09-19；VAL-S00-001、VAL-S00-004。
- Impact: 后续变更必须保持需求 ID 并记录影响；本批准不选择 P1–P4，也不冻结详细几何。
- Reversible?: 可经变更审查修订；历史基线不可覆写。
- Date/version: 2026-09-19 / Requirements v0.1, Architecture v0.1

## DEC-0009 — 任务包首轮筛选策略

- Decision: P1 作为所有方案的共同底座；首轮让 P2 与 P3 进入 M1 并行概念研究，暂缓 P4 全功能集成，最终任务组合留待低成本试验和资源预算后选择。
- Reason: 中性、可靠性优先和资源受限三组权重下，P1 始终是最稳健底座；P3 战略得分潜力高，P2 风险较低；P4 的空间、控制和验证耦合尚无证据支撑。
- Alternatives considered: 立即选择 P3；直接开发 P4；只做 P1。
- Evidence/calculation: `docs/task_package_trade_study.md`；`calculations/task_package_trade.py` 的确定性结果及敏感性分析。
- Impact: T04/T05 先研究共享物体链，T06/T07 分支独立比较；不承诺最终同时安装两条得分链。
- Reversible?: 是；原型数据、赛程或用户权重可触发重评。
- Date/version: 2026-09-19 / Trade Study TS-S00-001 v0.1

## DEC-0010 — 战略主导且证据锚定的任务包筛选

- Decision: TS-S00-001 v0.2 将战略总权重提高至 70%，用 TU01 的分值、RP、计分窗口和解锁关系锚定战略评分；P3 为主 M1 方向，P4 为受资源关口约束的扩展，P2 为风险回退。此决策取代 DEC-0009 中 P2/P3 等量并行的安排。
- Reason: v0.1 的战略权重只有 25%，使低复杂度 P1 在总分中失真地领先；用户要求战略价值显著主导且每项评分有证据。
- Alternatives considered: 仅调高原“战略价值”单项而保留其余主观评分；直接选择 P4；完全忽略工程交付风险。
- Evidence/calculation: TU01 §10.1、§10.4、§10.5 及 Table 10-2/10-3；`docs/task_package_trade_study.md`；`calculations/task_package_trade.py`。战略权重 60%–80% 时 P3 均第一、P4 均第二。
- Impact: 研发资源优先用于 HIVE 发射与共享物体链；FLOWER 先做 P4 增量兼容研究，不与 P3 平分资源。
- Reversible?: 是；官方 RP 阈值、M1 资源预算或 L6 原型数据可触发重评。
- Date/version: 2026-09-19 / Trade Study TS-S00-001 v0.2

## DEC-0011 — P3 首轮发射原型路线

- Decision: 让 C06-B 对置双飞轮与 C06-A 单飞轮曲面压板进入共用可调台架；C06-C 可调弹射器保留为风险回退。首个基准优先固定低位发射，不预先加入升降或炮塔。
- Reason: 弹道计算显示固定 400 mm 高度在 1.5 m/55° 时只比 700 mm 高位多约 13% 出射速度，却避免展开接口；C06-B 对双球尺寸适配更有潜力，C06-A 提供低电机数对照。
- Alternatives considered: 直接冻结双飞轮；只做单飞轮；立即采用冠军先例弹射器；先做电动炮塔/升降。
- Evidence/calculation: `docs/p3_hive_concept.md`；P3-BAL-0.1、P3-MOT-0.1、P3-TS-001；PRE-FTC-002/003/004 与新增先例。
- Impact: T06 暂占 1–2 个电机；双飞轮整机预算正好达到 8 电机，不允许无资源重分配增加电机炮塔或 P4 机构。
- Reversible?: 是；L6 命中率、功耗、恢复时间或双球损伤数据可改变排序。
- Date/version: 2026-09-19 / P3-M1 v0.1

## DEC-0012 — P3 主发射器与 FLOWER intake 复用边界

- Decision: 选择 C06-B 对置双飞轮作为 P3 主原型和默认架构，C06-A 单飞轮曲面压板作为同台对照与回退；让 T04 intake 兼任 FLOWER 底部逐个取出 POLLEN，但不把顶部 FLOWER 放球纳入当前基线。
- Reason: 在已批准的 P3 战略优先顺序下，C06-B 具有可解析证明的理想零自旋设定点、平移/自旋独立控制和对称调隙中心线不变；底部取球可复用现有 intake 电机，使 8 电机上限仍满足部分 FLOWER 交互。顶部放球对 NECTAR 只有 5.25 mm 名义径向余量且需要展开，证据不足。
- Alternatives considered: C06-A 作为主架构；继续以旧主观加权分并列两方案；为 FLOWER 单独增加第 9 个电机；立即加入可抬升 intake 顶部放球。
- Evidence/calculation: TU01 §9.7、§9.8、§10.3.1、§10.5.2、G407、G410、G415、G418、R105、R503；`docs/p3_launcher_comparison.md`；P3-LAUNCHER-CMP-0.2；PRE-FTC-004/010/011。
- Impact: T06 默认占 2 个电机并用满整机 8 个电机端口；T07 不得自行增加电机。C06-A 必须保留到 L6 随机交错对照完成，实测电源/精度/维护失败可触发反转。
- Reversible?: 是；按 VAL-T06-004 的预登记反转规则执行，不凭印象改回。
- Date/version: 2026-09-19 / P3-LAUNCHER-CMP-0.2

## DEC-0013 — 单电机拨杆—转轮复合 Intake

- Decision: T04采用C04-A上方薄拨叉、末端落钩和顺从分段roller；只用1个直流电机驱动roller并预留共驱短输送，使用2个舵机完成拨叉伸缩和落钩。FLOWER底部取POLLEN不增加电机。
- Reason: Retrieval Opening对名义POLLEN有19 mm总高度余量，4 mm拨叉可从球上方进入并保留15 mm名义余量；两舵机把间歇路径运动与连续roller动力分离。共享T04/T05电机后，四电机底盘和双飞轮仍只占7个电机，保留1个端口。
- Alternatives considered: 只用roller直接拉球；为拨杆增加第二直流电机；单舵机弹性钩；从FLOWER侧面取球；独立FLOWER intake。
- Evidence/calculation: TU01 §9.7、§9.8、G407、G415、G418、R503；`docs/t04_intake_concept.md`；T04-INTAKE-0.1。
- Impact: T04预占1电机/2舵机，T05单球闸门预占1舵机；拨叉宽度、实际取出力和完整扫掠必须由L3/L6关闭，当前不得发布制造图。
- Reversible?: 是；若100次夹具试验证明两舵机路径不可靠，可换成单自由度凸轮或其他底部取球机构，但不得无审查增加电机。
- Date/version: 2026-09-20 / T04-INTAKE-0.1

## DEC-0014 — 当前保留四电机麦克纳姆底盘

- Decision: 当前不把3209-0001-0007改成两电机差速，也不为“效率”单独改成四电机差速；保留轮距、轴距和四电机麦克纳姆运动学。
- Reason: 四电机差速不释放端口；两电机差速虽释放2个端口并移除874 g电机，但理想峰值轴功率和电机限制牵引力减半，且失去保持射击朝向时的横移。C04-A共享动力后整机已有1个电机端口余量。
- Alternatives considered: 四电机差速；两电机差速+链/带驱动四轮；立即更换96 mm牵引轮；维持麦克纳姆但减少到两电机（运动学不可接受）。
- Evidence/calculation: `docs/t01_drive_trade_study.md`；T01-DRIVE-TRADE-0.1；5203-2402-0019和3209-0001-0007供应商规格；P3/T04资源预算。
- Impact: 保持全向对位与现有底盘最小改动；驱动仍占4个电机。若未来批准的功能需要至少2个额外电机，必须按预登记条件重开评审。
- Reversible?: 是，但属于用户已冻结底盘不变量的变更，执行前必须再次批准并完成L6路径/牵引测试。
- Date/version: 2026-09-20 / T01-DRIVE-TRADE-0.1

## DEC-0015 — C04-B1底部开口内侧拨优先原型

- Decision: 将用户提出的C04-B拆分为合法性待验证的C04-B1“底部Retrieval Opening内侧拨、出底部边界后导入标准roller”和被规则排除的C04-B2“穿过FLOWER侧面离开”。C04-B1成为首个L3/L6原型，C04-A保留为并行回退；当前不冻结最终方案。
- Reason: B1名义上只需一个专用舵机、不增加电机，并把FLOWER解锁动作与普通roller解耦。理想台阶模型证明40 mm侧扫能覆盖13 mm环唇所需的27.46 mm水平跨越，20–30°工作面可在26.00–38.01 mm路径内提供13 mm抬升；但横向侧管净空尚未从官方STEP关闭。
- Alternatives considered: 保持C04-A为唯一方案；把任何侧向球速都误判为侧面取出；采用真正穿过侧管间隙的C04-B2；立即冻结B1制造尺寸。
- Evidence/calculation: TU01 G415/G418；`docs/t04_intake_side_sweep_trade.md`；T04-INTAKE-0.2 INT-014..022；用户草图与说明2026-09-20。
- Impact: IF-T04-FLOWER-01升至v0.3；新增VAL-T04-004/005。下一步优先隔离官方STEP底部截面并建立A/B同夹具对照。未通过规则边界或发生不可恢复侧向楔球时回退C04-A。
- Reversible?: 是；按预登记L3/L6门槛选择，不凭加权分单独冻结。
- Date/version: 2026-09-20 / T04-INTAKE-CMP-0.1

## DEC-0016 — C04-B1由纯横向改为25°斜向侧拨并进入M3

- Decision: 淘汰模型−X方向纯横向直线；采用从−X朝合法底部开口前方−Y偏25°的斜向侧拨作为C04-B1 M3中心路径。拨片动力行程60 mm，之后由位于路径距离116 mm处的Ø60 × 120 mm标准roller接管。目标舵机按6 V、3.2:1减速建模；不默认使用7.4 V。
- Reason: 官方独立FLOWER STEP显示纯横向球路与左后短支柱存在−5.437 mm解析净空和590.763 mm³最大实体交叠；25°路径保留90.6%侧向分量，同时提供3.680 mm名义支柱净空，完整球、拨片与roller名义交叠均为0。目标舵机6 V直驱扭矩不足，3.2:1在80%效率和50%堵转运动边界下刚好覆盖10 N。
- Alternatives considered: 保持纯横向并依赖软球变形；改为完全朝−Y拉出；直接采用7.4 V；双舵机；回退C04-A。
- Evidence/calculation: SRC-016；T04-FLOWER-SWEEP-0.1 SWP-001..013；T04-INTAKE-0.3 INT-025..033；`cad/modules/t04_intake/side_sweep_intake.py`。
- Impact: 允许生成非制造用途M3低细节模型；3.680 mm名义余量、2.9 A堵转、电源瞬态、舵机外形和实物取出力仍阻塞M4。C04-A继续保留。
- Reversible?: 是；VAL-T04-005实体对照失败则修改角度/柔顺或回退C04-A。
- Date/version: 2026-09-20 / T04-INTAKE-CMP-0.2 / T04-C04B1-M3-0.1

## DEC-0017 — 首轮侧拨验证采用17 mm卷线鼓直线驱动

- Decision: C04-B1首轮实体验证用REV-41-3336在6 V下驱动17 mm节圆半径单层卷线鼓，以绳索拉动25°楔形滑块完成60 mm直线行程；3.2:1减速圆弧拨杆保留为回退，不作为默认夹具。
- Reason: 官方270°范围允许卷线鼓用202.22°完成60 mm行程；在80%效率、50%堵转运动边界和1.5 N回位载荷下，仍有11.42 N可用于外部负载，高于10 N原型目标；全堵转短时结构边界扣除回位载荷后为24.34 N，高于20 N结构目标。直线滑块复用已通过FLOWER STEP的直线路径，避免70 mm圆弧机构相对60 mm弦产生6.75 mm弓高偏差。
- Alternatives considered: 3.2:1齿轮/皮带减速加70 mm圆弧拨杆；UltraSpeed直驱长拨杆；改用Balanced舵机；第二个直流电机。
- Evidence/calculation: SRC-017/018；T04-INTAKE-0.4 INT-025..043；VAL-T04-006；`cad/modules/t04_intake/flower_side_sweep_prototype.py`。
- Impact: 新增三件可打印验证件和REV-41-1828铝舵盘/绳索/低力回位件；不增加电机或舵机数量。绳滑移、卷绕半径变化和电源瞬态仍阻塞M4。
- Reversible?: 是；若L6显示滑移、磨损或周期不稳定，则切换3.2:1回退或重新选择卷线半径，需保持60 mm直线路径及力/角度双门槛。
- Date/version: 2026-09-20 / T04-INTAKE-0.4 / T04-C04B1-M3-0.2

## 新条目模板

## DEC-0018 — KEI-16 单电机翻转 Intake 的 COTS 传动与被动部署基线

- Decision: 导入参考 KEI-16 采用1台 goBILDA 312 rpm直流电机、24T:24T MOD1斜齿轮、两段14T/38节钢链驱动3根固定roller，并以16T:24T/460 mm HTD5恒中心距带驱动翻臂前轴；采用左右双弹簧、双承载棘爪、双硬止挡和只负责解锁的REV-41-3334。当前仅支持赛前手动收纳和比赛中一次弹出，不宣称主动收回。
- Reason: 该拓扑保留参考视频的一电机、多横轴、90°换向和前指轴特征，同时把关键传动件收敛到goBILDA/REV目录规格；独立短链段便于张紧维护，恒中心距带不会随翻臂角变化，承载棘爪/硬止挡使舵机和传动不承受碰撞载荷。
- Alternatives considered: 435 rpm加20T:28T占位齿轮与多轴同步带；一条长链跨三轴；主轴反转凸轮解锁；用驱动电机主动收回；让舵机保持弹簧或碰撞载荷。
- Evidence/calculation: `calculations/kei16_flipout_drive_inputs.json`、`calculations/kei16_flipout_drive.py`、`docs/engineering/t02-single-motor-flipout-intake-baseline.md`、`cad/biobuzz_single_motor_flipout_intake.py`；96.000 mm链轴距、179.887 mm带轴距、7.82齿啮合、0.755 N·m估算告警扭矩和双弹簧端点力矩复算通过。
- Impact: 允许采购核心COTS传动件并制作单侧M3/L6台架；弹簧、打滑器、棘爪、止挡、轴向堆叠和整机接口仍阻塞M4。该导入参考不改写Architecture v0.1的T02/T04编号，也不自动取代T04 C04-B1。
- Reversible?: 是；实测堵转、球路、弹簧、碰撞或维护性失败时可调整齿比、轴距和部署机构，并以superseded记录保留本版本。
- Date/version: 2026-09-27 / KEI16-FLIPOUT-COTS-0.2

## DEC-0019 — C06-B 双飞轮采用 goBILDA 8 mm REX 直驱 COTS 栈

- Decision: `C06B-COTS-0.1` 保留两根独立对置飞轮轴，不设置外置齿轮；每根轴由一台 goBILDA `5203-2402-0003` 经 `4007-4008-4008` 联轴器直驱。飞轮、Sonic Hub、168 mm REX 轴、14 × 5 mm REX 轴承和36 mm夹具均采用已核对 SKU。两台电机置于−Y侧，调隙连杆置于+Y侧。
- Reason: 回滚后的 CAD 使用 Ø38 电机/无 SKU 夹具、16 × 7 mm 轴承、194 mm 轴和无 SKU 联轴器，不能形成可采购且可验证的轴向堆叠。直驱保留双电机独立控速，不增加齿隙、额外轴或采购风险。
- Alternatives considered: 保留占位件；增加外置齿轮同步两轴；使用 REV HD Hex/UltraPlanetary 并增加 REV-to-REX 转接；在调隙连杆一侧继续布置上电机。
- Evidence/calculation: SRC-019；`config/t06_launcher_cots.json`；`docs/engineering/t06-opposed-flywheel-cots-audit.md`；`cad/output/paddle_launcher_feasibility_report.json`；VAL-T06-006。
- Impact: 侧板长槽由轴承穿槽改为8.4 mm轴槽；目录轴长改为168 mm；两端点的电机、夹具和联轴器随滑座移动。该版本允许进入官方 STEP 轴向复核，不允许跳过实物旋转、护罩、电流和温升测试。
- Reversible?: 是；若官方 STEP 或台架显示联轴器夹持、轴挠度、1620 rpm裕量或双电机电流不合格，应创建 superseding 版本并保留本记录。
- Date/version: 2026-09-28 / C06B-COTS-0.1

## DEC-0020 — T06 采购件在工作装配中按每 SKU 一个连通实体表示

- Decision: 保留 13 个 goBILDA 官方原始多实体 STEP 及其哈希作为审计证据；`C06B-COTS-0.2` 的工作装配依据官方 CAD 包络和关键接口，为电机、舵机、支架、轮毂、飞轮、轴承、联轴器和轴分别生成“每个 SKU 一个连通实体”。
- Reason: 用户明确要求把电机等多实体当作一个实体处理。官方电机 STEP 含 66 个实体，直接展开会把采购总成内部零件错误暴露为机器人装配层级，并增加重建、导出和干涉检查成本；单连通实体能稳定表达采购边界，同时保留轴、孔、轮缘和安装包络。
- Alternatives considered: 在主装配中完整展开供应商子零件；只保留官方 STEP 最大实体；继续使用未绑定官方尺寸的原始几何占位。
- Evidence/calculation: SRC-019；`references/vendor/gobilda/t06/manifest.json`；`cad/t06_vendor_cad.py`；`config/t06_launcher_cots.json`；`cad/output/paddle_launcher_feasibility_report.json`；`tests/test_t06_launcher_cots.py`。
- Impact: 13 个采购件工作代理均回读为 1 个实体，POLLEN/NECTAR 两端点干涉和 18 in 包络检查通过。该表示用于 M3 包络与运动链验证，不保留内部紧固件/花键细节，不能直接发布为制造模型；原始官方 STEP 可用于局部复核。
- Reversible?: 是；需要审查具体内部配合时可在隔离文件中加载原始 STEP，不必改变主装配层级或删除本版本。
- Date/version: 2026-10-01 / C06B-COTS-0.2
- Status: SUPERSEDED 2026-10-01，由下方 DEC-0021 取代。本版本把每个 SKU 融合为"一个连通实体"的并集链已被测量否决（丢料/增料/不可承受的运行时间）。记录保留用于追溯，不删除。

## DEC-0021 — T06 采购件按"整个官方部件"表示，不对供应商实体做布尔并集

- Decision: `C06B-COTS-0.3` 取消"每 SKU 一个连通实体"的布尔并集链，改为把每个采购 SKU 的官方 STEP **整件**当作一个工作部件使用：官方文件是几个实体，工作部件就是几个实体（`cad/t06_vendor_solids.py` 的 `whole_part()` 返回单实体或 `Compound`，永不调用布尔并集）。只有供应商随机附带、不属于所购部件的散件才按 `config/t06_vendor_derivation.json` 的 `keep` 规则丢弃并登记。13 个 SKU 中 9 个为多实体（电机 66、两台舵机各 11、飞轮 2、轮毂 3、轴各 2、夹具 2、轴承 3），4 个为单实体。
- Reason: 用户明确指示"把官方部件当一个整体看就行了"，即采购边界是"整件"，而不是"一个 B-rep 实体"。同时测量否决了布尔并集：一次多参数 `fuse` 处理 `1309-0016-4008` 需超过 3 min 且在执行完毕后丢失 29.44 mm³（总 4203.984 mm³），`1401-0043-0036` 反而凭空增加 3.7 mm³；OCC 还会返回 `isValid()==True` 的空结果，电机 66 个实体之间真实间隙为 0.0289–0.05 mm。并集既不可承受也不可信，并会删除用于复核的间隙证据。
- Alternatives considered: 继续做布尔并集或改用 `unify_same_domain`（已被测量否决，会丢料/增料）；只保留最大实体（丢弃盾片、压配件等真实结构，等于未登记的近似）；在主装配中把 66 个实体提升为独立装配层级（把采购总成内部零件错误暴露为机器人 BOM 层级）。
- Evidence/calculation: SRC-019；`cad/t06_vendor_solids.py`（`DERIVATION_VERSION=8`、`BOOLEAN_UNION_POLICY`、`VOLUME_METHOD`）；`config/t06_vendor_derivation.json`；`cad/output/vendor_solids/<sku>.json`（逐 SKU 记录来源实体数、保留数、丢弃数、空隙事实与 `boolean_union.attempted=false`）；`tools/inspect_geometry.py`；`config/t06_geometry_checks.json`。派生运行证据 `tmp/derive_whole_part.log`：13/13 SKU 成功，`derived_volume_mm3 == kept_volume_mm3` 全部成立。
- Impact: 工作装配保留供应商的真实内部间隙，13 个采购件中 9 个为多实体，`tools/inspect_geometry.py` 的自动检查目标改为逐 SKU 的实测实体数而非统一的 1。体积不再使用 `Compound.Volume()`（OCC 把 compound 当作一个形状积分，在曲面上与自身实体之和不一致，实测差约 0.35 mm³ 且不随容差收敛），改用 `sum(Solids().Volume())`，可直接与保留输入体积比较。干涉检查、包络与导出的计算量上升（电机 66、舵机 11 个实体）；内部零件级配合仍不声明。
- Reversible?: 是；若后续需要单实体代理，必须新增显式的表示策略并保留本记录，不得静默改动。
- Date/version: 2026-10-01 / C06B-COTS-0.3

## DEC-0022 — 拨杆出口止回指按标准尼龙扎带（zip tie）实现

- Decision: `C06B-COTS-0.3` 中位于 52 度导槽入口的两个止回指（`one_way_finger_+1` / `one_way_finger_-1`）在实物上按**标准尼龙扎带（zip tie，尼龙 6/6）**实现：扎带一端固定在斜坡底面，另一端自由并预压在小球侧面上。仿真与后续计算按此材料/截面建模；M3 装配中的 38 x 1.2 x 44 mm 板片仍作为代理几何保留，不再是最终零件定义。
- Reason: 用户 2026-10-03 明确指示"弹性就按一般 zip-tie 来写就行了，在实际运用中估计也是这么办"。扎带是 FTC 上现成、可更换、几乎零成本的单向弹性件，不需要打印件或独立铰链；建模为一个悬臂薄片即可表达止回所需的弯曲刚度。
- Alternatives considered: 打印 PETG 柔性片（需额外打印件与装配，且打印方向影响刚度）；金属弹簧片（成本、重量与安装复杂度都更高）；刚性单向门（无弹性，靠重力复位，低速时不可靠）。以上均不保留为当前方案。
- Evidence/calculation: `cad/paddle_launcher_constrained.py:302-307`（几何与坐标）；`cad/output/paddle_launcher_motion_free_fingers_report.json`（含止回指的导出）；`config/parameters.yaml` 的 `materials.backflow_finger`（E = 2.7 GPa、nu = 0.39、rho = 1150 kg/m3、截面 4.7 x 1.14 mm，均为 ASSUMED 通用尼龙 6/6 取值，采购后必须实测替换）；`docs/requirements.md` 与 KEI-5 的"不得回滚"要求。
- Impact: 仿真需要把止回指当作几何非线性悬臂薄片处理，刚度来自扎带截面而不是板片代理厚度；`ASSUMED` 的材料数据不得用于发布结论，实测后方可升级。同时记录一项待验证事实：两指内表面净距 74.8 mm，POLLEN 球（名义 71 mm）约余 3.8 mm 总间隙，NECTAR 球（名义 91 mm）约过盈 16 mm；指端是否真正拦到两种球的包络仍为 `TBD`，须在 T03.2 台架上确认。
- Reversible?: 是；若要换成打印柔性片或金属弹簧片，新增决策记录并保留本条，不得静默替换。
- Date/version: 2026-10-03 / C06B-COTS-0.3

## DEC-0023 — T06 POLLEN 送球段 V2：外罩与倾斜托板合并为单一零件，同轴由构造保证

- Decision: 送球段重做为 `C06B-POLLEN-FEEDER-V2`：外罩不再是在父级装配里另行摆放的圆环，而是**以拨杆轴 C = (29.49, 0.0, 111.46) mm 为圆心直接画出圆弧**，并把 5° 倾斜托板与唇口连接筋画进**同一条闭合 XZ 轮廓**后沿 Y 挤出 108 mm，成为**一个零件**。父模块 `cad/paddle_launcher_constrained.py` 一行不改，V2 由派生的 `cad/paddle_launcher_feeder_redesign.py` 生成。
- Reason: 用户 2026-10-03 指示"进行重做吧。拨杆，外罩按照你的设想进行调整，使其保持同轴度，与倾斜托板适配"。把圆心与拨杆轴绑成同一个构造点后，"同轴"不再是需要装配公差保证的配合关系，而是画出来的事实；托板与外罩合并后也不再需要独立的托板安装接口。
- Alternatives considered: (a) 保留父级的分件外罩与独立托板，用装配约束/定位销保证同轴 —— 需要额外接口且同轴度仍受公差累积影响；半圆环＋独立托板还难以一次打印；(b) 把托板做成独立打印件再螺接到外罩上 —— 多一个零件与一组螺孔，且托板倾角靠装配保证。两者均不采用。
- Evidence/calculation: `cad/paddle_launcher_feeder_redesign.py`；`cad/output/paddle_launcher_motion_free_pollen_v2_report.json`；`config/parameters.yaml` 的 `t06_feeder_v2`；V2 STEP 回读（`n_solids = 30`、外罩+托板单体体积 255,347.1 mm³、Y 向 ±54 mm = 108 mm 宽、包围盒 281.773 × 192.0 × 325.964 mm）。出口 142° 处球心 (−16.53, 147.415) 到 52° 地板线 55.0022 mm，通道中线 55.00 mm → 偏差 **0.0022 mm**（`pass`）。停位球心 (−2.30, 53.06) 到唇口 35.57 mm ≈ 球半径 35.56 mm（楔紧）。新外罩 vs `guide_floor_3 / guide_roof_3 / guide_wall_3_±1` 干涉全为 0；拨杆扫掠包络 vs 喉道/外罩/导板全为 0，扫掠尖角半径 62.362 mm < 鼓半径 63 mm。
- Impact: 送球段零件数下降；同轴度不再作为公差项检验，改为构造约束（圆心即拨杆轴）。托板与外罩合并使 V2 送球段只能整体更换。父级 `paddle_launcher_constrained.py` 与既有 `paddle_launcher_motion_free_fingers_*`、`paddle_launcher_motion_only_*`、`paddle_launcher_feasible_*` 均未被覆盖，V2 为并列的派生版本。上一轮记录的 `guide_wall_3_-1` 2133 mm³ 干涉经复测确认为外罩挤出方向写错导致的**误报**，实测为 0，侧板不必删除。
- Reversible?: 是；若要回到分件外罩＋独立托板，新增决策记录并保留本条，不得静默替换。
- Date/version: 2026-10-03 / C06B-POLLEN-FEEDER-V2

## DEC-0024 — V2 删除 52 度地板与两片止回指，止回改由 5 度托板自滚 + 唇口楔紧承担

- Decision: `C06B-POLLEN-FEEDER-V2` 从父级装配中删除 `guide_floor_1/2/3`、`guide_roof_1/2`、`guide_wall_1_+1/-1`、`guide_wall_2_+1/-1` 与两片止回指 `one_way_finger_+1/-1`；`shooter_throat_-55` 因被拨杆扫掠鼓挖空至体积归零而自动丢弃。**不再设置独立止回件**：靠 5° 托板让球自滚到位、并在 225° 唇口处被楔紧（球心到唇口 35.57 mm ≈ 球半径 35.56 mm）承担止回。保留 `guide_roof_3`、`guide_wall_3_±1` 与 `shooter_throat_+55`。
- Reason: 拨杆重做后轴心下移 38 mm，停位球心 (−2.30, 53.06) 与父级 52° 地板 `guide_floor_3` 实测重叠 2660.4 mm³，且新拨杆扫掠必打穿该地板 —— 地板必须删。父级两片止回指锚在 (−14.57, ±38, 65.11)，距新停位球心仅 17.2 mm（小于球半径 35.56 mm），物理上已无容身位置，必须删。旧位置时整条 52° 地板本来就被 R = 63 mm 的拨杆扫掠鼓吃光，因此这两处冲突此前从未暴露。
- Alternatives considered: (a) 保留止回指并整体外移 —— 指根要退出球包络需要移动 20 mm 以上，会撞上拨杆臂；(b) 在唇口另加刚性单向门 —— 需要新的铰链/复位元件，且低速下复位不可靠；(c) 保留 52° 地板并把送料段整体抬高回去 —— 等于放弃本轮"缩短拨杆行程"的目标。均不采用。
- Evidence/calculation: `cad/output/paddle_launcher_motion_free_pollen_v2_report.json` 的 `removed_from_parent`、`consumed_by_rotor_drum`、`rest_ball_clash_mm3`（保留零件全部为 0）；托板 X −56 → 150 mm、厚 6 mm、倾角 5°，入口到停位落差 13.326 mm，自滚行程 206 mm、落差 18 mm，落位速度约 0.43 m/s；停位球到唇口 35.57 mm。
- Impact: 送球段的无源件只剩"外罩＋托板"这一件；止回由重力与楔紧几何承担，不引入弹性件刚度假设。`docs/decision_log.md` 的 DEC-0022（止回指按尼龙扎带实现）就"止回指作为 V2 送球段零件"这一用法被本条取代（superseded），其 zip-tie 材料结论与 `config/parameters.yaml` 的 `materials.backflow_finger` 记录保留，供历史上溯与将来重新引入止回件时复用。
- Reversible?: 是；若要重新引入止回件，必须新增决策记录、重新校核球包络并保留本条。
- Date/version: 2026-10-03 / C06B-POLLEN-FEEDER-V2

## DEC-0025 — 送球段方案取舍：以指片布置为主、唇口喇叭为辅，B/C 归档

- Decision: V2 送球段的改进以**指片布置**为主杠杆——由现状三指 120° 等分（θ=342/222/102）改为**二指对置 180°（θ=350/170）**；几何上叠加 **A 唇口喇叭**（删 225° 挡墙，改 227.5/231.5/235.5° 三段斜楔，r_in 95.5/99.5/103.5），可选叠加 **D 球窝抬高 6.8 mm**。目标门槛 **0.46 N·m @ 90 rpm**、稳健 2/2。**B 托板末端缩进与 C 叶尖卸载记为负结果并归档，不再投入**。
- Reason: 逐个仿真实测显示真正的门槛来源不是唇口而是指片停位——现状三指相位下球**滚不到唇口**，沿托板滚到 X≈112（θ=330°）即撞在指片**尖端平面**上停住，球心 r=95.5 mm，而设计轨道为 R=58.40 mm；送球完全靠叶尖拖拽与硬夹，这才是 0.94 N·m 的来源。改二指对置后停位让出球道，门槛降至 0.55，叠加 A 后 0.46。
- Alternatives considered: (a) 仅做 A 唇口喇叭 0.72（−23%，有效但不足）；(b) 仅做 B 托板缩进 0.94（与现状相同，无效）；(c) 仅做 C 叶尖卸载 1.25（比现状恶化 33%）；(d) 仅做 D 球窝抬高 0.68（−28%，有效）；(e) A+D 0.64（最低但稳健性掉到 1/2）；(f) R2/R5/R3 二指组合 0.46/0.42/0.42，稳健均 2/2 —— **采用 (f) 的 R2**。
- Evidence/calculation: `simulation/mujoco/out/FINDINGS_v2_zh.md` 第七节；`summary_v2_rerun_opts.json`（逐个复跑，与首轮逐字一致）；`summary_v2_phase.json`、`summary_v2_best.json`；总图 `geom_options_verdict_zh.png`；脚本 `_work/opt_lib.py`、`_work/rerun_opts.py`、`_work/best_probe2.py`。工况：拨杆 200 rpm，球从托板 X=145 滚入，门槛用二分法求最小可通过力矩限幅，分辨率 0.05 N·m。全流程 `pass`（飞轮 1620 rpm → 出口 6.53 m/s @ 50.2°）。摩擦为**反杠杆**：μ_ball 1.0→0.94、0.7→1.16、0.5/0.35→>1.6 不发射；μ_shell 无影响（球 geom `priority=1` 覆盖）。
- Impact: 送球门槛从 0.94 降到 0.46 N·m（−51%），转速门槛从 120–140 rpm 降到 90 rpm，但仍**只压在 SRS V2 UltraSpeed 7.4 V 线性包络边界**（该转速下模型可用 0.416 N·m）——属**边界可行**，**不得判定单只 SRS V2 直驱安全**，必须台架实测。二指转子**尚未进入 CAD**：`cad/paddle_launcher_feeder_redesign.py` 仍生成原三指转子，改 CAD 前需先经用户确认方案示意。
- Reversible?: 是；B/C 负结果以 `superseded` 方式归档，保留原始数据与判据以便复算。
- Date/version: 2026-10-03 / C06B-POLLEN-FEEDER-V2 候选修订（待用户接受）

## DEC-0026 - 送球门槛改用 12 s 统一预算重测；舵机问题由「不可行」改判为「可行」，推荐 25-4 Super Speed + R5

- Decision: 送球门槛的仿真预算由 7 s（单入口 x=145）统一改为 **12 s 且双入口（x=145 与 x=138）**，并以此重测 R5 几何（二指 θ=350/170 + D 球窝垫 6.8 mm）；**推荐几何由 R2 改为 R5**；舵机选型推荐 **goBILDA 25-4 Super Speed @7.4 V**。DEC-0025 的「0.46 N·m @90 rpm / 边界可行 / 单只 SRS V2 不得判定安全」结论记为 **SUPERSEDED**；其相对排序（A 唇口喇叭有效 −23%、D 球窝抬高有效 −28%、B 托板缩进无效、C 叶尖卸载恶化 +33%）与根因分析保留有效。
- Reason: 旧 7 s 预算下，30/40/60/70/75/145 rpm **即使把力矩限幅给到 3.0 N·m 也判失败**；把预算延长到 12 s 后这些转速**全部成功发射**。机理不是扭矩不足，而是**球在球窝里蠕动**：球滚下托板后停在球窝边缘（r≈83–95.5 mm，θ≈322–328°），要等指片转到才被抓住——40/50 rpm 首抓约 0.6 s，70 rpm 约 4.2 s。旧门槛 0.94 / 0.46 因此把「球还没被抓住」的耗时混进了力矩门槛，不是纯粹的发动力矩需求。
- Alternatives considered: (a) 保留 7 s 口径只调扭矩——会把「球还没被抓住」错判成「扭矩不够」，已用 3.0 N·m 仍失败反证否掉；(b) 只延长到 10 s——70 rpm 首抓约 4.2 s，余量偏薄，取 12 s；(c) 单入口 x=145——会漏掉入口位置敏感性，改为双入口取较坏值。
- Evidence/calculation: `simulation/mujoco/out/_r2r5_speed_req12.json`（R5，双入口，二分容差 ±0.03 N·m）门槛（N·m）：40/50 ≤0.24（0.24 是扫描下限，真实值 ≤0.24）、60 → 0.339、75 → 0.439、90 → 0.24、105 → 0.24、120 → 0.289、130 → 0.356、**145 → 0.472（最坏点）**、160 → 0.323、200 → 0.273、290 → 0.306。预算敏感性 `simulation/mujoco/_work/diag_lowrpm.py`、`_work/r5_lowrpm.py`；包线与舵机判定图 `simulation/mujoco/out/servo_envelope_zh.png`（脚本 `_work/servo_envelope_zh.py`）。R5 在 90/105 rpm 门槛仅 0.24，明显优于 R2。舵机换算 1 kg·cm = 0.0980665 N·m；厂家扭矩为堵转值，可用扭矩沿堵转→空载直线插值。
- Impact: 舵机问题由「不满足」改判为 **可行**。7.4 V 逐只判定：25-4 Super Speed（堵转 0.530 N·m / 空载 290 rpm）窗口 30–70、80–122 rpm → **推荐**（唯一能上 120 rpm，90–105 rpm 余量 >40%，避开 70–80 rpm 缺口）；25-3 Speed（1.059 / 145）30–110；Axon MAX MK2（3.825 / 100）30–94，低速余量最大；25-2 Torque 与 25-2 5-Turn（2.471 / 60）30–53，可用但慢（约 1.2 s/球）；旧参考件 REV SRS V2 UltraSpeed（0.608 / 285.7）30–125，**此前误判为不可行，现同样可用**。新增开放项：送球**相位敏感**——结论随拨杆转速经「指片—球到达相位」耦合，相邻 10 rpm 即可翻转（145 rpm 单入口过、双入口不过），拨杆转速必须锁在窗口内稳态运行；根因仍未解决——球停在 r≈95.5 mm 而设计轨道 R=58.4 mm，**差 37.1 mm**，送球仍靠叶尖拖拽而非输送轨道（DEC-0025 根因，本轮未改）。
- Reversible?: 是；旧 7 s 数字在 `config/parameters.yaml` 以 `SUPERSEDED` 标签连同原始 source 保留，可随时复算对比。
- Date/version: 2026-10-03 / C06B-POLLEN-FEEDER-V2

## DEC-0027 — 送球段「平滑曲面」优化（R6）与蠕动根因：卡滞在停位球窝，不在接合处台阶

- Decision: 新增候选几何 **R6**：取消 R5 的 30×108×12.8 平垫块，把外罩内弧（r = R_IN = 93.96 mm，圆心 = 拨杆轴 29.49/111.46）从 225° 唇口沿同一半径平滑延伸到 **260.2°**，终点落在托板顶面 x = 13.5 mm（z = 18.87 mm，该处抬升 0.0 mm、与托板相切）；弧面块用 12 段 box 近似，与 `shell_*` 同类。**R5 保留不删**，与 R6 并列记录；R6 标为**候选，待用户接受**。两种几何都仅存在于 MuJoCo 仿真，**均尚未进入 CAD**。
- Reason: 用户 2026-10-03 指令「采用 goBILDA 25-4 Super Speed（0.530 N·m / 290 rpm），尝试对 R5 优化，把外罩和球窝垫用平滑曲面连接，看会不会效果更好、尽量减少球的蠕动」。仿真给出的答案是**不能**：抓球前等待 2.98 s → 2.93 s（仅 −1.7%，在噪声量级），全程 7.49 s → 7.38 s（−1.5%）。因此本决策记录的是「R6 有效但微小 + 蠕动根因另有他处」，而不是把 R6 当作已解决的问题。
- Alternatives considered: (a) R5 原样（二指 θ=350/170 + 6.8 mm 平垫块，基线，保留）；(b) **R6** 弧面延伸到与托板相切（本决策，推荐用于「本来就要改版」的场合，因为它少一个零件、无台阶）；(c) R6c 弧面止于 256° 且半径收窄 2 mm（全程再快 0.26 s / 3.5%，但球窝变窄、对球径与公差更敏感，未推荐）。三者均一次通过全流程（launched=True），出口球速 6.67 m/s、飞轮 1620 rpm，无失败工况可区分优劣，只能按时间排序。
- Evidence/calculation: 图 `simulation/mujoco/out/r5_vs_r6_smooth_zh.png`（脚本 `_work/r6_fig_zh.py`）；数据 `_work/r6_summary.py` → `out/_r6_summary.json`、`out/_r6_fig_data.json`。电机模型 `_work/r6_motor.py`：把 `paddle_vel` 的 `kv` 由 0.08 换成 25-4 的真实线性斜率 kv = 0.530 /(290·2π/60) = 0.017452、`forcerange` 改为 ±0.530、`ctrl` = 空载 290 rpm（即全油门直流电机线 T = T_stall(1 − ω/ω_free)）；球从托板 x = 145 mm 滚入，12 s 预算。结果（s，抓球前蠕动 / 运载 / 放球—发射）：R5 2.98 / 3.72 / 7.49；R6 2.93 / 3.66 / 7.38；R6c 2.99 / 3.46 / 7.23。运载段实测（拨杆转速 / 输出力矩均值）：R5 3.95 rpm / 0.523 N·m；R6 4.05 rpm / 0.523 N·m；R6c 4.36 rpm / 0.522 N·m。
- Evidence/calculation（蠕动根因，独立复测）: `_work/r7_loadprobe2.py` 用同一 R5 几何把拨杆换成刚性速度源（kv = 0.08、指令 145 rpm、限幅放宽到 ±5 N·m），运载段拨杆仍只有约 6.8 rpm、出力约 1.16 N·m；球心半径实测 59.4 mm（设计 R_CARRY = 58.4 mm）。**蠕动发生在球停稳后的停位球窝**：球停稳在 r ≈ 83–95 mm、角 ≈ 322–329°，被指片楔住，把拨杆拖到几 rpm，等楔口松脱（约 2.3 s @145 rpm 指令）才被指片带入运载轨道。接合处的台阶在蠕动时段根本不参与接触。
- Impact: (1) 「外罩—球窝接合处形状」被证伪为蠕动的成因，**不得再作为缩短循环时间的手段**；有效方向是改**停位球窝**（让球停在指片扫掠范围之外）或提高伺服扭矩。(2) 舵机余量口径需重开：DEC-0026 的 `paddle_torque_threshold_12s_by_rpm` 由 kv = 0.08 的假执行器取得，「通过」只表示在限幅内 12 s 跑完，与真实电机模型的扭矩余量不是同一件事；本决策只主张「25-4 全油门模型下运载段拨杆约 4 rpm、出力 0.523 N·m 已贴 0.530 N·m 堵转，余量很薄」，**不主张 DEC-0026 的 0.24 N·m 数字作废**（两者口径不同，不可直接相除比较）。(3) 卡滞力矩在仿真里对接触正则化与到达相位敏感（同一几何在 3.95 rpm 与 6.8 rpm 下分别读出 0.52 与 1.16 N·m），上述绝对值只能当量级参考，**不得作为选型定论**。(4) R6 若被接受，需在 `cad/paddle_launcher_feeder_redesign.py` 增加「弧面替换平垫块」的生成逻辑；**不得改** `cad/paddle_launcher_constrained.py`、不得覆盖原 STEP。
- Reversible?: 是。R5 与 R6/R6c 的几何、脚本与数据全部保留，可随时复算对比；被替代方案以本记录链接，不删除历史。
- Date/version: 2026-10-03 / C06B-POLLEN-FEEDER-V2（R6 候选，待用户接受）

## DEC-0028 — 球—外罩摩擦系数估算（μ≈0.40）与「送球靠摩擦拖拽」的定量判定

- Decision: 光面塑料球对 **0.4 mm 层高 FDM 打印 PET 外罩** 的滑动摩擦系数取 **μ = 0.40**（合理区间 **0.30–0.50**），标 `ASSUMED`，作为本轮仿真输入。在该摩擦下重跑 **R5**（二指 θ=350/170 + D 球窝垫 6.8 mm）全流程，结果是 **未能送入运载轨道**（20 s 预算内未发射）；扫描得到送球成功的摩擦门槛为 **μ ≈ 0.65**。因此把结论定为「现有 R5 送球几何靠拖拽而不靠轨道，实物磨擦做不到这个数字」，并把修正方向收敛到「把球抬到运载半径再让叶片用法向力推」，而不是继续调摩擦假设或改外罩—球窝接合处形状（DEC-0027 已否定后者）。
- Reason: 用户指定「塑料球是光面的，外罩是一般 3D 打印层高 0.4 mm 的 PET，估一下摩擦系数，随后跑仿真」。此前所有通过全流程的结论（DEC-0024–0027）都是在 `ball` class 的 `friction="1.0 ..."`（priority=1，覆盖其他所有接触）下取得的，而 1.0 对光面塑料对塑料是不现实的（接近橡胶）。本记录把输入换成实物可得值后重新判定，避免把一个靠假摩擦才成立的几何误当作已验证方案。
- Alternatives considered: (a) 沿用 μ=1.0 旧基线（被本记录否定为非物理输入）；(b) μ=0.40 全局作用于球的所有接触（本记录采用，得到失败结论）；(c) 逐对摩擦模型——球对打印件 0.40、飞轮另给 priority=2 保留自身高摩擦（已跑，与 (b) 逐位相同，说明发射轮不是瓶颈）；(d) 只改摩擦不动几何并把吹程延长（20 s 已给足，仍失败）。
- Evidence/calculation: 仿真入口 `simulation/mujoco/_work/r9_strike_zh2.py`、`_work/r9_clean.py`；数据 `simulation/mujoco/out/_r9_clean.json`，图 `simulation/mujoco/out/r9_mu_verdict_zh.png`。口径：R5 几何 + 托板延长到 x=185 mm 并在 x=188 mm 设止挡板（避免球被弹出托板后永久丢失），球从 x=145 mm 自然入料，飞轮 1620 rpm，拨杆用 25-4 真实线性模型（kv=0.017452、限幅 ±0.530 N·m），20 s 预算。结果（μ → 出球时刻 / 出球速度 / 拨杆中位转速 / 卡滞时间占比 / 球最小半径）：0.40 → **未发射** / 281.9 rpm / 36% / 86.0 mm；0.50 → **未发射** / 8.7 rpm / 54% / 86.1 mm；0.60 → **未发射** / 8.4 rpm / 77% / 93.7 mm；0.70 → 15.69 s / 6.35 m·s⁻¹ / 3.3 rpm / 76% / 54.3 mm；0.80 → 8.54 s / 6.42 / 281.9 / 40% / 54.3；1.00 → 7.50 s / 6.67 / 281.9 / 35% / 54.3。**门槛 μ ≈ 0.65**；出球速度在 μ=0.70–1.00 区间几乎不变（6.35–6.67 m·s⁻¹，52°）→ **飞轮发射能力本身不受影响，瓶颈全在送球段**。轨迹机理（同一脚本，4 s 分辨）：μ=0.40 时球从 x=145 滚到 r≈95.9 mm（t=0.328 s，paddle_flex_2 指尖）被擦打后被弹回，在 x≈100–150 mm、r≈86–128 mm 之间来回摆动而不前进；μ=1.00 时同一撞击被“咬住”，t=2.088 s 时球心已到 r=56.0 mm（设计 58.4 mm）并被带入运载轨道。摩擦系数估算依据：光面塑料对光面塑料干摩擦 μ≈0.2–0.3；FDM 0.4 mm 层高在 45° 壁面上形成峰谷 0.1–0.2 mm 的层纹，使表观 μ 抬升到 0.35–0.55；取中值 **0.40**，区间 **0.30–0.50**，对本设计而言“最坏情况”是低端 0.30。**误差记录**：第一版止挡板放在 x=153 mm，而球心在 x=145 mm 时球尾已伸到 x≈180.6 mm，挡板**在 t=0 就贯穿球**，该批数据作废并已重跑（新口径含 t=0 无接触自检 `t0_contacts=tray`）。
- Impact: (1) 「R5 可行」的旧结论仅在 μ≥1.0 成立，**不得再作为设计依据**；DEC-0026 的力矩门槛与舵机选型结论依然成立，但它们描述的是「假设能拓住球之后的起步力矩」，**不包含拓住球本身的可行性**；(2) 送球段修正方向收敛为「把球的停位抬到运载半径（r≈58.4 mm，即球外表面贴上外罩内弧 r=93.96 mm），让叶片用**法向力**推球」，而不是继续靠指尖摩擦拖拽；已知的 37.1 mm 半径差（DEC-0025）就是这个瓶颈；(3) 即使拖拽成功（μ≥0.7），运载段拨杆只有 3.3–8.5 rpm、卡滞占比 76–77%，说明即使强行靠摩擦也会把 25-4 压在堵转附近，与 DEC-0027 的「余量很薄」一致；(4) 本记录不主张实物 μ 就是 0.40，只主张「实物可得的 μ 不会到 0.65」，所以**必须台架实测摩擦系数**才能把本条从 `ASSUMED` 升为 `MEASURED`；(5) R5/R6 仍**未进 CAD**，本记录不触及 `cad/paddle_launcher_constrained.py` 与原 STEP。
- Reversible?: 是。所有 μ 档位的脚本、JSON 与图均保留，可随时复算；被取代的 μ=1.0 基线以本记录链接保留，不删除。
- Date/version: 2026-10-04 / C06B-POLLEN-FEEDER-V2（DEC-0028）

```text
Decision:
Reason:
Alternatives considered:
Evidence/calculation:
Impact:
Reversible?:
Date/version:
```

## DEC-0029 — T06 NECTAR 送球段 a' 定稿：托盘与运载圆精确相切（Δ = R_in − d0）、唇口 275°、桨毂 Ø24、飞轮夹口取 NECTAR 文件的 82 mm

> **部分 SUPERSEDED by DEC-0030**：本条的**叶片数量与相位**（三叶 18/138/258）已被取代 —— R28 证明 258° 那片叶落在 275° 唇口/入料口前缘，把 91.9 mm 球推回托盘并卡死（堵转时间占比 80%）。相切托盘（Δ = 17.142 mm）、唇口 275°、桨毂 Ø24、夹口 82 mm 的内容**继续有效**；R25 的生成器已标 SUPERSEDED，其 STEP/STL 只作历史保留。

- Decision: 为 NECTAR 球（D = 91.948 mm）定稿送球段几何集 **R25**，写进派生脚本 `cad/paddle_launcher_feeder_a_prime_nectar.py`（父模块 `cad/paddle_launcher_constrained.py`、a' POLLEN 脚本 `cad/paddle_launcher_feeder_a_prime.py` 与原 STEP 一律不改）：
  1. **托盘与运载圆必须精确相切**。托盘顶面（过 `PIVOT`、倾角 5°）到桨轴的距离记为 `d0`，球心运载半径记为 `R_CARRY`，外壳内弧记为 `R_in = R_CARRY + BALL_R`。当且仅当 `d0 = R_in` 时球滚到托盘末端正好落在运载圆上；否则球在托盘末端比运载圆高 `R_in − d0`，落下后撞唇口弹回并卡死。现有托盘实测 `d0 = 90.832 mm`（`(PADDLE_CZ−PIVOT_Z)·cos5° − (PADDLE_CX−PIVOT_X)·sin5°`），故整块托盘必须沿自身法线 `(sin5°, −cos5°)` **外移 Δ = R_in − d0**：R25 取 `R_CARRY = 62.0 mm` → `R_in = 107.974 mm` → **Δ = 17.142 mm**，新 `PIVOT = (−0.806, 0.423) mm`。
  2. **外壳唇口角 = 275.000°**，等于 `atan2(−cos(tilt), sin(tilt))`，与球径、与 `R_CARRY` 都无关；它与托盘新切点 `(38.901, 3.897) mm` 重合，托盘左端裁到该 x（`TRAY_X0 = 38.901 mm`），右端保持 `x = 150 mm`。
  3. **桨毂由 Ø36 缩到 Ø24**（radius 18 → 12），桨臂内端由 r=14 延到 r=10 以保持与毂搭接；球窝与毂的间隙由 0.03 mm 放宽到 **4.026 mm**（`R_CARRY − HUB_R − BALL_R`）。
  4. **飞轮夹口取 NECTAR 文件的 82 mm**（用户 2026-10-04 明确指示「nectar 的间隙使用 nectar 文件的」），即 `half_spacing = 89 mm = 82/2 + WHEEL_R(48)`；对 D=91.948 的球是 9.9 mm 过盈。此前 R13–R22 的 NECTAR 仿真沿用 POLLEN 的 `HALF_SPACING = 80`（夹口 64 mm，过盈 27.9 mm），夹口口径是错的。
- Reason: 用户指令「进行 a 修改，同时该结构也需要是上传文件中的球通过送球机构，按已有经验进行修改」。DEC-0028 已判定 POLLEN 的 a' 方向是唯一能绕开摩擦门槛的路线（把球抬到运载半径、让叶片用法向力推球）。把同一配方搬到 NECTAR 时，前三轮（R20/R21/R22）连续卡死；R23 的几何推导指出根因不是球径本身，而是 **托盘平面到桨轴的距离跟着球径一起变大后没有跟着补偿**：POLLEN 的 Δ 只有 3.13 mm（1.1 mm 落差，可容忍），NECTAR 的 Δ 是 13.5–19.1 mm，13 mm 级的落差足以让球在唇口弹回并永久卡住。定下「相切」这条充要条件后，托盘外移量、切点位置、唇口角都能一次算准，不再需要试凑。
- Alternatives considered: (a) 不改托盘、只改桨毂或球窝半径 —— 被 R23 否定：`R_in` 只会更远离 `d0`，落差更大；(b) 保留 POLLEN 的夹口 64 mm —— 对 91.9 mm 球是 27.9 mm 过盈，既不是 NECTAR 文件的几何，也与用户指示冲突；(c) 把整个发射部分（桨轴 + 飞轮）下移 Δ 而保持托盘不动 —— 同样满足相切，但会把飞轮与底盘、与上游接口一起挪动，改动面比挪托盘大得多；(d) 桨毂保持 Ø36（R24 的 H1/H2 中间方案）—— 仿真仍能发射，但托盘要外移 25.1/21.1 mm、出球要 11.7/8.8 s、卡滞 43 %/31 %，劣于 Ø24。均不采用。
- Evidence/calculation:
  - 充要条件的推导与数值见 `simulation/mujoco/_work/r23.py`（`plane_dist()`、`tangent_setup()`）；`d0 = 90.832 mm`、`R_in = 107.974 mm`、`Δ = 17.142 mm`、切点 `(38.901, 3.897) mm`、`a_lip = 275.000°`、新 `PIVOT = (−0.806, 0.423) mm`，全部 `CALCULATED`。
  - 球径与质量：`BALL_D = 91.948 mm`、`vol = 43129.8 mm³`、2 个实体（`MEASURED`，回读 `am-5852_blue Blue Alliance Nectar.STEP`）；质量 `BN_MASS = 0.130 kg`（`ASSUMED`，按中空塑料球估计，未称重）。
  - **R23（SIMULATED）**：四组配置全部发射成功 —— G1（毂 r=12、R_CARRY=58.4、夹口 82、60 rpm）`launch=True, exit_t=4.016 s, v=4.698 m/s, 51.11°, 卡滞 10 %`；G2（同 G1、90 rpm）`3.616 s, 4.733 m/s`；G3（毂 r=18、R_CARRY=64）`6.316 s, 4.732 m/s, 50.71°, 卡滞 21 %`；G4（G3 预置）`6.05 s, 卡滞 67 %`（仅对照）。数据 `simulation/mujoco/out/_r23_nectar_gravity.json`。
  - **R24（SIMULATED，桨毂中间方案对比，60 rpm、μ=0.40、夹口 82、25 s）**：H1（毂 Ø36、R_CARRY=70、Δ=25.142）`launch=True, exit_t=11.728 s, v=4.712 m/s, 卡滞 43 %`；H2（毂 Ø30、R_CARRY=66、Δ=21.142）`8.784 s, 4.742 m/s, 卡滞 31 %`；**H3（毂 Ø24、R_CARRY=62、Δ=17.142）`launch=True, exit_t=3.264 s, v=4.740 m/s, 51.93°, 卡滞 8 %`** ← 采用。三种配置的球窝最小半径分别为 65.9 / 65.9 / 62.0 mm。数据 `simulation/mujoco/out/_r24_nectar_trade.json`。
  - 三类仿真口径统一为：MuJoCo 3.14.0、60 rpm 拨杆（sign=+1，前视逆时针）、`mu = 0.40`（DEC-0028 的 `ASSUMED` 值）、`forcerange = ±0.530 N·m`、`CTRL = 290 rpm`（25-4 Super Speed 线性 T–n 模型）。**判定量用 `launched` / `exit.t` / `exit.speed_m_s` / `jam`，不用 `peak_speed_m_s`（含自由落体）。**
  - 几何自检（生成脚本在**导出前的最终实体**上测）：`nest_ball_clash_with_shell_mm3`、`nest_ball_clash_with_hub_mm3`、`shell_tray_clash_with_kept_parts_mm3` 全为 0；`hub_clearance_mm = 4.026`；单件 STEP 回读见 `cad/output/inspection/`。
  - 图：`cad/output/_r25_nectar_final_zh.png`（定稿剖面 + Δ 对比 + R23/R24 结果）；`cad/output/_r23_gravity_handoff_zh.png`（相切推导）。
- Impact: (1) NECTAR 从「a' 配方不适用」改判为 **可发射**，且比 POLLEN 的 a' 少一个不确定项（POLLEN 靠 1.1 mm 容忍度，NECTAR 是精确相切）；(2) 托盘、外罩、桨毂都要改 —— 托盘外移 17.142 mm 并裁到 x=38.901 mm，外壳扇区由 142–225° 改为 142–275°，桨毂 Ø36→Ø24 且桨臂内端延到 r=10；(3) **R13–R22 的 NECTAR 结论全部作废**（夹口写成 64 mm 且托盘未移），保留文件但不得再引用；(4) DEC-0028 的 `feeder_fix_direction_friction_based` 在 NECTAR 上**已落实**（球停在 r=62 mm 运载圆上、由叶片法向推），在 POLLEN 上仍未落实；(5) μ=0.40 仍是 `ASSUMED`，台架实测项不因此关闭；(6) 9.9 mm 夹口过盈是 NECTAR 文件的既有几何，本轮只做运动学验证，**不构成对球或飞轮的结构强度结论**。
- Reversible?: 是。托盘外移量、切点、唇口角都由 `R_CARRY` 一个参数决定（`Δ = R_CARRY + BALL_R − d0`），改 `R_CARRY` 即可整套重算；R23/R24 的脚本、JSON 与图全部保留可复算。若回到「不挪托盘」的旧路线，须新增决策记录并保留本条，不得静默替换。
- Date/version: 2026-10-04 / C06B-FEEDER-A' -NECTAR-R25

## DEC-0030 — T06 送球段「一套机构兼容两种球」：两叶 330°/150° + 索引式循环，只有飞轮夹口随球改变

- Decision: NECTAR（D = 91.948 mm）与 POLLEN（D = 71.120 mm）**共用同一套送球段**，两个版本之间**只有飞轮夹口改变**：NECTAR **82 mm**（轴距 89 mm，取自 nectar 文件）、POLLEN **64 mm**（轴距 80 mm，原文件值）。共用几何量全部由**大球**定：外罩内弧 `R_IN = 107.974 mm`、扇区 **142–275°**、壁厚 7 mm、宽 108 mm、5° 托盘与外罩内弧**精确相切**（切点 x = 38.901 mm，右端 x = 150 mm）、桨毂 **Ø24**、桨臂 r = 10..46、叶片 r = 46..58、TPU 尖 r = 56..60。**拨杆由三叶（18/138/258）改为两叶 330°/150°**，并用**索引式循环**驱动：停 ≥ 1.2 s 让球自流进球窝 → 一次扫掠 **240–260°**（290 rpm）→ 释放。生成脚本 `cad/paddle_launcher_feeder_a_prime_shared.py`（父模块与既有 a'/POLLEN/NECTAR 脚本、原 STEP 均不改）。
- Reason: 用户指令「nectar 和 pollen 使用的是同一个装置，只有飞轮间隙会改变，确保修改后的输送部分能兼容两种尺寸的球并将它们高效送入发射部分」。R28 对照实验证明 CAD 原有的三叶布置**对 NECTAR 直接失败**：258° 那片叶正落在 275° 唇口/入料口前缘，大球停在托盘上（r≈93 mm）时只被该叶的外前侧碰到，接触法线朝外，把球推回托盘并卡死（80% 时间在堵转）。两叶 330/150 把 **275°→142° 的入料走廊完全让开**，两种球都能先自流到球窝再被扫掠；又因为大球在共用外罩内的静止半径（62.0 mm）与小球（72.4 mm）不同，只有"共用外罩 + 让开走廊 + 指数式一次扫掠"这一组合能让同一套零件对两种球都成立。
- Alternatives considered: (a) 三叶 18/138/258（R25 现状）—— 被 R28 否定（NECTAR 卡死 80%）；(b) 两叶 10/190 —— R29 可用，但入料 x = 108/118 且停时 1.2 s 时 POLLEN 会失败（相位敏感、余量小），劣于 (c)；(c) **两叶 330/150 —— 采用**；(d) 连续旋转代替索引式 —— 被 R27/R29 否定：连续转时拨杆会撞上飞轮室里尚未离开的球，停时与入料位置都失去余量；(e) 两种球各做一套送球段 —— 与用户"同一个装置"的指令冲突。
- Evidence/calculation:
  - 脚本 `simulation/mujoco/_work/r28.py`（布置对照）、`r29.py`（48 组鲁棒性网格）、`r30.py`（12 组余量）；数据 `simulation/mujoco/out/_r28_layouts.json`、`_r29_grid.json`、`_r30_margin.json`。
  - **R28（SIMULATED）**：三叶 18/138/258 → NECTAR `launched = False`，球卡在 r = 67.3 mm / 295°，堵转时间占比 80%；两叶 330/150 → NECTAR `t = 2.80 s, v = 4.63 m/s, 49.8°`，POLLEN `t = 2.30 s, v = 5.93 m/s, 49.9°`。
  - **R29（SIMULATED，48 组）**：`home × 扫掠(180/200/248°) × 入料 x(98/108/118/128) × 停时(1.2/1.8 s)`。330/150 + 总扫掠 ≥ 248° 的 16 组**两种球全部通过**；扫掠 180/200° **一律失败** → 240–260° 的总扫掠量是必需的。
  - **R30（SIMULATED，12 组，停时 3.0/5.0 s、入料 x = 98/128、扫掠 240/248/260°）**：**12/12 全通过** —— NECTAR `t = 4.00/6.00 s, v ≈ 4.64–4.68 m/s, 卡滞 10%`，POLLEN `t = 3.40/5.40 s, v ≈ 5.87–6.13 m/s, 卡滞 0%`。停留时间与入料位置都有很大余量。
  - 仿真口径：MuJoCo 3.14.0、μ = 0.40（DEC-0028 的 `ASSUMED` 值）、飞轮 1620 rpm、拨杆 25-4 Super Speed 线性模型（kv = 0.017452、限幅 ±0.530 N·m）、无输出预算 12–25 s；判定量用 `launched` / `exit.t` / `exit.speed_m_s`，卡滞用「扭矩 > 0.40 N·m 的时间占比」。
  - 共用性核验（KNOWN）：`cad/paddle_launcher_constrained.py` 全文**不出现球径参数**，外罩/托盘/拨杆都不引用 `BALL_R` / `BALL_D`；共用脚本只把飞轮轴距 `half_spacing = nip/2 + WHEEL_R(48)` 按 variant 传入 → **两版实体差异只有飞轮夹口**（89 − 80 = 9 mm 单侧 / 18 mm 夹口差）。
  - 产物：图 `cad/output/_t06_shared_feeder_zh.png`（四联：共用剖面 + 两球各自静止半径 / 叶片布置 vs 入料走廊 / 两球球心半径历程 / 鲁棒性网格）；STEP `cad/output/paddle_launcher_feeder_a_prime_shared_{nectar,pollen}.step`；报告 `cad/output/paddle_launcher_feeder_a_prime_shared_report.json`；单件 `cad/output/inspection/_r26_shared_{paddle_hub,feeder_shell_tray}.step`；几何检验 spec `config/t06_feeder_aprime_shared_{hub,shell}_checks.json`。
  - **CAD 导出实测（MEASURED，读自导出前的最终实体）**：夹口 `flywheel_nip_measured_mm` = **NECTAR 82.000 / POLLEN 64.000**，4 对飞轮逐一等于目标 `2·half_spacing − WHEEL_OD`（量法：飞轮缘部三角化点云沿 52° 通道法线投影，容差 0.5 mm。飞轮的精确 B-rep 距离 `Shape.distance()` 在辐条轮上**病理级慢**，单次 > 6 min 不收敛，已弃用并在脚本内注明）；毂—外罩内弧 **95.974 mm**（两变体相同，目标 95.974），毂∩外罩 = 0 mm³；停位球 ∩ 外罩 / ∩ 毂两球全为 **0 mm³**。
  - **「同一装置」的充要证据（KNOWN）**：两变体导出的外罩体积 **267723.34 mm³ 完全相同**、外罩 bbox 完全相同、毂—外罩 95.974 相同 → 差异**只剩**飞轮轴距（89 vs 80）与由它决定的运载半径（62.000 vs 72.414）。`paddle_launcher_feeder_a_prime_shared_report.json` 的 `shared_check` 对本组等式逐项判定为 true。
  - **几何检验（MEASURED，`tools/inspect_geometry.py`，目标取自 `config/parameters.yaml` 而非被测件）**：`cad/output/inspection/t06_shared_R026_hub.json` = **pass 6/6**；`t06_shared_R026_shell.json` = **pass 7/7**。
  - **新测出的既有干涉（MEASURED，开放项，待用户决策）**：共用外罩与**保留的父级结构**仍有交叠 —— `shooter_throat_+55` **5717.5 mm³**、`guide_roof_3` **126.5 mm³**，两变体数值相同。性质是**继承而非回归**：R25 的 NECTAR 外罩对 `guide_roof_3` 就是 1727.2 mm³（R26 降到 126.5 mm³），外罩对 `shooter_throat_+55` 此前从未测过（`shell_tray_clash_with_kept_parts_mm3` 是本轮新增的键）。送球功能不受影响（R29/R30 即用这套几何跑通），但实物装配时外罩会与喉道上导板相碰。交叠位于球道**外侧**（r > 108 mm，球外表面最大到 107.974 mm），所以让位布尔不会碰到球道。
- Impact: (1) 送球段不再按球分两套 —— BOM 与装配**只剩"换飞轮垫片"这一项差异**，符合"同一个装置"的实物约定；(2) **拨杆冻结为两叶 330°/150°，且必须索引式驱动**，连续旋转不可用；(3) DEC-0029 的叶数与相位被本条取代（相切托盘 / 唇口 275° / 桨毂 Ø24 继续有效），R13–R25 的 NECTAR 文件全部保留但只作历史；(4) `cad/paddle_launcher_feeder_a_prime_nectar.py`（R25 三叶生成器）已标 SUPERSEDED，运行即退出，不再产生与仿真口径不一致的几何；(5) μ = 0.40 仍是 `ASSUMED`，台架摩擦实测项**不因此关闭**；(6) 索引式循环需舵机控制实现（停—扫—停）与实物验证，尚未关闭。
- Reversible?: 是。叶片相位、扫掠量、停时、入料位置都是可复算输入（r28/r29/r30 三个脚本 + opt_lib 复用），任意改动都能重跑验证；旧三叶几何与 R13–R25 的文件、JSON、图全部保留，仅以本条链接取代，不删除历史。
- Date/version: 2026-10-04 / C06B-FEEDER-A-PRIME-SHARED-R26


## DEC-0031 — T06 共用外罩 R27 让位：对既有干涉的保留父级件做 0.5 mm 间隙布尔切除（只削球道外侧）

- Decision: 在 DEC-0030 的共用送球段（R26）之上，把**保留的父级结构**穿进外罩的那部分料直接切掉，做成 **R27**：对 `shooter_throat_+55` 与 `guide_roof_3` 各自先**外扩 0.5 mm**，再用外扩体对 `feeder_shell_tray` 做布尔差。切削区全部位于球道**外侧**（r > R_IN = 107.974 mm），球实际接触的内弧面不被触碰。生成器 `cad/paddle_launcher_feeder_a_prime_shared.py` 新增常量 `RELIEF_PARTS = ("shooter_throat_+55", "guide_roof_3")`、`RELIEF_CLEARANCE_MM = 0.5`，以及报告键 `shell_relief`。
- Reason: R26 首次把「外罩 ∩ 保留件」纳入测量后发现既有干涉 —— `shooter_throat_+55` **5717.5 mm³**、`guide_roof_3` **126.5 mm³**（两变体数值相同）。这是**继承而非回归**：R25 的 NECTAR 外罩对 `guide_roof_3` 就是 1727.2 mm³，而外罩对 `shooter_throat_+55` 此前从未测过（该键 R26 才加入）。送球功能不受影响（R29/R30 用这套几何跑通），但**实物装配时外罩会与喉道上导板相碰**，属于必须消掉的装配冲突。
- Alternatives considered: (a) 不动几何、装配时手工修锉或加垫 —— 被否，不可复算、不可复现，且违反「几何必须能独立生成和验证」；(b) 用保留件的**原始实体**直接做布尔差（零间隙）—— 被否，打印件与外罩表面贴合、没有装配间隙，0.4 mm 层高的 PET 会互相咬死；(c) **让位件外扩 0.5 mm 后切除**（本记录采用）；(d) 移动或删除父级导板 —— 被否，父级结构不属于本模块职责，且会破坏 T06 与上级装配的接口；(e) 只切 `shooter_throat_+55`、保留 `guide_roof_3` 的 126.5 mm³ —— 被否，1 个数量级虽小但同样是实体干涉。
- Evidence/calculation: 生成器 `cad/paddle_launcher_feeder_a_prime_shared.py`（`_grow()` / `_relieve_shell()`）；报告 `cad/output/paddle_launcher_feeder_a_prime_shared_report_{nectar,pollen}.json` 的 `variants.<v>.shell_relief`。**CAD 导出实测（MEASURED，读自导出前最终实体，两变体逐位相同）**：
  - `relief_targets_removed_mm3` = `shooter_throat_+55` **5717.5021** / `guide_roof_3` **90.8564**；
  - `relief_clearance_mm` 两者均为 **0.5**（说明外扩成功生效，而不是静默回退成零间隙切割）；
  - 外罩体积 **267723.34 → 260374.21 mm³**（净削 **7349.13**，其中 90.8564 是 roof 的真实交叠、其余是喉咙件扣除重叠后的净去除量，两者之和大于净削量说明两个切削体在外罩内互相重叠）；
  - `shell_tray_clash_with_kept_parts_mm3` = **0**、`shell_tray_clash_hits` = **{}**（R26 的 5717.5 / 126.5 归零）；
  - 球道未受影响：`nest_ball_clash_with_shell_mm3` = 0、`nest_ball_clash_with_hub_mm3` = 0，新增的**球道扫描自检** `sweep_ball_clash_with_shell_max_mm3` = **0**（沿 142°→275° 运载弧取 19 个球心位姿，逐点求 球∩外罩 体积取最大）；
  - `shell_bbox_after_mm` = [-85.484, -54.0, -3.514, 150.261, 54.0, **180.043**]：**只有 zmax 从 182.245 变到 180.043**（-2.202 mm，被挖掉的是外罩上缘伸出到导板上方的那一小块），xmin/xmax/ymin/ymax/zmin 全部不变；`paddle_hub_to_shell_inner_arc_measured_mm` = **95.974** 不变，`flywheel_nip_measured_mm` = NECTAR 82.000 / POLLEN 64.000 不变。
  - **几何检验（MEASURED，`tools/inspect_geometry.py`，目标取自 `config/parameters.yaml` 而非被测件）**：`cad/output/inspection/t06_shared_R027_hub.json` = **pass 6/6**；`t06_shared_R027_shell.json` = **pass 7/7**。其中 `T06-APS-SHELL-004` 由 `bbox_max` 改为 `group_bbox` + `axis=z` + `rule=le` + `target=185.759`（= 原 182.245 加上扇形包络跨度 3.514，脚本质硬编码 `bbox_max` 为绝对值比较，无法表达 `le`）。
  - 图 `cad/output/_t06_shared_relief_r27_zh.png`：(a) 让位上下文 3D（外罩 + 两个被让位件）；(b) 中截面俯视，标出球道内弧 107.974 / 外弧 114.974 与让位发生的位置。
  - **教训（已写进代码注释）**：`BRepOffsetAPI_MakeOffsetShape.PerformByJoin` 必须**逐 solid** 调用。把部件作为 **compound** 喂进去，OCCT 会当成「外表面的偏移」而返回**更小**的实体（实测 compound 38596 → 20737 mm³），第一版 R27 因此静默回退成零间隙切割 —— 所以 `_grow()` 现在逐 solid 外扩并显式校验 `fused.Volume() > shape.Volume()`，报告里另存 `relief_clearance_mm` 作为「外扩真的生效」的证据。
- Impact: (1) R26 的「实物装配时外罩会与喉道上导板相碰」开放项**关闭**，R27 的两个 STEP 变体可直接用于装配与打印；(2) 「一套机构兼容两种球」的结论不变 —— 两变体外罩体积、bbox、让位量逐位相同，差异仍**只有飞轮夹口**（89 vs 80 mm 半轴距 → 82 vs 64 mm 夹口）；(3) 让位只发生在外罩，托盘、拨杆、运载半径、唇口 275°、出口 142° 全部未动，因此 DEC-0030 的索引式驱动结论（240–260° 扫掠、停 ≥1.2 s、两叶 330°/150°）与 R28–R30 的仿真证据**继续有效**；(4) 单件导出文件名改为 `_r27_shared_paddle_hub.step` / `_r27_shared_feeder_shell_tray.step`，另加 `_r27_shared_relief_context.step`（外罩 + 两个被让位件，供可视化）；R26 的单件与检验报告保留为历史；(5) μ = 0.40 仍是 `ASSUMED`，台架摩擦实测项不因此关闭；索引式舵机控制仍未实机实现。
- Reversible?: 是。让位由 `RELIEF_PARTS` / `RELIEF_CLEARANCE_MM` 两个常量完全参数化，改间隙或换让位件只需改常量重跑；原始外罩在脚本里由父模块重建，`_relieve_shell()` 之前的所有几何仍可单独导出；R26 的 STEP、报告与检验 JSON 全部保留，仅以本条链接取代。
- Date/version: 2026-10-04 / C06B-FEEDER-A-PRIME-SHARED-R27

## V-0032 — 验证记录（非决策）：R27 几何下两球各自正确夹口的全流程仿真复核

- 目标（KNOWN）：用户要求「对新版（R27）进行仿真，pollen nectar 都要做，使用正确的飞轮间隙」，确认无误后交用户自行复核。
- 方法（SIMULATED）：`simulation/mujoco/_work/r32.py`，复用 `pollen_v2_sim.py` + `_work/r10_cradle.py`。几何取 R27（DEC-0031），球实际接触的内弧面与 R26 逐点相同；唯一随球改变的量是飞轮半轴距 `nip/2 + 48`。
- 结果（SIMULATED，6/6 通过）：NECTAR（夹口 82）出口 t = 2.18 / 3.97 / 3.97 s、v = 4.79–4.82 m/s、出口角 50.5–51.8°、卡滞 10 %；POLLEN（夹口 64）出口 t = 1.83 / 3.38 / 3.37 s、v = 6.18–6.20 m/s、出口角 51.6–51.8°、卡滞 0–3 %。球路：α 由 323°（托板停位，r ≈ 93 mm）递减至出口 142°，共 181°。
- 让位验证（SIMULATED）：球在 142–275° 扇区内的最大外缘半径 108.474 mm（NECTAR）/ 108.650 mm（POLLEN），仅比内弧面 107.974 mm 多 0.5–0.7 mm（叶片压入量）；让位面位于 r > 107.974 mm 的球道外侧，全程无球接触 —— 与 CAD 侧 19 点球道扫描 0 mm³ 互为独立证据。
- 结论：R27 的让位**不改变**送球与发射行为；DEC-0030 的索引式驱动口径与 R28–R30 的结论继续有效。图 `cad/output/_t06_r32_fullflow_zh.png`，数据 `simulation/mujoco/out/_r32_r27_full.json`。
- 未关闭：μ = 0.40（`ASSUMED`）、球质量 0.130 / 0.060 kg（`ASSUMED`）、索引式舵机控制未实机实现、9.9 mm 夹口过盈无结构校核。
- Date/version: 2026-10-04 / C06B-FEEDER-A-PRIME-SHARED-R27（仿真复核，几何未变）

## DEC-0032 — T06 飞轮硅胶离心膨胀：垫片长度按「热态外径」配，取 dr_hot = 0.8 mm

- Decision: 承认 goBILDA `3613-0014-0096` 飞轮（Ø96 × 24，30A 硅胶，1620 rpm）在离心力下外径会变大，**装配时的轮轴间距按热态外径配**：`half_spacing = nip/2 + WHEEL_R(48) + dr_hot`，取 **`dr_hot = 0.8 mm`**（ASSUMED）。以此推出 R35 热态 CAD（`cad/paddle_launcher_feeder_a_prime_shared_hot.py`，`DR_HOT_MM = 0.8`）。送球段（外罩 + 托盘 + 拨杆）几何**与 R27 逐点相同**，只改轮轴间距；不覆盖 R27 的任何源文件或产物。**不修改拨杆或外罩几何**。
- Reason: (1) 膨胀计算给出真实量级 0.5–1.8 mm，0.8 mm 落在中位；(2) R33 实测证明「按冷态配间距」会让运行夹口变成 `nip − 2·dr`，dr ≥ 1.0 mm 起 POLLEN 出手相位被打乱、小球掉进毂—叶片夹角卡死（冷态口径 26/36）；(3) R34 实测「按热态配间距」运行夹口恒为设计值，30/30 通过、零接触。即：**问题出在装配口径，不在几何**，用垫片长度就能解决，无需改件。
- Alternatives considered: (a) 不处理，接受运行夹口缩小 —— R33 证伪（POLLEN 26/36 → 4/6 FAIL）；(b) 直接减小设计夹口以补偿 —— 会把冷态夹口改坏，且两球的补偿量不同，破坏「同一装置」；(c) 加厚硅胶 / 换低膨胀材料 —— 改变发射性能且成本高，无必要；(d) 改拨杆或外罩让出膨胀空间 —— 实测余量充足（见下），改件没有收益。
- Evidence/calculation: `calculations/t06_flywheel_silicone_centrifugal.py` / `.txt`（三模型，轮毂固支 M3 为下界 0.26–0.55 mm、自由厚环 M2 0.55–1.19 mm、自由薄环 M1 为上界 2.44–5.23 mm；周向应力 0.008–0.017 MPa 远低于 30A 硅胶强度，弹性模型成立）。**不接触的判定（几何 + 仿真双证）**：拨杆真实轮廓外切半径 Rmax = 62.36 mm（MEASURED），冷态间隙 NECTAR 115.91 − 48 − 62.36 = **5.55 mm**、POLLEN 113.87 − 48 − 62.36 = **3.51 mm**；dr = 0.8 mm 时剩余 **4.75 / 2.71 mm**；即使取模型绝对上界 dr = 3.7 mm，NECTAR 仍留 **1.86 mm**，POLLEN 的接触门槛才是 **dr ≈ 3.51 mm** → 设计值余量 **4.4 倍**。仿真侧：R33 dr = 3.7 时飞轮—拨杆接触 3 起（**全部只在 POLLEN**）；R34 热态配间距 dr 0.5–2.7 全档 **30/30 零接触**（最小间隙 1.351 mm），边缘档 dr = 3.0 / 3.7 **12/12 零接触**（POLLEN 1.117 / 0.567 mm）。
- Impact: (1) **送球设计冻结，拨杆/外罩/托盘不改**；(2) 飞轮垫片长度成为**唯一随温度/转速变化的装配尺寸**，制造与装配图上必须写明「按热态外径配，含 dr = 0.8 mm」；(3) R27 的 `half_spacing = nip/2 + 48` 定性为**冷态口径**，R35 的 `+ dr_hot` 为其取代版（R27 文件全部保留，仅作历史）；(4) 存能核算不变：1620 rpm 两轮 3.70 J，NECTAR 需求占 41 %、POLLEN 占 31 %；(5) E 值 0.7–1.5 MPa 与 dr_hot = 0.8 mm 仍是 **ASSUMED**，需高速摄影或台架实测升级为 MEASURED。
- Reversible?: 是。`DR_HOT_MM` 是生成器里的单一常量，改值重跑即得新几何；R33/R34 两个仿真脚本按 dr 参数化（0.5–3.7 mm 扫过），任何新膨胀量都能直接复核间隙与通过率；R27 的 STEP、报告、检验 JSON 与 R33/R34 数据全部保留。
- Date/version: 2026-10-04 / C06B-FEEDER-A-PRIME-SHARED-R35（热态配间距）

## V-0034 — 验证记录（非决策）：膨胀量扫描 + 热态配间距的送球全流程仿真

- 目标（KNOWN）：用户要求「算膨胀量 → 重跑仿真 → 确认膨胀后飞轮不与拨杆接触；若接触则迭代改送球设计，直到 POLLEN 与 NECTAR 都通过」。
- 方法（SIMULATED）：MuJoCo 3.14.0，基线与 R32 一致（μ = 0.40、飞轮 1620 rpm、拨杆 25-4 Super Speed 线性模型 kv = 0.017452 / 限幅 ±0.530 N·m、索引式循环）。三个脚本按 dr 参数化：`simulation/mujoco/_work/r33.py`（冷态配间距，36 工况）、`_work/r34.py`（热态配间距，30 工况，dr 0.5/1.0/1.5/2.0/2.7）、`simulation/mujoco/out/_r34_edge.json`（边缘档 dr 3.0/3.7，12 工况）。间隙用 `mj_geomDistance` 量「拨杆几何↔飞轮」的实时最小距离。
- 结果（SIMULATED）：
  - **R33 冷态配间距 26/36 通过**。dr = 0 全过；dr ≤ 2.7 时 NECTAR 全过；**dr = 3.7 时 NECTAR 3/3 FAIL**；POLLEN 从 dr = 1.0 起出现 FAIL。飞轮—拨杆接触 3 起，**全部在 POLLEN dr = 3.7**（contacts 2121 / 150 / 150，间隙 0.001 mm）。FAIL 机理：夹口缩小改变出手相位，小球掉进拨杆毂—叶片夹角卡死 —— **不是**飞轮挡球。
  - **R34 热态配间距 30/30 通过、零接触**，逐档最小间隙 3.109（dr 0.5）/ 2.708（1.0）/ 2.304（1.5）/ 1.905（2.0）/ 1.351 mm（2.7，POLLEN）。
  - **边缘复核 12/12 通过、零接触**：dr = 3.0 时 POLLEN 1.117 / NECTAR 3.383 mm；dr = 3.7 时 POLLEN 0.567 / NECTAR 2.884 mm。
- 结论：**膨胀后的飞轮不与拨杆接触**（设计 dr = 0.8 mm → POLLEN 余 2.71 mm / NECTAR 余 4.75 mm；绝对上界 dr = 3.7 mm 时 NECTAR 仍余 1.86 mm、POLLEN 余 0.57 mm 且不接触）。**无需改拨杆/外罩**，只需把垫片长度按热态外径配（DEC-0032）。新图纸 = R35，产物 `cad/output/_r35_hot/`。
- 图与数据：`cad/output/_t06_r34_expansion_zh.png`、`cad/output/_t06_r34_geometry_zh.png`；`simulation/mujoco/out/_r33_expansion.json`、`_r34_expansion_hot.json`、`_r34_edge.json`。
- 未关闭：硅胶 E = 0.7–1.5 MPa 与 dr_hot = 0.8 mm 为 `ASSUMED`；μ = 0.40 `ASSUMED`；球质量 0.130 / 0.060 kg `ASSUMED`；索引式舵机控制未实机实现；9.9 mm 夹口过盈无结构/球变形校核。
- Date/version: 2026-10-04 / C06B-FEEDER-A-PRIME-SHARED-R35（R33/R34 仿真）
