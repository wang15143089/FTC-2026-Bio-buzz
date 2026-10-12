# -*- coding: utf-8 -*-
"""R36 结果清洗：把 `out/_r36_multiball.json` 里的"出膛"逐颗分类。

背景（教训，见 DEC-0033）：原判定只看位置越界，球被甩出机构后落在脚本自加的
`catch_floor` 上滚到 x ~ 488 mm 也会被记成"出膛"（实测 v = 0.32 / 0.62 m/s）。
因此任何"成功率"必须先按速度过滤。

分类规则（显式、可复算）：
  REAL  : v >= 3.0 m/s 且 x < 200 mm   —— 真正被飞轮打出去（v 实测 6.0~6.3）
  BOGUS : v <  1.0 m/s 且 x > 300 mm   —— 被甩出后在地板上滚（假阳性）
  SPILL : 其余                        —— 逸出/掉出机构
用法： python r36_recheck.py
"""
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
OUT = Path("simulation/mujoco/out")
SRC, DST = OUT / "_r36_multiball.json", OUT / "_r36_multiball_recheck.json"


def classify(e):
    if e is None:
        return "SPILL"
    if e["v"] >= 3.0 and e["x"] < 200.0:
        return "REAL"
    if e["v"] < 1.0 and e["x"] > 300.0:
        return "BOGUS"
    return "SPILL"


def main():
    rows = json.loads(SRC.read_text(encoding="utf-8"))
    out = []
    tot = dict(REAL=0, BOGUS=0, SPILL=0)
    nball = 0
    for r in rows:
        cls = [classify(e) for e in r["exit"]]
        nball += len(cls)
        for c in cls:
            tot[c] += 1
        reals = [e for e, c in zip(r["exit"], cls) if c == "REAL"]
        rec = dict(mix=r["mix"], ph0=r["ph0"], nip=r["nip"], hold=r["hold"],
                   stacked=r["stacked"], in_channel=r["in_channel"],
                   cls=cls,
                   n_real=cls.count("REAL"),
                   v_real=[round(e["v"], 2) for e in reals],
                   t_real=[round(e["t"], 2) for e in reals],
                   cyc_real=[round(e["cyc_t"], 2) for e in reals],
                   n_bogus=cls.count("BOGUS"), n_spill=cls.count("SPILL"),
                   tq_peak=r["tq_peak"], jam_frac=r["jam_frac"])
        out.append(rec)
        print("ph0=%3.0f  %s  真出膛 %d/%d  v=%s  假阳性 %d  逸出 %d  扭矩 %.3f  卡滞 %.0f%%"
              % (r["ph0"], ">".join(r["mix"]), rec["n_real"], len(cls),
                 rec["v_real"] or "--", rec["n_bogus"], rec["n_spill"],
                 r["tq_peak"], 100 * r["jam_frac"]), flush=True)
    print("\n合计 %d 颗：真出膛 %d / 假阳性 %d / 逸出 %d" % (nball, tot["REAL"], tot["BOGUS"], tot["SPILL"]))
    vv = [v for r in out for v in r["v_real"]]
    cc = [c for r in out for c in r["cyc_real"]]
    if vv:
        print("真出膛速度 %.2f~%.2f m/s（均值 %.2f）；轮内耗时 %.2f~%.2f s（均值 %.2f）"
              % (min(vv), max(vv), sum(vv) / len(vv), min(cc), max(cc), sum(cc) / len(cc)))
    DST.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("saved", DST)


if __name__ == "__main__":
    raise SystemExit(main())
