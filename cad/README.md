# BIOBUZZ 对置飞轮发射机构初模

坐标约定：`X-Y` 为底盘安装平面，`+Z` 向上，`+X` 为发射方向在底盘上的投影。模型单位均为毫米。

## 初版参数

- 发射总成相对底盘倾角：52°
- 96 mm GripForce Gecko，单轴两片、上下共四片
- POLLEN轮缘间隙：64 mm；轴心距160 mm
- NECTAR轮缘间隙：82 mm；轴心距178 mm
- 上下滑台各移动9 mm
- 通道净宽104 mm、净高110 mm
- 水平输送段：163 mm长，球心高56 mm
- 水平转斜向：72 mm主动踢送滚轮＋48 mm弹性上导向滚轮
- 马达包络：Ø38 × 104 mm
- 舵机包络：41 × 21 × 40 mm

`biobuzz_launcher.py`生成POLLEN和NECTAR两个位置的STEP总成、GLB与STL预览网格。STEP保留零件名称与颜色。水平输送原型采用包络建模，包含低位输送带、主动踢送滚轮、弹性上导向滚轮、单球闸门以及约38°到52°的过渡导槽。

## 运行

```powershell
python -m venv .venv-cad
.\.venv-cad\Scripts\python.exe -m pip install -r .\cad\requirements.txt
.\.venv-cad\Scripts\python.exe .\cad\biobuzz_launcher.py
```

输出位于`cad/output/`。

## 倾角计算假设

初算采用：发射口高度0.34 m、目标中心高度1.15 m、水平距离1.50 m。真空弹道的最低能耗角约59.2°；模型采用52°，以缩短带孔球的滞空时间、降低气动离散、控制机构高度，并预留42°～58°的长孔机械调角范围。该角度必须在真实场地以不同距离和球体样本继续标定。

## 需要实物确认的尺寸

- Gecko轮实际厚度、轮毂紧固方式及高速径向膨胀
- 选用马达和联轴器的法兰孔位
- 选用舵机的耳板孔距和输出轴高度
- 底盘梁位置及机器人起始包络
- CELL实际目标中心、机器人允许发射位置与常用射距

## T02 单电机翻转 intake

`biobuzz_single_motor_flipout_intake.py`建立视频启发的三固定滚筒＋同轴摆臂前指轮基线。模型包含竖置电机、锥齿轮转向、单侧同步带、多级横轴、恒中心距摆臂皮带、弹簧放出、硬止挡、舵机锁扣和严格单执行器用的反转凸轮备选，并导出展开/收纳两种姿态。

```powershell
.\.venv-cad\Scripts\python.exe .\cad\biobuzz_single_motor_flipout_intake.py
```

设计依据、参数、BOM 与测试标准见 `docs/engineering/t02-single-motor-flipout-intake-baseline.md`。

## 连续舵机送料细模

`continuous_feeder.py`为不含比赛用球的独立送料机构细模。两条水平同步带和两条38°斜升同步带共用转角驱动轴，由一只连续旋转舵机驱动；出口72 mm弹性上压轮由第二只连续旋转舵机通过20T:48T同步带减速驱动，并通过双摆臂与预紧连杆浮动22 mm。模型包括侧板、轴、轴承座、带齿同步轮、双带、护罩、ServoBlock支架、联轴器、导向板和发射入口软导向。

```powershell
.\.venv-cad\Scripts\python.exe .\cad\continuous_feeder.py
.\.venv-cad\Scripts\python.exe .\cad\render_continuous_feeder.py
```

## 三拨杆连续送料＋对置飞轮完整总成

`paddle_feeder_launcher.py`取消所有输送带，改用连续旋转舵机直驱的三拨杆转子。每根拨杆带独立铰轴与可更换柔性拨片，经过三段固定导槽和单向柔性挡片，将水平进入的物体连续送入52°发射通道。模型明确保留上下两根飞轮轴，每根轴安装两片96 mm Gecko轮，并补齐8 mm轴到14 mm轮芯的Sonic Hub连接。

```powershell
.\.venv-cad\Scripts\python.exe .\cad\paddle_feeder_launcher.py
.\.venv-cad\Scripts\python.exe .\cad\render_paddle_launcher.py
```
