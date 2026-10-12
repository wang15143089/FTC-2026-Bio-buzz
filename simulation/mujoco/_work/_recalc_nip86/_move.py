import pathlib, shutil
W = pathlib.Path("simulation/mujoco/_work")
D = W / "_recalc_nip86"
D.mkdir(exist_ok=True)
for n in ("_r38_gapcal.py","_r38_limit.py","_r38_cmp86.py","_r38_cmp86b.py","_r38_where.py","_r38_travel.py","_r38_zoom.py"):
    p = W / n
    if p.exists():
        shutil.move(str(p), str(D / n))
print("moved:", sorted(x.name for x in D.iterdir()))
print("_work 下 r38 活动脚本:", sorted(x.name for x in W.glob("r38_v*.py")))
