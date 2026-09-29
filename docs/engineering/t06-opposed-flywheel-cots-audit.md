# T06 对置双飞轮 COTS 审计与修订

日期：2026-09-28  
设计 ID：`C06B-COTS-0.1`  
成熟度：M3 COTS-CONSTRAINED PACKAGING；不等于制造发布或实物验证。

## 范围与结论

- `KNOWN`：回滚后的最新版双飞轮基线是 `cad/paddle_launcher_constrained.py`；每根飞轮轴由一台电机独立直驱，模型中没有外置啮合齿轮。
- `REJECTED_CATALOG_MATCH`：旧 Ø38 mm 电机、无 SKU 电机夹具、16 × 7 mm 轴承代理、194 mm 轴和无 SKU 联轴器不能直接形成可采购 BOM。
- `DECISION`：改用 goBILDA 原生 8 mm REX 传动栈；两台电机统一布置在 −Y 侧，调隙双连杆保留在 +Y 侧。
- `VALIDATED_GEOMETRY`：POLLEN/NECTAR 两个端点均通过所列实体干涉检查；总包络保持在 18 in 立方体内。
- `TBD`：电机、夹具和联轴器的官方 STEP 仍需替换当前简化包络，以关闭全部轴向细节、公差、紧固件长度和电线弯曲空间。

## 采购件映射

| 功能 | 数量 | 供应商与 SKU | 审计结果 |
|---|---:|---|---|
| 96 mm 30A Gecko 飞轮 | 4 | goBILDA `3613-0014-0096` | `KNOWN_VENDOR`，14 mm 孔、16 mm 方孔型、105 g/件 |
| 飞轮轮毂 | 4 | goBILDA `1309-0016-4008` | `KNOWN_VENDOR`，8 mm REX、16 mm 孔型、平衡式 Sonic Hub |
| 飞轮轴 | 2 | goBILDA `2106-4008-1680` | `KNOWN_VENDOR`，168 mm 不锈钢 8 mm REX；替代不存在的 194 mm 目录长度 |
| 轴承 | 4 | goBILDA `1611-0514-4008` | `KNOWN_VENDOR`，8 mm REX × 14 mm OD × 5 mm；替代旧 16 × 7 mm 代理 |
| 飞轮电机 | 2 | goBILDA `5203-2402-0003` | `KNOWN_VENDOR`，3.7:1、1620 rpm、396 g、24 mm 8 mm REX 输出轴 |
| 电机夹具 | 2 | goBILDA `1401-0043-0036` | `KNOWN_VENDOR`，43 mm 宽、36 mm 孔；替代无 SKU Ø38 夹具 |
| 轴联轴器 | 2 | goBILDA `4007-4008-4008` | `KNOWN_VENDOR`，8 mm REX–8 mm REX，高速平衡夹紧式 |
| 调隙舵机 | 1 | goBILDA `2000-0025-0002` | `KNOWN_VENDOR`，位置模式、60 g |
| 送料连续旋转舵机 | 1 | goBILDA `2000-0025-0003` | `KNOWN_VENDOR`，连续旋转模式、58 g |
| 送料轴 | 1 | goBILDA `2106-4008-1920` | `KNOWN_VENDOR`，192 mm 不锈钢 8 mm REX |
| 舵机框架 | 2 | goBILDA `1802-0043-0001` | `KNOWN_VENDOR`，标准舵机、43 mm 宽 |
| 调隙舵机盘 | 1 | goBILDA `1908-0025-0032` | `KNOWN_VENDOR`，25T、Ø32 × 6 mm |
| 送料轴联轴器 | 1 | goBILDA `4001-0025-4008` | `KNOWN_VENDOR`，25T 到 8 mm REX |
| 外置齿轮 | 0 | 不需要 | 两轴各自直驱；不得在 BOM 或 CAD 中加入悬空齿轮 |

所有已选机械采购件均可从用户允许的 goBILDA/REV 两家商店之一采购；本版机械件全部选用 goBILDA。REV Control/Expansion Hub 保持系统电气基线，不作为本次机械改型对象。

## 真实连接与轴向堆叠

从机器人中心向 −Y 依次为：飞轮轴 → 外置滑座内的 14 × 5 mm 轴承 → 8 mm REX 双夹紧联轴器 → 电机 24 mm REX 输出轴 → 36 mm 电机夹具。两台夹具均通过两条刚性桥接件固定到各自移动滑座，因此调隙时电机、联轴器、轴承和飞轮轴保持同轴。

`CALCULATED` 简化轴向堆叠：

- 飞轮轴进入联轴器 7.5 mm；
- 电机输出轴进入联轴器 9.5 mm；
- 两轴端面间留 4.0 mm；
- 联轴器与滑动轴承座留 0.5 mm 名义间隙；
- 侧板只开 8.4 mm 宽轴槽，9 mm 中心行程对应 17.4 mm 总槽长，轴承不再穿过侧板长槽。

这些数值是基于目录界面和简化包络的 `CALCULATED` 值，最终必须用官方 STEP 和实物垫片/卡簧堆叠复核。

## 验证与开放项

- `VALIDATED_GEOMETRY`：POLLEN 160 mm 与 NECTAR 178 mm 轴距端点的飞轮/侧板、飞轮/通道、飞轮/滑座、电机/滑座、夹具/滑座、联轴器/滑座、拨杆/通道和调隙连杆检查均无实体交叠。
- `CALCULATED`：包络约 383.849 × 359.014 × 400.024 mm，低于 457.2 mm 立方体限制；该结论不包含线束和最终护罩。
- `TBD`：实际 Gecko 高速膨胀、Sonic Hub 螺钉长度/防松、联轴器最低夹持长度、轴端卡簧方向、打印滑座配合、调隙舵机力矩、双电机电流与温升。
- `NEXT`：导入所列官方 STEP，做轴向堆叠与紧固件检查；之后才允许采购和安全旋转台架。

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
