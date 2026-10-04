import io
p = "config/parameters.yaml"
s = io.open(p, encoding="utf-8").read()
old = '''  open_question: {value: "Whether the V2 feeder can actually deliver the ball from the tray, past the lip wedge and into the 52 deg flywheel nip has not been simulated yet; a MuJoCo full-flow run is the next action.", status: "TBD", source: "PROJECT_STATUS.md NEXT ACTION"}'''
new = '''  simulation_full_flow:
    status: "SIMULATED"
    source: "simulation/mujoco/pollen_v2_sim.py; simulation/mujoco/out/FINDINGS_v2_zh.md"
    tool: {value: "MuJoCo 3.14.0, timestep 2e-4 s, implicitfast, shell approximated by 24 chained boxes", status: "SIMULATED"}
    full_flow_result: {value: "pass", status: "SIMULATED", source: "tray feed -> blade pickup -> 99 deg wall carry -> 142 deg tangential release -> 52 deg channel -> 52 deg opposed flywheel nip -> launch"}
    channel_entry_offset_from_centreline: {value: 4.0, unit: "mm", status: "SIMULATED", source: "simulation/mujoco/out/FINDINGS_v2_zh.md"}
    exit_speed_by_flywheel_rpm: {value: {810: 3.60, 1620: 6.53, 2430: 8.67}, unit: "m/s", status: "SIMULATED"}
    exit_angle_by_flywheel_rpm: {value: {810: 50.8, 1620: 50.2, 2430: 51.0}, unit: "deg", status: "SIMULATED"}
    range_same_height_by_flywheel_rpm: {value: {810: 1.29, 1620: 4.28, 2430: 7.49}, unit: "m", status: "SIMULATED"}
    exit_speed_over_rim_speed: {value: 0.80, unit: "1", status: "SIMULATED"}
    paddle_rpm_min_from_rest: {value: 105.0, unit: "rpm", status: "SIMULATED", source: "100 rpm stalls at 182 deg; 105/110/115/200 rpm all launch"}
    paddle_rpm_min_from_tray: {value: 200.0, unit: "rpm", status: "SIMULATED", source: "140 rpm 2/8 phase sweep; 200 rpm 8/8"}
    paddle_torque_limit: {value: 1.5, unit: "N*m", status: "ASSUMED", source: "velocity actuator forcerange +/-1.5; dominant uncertainty of the paddle rpm threshold, must be replaced by the real servo torque-speed curve"}
  open_question: {value: "The V2 full flow is SIMULATED and passes. The only item still open is whether the real servo (or paddle drive) can supply the torque needed at 200 rpm (3.3 rev/s); the simulator used an ASSUMED +/-1.5 N*m forcerange and a rigid (non zip-tie) blade.", status: "TBD", source: "simulation/mujoco/out/FINDINGS_v2_zh.md section 5" }'''
assert old in s, "anchor"
s = s.replace(old, new)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("parameters.yaml updated")
