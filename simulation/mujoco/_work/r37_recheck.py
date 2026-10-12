# -*- coding: utf-8 -*-
"""R37 结果清洗：把 out/_r37_multiball_*.json 的"出膛"逐颗分类 + 队列纪律分析。

判定沿用 DEC-0033（R36 教训）：只看位置越界会把被甩到地板上滚的球记成出膛。
  REAL  : v >= 3.0 m/s 且 x < 200 mm
  BOGUS : v <  1.0 m/s 且 x > 300 mm
  SPILL : 其余
队列纪律（新增）：球在"轮到自己之前"是否被拨杆/邻球推开 —— 用 0.05 s 采样的
轨迹算每颗球在自己出膛前的累计行程 travel_mm（> 10 mm 记为"等待期被动"）。
用法: python simulation/mujoco/_work/r37_recheck.py
"""
import json, math, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
OUT = Path("simulation/mujoco/out")
DST = OUT / "_r37_recheck.json"


def classify(e):
    if e is None:
        return "SPILL"
    if e["v"] >= 3.0 and e["x"] < 200.0:
        return "REAL"
    if e["v"] < 1.0 and e["x"] > 300.0:
        return "BOGUS"
    return "SPILL"


def travel_before(tr, t_launch, x0=None, z0=None):
    """出膛前累计行程 (mm)；x0/z0 给定则从该点起算。"""
    pts = [q for q in tr if q["t"] <= (t_launch if t_launch else 1e9)]
    if not pts:
        return 0.0, None
    d = 0.0
    prev = (x0, z0) if x0 is not None else (pts[0]["x"], pts[0]["z"])
    for q in pts:
        d += math.hypot(q["x"] - prev[0], q["z"] - prev[1])
        prev = (q["x"], q["z"])
    return d, prev


def main():
    out = []
    tot = dict(REAL=0, BOGUS=0, SPILL=0)
    nball = 0
    for src in sorted(OUT.glob("_r37_multiball_*.json")):
        rows = json.loads(src.read_text(encoding="utf-8"))
        for r in rows:
            cls = [classify(e) for e in r["exit"]]
            nball += len(cls)
            for c in cls:
                tot[c] += 1
            settle = {i: q for i, q in enumerate(r.get("settled", []))}
            balls = []
            for k, e in enumerate(r["exit"]):
                tr = r["trace"][k]
                s = settle.get(k)
                d, last = travel_before(tr, e["t"] if e else None,
                                        s[0] if s else None, s[1] if s else None)
                cyc = e["cyc"] if e else None
                balls.append(dict(k=k + 1, cls=cls[k], v=(e["v"] if e else None),
                                  t=(e["t"] if e else None),
                                  cyc_t=round(e["cyc_t"], 2) if e else None,
                                  cyc=cyc, travel_mm=round(d, 1),
                                  moved_while_waiting=bool(d > 10.0)))
            reals = [b for b in balls if b["cls"] == "REAL"]
            pitch = ([round(balls[j + 1]["cyc"] - balls[j]["cyc"], 2)
                      for j in range(len(balls) - 1)
                      if balls[j]["cyc"] is not None and balls[j + 1]["cyc"] is not None]
                     if all(b["cyc"] is not None for b in balls) else None)
            out.append(dict(tag=src.stem.replace("_r37_multiball_", ""),
                            mix=r["mix"], ph0=r["ph0"], nip=r["nip"],
                            stacked=r["stacked"], in_channel=r["in_channel"],
                            settled=r.get("settled"), balls=balls,
                            n_real=len(reals), n_ball=len(balls),
                            v_real=[b["v"] for b in reals],
                            cyc_real=[b["cyc_t"] for b in reals],
                            index_pitch_rev=pitch,
                            t_total_s=r.get("t_total_s"),
                            tq_peak=r["tq_peak"], jam_frac=r["jam_frac"]))
    print("%-9s %-5s %s" % ("tag", "ph0", "每颗：真出膛/轮内耗时/等待期行程"))
    for rec in out:
        print("%-9s %5.0f  真出膛 %d/%d  v=%s  等待期行程 %s mm  叠放 %d  扭矩 %.3f 卡滞 %.0f%%"
              % (rec["tag"], rec["ph0"], rec["n_real"], rec["n_ball"],
                 [round(v, 2) for v in rec["v_real"]] or "--",
                 [b["travel_mm"] for b in rec["balls"]], rec["stacked"],
                 rec["tq_peak"], 100 * rec["jam_frac"]))
    trues = [b for rec in out for b in rec["balls"] if b["cls"] == "REAL"]
    print("\n合计 %d 颗（%d 轮）：真出膛 %d / 假阳性 %d / 逸出 %d  = %.0f%%"
          % (nball, len(out), tot["REAL"], tot["BOGUS"], tot["SPILL"],
             100.0 * tot["REAL"] / nball))
    if trues:
        vv = [b["v"] for b in trues]
        cc = [b["cyc_t"] for b in trues]
        print("真出膛速度 %.2f~%.2f m/s（均值 %.2f）；轮内耗时 %.2f~%.2f s（均值 %.2f）"
              % (min(vv), max(vv), sum(vv) / len(vv),
                 min(cc), max(cc), sum(cc) / len(cc)))
    wait = [b for rec in out for b in rec["balls"] if b["cls"] == "REAL"
            and b["k"] > 1]
    if wait:
        print("等待球（非第一颗，真出膛计 %d 颗）等待期行程 均值 %.1f mm，最大 %.1f mm"
              % (len(wait), sum(b["travel_mm"] for b in wait) / len(wait),
                 max(b["travel_mm"] for b in wait)))
    for tag in sorted({r["tag"] for r in out}):
        sub = [r for r in out if r["tag"] == tag]
        n = sum(r["n_ball"] for r in sub)
        ok = sum(r["n_real"] for r in sub)
        best = [r["ph0"] for r in sub if r["n_real"] == r["n_ball"]]
        print("  %-9s %-30s 真出膛 %2d/%2d = %3.0f%%  全清相位 %s"
              % (tag, ">".join(sub[0]["mix"]), ok, n, 100.0 * ok / n,
                 [int(p) for p in best] or "无"))
    DST.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("saved", DST)


if __name__ == "__main__":
    raise SystemExit(main())
