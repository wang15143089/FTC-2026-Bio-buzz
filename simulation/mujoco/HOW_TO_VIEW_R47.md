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

软件：本仓库的 `.venv-cad`（内含 `mujoco 3.14.0`，不需要另装）。在仓库根目录 PowerShell 里：

```powershell
.\.venv-cad\Scripts\python.exe -m mujoco.viewer --mjcf=simulation/mujoco/out/R47_launcher_4xPOLLEN_gap064.xml
```

四个可选 XML（换成别的路径即可）：

| 文件（`simulation/mujoco/out/` 下） | 内容 |
|---|---|
| `R47_launcher_4xPOLLEN_gap064.xml` | 4 颗 POLLEN，轮间夹口 64 mm |
| `R47_launcher_4xNECTAR_gap082.xml` | 4 颗 NECTAR，轮间夹口 82 mm |
| `R47_launcher_mixed4_gap064.xml` | 混装，初始档 64 mm |
| `R47_launcher_mixed4_gap082.xml` | 混装，初始档 82 mm |

鼠标：左键拖 = 旋转，右键拖 = 平移，滚轮 = 缩放，空格 = 暂停/继续，Esc = 关闭。
右侧面板的 Control 滑条可以手动给飞轮/拨杆速度（拖动后飞轮会转），但闸门是 mocap，不会自己动。

## B. 看全流程动画（推荐）：同一个 MuJoCo 窗口 + 驱动脚本

```powershell
# 默认：POLLEN gap064
.\.venv-cad\Scripts\python.exe simulation/mujoco/run_R47_xml.py --view

# 指定文件
.\.venv-cad\Scripts\python.exe simulation/mujoco/run_R47_xml.py out/R47_launcher_4xNECTAR_gap082.xml --view

# 混装（自动换档；换档时窗口会重建一次）
.\.venv-cad\Scripts\python.exe simulation/mujoco/run_R47_xml.py --pair --view

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

## C. 备用：MuJoCo 官方 GUI（`simulate.exe`）

本机**没有** `simulate.exe`（`.venv-cad` 与 `C:\Program Files` 下都没有）。若以后要用：
从 MuJoCo 官方 GitHub release 下载 `simulate` 压缩包，运行 `bin\simulate.exe`，
菜单 `File → Open Model…` 选上表任意 XML。行为与方案 A 相同：**静止**，要动作仍得跑方案 B。

## 相关文件（绝对路径）

- `C:\Users\admin\OneDrive\文档\ChatGPT\FTC 2026 biobuzz\simulation\mujoco\run_R47_xml.py`
- `C:\Users\admin\OneDrive\文档\ChatGPT\FTC 2026 biobuzz\simulation\mujoco\out\R47_launcher_4xPOLLEN_gap064.xml`
- `C:\Users\admin\OneDrive\文档\ChatGPT\FTC 2026 biobuzz\simulation\mujoco\out\R47_launcher_4xNECTAR_gap082.xml`
- `C:\Users\admin\OneDrive\文档\ChatGPT\FTC 2026 biobuzz\simulation\mujoco\out\R47_launcher_mixed4_gap064.xml`
- `C:\Users\admin\OneDrive\文档\ChatGPT\FTC 2026 biobuzz\simulation\mujoco\out\R47_launcher_mixed4_gap082.xml`
- 模型生成器：`C:\Users\admin\OneDrive\文档\ChatGPT\FTC 2026 biobuzz\simulation\mujoco\gen_R47_mjcf.py`
