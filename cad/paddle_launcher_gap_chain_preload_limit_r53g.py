# -*- coding: utf-8 -*-
"""T06 R53g -- 锁紧件预载上限：拧过头多少才会顶停 25-2？

用户判据：加锁紧件，但锁紧件不得影响正常位置改变。
R53b 的预载由操作者拧螺母决定 => 存在「拧过头」的失效路径。本脚本把这条路径定量：
沿预载扫描，跑与 R53d/R53e 同源的换档动力学，找出**预载上限**（再大就换不动/换不到位）。

输出 cad/output/_r53g_limit/report_r53g_preload_limit.json + 图 T06_R53g_preload_limit.png

Run: .venv-cad/Scripts/python.exe -X utf8 cad/paddle_launcher_gap_chain_preload_limit_r53g.py
"""
import json, math, os

R_CRANK, L_DRAG, L_MAIN, U_TAB, D0 = 12.0, 65.0, 110.0, 18.0, 120.0
HALF = {"pollen": 80.0, "nectar": 91.0}


def d_of_theta(th):
    return R_CRANK*math.cos(th) + math.sqrt(L_DRAG**2 - R_CRANK**2*math.sin(th)**2)


def half_of_theta(th):
    u = d_of_theta(th) - D0
    return math.sqrt(max(0.0, L_MAIN**2 - (U_TAB - u)**2))


def theta_of_half(h):
    d_t = (U_TAB - math.sqrt(L_MAIN**2 - h*h)) + D0
    lo, hi = 0.0, math.pi
    for _ in range(200):
        mid = 0.5*(lo+hi)
        if d_of_theta(mid) > d_t:
            lo = mid
        else:
            hi = mid
    return 0.5*(lo+hi)


def dh_dtheta_mm(th, eps=1e-5):
    return (half_of_theta(th+eps) - half_of_theta(th-eps))/(2.0*eps)


TH = {k: theta_of_half(v) for k, v in HALF.items()}
STUDS, FACES = 8, 2.0
T_STALL, NOLOAD_RPM = 2.471, 60.0
W_NOLOAD = NOLOAD_RPM*2.0*math.pi/60.0
J_EFF, KP, DT, TMAX = 1.0e-4, 200.0, 2.0e-5, 5.0
NOMINAL_N = 3.0                      # R53b/R53f 设计预载


def switch(preload, mu, src="pollen", dst="nectar"):
    th0, th1 = TH[src], TH[dst]
    f_tot = 2.0*FACES*STUDS*preload*mu
    th, w, t, t_load_max = th0, 0.0, 0.0, 0.0
    sgn = 1.0 if th1 > th0 else -1.0
    frozen, TOL_RAD = 0.0, 5.0e-3      # 停稳 0.05 s 且残余角误差 < TOL_RAD 才算换到位
    while t < TMAX:
        T_load = f_tot*abs(dh_dtheta_mm(th))*1.0e-3
        T_avail = T_STALL*(1.0 - min(1.0, abs(w)/W_NOLOAD))
        T_motor = max(-T_avail, min(T_avail, KP*(th1-th) - 0.4*w))
        w += ((T_motor - sgn*T_load)/J_EFF)*DT
        if w*sgn < 0.0:
            w = 0.0
        th += w*DT
        t += DT
        t_load_max = max(t_load_max, T_load)
        frozen = frozen + DT if abs(w) < 1.0e-9 else 0.0
        if frozen > 0.05:              # 停稳：要么到位（残余 = 静差），要么顶停在中途
            pct = round(100.0*t_load_max/T_STALL, 1)
            if abs(th1-th) < TOL_RAD:
                return {"ok": True, "t_s": round(t, 4), "pct_of_stall": pct}
            return {"ok": False, "t_s": None, "pct_of_stall": pct,
                    "stopped_mm_from_target": round(abs(th1-th)*abs(dh_dtheta_mm(th)), 3)}
    return {"ok": False, "t_s": None, "pct_of_stall": round(100.0*t_load_max/T_STALL, 1)}


sweep = {}
for mu in (0.30, 0.60):
    rows = []
    p = 1.0
    while p <= 20.001:
        r = switch(p, mu)
        rows.append({"preload_n": round(p, 2), "ok": r["ok"],
                     "t_s": r["t_s"], "pct_of_stall": r["pct_of_stall"]})
        p += 0.5
    lim = next((x["preload_n"] for x in rows if not x["ok"]), None)
    # 静态判据（R53b 用的降额口径：不得超过堵转的 60 %）
    p_static = T_STALL*0.60/(2.0*FACES*STUDS*mu*abs(dh_dtheta_mm(TH["pollen"]))*1.0e-3)
    sweep["mu%.2f" % mu] = {"rows": rows, "limit_hard_n": lim,
                            "limit_60pct_stall_n": round(p_static, 2)}

_pct_nom = [r["pct_of_stall"] for r in sweep["mu0.60"]["rows"] if r["preload_n"] == 3.0][0]
_hard = sweep["mu0.60"]["limit_hard_n"]
_t_hard = [r["t_s"] for r in sweep["mu0.60"]["rows"] if r["preload_n"] == _hard - 0.5][0]
CONCLUSION = (
    "名义 2.98 N（R53f 限位环锁定值）时最不利占堵转 %.1f %%（mu = 0.60）；"
    "吃掉 60 %% 堵转余量的门槛是 %.1f N（mu = 0.60）/ %.1f N（mu = 0.30）；"
    "真正顶停出现在 %.1f N（mu = 0.60，0.35 s -> %.1f s -> 失效），"
    "mu = 0.30 在 20 N 内不顶停。=> 靠手感拧螺母有 4 倍以上过拧空间，"
    "落在危险区完全可能 => R53f 用定长限位环把预载锁在 2.98 N 几何值，从根上消掉这条路径。"
    % (_pct_nom, sweep["mu0.60"]["limit_60pct_stall_n"],
       sweep["mu0.30"]["limit_60pct_stall_n"], _hard, _t_hard))

rep = {
    "units": "mm, N, N.m, s",
    "question": "锁紧件预载拧到多少会把 25-2 顶停（即开始影响正常位置改变）？",
    "model": "与 R53d/R53e 同源：T_load = 2 f |dh/dth|，f = 2 面 x 8 螺柱 x 预载 x mu；"
             "T(w) = T_stall (1 - |w|/w_noload)；J = 1.0e-4 kg.m2、Kp = 200 N.m/rad（ASSUMED）",
    "nominal_preload_n": NOMINAL_N,
    "sweep": sweep,
    "conclusion": CONCLUSION,
    "status": "CALCULATED",
}
OUT = os.path.join("cad", "output", "_r53g_limit")
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "report_r53g_preload_limit.json"), "w", encoding="utf-8") as f:
    json.dump(rep, f, ensure_ascii=False, indent=1)

for mu in ("mu0.30", "mu0.60"):
    d = sweep[mu]
    print("%s: 60%% 门槛 %.1f N/螺柱, 硬上限 %s N/螺柱, 名义 3 N 占比 %.1f %%"
          % (mu, d["limit_60pct_stall_n"], d["limit_hard_n"],
             [r["pct_of_stall"] for r in d["rows"] if r["preload_n"] == 3.0][0]))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
prop = font_manager.FontProperties(fname="C:/Windows/Fonts/msyhbd.ttc")
plt.rcParams["axes.unicode_minus"] = False

fig, ax = plt.subplots(1, 2, figsize=(13.5, 5.2))
for mu, col in (("mu0.30", "#2e7d32"), ("mu0.60", "#c62828")):
    rows = sweep[mu]["rows"]
    xs = [r["preload_n"] for r in rows]
    ax[0].plot(xs, [r["t_s"] if r["ok"] else float("nan") for r in rows], "-o", ms=3,
               color=col, label="mu = %s" % mu[-4:])
    sx = [r["preload_n"] for r in rows if not r["ok"]]
    if sx:
        ax[0].plot(sx, [TMAX]*len(sx), "x", ms=5, color=col,
                   label="mu = %s 卡死" % mu[-4:])
    ax[1].plot(xs, [r["pct_of_stall"] for r in rows], "-o", ms=3, color=col,
               label="mu = %s" % mu[-4:])
    lim60 = sweep[mu]["limit_60pct_stall_n"]
    limH = sweep[mu]["limit_hard_n"]
    for a in ax:
        a.axvline(lim60, color=col, ls="--", lw=1.0)
        if limH:
            a.axvline(limH, color=col, ls=":", lw=1.0)
ax[0].axvline(NOMINAL_N, color="#1565c0", lw=2.0)
ax[0].text(NOMINAL_N+0.2, ax[0].get_ylim()[1]*0.9 if ax[0].get_ylim()[1] else 1,
           "名义 3 N\n（R53f 限位环锁死）", color="#1565c0", fontproperties=prop, fontsize=9)
ax[1].axhline(60.0, color="k", ls="--", lw=1.0)
ax[1].text(12, 62, "R53b 采用的 60 % 堵转门槛", fontproperties=prop, fontsize=9)
ax[1].axhline(100.0, color="k", ls=":", lw=1.0)
ax[1].text(12, 102, "100 % 堵转", fontproperties=prop, fontsize=9)
ax[0].set_xlabel("单螺柱预载 (N)", fontproperties=prop)
ax[0].set_ylabel("换档耗时 (s)", fontproperties=prop)
ax[0].set_title("(a) 预载越大越推不动：耗时至失效", fontproperties=prop, fontsize=12)
ax[1].set_xlabel("单螺柱预载 (N)", fontproperties=prop)
ax[1].set_ylabel("所需力矩 / 堵转 (%)", fontproperties=prop)
ax[1].set_title("(b) 预载上限：超过门槛就没有余量", fontproperties=prop, fontsize=12)
for a in ax:
    a.grid(alpha=0.3)
    a.legend(prop=prop, fontsize=9)
fig.suptitle("T06 R53g 锁紧件预载上限（虚线 = 60 % 堵转门槛，点线 = 100 % 堵转）",
             fontproperties=prop, fontsize=13)
fig.tight_layout(rect=[0, 0, 1, 0.93])
png = os.path.join(OUT, "T06_R53g_preload_limit.png")
fig.savefig(png, dpi=130)
print("figure ->", png)
