import pathlib
p = pathlib.Path("simulation/mujoco/_work/r38_v7.py"); s = p.read_text(encoding="utf-8")
s = s.replace("        mujoco.mj_setConst(m, d)\n", "        # 注意: 切勿在运行中调用 mj_setConst, 会把 d.qpos 清零\n")
p.write_text(s, encoding="utf-8")
print("setConst removed:", "mj_setConst" not in s)
