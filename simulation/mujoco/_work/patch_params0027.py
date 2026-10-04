# -*- coding: utf-8 -*-
import pathlib

p = pathlib.Path("config/parameters.yaml")
s = p.read_text(encoding="utf-8")
anchor = '    servo_recommended_for_feeder: {value: "goBILDA 25-4 Super Speed @7.4V, window up to about 122 rpm and over 40% torque margin at 90-105 rpm; avoid the 70-80 rpm notch", status: "SIMULATED", source: "simulation/mujoco/out/servo_envelope_zh.png"}\n'
assert anchor in s, "anchor not found"

add = u'''    # --- 2026-10-03 DEC-0027: R6 smooth-arc candidate; creep root-caused to the rest pocket, not the junction step ---
    r6_arc_definition: {value: "shell inner arc (r=R_IN) extended smoothly from the 225 deg lip to 260.2 deg, tangent to the tray top at x=13.5 mm z=18.87 mm (0.0 mm rise); replaces the R5 flat rest pad", status: "SIMULATED", source: "DEC-0027; simulation/mujoco/_work/r6_smooth.py"}
    r6_vs_r5_25_4_model: {value: {"R5": {"creep_s": 2.98, "carry_s": 3.72, "release_to_launch_s": 7.49, "carry_rpm": 3.95, "carry_torque_Nm": 0.523}, "R6": {"creep_s": 2.93, "carry_s": 3.66, "release_to_launch_s": 7.38, "carry_rpm": 4.05, "carry_torque_Nm": 0.523}, "R6c": {"creep_s": 2.99, "carry_s": 3.46, "release_to_launch_s": 7.23, "carry_rpm": 4.36, "carry_torque_Nm": 0.522}}, unit: "s / rpm / N*m", status: "SIMULATED", source: "DEC-0027; ball enters at tray x=145 mm, 12 s budget, flywheel 1620 rpm, paddle driven by the 25-4 linear T-n model (kv=0.017452, forcerange +-0.530, ctrl=290 rpm); simulation/mujoco/out/r5_vs_r6_smooth_zh.png"}
    r6_verdict_vs_r5: {value: "smooth arc does NOT remove the creep; R6 is 0.11 s (1.5%) faster end-to-end, R6c 0.26 s (3.5%); all three launched on the first try, so there is no failure case to separate them", status: "SIMULATED", source: "DEC-0027"}
    creep_root_cause: {value: "the ball parks at r about 83-95 mm / angle about 322-329 deg and wedges the paddle to a few rpm until the wedge releases; the shell-to-pad junction step takes no part in that phase, so changing it cannot help", status: "SIMULATED", source: "DEC-0027; simulation/mujoco/_work/r7_loadprobe2.py"}
    carry_load_stiff_source_probe: {value: {"kv": 0.08, "ctrl_rpm": 145.0, "forcerange_Nm": 5.0, "carry_rpm": 6.8, "carry_torque_Nm": 1.16, "ball_r_mm": [59.3, 60.5]}, status: "SIMULATED", source: "DEC-0027; friction-regularisation sensitive, order-of-magnitude only, do NOT use as a selection number"}
    carry_margin_open_item: {value: "at full-throttle 25-4 the carry stage runs at about 4 rpm and 0.523 N*m against a 0.530 N*m stall, i.e. a very thin margin; DEC-0026 thresholds used a kv=0.08 dummy actuator and are a different metric, so the servo margin must be re-checked with a real motor model before it is called closed", status: "TBD", source: "DEC-0027"}
    next_fix_direction: {value: "re-shape the REST POCKET so the ball parks clear of the blade sweep (or raise servo torque); junction-shape work is ruled out", status: "TBD", source: "DEC-0027"}
'''
s = s.replace(anchor, anchor + add, 1)

# update the open_question to point at the new item
old_q = '  open_question: {value: "DEC-0026 reopened and closed the servo question as FEASIBLE. Remaining open items:'
new_q = '  open_question: {value: "DEC-0027 supersedes the creep explanation: the creep is a rest-pocket jam, not the junction step, and the R6 smooth arc is only 1.5% faster. The servo margin (DEC-0026) was measured with a kv=0.08 dummy actuator and must be re-checked with a real motor model - at full throttle the 25-4 sits at 0.523 of 0.530 N*m stall during the carry. Remaining open items:'
assert old_q in s
s = s.replace(old_q, new_q, 1)
p.write_text(s, encoding="utf-8")
print("parameters.yaml updated")
