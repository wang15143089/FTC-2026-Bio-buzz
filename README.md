# FTC 机器人长期工程项目

本仓库用于从需求到制造发布的模块化、参数化、可追溯 FTC 机器人开发。BIOBUZZ 2026–2027 的 Requirements v0.1 与 Architecture v0.1 已批准；当前正由系统级 M0 进入 P3 HIVE 主分支的 M1 概念筛选，尚未选择具体机构或详细尺寸。

## 当前状态

- `KNOWN`：当前规则基线为 Competition Manual TU01；采用轻量化、模块化、验证优先和 Git 兼容工作流。
- `KNOWN`：已有 3209-0001-0007 Strafer 底盘；必须保持轮距、轴距和四轮布局，只允许最低限度拆分重组。
- `KNOWN`：使用 REV Control Hub + Expansion Hub 和 goBILDA 3100-0012-0020 电池；5203-2402-0051 仅作通用电机包络参考。
- `CALCULATED`：证据锚定的任务包比较以 70% 战略权重选择 P3 HIVE 为主 M1 方向、P4 为受资源关口约束的扩展；P1 是共同底座，P2 是风险回退。
- `CALCULATED`：P3-BAL-0.1 已建立参数化弹道窗口；当前台架优先比较 C06-B 对置双飞轮与 C06-A 单飞轮曲面压板，尚未冻结最终发射机构。
- `TBD`：最终任务组合、性能目标、机构电机选型、时间表和预算。
- 详细恢复点见 `PROJECT_STATUS.md`。

## 目录

```text
/
├── AGENTS.md                  # 长期协作与恢复规则
├── README.md                  # 项目入口
├── PROJECT_STATUS.md          # 当前检查点
├── docs/                      # 需求、架构、接口、验证和决策记录
├── config/parameters.yaml     # 全局工程参数主源
├── cad/common/                # 可复用低细节零件/基准
├── cad/modules/               # 可独立生成的模块 CAD
├── calculations/              # 可复算的工程计算
├── simulation/                # 轻量模型与仿真配置
├── scripts/                   # 构建、导出和检查脚本
├── tests/                     # 参数、CAD 和集成检查
├── references/                # 已核验规则/供应商资料索引
└── exports/{step,stl,drawings}/ # 制造与交换输出
```

Codex 环境自带的 `work/` 用于临时分析，`outputs/` 只用于向用户交付文件；二者不属于正式工程架构。正式可追溯产物存放在上述项目目录中。

## 工作方式

开始会话：读 `AGENTS.md` → 读 `PROJECT_STATUS.md` → 查 Git → 查当前模块文件。结束会话：完成相称验证 → 更新文档和状态 → 在验证里程碑处准备提交。

任何 `TBD` 参数不得在 CAD 或计算中以未记录的“临时数值”替代。
