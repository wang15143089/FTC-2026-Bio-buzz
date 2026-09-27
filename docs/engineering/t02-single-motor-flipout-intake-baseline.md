# 单电机翻转 Intake：COTS 约束设计基线

日期：2026-09-27

版本：`KEI16-FLIPOUT-COTS-0.2`

成熟度：M2 计算完成、M3 包络 CAD 已生成；Prototype / Testing 未开始

来源编号：Linear `KEI-16 / T02 Intake`（导入参考）

当前仓库权威模块：`T04 Intake`；本文不更改 Architecture v0.1 编号，也不自动取代 C04-B1
视频参考：[Robot in 30 Hours Reveal | FTC BIOBUZZ 2026-2027](https://youtu.be/RIt5xxJ2Yxs)

## 设计结论

本方案把外观相似度降为次要目标，把以下两项作为核心：

1. **一台直流电机驱动四根 Intake 轴**：goBILDA 312 rpm 电机经 24T:24T 斜齿轮转向；三根固定 Ø60 mm roller 由两条独立 14T/38 节链条串联；同一主动轴再以 16T:24T、460 mm HTD5 同步带驱动翻臂前端柔性指轴。
2. **碰撞载荷与驱动解耦的翻转放出**：左右双弹簧储能，双棘爪收纳锁定，REV 舵机只负责解锁，左右双硬止挡承受展开与碰撞载荷。该基线为赛前手动收起、比赛中一次性弹出，**不包含主动收回**。

`KNOWN_VENDOR` 齿轮、链条、链轮、同步带、带轮、电机、轴承/轴承座和锁扣舵机均选自 goBILDA 或 REV 的现售规格。滚筒筒体、摆臂板、指片、弹簧、锁扣与硬止挡仍是项目自制件或待选标准件。

## 视频事实与项目设计的边界

视频画面可支持的观察：竖置减速电机、90°齿轮换向、机器人一侧向多根横轴分配动力、前端柔性指片轴和连续 roller 球路。视频没有给出齿数、轴距、材料、弹簧或锁止细节。

因此，同心翻臂、链条规格、恒中心距同步带、弹簧坐标、双棘爪、打滑离合器和硬止挡都是本项目的工程实现；不得写成原机器人的隐藏结构事实。

## 传动拓扑

```text
goBILDA 5203 312 rpm 电机
  → 24T:24T MOD1 斜齿轮（90°、1:1）
  → 主动 roller / 翻臂同心轴
      ├─ 14T → 14T，38 节 8 mm 链 → roller 2
      │    └─ 14T → 14T，38 节 8 mm 链 → roller 3
      └─ 16T → 24T，460 mm HTD5 同步带 → 翻臂前指轴
```

两条固定 roller 链路相互独立。中间轴装两只链轮，分别位于不同 Y 平面；这允许单独张紧和更换，并避免一条长链跨三轴造成难以控制的包角与累积误差。

## COTS 选型与尺寸

| 功能 | 厂商与 SKU | 数量 | 状态与用途 |
|---|---|---:|---|
| 主电机 | goBILDA `5203-2402-0019` | 1 | `KNOWN_VENDOR` 19.2:1、312 rpm、8 mm REX、12 V |
| 90°换向 | goBILDA `2320-4008-0024` | 2 | `KNOWN_VENDOR` 24T、MOD1、8 mm REX；1:1 配对 |
| 固定轴链轮 | goBILDA `3302-4008-0014` | 4 | `KNOWN_VENDOR` 14T、8 mm pitch、8 mm REX；中间轴两只 |
| 固定轴链条 | goBILDA `3315-0008-0038` | 2 | `KNOWN_VENDOR` 钢链、38 节、304 mm 节距长度 |
| 链条惰轮 | goBILDA `3312-0006-0008` | 2 | `KNOWN_VENDOR` 每段一个，用于公差与磨损补偿 |
| 张紧支架 | goBILDA `1524-0001-0001` | 2 | `KNOWN_VENDOR` arc-slot tensioner |
| 翻臂主动带轮 | goBILDA `3417-4008-0016` | 1 | `KNOWN_VENDOR` 16T、HTD5、8 mm REX |
| 翻臂从动带轮 | goBILDA `3417-4008-0024` | 1 | `KNOWN_VENDOR` 24T、HTD5、8 mm REX |
| 翻臂同步带 | goBILDA `3412-0009-0460` | 1 | `KNOWN_VENDOR` 460 mm、92T、9 mm 宽 HTD5 |
| 轴承 | goBILDA `1611-0514-4008` | 按装配 | `KNOWN_VENDOR` 8 mm REX 法兰轴承 |
| 双轴承座 | goBILDA `1614-0016-4008` | 按装配 | `KNOWN_VENDOR` 优先用于主动轴和悬臂载荷处 |
| 锁扣舵机 | REV `REV-41-3334` | 1 | `KNOWN_VENDOR` Smart Robot Servo V2 Balanced；只解锁，不承载 |

供应商网页只证明目录规格和可选生态，不证明当前 CAD 的装配公差。采购前必须重新核对库存、图纸、轴向堆叠和 FTC 当季合法性。

官方资料入口：[5203 312 rpm 电机](https://www.gobilda.com/5203-series-yellow-jacket-planetary-gear-motor-19-2-1-ratio-24mm-length-8mm-rex-shaft-312-rpm-3-3-5v-encoder/)；[24T MOD1 斜齿轮](https://www.gobilda.com/clamping-steel-miter-gear-8mm-rex-bore-24-tooth-mod-1/)；[16T HTD5 带轮](https://www.gobilda.com/3417-series-5mm-htd-pitch-set-screw-pinion-timing-belt-pulley-8mm-rex-bore-16-tooth/)；[24T HTD5 带轮](https://www.gobilda.com/3417-series-5mm-htd-pitch-set-screw-pinion-timing-belt-pulley-8mm-rex-bore-24-tooth/)；[460 mm HTD5 同步带](https://www.gobilda.com/3412-series-5mm-htd-pitch-timing-belt-9mm-width-460mm-pitch-length-92-tooth/)；[8 mm pitch 链条/链轮目录](https://www.gobilda.com/sprockets-chain)；[8 mm REX 双轴承座](https://www.gobilda.com/dual-bearing-pillow-block-8mm-rex-bore/)；[REV Smart Robot Servo V2](https://www.revrobotics.com/Smart-servo-v2)。

## 可复算结果

输入唯一记录：`calculations/kei16_flipout_drive_inputs.json`。计算脚本：`calculations/kei16_flipout_drive.py`。结果：`calculations/kei16_flipout_drive_results.json`。

| 项目 | 结果 | 标签 |
|---|---:|---|
| 24T:24T 后固定 roller 空载转速 | 312 rpm | `CALCULATED_FROM_VENDOR_SPEC` |
| Ø60 roller 空载表面速度 | 0.980 m/s | `CALCULATED_FROM_VENDOR_SPEC` |
| 每段 14T/38 节链的理论轴距 | 96.000 mm | `CALCULATED` |
| 460 mm、16T:24T 带轮理论轴距 | 179.887 mm | `CALCULATED` |
| 小带轮包角 / 啮合齿数 | 175.94° / 7.82 齿 | `CALCULATED` |
| 前指轴空载转速 | 208 rpm | `CALCULATED_FROM_VENDOR_SPEC` |
| 73 mm 指尖空载速度 | 1.590 m/s | `CALCULATED_FROM_VENDOR_SPEC` |
| 3.4 A 告警点的估算主轴扭矩 | 0.755 N·m | `CALCULATED_FROM_LINEAR_MOTOR_MODEL` |
| 该扭矩下链条有效拉力 | 42.3 N | `CALCULATED_FROM_LINEAR_MOTOR_MODEL` |

空载速度不是实物负载速度。电流—扭矩采用直线模型且只用于保护起始值；链条冲击、摩擦、滚筒压缩和电池压降未被建模。

## 轴距、轴向堆叠与支撑

- 固定 roller 中心依次为 `(25.000, 67.000)`、`(113.000, 105.367)`、`(201.000, 143.733)` mm；相邻中心距 96.000 mm。
- 翻臂 pivot 与第一主动 roller 同轴，前轴中心距 179.887 mm。翻臂转动不会改变同步带中心距。
- 主动轴从捕获区向驱动侧的建议堆叠：roller hub → 轴承 → 16T 前轴带轮 → 14T 链轮 → 24T 斜齿轮 → 0.8 N·m 级打滑元件。实际垫片厚度与轴长 `TBD`。
- 第二固定轴需要两只 14T 链轮，分处两个链平面；两链平面至少预留链片、护罩和轴环所需间隔，最终以供应商图纸和实物量规关闭。
- 斜齿轮、链轮和带轮应靠近轴承；主动轴使用双轴承座或等效宽跨距支撑，不允许由滚筒薄壁筒体承担齿轮啮合载荷。
- 每段链采用 arc-slot idler 调节。理论几何仍需预留装配与磨损行程；不得把 96 mm 固定孔距当成无需张紧的证据。

## 堵转保护

- `ASSUMED` 软件电流告警：3.4 A 连续 200 ms 后停机；允许受控短反转清堵，但不得让反转触发部署锁扣。
- `ASSUMED` 主轴机械打滑目标：0.8 ± 0.1 N·m。它必须位于齿轮之后、所有 roller 分支之前，才能保护整个传动。
- `CALCULATED` 线性电机模型在 3.4 A 对应约 0.755 N·m 主轴扭矩；0.8 N·m 打滑目标与软件阈值相邻，需在台架上用扭矩臂校准。
- `TBD` 打滑元件具体结构、摩擦片材料、热衰减和复位重复性。CAD 中仅有包络，不是已选购件。

## 翻转放出与锁扣

### 运动定义

- 展开角 198°，收纳角 103°，角度均相对 +X 定义。
- 左右各一个弹性元件；底盘锚点相对 pivot 为 `(-45, -47)` mm，摆臂连接点半径 90 mm。
- `ASSUMED` 每侧弹簧力：收纳端 30 N、展开端 15 N。对应弹簧端点长度约 136.95 / 44.90 mm；这不是标准弹簧料号，必须实测力—长度曲线。
- `CALCULATED` 双弹簧部署扭矩约为收纳端 2.146 N·m、展开端 1.852 N·m；展开端约形成 10.3 N 指轴下压力。

### 结构载荷路径

收纳时由左右两个承载棘爪锁住摆臂，并用贯穿横轴同步。棘爪接触法线应在其转轴 1 mm 内通过，使弹簧力不会把大扭矩传到解锁舵机。REV `REV-41-3334` 通过 20 mm 曲柄和拉杆只转动横轴；舵机输出轴、摇臂和拉杆均不得成为收纳止挡。

`CALCULATED` 在 90 mm 锁扣半径处，总锁扣载荷约 23.8 N；加入 0.05 N·m 回位扭矩后，静态解锁需求约 0.074 N·m，仅为该舵机 6 V 目录堵转扭矩的约 5.6%。这不包含摩擦、偏心、冲击或供电压降，因此仍需实物验证。

展开端由左右独立机械硬止挡承载，使用可更换 TPU 垫消能。`ASSUMED` 原型静载目标为每侧 250 N；该数值必须通过载荷测试关闭，不能由当前包络 CAD 宣称通过。

### 收回边界

当前版本是“赛前手动压回并重新挂锁、比赛中一次弹出”。它满足单直流电机驱动 Intake，但使用一个小舵机解锁。若规则/策略要求比赛中主动收回，必须新增需求和机构；不得把手动收回隐含为主动收放。

主轴反转凸轮方案被保留为 `SUPERSEDED_HIGH_RISK`：它会与反吐/清堵方向冲突，且把部署状态耦合到 roller 控制。首个原型不采用。

## 自制件边界

- 三根 Ø60 × 318 mm roller：薄壁管＋可替换高摩擦套；筒体壁厚、端塞和动平衡 `TBD`。
- 前端 13 片 73 × 18 × 3 mm TPU/硅胶指片：硬度与根部圆角 `TBD`。
- 两块摆臂板：材料初选 3 mm 6061 铝或 4.5–6 mm 纤维增强板，最终截面待静载和撞击试验。
- 弹簧、棘爪、横轴、硬止挡、链罩、带罩及清堵门均需详细 CAD；所有外露夹点必须有护罩。

## 原型验收矩阵

1. **单侧空载台架**：安装真实电机、斜齿轮、主轴、两段链路和前轴带路；25%/50%/100% 指令各运行 2 min，记录转向、跑偏、异响、温升和空载电流。
2. **链/带几何**：量出两段链中心距和前轴中心距；确认小带轮至少 6 齿啮合，所有护罩动态间隙 ≥2.5 mm。
3. **打滑校准**：扭矩臂测主轴打滑起点，目标 0.8 ±0.1 N·m；连续 10 次偏差 ≤10%，热态重复。
4. **堵转保护**：逐级卡住 roller，确认 3.4 A / 200 ms 起始策略不会损伤齿轮、链条、轴承座或 Control Hub；用实测数据修订阈值。
5. **弹簧表征**：逐根测量 44.9–137.0 mm 范围力曲线和滞回；展开/收纳两端均不得出现负部署力矩。
6. **锁扣循环**：先无弹簧验证双棘爪同步，再在目标弹簧载荷下做 200 次释放；断电保持收纳，舵机不接触结构止挡。
7. **硬止挡**：每侧逐级加载至 250 N 原型目标并检查永久变形；随后低速场边碰撞 10 次。
8. **球路**：POLLEN 与 NECTAR 各至少 30 次，覆盖中心、±120 mm 偏置、贴墙、静止和滚动；记录首次捕获率、峰值电流和堵塞位置。
9. **包络**：收纳、展开、受压、抬起四种稳定状态分别进入正式尺寸夹具。CAD 当前包络通过只是一项几何筛查。

## 当前风险与下一步

- `TBD` 底盘前梁、保险杠/车轮、T05 输送入口、电池和线束实测接口；没有这些数据不能发布整机安装图。
- 444 mm CAD 宽度位于 457.2 mm 方向内，但只剩约 13.2 mm 总余量；真实螺栓头、护罩与结构公差必须进入尺寸链。
- 弹簧与打滑器仍无 COTS 料号，不能下整套采购单。
- 同一电机驱动全部轴，任一处堵转都会影响整个 Intake；清堵门和主轴保护不是可选项。
- 本设计是否进入当前 T04，必须与 C04-B1 做接口、资源、策略和实物表现比较并形成新决策。

**NEXT ACTION**：制作单侧全传动＋单摆臂锁扣验证台架，先采购/借用上述 goBILDA/REV 件；测量链带轴向堆叠、打滑扭矩、弹簧力曲线和 200 次释放，再决定是否进入 M4 详细 CAD。
