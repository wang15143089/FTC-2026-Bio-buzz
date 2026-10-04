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

```text
Decision:
Reason:
Alternatives considered:
Evidence/calculation:
Impact:
Reversible?:
Date/version:
```
