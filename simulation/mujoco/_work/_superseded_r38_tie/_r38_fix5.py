import pathlib
p = pathlib.Path("simulation/mujoco/_work/r38_v5.py")
s = p.read_text(encoding="utf-8")
s = s.replace("m.joint_springref[s] = b + off_mm * 0.001", "m.qpos_spring[s] = b + off_mm * 0.001")
p.write_text(s, encoding="utf-8")
print("patched", "qpos_spring" in s)
