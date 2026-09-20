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

## 新条目模板

```text
Decision:
Reason:
Alternatives considered:
Evidence/calculation:
Impact:
Reversible?:
Date/version:
```
