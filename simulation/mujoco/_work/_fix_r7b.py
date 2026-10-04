# -*- coding: utf-8 -*-
import pathlib
p = pathlib.Path("simulation/mujoco/_work/r7_loadprobe2.py")
s = p.read_text(encoding="utf-8")
s = s.replace("import opt_lib as ol\n", "import r6_smooth as r6\nimport opt_lib as ol\n", 1)
p.write_text(s, encoding="utf-8")
print("ok")
