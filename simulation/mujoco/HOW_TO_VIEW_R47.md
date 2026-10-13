# R47 MuJoCo 台架：用什么软件打开什么文件

适用于 R47 交付的 4 号 MJCF（见 `out/`）。几何单位 mm，模型内部单位 m（`MM = 0.001`）。

## 0. 最重要的一件事

**MJCF 只描述几何和驱动器，不包含控制逻辑。** 用任意 MJCF 查看器直接打开 XML，看到的是一个
**静止**的机构：飞轮不转、拨杆不动、闸门不升降。以下三件事都是外部驱动：

- 飞轮 ±1620 rpm：`fw_upper_vel` / `fw_lower_vel` 速度伺服（靠 `ctrl`）
- 拨杆扫掠：`paddle_vel`（靠 `ctrl`）；停位保持 188° 也是外部速度伺服
- 闸门升降 z 47.5→139.5 mm：`gate_leaf` 是 `mocap` body，得外部每步写 `mocap_pos`

要看到「送球 → 发射」全流程，**必须跑 `run_R47_xml.py`**（方案 B）。

## A. 只看几何（静止）：MuJoCo 自带窗口

软件：本仓库的 `.venv-cad`（内含 `mujoco 3.14.0`，不需要另装）。
在仓库根目录（`C:\Users\admin\OneDrive\文档\ChatGPT\FTC 2026 biobuzz`）的 PowerShell 里：

```powershell
.\.venv-cad\Scripts\python.exe -m mujoco.viewer --mjcf=simulation/mujoco/out/R47_launcher_4xPOLLEN_gap064.xml
```

四个可选 XML（换成别的路径即可）：

| 文件（`simulation/mujoco/out/` 下） | 内容 |
|---|---|
| `R47_launcher_4xPOLLEN_gap064.xml` | 4 颗 POLLEN，轮间夹口 64 mm |
| `R47_launcher_4xNECTAR_gap082.xml` | 4 颗 NECTAR，轮间夹口 82 mm |
| `R47_launcher_mixed4_gap064.xml` | 混装（随机排布），初始档 64 mm |
| `R47_launcher_mixed4_gap082.xml` | 混装（随机排布），初始档 82 mm |

鼠标：左键拖 = 旋转，右键拖 = 平移，滚轮 = 缩放，空格 = 暂停/继续，Esc = 关闭。
右侧面板的 Control 滑条可以手动给飞轮/拨杆速度（拖动后飞轮会转），闸门是 mocap，不会自己动。

## B. 看全流程动画（推荐）：同一个 MuJoCo 窗口 + 驱动脚本

```powershell
# 默认：POLLEN gap064
.\.venv-cad\Scripts\python.exe simulation/mujoco/run_R47_xml.py --view

# 指定文件（从仓库根目录用相对路径即可）
.\.venv-cad\Scripts\python.exe simulation/mujoco/run_R47_xml.py out/R47_launcher_4xNECTAR_gap082.xml --view

# 六相位任选（0/30/60/90/120/150 deg -> --ph 0..5）
.\.venv-cad\Scripts\python.exe simulation/mujoco/run_R47_xml.py out/R47_launcher_4xPOLLEN_gap064.xml --ph 3 --view

# 两倍慢放
.\.venv-cad\Scripts\python.exe simulation/mujoco/run_R47_xml.py --view --slow 2.0
```

窗口操作同方案 A（左键旋转 / 右键平移 / 滚轮缩放 / 空格暂停 / Esc 关闭），机位已预设为侧视，
一眼能看到托板 + 四球 + 闸门 + 拨杆 + 外罩 + 双飞轮。运行时控制台每 1 s 打一行遥测：

```
  t=  8.00s  paddle=  188.0deg  fw=  -1619/  +1619 rpm  gate= 116.3mm  out=1/4
  t=  9.00s  paddle=  548.0deg  fw=  -1619/  +1619 rpm  gate= 139.5mm  out=2/4
```

读法：`paddle` 停在 188°（停位），大于 188° 就是在扫掠；`fw` 一正一负 = 对向旋转；
`gate` 47.5 ↔ 139.5 mm = 闸门抬落；`out` = 已出膛球数。跑完窗口保持打开，Esc 关掉即可。
（遥测是纯 ASCII，中文只是给最终报告用的，重定向到文件也不会崩。）

## B2. 混装 / 随机排布版（4 球 P/N 交替）

混装模型里 4 颗球直径不一致（POLLEN 71.1 mm / NECTAR 92.0 mm），脚本会**自动识别并换档**
（按当前要发的球把轮间夹口切到 64 / 82 mm），命令行不用额外加 `--pair`：

```powershell
.\.venv-cad\Scripts\python.exe simulation/mujoco/run_R47_xml.py out/R47_launcher_mixed4_gap064.xml --view
```

- 换档瞬间旧窗口关掉、按新夹口重开一个窗口，状态（球位、转速、拨杆角）完整搬运，画面接着走。
- 六个起始相位：`--ph 0..5`；要手动强制换档模式仍可用 `--pair`。
- 实测（`--ph 0`）：换档 3 次，**4/4 出膛** —— 球1 6.43 / 球2 5.26 / 球3 6.32 / 球4 5.28 m/s，
  全清 11.28 s（含静置 6 s），每颗平均 1.32 s。日志：`out/_r47v_mix_ph0.log`。
- 带窗口跑 `--view` 时 3 次换档均无报错。

## C. 备用：MuJoCo 官方 GUI（`simulate.exe`）

本机**没有** `simulate.exe`（`.venv-cad` 与 `C:\Program Files` 下都没有）。若以后要用：
从 MuJoCo 官方 GitHub release 下载 `simulate` 压缩包，运行其中的 `simulate.exe`，
菜单 `File → Open Model…` 选上表任意 XML。行为与方案 A 相同：**静止**，要动作仍得跑方案 B。

## 相关文件（绝对路径）

- 驱动脚本：`C:\Users\admin\OneDrive\文档\ChatGPT\FTC 2026 biobuzz\simulation\mujoco\run_R47_xml.py`
- 说明（本文件）：`C:\Users\admin\OneDrive\文档\ChatGPT\FTC 2026 biobuzz\simulation\mujoco\HOW_TO_VIEW_R47.md`
- 单球种：`C:\Users\admin\OneDrive\文档\ChatGPT\FTC 2026 biobuzz\simulation\mujoco\out\R47_launcher_4xPOLLEN_gap064.xml` / `C:\Users\admin\OneDrive\文档\ChatGPT\FTC 2026 biobuzz\simulation\mujoco\out\R47_launcher_4xNECTAR_gap082.xml`
- 混装（随机排布）：`C:\Users\admin\OneDrive\文档\ChatGPT\FTC 2026 biobuzz\simulation\mujoco\out\R47_launcher_mixed4_gap064.xml` / `C:\Users\admin\OneDrive\文档\ChatGPT\FTC 2026 biobuzz\simulation\mujoco\out\R47_launcher_mixed4_gap082.xml`
- 混装实测日志：`C:\Users\admin\OneDrive\文档\ChatGPT\FTC 2026 biobuzz\simulation\mujoco\out\_r47v_mix_ph0.log`
- 模型生成器：`C:\Users\admin\OneDrive\文档\ChatGPT\FTC 2026 biobuzz\simulation\mujoco\gen_R47_mjcf.py`
