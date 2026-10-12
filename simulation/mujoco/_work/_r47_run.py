# -*- coding: utf-8 -*-
import os, re, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
PY = os.path.join(HERE, "..", "..", "..", ".venv-cad", "Scripts", "python.exe")
PY = os.path.abspath(PY)
GATE = os.path.join(HERE, os.environ.get("GATE4", "_r45_gate4.py"))
OUT = os.path.abspath(os.path.join(HERE, "..", "out"))
BASE = ["--mix", "POLLEN,NECTAR,POLLEN,NECTAR", "--tray", "460",
        "--gate-x", "180", "--phases", "60", "--hold", "1", "--mu", "0.6", "--park", "188"]

def run(tag, args, base=None):
    b = list(BASE if base is None else base)
    cmd = [PY, "-X", "utf8", GATE] + b + args + ["--tag", tag]
    t0 = time.time()
    p = subprocess.run(cmd, cwd=os.path.abspath(os.path.join(HERE, "..", "..", "..")),
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    txt = (p.stdout or "") + (p.stderr or "")
    open(os.path.join(OUT, os.environ.get("LOGPFX", "_r47") + "_%s.log" % tag), "w", encoding="utf-8").write(txt)
    clears = re.findall(r"清空([\d.]+) s 扭矩峰([\d.]+) 卡滞(\d+)%", txt)
    fires = re.findall(r"-> 出膛 (\d)/(\d)", txt)
    warn = re.findall(r"\[警告\].*", txt)
    print("[%s] %5.1fs  %s  %s  %s" % (tag, time.time() - t0,
          ("清空%s/峰%s/滞%s%%" % clears[0]) if clears else "无清空行",
          ("出膛%s/%s" % fires[0]) if fires else "", warn), flush=True)
    return txt

if __name__ == "__main__":
    for spec in sys.argv[1:]:
        tag, _, rest = spec.partition("=")
        run(tag, rest.split() if rest else [])
