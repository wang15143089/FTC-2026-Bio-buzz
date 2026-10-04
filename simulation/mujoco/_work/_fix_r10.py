from pathlib import Path
p = Path("simulation/mujoco/_work/r10_cradle.py")
t = p.read_text(encoding="utf-8")
n = t.count("r6.th2((350.0, 170.0))()")
assert n == 2, n
t = t.replace("r6.th2((350.0, 170.0))()", "r6.th2((350.0, 170.0))")
p.write_text(t, encoding="utf-8")
print("patched", n)
