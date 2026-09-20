# 模块接口控制方法（ICD）

## 全局坐标系

采用右手坐标系：`+X` 为机器人前进方向，`+Y` 为机器人左侧，`+Z` 向上。全局原点 `R0` 暂定在名义驱动接触平面上、T01 轮迹包络的几何中心。方向约定为 `KNOWN` 的项目约定；原点的可制造基准实现为 `TBD`，在底盘概念确定后冻结。

观察方向定义：俯视图沿 `-Z` 看，前视图沿 `-X` 看，左视图沿 `-Y` 看。角度按右手定则；CAD 长度默认 mm。

## 接口作为一等对象

每个跨模块接口使用稳定 ID `IF-<源模块>-<目标模块>-NN`，并指定单一接口责任人、版本和双方批准状态。一个接口记录至少包含：

| 类别 | 必填内容 |
|---|---|
| 机械 | 基准面/轴、孔型、紧固件、载荷与力矩、材料接触、装配方向 |
| 运动 | 轴/轴承、皮带/链条/齿轮、行程、速度、禁入区、动态余量 |
| 几何 | 名义包络、扫掠包络、连接区、维修空间、最小间隙、坐标变换 |
| 电气 | 执行器/传感器、控制器端口、电压、峰值/持续电流、连接器、线束路径 |
| 软件 | 命令、单位、范围、更新率、传感输入、状态、故障/超时行为 |
| 验证 | 检查方法、验收阈值、证据文件、状态和日期 |

## 机械接口约束

- 孔位必须相对命名基准标注，不能通过上一个零件的偶然边缘定位。
- 轴、轴承、轮毂和传动件分别记录名义尺寸、配合、公差和轴向约束。
- 名义包络与运动扫掠包络分开；线束、工具进入和拆卸路径也属于包络。
- 制造公差与装配间隙不得混入名义几何参数。

## 变更控制

接口从 `DRAFT → PROPOSED → FROZEN → VERIFIED`。冻结后，任何孔位、基准、连接器、信号或包络变更都必须：更新接口版本；列出受影响模块；记录验证回退范围；在决策日志或变更记录中说明原因。

## 接口记录模板

```text
Interface ID / Version / Status:
Owner / Participating modules:
Requirement links:
Mechanical and datum definition:
Geometric envelope and clearance:
Moving/power-transmission interface:
Electrical definition:
Software/control definition:
Loads, tolerances, units:
Failure behavior:
Verification method and evidence:
Open items:
```
