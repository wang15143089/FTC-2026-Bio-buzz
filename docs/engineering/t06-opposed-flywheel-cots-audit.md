# T06 对置双飞轮 COTS 审计与修订

日期：2026-10-01

设计 ID：`C06B-COTS-0.2`

成熟度：M3 COTS-CONSTRAINED PACKAGING；不等于制造发布或实物验证。

## 范围与结论

- `KNOWN`：回滚后的最新版双飞轮基线是 `cad/paddle_launcher_constrained.py`；每根飞轮轴由一台电机独立直驱，模型中没有外置啮合齿轮。
- `KNOWN_VENDOR_CAD`：13 个已选 goBILDA SKU 的官方 STEP 已下载、回读并登记 SHA-256，原始文件位于 `references/vendor/gobilda/t06/step/`，清单为 `references/vendor/gobilda/t06/manifest.json`。
- `DECISION`：工作装配按用户要求将电机、舵机、支架、轮毂等每个采购 SKU 表示为一个连通实体；官方原始多实体 STEP 保留为尺寸与接口审计依据，不在主装配中展开内部零件。
- `DECISION`：采用 goBILDA 原生 8 mm REX 传动栈；两台电机统一布置在 −Y 侧，调隙双连杆保留在 +Y 侧。
- `VALIDATED_GEOMETRY`：POLLEN/NECTAR 两个端点均通过所列实体干涉检查；每个采购件工作模型均恰为一个实体；总包络保持在 18 in 立方体内。
- `TBD`：实际垫片、卡簧、螺钉、花键配合、打印公差、线束弯曲空间与高速动态行为仍需实物关闭。

## 采购件映射

| 功能 | 数量 | 供应商与 SKU | 审计结果 |
|---|---:|---|---|
| 96 mm 30A Gecko 飞轮 | 4 | goBILDA `3613-0014-0096` | `KNOWN_VENDOR_CAD`，14 mm 孔、16 mm 方孔型、105 g/件 |
| 飞轮轮毂 | 4 | goBILDA `1309-0016-4008` | `KNOWN_VENDOR_CAD`，8 mm REX、16 mm 孔型、平衡式 Sonic Hub |
| 飞轮轴 | 2 | goBILDA `2106-4008-1680` | `KNOWN_VENDOR_CAD`，168 mm 不锈钢 8 mm REX |
| 轴承 | 4 | goBILDA `1611-0514-4008` | `KNOWN_VENDOR_CAD`，8 mm REX × 14 mm OD × 5 mm，法兰最大 Ø15 mm |
| 飞轮电机 | 2 | goBILDA `5203-2402-0003` | `KNOWN_VENDOR_CAD`，3.7:1、1620 rpm、396 g、24 mm 8 mm REX 输出轴；官方 CAD 包络 37.5 × 131.17 × 37.5 mm |
| 电机夹具 | 2 | goBILDA `1401-0043-0036` | `KNOWN_VENDOR_CAD`，43 mm 宽、36 mm 孔；官方 CAD 包络 43 × 8 × 49 mm |
| 轴联轴器 | 2 | goBILDA `4007-4008-4008` | `KNOWN_VENDOR_CAD`，8 mm REX–8 mm REX；官方 CAD 最大 Ø20.495 × 21 mm |
| 调隙舵机 | 1 | goBILDA `2000-0025-0002` | `KNOWN_VENDOR_CAD`，位置模式、60 g；官方 CAD 包络 54.3 × 20.15 × 44.1 mm |
| 送料连续旋转舵机 | 1 | goBILDA `2000-0025-0003` | `KNOWN_VENDOR_CAD`，连续旋转模式、58 g；同系列官方 CAD 包络 |
| 送料轴 | 1 | goBILDA `2106-4008-1920` | `KNOWN_VENDOR_CAD`，192 mm 不锈钢 8 mm REX |
| 舵机框架 | 2 | goBILDA `1802-0043-0001` | `KNOWN_VENDOR_CAD`，标准舵机、43 mm 宽 |
| 调隙舵机盘 | 1 | goBILDA `1908-0025-0032` | `KNOWN_VENDOR_CAD`，25T、Ø32 × 6 mm |
| 送料轴联轴器 | 1 | goBILDA `4001-0025-4008` | `KNOWN_VENDOR_CAD`，25T 到 8 mm REX；官方 CAD 长 17 mm |
| 外置齿轮 | 0 | 不需要 | 两轴各自直驱；不得在 BOM 或 CAD 中加入悬空齿轮 |

所有已选机械采购件均可从用户允许的 goBILDA/REV 两家商店之一采购；本版机械件全部选用 goBILDA。REV Control/Expansion Hub 保持系统电气基线，不作为本次机械改型对象。

## 单实体表示规则

官方 STEP 可能把紧固件、壳体、轴、编码器盖等拆成多个实体，例如电机源文件包含 66 个实体。`cad/t06_vendor_cad.py` 读取清单中的官方包络和关键接口尺寸，为每个 SKU 生成一个连通的工作实体；电机本体与输出轴、舵机本体与输出端、轮与轮芯、支架各壁均在组件内部融合。

该处理适合 M3 包络、运动链和干涉检查，但不会宣称保留内部零件级细节。官方 STEP 未被删除或改写，可随时用于局部接口复核。不得把工作单实体当成制造模型或把融合后的紧固件视为可加工结构。

## 真实连接与轴向堆叠

从机器人中心向 −Y 依次为：飞轮轴 → 外置滑座内的 14 × 5 mm 轴承 → 8 mm REX 双夹紧联轴器 → 电机 24 mm REX 输出轴 → 36 mm 电机夹具。两台夹具均通过两条刚性桥接件固定到各自移动滑座，因此调隙时电机、联轴器、轴承和飞轮轴保持同轴。

`CALCULATED` 简化轴向堆叠：

- 飞轮轴进入联轴器 7.5 mm；
- 电机输出轴进入联轴器 9.5 mm；
- 两轴端面间留 4.0 mm；
- 联轴器与滑动轴承座留 0.5 mm 名义间隙；
- 侧板只开 8.4 mm 宽轴槽，9 mm 中心行程对应 17.4 mm 总槽长，轴承不穿过侧板长槽。

这些数值是基于目录界面和官方 CAD 包络的 `CALCULATED` 值，最终仍须用实物垫片、卡簧与紧固件堆叠复核。

## 验证与开放项

- `VALIDATED_GEOMETRY`：POLLEN 160 mm 与 NECTAR 178 mm 轴距端点的飞轮/侧板、飞轮/通道、飞轮/滑座、电机/滑座、夹具/滑座、联轴器/滑座、拨杆/通道和调隙连杆检查均无实体交叠。
- `VALIDATED_GEOMETRY`：修正送料支撑颊板轴孔曾错误切在 Y=0、未切到各颊板的问题；轴孔现分别位于 Y=±62 mm，送料轴与颊板不再穿模。
- `CALCULATED`：包络约 383.849 × 364.783 × 400.024 mm，低于 457.2 mm 立方体限制；该结论不包含线束和最终护罩。
- `VALIDATED_SOFTWARE`：自动测试 40/40 通过，发射器报告 14/14 检查为真，13 个 SKU 工作代理的实体计数均为 1。
- `TBD`：实际 Gecko 高速膨胀、Sonic Hub 螺钉长度/防松、联轴器最低夹持长度、轴端卡簧方向、打印滑座配合、调隙舵机力矩、双电机电流与温升。
- `NEXT`：制作带护罩的双轴安全旋转台架，实测两个间隙端点的轴向堆叠、空载振动、电流、温升和转速恢复；通过前不得进入 M4。

## 官方来源

- https://www.gobilda.com/gripforce-gecko-wheel-14mm-bore-96mm-diameter-30a-durometer/
- https://www.gobilda.com/1309-series-sonic-hub-8mm-rex-bore/
- https://www.gobilda.com/stainless-steel-rex-shafting/
- https://www.gobilda.com/1611-series-flanged-ball-bearing-8mm-rex-id-x-14mm-od-5mm-thickness-2-pack/
- https://www.gobilda.com/5203-series-yellow-jacket-planetary-gear-motor-3-7-1-ratio-1620-rpm-3-3-5v-encoder/
- https://www.gobilda.com/1401-series-2-side-2-post-clamping-mount-43mm-width-36mm-bore/
- https://www.gobilda.com/4007-series-hyper-coupler-8mm-rex-bore-to-8mm-rex-bore/
- https://www.gobilda.com/2000-series-dual-mode-servo-25-2-torque/
- https://www.gobilda.com/2000-series-dual-mode-servo-25-3-speed/
- https://www.gobilda.com/1802-series-servo-frame-43mm-width-for-standard-size-servos/
- https://www.gobilda.com/1908-series-servo-hub-25-tooth-spline-32mm-diameter/
- https://www.gobilda.com/4001-series-clamping-servo-to-shaft-coupler-25-tooth-spline-to-8mm-rex-bore/
