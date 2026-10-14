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

## DEC-0033 — T06 R36 教训：净距、相位、成功率三个口径必须先用 MuJoCo 自己标定

- Decision: 从本轮起，T06 仿真报告里的这三类数字只在下列口径下有效：
  1. **净距**只用 MuJoCo 自己的几何接口（`mj_geomDistance`）当量具；本模型是**米制**（`gravity=-9.81`、`ball_r=0.045974`、`t=2e-4 s`），返回值必须显式 `*1000` 才是 mm。自写解析净距（旧 `paddle_clearance()` 之类）**不再作为证据** —— 它曾把 −40 mm 的穿透读成 +50 mm 的净空，方向完全相反。
  2. **`distmax` 是截断不是范围**：`mj_geomDistance(..., 0.06)` 对任何 >60 mm 的净距一律返回 0.06 ⇒ 报告里 **+60.0 要读作「≥60 mm 无碰撞」**，只有负值（穿透）是真实 mm 值。
  3. **相位必须几何标定**：`parts(phases=(330,150))` 在 `ph0=0` 时叶片实测落在 **30°/210°**；**`ph0=60` 才等于 CAD 标称零位 330°/150°**。参数名/参数值不能代替实测，否则装载区与驱动起点全错。
  4. **「出膛」必须带速度门槛**：只按位置越界，会把「被甩出机构、在自加地板上滚」记成出膛（实测 v = 0.32 / 0.62 m/s、x ≈ 488 mm）。
- Reason: 这三处口径没标定，已经造成过方向性相反的结论和污染的成功率；本轮多球结论完全依赖它们。
- Alternatives considered: 继续用自写解析几何（快，但已被证伪）；按参数名/参数值推断相位（已被证伪）。
- Evidence: `simulation/mujoco/_work/r36_probe_check.py` + `simulation/mujoco/out/_r36_probe_check.txt`（单位、相位、扫掠、容量四张表，纯 MuJoCo 探针）；`simulation/mujoco/_work/r36_recheck.py` + `simulation/mujoco/out/_r36_multiball_recheck.json`（出膛逐颗分类）。
- Impact: 引用净距/相位/成功率前必须先跑对应标定；MuJoCo 脚本改长度单位时要同步改这个系数。
- Reversible?: 是（判定口径，可随模型单位改变而改）。
- Date/version: 2026-10-11 / T06-R36

## DEC-0034 — T06 R36 结论：「托板上的等待球」在原理上不成立；多球容量 NECTAR 1 / POLLEN 2

- Decision（结论，MEASURED + CALCULATED）: 拨杆扫掠带是绕轴心的 **r ≈ 46–60 mm** 环带（叶片 46–58、TPU 尖 56–60，宽度 ±48 mm）；**球心距轴心 < 60 + r_球 的球一定会被叶片扫到**（NECTAR 需 ≥ 106、POLLEN 需 ≥ 96）。托板上球心距轴心只有 **62–93 mm**，而球径 ≥ 71 mm，球体内表面伸到距轴心 16–47 mm ⇒ 落在扫掠带里。实测：每一个 180° 周期内，停在托板面 x ≥ 30 mm 的球都会被 `paddle_flex_*` / `paddle_blade_*` 打出 **−4.0 … −39.1 mm** 穿透（最坏 ph0 = 90°）。**⇒ 托板不能当料仓：上面只能有「正在被推的那一颗」**，任何后排等待球都会被叶片打飞。
- 容量（MEASURED）：后挡墙在 x = 150 ⇒ 球心最远 x = 104（NECTAR）/ 114（POLLEN）；相切排队间距 = 2r = 91.9 / 71.1 mm ⇒ 托板最多 **NECTAR 1 颗 / POLLEN 2 颗**（POLLEN×3 实测排布 = 弧道 1 + 托板 2）。**「4 颗紧密排队」对两种球都是几何不可能**，与仿真参数无关。
- 更正（KNOWN）：先前把「托板末端与飞轮腔重叠 −43 mm」当作要清理的对象是**误读** —— 探针点 (104, 148) / (104, 200) 本身就落在飞轮盘实体里（`fw_lower_1` 轴心 (122.4, 180.7)、R 48），球不可能停在那儿。**托板与飞轮实体本身并不重叠**；飞轮相关的真实问题是 NECTAR 的摞球点被塞进飞轮（见 V-0035）。
- Reason: 用户要求评估结构应对多球的能力；实测把问题从「清干涉」改成「多球进料方式本身要改」。
- Alternatives considered: (A) 保持单球索引 + 外部料仓逐颗落料；(B) 等待区搬到扫掠圆外（球心距轴心 ≥ 106/96 ⇒ x ≥ 116，机构加长 60–100 mm）；(C) 取消托板等待位，改为从上方/侧向直接落料到拾取位。
- Impact: (b) 的 CAD 改动不再是「清理重叠 + 加长托板」，需先选定方向；方向未定前不动 CAD。
- Reversible?: 是；三个方向都只改送料段，不动飞轮、夹口与发射几何。
- Date/version: 2026-10-11 / T06-R36

## V-0035 — 验证记录（非决策）：R36 多球仿真（POLLEN×3 × 6 相位）清洗后结果

- 口径（SIMULATED）：`simulation/mujoco/_work/r36_multiball.py --mix POLLEN,POLLEN,POLLEN --cases 6 --hold 3.0`；几何 = R27/R32；索引式驱动（停 3.0 s → 扫 248° → 转回取下一颗）；μ = 0.40；夹口 64 mm。
- 结果（SIMULATED，按 DEC-0033 清洗后）：真出膛 **10/18**（v = 6.01–6.26 m/s，均值 6.15）；假阳性 2；逸出 6。逐相位真出膛：ph0 = 0 → 0/3、30 → 0/3、60 → **3/3**、90 → **3/3**、120 → 1/3、150 → **3/3**。扭矩峰值 0.520–0.530 N·m（25-4 额定 0.530 刚好用满），卡滞 0–24 %。
- 细节（SIMULATED）：ph0 = 60 的三颗在 0.33 s 内几乎同时出膛（t = 12.15 / 12.21 / 12.48 s）⇒ 不是「依次索引」，而是同一轮扫掠把多颗球一起带出，与 DEC-0034 的「后排球被叶片打飞」一致。
- 修掉的口径 bug（KNOWN）：球出膛后又被计入逸出（已加 `exits[k] is None` 条件）。
- 作废（KNOWN）：首轮 `simulation/mujoco/out/_r36_run1.txt` 以及「12/24、平均每颗 3.43 s」的说法全部作废（相位未标定 + 出膛判定未过速度门），该文件已删除；清洗脚本 `_work/r36_recheck.py`，数据 `out/_r36_multiball_recheck.json`。
- NECTAR×4 未采用（KNOWN）：排布算法（为省时间）跳过了摞球点的穿透检查，3 颗球被摞在 x = 104、z = 148/241/333 mm，其中两颗分别埋进 `fw_lower_1` 43.0 / 30.8 mm ⇒ 仿真数值爆炸（球 1 s 内飞到 ±1800 mm）。**这不是物理结论，是无效输入**；NECTAR 的托板容量实测只有 1 颗（DEC-0034），≥2 颗的工况在现有几何下摆不出来。
- 未关闭（TBD）：μ = 0.40、球质量 0.130 / 0.060 kg 仍是 `ASSUMED`；索引式舵机控制未实机实现。
- Date/version: 2026-10-11 / T06-R36
- 同步（KNOWN）：Linear KEI-18 长评论 + 新建 KEI-19（T06.8 多球进料方式）https://linear.app/keithschoolrobotic/issue/KEI-19；Notion https://app.notion.com/p/3ef7fc7bbcfb8177bf86d310c29afaa6 页尾追加 R36 小节（2026-10-11 已确认）。


## DEC-0035 — T06 R37 多球进料方向选定为 B：等待区搬到扫掠圆外，托板右端 150 -> 215 mm

- Decision（KNOWN）: 采纳 DEC-0034 的备选 **方向 B**。对送料段只有**一处几何改动**：托板/外罩右端（进料口）`TRAY_X1` 由 **150.000 mm 加长到 215.000 mm（+65 mm）**，`TRAY_X0` 同时由切点向内延 14 mm 到 24.901 mm（见 DEC-0036 的并实体要求）。除此之外**送球段与发射段几何全部不变**（外壳 R_IN 107.974、扇区 142..275°、壁厚 7、托板倾角 5°、拨杆轴心、叶片 46..58、TPU 尖 56..60、飞轮夹口按 DEC-0032 热态口径）。**不覆盖** R27/R35 的任何源文件与产物。
- Reason/计算（CALCULATED）: 扫掠带半径实测上限 60 mm（DEC-0034），球心安全下限 = 60 + r_ball ⇒ NECTAR 105.974 / POLLEN 95.560 mm。托板面是绕轴心与 R_IN = 107.974 圆相切的 5° 斜面，球心距轴心 `d(s) = sqrt(62.000² + s²)`（NECTAR）/ `sqrt(72.414² + s²)`（POLLEN），令 `d(s) = 60 + r` 解出等待区起点 **x ≥ 124.5（NECTAR）/ x ≥ 101.0（POLLEN）**。排队时第 k 颗球心 s = (k−1)·2r，于是第 2 颗本来就落在安全区（NECTAR x = 126.485 余 6.0 mm、POLLEN x = 106.650 余 9.2 mm）—— **R36 里「托板球被打飞」是探针瞬时位，不是排队稳态位；真正的限制是容量**（旧托板右端 150 只能停 1 颗 NECTAR / 2 颗 POLLEN）。
- 实测结果（MEASURED，`cad/output/_r37_stage/paddle_launcher_feeder_a_prime_shared_staging_report.json`）: 加长到 215 后容量变 **NECTAR 2 颗 / POLLEN 3 颗**。逐球心距轴心：NECTAR 停位 72.414（待推球，扫掠圆内，设计意图）+ 等待球 101.498 / …，POLLEN 停位 72.414 + 101.498 / 159.612；`waiting_balls_all_clear = true`（除第 1 颗待推球，**所有等待球都在扫掠圆外**，最小余量 POLLEN 第 2 颗 +5.938 mm）。
- 空域确认（MEASURED，`_r37_bbox.py` 后已删除）: 托板延长段（x 150→215、z ≈ 15）**没有任何既有实体**，最近的 `gecko_flywheel_lower_*` 只到 z ≥ 138.3 ⇒ 加长托板不会与任何保留件干涉。
- 代价（KNOWN + TBD）: 机构在 +x 方向**变长 65 mm**；进料口外移到 x = 215 后，**外部供料路线（料仓/输送）需要跟着调整**，该项由用户后续决定（对应 Linear KEI-19）。
- Alternatives considered: (A) 保持单球索引 + 外部料仓逐颗落料 —— 不改几何，但多球能力靠料仓而非机构；(C) 取消托板等待位改为上方/侧向落料 —— 要重做上料路径与节拍。三条并列见 DEC-0034。
- Reversible?: 是。`STAGE_X1` 是派生生成器里的单一常量；改值重跑即得新几何。R27/R35 源文件与产物、R26 让位记录全部保留。
- Date/version: 2026-10-11 / C06B-FEEDER-A-PRIME-SHARED-R37-STAGING

## DEC-0036 — T06 R37 (b) 重叠清理：四个重叠对的处理口径 + 拨杆并为一个实体

- Decision（MEASURED 驱动）: 对 R37 工作装配内的**自制件**做重叠普查（布尔交，`cad/output/_r37_census3.json`），按「不改变配合语义、不留重叠」的原则处理四个重叠对，并顺手清掉一个遗留占位孔：

  | 重叠对 | 实测重叠 | 处理 |
  |---|---|---|
  | `paddle_hub` × `paddle_arm_1` / `_2` | 295.762 mm³ ×2 | 轮毂 + 双臂 + 双叶片 **并为一个 `paddle_rotor` 实体** |
  | `paddle_blade_1/2` × `paddle_flex_tip_1/2` | 5760.000 mm³ ×2 | TPU 尖片**径向缩到 r = 58…60**（只留伸出叶片的那 2 mm） |
  | `guide_roof_3` × `guide_wall_3_+1` / `_-1` | 315.000 mm³ ×2 | 侧壁按 **0.5 mm 间隙**让位（复用 R27 的 `RELIEF_CLEARANCE_MM`），让位后实测归零 |
  | `feeder_shell_tray` 自身 | — | 原是**2 个只相切的实体**（球道弧 + 托板），托板向里延 **14 mm** 使其体积相交后**并为一个实体** |
  | （附）轮毂内孔 Ø4.1 | 与 Ø12 拨杆轴相交 | 改为 **Ø12.1 让位孔**（原 Ø4.1 是 R25 之前的占位孔遗留） |

- Reason: 用户指令「把重叠的部分删除，或者将有重叠多个实体整理为一个」。上面四处都属**同一个零件的内部自重叠或同名配合面的重复料**，不是功能间隙，因此可以合并/让位；而 `shooter_throat_+55` 与各飞轮/轴的配合**实测无重叠**，一律不动（DEC-0021：COTS 件整体带入、不做布尔并集）。0.5 mm 让位口径与 R27 一致，保证打印件仍有真实装配间隙。
- Evidence（MEASURED，导出后回读本轮 STEP）: 自制件两两布尔交 **全部为 0**（`our_part_overlaps_mm3 = {}`，两球）；全部自制件 `Solids() == 1`（含 `feeder_shell_tray`、`paddle_rotor`、`guide_wall_3_±1`、`guide_roof_3`、`shooter_throat_+55`、`paddle_flex_tip_1/2`、`paddle_shaft_support_bridge`）；拨杆轴 **Ø12 ∩ `paddle_rotor` = 0.000 mm³**、∩ `paddle_shaft_support_bridge` = 0.000 mm³（让位孔生效）。多实体件只剩 7 个厂商 COTS 件（飞轮/轴/拨杆轴的原厂装配语义，DEC-0021 要求保留）。
- 实现（KNOWN）: 新增派生生成器 `cad/paddle_launcher_feeder_a_prime_shared_staging.py`，**不修改**父模块 `paddle_launcher_feeder_redesign.py` / `paddle_launcher_feeder_a_prime_shared.py` / `paddle_launcher_constrained.py`；覆盖方式为 `pl.paddle_parts`（拨杆零件表）+ `F.KEEP_EXACT`（把 `paddle_rotor` 加进保留名单，这是第一次 dry-run 报 `KeyError` 的根因）+ `F.TRAY_X0/X1` + 输出目录 `cad/output/_r37_stage/`。
- Impact: 拨杆由「轮毂 + 2 臂 + 2 叶片 + 2 尖片 = 7 件」变为「1 个刚性本体 + 2 片 TPU 尖 = 3 件」，刚性件仍是**一个可打印/可加工实体**，两片尖片保留为可更换件；运动学（轴心、相位 330°/150°、外缘 r ≤ 60）逐点不变。
- Reversible?: 是；改动集中在派生生成器，父模块与 R27/R35 产物均在。
- Date/version: 2026-10-11 / C06B-FEEDER-A-PRIME-SHARED-R37-STAGING

## V-0036 — 验证记录（非决策）：R37 最终 STEP 的回读复测与几何检验 R005

- 目标（KNOWN）: 按 AGENTS.md「CAD 几何检验」要求，对 R37 的**最终导出实体**（不是生成参数）做关键尺寸/体积复测，输出 JSON 报告。
- 方法（MEASURED）: (1) `_r37_readback.py`（临时脚本）用 cadquery 回读 `cad/output/_r37_stage/*.step`，量整机边界框、根实体数、总体积；(2) `tools/inspect_geometry.py --step <nectar.step> --spec config/t06_feeder_r37_checks.json --run-label R005 --report cad/output/inspection/t06_feeder_r37_R005.json`，4 项检查全部给出目标值/公差/实测值/测量方法。
- 结果（MEASURED）: **R005 = 4/4 `pass`，0 `fail` / 0 `not_run` / 0 `unresolved`，退出码 0，用时 397.1 s。**
  - `T06-R37-GEO-001` bbox_max x = **215.2615**（目标 215.0 ± 0.5；超出量来自托板末端倒角）⇒ 方向 B 的 +65 mm 已落在最终几何里。
  - `T06-R37-GEO-002` bbox_max z = **338.7996**（目标 338.8 ± 1.0）⇒ 只动托板，发射段/飞轮轴向位置未受影响。
  - `T06-R37-GEO-003` 体积 = **930299.217 mm³**（目标 930299.902，相对 1e-5；差 0.685 mm³ 为 STEP 往返容差）⇒ 清理既没丢料也没重复料。
  - `T06-R37-GEO-004` 根实体数 = **23**（目标 23 = 16 个部件 + 7 个 COTS 件按官方多实体保留）⇒ 导出未合并/丢失实体。
  - 回读口径（两球一致）：根实体 23；NECTAR bbox z 上限 338.8 / POLLEN 333.259（只差飞轮轴向位置）；两球总体积同为 930299.9 mm³（体积平移不变，与「只移动飞轮」一致）。
- 未验证（TBD）: μ（球—PET 打印件）仍为 `ASSUMED`；球质量 0.130 / 0.060 kg 仍为 `ASSUMED`；索引式舵机控制未实机；**R37 几何尚未接入 MuJoCo 多球仿真**（现有 `_work/r36_multiball.py` 取 R27/R32 几何）。
- Date/version: 2026-10-11 / T06-R37

## V-0037 — 验证记录（非决策）：R37 几何的 MuJoCo 多球全流程仿真（方向 B 是否真的能依次索引送球）

- 目标（KNOWN）: 用户指令「跑吧，供料路线改就改吧」—— 把 R37（方向 B：等待区搬出拨杆扫掠圆、托板右端 150 → 215 mm）接进 MuJoCo，验证多颗球能否**依次**被索引送入并被飞轮发射。测试标准：(1) 设计容量工况（NECTAR 2 颗 / POLLEN 3 颗）多次、多相位下都能把球全部送出；(2) 出膛速度达到可发射量级（对照 R36 的 4.7–6.3 m/s）；(3) 不出现 R36 那种摞球点埋进飞轮的数值失效。
- 方法（SIMULATED）: `simulation/mujoco/_work/r37_multiball.py`（由 `r36_multiball.py` 派生：`TRAY_X1 = 215`、TPU 尖 r 58…60、`SPILL_X = 240`、窗口 `t0 + (nb+2)×(T_ROT+hold) + 4 s`）。5 种球数 × 6 个拨杆起始相位（ph0 = 0/30/60/90/120/150°，hold 3.0 s）＝ **30 轮 / 84 颗**；拨杆 60 rpm 索引式、μ = 0.40、飞轮 1620 rpm、扭矩限幅 ±0.530 N·m（25-4 Super Speed 线性 T–n）。判定沿用 DEC-0033：**真出膛 = v ≥ 3.0 m/s 且 x < 200 mm**；再看每颗球「轮到自己之前」的累计行程（队列纪律）。清洗脚本 `simulation/mujoco/_work/r37_recheck.py` → `out/_r37_recheck.json`。
- 结果（SIMULATED）: **设计容量工况可用。** NECTAR × 2 = **12/12（100%，6/6 轮全清）**，v = 4.68–4.86 m/s（均 4.76），平均轮内耗时 3.21 s、全清 6.42 s；POLLEN × 3 = **15/18（83%，4/6 轮全清）**，v = 6.01–6.23 m/s（均 6.13），平均轮内耗时 3.55 s、全清 10.46 s。最差相位 ph0 = 120°（POLLEN×3 1/3）；POLLEN×3 在 ph0 = 0/30/60/150° 四档全清。超容量工况：POLLEN×2 8/12（67%）、NECTAR×3 11/18（61%，叠 1 颗）、mix4 5/24（21%，叠 1–2 颗），一律按「设计容量外」解读，**不作为结构缺陷**。假阳性 2/84。扭矩峰值全程 0.530 N·m（额定用满），卡滞占比 0–72 %（大卡滞只出现在超容量轮次）。
- 关键发现（SIMULATED）: 等待区**第 2 颗球**稳定停在 `x ≈ 87–88 mm`（`r ≈ 89 mm`、极角 ≈ 317°），**在拨杆扇区 142–275° 之外** ⇒ 拨杆扫不到它，只能靠**后排球推挤**或**拨杆回程蹭带**逐步索引进扫掠圆。因此 POLLEN×3（有第 3 颗在后面推）83% 明显优于 POLLEN×2（无后排）67%，且后者更慢（平均轮内 4.24 s vs 3.55 s）。注意该停靠点比参数表「等待区起点 x ≥ 97.772（POLLEN）」**靠内约 10 mm**：半径上其实在扫掠圆之内，只因极角在扇区外才没被打飞。
- 口径澄清（KNOWN）: 迹线里 `|z|` 达 10⁶ mm 的记录**不是数值爆炸** —— 出膛后球在无边界空间继续自由下落并沿 +x 飞行（`z = −1200 m` ↔ 约 15 s 自由落体，与运行时长吻合）。R36 的「摞球点埋进飞轮导致爆炸」问题在**容量内工况未复现**（叠放 0 颗）。
- 与 R36 对比（SIMULATED）: 同口径清洗后 R36 的 POLLEN×3 = **10/18（56%）**（V-0035），R37 = **15/18（83%）** ⇒ 方向 B「等待区搬出扫掠圆」为**净收益**；出膛速度均值从 6.26 降到 6.13 m/s（−2%，夹口/几何差异与采样差异混合，未单独归因）。
- 未验证（TBD）: μ（球—PET 打印件）与球质量仍为 `ASSUMED`；索引式舵机控制未实机；外部供料路线随进料口 x = 215 待改（KEI-19，用户已批准改）；**第 2 颗球索引余量偏紧**，建议的几何动作（放开 x ≈ 87 处门槛 / 按实际停靠半径重算等待区门槛）本轮**未做**。
- Date/version: 2026-10-11 / T06-R37 / 生成器 `cad/paddle_launcher_feeder_a_prime_shared_staging.py`（本轮未改 CAD 几何）

## DEC-0037 — T06 NECTAR 运行夹口重算 82 -> 86 mm（真实调隙舵机两档刚性定位）

- Decision（KNOWN，用户 2026-10-12 明确接受）: NECTAR 的**运行夹口由 82.0 改为 86.0 mm**，POLLEN 保持 64.0 mm。夹口是**纯几何的刚性对称定位**，没有弹性件；两档之间的切换由真实位置舵机 `2000-0025-0002` 完成，行程仅 **23.08°**（82 档曲柄 42.41° → 86 档曲柄 19.33°），全行程 19.33…96.68° 共 **77.35°**。
- 触发（KNOWN + SIMULATED）: 82 档对 Ø91.948 球的**单侧压入 4.97 mm**，要靠约 **8.6 N·m/轮**的摩擦扭矩才能把球压过夹口，远超 25-4 Super Speed 的能力 → 轮子打滑、球在夹口里「蠕」过（轮内 14–21 s），驱动 **64–82 % 时间堵转**，后面队列被饿死。参数表里那条 `TBD: 9.9 mm 压入无结构/变形校核` 至此被坐实。
- Reason/反解（CALCULATED）: 调隙链为 曲柄 12 → 定长拉杆 65 → 水平十字滑块 → 两根定长 110 对角连杆 → 滑座耳片（`cad/paddle_launcher_constrained.py:369-431`：`crank_r, drag_len = 12.0, 65.0`、`servo_u = -120.0`、`carriage_pin_u = 18.0`、`main_link_len = 110.0`）。反解 `crosshead_u = 18 − sqrt(110² − half_spacing²)`、`cos θ = (d² + r² − L²)/(2 d r)`，`d = crosshead_u + 120`：

  | 夹口 | 半间距 | 十字滑块 u | 曲柄角 | 单侧压入 | 距死点 |
  |---|---|---|---|---|---|
  | **82（旧）** | 89.0 | −46.645 | 42.41° | 4.97 mm | 3.65 mm |
  | 85 | 90.5 | −44.530 | 26.92° | 3.47 mm | 1.53 mm |
  | **86（新）** | **91.0** | **−43.798** | **19.33°** | **2.97 mm** | **0.80 mm** |
  | 87 | 91.5 | −43.045 | 5.06° | 2.47 mm | 0.05 mm |
  | 87.07 | 91.537 | −43.000 | 0° | — | **死点** |

  **机构可达上限 = 87.07 mm**（曲柄与拉杆共线）。⇒ 单球扫参里 88/90 的漂亮数据**不可实现**，只能作趋势参考。传动比 `dT/dF` 由 82 档的 9.204 mm/rad 降到 86 档的 4.666 mm/rad，即**保持扭矩需求约减半**。
- Evidence（SIMULATED，见 V-0038）: 6 相位（150/145/140/130/120/160）× mix P/N/P/N × 75 s：**全清 6/6、真出膛 24/24**。NECTAR 出膛速度 5.10 → **5.76 m/s（+13 %）**，轮系接触冲量 16.65 → **9.49 N·s（−43 %）**；POLLEN 完全不变（v 6.35）。清空时间 41.9 → 42.0 s。
- 收益与代价: 收益＝球挤压量与轮系打滑大幅下降、舵机保持扭矩减半、参数表 TBD 项的物理依据被移除；代价＝86 距机构死点只有 **0.80 mm**，实物装配公差要留意（若要更大余量可退到 85 档，余 1.53 mm，代价是 v 少约 0.16 m/s）。
- Alternatives considered: (A) 维持 82 并加大飞轮电机/提高接触摩擦 —— 需要约 8.6 N·m/轮，超出 25-4 量级，否决；(B) 87 —— 距死点 0.05 mm，实物装不进去，否决；(C) 88 / 90 —— **机构不可达**，否决；(D) zip-tie 弹性夹口（`r38_v3/v4/v6/v7`）—— 无零件号假设，2026-10-11 已回滚并归档到 `simulation/mujoco/_work/_superseded_r38_tie/`。
- Reversible?: 是。夹口由 `half_spacing = nip/2 + WHEEL_R` 单一常量派生，改值重跑生成器即得新几何；R27/R35/R37 的源文件与产物全部保留，82 的旧值以 `SUPERSEDED` 留在原处。
- Date/version: 2026-10-12 / C06B-GAP-R38

## V-0038 — 验证记录（非决策）：NECTAR 夹口 86 的机构反解 + MuJoCo 单球扫参与 6 相位多球全流程

- 目标（KNOWN）: 用户指令「重算」—— 用**真实调隙舵机两档刚性夹口**（不是弹性件）重算 NECTAR 夹口。测试标准：(1) 新夹口必须落在机构可达范围内；(2) 多球全流程仍要 100 % 全清与真出膛；(3) 相对 82 档在出膛速度或轮系负荷上有可量化的改善。
- 方法（CALCULATED + SIMULATED）: (a) 机构反解 —— `_r38_gapcal.py` / `_r38_limit.py`（`_work/_recalc_nip86/`，产物 `out/_r38_gap_recalc.json`）；(b) 单球夹口扫参 —— `_work/r38_v8.py --mix NECTAR --phases 150 --tmax 40`，夹口 82/84/85/86/87/88/90；(c) 6 相位多球全流程 —— `_work/r38_v8.py --mix POLLEN,NECTAR,POLLEN,NECTAR --nip-net 86 --phases 150,145,140,130,120,160 --tmax 75 --sw-delay 0.25`（μ = 0.60 塑料光球 / 0.4 mm 层高 PET）。判定沿用 DEC-0033：**真出膛 = v ≥ 3.0 m/s 且 |l_x| > 40 mm 且 |l_n| < 80 mm**，且必须先进入过转盘。换档时点 = 上一颗球出膛后 0.25 s（不是换球保持段：拨杆是索引式的，上一颗出膛时下一颗已被第二片叶片拾起）。
- 结果 a（CALCULATED）: 机构可达上限 **87.07 mm**；86 档 十字滑块 u = −43.798、曲柄 19.33°、单侧压入 2.97 mm、距死点 0.80 mm；82 → 86 伺服行程 23.08°，82 → 64 为 54.27°。
- 结果 b（SIMULATED，单球 NECTAR，ph0 = 150）:

  | 夹口 | 单侧压入 | 峰值法向力 | 接触冲量 | 出膛 v | 轮内 |
  |---|---|---|---|---|---|
  | 82 | 4.97 mm | 313.0 N | 14.63 N·s | 5.21 m/s | 14.44 s |
  | 86 | 2.97 mm | 300.3 N | 8.25 N·s | 5.81 m/s | 14.44 s |
  | 88（不可达） | 1.97 mm | 256.2 N | 5.33 N·s | 5.93 m/s | 14.44 s |
  | 90（不可达） | 0.97 mm | 159.0 N | 1.92 N·s | 5.16 m/s | 14.45 s |

  夹口越松 → 接触冲量越小、v 越高，**86 是可达范围内的甜点**；90 起接触太淡开始掉速。
- 结果 c（SIMULATED，6 相位 × 4 颗 = 24 颗）: 全清 **6/6**、真出膛 **24/24**。POLLEN v 6.32–6.37 m/s（均 6.35，与 82 档逐位相同）；NECTAR v 5.65–5.85 m/s（均 **5.76**，82 档为 5.10）、轮系接触冲量均 **9.49 N·s**（82 档 16.65，−43 %）。清空时间均 41.95 s / 最慢 42.18 s。换档记录（ph0 = 150）: t = 12.42 → 86、27.74 → 64、36.72 → 86。
- 关键发现（SIMULATED，纠正前一轮口径）: **夹口不是节拍瓶颈。** 迹线显示拨杆收到 290 rpm 恒速指令后，负载下实际只有约 **22 °/s**（关节 140.7° → 207.3° 用 3.0 s，对应球心线速度约 24 mm/s），即 0.530 N·m 的 25-4 扭矩在运送段**已经饱和**；这也解释了为什么单球扫参 82→90 的「轮内」时间一位小数都不变。**球质心到出膛的纯运送时间只有 0.15–0.74 s**，之前报的「轮内 17–21 s」是把保持等待段算进去了，不是蠕动。⇒ 夹口 86 的收益是**降低球的挤压量与轮系打滑**，不是提速；要提节拍必须动拨杆（减速比/扭矩）或缩短运送角。
- 未验证（TBD）: 夹口 86 只有仿真 + 机构反解支撑，**尚无实物**；球压缩量、硅胶轮热态外径（dr_hot 0.8 mm）、μ = 0.60、球质量 0.130 / 0.060 kg 仍为 `ASSUMED`；86 距死点 0.80 mm 的装配公差未核算；`flywheel_nip_measured_hot_mm` 的 NECTAR 87.6 是按 86 基准外推的**计算值**，要在重新生成的热态 STEP 上实测才成立。
- Date/version: 2026-10-12 / C06B-GAP-R38 / 脚本 `simulation/mujoco/_work/r38_v8.py` + `_work/_recalc_nip86/`

## DEC-0039 — T06 送球道低摩擦内衬（PTFE 带 0.5 mm）：把节拍瓶颈从「拨杆扭矩」改判为「球—球道滑动摩擦」

- Decision（KNOWN，用户 2026-10-12「接受，开始进行修改」）: 球道的两个接触面 —— **外罩内弧（142°–275° 扇区）与托板顶面** —— 各加一条 **0.5 mm 厚、88 mm 宽**的 PTFE 带；打印件按带厚**预缩**，贴带后球看到的有效表面与原设计**逐面重合**，因此仿真所用的球道几何、轨迹与 R38 完全一致：
  - 外罩：内弧打印半径 `R_IN + 0.5`（外弧/外径**不变** ⇒ 壁厚 7.0 → 6.5），扇区与 R38 相同（142°–275°）。
  - 托板：顶面下沉 0.5 mm（底面不动 ⇒ 厚度 6.0 → 5.5），倾角与 x 范围不变（24.901…215 mm，5°）。
  - **拨杆几何不改**（见下「否证项」）。**不覆盖任何原文件**：新增 `cad/paddle_launcher_feeder_a_prime_liner.py`，原 R38 生成器与产物原样保留。
- 触发/根因（SIMULATED）: R38 把节拍瓶颈记为「拨杆扭矩饱和（实际只有约 22 °/s）」，R39 进一步定位**扭矩被谁吃掉**：球被叶片压在**外罩内弧与托板顶面之间**，接触法向力 5–6.5 N 且有 2–3 处同时接触，**0.530 N·m 的 25-4 扭矩全程被球—球道的滑动摩擦削平**，单球要 11.6 s 才送达；同一台架把这两处有效 μ 从 0.60 降到 0.05 后，单球运送 **0.16 s**、全流程清空 **47.1 → 10.0 s**。⇒ 「扭矩不够」是表象，**摩擦才是瓶颈**；继续加扭矩只会把轮系/舵机成本推高而不提速。
- Evidence（SIMULATED，同一台架单变量，见 V-0039）:

  | 球道 μ | 清空（4 颗，6 相位） | 卡滞 | 全清 | 真出膛 |
  |---|---|---|---|---|
  | 0.60（R38 同台架基线） | 46.23–47.57 s（均 47.11） | 72 % | 6/6 | 24/24 |
  | 0.30 | 19.5–23.8 s | 37–46 % | 6/6 | 24/24 |
  | 0.10 | 11.66 s | 10 % | 6/6 | 24/24 |
  | **0.05** | **10.0 s** | **1 %** | 6/6 | 24/24 |
  | 0.05 + hold 1.0 s | **4.0 s** | 4 % | 6/6 | 24/24 |

  出膛速度不退化：POLLEN 6.3 m/s、NECTAR 5.7–6.1 m/s（R38 为 6.35 / 5.76）；μ ≤ 0.05 已触底（继续降低无收益）。相对 R38 交付口径（41.95 s / 69–70 %），清空时间 **约 1/12**、卡滞 **72 % → 1 %**。
- 否证项（本轮实测，都必须写进历史以免重犯）:
  1. **只贴外罩等于只拿到一半收益** —— 只把外罩内弧降到 μ = 0.05、托板保持 0.60 时清空仍是 19.5–25.9 s、卡滞 38–50 %。**两个面必须一起贴**。
  2. **改拨杆形状没用** —— 内衬到位后对比 8 种叶片型面（原设计 / 加高 / 全高筋 R60·R64 / 圆头 / 带臂 / 厚条 / 半高筋），送达时间 **0.16–0.17 s 全部相同**，扭矩均值 0.149–0.176 N·m 同量级。⇒ 拨杆改型不是本轮的提速手段，不做。
  3. **OCC 的 distance / intersect 不能当量具** —— 本 CadQuery build 上 `Solid.distToShape` / `Compound.distToShape` 不存在；`Solid.distance` 对「大球 vs 旋转外罩」给出 31.29 mm（与实体自相矛盾，真实约 0.47 mm）；`Solid.intersect` 体积系统性偏小约一半（r = 10 球 ∩ x ≥ 9 盒：解析 30.3687 → 量到 15.1844），含奇异点的 cone 直接返回 0。⇒ R39 起球道面偏差一律用**导出细网格 + 射线求交**量（`r39_liner_report.json`），并把 `tools/inspect_geometry.py` 的 distance 检查改到 `Shape.distance`（标 `brep_extrema_distance`）并支持 `check["rule"]` 覆盖判定方向。
- Alternatives considered: (A) 换更大扭矩舵机 / 提高传动比 —— R38 已证夹口不是瓶颈，本轮又证摩擦是瓶颈，加扭矩是治标且抬高成本，否决；(B) 只贴最长的外罩弧（省料省工）—— 实测只有一半收益，否决；(C) 改拨杆型面/减薄叶片 —— 8 型对比无差别，否决；(D) 喷特氟龙干膜 / 抹硅脂 —— 同为降 μ，但涂层的厚度、均匀性与耐久不可复现，贴带可换可量，保留为备选（同一几何，若带材贴合失败可退到此项）；(E) 直接改用低摩擦材料打印球道 —— 需要重做整机几何与强度核算，保留为后续备选（加 PTFE/石墨填充的 PET 或 POM 打印）。
- Risks/未验证（TBD）: μ = 0.05–0.10 为 `ASSUMED`（PTFE 带对光面塑料球，具体批次与 3D 打印层纹的耦合未实测）；带材在 118 mm 长的弧面上的贴合与端头翘边、0.5 mm 台阶对球滚过的影响、88 mm 带宽**以外**两侧裸露打印面在多球索引时的行为，均未验证；本条改动**尚未实机**。
- Reversible?: 是。内衬是独立的两条带 + 预缩的打印件，去掉带材换回 R38 件即回到原状态；两份 STEP 与量测报告全部入库。
- 编号说明（KNOWN）: 本决策占用 **DEC-0039**（用户上一轮已按此编号记录 R39 产物），**DEC-0038 保留未用**，不作为缺口补写，以免与已入库的产物编号冲突。
- Date/version: 2026-10-12 / C06B-FEEDER-R39 / 生成器 `cad/paddle_launcher_feeder_a_prime_liner.py`

## V-0039 — 验证记录（非决策）：送球道低摩擦内衬的 MuJoCo 单变量扫参 + CAD 几何检验

- 目标（KNOWN）: 用户指令「接受，开始进行修改，记得上传，再次对送球部分结构进行优化（拨杆，外罩等），每次优化后跑仿真，重复此流程直到获得较大提升」。测试标准：(1) 相对 R38 基线在**清空时间/卡滞**上有量级级改善；(2) 全流程仍要 100 % 全清与真出膛；(3) 出膛速度不退化；(4) 交付几何的关键尺寸要从最终实体量出来（AGENTS.md「CAD 几何验证」）。
- 方法（SIMULATED + MEASURED + CALCULATED）:
  - 仿真台架 `simulation/mujoco/_work/_r39_v9.py`：**完整复用** R38 的 `r38_v8.py`（真实调隙舵机两档刚性夹口、6 相位、mix P/N/P/N、nip NECTAR 86 / POLLEN 64、75 s 预算），只多一个 `--liner MU` —— 把外罩内弧（`r10_*`/`shell_*`）与托板（`tray`）的 geom 摩擦设为 MU 并把 priority 提到 2（MuJoCo 取高优先级 geom 的摩擦），因此**有效 μ 是唯一变量**。基线复现：`--liner 0.60`。
  - 几何量具 `cad/paddle_launcher_feeder_a_prime_liner.py::measure_wall()`：导出 tolerance 0.01 mm / angularTolerance 0.05 的细网格 STL（729 三角形），用 numpy 射线—三角形求交沿 130°–290° 逐 1° 量内/外弧、沿托板 x 自上而下量托板面偏移。
  - 规格检验 `tools/inspect_geometry.py --step <R39 STEP> --spec config/t06_r39_liner_checks.json`（5 项：单实体、Y 宽 108、托板右端 x、外罩最低点 z、STEP 往返）。
- 结果 a（SIMULATED，同台架单变量，每档 6 相位 × 4 颗 = 24 颗）: 见 DEC-0039 表。μ = 0.60/0.30/0.10/0.05 的清空时间均值为 47.11 / 约 21.7 / 11.66 / 10.0 s，卡滞 72 / 37–46 / 10 / 1 %；**每一档都是全清 6/6、真出膛 24/24**；μ = 0.05 + hold 1.0 s → **4.0 s / 卡滞 4 %**。出膛速度 POLLEN 6.3 m/s、NECTAR 5.7–6.1 m/s。
- 结果 b（SIMULATED，否证）: 只贴外罩（托板保持 0.60）清空 19.5–25.9 s / 卡滞 38–50 %；拨杆 8 种型面在 μ = 0.05 下送达 0.16–0.17 s、扭矩均值 0.149–0.176 N·m，**无可测差异**（`out/_r39_padd.log`、`out/_r39_padd_liner.json`）。
- 结果 c（MEASURED + CALCULATED，两个变体逐位相同）: **5/5 pass**（`cad/output/inspection/t06_feeder_r39_liner_{nectar,pollen}.json`）。
  - 网格射线实测（交付几何，不是参数）：内弧 **108.4616 mm**（设计 107.974 ⇒ 偏移 **+0.4876**，与预缩 0.5 相符）、外弧 **114.9738 / −0.0002**（外径未被一起缩小）、托板面偏移 **−0.4608**（最大 0.4895）、扇区 **142.0°–275.0°**、单实体、体积 279545.9 mm³、包围盒 300.7237 × 108.0 × 183.5574 mm；STEP 往返 bbox/volume 偏差 0。
  - 带下料（CALCULATED）：弧带开发长 **250.64 mm**、托板带长 **190.83 mm**、宽 88 mm、带体积 **19449.96 mm³**（`cad/output/_r39_liner/liner_tape_arc.step`、`liner_tape_tray.step`）。
- 关键发现: (1) 送球段瓶颈是**摩擦**，不是舵机扭矩也不是拨杆形状；(2) 内衬到位后，节拍的主导项变成**保持（hold）时间**：3.0 → 10.0 s、2.0 → 7.0 s、1.0 → 4.0 s，即「每颗球的固定等待」而不是「运送本身」（运送只需 0.16 s）；(3) 有效 μ ≤ 0.05 后曲线触底，继续降 μ 无收益，故把目标定为 μ = 0.05–0.10 的 PTFE 带。
- 未验证（TBD）: μ（PTFE 带 vs 光面塑料球）为 `ASSUMED`；带材贴合/翘边、0.5 mm 台阶、带宽外裸露面在多球索引下的行为、以及本条改动的**实物**表现全部未验证；仿真里的球道几何仍是 24 段盒链近似（`simulation/mujoco/_work/r38_v8.py` 口径），不是 CAD 实体本身。
- Date/version: 2026-10-12 / C06B-FEEDER-R39 / 脚本 `_work/_r39_v9.py`、`cad/paddle_launcher_feeder_a_prime_liner.py`、`tools/inspect_geometry.py`
## DEC-0040 — 低摩擦内衬（R39）的交付口径收窄：标准相位下全清率不成立于 μ=0.05；瓶颈转为节拍错配 + 等待区第 2 颗球索引余量

- 类型（KNOWN）: 复核性决策 —— 收窄 DEC-0039 / V-0039 的**适用范围**，不推翻其几何与「摩擦是原瓶颈」的根因判断。
- 触发（KNOWN）: 用户指令「先跑主要未知」。R39（V-0039）的多球证据只取自 6 个**特定**相位（150/145/140/130/120/160），从未跑标准相位 0/30/60/90/120/150，「全清 6/6 + 真出膛 24/24」在相位维度上未被复核；同时 V-0037 遗留的「等待区第 2 颗球停靠在扇区外」在 μ 降到 0.05 后从未复测。
- 复核口径（SIMULATED）: 同台架全流程（真实两档刚性夹口、mix = POLLEN>NECTAR>POLLEN>NECTAR、4 颗 x 6 相位、hold 3.0 s、预算 75 s），几何用 R38/R39 现行口径 **tray = 285 mm**。⚠️ 若沿用 R37 默认的 215，球会从开口端滚掉（x=4746 / z=-64645），结果无意义。有效 μ 是唯一变量。
- 旁证（SIMULATED）: 另一组 11 相位扫参（含 R39 的 6 个旧相位，共 39 颗，`out/_r40_LIN05.log`）得 出膛 30/39 = 77 %、真出膛 20/39 = 51 %、**全清 6/11**、逸出 0 颗（tray=285 已修正）—— 与标准六相位结论同向。
- 结果（SIMULATED，6 相位 x 4 颗 = 24 颗）:

  | 口径 | 出膛 | 真出膛(v>=3.0) | 全清轮 | t_total 均值 | 卡滞均值 |
  |---|---|---|---|---|---|
  | 内衬 0.05 双面（换档滞后 0.25 s） | 21/24 | 19/24 | **4/6** | 8.51 s（3.94-10.0） | 1.5 % |
  | 内衬 0.05 双面（换档滞后 0.05 s） | 21/24 | 21/24 | 4/6 | 8.40 s（3.74-9.97） | 1.1 % |
  | 对照 μ=0.60（无内衬） | 24/24 | 24/24 | **6/6** | 57.18 s（46.89-78.41） | 75.6 % |
  | 外罩 0.05 + 托板 0.15 | 21/24 | 19/24 | 5/6 | 14.53 s | 23.5 % |
  | 外罩 0.05 + 托板 0.30 | 21/24 | 19/24 | 5/6 | 15.64 s | 37.2 % |

- 结论（SIMULATED，收窄 V-0039 口径）: **低摩擦内衬买到的是「速度」而不是「可靠性」。** 清空时间 46.9-78.4 s -> 3.7-10.0 s（约 1/6-1/8）、卡滞 75.6 % -> 1.1 %，但全清轮 6/6 -> **4/6**、真出膛 24/24 -> 19-21/24。**R39/V-0039 写的「全清 6/6、真出膛 24/24」只在原取样相位成立，不得作为交付口径。** 内衬几何（0.5 mm PTFE、预缩内弧 +0.4876 / 托板面 -0.4608）与「原瓶颈是球—球道摩擦」的判断不变，继续保留。
- 失败机理（SIMULATED，已定位，勿归错因）:
  1. **节拍错配（主因）**: μ 降到 0.05 后球到喉部**提前约 0.3 s**，而换档触发仍是「上一颗出膛 + `--sw-delay` 0.25 s」⇒ 用**错夹口**漏出（表现为 v=1.54-1.55 m/s 的「速度不足」）。把滞后压到 0.05 s 能把 ph0=0 那轮的「速度不足」改成真出膛（真出膛 19 -> 21），但 ph0=60 出现 ln=227.2 的卡球、ph0=30 第 4 颗仍完全未出膛 ⇒ 还有第二个瓶颈。
  2. **等待区第 2 颗球索引余量（次因，V-0037 遗留）**: 等待区第 2 颗球稳定停在**拨杆扇区之外** —— NECTAR r≈101 mm / 极角≈327°，POLLEN r≈96-97 mm / 极角≈316°（**4 球混合轮**口径；跨轮实测范围 NECTAR r 65.5-106.9 mm、POLLEN 76.4-100.2 mm，**全部判为「扫掠不可达」**。可达判据：142° <= 极角 <= 275° 且 r <= 61 + r_ball，即 NECTAR 107 / POLLEN 96.6 mm）。只有靠后排推挤与拨杆回程蹭带才陆续索引进扫掠圆。**μ=0.05 只让队首到位更快，没有改变这个几何事实** —— 三个托板摩擦口径（0.15 / 0.30 / 0.60）缺失的是**同一批球**（ph0=30 的第 4 颗、ph0=60 的第 3+4 颗）。
- 否证项（SIMULATED，第 3、4 次否证，必须写入历史以免重犯）:
  1. **调托板摩擦解决不了全清** —— 托板 0.15 / 0.30 与球道 0.60 缺失的球完全相同。
  2. **调拨杆型面解决不了全清** —— V-0039 的 8 种型面送达时间全同（0.16-0.17 s），本轮再次确认。
  3. **低摩擦不是无代价** —— 托板倾角 5° 下 **托板 μ 必须 > tan5° ≈ 0.09**，否则整队列沿坡自滑、在拨杆入口堆死（R40 首轮 ph0=30 即 0/4、卡滞 87 %）。内衬的 μ 目标区间（0.05-0.10）与该下界几乎重叠 ⇒ 若同时依赖倾角自流与低摩擦球道，**必须把倾斜段的 μ 与扫掠段的 μ 分开处理**。
- Alternatives considered: (A) 继续降球道 μ —— 已触底（V-0039）且本轮证明反而丢全清，否决；(B) 只压换档滞后（`--sw-delay` 0.25 -> 0.05 s）—— 有改善（真出膛 19 -> 21）但不解决全清，保留为**必要而非充分**措施；(C) **改等待区几何**让第 2 颗球自然落进扫掠圆（放开 x ≈ 87 处门槛，或按实际停靠半径重算等待区起点）—— **本轮给出的下一步方向**；(D) 按球种拆开 hold / 转速（`--hold-map` / `--spd-map` 已支持）—— 与 (B) 同族，待 (C) 到位后再扫。
- Risks/未验证（TBD）: 标准相位只取 6 个（0/30/60/90/120/150），不是全相位；仿真球道仍是 24 段盒链近似；μ 0.05-0.10 仍为 `ASSUMED`；**本条全部为仿真，未实机**。
- Reversible?: 是。纯仿真复核 + 文档口径修正，未改任何 CAD、未覆盖任何原文件。
- 产物入库口径（KNOWN）: 入库 `_work/_r40_liner_mix.py` + 全部 `.log`（逐轮逐球明细与汇总）+ `out/_r40_LIN05.json`（11 相位诊断，含逐球停靠 r / 极角 / 扫掠可达）。五个 mix 的逐帧 trace JSON（`_r38_MIX*.json`，共约 26 MB）**未入库** —— 体积比既有「1-5 MB / 份」口径大约 6 倍；同一组数字可用已入库脚本复算（命令见 V-0040）。
- Date/version: 2026-10-12 / C06B-FEEDER-R40 / 脚本 `simulation/mujoco/_work/_r40_liner_mix.py`

## V-0040 — 验证记录（非决策）：R39 内衬在**标准**六相位下的多球复核

- 目标（KNOWN）: 关闭 R39/V-0039 遗留的两个未知 —— (1)「全清 6/6」是否在标准相位下成立；(2) μ 降到 0.05 后「等待区第 2 颗球停靠在扇区外」是否改变。测试标准：全清轮数、真出膛数、清空时间、卡滞占比；退化即记录并收窄结论。
- 方法（SIMULATED）:
  - 新台架 `simulation/mujoco/_work/_r40_liner_mix.py`：独立于 r37/r38，用 monkeypatch 把外罩内弧（`r10_*` / `shell_*`）与/或托板的 geom 摩擦设为目标值并把 priority 提到 2；参数 `--liner / --liner-shell / --liner-tray / --tray / --mu-ball / --qgap / --extra`。**已知坑**：`build_patch(mix, ph0, nip, mu=None)` 必须把球—球摩擦透传（`_orig(mix, ph0, nip, a.mu_ball)`），否则 ball-ball 接触仍是 0.60、混合球序不生效。
  - 换档滞后扫参用 `_work/_r39_v9.py --liner 0.05 --nip-net 86 --mix POLLEN,NECTAR,POLLEN,NECTAR --phases 0,30,60,90,120,150 --sw-delay 0.05`。
  - **几何口径**: `tray = 285`（= `r38_v8.py` 默认、R38/R39 现行板长）。⚠️ 沿用 `r37_multiball.py` 的默认 215 会让球从开口端滚掉（x=4746、z=-64645）；直接调 `R.run_case` 会被其默认覆盖回 215。
- 结果 a（SIMULATED）: 见 DEC-0040 表。逐相位失败明细 —— 内衬 0.05（滞后 0.25 s）: ph0=0 球 3 v=1.54 速度不足、ph0=30 球 3 速度不足 + 球 4 未出膛、ph0=60 球 3+4 未出膛（最小间隙 ln=227.2）；滞后 0.05 s 时 ph0=0 转为 4/4 真出膛，ph0=30 剩球 4 未出膛、ph0=60 仍 2/4。
- 结果 b（SIMULATED，几何事实复现）: 等待区第 2 颗球稳定停在扇区外 —— 4 球混合轮 NECTAR r≈101 / 极角≈327°、POLLEN r≈96-97 / 极角≈316°；跨轮实测 NECTAR r 65.5-106.9 mm / 极角 294-330°、POLLEN 76.4-100.2 mm / 极角 293-317°，**全部判为扫掠不可达**（可达判据 142°-275° 且 r <= 61 + r_ball）。与 V-0037 一致，**未因 μ 变化而改变**。
- 结果 c（SIMULATED，新边界条件）: 托板倾角 5° 下，**托板 μ 必须 > tan5° ≈ 0.09**，否则整队列自滑并在拨杆入口堆死。
- 关键发现（SIMULATED）: (1) R39 的「全清 6/6」是**相位取样偏乐观**；(2) 低摩擦把**速度**问题解决，同时把**节拍余量**问题暴露出来 —— 换档触发是按旧（高摩擦）到达时刻设计的；(3) 剩余失败与球道摩擦、拨杆型面**无关**，指向等待区第 2 颗球的索引几何。
- 未验证（TBD）: 未跑全相位；未实机；μ 仍为 `ASSUMED`；等待区索引几何的修正方案尚未设计。
- 复算命令（KNOWN）: `.venv-cad\Scripts\python.exe -X utf8 simulation/mujoco/_work/_r40_liner_mix.py --liner 0.05 --tag MIXLIN05`；对照 `--liner -1`；11 相位诊断 `--liner 0.05 --tag LIN05`。换档滞后扫参 `_work/_r39_v9.py --liner 0.05 --nip-net 86 --mix POLLEN,NECTAR,POLLEN,NECTAR --phases 0,30,60,90,120,150 --sw-delay 0.05`。
- Date/version: 2026-10-12 / C06B-FEEDER-R40 / 脚本 `_work/_r40_liner_mix.py`、`_work/_r39_v9.py`、`_work/r38_v8.py`

## DEC-0041 — 「降摩擦 / 降压力」路线关闭：三杠杆判决性对照后真出膛锁定 19/24，改为用结构分隔球—球挤压

- 类型（KNOWN）: 路线关闭性决策（负结果，保留历史）。不推翻 DEC-0039 / DEC-0040 —— 低摩擦内衬仍有效（买速度），只是不再往这个方向加力。
- 触发（KNOWN）: 用户指令「你可以试一试减小压力这一种减小摩擦的方式。比如减少球和外罩接触面积等」，中途打断筋条长跑后改为「好，试一试别的方法」。
- 待检验假设（ASSUMED -> 本轮检验）: 若送球段剩余 5/24 失败的原因是**摩擦阻力**，则 (1) 降低最大摩擦接触面的 mu、(2) 直接降低法向载荷，两者都应改善真出膛数。
- 口径（SIMULATED）: R40 真口径 —— `_work/r38_v8.py`（真实两档刚性夹口 + 换档）外面包 `_work/_r39_v9.py` 注入内衬，本轮新台架 `_work/_r42_lever.py` 再加 `--paddle-mu` / `--grav`。固定交替 mix `POLLEN,NECTAR,POLLEN,NECTAR`、相位 0/30/60/90/120/150、`tray=285`、`--nip-net 86`、hold 3.0 s、真出膛门槛 v>=3.0 m/s。有效 mu 与重力是唯一变量。
- 结果（SIMULATED，6 相位 x 4 颗 = 24 颗；同为外罩 mu=0.05 + 托板 mu=0.15）:

  | 口径 | 真出膛 | 全清轮 | t_total 均值 | 最大卡滞 |
  |---|---|---|---|---|
  | 对照（拨杆 mu=0.70、g=9.81） | 19/24 | 5/6 | 20.97 s | 62 % |
  | A 拨杆 mu 0.70 -> 0.10（最大摩擦接触面） | 19/24 | 4/6 | 21.52 s | 69 % |
  | B g=2.0（法向压力 -80 %） | 19/24 | 3/6 | 38.96 s | 91 % |

- 结论（SIMULATED，判决性）: **三口径真出膛完全相同（19/24），且逐轮失败分布也完全相同** —— ph0=60 整轮 1/4、ph0=0 与 ph0=30 的第 3 颗 POLLEN 均以 v=1.52-1.59 m/s「速度不足」出膛。失败点的球种、次序、位置都不随摩擦/压力变化 => **剩余失败不由摩擦或法向压力决定**。降摩擦只压低「蠕动」（卡滞 40 % -> 29 % -> 23 %）却换不来真出膛，与 DEC-0040 同一签名。对照口径逐轮真出膛（3/3/1/4/4/4）与 R40 记录的 T015 逐轮真出膛逐位相同，说明台架是透传的。
- 否证项（SIMULATED，第 5-8 次否证，必须写入历史以免重犯）:
  1. **接触面积与库仑滑动摩擦无关** —— 外罩内弧由整面 108 mm 改 3 x 4 mm 筋（接触面积 -86 %）后，接触力账单（逐接触对象的采样数、平均 |N|、平均 |Ff|、峰值 |N|）**逐位完全相同**（拨杆 10.493 N / 4.807 N / 20.709 N 等）。减少接触面积不改变任何接触力。
  2. **外罩 mu -> 0 无改善** —— 0.05 -> 0.00 反而更差（真出膛 10 -> 7/24）。
  3. **拨杆 mu 0.70 -> 0.10 无改善** —— 真出膛不动，全清 5/6 -> 4/6 反而更差。
  4. **法向压力 -80 % 无改善** —— 真出膛不动，全清 5/6 -> 3/6、清空 21 -> 39 s、ph0=90 那轮拖到 175.9 s / 卡滞 91 %。降低压力不是可靠的减摩手段。
- 工程含义（KNOWN）: 送球段的剩余失败是**索引/落点几何**问题（POLLEN 换档后没被飞轮咬住、球挤着球推挤），不再在摩擦方向上投入试验。已否证的杠杆清单：球道 mu、外罩 mu、拨杆 mu、接触面积、重力/压力。
- Next step（用户 2026-10-12 已批准）: 在托板上加**分隔结构**（每颗球独立落位 / 分球筋），使送球段不再出现球挤着球；随后按同一 R40 口径回跑标准六相位并对照 19/24。仍挂 KEI-20（等待区索引几何 + 换档改事件触发）。
- Risks/未验证（TBD）: 全部为仿真，未实机；mu 仍为 `ASSUMED`；`--nip-net 86` 与 R40 记录一致但 82/86 对汇总不敏感；R40 表格里 T015 行的「t_total 14.53 s / 卡滞 23.5 %」与本轮对照实测（20.97 s / 40 %）不一致，**该两列疑为错行，引用时以本轮实测为准**（真出膛列两处一致）。
- Reversible?: 是。纯仿真 + 文档，未改任何 CAD、未覆盖任何原文件。
- 产物入库口径（KNOWN）: 入库新台架 `_work/_r42_lever.py` + 4 个 `.log`（`_r42_PAD070`、`_r42_PAD070B`、`_r42_PAD010`、`_r42_G20`）。逐帧 trace JSON（`out/_r38_PAD*.json` / `_r38_G20.json`，4.8-10.6 MB/份）**未入库**，理由同 V-0040（体积口径 + 可用已入库脚本复算）；R41 的 11 份 trace JSON 同样未入库，仅入库接触力账单 `out/_r41_RIB.log`。
- Date/version: 2026-10-12 / C06B-FEEDER-R42 / 脚本 `_work/_r42_lever.py`、`_work/_r39_v9.py`、`_work/r38_v8.py`

## V-0041 — 验证记录（非决策）：R41/R42 三杠杆判决性对照，以及两个「错口径」陷阱

- 目标（KNOWN）: 关闭「减小压力 / 减小接触面积能否改善送球成功率」这个未知；同时把 R41 一轮筋条实验的**台架合法性问题**固化下来，避免今后在错口径上做判断。
- 方法（SIMULATED）:
  - 新台架 `simulation/mujoco/_work/_r42_lever.py`：完全复用 `_r39_v9.py`（= `r38_v8.py` + 内衬注入）的机制，只新增 `--paddle-mu`（拨杆 `paddle*` geom 摩擦上限，priority=2）与 `--grav`（改写 `m.opt.gravity[2]`）。
  - 自检（KNOWN）: `--paddle-mu 0.70`（= 原值）必须复现 R40 的 T015 口径；实测 21/24 出膛、19/24 真出膛、全清 5/6、逐轮真出膛 3/3/1/4/4/4 => 与 R40 记录逐位相同，包装器透传成立。
  - 复算命令（KNOWN）: `.venv-cad\Scripts\python.exe -X utf8 simulation/mujoco/_work/_r42_lever.py --liner-shell 0.05 --liner-tray 0.15 --mix POLLEN,NECTAR,POLLEN,NECTAR --phases 0,30,60,90,120,150 --tray 285 --nip-net 86 --hold 3.0 --paddle-mu 0.10 --tag PAD010`；重力对照把 `--paddle-mu 0.10` 换成 `--grav 2.0`。
- 结果 a（SIMULATED）: 见 DEC-0041 表。三口径真出膛均 19/24，逐轮失败分布也相同。
- 结果 b（SIMULATED，接触力账单，R41 筋条诊断，结论有效）: 拨杆扫掠 1.2 s 内球—环境接触 —— `paddle_blade_1` 采样 116、平均 |N| 10.493 N、平均 |Ff| 4.807 N、峰值 |N| 20.709 N；外罩内弧 `r10_19..23` 采样 24-110、平均 |N| 2.39-4.65 N、平均 |Ff| 1.32-1.83 N、峰值 6.5-10.5 N；`paddle_blade_2` / `paddle_flex_1` 各 1-2 次且为 0；**托板在扫掠段完全不受力（0 接触）**。=> 扫掠段的主导摩擦接触是拨杆而非外罩，这解释了「只在外罩降 mu 收益有限」，也定下了本轮 A 杠杆的选择。同组筋条（整面 108 mm -> 3 x 4 mm）与整面**逐位相同**，构成否证 1 的直接证据。
- 陷阱一（KNOWN，台架合法性）: **R41 那批数字全部作废** —— `_work/_r41_ribs.py` 走 `r37_multiball.R.run_case`，夹口取 `max(nip)` 后**全程恒定 82**，没有 `r38_v8.py` 的换档机制。POLLEN（r=35.56）在 82 夹口里根本夹不住，只能以 v≈1.5 m/s 溜出 => 该台架下的 POLLEN 结果与真实机构无关。**今后任何送球台架必须确认换档链路存在（日志里应有 `[换档] ... -> 夹口 64/86`）。** 另注：R41 用**每轮随机 mix**，与 R40 的固定交替 mix 不可直接比数（随机轮会抽到 4xNECTAR / 4xPOLLEN 这类更狠的队形，例如 V15CHK 的 ph0=0 就是 4xNECTAR）。
- 陷阱二（KNOWN，计数口径）: `r37_multiball.run_case` 的出膛判定是「球心在射手坐标 lx > XLIM」，在队列摆放越界或相位边界处会产出**假出膛**（`t=0.00 / 轮内 0.00 / v=0.00`，或 `轮内<=0.05 s`）。R41 某轮记的「出膛 4/4」实为 3 真 1 假。**汇总时必须剔除 `cyc_t <= 0.05 s` 的记录。** R40/R42 走的 `r38_v8.py` 未出现该现象（逐轮轮内均 >3 s）。
- 关键发现（SIMULATED）: (1) 摩擦/压力方向的杠杆已全部试完并全部否证；(2) 剩余失败在三种口径下**位置不变**，是几何/索引问题；(3) 台架口径（换档、mix、nip 覆盖、假出膛）比参数微调更能毁掉一次对比 —— 三次口径事故都发生在这一轮。
- 未验证（TBD）: 未跑全相位；未实机；未测球—球摩擦（`--mu-ball` 恒 0.60，为 `ASSUMED`）；托板分球结构尚未设计。
- Date/version: 2026-10-12 / C06B-FEEDER-R41/R42 / 脚本 `_work/_r41_ribs.py`、`_work/_r42_lever.py`


## DEC-0042 — 决策：R44 分球挡球件（B1 弹性片 / B2 自重挡爪）全部否决，保留加长托板 350 mm

- Decision: 在托板 `s=42 mm`（托板面到挡件基面法向 3 mm）处新增**被动**分球挡件的 B1（贴托板铰 + zip-tie 弹性片）与 B2（上铰 + 自重挡爪）两案，经同口径六相位对照后**两案都否决**；托板加长 215 -> 350 mm 保留（对指标零影响、可多容纳一颗球）；**不装挡件**是当前最优配置（真出膛 19/24、全清 5/6）。
- Reason（SIMULATED，判决性）: 两案在标准口径（`tray=350`、`nip-net 86`、固定交替 mix P>N>P>N、6 相位、`hold 3.0`）下**都退化为死墙**：B1 6/24 真出膛、全清 0/6；B2 6/24、全清 0/6；无挡件对照 19/24、5/6。参数扫描（k = 0.002-0.50 N·m/rad、挡片质量 2-50 g、高度 h = 22 / 50 mm）**18 组全部过不去**。
- 机理（CALCULATED + SIMULATED，本轮新增）:
  1. **B1 是几何失败**：片体以贴托板铰打开后，自身变成相对托板 72° 的斜坡；球在 5° 托板上的爬坡能力只有 5°，故被顶在片体上。实测 k=0.02 时片体只摆开 18.1°（弹簧力矩与队列推力平衡），k=0.002 时摆到 46.3° 仍过不去 —— 摆开越大，斜坡越平但仍远高于 5°。
  2. **B2 是运动学失败**：上铰离托板只有 53 mm，下垂挡爪的爪尖高度上限就是铰高（53 mm），而 NECTAR（r=45.97）通过需要 ≥ 94 mm 净空。实测挡爪已被球推到 61.6°（平均 42.6°），爪尖仍只有 29 mm。**无论挡爪做多重多轻，爪尖都抬不过 53 mm。**
  3. **被动分球在本几何下原理上不成立**：托板 5° 上单颗球的驱动力只有 0.05 N（POLLEN）/ 0.11 N（NECTAR），整条队列（4 颗）的全部推力也只有约 0.15 N，与「挡得住」的门槛同量级 —— 挡得住的配置必然连一颗都放不过，放得过的配置必然一颗都挡不住，两者之间没有可分区间。
- Alternatives（未采纳，保留为后续方向）:
  1. 与球窝联动的**索引杆**（球占据发射位时镇压挡杆关闸、球被扫走后开闸），被动但需要发射位的存在信号；
  2. **舵机主动销闸**（`_work/_r43_pin.py` 台架已建，但存在「插入销执行器后拨杆执行器失效」的未解决 bug，须先修）；
  3. 停位仓 / 球窝（方案 B，靠球窝把球限制为单颗落位）。
- Evidence: `simulation/mujoco/out/_r43_N350.log`（无挡件基线 19/24、5/6）、`_r44_FLEX2.log`、`_r44_PAWL2.log`、排队筛选 `_work/_r43_sweep.py`（18 组参数）、剖面判决图 `out/_r44_gate_verdict.png`。
- Risks: 全部为仿真（SIMULATED），未实机；球—挡件 mu=0.30、球—托板 0.15 仍为 `ASSUMED`；未评估挡件带来的制造/装配误差与球种切换（夹口 64 <-> 86）的交互。
- Next step: 不装被动挡件；若要关闭「一次扫掠连发多颗」，改走索引杆或舵机主动销闸（见上 Alternatives）；本轮的加长托板 350 mm 若最终采纳，需同步把 CAD 里的 `TRAY_X1` 由 215 改为 350 并出剖面图。
- Reversible?: 是。纯仿真 + 文档，未改任何 CAD，未覆盖任何原文件。
- Date/version: 2026-10-12 / C06B-FEEDER-R44 / 台架 `_work/_r43_gate.py`、筛选 `_work/_r43_sweep.py`

## V-0042 — 验证记录（非决策）：R44 B1/B2 分球挡球件六相位对照与排队扫描

- 目标（KNOWN）: 判定「在托板加被动分球结构能否消除送球段球挤着球」这一用户 2026-10-12 指令下的未知。
- 方法（SIMULATED）:
  - 主台架 `simulation/mujoco/_work/_r43_gate.py`（`--gate none|fixed|flex|pawl` + `--gate-s/-h/-t/-w/-k/-m/-gate-clear`，其余透传 `r38_v8.py`），托板加长通过 `--tray 350`。
  - 快速筛选台架 `simulation/mujoco/_work/_r43_sweep.py`：单变量放三颗球、冻结拨杆、把发射位腾空，6 s 内看第 2 颗球能否滚到发射位，并记录挡件峰值摆角。18 组参数每组约 1 s。
  - 复算命令（KNOWN）: `.venv-cad\Scripts\python.exe -X utf8 simulation\mujoco\_work\_r43_gate.py --gate flex --gate-s 42 --gate-h 22 --gate-k 0.02 --gate-m 0.005 --liner-shell 0.05 --liner-tray 0.15 --paddle-mu 0.70 --tray 350 --nip-net 86 --phases 0,30,60,90,120,150 --mix POLLEN,NECTAR,POLLEN,NECTAR --tag R43FLEX2`（B2 把 `--gate flex ... --gate-k 0.02` 换成 `--gate pawl --gate-m 0.005`）。
- 结果 a（SIMULATED，六相位 6 轮 x 4 颗）:
  | 口径 | 真出膛(v>=3.0) | 全清轮 | 挡件峰值摆角 |
  |---|---|---|---|
  | 无挡件 tray=350（`R43N350`） | **19/24** | **5/6** | — |
  | B1 弹性片 k=0.02 m=5 g（`R43FLEX2`） | 6/24 | 0/6 | 18.1 deg |
  | B2 自重挡爪 m=5 g（`R43PAWL2`） | 6/24 | 0/6 | 61.6 deg |
  | （上一轮错口径）B1 k=0.50 m=50 g（`R43FLEX`） | 6/24 | 0/6 | — |
  | （上一轮）B2 m=20 g（`R43PAWL`） | 6/24 | 0/6 | — |
  两案的逐轮失败分布相同：球 1 出膛后球 2/3/4 永久静止（`最近ln=None` / 球 4 停在 ln≈279-282）。
- 结果 b（SIMULATED，排队扫描，`s=42`、h=50、挡件 mu=0.30）: 无挡件时第 2 颗球 0.52 s 滚到发射位；18 组挡件配置**全部未达**，球停在挡件上游 12-30 mm。B1 最软 k=0.002 摆开 46.3 deg、B2 最轻 2 g 摆开 26.6 deg，都过不去。
- 结果 c（SIMULATED，无挡件基线的真实失败模式，本轮重新解读）: 失败不是「挡不住」而是**一次扫掠连发多颗** —— ph0=0 与 ph0=30 两轮里，球 2 与球 3 仅相隔 0.21/0.18 s 被同一轮扫掠带出，第 3 颗以 v=1.49/1.60 m/s「速度不足」出膛；ph0=60 整轮只出 1 颗（球 2/3/4 一直没到位）。=> 队列把多颗球同时送进了轮夹，这才是要解决的「球挤着球」。
- 陷阱（KNOWN，口径事故第 4 次，必须写入历史）: 上一轮 `_r43_FLEX.log` 头部写的是 `gate=flex s=42.0 h=22.0 k=0.50`，**用的是刚性极限 k=0.50，而不是 zip-tie 的软弹性**，导致「弹性片不行」的第一版结论并不公平。**今后判「弹性件能否让路」必须回读日志头部的 `k=`/`m=`，并至少扫 3 档刚度。**
- 关键发现（SIMULATED）: (1) 被动挡件在 `s=42` 无论刚度/配重都是死墙；(2) 加长托板 215 -> 350 对 19/24、5/6 零影响（与 tray=285 的 R42 基线逐轮一致）；(3) 送球段真正要解决的是「一次扫掠连发多颗」，需要能感知「发射位是否为空」的索引机构。
- 陷阱（KNOWN，判读）: 三份日志头部由 `_r43_gate.py` 在 CLI 解析**之前**打印，`tray=` 一律显示默认 **215**，而实际运行是 **350**（以 `r38v8` echo 行 `tray=350` 为准）=> 不是口径事故，别按 215 判废；脚本已改为回显 `--tray` 实参。
- 未验证（TBD）: 索引杆 / 舵机销闸均未实现；`_work/_r43_pin.py` 有「插入销执行器后拨杆执行器不动作」的未解决 bug；未做实物。
- Date/version: 2026-10-12 / C06B-FEEDER-R44 / 脚本 `_work/_r43_gate.py`、`_work/_r43_sweep.py`、`_work/_r44_fig.py`

## DEC-0043 — 决策：R45 主动索引闸改用「竖向全宽挡舌 x=180 + 真实舵机待机停位保持」，6 相位 x 4 颗真出膛 24/24

- Decision: 在用户 2026-10-12 指令「把柱塞改成从侧向摆入的挡舌」下，先实施**侧向摆入**方案并判决性否决，按用户追加授权「侧向摆入不行就换路线」改为**自上方竖直下插的全宽挡舌**（只做 z 向平移、无横向扫掠），闸位由 x=98 后移到 **x=180**、托板加长 **460 mm**；同时给台架加入**真实舵机待机停位保持**（`--park` / `--park-kp`，J_park = 188°）。结果：6 相位 x 4 颗**真出膛 24/24、全清 6/6**（上一版同口径 21/24、5/6）。
- Reason（SIMULATED，判决性）: 见下「侧向摆入被否的三条互斥约束」与「根因」。旧版唯一失败轮 ph0=60 只出 1 颗；同相位在加入停位保持后为 4/4、清空 66.21 s，其余 5 轮逐轮 4/4，清空 74.64 / 66.36 / 66.21 / 66.18 / 66.18 / 66.17 s。
- 侧向摆入被否的三条互斥约束（SIMULATED + CALCULATED，勿回退 x<175）:
  1. **无侧壁**：闸位 x≈98 处托盘没有 +y 侧导槽壁（导槽壁只到 x=12.5），球可横向游到 y≈±54 ⇒ 挡舌必须横跨 108 mm 全宽（L≈106）。
  2. **摆程半径 > 铰到球窝距**：L≈106 的绕竖轴摆程扫掠半径 106 mm > 球窝球到铰心 100.3 mm ⇒ 关门必扫球窝球（实测 1/4）；改用短挡舌 L=40 又挡不住，球从舌尖外侧 y=+42.9 绕过闸口滚过（实测 0/4）。两条互斥，无解。
  3. **正上方是下飞轮**：x=98 正上方是下飞轮盘（圆心 x=124, z=179.5, r=48）；抬起位 z=139.5 与轮重叠 −18.75 mm（几何检验抓到）。
- 陷阱（KNOWN，必须写入历史，本轮新增两例）:
  1. **mocap 假阴性**：仿真里挡舌是 `mocap`、飞轮是动力学体；MuJoCo 中 mocap 只推别人、不会被推，故「抬舌穿飞轮」不报错，但结果被污染（早期「卡滞 79–80%」即来源于此）。**今后 mocap 件与动力学件必须做显式几何重叠检查，不能只看仿真是否报错。**
  2. **待机姿态被忽略**：相位机把待机段写成 `ctrl=0` 等价于「舵机断电自由摆」，与真实舵机的位置保持行为不符，导致一个只咬 NECTAR 的伪卡滞。**今后台架的待机段必须显式写控制律（保持角或阻尼），不得留 0 而不加说明。**
- 根因与修法（SIMULATED + CALCULATED，本轮关键）: 楔死**不在挡舌**，而在拨杆待机姿态 —— `settle` / `settle_tail` 段写 `ctrl=0` ⇒ 拨杆变自由摆、重力下垂到 ≈53° ⇒ 弹性指 `paddle_flex_1`（外缘 r=61）正落在球道内的球心半径上（极角 ≈337°，正是球道/球窝窗口）⇒ 与斜托板形成径向夹口，后到的球在 x≈122 被永久楔死，任何入闸速度都推不动（POLLEN 球心 r=72.4 不在此夹口，故只咬 NECTAR）。修复：`ctrl==0` 时改为速度伺服保持 PARK 角，`d.ctrl[aid] = clamp(Kp * remainder(rad(PARK) - qpos[jid]), ±100)`，Kp=40 1/s、峰值扭矩 0.08*40*0.5 = 1.6 N·m（25-4 Super Speed 失速 0.530 N·m，真实侧加 3:1 皮带配重后仍在量级内）；**补丁放在闸门判决之后**，闸门仍靠 `ctrl==0` 判「拨杆已停」，判据不变。
- 停位角取值（CALCULATED + SIMULATED）: 挡片极角 = 390 − J 不得落进球道/球窝窗口 [235°,355°] ⇒ **J_park ∈ (171°,199°)**，取中点 **188°**。扫角实测：53–95° 楔死（球停 x≈116–123）、105–165° 被挡（x≈50–97）、185–205° 进球窝（x≈25–30）；168/175/195 各跑 ph0=60 单轮全 4/4 ⇒ **±20° 余量，非临界设计**。
- 当前生效参数（KNOWN）: `GX=180.0, GW=108.0, GH=55.0, GT=5.0, GZ_DN=47.5(挡), GZ_UP=139.5(放), 行程 92 mm, GRAMP=0.15 s`；托盘 `--tray 460`；`PARK=188.0, PKP=40.0`；关窗逻辑：抬起后等「被送球整体越过闸口面（tail < GX − GT/2 − GMARG）」就下插（GMARG=3.0, GMAXOPEN=3.0）。
- Alternatives（保留为 superseded / 后续方向）:
  1. **侧向摆入挡舌（superseded）**：三条互斥约束判决性否决，实现脚本与日志保留，不删除；
  2. 被动分球挡件（B1 弹性片 / B2 自重挡爪）：已由 DEC-0042 否决（死墙 6/24），本方案是其后续替代；
  3. 停位仓 / 被动索引杆：未实现，作为更省舵机资源的后续方向保留。
- Evidence: `simulation/mujoco/out/_r45_G6_6p.log`（6 相位 24/24、全清 6/6）、`_r45_G6_p60.log`（ph0=60 单轮 4/4、清空 66.21 s）、`_r45_G6_park168.log` / `_r45_G6_park175.log` / `_r45_G6_park195.log`（停位角鲁棒性各 4/4）、`_r45_G5_6p.log`（上一版对照 21/24、5/6）、`_r45_gate_diag.csv`（闸口 dump：b2 从 x=228 一路滚到球窝 (23,50) 停住，J 稳定保持 188.0）、几何检验 `_work/_r45_idxchk16.py`（A–F 全段无干涉，抬起位净空 NECTAR +3.3 mm）、扫角探针 `_work/_r45_park3.py`、几何/极角验证 `_work/_r45_geodump.py`。
- Risks: 全部为仿真（SIMULATED），未实机；待机保持的 Kp 与峰值扭矩 1.6 N·m 为台架取值，真实舵机 + 3:1 皮带配重的动态与背隙未验证；挡舌 24 次动作的时序在实物上的抖动未评估；μ 系列仍为 `ASSUMED`。
- Next step: 把竖向挡舌与停位保持同步进 CAD（闸位 x=180、托板 460 mm、挡舌下插/抬起两个位置），并做索引闸在球种切换（夹口 64 <-> 82）下的综合复核；如需更省舵机资源，再评估停位仓方案。
- Reversible?: 是。纯仿真 + 文档，未改任何 CAD，未覆盖任何原文件；旧方案按 superseded 保留。
- Date/version: 2026-10-12 / C06B-FEEDER-R45 / 台架 `_work/_r45_gate4.py`（生成器 `_work/_mk_gate4.py`）、底座 `_work/r37_multiball.py` + `_work/r38_v8.py`

## V-0043 — 验证记录（非决策）：R45 主动索引闸六相位 x 4 颗全流程

- 目标（KNOWN）: 判定用户 2026-10-12 指令「柱塞改侧向摆入挡舌」的可行性，并在侧向不可行时换路线验证「索引闸能否消除送球段球挤着球、把全清率拉满」。
- 方法（SIMULATED）: 台架 `simulation/mujoco/_work/_r45_gate4.py`（= `_r45_gate3.py` + `--park` 补丁，由 `_work/_mk_gate4.py` 生成）；口径 `--mix POLLEN,NECTAR,POLLEN,NECTAR --tray 460 --gate-x 180 --phases 0,30,60,90,120,150 --hold 3 --mu 0.6 --park 188`；挡舌为全宽 z 向 mocap 板，抬起/下插两个位置由闸门状态机驱动；闸门判决仍用 `ctrl==0`，停位保持补丁在其后写入。
- 复算命令（KNOWN）: `.venv-cad\Scripts\python.exe -X utf8 simulation\mujoco\_work\_r45_gate4.py --mix POLLEN,NECTAR,POLLEN,NECTAR --tray 460 --gate-x 180 --phases 0,30,60,90,120,150 --hold 3 --mu 0.6 --park 188`（加 `--gate-dump` 出 `out/_r45_gate_diag.csv`；单相位把 `--phases` 改成 `60`）。6 相位全跑约 4 分钟。
- 结果 a（SIMULATED，六相位 6 轮 x 4 颗，口径对照）:
  | 口径 | 出膛/真出膛 | 全清轮 | 清空（逐轮 s） |
  |---|---|---|---|
  | R45 竖向挡舌 x=180 + 停位保持 188°（`R45G6`） | **24/24** | **6/6** | 74.64 / 66.36 / 66.21 / 66.18 / 66.18 / 66.17 |
  | R45 竖向挡舌 x=180，无停位保持（`R45G5`） | 21/24 | 5/6 | 唯一失败轮 ph0=60 只出 1 颗 |
- 结果 b（SIMULATED，停位角扫角探针 `_work/_r45_park3.py`）: 53–95° 球停 x≈116–123（楔死，接触 `paddle_flex_1` + `tray`）；105–165° 球停 x≈50–97（被挡，进不了球窝）；185–205° 球停 x≈25–30（进球窝）。安全区间 (171°,199°) 与几何推导一致。
- 结果 c（SIMULATED，停位角鲁棒性）: 168 / 175 / 195 各跑 ph0=60 单轮，全部 4/4 真出膛 ⇒ 取值有 ±20° 余量，不是临界设计。
- 结果 d（SIMULATED，闸口轨迹复核 `_r45_gate_diag.csv`，t=9.5–14.0 s）: 第 2 颗球从 x=228 一路滚到球窝 (23,50) 停住，不再在 x≈122 楔死；待机期间拨杆角 J 稳定在 188.0。
- 结果 e（SIMULATED，挡舌动作序列）: 24 次动作全部为「抬起 -> 球已过闸口 -> 下插」，无一次误动作或超时（`GMAXOPEN=3.0 s` 内完成）。
- 几何检验（SIMULATED/L3）: `_work/_r45_idxchk16.py 185` 输出 A–F 全段无干涉，抬起位对 NECTAR 净空 +3.3 mm。
- 陷阱（KNOWN，写入历史）: ①台架脚本头部说明与默认 `GX` 仍描述旧的 x=98 方案，实际口径由 `--gate-x 180` 指定 ⇒ **判读前必须回读日志头部 `x=`**，这是本仓库第 5 类「文字口径与运行口径不一致」事故；②mocap 挡舌穿飞轮不报错（见 DEC-0043 陷阱 1）。
- 未验证（TBD）: 未实机；未测挡舌实物摩擦/惯性；停位保持 Kp 与 1.6 N·m 峰值扭矩未与真实舵机 + 3:1 皮带配重比对；未做实物节拍（仿真单颗节拍 ≈22.8 s NECTAR / ≈15.6 s POLLEN）；CAD 侧尚未落进竖向挡舌与 x=180 闸位。
- Date/version: 2026-10-12 / C06B-FEEDER-R45 / 脚本 `_work/_r45_gate4.py`、`_work/_r45_park3.py`、`_work/_r45_geodump.py`、`_work/_r45_show.py`、`_work/_r45_idxchk16.py`

## DEC-0044 — 决策：R47 提速改用「外罩内弧 + 托板贴低摩擦胶带」，闸板后移 / 减小行程 / 纯几何改喉口三条路全部判决性否决

- Decision: 在用户 2026-10-12 指令「试一试能否通过闸板后移与减小行程来使速度更快，1 分钟太慢了」下，先逐项验证该路线（闸板后移 x=220/240、闸板前移 x=150、缩短扫掠 `--sweep 120/200`、三个纯几何旋钮 `--flex-in/--blade-in/--exit-open`），**全部判决性否决**；改为**零几何改动**的单侧降摩擦：外罩内弧与托板顶面贴低摩擦胶带（等效 μ ≈ 0.30），拨杆侧不动、不贴带（用户 2026-10-12 追加约束「我没有使用弹性外缘的条件」，与此前「弹性指外缘难度较大，估计现有条件能贴降低摩擦的胶带」一致）。结果：6 相位 x 4 颗**真出膛 24/24、全清 6/6、清空 5.22–5.28 s**，相对 R45 的 66.2 s 约 **13 倍**提速。
- Reason（SIMULATED + CALCULATED，判决性）:
  1. **慢的根因不是闸板、不是行程，而是摩擦楔自锁** —— 球在「拨杆叶片顶端 ↔ 外罩出口唇」喉口被摩擦楔楔死，拨杆电机全程贴 0.530 N·m 堵转上限。台架运动学：转速 290 rpm ⇒ 整圈仅 360/(290*6) = 0.207 s，而实测每颗球 15–23 s、卡滞占比 77–89 % ⇒ **拨杆约 99 % 时间没在转**。「减小行程」的理论上限因此只有约 0.207 x 4 ≈ 0.8 s，该路线在算术上就不成立。
  2. **闸板后移会连带把整列球往后推、把闸口让给球 ⇒ 闸板失守**（真出膛掉到 2/4），同时前排球位置 `b1 x=-40.2` 与基准逐位一致 ⇒ 闸板位置对发射行程零影响。
  3. **`--sweep` 是死参数** —— `r38_v8.py` 第 138–139 行把扫掠段写成 `sweep_end = J0 + 360*kk + sw`、`reindex_end = J0 + 360*(kk+1)`，第 141 行两段共用同一恒定速度 `d.ctrl[aid] = w * SPD[...]` ⇒ 改 sweep 只改个名字。
- 否决证据（SIMULATED，判读基准 `--gate-x 180 --hold 1 --mu 0.6 --park 188`、mix P>N>P>N）:

  | 组 | 口径 | 清空 | 卡滞 | 真出膛 | 判定 |
  |---|---|---|---|---|---|
  | 基准 | gate-x 180、tray 460 | 52.19 s | 89 % | 4/4 | — |
  | 闸板后移 | gate-x 220、tray 560 | 35.43 s | 84 % | **2/4** | ✗ 闸板失守 |
  | 闸板后移 | gate-x 240、tray 580 | 16.5 s | 53 % | **2/4** | ✗ 同上，提速是假的 |
  | 闸板前移 | gate-x 150、tray 430 | 54.6 s | 89 % | 4/4 | 略差 |
  | 缩短行程 | `--sweep 200` | 52.19 s | 89 % | 4/4 | 与基准逐位相同 |
  | 缩短行程 | `--sweep 120` | 52.19 s | 89 % | 4/4 | 逐位相同 |
  | 纯几何 | `--flex-in 3` | 53.0 s | 89 % | — | ✗ |
  | 纯几何 | `--blade-in 3` | 54.32 s | 89 % | — | ✗ |
  | 纯几何 | `--exit-open 3` | 51.11 s | 89 % | — | ✗ |
  | 纯几何 | `--flex-in 5` | 53.67 s | 89 % | — | ✗ |
  | 纯几何 | 三者同时 | 53.45 s | 89 % | — | ✗ |

  ⇒ 闸板 / 行程 / 几何三条路在 μ=0.60 下都救不回来，印证用户判断「现有条件能贴降低摩擦的胶带」。
- 摩擦悬崖（SIMULATED，外罩/托板单侧降 μ，拨杆保持 0.70）:

  | 外罩 μ | 清空 | 卡滞 |
  |---|---|---|
  | 0.05 / 0.08 / 0.10 / 0.12 / 0.15 / 0.20 | 5.0–5.09 s | 1 % |
  | 0.25 | 5.14 s | 1 % |
  | **0.30（设计点）** | **5.22 s** | **1 %** |
  | 0.35 | 5.41 s | 4 % |
  | 0.40 | 6.76 s | 24 % |
  | 0.50 | 60.4 s | 90 % |

  悬崖落在 μ 0.40–0.50 之间；**取 0.30 为设计点**（1 % 卡滞且离悬崖仍有余量，比 0.35 更稳）。
- 接触测绘（SIMULATED，`_work/_r47_touch.py`，基准一轮球-静态件累计法向冲量）:

  | geom | 冲量 N·s | 占比 | 拨杆轴极角范围 |
  |---|---|---|---|
  | `paddle_blade_2`（叶片推球面） | 433.2 | 34.1 % | 113.8°–261.5° |
  | `r10_00…r10_20`（外罩内弧整圈） | ≈600 | ≈47 % | 135°–258° |
  | `paddle_flex_1/2` | 127.7 | 10.0 % | 88.5°–235.1° |
  | `tray`（托板） | 89.9 | 7.1 % | — |
  | `shell_exit_face`（出口唇） | 21.1 | 1.7 % | 129.5°–147.6° |

  ⇒ **贴带目标：外罩内弧 135°→258°（约 123° 弧长）+ 托板顶面**；拨杆侧不动、不贴带。
- 验收口径与结果（SIMULATED）: 台架 `_work/_r47_geo.py`，`--liner-shell 0.30 --relief -0.20`（拨杆不动、不贴带），6 相位 0/30/60/90/120/150 x mix P>N>P>N、tray 460、gate-x 180、hold 1、μ_ball 0.6、park 188：
  **清空 5.28 / 5.23 / 5.22 / 5.23 / 5.23 / 5.23 s；每轮真出膛 4/4、全清 6/6、卡滞 1–2 %、拨杆扭矩峰 0.507–0.522 N·m。**
  恶劣工况：4 x NECTAR（最大最重、tray 520）μ0.30 -> 5.33 s / 4/4 / 2 %；μ0.20 -> 5.14 s；μ0.40 -> 7.41 s / 30 %；4 x POLLEN -> 5.05 s / 4/4 / 1 %。
  **胶带厚度（`--relief -0.20 / -0.50` 模拟贴带占位）对结果无影响** ⇒ 打印件不需要预缩，直接贴即可。
- 硬约束（KNOWN，勿违反）: 托板倾角 5° ⇒ **托板 μ 必须 > tan5° ≈ 0.09**，否则整队列自滑并在拨杆入口堆死（V-0040）。设计点 μ≈0.30 远高于该下限；**不要为追求速度把外罩/托板降到 0.05**。
- Alternatives（保留为 superseded / 后续方向）:
  1. 闸板后移 + 缩小行程（superseded）：理论提速上限仅 0.8 s 且闸板失守，脚本与日志保留，不删除；
  2. 纯几何改喉口（`--flex-in / --blade-in / --exit-open`，superseded）：μ=0.60 下 5 组全无改善；
  3. 弹性指 / 弹性外缘（superseded）：用户明确不具备制造条件，放弃；
  4. 停位仓 / 索引杆：仍作为更省舵机资源的后续方向保留（承接 DEC-0043）。
- Evidence: `simulation/mujoco/out/_r47_ref.log`、`_r47_gate220_t560.log`、`_r47_gate240_t580.log`、`_r47_gate150_t430.log`、`_r47_sw120.log`、`_r47_sw200.log`、`_r47g_*.log`（几何否决）、`_r47s_shell*.log`（悬崖）、`_r47lo_s*.log`、`_r47t_*.log`（胶带厚度）、`_r47v30_p0*.log`（6 相位验收）、`_r47w_*.log`（恶劣工况）、`_r47_tape_section.png`（剖面示意图，红色 = 贴带弧 135°→258°）；脚本 `_work/_r47_run.py`、`_work/_r47_geo.py`（生成器 `_work/_mk_r47geo.py`）、`_work/_r47_touch.py`、`_work/_r47_fig.py`；JSON `out/_r38_r47*.json`。
- Risks: 全部为仿真（SIMULATED），未实机；μ=0.30 对应「一般 3D 打印 PET 层高 0.4 mm + 低摩擦胶带」的组合，仍标 `ASSUMED`；胶带选型 / 宽度 / 端头处理 / 翘边未定；胶带占位厚度对节拍无影响，但对实物贴合工艺未验证。
- Next step: 把贴带落进 CAD（外罩内弧 135°→258° 扇区 + 托板顶面），按 DEC-0039 的方式决定预缩或直接贴；如需更省舵机资源再评估停位仓。
- Reversible?: 是。纯仿真 + 文档，未改任何 CAD，未覆盖任何原文件；旧方案按 superseded 保留。
- Date/version: 2026-10-12 / C06B-FEEDER-R47 / 台架 `_work/_r47_geo.py`、批量驱动 `_work/_r47_run.py`、接触测绘 `_work/_r47_touch.py`、示意图 `_work/_r47_fig.py`

## V-0044 — 验证记录（非决策）：R47 提速路线对照（闸板 / 行程 / 几何 / 胶带）

- 目标（KNOWN）: 判定用户 2026-10-12 指令「闸板后移 + 减小行程能否提速」的可行性，并在否决后验证「单侧贴低摩擦胶带」能否在**零几何改动**下消除卡滞。
- 方法（SIMULATED）: 台架 `simulation/mujoco/_work/_r47_geo.py`（= `_r46_relief.py` + `--flex-in/--blade-in/--exit-open` 三个径向几何旋钮，`--relief` 负值模拟贴带占位厚度；底座 `r37_multiball.py` / `r38_v8.py` 未改）；批量驱动 `_work/_r47_run.py`（环境变量 `GATE4` 选台架、`LOGPFX` 加日志前缀）；接触测绘 `_work/_r47_touch.py`。
- 复算命令（KNOWN）: `.venv-cad\Scripts\python.exe -X utf8 simulation\mujoco\_work\_r47_geo.py --mix POLLEN,NECTAR,POLLEN,NECTAR --tray 460 --gate-x 180 --phases 0,30,60,90,120,150 --hold 1 --mu 0.6 --park 188 --liner-shell 0.30 --relief -0.20 --tag r47v30`（6 相位约 30 s）。
- 结果 a（SIMULATED，路线否决）: 见 DEC-0044 表 1 —— 闸板后移 2/4、`--sweep` 与基准逐位相同、5 组几何旋钮全无改善。
- 结果 b（SIMULATED，摩擦悬崖）: 见 DEC-0044 表 2 —— μ 0.30 为设计点（5.22 s / 1 %），悬崖在 0.40–0.50。
- 结果 c（SIMULATED，验收）: 6 相位全清 6/6、真出膛 24/24、清空 5.22–5.28 s、卡滞 1–2 %、扭矩峰 0.507–0.522 N·m。
- 结果 d（SIMULATED，恶劣工况）: 4 x NECTAR μ0.30 -> 5.33 s / 4/4 / 2 %；μ0.20 -> 5.14 s；μ0.40 -> 7.41 s / 30 %；4 x POLLEN -> 5.05 s / 4/4 / 1 %。
- 结果 e（SIMULATED，胶带厚度）: `--relief -0.20 / -0.50`（0.2 / 0.5 mm 占位）与 0.15/0.25/0.30/0.35 各组合均在 5.0–5.4 s ⇒ 无影响。
- 结果 f（SIMULATED，接触测绘）: 见 DEC-0044 表 3 —— 外罩内弧 ≈47 %、叶片推球面 34 %、弹性指 10 %、托板 7 %。
- 陷阱（KNOWN，写入历史）: ①闸板台架 `_r45_gate4.py` 头部 `GX=98` 是旧默认，实际由 `--gate-x 180` 覆盖 ⇒ **判读前回读日志第 3 行 `x=`**；②`--sweep` 参数名还在，但被硬编码的整圈同速覆盖，**不要用它做行程实验**（本轮已用逐位相同的日志证死）；③台架 `--relief` 为负值表示「贴带占位使通道变大」，与 `--flex-in` 等正值旋钮方向相反。
- 陷阱（KNOWN，写入历史，本轮第 4 条）: **示意图脚本 `_work/_r47_fig.py` 曾把拨杆硬编码成 3 叉（相位 30/150/270）**，与实际模型不符 —— 仿真模型一直是**两叉**（`r37_multiball.py` 第 54 行 `def parts(phases=(330.0, 150.0))`，第 202 行调用未传参），所有仿真数据（含接触测绘的 `paddle_blade_1/2`、`paddle_flex_1/2`）均基于两叉、有效。已把绘图脚本改为 330/150 两叉并重出 `_r47_tape_section.png`。**教训：示意图的机构相位必须与模型同源，不得在绘图脚本里手写自由度。**
- 未验证（TBD）: 未实机；μ=0.30 为 `ASSUMED`；胶带选型 / 带宽 / 端头 / 翘边未定；贴带尚未落进 CAD。
- Date/version: 2026-10-12 / C06B-FEEDER-R47 / 脚本 `_work/_r47_geo.py`、`_work/_r47_run.py`、`_work/_r47_touch.py`、`_work/_r47_fig.py`

## DEC-0045 — 决策：R47 台架落盘为独立 MJCF（4 份 XML + 驱动脚本），并修复混装换档缺陷

- Decision: 按用户 2026-10-12 指令「我要你在MUJOCO仿真用的文件」，把 R47 验收口径台架（DEC-0044 口径）**落盘为独立 MJCF 文件**，交付 4 份 XML 与 1 份驱动脚本；同时修复驱动脚本混装模式把路径字符串当成模型对象传入 `xfer()` 的缺陷。
- Reason （KNOWN）:
  1. 此前全部台架（`r37_multiball.py` / `r38_v8.py` / `_r47_geo.py` 等）用 `from_xml_string` 字符串建模，模型从未落盘 ⇒ 外部无法加载、无法复现。
  2. 模型的摩擦 / priority / 径向让位是在**编译后**直接写编译器数组的（不在 XML 文本里），直接 `mj_saveLastXML` 会丢这些改动 ⇒ 必须按 geom 名回注文本并回读逐项比对。
  3. **MJCF 无法表达控制逻辑**：挡舌是 `mocap` body（z 47.5↔139.5 mm 抬落）、待机停位保持是外部速度伺服（188°、Kp=40） ⇒ 两者必须由运行脚本注入，只加载 XML 不会动。这是交付包必须含脚本的原因。
  4. 混装模型对（64 / 82 mm）必须靠脚本换档，且换档时要搬运 `qpos/qvel/ctrl/act` 全状态；两档模型结构必须一致（脚本启动即校验球径序列）。
- Alternatives: ①只交结果 JSON（已被用户否决）；②只交单个合并 XML（不可行 —— 单份 XML 只能有一个轮间夹口，且 keyframe 无法表达挡舌/停位）；③把挡舌写成 `<equality>` / 位置伺服（会改变模型物理、与已验收口径不一致）。采用②的变体：**四份 XML 各自自洽 + 一份驱动脚本**。
- Evidence （SIMULATED）:
  - 4xPOLLEN gap064 ph0：4/4，6.21–6.44 m/s，全清 11.11 s。
  - 4xNECTAR gap082 ph0：4/4，5.27–5.44 m/s，11.45 s。
  - 混装 `--pair` ph0：4/4，自动换档 3 次（64→82→64→82），6.43 / 5.26 / 6.32 / 5.28 m/s，11.28 s。
  - 落盘校验：回读 XML 与捕获模型逐项比对（geom 名 / 摩擦 / priority / pos / size、keyframe0 qpos、nq / nv / ngeom / nbody / nu）全等。
  - 口径：`--mix POLLEN,NECTAR,POLLEN,NECTAR --tray 460 --gate-x 180 --phases 0 --hold 1 --mu 0.6 --park 188 --liner-shell 0.30 --relief -0.20`。
- 注入规则（KNOWN，已与模型比对通过）: `shell_*`/`r10_*` → μ 0.30 + priority 2 + 径向让位 −0.20 mm；`tray`/`ramp` → μ 0.30 + priority 2（**不做径向让位**）；`paddle*` → μ 0.70 + priority 2；`gate*` → μ 0.40 + priority 2；球 → μ 0.60 + priority 1。
- 交付位置: `simulation/mujoco/out/R47_launcher_mixed4_gap064.xml`、`R47_launcher_mixed4_gap082.xml`、`R47_launcher_4xPOLLEN_gap064.xml`、`R47_launcher_4xNECTAR_gap082.xml`；驱动 `simulation/mujoco/run_R47_xml.py`；生成/校验 `simulation/mujoco/gen_R47_mjcf.py`；桌面同名副本。
- Bugs fixed: 驱动脚本 `--pair` 原先把路径字符串传给 `xfer()` 导致报错 ⇒ 现在启动时把两档都建成 `Rig` 实例并校验球径序列一致。
- Risks: 四份 XML 与台架脚本存在**双份真源**（台架改参数后必须重新 `gen_R47_mjcf.py`）；桌面副本不受 Git 管理。
- 已裁剪（superseded）: 更早的 `R47_launcher_4ball.xml` / `_gap064.xml` / `_gap082.xml`（单相位、无 keyframe 集）按用户指令从桌面与 `out/` 删除，保留本条记录。
- Next step: 若需对外发布，在 `gen_R47_mjcf.py` 加 `--check` 回归；待用户明确接受后把 `T06-R47-MJCF-1.0` 从候选转为接受记录。
- 未验证（TBD）: 未实机；XML 只含代理几何与验收参数，未含 CAD 细节。
- Date/version: 2026-10-12 / C06B-FEEDER-R47-MJCF-1.0 / 脚本 `simulation/mujoco/gen_R47_mjcf.py`、`simulation/mujoco/run_R47_xml.py`

## DEC-0046 — 决策：建立 T06 运动部分几何基准文档，并据以核对 CAD 版本（核对轮 R48，无几何改动）

- Decision （KNOWN）: 新建 `docs/engineering/t06-motion-part-geometry-baseline.md` 作为**运动部分几何位置关系的唯一主索引**（坐标、半径、相位、间距只定义一次并逐项标注来源版本），并用它对 CAD 产物做一次版本与几何核对；按核对结果交付一份带部件名、Fusion 可直接打开的运动部分装配到桌面。本轮**不修改任何几何、不覆盖任何原 STEP**，生成脚本 `cad/paddle_launcher_motion_check.py` 只读复用 R37/R39 生成器。
- Reason （KNOWN）: 用户 2026-10-13 指令「使用 linear、notion 以及项目中的 .md 整理目前整个机构（最新版）的运动部分的几何位置关系，用于检查 CAD 文件是否版本正确、几何正确……注意识别信息来源的版本，确认是目前版本」。此前几何事实散落在 R37/R39 参数块、DEC-0035/0036/0039/0043/0044、Linear KEI-17..20 与 Notion 页中，且 `docs/engineering/launcher-feeder-baseline.md` 仍是三叶片旧基线（R27 前），没有一份能直接用来判版本的文件。
- 来源版本（本条记录的判定依据）: `PROJECT_STATUS.md` §LATEST DESIGN VERSION（2026-10-12，`T06-R47-MJCF-1.0` 候选）；`config/parameters.yaml` → `t06_feeder_r37`（DEC-0035/0036）、`t06_liner_r39`（DEC-0039）——**这是 parameters.yaml 里最新的两个 T06 块**；`docs/decision_log.md` DEC-0032/0035/0036/0039/0043/0044/0045；Linear KEI-20（2026-10-13T00:05Z）；Notion「Decision — Redo the POLLEN feeder as a coaxial one-piece shell with a 5 deg gravity tray」（最后编辑 2026-10-13T00:05Z）。
- 版本判定 （KNOWN）: **CAD 产物最新 = `_r37_stage/`（2026-10-11 22:16）+ `_r39_liner/`（2026-10-12 02:16）；仿真验收最新 = `T06-R47-MJCF-1.0`（2026-10-12）。二者不是同一代。** KEI-20 自己也写明「CAD 侧未落进：竖向挡舌 + x=180 闸位 + 托板 460 mm；外罩内弧 135°→258° 与托板顶面的贴带区」。
- 核对结论 （MEASURED）:
  1. 桌面 `T06_R37_pollen.step` / `T06_R37_nectar.step` 与仓库 `_r37_stage/paddle_launcher_feeder_a_prime_shared_staging_*.step` **逐字节相同**（SHA256 `80CB3ED05CEDC283081B255D0780ED42E0DC5892071EB8127E6BC2A2E36B1966`），且与 R005 几何检验所测文件同一哈希 ⇒ 桌面 R37 文件版本正确。
  2. 回归 R005 4/4 pass：托板右端 215.2615（目标 215 ± 0.5）、飞轮组 z 上限 338.7996（338.8 ± 1.0）、体积 930299.217（930299.902，相对偏差 1e-6）、根实体 23。
  3. 本轮独立复算：16 部件体积合计 **930299.1 mm³**（发布值 930299.9，差 0.8 mm³）；拨杆轴心实测 **(29.49, 0, 111.46)** 与 KNOWN 值零偏差；轮轴距 **161.60 / 179.60** = 2 × 80.8 / 2 × 89.8；冷态夹口 65.60 / 83.60 − 2 × dr_hot = 热态 64.0 / 82.0（DEC-0032）✔；轮轴分离方向 −38° 与 52° 球道正交 ✔；TPU 尖实测极角 30°/210°（两片相隔 180°，**两叉**，与 `r37_multiball.py` 一致）。
  4. R39 内衬单体 5/5 pass（内弧偏移 +0.4876、外弧 −0.0002、托板面 −0.4608、扇区 142.0–275.0°）。
- 交付 （KNOWN）: 桌面 `T06_motion_pollen.step`（SHA256 `57EBA523…C0EAA9`）/ `T06_motion_nectar.step`（`2342C3D3…4E1C181`），各 18 部件 / 25 实体，带部件名与颜色（外罩半透明蓝、飞轮近黑、拨杆橙、TPU 尖黄、贴带红）；回读 948918.082 mm³、包围盒 z 上限 333.259 / 338.800。仓库副本 `cad/output/_motion_check/`，并附 `T06_motion_check_report.md`。
- 版本不一致（须用户决策，本轮**未改 CAD**）:
  - F1 **托板右端**：CAD 215.0（DEC-0035）vs 最新口径 **460**（DEC-0044 验收；中途另有 R44 的 350，DEC-0042 亦未落地）⇒ `fail`。
  - F2 **竖向全宽挡舌**：CAD 里**不存在该零件**（R37 的 13 个自制件无 gate，`cad/*.py` 无生成器）⇒ 而 R47 的 6/6 全清、24/24 真出膛**依赖挡舌**（DEC-0043）⇒ `fail`，缺件。
  - F3 **贴带区**：CAD 无贴带；R39 下料带扇区 142°→275°，而 R47 实测贴敷区为 **135°→258°** + 托板顶面 ⇒ `fail`，未落地且扇区口径不同。
  - F4 **参数主数据**：`config/parameters.yaml` 最新 T06 块 = `t06_liner_r39`，R40–R47 全部决策无参数条目 ⇒ `not_run`。
- Alternatives: ①直接把 CAD 改到 R47 口径（改托板长度 + 新增挡舌 + 贴带区）—— 否决：属结构级变更，未经用户确认，且会覆盖「当前 CAD 基线」的版本语义；②只交检查报告不改文件 —— 否决：用户明确要桌面交付件；③把 R39 预缩变体当作交付 —— 否决：DEC-0044 已判定「不需要预缩」，且预缩会让交付件与仿真所验面差 0.5 mm。采用「**CAD 原样 + 贴带区标注件 + 版本表**」。
- Risks （KNOWN）: ①交付件里的 `liner_tape_arc` / `liner_tape_tray` 是**贴敷位置标注件**，不是打印件也不是裁带下料件（下料件仍为 `_r39_liner/liner_tape_*.step`）；②CAD 版本落后于仿真版本，**当前 CAD 不得当作已验证机构的可制造版本**；③桌面副本不受 Git 管理。
- Next step: 等用户就 F1–F3 决策；若确认按 R47 口径重做 CAD，需先落 X=180 挡舌零件与托板 460 mm 的新 DEC，再改 `_r37_stage` 之后的新生成器（**不得改** `cad/paddle_launcher_constrained.py` / `feeder_a_prime*` 原文件）；同时把 R40–R47 的口径补进 `config/parameters.yaml`（F4）。
- 未验证（TBD）: 未实机；μ ≈ 0.30 仍为 `ASSUMED`；胶带选型/带宽/端头/翘边未定。
- Date/version: 2026-10-13 / `T06-MOTION-BASELINE-R48` / 脚本 `cad/paddle_launcher_motion_check.py`、`cad/_readback_delivery.py`；证据 `cad/output/_motion_check/parts_{pollen,nectar}.json`、`delivery_readback.json`、`docs/engineering/t06-motion-part-geometry-baseline.md`

## V-0046 — 验证记录（非决策）：R48 运动部分几何核对（CAD 版本 + 几何 + 交付回读）

- 目的 （KNOWN）: 用可追溯的几何基准判「最新 CAD 文件是否版本正确、几何正确」，并为后续仿真/制造提供一份位置关系明确、Fusion 可开的运动部分装配。
- 方法 （MEASURED）:
  - 版本同一性：对桌面与仓库 STEP 取 SHA256 与 R005 报告中的输入哈希逐一比对。
  - 几何复算：`cad/paddle_launcher_motion_check.py` 调 R37 staging 生成器取最终实体，逐件量 `n_solids` / 体积 / 包围盒 / 质心；由包围盒中心反推拨杆轴心与飞轮轴心。
  - 交付回读：`cad/_readback_delivery.py` 用 `cq.importers.importStep` 回读导出的桌面 STEP，量根实体数 / 体积 / 包围盒。
  - 量具纪律：遵守 V-0039 —— 球道面偏差用导出网格 + 射线求交，本轮不涉及该量具；本轮量的是实体包围盒与体积，不做 OCC `distance` 判读。
- 结果 （MEASURED）:
  - 版本：桌面 = 仓库 = R005 输入，SHA256 三者相同（`80CB3ED0…`）⇒ pass。
  - 几何：16 部件体积合计 930299.1 mm³ vs 发布 930299.9（差 0.8 mm³，相对 8.6e-7）⇒ pass；拨杆轴心 0 偏差；轮轴距/夹口/dr_hot 关系全部成立 ⇒ pass。
  - 交付：25 实体、948918.082 mm³（930299.1 + 18618.8 贴带件 = 948917.9）⇒ pass。
  - 不一致项：F1 托板 215 vs 460（fail）、F2 挡舌缺件（fail）、F3 贴带区未落地（fail）、F4 参数主数据滞后（not_run）。
- 状态: `pass`（CAD 版本与几何本身）\+ `fail`（与最新仿真口径的版本一致性，见 F1–F3）\+ `not_run`（F4）。**不得**据此把 `T06-R47-MJCF-1.0` 或 CAD 标为最终。
- 未验证项: 与 DEC-0046 的 TBD 相同（未实机、μ 假设、工艺未定）。
- Date/version: 2026-10-13 / 产物 `cad/output/_motion_check/`

## DEC-0047 — 决策：T06 闸门行程 92 -> 72 mm、驱动改为 25-3 曲柄滑块、支架横梁与绿腿齐平（R49）

- Decision （KNOWN）: 对 T06 主动索引闸（DEC-0043 口径）做三处改动并落到新生成器 `cad/paddle_launcher_gate_drive_r49.py`（**只读复用** R37 staging / R39 内衬 / 采购件 STEP，不覆盖任何原文件）：
  1. **舵机 SKU** `2000-0025-0002`（25-2）-> **`2000-0025-0003`**（25-3 Speed）。
  2. **行程 92 -> 72.074 mm**：挡舌中心关闭位 `47.5 -> 67.482`（下端 `20.0 -> 40.0`），打开位保持 `139.557`（下端 112.1）。
  3. **支架横梁收边**：`x 165..205 -> 176..204`、`y 34..72 -> 34..62`，与绿腿（`LEG_X 176..204`、`LEG_Y 34..42`）外面齐平。
- Reason （KNOWN）: 用户 2026-10-12 指令「用 25-3，把突出的深蓝部分剪掉，让其与绿色底部平齐，同步改动并完善 CAD 图」；行程改动的触发是更早的「挡板不一定要有那么大的行程，最下端低于 pollen 中心即可」。截图圈选的深蓝凸出件经比对确认为**支架横梁**（原左伸到 x=165，比绿腿左面 176 多出 11 mm；外伸到 y=72，比立柱外面 62 多出 10 mm），不是中间立柱。
- 行程收短依据 （CALCULATED）: pollen 待机球心 z ≈ **55.1**、球顶 ≈ 90.7；挡舌下端 **40.0** 比球心低 **15 mm** 仍能拦住（球被托板 5° 面与前球顶住，不会翻越），打开后闸口净空 **21 mm** > 球径 71.12 的有效通过裕度。上抬上限经扫参 ≈ 67.5（70 / 72.5 / 77.5 会跑球 3/4）。
- 曲柄滑块（CALCULATED）: 曲柄中心 `(190, 0, 240)`、`r = 38.35`、连杆 `L = 90`、偏置 `DX = 10`；扫角 `20° -> 160°`（两端各离死点 20°，不自锁）。`z_pin = 240 + 38.35 sin(phi)`，`blade_centre = z_pin − 27.5 − 22.0` ⇒ 实测关闭 **67.482** / 打开 **139.557** / 行程 **72.074 mm**；销 z 116.982 -> 189.057。
- 舵机能力 （KNOWN，2026-10-12 联网核实 goBILDA 官方规格）: `2000-0025-0003` = 2000 Series Dual Mode Servo（25-3, Speed），**出厂默认位置模式**（能保持闸门位，不需要额外保持力），7.4 V 堵转 **1.059 N·m**、**0.07 s/60°（≈145 rpm）**。外壳与花键和 `2000-0025-0002` **完全相同** ⇒ 支架 / 曲柄 / 连杆 / 销的接口一律不变，选型只改 SKU。曲柄 `r = 38.35 mm` ⇒ 销切向力 ≈ **27.6 N**，而闸门阻力 < 1 N ⇒ **余量 > 20x**；140° 行程约 **0.16 s**。
- 几何（MEASURED，`cad/output/_r49_gate/parts_pollen.json`）: 挡舌 `5 × 108 × 55`、x `177.5..182.5`、y `±54`、vol 27432.0、下端双面 `CHISEL_H = 12.0 / CHISEL_FLAT = 1.5` 倒角（DEC-0043 的抗卡楔保留）；支架 **vol 56352 -> 44704 mm³**；立柱/横梁两实体 bbox `x 175..204, y 34..62, z 13.29..198`（对称两件）。
- 干涉复检（MEASURED）: `frame × bracket` / `frame × blade` / `frame × rod` 在 2 个姿态、共 56 组布尔求交**全部 0 mm³**。
- 验收（SIMULATED，`simulation/mujoco/run_R47_xml.py`，R47 台架 MJCF，`--gate-dn 67.5 --gate-up 139.5 --gate-ramp 0.15`）:
  - 4 × POLLEN `gap064`，6 相位 0/30/60/90/120/150：**每相位 4/4 真出膛 = 24/24**，全清 **6/6**，出膛速度 **6.28–6.44 m/s**，清空 11.08 / 11.09 / 11.09 / 11.09 / 11.14 / 12.79 s（含静置 6 s）。日志 `simulation/mujoco/out/_r49_reg.log`。
  - 4 × NECTAR `gap082` 与混装 `--pair`（自动换档）：见 V-0047。
  - ramp 敏感性：0.10 / 0.15 / 0.25 / 0.70 s 均 24/24；**0.20 与 0.40 s 出现球 3 / 球 4 逸出**（非单调）⇒ 判为数值/接触敏感性，**按 0.15 s 验收**。0.20 s 的机理：闸门关瞬间挡舌接触 ball_3，Fz 峰值 −960 N —— 是 mocap 无限刚度下的数值尖峰，**不是设计载荷**（真实舵机 1.059 N·m / 曲柄 38.35 mm ⇒ 上限 27.6 N）。
- Alternatives: ①保留 92 mm 行程 —— 否决：用户明确要求缩短，且实测 72 mm 无收益损失（24/24 与旧口径一致）；②保留 25-2 —— 否决：用户指定 25-3，且 25-3 与 25-2 同壳同花键（零接口风险）；③把横梁改成与立柱齐平但不改 x —— 否决：截图凸出的是**左侧 11 mm**，只改 y 不解决观感；④顺手把中间立柱也收掉 —— 否决：立柱是支架唯一的固定点，收掉后支架无支撑（需另加托板下支撑，属结构级变更，本轮不动）。
- 命名（KNOWN）: 生成器由 `_r48.py` / `_r48_view.py` 改名为 `_r49.py` / `_r49_view.py`，因为 **DEC-0046 已占用 "R48 = 运动部分几何核对轮"**，避免同一编号指两件事。
- Superseded: DEC-0043 的 **92 mm 行程**（中心 47.5 / 下端 20）与 **25-2 舵机**口径被本条取代，历史保留不删除；R47 交付的顶梁外形同样被本轮收边取代。
- Risks （KNOWN）: ①横梁收边后 **zip-tie 绑扎路径**与 25-3 出线方向未实机验证；②挡舌下端 40.0 只比 pollen 球心低 15 mm，**若实机球在托板上被抬起 > 15 mm 会失守**（仿真内未见，但依赖托板与前球约束）；③`μ ≈ 0.30` 贴带仍为 `ASSUMED`；④桌面副本不受 Git 管理。
- Next step: 实机验证挡舌在 40.0 处的拦球裕度与 zip-tie 绑扎；若托板件改版需同步 `LEG_Y 34..42` 与收边后的 34..62。
- 未验证（TBD）: 未实机；闸门控制律仍属台架口径（停稳 + 0.10 s 抬起）；球质量 / μ 仍为 `ASSUMED`。
- Date/version: 2026-10-12 / `T06-GATE-DRIVE-R49` / 脚本 `cad/paddle_launcher_gate_drive_r49.py`、视图 `cad/paddle_launcher_gate_drive_r49_view.py`；证据 `cad/output/_r49_gate/parts_pollen.json`、`r49_gate_drive_view.png`、`simulation/mujoco/out/_r49_reg.log`、`config/parameters.yaml → t06_gate_drive_r49`

## V-0047 — 验证记录（非决策）：R49 闸门驱动（行程 72 mm + 25-3 + 横梁收边）

- 目的 （KNOWN）: 确认换 25-3、缩短行程、横梁收边三处改动**不破坏**已验收的发射能力，并给出可复算的几何与干涉证据。
- 方法 （MEASURED）:
  - 几何：`cad/paddle_launcher_gate_drive_r49.py` 生成后 `dump()` 逐件量 `n_solids` / 体积 / 包围盒 / 质心，落 `parts_pollen.json`。
  - 干涉：布尔求交（`cq.Workplane.newObject` 组包后 `intersect`；直接 `Shape.intersect(Shape)` 不可用），2 姿态 x 56 组。
  - 出膛：R47 台架 MJCF（`T06-R47-MJCF-1.0` 落盘件）+ `run_R47_xml.py`，真出膛速度取 `cvel[bid][3:6]` 模长，阈值 3.0 m/s。
  - 量具纪律: 沿用 V-0039 / V-0046，不以 TUI 目视为判据。
- 结果 （MEASURED / SIMULATED）:
  - 行程：实跑回显「中心 67.5 -> 139.5 mm，下端 40.0 -> 112.0 mm，行程 72 mm」⇒ 与 `parts_pollen.json` 的 **72.074 mm** 一致 ⇒ `pass`。
  - 干涉：56 组全部 0 mm³ ⇒ `pass`。
  - 出膛 4 × POLLEN gap064、6 相位：**24/24 真出膛、6/6 全清**，6.28–6.44 m/s ⇒ `pass`（与旧 92 mm 口径 24/24 逐项同量级）。
  - 4 × NECTAR gap082 ph000：**4/4 真出膛 5.22–5.29 m/s，全清 11.46 s**；混装 `--pair` ph000：**4/4 真出膛 6.43 / 5.27 / 6.43 / 5.22 m/s，自动换档 3 次，全清 11.66 s** ⇒ `pass`，与 R47（DEC-0045）旧口径逐项同量级。日志 `simulation/mujoco/out/_r49_reg2.log`。
- 状态: `pass`（几何 / 干涉 / 出膛）；`not_run`（实机、zip-tie 绑扎、25-3 出线）。
- 未验证项: 未实机；挡舌 40.0 拦球裕度只由仿真支撑；`μ = 0.30` 为 `ASSUMED`。
- Date/version: 2026-10-12 / 产物 `cad/output/_r49_gate/`、`simulation/mujoco/out/_r49_reg.log`

## DEC-0048 — T06 发射部分驱动化 + 支撑结构（R50）

- Decision （KNOWN）: 在 R37 运动件与 R49 闸门之上补齐发射部分的驱动链与承载框架，**R37/R47/R49 的生成器与产物一律只读复用、不覆盖**：(1) 飞轮驱动 x2 = goBILDA `5203-2402-0003` 马达 + `1401-0043-0036` 夹具 + `4007-4008-4008` 联轴器，上下飞轮各自直驱，两台马达统一在 -Y 侧；(2) 拨杆驱动 x1 = goBILDA `2000-0025-0004`（25-4 Super Speed）+ `1802-0043-0001` 支架 + `4001-0025-4008`（25T -> 8 mm REX）联轴器，置于 +Y 侧；(3) 支撑框架 = 双侧 6 mm 打印面板（三个轴心 R34 凸台 + 44 mm 连杆轮廓 + 三条腿）+ 3 根横梁（底部横梁带 4 个 O4.6 底盘安装孔）。生成器 `cad/paddle_launcher_shooter_drive_r50.py`，视图 `cad/paddle_launcher_shooter_drive_r50_view.py`。
- Reason: (1) 用户指令「给飞轮加上马达，给拨杆加上舵机（两者已经确定型号，注意查找），同时给整个发射部分加上支撑结构」；(2) 型号不是新选型而是**沿用已固定口径** —— 飞轮马达链来自 C06B-COTS-0.1 / DEC-0021，拨杆舵机来自 DEC-0026 的 `index_drive_servo`（`config/parameters.yaml` 第 284 行）；(3) 面板画成凸台/连杆轮廓而不是整块板：所有轮廓都落在 |y| >= 65、机体（外罩与导轨 |y| <= 57、拨杆转子 |y| <= 48）之外的空白区，只有三根轴穿过面板，因此面板不需要任何让位孔；(4) 拨杆轴在 -Y/+Y 两侧都改用 `1611-0514-4008` 轴承座（轴承 4 -> 6），使拨杆轴由框架承担径向载荷而不是只靠送料桥。
- Alternatives considered: ①用外置齿轮同步两飞轮 —— 否决：C06B-COTS-0.1 已明确保留两根独立直驱轴、外置齿轮数为 0；②把拨杆舵机放在 -Y 侧与马达同侧 —— 否决：-Y 侧 y -219..-68 已被两台马达 + 夹具 + 联轴器 + 马达桥占满，无可用工位；③支撑框架做成单侧板 —— 否决：单侧悬臂使飞轮轴与拨杆轴都成悬臂梁，且 DEC-0037 口径下飞轮座要承受径向交变载荷；④面板做成整块矩形板再开让位孔 —— 否决：与机体（外罩 / 导轨 / 闸门支架）干涉面太多，挖孔量远大于直接用轮廓；⑤横梁挖空 / 桁架 —— 本轮未做，见 Risks。
- Evidence （MEASURED / CALCULATED）: `cad/output/_r50_drive/parts_pollen.json`（51 件，`build_s = 2428.2`）：面板 2 x 189479.7 mm³、横梁 151632.0 / 134784.0 / 104591.8 mm³、马达桥 4 x 9152.0、伺服桥 2 x 4368.0 mm³ ⇒ 打印件合计 815311.2 mm³（≈ 1035 g @ PETG 1.27 g/cm³，密度为 ASSUMED）。轴向堆叠实测与生成器常量逐项一致：马达体 -219.17..-112.00、夹具 -120..-112、马达桥 -112..-68、联轴器 -96.5..-75.5、面板 -71..-65 / 79..85、飞轮轴 -84..84、拨杆轴 -96..96、舵机联轴器 88.0..105.0、舵机支架 96..102、舵机体 101.5..145.6。轴心从最终实体量取：上 (-11.368, 285.259)、下 (115.975, 185.769)、拨杆 (29.490, 111.460)。干涉复检（布尔求交）7 处非零，**全部是轴 / 轴承 / 联轴器的正常径向配合**（联轴器 x 飞轮轴 25.308 x2、轴承 x 轴 5.883 / 6.725 x4、舵机联轴器 x 拨杆轴 21.739）；`servo_frame x servo_coupler`、`servo_coupler x servo_bridge_-28/+28`、`servo_coupler x shooter_frame_neg/pos` **全部 0 mm³**；`servo_coupler x servo = 3.182 mm³` 为 25T 花键齿顶轻咬，判为可接受。
- 修掉的隐患（MEASURED）: 舵机联轴器原本用 `Shape.mirror("XZ")` 定姿态 —— 那是绕**世界** XZ 平面镜像，把件搬到 y -105.0..-88.0（马达侧），**与舵机完全不接**（旧姿态实测 `servo_coupler x servo = 0`、`servo_coupler x paddle_shaft = 119.232 mm³`，纯属错误穿模）。改为「平移到原点 -> 绕自身 X 直径翻转 180 度 -> 平移回位」后，联轴器落在 y 88.0..105.0，径向剖面实测：y 88.0..96.0 为 REX 通孔（r >= 4.0，套住止于 96.0 的拨杆轴端）、y 96.5..100.0 为 R5.0 本体、y 100.5..101.5 为 25T 花键孔、y 102.0..105.0 为花键孔径全开。注意 `Shape.rotate` 的两个向量是「点 + 方向」而不是「起点 + 终点」，把放置中心当起点会让件绕近似 Y 轴自旋 —— 因此翻转必须在原点做。
- Risks: ①打印件 815.3 cm³ ≈ 1035 g PETG，**偏重**，横梁（391.0 cm³）与面板（379.0 cm³）都还有挖空余量，本轮未做；②结构强度与振动完全未验（无计算、无实机）；③舵机联轴器与舵机壳面只留 0.6 mm，实机装配公差与舵机支架厚度偏差可能吃掉；④-Y 侧马达外伸到 y = -219.17，整机底盘落位时该侧突出量需与底盘 / 立柱复核；⑤桌面副本不受 Git 管理。
- Next step: 用户先看三视图与 STEP 是否接受；接受后再决定是否挖空横梁 / 面板减重、以及 25-4 是否切连续旋转（影响拨杆能否按 DEC-0037 的两档刚性定位工作）。
- 未验证（TBD）: 未实机；未做强度 / 振动 / 热分析；拨杆舵机控制律（位置 vs 连续旋转）与 DEC-0037 调隙链的整机落位未裁定。
- Date/version: 2026-10-13 / `T06-SHOOTER-DRIVE-R50` / 脚本 `cad/paddle_launcher_shooter_drive_r50.py`、视图 `cad/paddle_launcher_shooter_drive_r50_view.py`；证据 `cad/output/_r50_drive/parts_pollen.json`、`r50_shooter_drive_view.png`、`config/parameters.yaml → t06_shooter_drive_r50`、`references/vendor/gobilda/t06/manifest.json`

## V-0048 — 验证记录（非决策）：R50 发射部分驱动链与支撑框架

- 目的 （KNOWN）: 确认新增的两台飞轮马达、拨杆舵机与支撑框架**几何上接得上、彼此不干涉**，且不改变已验收的 R37 运动件与 R49 闸门口径。测试标准：(1) 驱动链接合面对得上；(2) 舵机联轴器同时咬住拨杆轴端与舵机花键；(3) 新增件对既有件无非预期干涉；(4) 轴心与轴向堆叠口径与既有验收记录一致。
- 方法 （MEASURED）:
  - 几何：`cad/paddle_launcher_shooter_drive_r50.py` 生成后 `dump()` 逐件量 `n_solids` / 体积 / 包围盒，落 `parts_pollen.json`（51 件）。
  - 姿态：对舵机联轴器做径向剖面探测（逐 y 切片求最大半径），确认通孔 / 花键孔 / 本体的轴向分布。
  - 干涉：布尔求交（`cq.Workplane.newObject` 组包后 `intersect`），分两组 —— 新增件 x 既有件（R37 / R49），以及驱动链内部相邻对（9 对）。
  - 量具纪律: 沿用 V-0039 / V-0046 / V-0047，不以 TUI 目视为判据；轴心从最终实体量取，不手输。
- 结果 （MEASURED）:
  - 飞轮链接合：`motor_coupler x flywheel_shaft = 25.308 mm³ x2`（圆轴 vs REX 剖面建模差）、`flywheel_bearing x shaft = 5.883 / 6.725 mm³ x4` —— 均为径向配合 ⇒ `pass`。
  - 舵机链接合：`servo_coupler x servo = 3.182 mm³`（花键齿顶）、`servo_coupler x paddle_shaft = 21.739 mm³`、`servo_frame x servo_coupler = 0`、`servo_coupler x servo_bridge_-28/+28 = 0`、`servo_coupler x shooter_frame_neg/pos = 0` ⇒ `pass`。
  - 偏差记录与修正：旧姿态（`Shape.mirror("XZ")`）下 `servo_coupler x servo = 0`、`servo_coupler x paddle_shaft = 119.232 mm³` ⇒ 说明**此前生成的 JSON / STEP 里舵机联轴器在错误位置**；本轮已重刷 JSON 与桌面 + 仓库 STEP ⇒ `pass`（修正后）。
  - 结构强度 / 质量 / 实机装配 ⇒ `not_run`。
- 状态: `pass`（几何 / 姿态 / 干涉）；`not_run`（实机、强度、振动、减重）。
- 未验证项: 打印件 815311.2 mm³ 的实机质量与刚度；舵机联轴器 0.6 mm 壳面间隙的装配裕度；整机底盘落位。
- 交付件回读 （MEASURED）: 用 `cad/_r50_readback.py`（`cq.Assembly.load`）回读**桌面交付件** `T06_shooter_drive_R50_pollen.step`：加载 407.6 s、**51 个 children**（与生成器 `parts_pollen.json` 的 51 件同名同数）；逐件比对体积与包围盒，**0 处漂移**（阈值 体积 2 % / 包围盒 0.5 mm）；总体积 回读 2077828.0 mm³ vs 生成器 2077829.4 mm³，相对偏差 **6.5e-07** ⇒ 导出没有丢件或改形，落盘文件 = 被测模型。报告 `cad/output/_r50_drive/delivery_readback.json`。全程 686.8 s。`pass`
- Date/version: 2026-10-13 / 产物 `cad/output/_r50_drive/`（`parts_pollen.json`、`r50_shooter_drive_view.png`、`delivery_readback.json`、`T06_shooter_drive_R50_pollen.step`）

## DEC-0049 — T06 发射部分换基线到 2026-10-01 全整机，侧板开口改 59x56 滑窗（R51）

- Decision （KNOWN）: 发射部分（shooter）**换基线**为 `cad/output/paddle_launcher_feasible_pollen.step`（2026-10-01 22:36，414.3 MB / 98 件）—— 即用户说的「只保留运动部分」**之前最新一版**（它是 `paddle_launcher_motion_only.py --profile motion_free` 的父装配）。在该基线上只做两处改动，产物记作 **R51**：(1) 拨杆舵机 `2000-0025-0003` -> `2000-0025-0004`（DEC-0026 的 `index_drive_servo`；2000 系列外壳与花键相同 ⇒ 支架 / 曲柄 / 联轴器接口不变）；(2) **侧板开口由 `8.4 x 9` 轴槽改成 `59 x 56` 滑窗**。R37 / R47 / R49 / R50 的生成器与产物一律**只读复用、不覆盖**；新产物写入 `cad/output/_r51_drive/`，生成器 `cad/paddle_launcher_shooter_drive_r51.py`。同时把 R50 的支撑框架判为**不满足需求**（见 DEC-0048 的 SUPERSEDED 补记）。
- Reason: (1) 用户指令「两个飞轮不能连在一起，这样没法调间隙。你应该使用在『只保留运动部分』之前最新一版的 CAD 做基础来进行改动。先把那一版 CAD 找出来截张侧视图给我」；(2) 10-01 基线**已经是**「两轴各自独立 + 调隙链」的正确拓扑：每根飞轮轴坐在自己的**滑动轴承滑座**上，分别由 DEC-0037 调隙链（`2000-0025-0002` -> 12 mm 曲柄 -> 65 mm 拉杆 -> 十字头 -> 两根 110 mm 连杆 -> 滑座耳片）定位；(3) 基线唯一的真缺陷是侧板开口：老 `8.4 x 9` 轴槽只覆盖半间距 80..89（夹口 64..82），**够不到 NECTAR 已被接受的 86 mm 夹口**（半间距 91），而且被 `46 x 12 x 38` 滑座与两根 `5 x 10 x 52` 导轨**同时跨占**（板与运动的滑座抢同一块料）。改成 59 x 56 滑窗后，两档都被覆盖（半间距 80.0..91.2 ⇒ 夹口 64.0..86.4），滑座与导轨以 0.5 mm 侧隙从窗中通过，导轨改顶在窗壁上作侧向导向 —— 正好是原侧板注释一直想表达的设计意图。
- Alternatives considered: ①**留在 R50 框架上再加调隙机构** —— 否决：R50 的框架本身就是跨接两轴的刚体，任何加装都只是把锁死点换个位置；②**用「只保留运动部分」后的运动版做基础** —— 否决：那是抽取版（18 件），既不是用户指的基线，也缺驱动、底座与调隙链；③**在 R50 的 6 mm 面板上开双轴独立轴承座** —— 否决：面板是「三凸台 + 连杆 + 三腿」整板，要变成可动滑座等于重画底座，成本高于直接用 10-01 已含滑座 / 导轨 / 调隙链的底座；④**手动滑窗 + 螺栓锁位（不用舵机）** —— 未采用：用户此前已明确「我调整间隙采用的是舵机方案」，故保留 DEC-0037 的舵机调隙链；⑤**改小滑座或导轨以塞进老轴槽** —— 否决：会动到 DEC-0037 的连杆几何与滑座刚度，收益小于改开口。
- Evidence （MEASURED / CALCULATED）: 基线版本判定：`cad/output/_r51_base/manifest.json` = `cq.Assembly.load` 直接回读 10-01 STEP，**98 件**逐件记录体积 / 包围盒 / 三角数；侧视图 `cad/output/_r51_base/r51_base_side_view.png` 已交付桌面 `T06_基线_2026-10-01_侧视图.png`。R51 实测（`cad/output/_r51_drive/report_r51.json`，98 件 / 434.4 MB / 两变体）：开口覆盖 `pollen` 滑座 n 跨距 61.0..99.0、`nectar` 72.0..110.0，**两者都在窗内 56.5..112.5**，`carriage_inside_window = true`、`rails_inside_window = true`、导轨侧隙 0.5 mm；夹口行程 64.0..86.4。**轴隔离（本轮核心判据）**：bbox 保守筛选（超集）只剩**一个**候选 `shooter_side_plate_-1`，布尔求交对它 vs 上下滑座 = **0.0 / 0.0 mm³**（`touches_both = false`）；`carriages_touch_each_other = false`、`shafts_touch_each_other = false` ⇒ `rigid_link_between_axles = []`。侧板专项（`cad/output/_r51_drive/plate_booleans_r51.json`）：15 组候选（两滑座 / 导轨 x4 / 两飞轮轴 / 拨杆轴 / 轴承座 x2 / 马达桥 x4）在两档夹口下**全部 0 mm³**。驱动链沿用基线：联轴器 x 飞轮轴 24.724 x2、舵机联轴器 x 拨杆轴 92.315。
- Risks: ①滑座在滑窗内只靠两侧导轨定位，缺锁紧 / 微调件（滑窗只保证「能滑」，没保证「滑到位置后不自走」）；②R51 是 98 件全整机底座，打印件质量与刚度均未统计；③桌面 `T06_shooter_drive_R50_*.step` 仍在（superseded 但按规则不删）；④未实机。
- Next step: 把 R37 送球件与 R49 闸门搬到该底座上（已由 DEC-0050 完成）；后续按用户裁定决定是否给滑座加锁紧 / 微调，以及拨杆舵机工作模式。
- 未验证（TBD）: 未实机；结构强度 / 振动未验；滑座锁紧方式未定；打印件质量未统计。
- Date/version: 2026-10-13 / `T06-SHOOTER-DRIVE-R51` / 脚本 `cad/paddle_launcher_shooter_drive_r51.py`；证据 `cad/output/_r51_base/manifest.json`、`cad/output/_r51_drive/{report_r51.json,plate_booleans_r51.json,r51_shooter_view_*.png,r51_drive_support_sheet_pollen.png}`；`config/parameters.yaml -> t06_shooter_drive_r51`

## V-0049 — 验证记录（非决策）：R51 两根飞轮轴是否真的解耦（滑窗开口）

- 目的 （KNOWN）: 证明「两根飞轮轴不再被任何刚性件连在一起、夹口可在两档之间调」，并且滑窗开口确实覆盖 pollen / nectar 两档 —— 这是用户判据「两个飞轮不能连在一起，这样没法调间隙」的直接验收项。测试标准：(1) 除滑座 / 轴 / 飞轮 / 轮毂之外，**没有任何件同时接触上下两个滑座**；(2) 侧板本身与两滑座 / 导轨 / 轴 / 轴承座 / 马达桥的布尔交为 0；(3) 两档滑座行程都落在窗内；(4) 导出 STEP 与被测模型一致。
- 方法 （MEASURED）: `cad/paddle_launcher_shooter_drive_r51.py` 生成后逐件量体积 / 包围盒 -> `report_r51.json`；隔离性用**两级筛选** —— 先 bbox（保守超集，先证「没有漏网候选」），再对幸存者做真实布尔求交；侧板另跑 `plate_booleans_r51.json`（两档各 15 组）；开口覆盖用滑座 / 导轨的 n 跨距与窗 56.5..112.5 直接比大小；量具纪律沿用 V-0039 / V-0046 / V-0047（不以 TUI 目视为判据）。
- 结果 （MEASURED）: (1) `rigid_link_between_axles = []`，bbox 候选只有 1 个且布尔 0.0 / 0.0 ⇒ `pass`；(2) 15 组布尔**全 0**（两档）⇒ `pass`；(3) 两档 `carriage_inside_window` / `rails_inside_window` 均 true，导轨侧隙 0.5 mm ⇒ `pass`；(4) 交付 STEP 98 件 / 434.4 MB，两变体各 1 份。结构强度、锁紧方式、实机 ⇒ `not_run`。
- 状态: `pass`（隔离 / 开口覆盖 / 交付件数量与体积）；`not_run`（强度、锁紧、实机）。
- 未验证项: 滑座在窗内的锁紧与重复定位精度；打印件质量与刚度；整机装配。
- Date/version: 2026-10-13 / 产物 `cad/output/_r51_drive/`、`cad/output/_r51_base/`

## DEC-0050 — T06 R52：把 R37 送球件 + R49 闸门搬到 R51 独立轴底座上

- Decision （KNOWN）: 在 R51 底座之上把**已验收的送球与闸门件原样搬过来**，产物记作 **R52**（当前最新发射总成）：(1) 送球件 = `ST.build_variant_stage` 的 `R37_FEEDER_NAMES` **6 件**（`feeder_shell_tray`、`paddle_rotor`、`paddle_flex_tip_1/2`、`paddle_shaft_2106-4008-1920`、`paddle_shaft_support_bridge`），**世界坐标一律不动**（`r37_frozen_coordinates = true`）；(2) 闸门 = `G49.drive_parts(G49.PHI_DN, 0)` 9 件，并让 `gate_frame` 对 R37 托板做 **530.017 mm³ 让位**（只切闸门侧、不动 R37 只读件）；(3) 侧板 = R51 滑窗板 + 在 R37 拨杆轴处挖 `O14.1` 轴承座（用 `world_xz_to_local()` 反算）；(4) 新增支撑 = `servo_bridge_±26` + `feeder_mount_±1`（x -80..168、y 53.5..63、z 16..30，0.5 mm 咬住托板壁、搁在底盘纵梁顶面、距闸门支架 >= 7 mm）；(5) 拨杆驱动沿用 R50 已验证的 +Y 堆叠（`2000-0025-0004` + `1802-0043-0001` + `4001-0025-4008` + `1611-0514-4008` x2）。生成器 `cad/paddle_launcher_shooter_drive_r52.py`；产物 `cad/output/_r52_drive/`。R51 / R37 / R49 生成器与产物只读复用。
- Reason: 用户指令「把 R37 + R49 那套送球件搬到这个独立轴底座上」—— 即：把已经过 MuJoCo 验收的送球 + 闸门几何放到**两根飞轮轴解耦**的底座上，形成一版可继续做仿真的发射总成。
- Alternatives considered: ①把送球件按新底座重新建模 —— 否决：会破坏 R37 的验收口径（球道 / 球窝 / 叶尖半径都是量出来的），且违背「不覆盖原文件」；②改 R37 件的坐标去适配底座 —— 否决：同上，且 DEC-0035/0036 的几何证据会失效；③新做一版闸门支架 —— 否决：R49 的曲柄滑块与行程（92 -> 72 mm）已验证，直接搬 + 让位更省。
- Evidence （MEASURED）: `cad/output/_r52_drive/report_r52_{pollen,nectar}.json`：90 件；夹口 pollen 64.0 / nectar 86.0；拨杆轴实测 `[29.49, 111.46]`（与 R37 一致）；上轴 `[-10.737, 284.767]`、下轴 `[115.345, 186.261]`、轴距 160.0；叶尖 r 59.908，叶尖到下轮面 pollen 5.961 mm / nectar 8.55 mm；`imported_vs_base = []`（R37/R49 与 R51 底座 0 干涉）、`gate_vs_feeder = []`、`new_vs_rest` 5 处**全部是正常配合**（`feeder_mount ±1 x feeder_shell_tray` 81.651 x2 咬合、`paddle_bearing_-1 x 侧板` 10.285 轴承座配合、`paddle_servo_coupler x paddle_shaft` 21.739 花键、`servo_bridge_-26 x gap_servo_frame` 1.372 接触）；`gate_frame_relief_mm3 = 530.017`。交付 `T06_shooter_assembly_R52_{pollen,nectar}.step`（90 件 / 444.6、444.7 MB），回读（`cad/_r52_readback.py`）：各 **282 solids**、体积偏差 **-0.0001 %**、包围盒 6 面偏差 **0.00 mm**，`bbox = [-170.0, -219.17, -3.51, 232.0, 145.6, 401.02]`。桌面已放装配图与 STEP。
- Risks: ①`feeder_mount ±1` 与托板只 0.5 mm 咬合，是「搁着 + 咬壁」的简化连接，强度未验；②R52 生成器的 `axle_isolation` 把 `shooter_side_plate_` 放进了 skip 列表 ⇒ **侧板在该轮没做布尔**，侧板证据来自 R51 的 15 组布尔（全 0）与本轮新增的 STEP 级复核 `cad/_r52_axle_isolation_step.py`（直接读交付 STEP）；③拨杆舵机工作模式（位置 vs 连续旋转）仍未裁定；④打印件质量未统计；⑤未实机。
- Next step: 用 R52 作为运动部分做仿真（送球 + 发射全流程口径沿用 R47 台架）；如需给滑座加锁紧 / 微调件，在 R51 底座上做增量修改。
- 未验证（TBD）: 未实机；结构强度 / 振动未验；打印件质量未统计；送球件与底座的连接强度未验。
- Date/version: 2026-10-13 / `T06-SHOOTER-DRIVE-R52` / 脚本 `cad/paddle_launcher_shooter_drive_r52.py`；证据 `cad/output/_r52_drive/{report_r52_pollen.json,report_r52_nectar.json,readback_r52.json,r52_assembly_sheet_*.png}`；`config/parameters.yaml -> t06_shooter_drive_r52`

## V-0050 — 验证记录（非决策）：R52 换装后的干涉与交付一致性

- 目的 （KNOWN）: 确认「R37 送球件 + R49 闸门」搬到 R51 底座后**接得上、不打架、不改已验收口径**，且导出的 STEP 与被测模型一致。测试标准：(1) 送球 / 闸门件与 R51 底座 0 干涉；(2) 闸门不与送球件干涉；(3) 拨杆轴心与 R37 验收值一致；(4) 回读交付 STEP 与生成器逐项一致。
- 方法 （MEASURED）: `cad/paddle_launcher_shooter_drive_r52.py` 生成后逐件量体积 / 包围盒 -> `report_r52_{pollen,nectar}.json`；干涉用布尔求交分组比对（R37+R49 vs 底座、闸门 vs 送球、新增件 vs 其余）；发货前落盘报告、再出图、再导 STEP；导出后用 `cad/_r52_readback.py` 重新 `importStep` 回读（注意：该脚本的 `axle_isolation_hits` 是**从报告里复制的**，不是从 STEP 重新推导的，故不算独立证据）。
- 结果 （MEASURED）: 干涉 3 组判定 —— `imported_vs_base` 0 处、`gate_vs_feeder` 0 处、`new_vs_rest` 5 处（**全部为正常配合**，见 DEC-0050 明细）⇒ `pass`；轴心与 R37 一致（拨杆 `[29.49, 111.46]`）⇒ `pass`；回读 282 solids、体积偏差 -0.0001 %、包围盒偏差 0.00 mm ⇒ `pass`。结构强度、锁紧、实机 ⇒ `not_run`。
- 状态: `pass`（干涉 / 轴心 / 交付一致性）；`not_run`（强度、实机）。
- 未验证项: `feeder_mount` 连接强度；滑座锁紧；拨杆舵机工作模式；实机装配。
- Date/version: 2026-10-13 / 产物 `cad/output/_r52_drive/`

## DEC-0051 — T06 滑座改常闭弹簧夹：取消人工锁位，换档仍由已有 25-2 调隙舵机自动完成（R53b）

- Decision （KNOWN）: R53 的**蝶形螺母手动锁位**作废。判据是用户本轮指令：「停，在比赛中人不能介入去动结构，我希望该结构可以利用已有舵机自动调节。」R53b **保留 R52/R53 的全部尺寸**，只换紧固件栈 —— 每颗螺柱由「蝶形螺母」改为 **M4 螺柱 + 压缩弹簧（Ø5.5 / 自由长 8.4 / 装好 6.0）+ 平垫 + M4 尼龙锁紧螺母**。弹簧**始终处于压缩态** ⇒ 两块 3 mm 耳板恒压侧板 ⇒ **断电也锁住**（fail-safe）；预载刻意取小（3 N/颗）⇒ 现有调隙舵机`2000-0025-0002`（25-2，堵转 2.471 N·m）照旧推得动滑座 ⇒ **换档（POLLEN 半间距 80 / NECTAR 91）仍然自动完成，不需要人工、不需要新舵机、不需要新通道**。同时把侧板锁紧长槽由「只开 +n 一侧」改为 **u = ±36 x n = ±(63.5..107.5) 共 4 条**。脚本 `cad/paddle_launcher_shooter_lock_r53b.py`，产物 `cad/output/_r53b_auto/`（该目录是指向桌面的 junction）。
- Reason: (1) 用户判据 —— 比赛中不允许人工拧螺母；(2) R53b 的「自动」不是新增执行器，而是**把夹紧这件事从"人工施加"改成"弹簧常压"**，调隙本身早在 DEC-0037 就已经是舵机链（12 mm 曲柄 -> 65 mm 拉杆 -> 十字头 -> 两根 110 mm 连杆 -> 滑座）；(3) 弹簧常闭还顺手解决了断电风险：滑座在断电、掉力、受飞轮反力冲击时都不会漂；(4) 长槽必须两侧对称 —— 两个滑座分别在 n = ±half_spacing，只开 +n 一侧会让另一侧的 8 颗螺柱直接穿透 4 mm 实心侧板。
- Alternatives considered: ①**留在 R53 蝶形螺母** —— 否决：用户判据（比赛中人不能介入）；②**什么都不加，靠舵机通电保持位置** —— 否决：滑座靠舵机齿轮保持，断电 / 掉力 / 长时间堵转发热都会被飞轮侧向反力推走，而比赛里有撞击与断电重启；③**另加一个夹紧舵机（主动夹紧/解锁）** —— 暂不采用：需要额外通道，而且用户这一轮问的正是"用已有舵机"；**若用户确认还有空闲通道，可在此件上加凸轮做主动解锁**（见 open_question）；④**偏心轮 / 凸轮夹紧** —— 否决：需要额外行程与径向空间，收益不如常闭弹簧；⑤**只靠弹簧、去掉螺柱限位** —— 否决：弹簧若失效滑座会无界漂移，保留螺柱 + 长槽把行程限在 4.5 mm 余量内；⑥**把摩擦面贴低摩擦带**（沿用 R47 的内衬经验）—— 未采用：这里是**要摩擦**（锁位），贴带方向相反。
- Evidence （MEASURED / CALCULATED）: 夹紧件共 **32 件**（16 螺柱栈 + 16 弹簧），每滑座 8 颗；`clamp_calc`（CALCULATED）：预载 3 N/颗、k = 1.24 N/mm、每颗 2 个摩擦面 ⇒ 单滑座摩擦 **14.4 N（μ=0.30）/ 28.8 N（μ=0.60）**、全机 28.8 / 57.6 N，均远低于舵机推力预算 ~112 N ⇒ `servo_can_still_slide_it = true`。几何（MEASURED，`cad/output/_r53b_auto/report_r53_{pollen,nectar}.json`）：`lock_travel` 长槽 63.5..107.5 覆盖两档螺柱位 68/79/92/103，两侧余量各 4.5 mm、`covered = true`；`ear_to_plate_min_gap_mm` 四处全 **0.3**（设计走合）；`lock_vs_rest_clashes = []`、`lock_vs_carriage_clashes = []`（螺柱 Ø4 穿 Ø4.4 间隙孔，本就应为 0）；`axle_isolation_hits = []`（两根飞轮轴仍各自独立）；`plate_vs_rest_clashes` 5 处与 R52 同源（`gap_servo_standoff` x 侧板 28.274 mm³ x4 + `paddle_bearing_-1` x 侧板 10.285 mm³），是既有正常配合。两档均为 **114 件**，STEP 446.3 / 446.4 MB。全程 618.7 s + 665.0 s。
- Risks / 教训（重要）: **R53 / R53b 的第一版把"夹紧件 vs 其它"报成 8 处干涉，根因是锁紧长槽只切了 +n 一侧**，下滑座（n = −half_spacing，同侧板实体区）的 8 颗螺柱以 **50.265 mm³/处**（= π x 2² x 4.0，正好一整个板厚）穿板。另有一条**更早的假报警教训**：R53 的锁紧件**没有调用 `K.to_world()`**，是拿局部坐标去比世界坐标 ⇒ R53 报出的所有 lock 干涉**全部无效，不得引用**；R53b 已让 `clamp_parts()` 对每个件显式 `to_world()`。凡 R53 的干涉结论一律作废，以 R53b 为准。
- Date/version: 2026-10-13 / 产物 `cad/output/_r53b_auto/report_r53_{pollen,nectar}.json`、`T06_shooter_assembly_R53b_{pollen,nectar}.step`；图 `cad/output/_r53b_auto/r53b_clamp_section.png`（桌面 `T06_R53b_夹紧剖面.png`）、`cad/output/_r53_lock/r53b_auto_lock_options.png`（桌面 `T06_R53b_自动锁紧方案.png`）

## V-0051 — 验证记录（非决策）：R53b 常闭弹簧夹两档干涉、锁紧行程与交付一致性

- 判据与结果（SIMULATED，几何布尔 + CAD 计算）: 两档各 114 件，跑 `paddle_launcher_shooter_lock_r53b.py pollen|nectar --step`。
  - 长槽覆盖：`slot_z_mm [63.5, 107.5]` ⊃ `bolt_z_needed_mm [68, 79, 92, 103]`，`covered = true`，`slack_mm [4.5, 4.5]` —— **两侧对称**后两档四颗螺柱全部落在槽内。
  - 耳板—侧板间隙：`upper_±1 / lower_±1` 全 **0.3 mm**，与设计走合一致（不夹死、不脱开）。
  - 夹紧件 vs 其余全部件：**0**（修长槽前为 8，见 DEC-0051 的 Risks）。
  - 夹紧件 vs 滑座：**0** —— 这是**期望值**：耳板孔已切成 Ø4.4 间隙孔，Ø4 螺柱穿过去没有实体相交，不是漏检。
  - 轴隔离：`axle_isolation_hits = []` ⇒ 改夹紧件没有把两根飞轮轴重新连起来（DEC-0049/V-0049 的核心判据仍成立）。
  - 侧板 vs 其余：5 处非零，**全部是 R52 就有的正常配合**（4 x 28.274 mm³ 舵机支座咬合 + 1 x 10.285 mm³ 拨杆轴承座），非本轮引入。
- 保持能力（CALCULATED，作为"断电也锁得住"的量级依据）: 现有 25-2 调隙舵机经 DEC-0037 链（曲柄 r = 12 mm）折算，回驱阈值 **97.7 N（POLLEN）/ 111.1 N（NECTAR）**；链内屈曲上限 **Ø6.4 x 110 主连杆 134 N**（PET-PG E ≈ 2 GPa，ASSUMED）是真正瓶颈；弹簧夹另加 28.8..57.6 N 摩擦 ⇒ 顺序安全。**注意**：这一项是量级核算，`E` 与 `μ` 都还是 ASSUMED，实物未测。
- 未验证项（TBD）: 弹簧刚度 / 预载按线性弹簧估算而未实测（采购件未定型号）；PET 打印件 μ 取 0.30 是 ASSUMED；"来回换档 50 次后预载是否衰减"未验；打印件质量、整机强度、实机均未验。

## V-0052 — 验证记录（非决策）：R53c 调隙链**全行程**复核（弹簧夹是否妨碍自动换档）

- 目的 （KNOWN）: 上一轮（V-0051）只算了**两个端点**就下了"弹簧夹不妨碍换档"的结论。本轮把 DEC-0037 调隙链在**整个行程**上扫一遍，回答用户判据「比赛中人不能介入，结构要用已有舵机自动调节」里最硬的一问：**加了常闭弹簧夹之后，现有 25-2 调隙舵机在行程中任何一点都推得动吗？最不利点在哪、余量多少？**
- 方法 （CALCULATED，虚功）: `cad/paddle_launcher_gap_chain_fullstroke_r53c.py`。链几何取 DEC-0037 口径：`h = sqrt(110^2 - (18-u)^2)`、`d = u + 120`、`d(theta) = r cos theta + sqrt(L^2 - r^2 sin^2 theta)`，`r = 12`（曲柄）、`L = 65`（拉杆）、`L2 = 110`（两根主连杆）。半间距 `h` 从 80.0 扫到 91.2（步长 0.05，**225 点**），`theta(h)` 用二分反解（不依赖闭式，避免公式风险）。**只用一个原则**：虚功 `T dtheta = sum(F_friction dh)` ⇒ `T_req = 2 f |dh/dtheta|`，`dh/dtheta = (18-u)/h * du/dtheta`，`f` = 单滑座摩擦 = 2 摩擦面 x 8 螺柱 x 3 N 预载 x mu（与 V-0051 同源）。再由 `F_u = T_req/|du/dtheta|` 反折十字头力，`F_main = F_u/(2 cos phi)`（`phi = asin(h/110)`）、`F_drag = F_u/cos beta`，与屈曲上限（主连杆 134 N / 拉杆 297 N，ASSUMED）比对。
- 结果 （CALCULATED）: **PASS**。全行程最不利点在 **POLLEN 端 h = 80.05**（曲柄 96.42 deg，`|dh/dtheta| = -11.00 mm/rad`）：
  - 需要舵机力矩 **0.317 N.m（mu = 0.30）/ 0.634 N.m（mu = 0.60）** = 25-2 堵转 2.471 N.m 的 **12.8 % / 25.6 %** ⇒ 余量 **7.8x / 3.9x**。
  - NECTAR 端 h = 91.0 只需要 **0.091 / 0.182 N.m** ⇒ 余量 **27x / 14x**（越靠近死点，力放大越大、需要力矩越小）。
  - 杆件力全程最大（mu = 0.60，POLLEN 端）：主连杆 **39.6 N** = 屈曲上限 134 N 的 **29.6 %**；拉杆 **55.3 N** = 297 N 的 **18.6 %**；十字头 **54.4 N** ⇒ **屈曲不是瓶颈**。
  - 曲柄跨度 **81.38 deg**（96.68 -> 15.30 deg）；按厂商堵转-空载线折算，最不利工况转速约 **44.6 rpm** ⇒ **换一次档约 0.30 s**。
  - **行程边界**：曲柄-拉杆共线死点在 **h = 91.537**（曲柄 0 deg）；最大档位 91.2 距死点 **0.337 mm / 15.2 deg 曲柄角**，最大档没有骑在死点上，但**没有机械硬限位**（滑窗 59 x 56 远宽于 11.2 mm 行程），所以**必须在舵机端设定行程端点**（约 19.3 deg .. 96.7 deg 曲柄角），编程器与固件都要限制，不得命令越界。
- 口径修正（重要，引用时用新口径）: ①`config/parameters.yaml` 里 `d(crosshead_u)/d(theta) = -u r sin(theta)/(u - r cos(theta))` 若按 DEC-0037 的 u = 18 - sqrt(110^2-h^2) 代入，与精确几何不符（**POLLEN 端高报 4.8 %：12.214 vs 11.658；NECTAR 端低报 32 %：3.156 vs 4.667 mm/rad**）—— 该式实际隐含 u 从**曲柄中心**起算（u' = u + 120 = d）；R53c 起统一以 `d(theta) = r cos theta + sqrt(L^2 - r^2 sin^2 theta)` + 二分反解为准。②V-0051 引用的"舵机推力预算 ~112 N"是**降额口径**（约堵转折算值的 53 %），**不应再作为预算引用**；洁净口径：十字头堵转推力 = `T_stall/|du/dtheta|` = **212 N**，实际需要 **27.2 N（mu = 0.30）/ 54.4 N（mu = 0.60）**。两条修正都不改变结论方向。
- 状态: `pass`（自动换档能力）；`not_run`（实机；弹簧刚度 / PET mu 未实测）。
- 未验证项（TBD）: 弹簧实测 k 与预载（采购件未定型号）；PET 打印件 mu = 0.30 仍是 ASSUMED（PET-PET 干摩擦，与光面塑料球无关）；静摩擦与动摩擦之差造成的**换档到位偏差**未测（有 3.9x 余量，预计 < 0.3 mm，可接受）；打印件质量、整机强度、实机均未验。
- Date/version: 2026-10-13 / 产物 `cad/output/_r53c_stroke/report_r53c_fullstroke.json`、图 `T06_R53c_fullstroke_check.png`（桌面同名）

## V-0053 — 验证记录（非决策）：R53d 调隙链**动力学**复核 —— 50 次来回自动换档

- 目的 （KNOWN）: V-0052 是**静力**（行程中每一点都推得动）。用户判据「比赛中人不能介入，要利用已有舵机自动调节」还差一条更硬的：**反复换**会不会在死点附近停滞、到位偏差多大、会不会逐次漂移。本轮把 25-2 的力矩-转速线、弹簧夹摩擦、杆件弹性一起积分，来回换 50 次。脚本 `cad/paddle_launcher_gap_chain_dynamic_r53d.py`。
- 方法 （CALCULATED）: ①链几何与 R53c 同源（精确式 `d(theta) = r cos theta + sqrt(L^2 - r^2 sin^2 theta)` + 二分反解）；②伺服 `T(w) = T_stall (1 - |w| / w_noload)`，`T_stall = 2.471 N.m`、空载 60 rpm；③摩擦折到曲柄 `T_load = 2 f |dh/dtheta|`，`f` = 单滑座摩擦 = 2 摩擦面 x 8 螺柱 x 预载 x mu；④积分 `J d2theta/dt2 = T_motor - sgn * T_load`，`J = 1.0e-4 kg.m2`、`Kp = 200 N.m/rad`（均 ASSUMED；真实位置舵机有积分作用 ⇒ 贴住指令角，负载表现为**弹性绕紧**而不是静态位置差）；⑤到位误差 = 弹性绕紧 `F_s ratio / k_chain` + 静动摩擦差 `F_s (1-ratio) / k_chain` + 舵机回差，`k_chain` 由 PET `E = 2 GPa` 与杆截面（主连杆 Ø6.4x110 两根并联，与拉杆 Ø6.0x65 串联）算得；⑥50 次来回，`mu ~ U(0.30, 0.60)`、动/静比 `~ U(0.70, 0.90)`、预载 ±15 %、起始相位 ±0.3 deg。
- 结果 （CALCULATED）: **PASS**。
  - 换档耗时 **0.325 .. 0.358 s（均 0.338 s）**，两方向对称，**0 次堵转 / 0 次超时**（50/50 都到位）。
  - 最不利点力矩 **0.634 N.m**（mu = 0.60、POLLEN 端）= 堵转的 **27.2 %**，余量 **3.7x**。
  - 到位误差 **0.051 .. 0.133 mm（均 0.092 mm）**，远小于用户口径的 1 mm；链条等效刚度 pollen **332.9 N/mm** / nectar **258.9 N/mm**。
  - 首末次误差之差 **-0.0089 mm** ⇒ **不累积漂移**：误差是有界的（弹性绕紧 + 静动摩擦差 + 回差），每档位置都由舵机角重新确立，链里没有积分机构。
  - 判定口径：常闭弹簧夹锁着的滑座，用**已有** `2000-0025-0002` 就能全自动换档；不需要人工、不需要新舵机、不需要空闲通道。
- 状态: `pass`（动力学自动换档）；`not_run`（实机；弹簧 k、PET mu、J、Kp 未实测）。
- 未验证项（TBD）: ①`mu` / `E` / `J` / `Kp` 均为 ASSUMED；②25-2 的 2.471 N.m 与空载 60 rpm 是厂商值，未实测；③**端点没有机械硬限位** ⇒ 必须在舵机编程器 + 固件把行程卡在约 `19.3 .. 96.7 deg` 曲柄角（V-0052）；④实机未验。
- Date/version: 2026-10-13 / 产物 `cad/output/_r53d_dyn/report_r53d_dynamic.json`、图 `T06_R53d_dynamic_check.png`（桌面同名）

## V-0054 - 验证记录（非决策）：R53e 比赛中**在线**换档工况复核 —— 时序 / 保持 / 端点

- 目的（KNOWN）: 用户 2026-10-13 裁定「换档需要（比赛中在线进行）」，并重申「在比赛中人不能介入去动结构，希望该结构可以利用已有舵机自动调节」。V-0052 / V-0053 只证明「换得动、换得准」，本轮补上「在线换档本身能不能排进比赛节奏、换完还能不能守住夹口」。脚本 `cad/paddle_launcher_gap_chain_match_r53e.py`。
- 方法（CALCULATED + ASSUMED）: ①链几何与积分器同 R53c / R53d（精确式 `d(theta) = r cos theta + sqrt(L^2 - r^2 sin^2 theta)` + 二分反解，`T(w) = T_stall (1 - |w| / w_noload)`）；②发射反力按球动量估：`F_tan = m v_exit / t_contact`（`v_exit = 5.56 m/s` 取自 P3 弹道基线；`m = 0.060 / 0.130 kg`、`t_contact = 20 ms` 均 ASSUMED），把两轮顶开的分量取 `F_sep = 1.8 F_tan / (2 mu_ball)`，`mu_ball = 0.40`（ASSUMED）；③保持能力：舵机堵转折算 `F_hold = T_stall / (2 |dh/dtheta|)`，夹紧件摩擦 `F_clamp = 2 面 x 8 螺柱 x 3 N x 0.30 = 14.4 N/滑座`；④冲击响应用单自由度（`k_chain = 332.9 N/mm`、`m_eff = 1.0 kg`、库仑摩擦 = 夹紧件摩擦）。
- 结果（CALCULATED）: **PASS（比赛在线可用）**。
  - 换档：单次 **0.354 s**（最不利 mu = 0.60），曲柄跨度 **77.35 deg**（96.682 -> 19.331 deg），舵机做功 <= 0.64 J；排一次换档 **0.45 s**（换档 0.354 + 稳定 0.05 + 余量），12 次/场 => 占空比 **3.6 %**。
  - 保持：发射反力峰值 **37.5 N（POLLEN）/ 81.3 N（NECTAR）每滑座**；舵机堵转保持 **112 N（POLLEN）/ 390 N（NECTAR）** => **守得住**。夹紧件只有 14.4 N => **发射时守住夹口的是舵机，不是夹紧件**（夹紧件负责断电保持与抗蠕变）。
  - 冲击响应：夹口单边偏移峰值 **0.41 mm**，发射后**回弹到 0.00 mm**（弹性，不跑位；残余量级 = `F_clamp / k` = 0.04 mm）。
  - 端点：nectar 档 `h = 91.0` 距行程死点 `h = 91.537` 只有 **0.537 mm**；死点是机构自带软止挡（再往外不可能），固件只需把命令锁在 **19.33 .. 96.68 deg**。
  - 结论：**比赛全程没有任何需要人碰的零件** —— 尼龙锁紧螺母只在装配时做一次反作用座，之后换档与保持都由**已有**的 `2000-0025-0002` 完成，不需要新舵机 / 新通道。
- 状态: `pass`（在线换档工况）；`not_run`（实机）。
- 未验证项（TBD）: ①发射反力是**估算**（球质量 0.060 / 0.130 kg 与出射速度 5.56 m/s 是 ASSUMED + 弹道基线，非实测），实机应实测一次出膛速度反推；②夹紧件预载仍靠装配时拧螺母一次设定，若要「零人工设定」可把螺母换成定长套筒 —— **已由 R53f 定长限位环完成**（DEC-0052 / V-0055）。
- Date/version: 2026-10-13 / 产物 `cad/output/_r53e_match/report_r53e_match.json`、图 `T06_R53e_match_cycle.png`（桌面同名）

## V-0055 - 验证记录（含决策 DEC-0052）：R53f 定长限位环 —— 把锁紧件预载从「靠手感」变成「靠几何」

- 目的（KNOWN）: 用户 2026-10-13 判据「保留调隙舵机 + 加锁紧件，锁紧件不得影响正常位置改变」，并确认「换档需要比赛中在线进行」。V-0054 已证在线换档可行；本轮消掉最后一条真实失效路径：R53b 的预载由装配时拧尼龙锁紧螺母的手感决定。脚本 `cad/paddle_launcher_shooter_lock_r53f.py`。
- 触发证据（CALCULATED，V-0056）: 预载扫描显示 mu = 0.60 时预载涨到 **12.0 N** 就把 25-2 顶停（换档耗时 0.35 s -> 2.7 s -> 失效），吃掉 60 % 堵转余量的门槛只有 **7.0 N**，而名义预载 2.98 N —— 手拧有 **4 倍以上**过拧空间。
- 决策（DEC-0052，KNOWN）: 每根 M4 螺柱上加一个**刚性定长限位环**，套在弹簧外面：`Ø8.0 / Ø5.7 x 6.0`（等于 6 mm 的 Ø8xØ6 尼龙/PU 管切段）。平垫被螺母压到限位环端面即到底（= 弹簧压到 6.0 mm => 预载 2.98 N），再拧只压环，**预载不再增长**。
- 方案否决记录（CALCULATED，务必保留）: 第一版设计是「套在螺柱上的细套筒 Ø4.5/Ø4.3 x 6.0」，**已在 R53f 内否决** —— M4 螺柱 Ø4.0 与弹簧内径 Ø4.5 之间只有 0.25 mm 径向间隙，套筒壁厚上限 0.25 mm、截面 **1.38 mm2**，PET 压缩屈服约 50 MPa => 只能扶约 **69 N**，手拧（M4 常见拧紧力矩 1 N·m 量级 => 数百 N）会压溃。改成套在弹簧外面的环：截面 **24.8 mm2（约 1.24 kN）**，同样的 6.0 mm 定长，径向占到 R4.0，平垫 R5.0 仍完整压住环端面。
- 几何证据（MEASURED）: 限位环 **16 件/档**（每螺柱 1 件），体积 **148.49 mm3**（解析值 148.49），轴向 75.3..81.3（与弹簧同一区间），Ø8.0 x 6.0；`lock_vs_rest = []`、`lock_vs_carriage = []`、`axle_isolation_hits = []`、耳板间隙 0.3 mm、长槽覆盖 68/79/92/103 余量 4.5 mm；两档各 **130 件**（R53b 114 + 16 环），STEP 446.5 / 446.6 MB。
- 交付一致性（MEASURED）: 回读本轮导出的 STEP（`cad/_r53f_readback.py` -> `cad/output/_r53f_lock/readback_r53f.json`）：两档各 **370 solids**（与生成器逐件累加 370 相同）、体积偏差 **-0.0001 %**、包围盒 6 面偏差 **0.00 mm**、夹口 64.0 / 86.0、限位环 16 件**件件 148.49 mm3**（轴向 +-75.3 .. +-81.3）、预载 2.976 N => 导出件与生成器一致。
- 打印公差（CALCULATED）: 限位环长度 ±0.2 mm 直接换算成预载 **±0.25 N**（名义 2.98 N，约 ±8 %）；相比「靠手感」的 4 倍以上不确定性，这是把预载钉死在几何上。
- 结论（KNOWN）: 换档（含比赛中在线换档）仍由**已有**的 `2000-0025-0002` 完成；限位环**不可能**影响正常位置改变（预载上限被几何锁死），失效方向只剩螺母松脱（掉预载、掉夹紧，不伤换档）=> 尼龙锁紧螺母 + 螺纹胶 243。
- 状态: `pass`（几何）；`not_run`（台架 50 次来回后复测预载衰减）。
- 未验证项（TBD）: ①限位环实际打印长度与材料压缩强度未实测；②弹簧 k = 1.24 N/mm 与 PET mu 仍未实测；③实机未验。
- 报告自洽修正（本轮补）: R53f 首版报告里 `clamp_calc.preload_n_per_stud` 还是 R53b 的 **3.0 N**，与 `seat.preload_n_per_stud_geometric = 2.976` 自相矛盾。生成器已改为写报告前用几何值覆写：`preload_n_per_stud = 2.976`、`preload_source = "geometric: SPRING_RATE x (SPRING_FREE - ring length)"`，并补 mu = 0.30 / 0.60 的摩擦与「舵机仍能推动」判定（全链 28.6 / 57.1 N < 0.6 x 112 N = 67.2 N 预算）。重跑后 STEP 与上一版**逐字节相同**（60 余分钟内只改了报告字段）。
- 教训（溯源陷阱，务必记住）: `cad/output/_r53f_lock/report_r53b_*.json` **不是** R53b 基线，而是 R53b 模块在 R53f 运行时写入的**同名副产物**（里面已有 16 件环，`n_parts = 130`）；真基线在 `cad/output/_r53b_auto/report_r53b_*.json`（`n_parts = 114`）。副产物已改名为 `report_r53f_deps_r53b_module_*.json`，生成器里加了自动改名；凡引用报告必须核对 `caliber` / `n_parts`，不能只看文件名。
- 逐件对比（MEASURED）: `cad/_r53f_compare_base.py` -> `cad/output/_r53f_lock/compare_r53f_vs_r53b.json`（真 R53b vs R53f）：两档均 **+16 件（全为 `carriage_clamp_seat_*`）、-0 件、位移 0 件（共有件 volume 与 bbox 逐件相等）、包围盒偏差 0.00 mm** => R53b 的其余每一个零件几何与位置完全未变。
- 输入口径说明（本轮补，防误读）: V-0052 / V-0053 / V-0054 的积分用的是 **3.0 N/颗** 预载（R53f 之前的「靠手感」名义值），比 R53f 几何锁定值 **2.976 N** 高 **0.8 %** => 属**保守**口径（摩擦被高估），三份结论（余量 3.9x / 50 次 0 堵转 / 在线换档可行）**不需要**改动。V-0056 的预载扫描（1.0..20.0 N）已把 2.976 N 夹在 **2.5 N（10.7 % / 21.4 % 堵转、0.321 / 0.343 s）**与 **3.0 N（12.8 % / 25.6 %、0.325 / 0.354 s）**两行之间，两行均 `ok = true` => 「锁紧件不影响正常位置改变」的结论不依赖 3.0 这个具体数字。
- 夹紧态口径说明（本轮补，CALCULATED，防误读）: `EAR_GAP = 0.30` 是**零件化建模的 running clearance**（报告里的 `ear_to_plate_min_gap_mm = 0.3` 就是它），**不是装配后的间隙**。装配后弹簧预载把两侧耳片压到板面上：**0.60 mm 归零**，`clamp_calc` 的 `faces = 2.0`（每颗螺柱压两个耳/板摩擦面）**只在归零后才成立** —— 未夹紧态摩擦副为 0，`faces = 2.0` 不是建模态读数。复算（`cad/_r53_clamp_caliber.py` -> `cad/output/_r53f_lock/caliber_clamp_interface.json`）：建模态链长（head 接触面 -> 平垫内侧面）= 3.0 + 0.30 + 4.0 + 0.30 + 3.0 + 6.0 = **16.6 mm**；①螺母拧到限位环端面贴合（链长缩到 16.0）= 弹簧 6.0 => **2.976 N/颗**（名义，耳-板 0.30 归零）；②螺母只在未夹紧态按 6.0 mm 设定（链长仍 16.6）= 弹簧 6.6 => **2.232 N/颗**（此时端面尚未贴上环，仅为**下界**）。两个值都远低于 V-0056 的门槛（吃掉 60 % 余量 **7.0 N**、真正顶停 **12.0 N**）=> V-0052 / V-0053 / V-0054 / V-0055 的结论**不需要**改动。**装配指令**：螺母拧到限位环端面贴合（= 2.976 N），此时建模态 0.30 mm 间隙归零、夹紧摩擦才成立。
- Date/version: 2026-10-13 / 产物 `cad/output/_r53f_lock/report_r53f_{pollen,nectar}.json`、桌面 STEP `T06_shooter_assembly_R53f_{pollen,nectar}.step`、图 `cad/output/_r53f_lock/T06_R53f_限位环剖面.png`（桌面同名；**采用方案 vs 已否决方案的并排剖面**，脚本 `cad/_r53f_section.py`）

## V-0056 - 验证记录（非决策）：R53g 锁紧件预载上限 —— 拧过头多少才顶停 25-2

- 目的（KNOWN）: 量化「加锁紧件但不得影响正常位置改变」这条判据的边界。脚本 `cad/paddle_launcher_gap_chain_preload_limit_r53g.py`。
- 方法（CALCULATED + ASSUMED）: 与 R53d / R53e 同源积分（`T_load = 2 f |dh/dtheta|`，`f` = 2 面 x 8 螺柱 x 预载 x mu；`T(w) = T_stall (1 - |w|/w_noload)`；`J = 1.0e-4 kg.m2`、`Kp = 200 N.m/rad`），预载 1.0 -> 20.0 N step 0.5 x mu = 0.30 / 0.60；到位判据 = 停稳 0.05 s 且残余角误差 < 5.0e-3 rad。
- 结果（CALCULATED）:
  - 名义 **2.98 N**：最不利占堵转 **25.6 %**（mu = 0.60）/ 12.8 %（mu = 0.30），换档 0.354 / 0.325 s。
  - 吃掉 **60 %** 堵转余量的门槛：**7.0 N**（mu = 0.60）/ 14.0 N（mu = 0.30）。
  - 真正顶停：**12.0 N**（mu = 0.60，耗时 0.35 -> 2.7 s 后失效）；mu = 0.30 在 20 N 内都不顶停。
  - 结论：预载从名义到顶停有 **4 倍以上**空间，落在危险区完全可能 => 支持 DEC-0052 的定长限位环。
- 判定口径修正（KNOWN，务必保留）: 第一版把「到位后靠静差停住（w = 0）」误判成卡死，导致「硬上限 1.0 / 1.5 N」的假结果；正确判据必须同时看**停稳**与**残余角误差**（到位时残余 = 静差 ≈ T_load / Kp ≈ 8e-4 rad）。修正后与曲线形状（mu = 0.60 在 11.5 N 处发散）自洽。
- 状态: `pass`（数值实验口径）；`not_run`（实机）。
- 未验证项（TBD）: ①mu、J、Kp、T_stall、空载转速均未实测；②限位环压溃载荷与打印公差未实测（69 N / 1.24 kN 为材料估算）。
- Date/version: 2026-10-13 / 产物 `cad/output/_r53g_limit/report_r53g_preload_limit.json`、图 `T06_R53g_preload_limit.png`（桌面同名）
## V-0057 - 验证记录（非决策）：R53h 锁紧件对换档的几何免疫 —— 不依赖预载数字的证明

- 目的（KNOWN）: 把 V-0055 / V-0056 的「预载阈值」换成**不依赖预载数字**的几何证明，并澄清「弹簧常压 => 断电也锁」的真实口径。判据仍是用户 2026-10-13 的「加锁紧件但不得影响正常位置改变」。脚本 `cad/_r53_lock_immunity.py` -> `cad/output/_r53f_lock/immunity_r53_lock.json`。
- 方法（CALCULATED）: 预载反解成限位环长度 `preload(L) = k x (free - L)`，k = 1.24 N/mm、free = 8.4 mm，L = 环长 = 装配后弹簧长度（环是刚性件，长度即弹簧压缩后的长度）；把 V-0056 的门槛代回求 L。
- 结果（CALCULATED）:
  - 吃掉 60 % 堵转余量的门槛 -> 环长：mu = 0.60（**支配工况**）**2.74 mm**；mu = 0.30 **-2.92 mm**（负值）。
  - 硬顶停（12.0 N，mu = 0.60）-> 环长 **-1.28 mm**（负值，几何不可能）。
  - **安全窗口 = [2.74, 8.4] mm**；名义环长 6.0 mm => 距下界余量 **3.26 mm**。
  - 结论: **只要限位环长度不超过弹簧自由长 8.4 mm，锁紧件在几何上不可能顶停 25-2**；若环长 >= 8.4 mm 或螺母根本没拧到环端面 => 预载 <= 0 => 摩擦更小、换档更轻松。**失效方向只有「锁不住」，没有「顶停」。**
  - 打印公差 ±0.2 mm => 预载 ±0.25 N（与 V-0055 一致，约 ±8 %）。
- 力矩口径（CALCULATED，装配指令依据）: 螺母拧到环端面贴合后，轴向力由**刚性环**承担，弹簧压缩量被环长钉死 => **预载只由环长决定，力矩不再改变预载** —— 这就是几何免疫的工程实现。环端面应力：名义预载 2.976 N -> **0.120 MPa**；10 倍也只有 1.20 MPa，远低于 PET 保守屈服 50 MPa（环截面 24.75 mm2 => 压溃载荷 **1.24 kN**）。只有「环做得比弹簧自由长还长、再继续强拧」才会压溃环（3.0 N.m 量级 => 约 3.75 kN => 151 MPa）。**装配口径：力矩上限 1.0 N.m + 尼龙锁紧螺母 + 螺纹胶 243**；预载不作为手感或力矩的函数。
- 保持力口径（CALCULATED，必须保留，防误读）: 夹紧件单独保持力 = mu x 2 摩擦面 x 8 螺柱 x 预载 => mu = 0.30 名义 **14.3 N/滑座**（下界预载 2.232 N -> 10.7 N）、mu = 0.60 名义 28.6 N（下界 21.4 N）。发射反力峰值 **37.5 N（pollen）/ 81.3 N（nectar）每滑座**：最有利组合（mu = 0.30、名义预载）也只有峰值的 **1/2.63、1/5.69**，最差组合 1/1.31、1/2.85。=> **断电 / 无指令时夹紧件挡不住发射反力**；发射过程中守住夹口的是**通电的 25-2**（保持力 112.3 / 389.9 N/滑座 => 峰值余量 **3.0x / 4.8x**）。R53b 与早前笔记里的「弹簧常压 => 断电也锁」必须读作「**挡得住 14.3 N/滑座以内的漂移**」，不是「断电后仍能承受发射冲击」。
- 判定（KNOWN）: 用户判据「锁紧件不能影响正常位置改变」在**不依赖任何预载数字**的前提下成立；锁紧件的全部失效方向落在「夹不紧」（换档更省力），不会污染换档。
- 状态: `pass`（解析 / 数值）；`not_run`（台架 50 次来回后复测预载衰减、实机）。
- 未验证项（TBD）: ①限位环 PET 压缩强度与打印长度实测；②弹簧 k = 1.24 N/mm 实测；③打印件 mu 实测；④台架与实机。
- Date/version: 2026-10-13 / 产物 `cad/_r53_lock_immunity.py` -> `cad/output/_r53f_lock/immunity_r53_lock.json`
## V-0058 - 验证记录（非决策）：R53h-2 弹簧采购包络 —— 让「锁紧件不顶停换档舵机」不依赖未实测的 k

- 目的（KNOWN）: V-0057 的几何免疫用的是**未实测**的弹簧刚度 k = 1.24 N/mm。CAD 里环长固定 6.0 mm，预载 = k x (L0 - 6.0) 完全由买到的弹簧决定 => 若买到偏硬的弹簧，锁紧件**可能**反过来吃掉 60 % 堵转余量。本记录把这个软点钉成**采购包络**。脚本 `cad/_r53_spring_envelope.py` -> `cad/output/_r53f_lock/spring_envelope_r53h.json`。
- 规则（CALCULATED）: 预载 = k x (L0 - 6.0)（环长 6.0 mm 为 CAD 固定值）。只要 **k x (L0 - 6.0) <= 7.02 N**（V-0056 的 60 % 余量门槛，mu = 0.60）锁紧件就不可能出现「顶停换档」；同时要求 >= **1.5 N** 才算真的夹得住。
- 采购规格（KNOWN）: `k x (L0 - 6.0) in [1.5, 7.0] N`；**外径 <= 5.6 mm**（要能塞进环内径 5.7）、**内径 >= 4.1 mm**（要能套在 M4 螺柱 Ø4.0 外）、安装长 6.0 mm。在 L0 = 8.4 mm 时刚度上限 **2.925 N/mm**（设计值 1.24 N/mm => 余量 2.4 倍）。
- 包络（CALCULATED）: L0 = 7.0 mm -> k <= 7.02；8.0 -> 3.51；8.4 -> 2.93；9.0 -> 2.34；10.0 -> 1.76；12.0 -> 1.17 N/mm。若要 2.976 N 名义预载，L0 = 7.0 -> k = 2.976；8.4 -> 1.24；10.0 -> 0.744 N/mm。
- 偏离后的处置（KNOWN，替代口径）: 若实测 (k, L0) 落在窗口外，**改打印的环长**而不是改装配力矩：`L = L0 - 2.976/k`（下限 `L0 - 7.02/k`）。力矩仍然是「拧到环端面贴合即停」（V-0057）。
- 判定: 设计弹簧 k = 1.24 / L0 = 8.4 => 2.976 N，落在窗口内 `pass`；「锁紧件不影响正常位置改变」现在只依赖**可采购可实测**的两个数 (k, L0)，不依赖手感、不依赖力矩。
- 未验证项（TBD）: ①购得弹簧的 k 与 L0 实测；②限位环打印长度与 PET 压缩强度；③台架 50 次来回后预载衰减；④实机。
- Date/version: 2026-10-13 / 产物 `cad/_r53_spring_envelope.py` -> `cad/output/_r53f_lock/spring_envelope_r53h.json`


## DEC-0053 - 决策：T06 R54 打印主体合并为一个件 + M3 贯穿螺栓装配（无自攻）

- 判据（KNOWN）: 用户 2026-10-14 指令 —— 下一版考虑**实际装配合理性**、**极少零件数**（托板与外罩合二为一、侧板与外罩连起来）、3D 打印便利、用 M3 螺丝装配并在本版里把厂商件剔除；追加口径：闸门暂不建模但**预留孔洞**；**这只是原型，耐用因素不考虑**；**自攻不用，两个构件都贯穿，一头螺栓一头螺母**。
- 决策（KNOWN）:
  1. 12 个自制件 + 16 根连接筋 + 2 块补缝块 + 4 条导轨腿 **熔合为 1 个打印件** `shooter_frame_R54_merged`：`feeder_shell_tray`、`shooter_side_plate_±1`、`feeder_mount_±1`、`guide_roof_3`、`guide_wall_3_±1`、`shooter_throat_+55`、`paddle_shaft_support_bridge`、`servo_bridge_±26`。
  2. 所有连接一律 **O3.4 通孔（M3 间隙孔，r = 1.70）+ 螺栓 / 螺母**；不设自攻孔、不设热熔铜螺母、不设螺母袋。
  3. 33 个厂商件与 9 个闸门件本版不入输出；闸门以**预留孔洞**代替（用户「可以先暂时不管闸门，但预留孔洞」）。
- 关键实测（MEASURED，`cad/output/_r54_frame/report_r54_pollen.json`，8 mm 步长探针）:
  - 合并后 **solids = 1**（导出 STEP 回读同为 1），V = 1 052 724 mm3，bbox x[-147.22, 215.26] y[-76.00, 99.00] z[-3.51, 401.02]。
  - `shooter_side_plate` 下缘是一条 **V 形斜边**，最低点 z = 33.6 落在 x 约 68：x = 52 -> 44、60 -> 38、68 -> 34、76 -> 42、84 -> 52、140 -> 124、190 -> 186、212 -> 228。
  - **侧板底 z = 33.6 与底座导轨顶 z = 16 之间是 17.6 mm 空气** => R53f 的打印主体与底座导轨之间**没有任何连接**。
  - 原 4 个「机架孔」（z 轴、y = ±58）**只穿过 `feeder_mount`、不穿过 `base_rail`**，材料 127 mm3 全部来自 feeder_mount => 是**无效接头**，已删除。
  - 侧板在 z = 200 / 220 处确实有料（y 轴通孔材料 72.6 mm3），在 z = 45 / 60 处 x >= 178 已无料 => 闸门预留孔改到 (x, z) = (190, 200) 与 (206, 220)。
- 连接设计（DEC，3D 打印 + M3）:
  - **导轨腿 4 条**：x = 60 / 76 各 ±1 侧，截面 12 x 12 mm，z 16 -> 44 / 48；底面与导轨顶面 z = 16 **相切**（不互穿），顶部与侧板下缘重叠 6 mm 后熔合进主体。每条腿一个 **O3.4 贯穿孔**（z 轴，y = ±70），同轴穿过「腿 + 底座导轨」，材料 199.7 mm3 => 一头螺栓一头螺母。
  - **闸门预留孔 2 条**（= 4 个孔）：y 轴 O3.4，位置 (x, z) = (190, 200) 与 (206, 220)，各穿过 ±1 两侧侧板。
  - **补缝块 2 块**（8 x 11 x 20 @ x = 54.5 / 4.5、y 71..82、z 101..121）：把侧板 (y 68..72)、轴支撑桥 (y 73..79)、舵机桥 (y 79..99) 连成一体 —— 原几何三者只相切（侧板底与桥面差 1 mm），布尔无法熔合，实测确实留下 2 个 8600 mm3 的游离实体。
- 判定: solids = 1 **pass**；6 个 M3 接头全部 pass（0 个 skipped，每孔材料 >= 20 mm3 门槛）；厂商件 / 闸门实体 100 % 剔除 **pass**。
- 未验证项（TBD）: ①螺栓长度与扳手空间（4 条腿的螺母侧在导轨下方 z < 2，需核对可达性）；②打印朝向与支撑策略；③O3.4 打印孔径公差与 PET 收缩（1 mm 级误差按用户口径可接受）；④闸门实体本版未建模，其孔位只按 R49 包络 x[166,232] z[14,258] 预留；⑤R49/R53 既有件与新主体的接口一致性未复核。
- Date/version: 2026-10-14 / 脚本 `cad/paddle_launcher_shooter_assembly_r54.py`、`cad/r54_joint_schematic.py` / 产物 `cad/output/_r54_frame/`（report + 2 个 STEP + sections/ 4 张图）


## DEC-0054 - 决策：T06 后续只交付 pollen 版（nectar 不是第二台机构）

- 判据（KNOWN）: 用户 2026-10-14 指令「你以后只给 pollen 版就行了，两版实际是同机构不同时间的不同状态」。
- 决策（KNOWN）:
  1. 后续 CAD / STEP / 仿真 / 图 **只出 pollen 口径**，不再另出 nectar 交付件。
  2. nectar 与 pollen 的关系重述为 **同一机构在换档行程两端的不同状态**（沿 DEC-0037 / DEC-0051 的调隙链：半间距 80.0 -> 91.0 mm），而不是两台独立机构；机间唯一变化量是**飞轮间隙**。
  3. 兼容性要求不变：同一套送球件必须能吃两种球径（DEC-0035 以来的口径继续有效），只是**不再单独发布 nectar 版本产物**。
  4. 历史 nectar 产物按 superseded 记录保留，不删除、不覆盖（`cad/output/_r51_*` / `_r52_*` / `_r53b_auto/` 与 `deliverables\` 中的 nectar STEP）。
- 影响: `cad/paddle_launcher_shooter_assembly_r54.py` 的 `HALF` 双档定义保留（换档计算仍需要 nectar 端点），但**默认交付变体 = pollen**；`report_r54_pollen.json` 为唯一交付报告。
- 未验证项（TBD）: 无（本决策只收敛输出范围，不改几何）。
- Date/version: 2026-10-14 / 关联 Linear KEI（R54 问题）、Notion 项目页 DEC-0053/0054 记录
