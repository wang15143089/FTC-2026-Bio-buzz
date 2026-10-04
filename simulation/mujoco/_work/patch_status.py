import io
p = "PROJECT_STATUS.md"
s = io.open(p, encoding="utf-8").read()
a1 = "- 待验证（TBD）：V2 是否真能把球送进 52° 夹口并被对置双飞轮发射，尚无 MuJoCo 全流程仿真结论。"
assert a1 in s
sec = io.open("simulation/mujoco/_work/newsec.md", encoding="utf-8").read().strip()
s = s.replace(a1, "- 待验证（TBD）：V2 是否真能把球送进 52° 夹口并被对置双飞轮发射 → 已由本轮全流程仿真关闭，见下节。\n\n" + sec)
lines = s.split("\n")
for i, ln in enumerate(lines):
    if ln.startswith("1. （立即）对 `C06B-POLLEN-FEEDER-V2` 跑 MuJoCo"):
        lines[i] = io.open("simulation/mujoco/_work/newaction.md", encoding="utf-8").read().strip()
        break
else:
    raise SystemExit("action anchor missing")
io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("PROJECT_STATUS updated")
