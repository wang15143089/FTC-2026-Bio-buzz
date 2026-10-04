# -*- coding: utf-8 -*-
"""Patch T06 feeder records for the 12 s-budget threshold correction (DEC-0026). v2 - exact indent match."""
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path("config/parameters.yaml")
L = P.read_text(encoding="utf-8").splitlines(True)
log = []
def repl(prefix, new):
    for i, s in enumerate(L):
        if s.startswith(prefix):
            log.append("OK   " + prefix.strip()[:44]); L[i] = new; return
    log.append("MISS " + prefix.strip()[:44])

repl('    paddle_rpm_min_from_rest:',
     '    paddle_rpm_min_from_rest: {value: 105.0, unit: "rpm", status: "SUPERSEDED", source: "old 7 s-budget single-entry scan, superseded by DEC-0026 / paddle_torque_threshold_12s_by_rpm"}\n')
repl('    paddle_rpm_min_from_tray:',
     '    paddle_rpm_min_from_tray: {value: 200.0, unit: "rpm", status: "SUPERSEDED", source: "old 7 s-budget phase sweep, superseded by DEC-0026"}\n')
repl('    paddle_torque_threshold:',
     '    paddle_torque_threshold: {value: 1.0, unit: "N*m", status: "SUPERSEDED", source: "old 7 s-budget capped-torque scan; contained a feed-time artefact, superseded by DEC-0026 / paddle_torque_threshold_12s_by_rpm"}\n')
repl('    servo_direct_drive_feasible:',
     '    servo_direct_drive_feasible: {value: false, status: "SUPERSEDED", source: "old judgement from the 7 s-budget threshold 1.0 N*m at >=105 rpm; overturned by DEC-0026 / servo_candidates_gobilda_7p4V"}\n')
repl('    contact_geom_threshold_by_option:',
     '    contact_geom_threshold_by_option: {value: {"V0_current": 0.94, "A_lip_flare": 0.72, "B_tray_recess": 0.94, "C_blade_tip_unload": 1.25, "D_rest_pad_6p8": 0.68, "A+B": 0.72, "A+D": 0.64}, unit: "N*m", status: "SUPERSEDED", source: "7 s budget, 200 rpm, single entry x=145, bisection 0.05 N*m; relative ranking A/C/D still valid, absolute values superseded by DEC-0026"}\n')
repl('    paddle_finger_phase_threshold:',
     '    paddle_finger_phase_threshold: {value: {"P0_three_342_222_102_current": 0.94, "P1_three_240_120_0": 0.99, "P2_three_154_34_274": 1.03, "R1_two_350_170": 0.55, "R2_two_350_170_A": 0.46, "R3_two_350_170_A_D": 0.42, "R4_three_current_A_D": 0.64, "R5_two_350_170_D": 0.42}, unit: "N*m", status: "SUPERSEDED", source: "7 s budget, bisection 0.05 N*m; ranking still valid, absolute values superseded by DEC-0026"}\n')
repl('    paddle_rpm_min_best_combo:',
     '    paddle_rpm_min_best_combo: {value: 40.0, unit: "rpm", status: "SIMULATED", source: "DEC-0026: with a 12 s run budget R5 launches at every sampled speed from 40 to 290 rpm; the earlier 90 rpm figure came from the 7 s budget"}\n')
repl('    best_combo_recommended:',
     '    best_combo_recommended: {value: "R5 two fingers theta=350/170 + D 6.8 mm rest pad (single flat block, no new flare part)", status: "SIMULATED", source: "DEC-0026; R2 needs an extra three-segment flare and is not preferred"}\n')
repl('    best_combo_servo_margin:',
     '    best_combo_servo_margin: {value: "feasible with margin, servo selection now open; must still be bench-verified", status: "SIMULATED", source: "DEC-0026; see servo_candidates_gobilda_7p4V and simulation/mujoco/out/servo_envelope_zh.png"}\n')
repl('  open_question: {value: "Servo torque question is now CLOSED',
     '  open_question: {value: "DEC-0026 reopened and closed the servo question as FEASIBLE. Remaining open items: (1) the feed is phase-sensitive - the ball can creep in the rest pocket for several seconds before a finger grabs it, so the paddle speed must be held inside the drive window and the phase/geometry fix is not yet designed; (2) R5 geometry (two fingers 350/170 + 6.8 mm rest pad) is not yet in CAD; (3) the rigid (non zip-tie) blade and the ASSUMED 0.060 kg ball mass remain open.", status: "TBD"}\n')

NEW = [
    '    # --- 2026-10-03 DEC-0026: 12 s unified run budget; the old 7 s numbers contained a feed-time artefact ---\n',
    '    paddle_torque_threshold_12s_by_rpm: {value: {"40": 0.24, "50": 0.24, "60": 0.339, "75": 0.439, "90": 0.24, "105": 0.24, "120": 0.289, "130": 0.356, "145": 0.472, "160": 0.323, "200": 0.273, "290": 0.306}, unit: "N*m", status: "SIMULATED", source: "R5 (two fingers 350/170 + D pad), dual tray entry x=145 and x=138, bisection tol 0.03 N*m, 12 s run budget; 0.24 is the scan lower bound so the true value is <= 0.24; simulation/mujoco/out/_r2r5_speed_req12.json"}\n',
    '    paddle_torque_threshold_budget_sensitivity: {value: {"7 s": "30/40/60/70/75/145 rpm fail even at 3.0 N*m", "12 s": "all of those speeds launch, threshold 0.24-0.47 N*m"}, status: "SIMULATED", source: "the 7 s failures are the ball creeping in the rest pocket for seconds before a finger grabs it, not a torque limit; simulation/mujoco/_work/diag_lowrpm.py"}\n',
    '    feed_phase_sensitivity: {value: "outcome depends on paddle rpm through the finger-vs-ball arrival phase; adjacent 10 rpm can flip it; first-launch time ranges 0.6 s (40/50 rpm) to about 4.2 s (70 rpm)", status: "SIMULATED", source: "simulation/mujoco/_work/r5_lowrpm.py, _work/diag_lowrpm.py"}\n',
    '    feeder_rest_radius_shortfall: {value: 37.1, unit: "mm", status: "SIMULATED", source: "ball rests at r about 95.5 mm while the design carry radius is 58.4 mm; feeding relies on tip drag, not on the carry track (DEC-0025 root cause, unchanged)"}\n',
    '    servo_candidates_gobilda_7p4V: {value: {"25-4_Super_Speed": {"stall_Nm": 0.530, "no_load_rpm": 290.0, "drive_window_rpm": [[30, 70], [80, 122]], "verdict": "usable, highest achievable paddle speed"}, "25-3_Speed": {"stall_Nm": 1.059, "no_load_rpm": 145.0, "drive_window_rpm": [[30, 110]], "verdict": "usable"}, "Axon_MAX_MK2": {"stall_Nm": 3.825, "no_load_rpm": 100.0, "drive_window_rpm": [[30, 94]], "verdict": "usable, largest low-speed margin"}, "25-2_Torque": {"stall_Nm": 2.471, "no_load_rpm": 60.0, "drive_window_rpm": [[30, 53]], "verdict": "usable but slow, cycle about 1.2 s per ball"}, "25-2_5_Turn_Torque": {"stall_Nm": 2.471, "no_load_rpm": 60.0, "drive_window_rpm": [[30, 53]], "verdict": "same spec as 25-2 Torque"}}, status: "SIMULATED", source: "simulation/mujoco/out/servo_envelope_zh.png; torque-speed line from stall to no-load; vendor torques are stall values (1 kg*cm = 0.0980665 N*m)"}\n',
    '    servo_reference_rev_srs_v2_ultraspeed: {value: {"stall_Nm": 0.608, "no_load_rpm": 285.7, "drive_window_rpm": [[30, 125]], "verdict": "also usable under the 12 s budget, previously mis-judged as boundary-infeasible"}, status: "SIMULATED", source: "DEC-0026; REV SRS V2 UltraSpeed 7.4 V linear envelope"}\n',
    '    servo_recommended_for_feeder: {value: "goBILDA 25-4 Super Speed @7.4V, window up to about 122 rpm and over 40% torque margin at 90-105 rpm; avoid the 70-80 rpm notch", status: "SIMULATED", source: "simulation/mujoco/out/servo_envelope_zh.png"}\n',
]
idx = next(i for i, s in enumerate(L) if s.startswith("  open_question: {value:"))
L[idx:idx] = NEW
P.write_text("".join(L), encoding="utf-8")
print("\n".join(log)); print("inserted", len(NEW), "lines at line", idx + 1)