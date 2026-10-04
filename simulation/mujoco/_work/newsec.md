## T06 POLLEN 送球段 V2 全流程仿真（2026-10-03）

- 用户指令（KNOWN）：好，跑新版全流程仿真吧。
- 方法（SIMULATED）：新增 `simulation/mujoco/pollen_v2_sim.py`（几何常量取自 `cad/paddle_launcher_feeder_redesign.py` 与 V2 报告，不依赖 CadQuery）；MuJoCo 3.14.0，timestep 2e-4 s，implicitfast，外罩以 24 段 box 链近似曲面。
- 结论（SIMULATED）：**V2 几何具备完整送球—发射能力**。球从托板右端滚入 → 叶片在 x ≈ 113 mm 接球 → 沿内壁 241° → 142°（约 99°）→ 142° 切向出罩（球心距 52° 通道中线 ≈ 4 mm）→ 进夹口 → 出射 **6.53 m/s @ 50.2°**，同高度射程 **4.28 m**（飞轮 1620 rpm，拨杆 200 rpm）。旧几何的 52° 顶板卡点未复现。
- 发射阶梯（SIMULATED）：810 / 1620 / 2430 rpm → 3.60 / 6.53 / 8.67 m/s，射程 1.29 / 4.28 / 7.49 m；出口速度/轮缘线速度 = 0.80，与 V1 的 `FINDINGS_zh.md` 一致 → V2 未损失发射性能。
- 拨杆转速门槛（SIMULATED，本轮关键新发现）：球已在唇口停位时 ≥ 105 rpm（100 rpm 卡在 182°）；球从托板进料时 140 rpm 仅 2/8 成功、**200 rpm 8/8 成功** → **推荐拨杆 ≥ 200 rpm（3.3 rev/s）**。
- 风险（ASSUMED，必须关闭）：拨杆力矩用 forcerange ±1.5 N·m 的速度执行器近似，是转速门槛结论的最大不确定来源；叶片按刚体建模，未含 zip-tie 弹性。舵机在 200 rpm 处的可用扭矩未经确认前，不得把送球可靠性写入制造结论。
- 产物（KNOWN）：`simulation/mujoco/out/FINDINGS_v2_zh.md`、`v2_fullflow_zh.png`、`v2_flywheel_ladder_zh.png`、`trace_v2_*.json`、`summary_v2_*.json`。父级 CAD 与既有导出均未改动。
