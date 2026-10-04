import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.font_manager as fm
names={f.name for f in fm.fontManager.ttflist}
for c in ("Microsoft YaHei","SimHei","Noto Sans CJK SC","Source Han Sans SC","DejaVu Sans"):
    if c in names: print("font ok:",c); break
print("has YaHei:", "Microsoft YaHei" in names, " has SimHei:", "SimHei" in names)
