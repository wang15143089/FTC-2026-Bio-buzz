# CONTINUOUS-FEEDER-COTS-0.1 可采购性审查与改版

日期：2026-09-28  
关联：Linear KEI-10、KEI-7、KEI-9  
输入附件：`C:\Users\admin\OneDrive\Desktop\continuous_servo_feeder.glb`  
文件身份：`KNOWN`，附件 SHA-256 `8AE12CF4F5D8D1B1154393231763643682DB87C25EB4D271C17B61F6F32B451C` 与仓库 `cad/output/continuous_servo_feeder.glb` 完全一致。

## 范围说明

`KNOWN`：该 GLB 是 71 节点的独立连续送料/上压轮机构，不包含 Gecko 飞轮、飞轮直流电机或飞轮电机夹具。它与对置飞轮发射器接口相邻，但不是完整发射器总成。因此本次直接改版其同步轮、同步带、轴、轴承、舵机与舵机安装接口；相邻对置飞轮模型的直流电机夹具仍属于 KEI-10 的后续官方 STEP/实物接口检查。

## 审查结论

| 原模型项目 | 审查结果 | 处理 |
|---|---|---|
| 20T:48T、5 mm HTD 上压轮减速 | `REJECTED_CATALOG_MATCH`：goBILDA 当前 5 mm HTD 目录只有 16T、24T、48T等选项，未找到原模型的20T；原18 mm带宽也不对应9 mm目录带 | 改为在售16T:48T，3.000:1；使用275 mm、9 mm宽皮带 |
| 水平/斜升“28 mm、20T”同步轮 | `REJECTED_CATALOG_MATCH`：齿数、节距直径和外径互相不一致 | 全部改为3417-4008-0016，16T、8 mm REX、5 mm HTD |
| 约329.2 mm斜升带 | `REJECTED_CATALOG_MATCH`：未确认330 mm目录带 | 改为3412-0009-0320，轴距从124.6 mm改为`CALCULATED` 120.000 mm，38°方向保持不变 |
| 360 mm水平带 | `KNOWN_VENDOR_VERIFIED` | 保留140.000 mm轴距，改成3412-0009-0360、9 mm宽 |
| “ServoBlock envelope” | `REJECTED_AS_PART_DEFINITION`：原几何不是任何一个完整SKU | 改为2000-0025-0003舵机＋1802-0043-0001舵机框＋4001-0025-4008 H25T到8 mm REX夹紧联轴器；轴由两侧轴承支承 |
| 8 mm圆轴和无料号轴承 | `REJECTED_AS_PURCHASING_DEFINITION` | 改为2106系列8 mm REX轴及1611-0514-4008法兰轴承 |
| 自定义侧板、导板、摆臂、弹性轮 | `CUSTOM_PART_ALLOWED` | 保留为PETG/柔性打印件；不得作为商用品采购 |

## 改版关键尺寸

- `CALCULATED` 水平16T:16T、360 mm带中心距：140.000 mm。
- `CALCULATED` 斜升16T:16T、320 mm带中心距：120.000 mm；斜率保持38.000°。
- `CALCULATED` 上压轮16T:48T、275 mm带近似中心距：51.163 mm；需要长孔或独立张紧器关闭制造误差。
- `CALCULATED` 上压轮传动比：3.000:1。115 rpm舵机空载时，上压轮约38.3 rpm；这是目录速度推算，不是带球实测。
- `CALCULATED` 上压轮皮带面移至Y=75 mm，与最近摆臂名义净距1.5 mm。
- `KNOWN` X-Y仍为底盘安装平面，+Z向上，+X为送料方向。

## COTS BOM（关键运动件）

| 数量 | SKU | 名称 | 状态 |
|---:|---|---|---|
| 2 | 2000-0025-0003 | Dual Mode Servo 25-3 Speed | `KNOWN_VENDOR_VERIFIED` |
| 2 | 1802-0043-0001 | 43 mm标准舵机框 | `KNOWN_VENDOR_VERIFIED` |
| 2 | 4001-0025-4008 | H25T至8 mm REX夹紧联轴器 | `KNOWN_VENDOR_VERIFIED` |
| 9 | 3417-4008-0016 | 16T、5 mm HTD、8 mm REX同步轮 | `KNOWN_VENDOR_VERIFIED` |
| 1 | 3415-0014-0048 | 48T、5 mm HTD、14 mm孔同步轮 | `KNOWN_VENDOR_VERIFIED` |
| 1 | 1309-0016-4008 | 8 mm REX Sonic Hub | `KNOWN_VENDOR_VERIFIED` |
| 2/2/1 | 3412-0009-0360 / -0320 / -0275 | 360/320/275 mm、9 mm宽HTD带 | `KNOWN_VENDOR_VERIFIED` |
| 3 | 2106-4008-1440 | 144 mm 8 mm REX钢轴 | `KNOWN_VENDOR_VERIFIED` |
| 1 | 2106-4008-1920 | 192 mm 8 mm REX钢轴 | `KNOWN_VENDOR_VERIFIED` |
| 8 | 1611-0514-4008 | 8 mm REX ID × 14 mm OD法兰轴承 | `KNOWN_VENDOR_VERIFIED` |

正式URL保存在 `cad/output/continuous_servo_feeder_cots_report.json`。REV目录也存在舵机支架和UltraPlanetary电机支架，但本改版避免混用5 mm HEX/8 mm REX与M3/M4结构体系，统一采用goBILDA运动接口。REV控制系统兼容性不因此改变。

## 输出与验证状态

- 生成脚本：`cad/continuous_servo_feeder_cots.py`
- STEP：`cad/output/continuous_servo_feeder_cots.step`
- GLB：`cad/output/continuous_servo_feeder_cots.glb`
- STL：`cad/output/continuous_servo_feeder_cots.stl`
- 预览：`cad/output/continuous_servo_feeder_cots_preview.png`
- 结构化BOM/参数：`cad/output/continuous_servo_feeder_cots_report.json`
- `VALIDATED_CALCULATION`：`tests/test_continuous_feeder_cots.py` 4/4通过。
- `VALIDATED_GEOMETRY`：CadQuery成功生成并导出STEP/STL/GLB，STEP回读50个实体、包络375.868 × 240.000 × 200.077 mm；STL开放/非流形边计数为0；GLB为51节点/50网格；预览完成。
- `TBD`：官方供应商STEP尚未逐件装入总成；轴向垫片、E-clip位置、皮带预紧、舵机框紧固件长度和实体装配净距必须在采购/台架阶段关闭。

## 相邻飞轮电机夹具

`KNOWN`：附件本身没有直流电机夹具。相邻发射器脚本中的58 × 6 mm电机安装板是自定义件，不能冒充目录件。若采用Ø36 mm goBILDA 5203，优先候选是1401-0043-0036双侧36 mm夹紧座；若采用REV UltraPlanetary，则应整体换成REV-41-1600电机/齿轮箱和REV-41-1621/1623/1624/1625支架，不可把REV 5 mm HEX输出与本改版8 mm REX传动直接混接。最终选择保持`TBD`，等待KEI-10按正式电机SKU和官方STEP关闭。

## 风险与下一步

1. 打印一侧轴系，实测16T/48T轴向堆叠和275 mm带张力；必要时加入3428-0019-0006张紧轮。
2. 以代表性POLLEN/NECTAR做100次送料，记录卡滞、双发、电流、舵机温升和摆臂回位。
3. 在完整发射器中用正式电机SKU替换包络后，再验证电机夹具、飞轮轴同轴度和护罩净距。
4. 原 `continuous_servo_feeder.glb` 保留为superseded基线，不用于采购或制造。
