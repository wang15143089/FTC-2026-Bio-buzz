# AI 应对“CPU/内存正常但长时间无输出”程序的执行与诊断规范

## 1. 目的

本规范用于指导 AI Agent、Codex、DeepSeek、自动化编程代理或其他代码执行系统处理以下情况：

> 程序仍在运行，CPU、内存、磁盘等资源没有明显异常，但终端、日志、SSE、标准输出或任务状态在较长时间内没有任何更新。

这种情况不能直接等同于“程序卡死”。

AI 必须先判断程序属于：

1. **正常的长耗时计算**
2. **阻塞等待**
3. **死锁 / 活锁**
4. **I/O 等待**
5. **子进程无输出**
6. **输出缓冲导致的假卡死**
7. **网络/API/SSE 长时间无数据**
8. **外部程序 GUI / CAD / 仿真软件正在执行但没有输出**
9. **程序已经失去有效进展**

核心原则：

> **无输出 ≠ 无进展。**
>
> AI 不应仅因为几分钟没有文本输出就杀死程序，而应通过“可观测证据”判断任务是否仍然在前进。

---

# 2. AI 的基本行为原则

当出现“长时间无输出”时，AI 必须遵循以下顺序：

```text
观察
↓
判断是否仍有进展
↓
轻量诊断
↓
请求/读取状态
↓
必要时进行超时恢复
↓
最后才终止程序
```

禁止采用：

```text
无输出
↓
直接认定卡死
↓
kill
```

---

# 3. AI 必须区分三种状态

## 3.1 ACTIVE：仍在工作

即使没有 stdout，只要存在以下任一证据，就应优先视为程序仍在运行：

- CPU 使用率持续存在
- CPU 时间持续增加
- GPU 使用率存在
- 文件大小持续变化
- 输出目录出现新文件
- 临时文件更新时间变化
- 子进程仍在活动
- 网络连接仍有传输
- 仿真时间仍在推进
- CAD/CAE 后台任务仍存在
- 数据库事务仍在运行
- 日志虽然没有新增，但阶段性产物正在更新

AI 应：

> 保持程序运行，并继续监控。

---

## 3.2 BLOCKED：程序在等待

典型表现：

- CPU 接近 0%
- 内存稳定
- 进程仍存在
- 长时间无输出
- 没有输出文件更新

可能原因：

```text
等待 stdin
等待文件锁
等待网络响应
等待 API
等待子进程
等待 GUI 操作
等待 socket
等待数据库锁
等待线程同步
```

AI 应首先检查等待原因，而不是立即终止。

---

## 3.3 STALLED：程序已经失去有效进展

满足多个条件时，可以认为程序可能真正卡住：

```text
CPU 长时间接近 0
+
CPU time 不增长
+
输出文件无变化
+
日志无变化
+
无网络传输
+
无子进程活动
+
无可解释的阻塞原因
```

只有在此情况下，AI 才应考虑：

```text
保存状态
→ 收集诊断信息
→ 优雅终止
→ 修改程序
→ 重试
```

---

# 4. 不允许只使用“固定超时”判断失败

错误：

```python
if no_output_for_120_seconds:
    kill_process()
```

推荐：

```python
if no_output_for_long_time:
    inspect_process_progress()

    if progress_detected:
        continue_running()

    elif known_blocking_operation:
        continue_or_investigate()

    elif no_progress_detected:
        diagnose_before_kill()
```

---

# 5. AI 应使用双超时机制

推荐同时存在两个时间概念。

## 5.1 Output Timeout

表示：

> 多久没有 stdout / stderr / SSE / 日志。

例如：

```text
output_timeout = 60 s
```

它只用于：

> 触发状态检查。

**不能直接用于杀死程序。**

---

## 5.2 Progress Timeout

表示：

> 多久没有任何可验证的进展。

例如：

```text
progress_timeout = 10 min
```

进展包括：

```text
CPU time 增长
文件更新时间变化
文件大小变化
checkpoint 更新
迭代计数增加
仿真时间增加
子进程状态变化
网络数据增加
数据库状态变化
```

只有超过 **Progress Timeout** 才进入深度诊断。

---

# 6. 推荐 AI 状态机

AI 应按照以下状态机管理长时间运行任务：

```text
RUNNING
│
├── 有输出 ───────────────→ RUNNING
│
├── 无输出但有进展 ───────→ SILENT_ACTIVE
│
├── 无输出且疑似等待 ─────→ BLOCKED
│
└── 无输出且无进展 ───────→ SUSPECTED_STALL
                               │
                               ↓
                           DIAGNOSE
                               │
                ┌──────────────┴──────────────┐
                ↓                             ↓
           可恢复阻塞                     无法恢复
                │                             │
                ↓                             ↓
             RESUME                        RESTART
```

---

# 7. AI 在无输出时应该检查什么

## 第一层：进程是否仍存在

检查：

```text
PID 是否存在
exit code 是否已经产生
进程状态
启动时间
CPU time
线程数量
```

Linux 示例：

```bash
ps -o pid,stat,etime,time,%cpu,%mem,cmd -p <PID>
```

Windows 示例：

```powershell
Get-Process -Id <PID> |
Select-Object Id, ProcessName, CPU, WorkingSet, Responding
```

---

# 8. CPU 使用率不能作为唯一判断依据

例如：

```text
CPU = 0%
```

可能只是程序正在：

```text
等待网络
等待硬盘
等待锁
等待子进程
等待 GPU
等待外部软件
等待用户输入
```

而：

```text
CPU = 100%
```

也不能证明程序正常。

它可能处于：

```text
无限循环
busy wait
活锁
错误重试循环
```

因此 AI 应检查：

```text
CPU time 是否增长
+
程序状态是否变化
+
输出产物是否变化
```

---

# 9. 文件是非常重要的“进度信号”

对于 CAD、仿真、机器学习、数据处理任务，应监控：

```text
输出文件 modification time
文件大小
checkpoint
缓存文件
中间 mesh
simulation state
数据库记录
```

例如：

```text
model.step
model.stl
checkpoint.json
result.csv
simulation.log
```

AI 可以比较：

```text
T0:
size = 120 MB

T1:
size = 138 MB
```

即使没有终端输出，也说明程序可能仍在工作。

---

# 10. 推荐引入 Heartbeat

对于预计运行超过几十秒的程序，应主动修改代码加入 heartbeat。

例如：

```python
import time

last_heartbeat = time.time()

for i in range(total_steps):

    run_step()

    if time.time() - last_heartbeat > 10:
        print(
            f"[HEARTBEAT] step={i}/{total_steps}",
            flush=True
        )
        last_heartbeat = time.time()
```

推荐 heartbeat 信息包含：

```text
当前阶段
当前迭代
总迭代
elapsed time
最近完成动作
当前文件
任务百分比
```

例如：

```text
[HEARTBEAT]
stage=mesh_generation
step=3412/12000
elapsed=183s
status=running
```

---

# 11. 必须主动 flush 输出

Python 默认可能存在 stdout 缓冲。

推荐：

```python
print("processing...", flush=True)
```

或者：

```bash
python -u script.py
```

环境变量：

```bash
PYTHONUNBUFFERED=1
```

否则 AI 可能误认为：

```text
没有日志
```

实际上只是：

```text
日志还在 buffer 中。
```

---

# 12. 对 subprocess 的处理

错误写法：

```python
subprocess.run(command)
```

当外部程序运行数分钟时，AI 可能完全看不到状态。

推荐：

```python
process = subprocess.Popen(
    command,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

for line in process.stdout:
    print(line, end="", flush=True)
```

如果外部程序本身不输出，则必须另外监控：

```text
PID
CPU time
文件变化
子进程
```

---

# 13. 不要因为 readline() 没返回就认定程序死亡

以下模式可能永久等待：

```python
line = process.stdout.readline()
```

如果子进程没有输出：

```text
readline()
```

本身会阻塞。

AI 应使用：

```text
非阻塞读取
线程读取
asyncio
select
轮询
```

而不是把 stdout 当作唯一生命信号。

---

# 14. 网络 / API / SSE 情况

如果 AI 调用：

```text
HTTP API
LLM API
SSE
WebSocket
远程服务器
```

出现长时间无数据，应区分：

```text
TCP 连接仍存在
服务器仍处理请求
连接已断开
代理超时
SSE idle
客户端读取阻塞
```

AI 应设计：

```text
connect timeout
read timeout
overall task timeout
heartbeat timeout
```

不要只使用一个 timeout。

例如：

```text
connect_timeout = 10 s
read_timeout = 120 s
overall_timeout = 30 min
```

如果服务支持 heartbeat，应利用：

```text
ping
keepalive
SSE comment
progress event
```

---

# 15. CAD / MuJoCo / Fusion / Blender 等外部工具

对于工程程序，终端无输出尤其常见。

AI 应检查：

```text
后台进程
CPU time
文件输出
autosave
临时目录
mesh 文件
仿真 state
solver progress
```

不要仅依赖：

```text
console stdout
```

例如 CAD 布尔运算可能：

```text
CPU 正常
内存正常
stdout = 0
持续几分钟
```

这不一定是异常。

---

# 16. 推荐建立 progress.json

对于 AI 控制的长期任务，推荐程序定期写：

```json
{
  "status": "running",
  "stage": "mesh_generation",
  "step": 351,
  "total_steps": 1200,
  "last_update": "2026-10-01T23:00:00",
  "last_action": "generated wheel hub mesh"
}
```

AI 可以每隔一段时间读取：

```text
progress.json
```

而不是等待 terminal 输出。

---

# 17. 推荐 checkpoint

长任务必须尽量设计 checkpoint。

例如：

```text
checkpoint/
    stage_01.json
    stage_02.step
    stage_03.pkl
```

如果程序确实需要重启：

```text
不要从头开始
```

而应：

```text
读取最近 checkpoint
→ 恢复运行
```

---

# 18. AI 的分级诊断策略

## Level 0：正常等待

条件：

```text
最近仍有输出
```

行为：

```text
继续等待
```

---

## Level 1：静默运行

条件：

```text
无输出
但存在进度信号
```

行为：

```text
继续运行
+
降低检查频率
```

---

## Level 2：疑似阻塞

条件：

```text
无输出
CPU 低
但存在等待状态
```

行为：

```text
检查：
stdin
网络
锁
子进程
I/O
```

---

## Level 3：疑似卡死

条件：

```text
无输出
CPU time 无变化
无文件变化
无网络
无 checkpoint
```

行为：

```text
收集诊断信息
```

包括：

```text
线程栈
进程树
打开文件
网络连接
最近日志
```

---

## Level 4：恢复

优先：

```text
发送诊断信号
↓
保存 checkpoint
↓
优雅退出
↓
重启
```

最后才：

```text
force kill
```

---

# 19. AI 在 kill 之前必须完成的检查

除非系统资源已经失控，否则必须至少确认：

```text
[ ] PID仍存在

[ ] CPU time是否变化

[ ] 输出文件是否变化

[ ] 是否存在子进程

[ ] 是否正在等待网络

[ ] 是否正在等待stdin

[ ] 是否可能被stdout buffering影响

[ ] 是否存在checkpoint

[ ] 是否可以优雅退出

[ ] 最近一次明确进展是什么
```

---

# 20. 推荐 AI 日志格式

AI 自己也应该记录监控判断：

```text
[23:02:11] process started PID=3812

[23:03:11] no stdout for 60s

[23:03:11] CPU time increased 31.4s → 47.1s

[23:03:11] output.step size 42MB → 61MB

[23:03:11] classification=SILENT_ACTIVE

[23:03:11] action=continue
```

如果最终判断卡住：

```text
[23:15:21] no progress for 600s

CPU time unchanged
output unchanged
network idle
no active child process

classification=STALLED

collecting diagnostics before restart
```

---

# 21. AI 不应重复盲目重试

错误：

```text
程序超时
→ 重启
→ 超时
→ 重启
→ 超时
→ 重启
```

推荐限制：

```text
retry 1:
normal restart

retry 2:
restart with debug logging

retry 3:
stop and analyze root cause
```

建议：

```text
MAX_RETRIES = 3
```

每次 retry 必须保存：

```text
错误
运行时间
最后状态
日志
配置
输入
```

---

# 22. AI 修改代码时优先增加“可观察性”

遇到无法判断的程序时，不应第一时间重写算法。

优先加入：

```text
heartbeat
progress counter
structured logging
flush
checkpoint
timeout
watchdog
```

目标：

> 让下一次运行可以明确知道程序正在做什么。

---

# 23. 推荐 Watchdog 逻辑

伪代码：

```python
last_output = now()
last_progress = now()

while process.is_running():

    output = read_nonblocking_output()

    if output:
        last_output = now()

    progress = inspect_progress()

    if progress.changed:
        last_progress = now()

    if now() - last_output > OUTPUT_TIMEOUT:
        inspect_process()

    if now() - last_progress > PROGRESS_TIMEOUT:

        diagnostics = collect_diagnostics()

        if diagnostics.indicate_blocked_but_valid:
            continue

        save_checkpoint()

        terminate_gracefully()

        restart_from_checkpoint()
```

---

# 24. AI 的标准决策模板

当长时间没有输出时，AI 应按照以下格式思考：

```text
1. 程序是否仍存在？
2. CPU time 是否增长？
3. 是否有文件/状态变化？
4. 是否有子进程？
5. 是否存在 I/O / 网络等待？
6. stdout 是否可能被缓冲？
7. 是否存在明确的长期计算阶段？
8. 最近一次进展是什么？
9. 已经多久没有任何“进展”，而不仅仅是输出？
10. 是否达到 progress timeout？
```

然后输出内部结论：

```text
STATE:
RUNNING / SILENT_ACTIVE / BLOCKED / STALLED

EVIDENCE:
...

ACTION:
continue / inspect / recover / restart
```

---

# 25. 推荐给 AI Agent 的直接系统提示词

下面内容可以直接加入 AI Agent 的 AGENTS.md、SYSTEM PROMPT 或开发规范：

---

## Long-running Process Policy

When running programs, do not treat lack of stdout, stderr, SSE events, or terminal messages as proof that a process is frozen.

A silent process may still be performing useful work.

When a process becomes silent:

1. Check whether the process still exists.
2. Check whether CPU time is increasing.
3. Check whether output files, checkpoints, or intermediate artifacts are changing.
4. Check for active child processes.
5. Check whether the process may be waiting on disk I/O, network I/O, stdin, locks, subprocesses, GUI applications, GPU work, or external solvers.
6. Consider stdout buffering before assuming that logging has stopped.
7. Distinguish `output timeout` from `progress timeout`.

An output timeout must only trigger inspection.

It must NOT automatically terminate the process.

A process should only be considered stalled when multiple independent indicators show that no meaningful progress has occurred for a sufficiently long period.

Use the following state model:

```text
RUNNING
SILENT_ACTIVE
BLOCKED
SUSPECTED_STALL
STALLED
RECOVERING
```

Before terminating a process:

- collect diagnostics;
- preserve logs;
- preserve intermediate files;
- save or locate the latest checkpoint;
- attempt graceful termination first.

Only force-kill a process when graceful recovery is impossible or resource/system safety requires it.

For processes expected to run longer than approximately one minute, prefer adding:

- heartbeat messages;
- progress counters;
- structured logs;
- explicit stdout flushing;
- progress files;
- checkpoints;
- resumable execution.

Do not repeatedly restart a silent process without identifying why it became silent.

If uncertainty remains, favor continued observation over destructive termination when system resources are stable.

---

# 26. 推荐用于 AI CAD / 仿真的附加规则

如果 AI 正在执行：

```text
CadQuery
FreeCAD
Fusion 360
Blender
MuJoCo
有限元
mesh generation
CAM
几何布尔计算
```

应额外遵循：

```text
终端输出不是主要进度判断依据。
```

优先检查：

```text
生成文件
文件更新时间
mesh数量
几何对象数量
solver状态
仿真时间
step计数
外部程序进程
```

对于计算量大的几何操作：

```text
Boolean
fillet
mesh
STEP export
collision generation
```

允许较长时间无日志。

---

# 27. 推荐目录结构

长期 AI 工程任务可以采用：

```text
project/
│
├── logs/
│   └── run.log
│
├── checkpoints/
│   └── checkpoint.json
│
├── output/
│
├── state/
│   └── progress.json
│
└── scripts/
```

这样 AI 可以通过：

```text
logs
+
checkpoint
+
progress
+
output
```

判断程序真实状态。

---

# 28. 核心规则总结

AI 必须牢记：

```text
无输出 ≠ 卡死

低CPU ≠ 卡死

高CPU ≠ 正常

进程存在 ≠ 正常

唯一可靠的方法是观察“进展”
```

判断程序健康状态的推荐优先级：

```text
1. 明确进度数据
2. checkpoint变化
3. 输出文件变化
4. CPU time变化
5. 子进程状态
6. 网络 / I/O 状态
7. stdout
```

最终原则：

> **AI 应以“是否存在可验证的有效进展”作为判断程序是否卡死的主要依据，而不是以“多久没有文本输出”作为依据。**
