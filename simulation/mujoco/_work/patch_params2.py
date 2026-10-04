# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

p = Path("config/parameters.yaml")
txt = p.read_text(encoding="utf-8")
if "contact_geom_threshold_by_option" in txt:
    print("已存在，跳过"); raise SystemExit

anchor = '    servo_direct_drive_feasible: {value: false,'
i = txt.index(anchor)
j = txt.index("\n", i) + 1

new = '''    # --- 2026-10-03 接触几何方案逐个仿真（现场复跑确认，逐字一致） ---
    contact_geom_threshold_by_option: {value: {"V0_current": 0.94, "A_lip_flare": 0.72, "B_tray_recess": 0.94, "C_blade_tip_unload": 1.25, "D_rest_pad_6p8": 0.68, "A+B": 0.72, "A+D": 0.64}, unit: "N*m", status: "SIMULATED", source: "200 rpm, tray feed x=145, bisection 0.05 N*m; simulation/mujoco/out/summary_v2_rerun_opts.json"}
    contact_geom_option_verdict: {value: {"A_lip_flare": "effective -23%", "B_tray_recess": "no effect 0%", "C_blade_tip_unload": "worse +33%", "D_rest_pad_6p8": "effective -28%", "A+D": "lowest 0.64 but robustness 1/2"}, status: "SIMULATED", source: "simulation/mujoco/out/summary_v2_options_final.json"}
    contact_geom_option_A_definition: {value: "delete shell_lip_face (225 deg wall); add 3 box segments at 227.5/231.5/235.5 deg with r_in 95.5/99.5/103.5 mm", status: "SIMULATED", source: "simulation/mujoco/_work/opt_lib.py flare()"}
    contact_geom_option_B_definition: {value: "tray end recessed from x=-56 to x=-12 mm", status: "SIMULATED", source: "simulation/mujoco/_work/opt_lib.py tray_recess()"}
    contact_geom_option_C_definition: {value: "blade outer radius reduced 62 to 56 mm (negative result, do not adopt)", status: "SIMULATED", source: "simulation/mujoco/_work/opt_lib.py blade_low()"}
    contact_geom_option_D_definition: {value: "rest pad raising ball centre 6.8 mm above tray top at x=-2 mm", status: "SIMULATED", source: "simulation/mujoco/_work/opt_lib.py pad()"}
    paddle_finger_phase_threshold: {value: {"P0_three_342_222_102_current": 0.94, "P1_three_240_120_0": 0.99, "P2_three_154_34_274": 1.03, "R1_two_350_170": 0.55, "R2_two_350_170_A": 0.46, "R3_two_350_170_A_D": 0.42, "R4_three_current_A_D": 0.64, "R5_two_350_170_D": 0.42}, unit: "N*m", status: "SIMULATED", source: "simulation/mujoco/out/summary_v2_phase.json; summary_v2_best.json"}
    paddle_rpm_min_best_combo: {value: 90.0, unit: "rpm", status: "SIMULATED", source: "R2/R3/R5 launch at 90/105/120 rpm and fail at 75 rpm; summary_v2_best.json"}
    best_combo_recommended: {value: "R2 two fingers theta=350/170 + A lip flare (optionally + D 6.8 mm rest pad)", status: "SIMULATED", source: "simulation/mujoco/out/summary_v2_best.json"}
    best_combo_servo_margin: {value: "boundary-feasible, must be bench-verified; a single SRS V2 cannot be declared safe", status: "SIMULATED", source: "SRS V2 UltraSpeed 7.4 V linear model gives 0.416 N*m at 90 rpm vs requirement 0.42-0.46 N*m"}
    feeder_rest_position_diagnosis: {value: "ball never reaches lip: stops on blade tip plane at r=95.5 mm (theta=329.6 deg) while design carry radius is 58.4 mm, so feeding relies on tip drag not on the carry track", status: "SIMULATED", source: "simulation/mujoco/out/summary_v2_options_final.json geom rest_r_mm"}
    feeder_friction_sensitivity: {value: {"mu_ball_1.0": 0.94, "mu_ball_0.7": 1.16, "mu_ball_0.5": ">1.6 no launch", "mu_ball_0.35": ">1.6 no launch", "mu_shell_0.10": "no effect"}, unit: "N*m", status: "SIMULATED", source: "summary_v2_options_final.json friction; ball geom priority=1 overrides the shell friction setting"}
'''
txt = txt[:j] + new + txt[j:]
p.write_text(txt, encoding="utf-8")
print("parameters.yaml 已补充接触几何条目")
