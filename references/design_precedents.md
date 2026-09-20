# 设计先例索引

状态：v0.1；初始检索 2026-09-19。先例用于提取设计原则，不构成当前赛季合法性、性能或尺寸证明。

## 使用规则

1. 获奖或高分只说明该系统在其赛季环境中有证据，不证明适合 BIOBUZZ。
2. 引用必须记录来源、可迁移原则、赛季差异和本项目验证方法。
3. 未公开尺寸不得反推为事实；第三方 CAD 先视为参考，几何需由官方资料或实测核验。
4. 真正采用到概念时，必须关联需求、接口、风险和验证 ID。

## FTC 机器人与公开工程资料

| ID | 来源 | 可迁移原则 | 限制与本项目用途 |
|---|---|---|---|
| PRE-FTC-001 | [FTC Open Alliance](https://theopenalliance.org/ftc) | 持续公开 CAD、代码、媒体和构建记录，适合追踪设计演变与失败经验。 | 是资料入口，不是性能验证；用于发现可审计案例。 |
| PRE-FTC-002 | [FTC 11128 Læk — Ultimate Goal](https://team11128.wixsite.com/main/laek) | 同侧收集与发射减少整车重新朝向；集成弹匣/发射链可缩短功能路径；参数化底盘利于迭代。 | 处理的是扁平 Ring，不是 71/91 mm 近球形物体；用于 T04/T05/T06 布局候选，尺寸不可直接复用。 |
| PRE-FTC-003 | [FTC 18438 Wolfpack Machina — 2020](https://www.wolfpackmachina.com/ftc2020) | 曲面压缩路径延长加速接触；增加飞轮惯量可减小连续发射转速跌落；控制器可达性应纳入布置。 | 远程赛季和 Ring 物体与 BIOBUZZ 不同；仅作为发射能量稳定和可维护性假设来源。 |
| PRE-FTC-004 | [REV Ultimate Goal Flywheel Launcher](https://docs.revrobotics.com/ftc-kickoff-concepts/ultimate-goal-2020-2021/shooter) | 先定义“不堵塞、出射一致”的需求；长接触路径和简单飞轮架构便于单因素原型。 | 教学概念而非夺冠证明；本项目需重新建立球体压缩、摩擦和安全边界。 |
| PRE-FTC-005 | [FTC 16010 Astra Machina Ri3D](https://roboftc.github.io/robots/astrari3d.html) | 固定角度发射、分级轮组及可调传动比适合快速探索速度窗口。 | 页面明确警告 CAD 可能有误，且不是优胜机器人；只用于形成可调试验台概念。 |
| PRE-FTC-006 | [FTC 11329 The Quadrangles 公开资源](https://www.thequadrangles.org/ftc-11329/resources) | 同时发布 CAD、代码、Portfolio 与 Reveal，可把“几何—控制—设计理由—赛场表现”交叉审查。 | 具体赛季功能不等同 BIOBUZZ；主要用于文档结构、模块维护和证据链参考。 |
| PRE-FTC-007 | [FIRST 2024 Jemison Division Awards](https://ftc-events.firstinspires.org/2024/FTCCMP1JEMI/awards) | 官方成绩页面用于核验团队/奖项叙述，避免仅凭团队宣传判断成熟度。 | 获奖不是机构适用性评分；与 PRE-FTC-006 配合使用。 |
| PRE-FTC-008 | [OpenVault FTC Portfolios](https://www.open-vault-ftc.org/portfolios/portfolios) | 多队工程 Portfolio 可用于横向比较需求、风险、试验与迭代记录。 | 内容质量不一；任何引用都必须落到具体原文和当前项目验证。 |
| PRE-FTC-009 | [FTC 724 RedNek Robotics Wun 官方队页](https://ftc-events.firstinspires.org/team/724)、[2017 冠军报道](https://www.sdftc.org/blog--news/rise-of-hephaestus-on-winning-alliance-at-the-first-first-festival-of-champions) | 2017 Velocity Vortex 冠军联盟采用的方案被社区资料描述为可调射程弹射器，说明离散储能方案可作为飞轮以外的高水平路线。 | 官方来源证明队伍/冠军身份，但“可调弹射器”细节来自社区二手描述；无尺寸、能量或寿命数据，不得直接复刻。 |
| PRE-FTC-010 | [goBILDA 5203 1620 RPM 官方规格](https://www.gobilda.com/5203-series-yellow-jacket-planetary-gear-motor-3-7-1-ratio-1620-rpm-3-3-5v-encoder/) | 1620 RPM、0.25 A 无负载电流、396 g、编码器、5.4 kg·cm 堵转扭矩和 9.2 A 堵转电流为轮速/质量/故障初筛提供供应商输入。 | 无负载/堵转端点不能代替持续工作曲线；必须做带载电流、温升和恢复测试。 |
| PRE-FTC-011 | [FIRST FTC Robot Best Practices](https://ftc-docs.firstinspires.org/en/latest/robot_building/best_practices/robot-best-practices.html) | 飞轮属于显著电力负载；整机多执行器同时工作可能造成电压下降、保险丝动作或控制系统棕断，应记录实际电流。 | 用于 C06-B 电源关口；不提供本机构的持续电流值。 |
| PRE-FTC-012 | [goBILDA 5203 312 RPM官方规格](https://www.gobilda.com/5203-series-yellow-jacket-planetary-gear-motor-19-2-1-ratio-24mm-length-8mm-rex-shaft-312-rpm-3-3-5v-encoder/) | 312 rpm、0.25 A无负载电流、9.2 A堵转电流、24.3 kg·cm堵转扭矩和437 g质量用于T01/T04端点模型。 | 端点线性模型不能代替带载效率、温升和电池压降实测。 |
| PRE-FTC-013 | [WPILib Mecanum Kinematics](https://docs.wpilib.org/en/latest/docs/software/kinematics-and-odometry/mecanum-drive-kinematics.html)、[Differential Kinematics](https://docs.wpilib.org/en/stable/docs/software/kinematics-and-odometry/differential-drive-kinematics.html) | 麦克纳姆将底盘三自由度速度映射到四轮；差速只映射前进与角速度。 | 支持T01运动学自由度边界；不提供FTC轮地效率数据。 |
| PRE-FTC-014 | [goBILDA 96 mm Hogback轮](https://www.gobilda.com/hogback-traction-wheel-96mm-diameter-50a-durometer/) | 82 g/个作为差速改装的质量敏感性参考。 | 直径与原104 mm轮不同，且传动未选；不得视为正式轮组选型。 |

## 系统工程与工业化原则

| ID | 来源 | 可迁移原则 | 本项目应用 |
|---|---|---|---|
| PRE-IND-001 | [NASA Systems Engineering Handbook](https://www.nasa.gov/wp-content/uploads/2018/09/nasa_systems_engineering_handbook_0.pdf) | 方案权衡应记录背景、准则、候选、方法、假设/不确定性/敏感性、结果和推荐。 | TS-S00-001 的结构及后续所有主要权衡记录。 |
| PRE-IND-002 | [NASA Decision Analysis](https://www.nasa.gov/reference/6-8-decision-analysis/) | 用决策树/筛选先淘汰不满足约束的方案，再把昂贵分析集中到少量候选。 | 先比较任务包，再比较机构；先低成本原型，再做重仿真。 |
| PRE-IND-003 | [OSHA Machine Guarding](https://www.osha.gov/etools/machine-guarding/introduction/general-requirements) | 进料夹点、旋转件和飞出物需要物理防护；防护不应依赖操作者保持距离。 | T06 飞轮、轴端、带/链和进料夹点采用固定/可维护护罩，并保留断电清障路径。 |

## 当前提取的设计准则

- `ASSUMED` 尽量让 T04/T05 成为 P2/P3 可共享的短物体路径，但必须用双直径球堵塞试验证明。
- `ASSUMED` T06 发射概念必须允许调整出射速度、压缩量或接触路径，避免首版刚性锁定未知参数。
- `ASSUMED` T03 的 Hub、电池、主开关和保险丝必须在不拆卸主要得分模块的情况下检查与更换；目标时间仍为 TBD。
- `KNOWN` 所有传动、飞轮和夹点需要护罩与断电安全移除路径；具体护罩尺寸到 M3/M4 决定。
- `ASSUMED` 插拔接口采用防错方向、线束应变释放和明确标签；在 ICD 冻结前不指定连接器数量与位置。
- `ASSUMED` T06 将单球闸门与发射能量级分离，使堵塞、轮速恢复和双球误进可独立验证。
- `ASSUMED` 首轮发射台架必须模块化更换单轮/双轮头部，并以实测轨迹替换真空模型和轮速传递假设。
