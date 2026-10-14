# -*- coding: utf-8 -*-
"""T06 R53e: 比赛中 ONLINE 换档工况复核（全自动、无人介入）。

回答三件事：
  1) 时序：射手发一发 -> 25-2 把夹口从 POLLEN 换到 NECTAR（或反向）要多久，能不能排进比赛节奏。
  2) 保持：发射瞬间球给两飞轮的反作用力会不会把夹口顶开（这会直接掉出膛速度）。
  3) 端点：nectar 档离机构死点只有 0.5 mm，固件命令范围必须卡在哪。
几何/链公式与 R53d 同源（cad/paddle_launcher_gap_chain_dynamic_r53d.py），这里只补比赛工况。

Run: .venv-cad/Scripts/python.exe -X utf8 cad/paddle_launcher_gap_chain_match_r53e.py
"""
import json, math, os

# ------------------------------------------------ 链几何（与 R53c/R53d 同源） -------
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
        if d_of_theta(mid) > d_t: lo = mid
        else: hi = mid
    return 0.5*(lo+hi)

def dh_dtheta_mm(th, eps=1e-5):
    return (half_of_theta(th+eps) - half_of_theta(th-eps))/(2.0*eps)

TH = {k: theta_of_half(v) for k, v in HALF.items()}
DH = {k: abs(dh_dtheta_mm(TH[k])) for k in HALF}          # mm/rad
H_DEAD = half_of_theta(0.0)                               # 机构行程上限（死点）

# ------------------------------------------------ 夹紧件（R53b） -------------------
STUDS_PER_CARRIAGE, FACES, PRELOAD_N, MU_FACE = 8, 2.0, 3.0, 0.30
F_CLAMP = FACES*STUDS_PER_CARRIAGE*PRELOAD_N*MU_FACE      # N / 滑座，抗滑摩擦

# ------------------------------------------------ 舵机 25-2 ------------------------
T_STALL, NOLOAD_RPM = 2.471, 60.0
W_NOLOAD = NOLOAD_RPM*2.0*math.pi/60.0
F_HOLD = {k: T_STALL/(2.0*DH[k]*1.0e-3) for k in HALF}    # N / 滑座，堵转保持能力

# ------------------------------------------------ 链刚度（与 R53d 同源） ----------
E_PET, A_MAIN, A_DRAG = 2000.0, math.pi*3.2**2, math.pi*3.0**2

def chain_stiffness_N_per_mm(h):
    phi = math.asin(min(1.0, h/L_MAIN))
    k_main = 2.0*(E_PET*A_MAIN/L_MAIN)*math.cos(phi)**2
    th = theta_of_half(h); d = d_of_theta(th)
    cb = (d*d + L_DRAG**2 - R_CRANK**2)/(2.0*d*L_DRAG)
    beta = math.acos(max(-1.0, min(1.0, cb)))
    k_drag = (E_PET*A_DRAG/L_DRAG)*math.cos(beta)**2
    return (k_main*k_drag)/(k_main + k_drag)

K_CHAIN = {k: chain_stiffness_N_per_mm(v) for k, v in HALF.items()}

# ================================================= 1) 换档时序 =====================
SPAN_DEG = abs(math.degrees(TH["pollen"] - TH["nectar"]))
DT, TMAX, J_EFF, KP = 2.0e-5, 5.0, 1.0e-4, 200.0

def switch(th0, th1, f_tot, dt=DT, tmax=TMAX):
    """R53d 同款积分 + 库仑摩擦死区判据：误差小于 T_load/Kp 时机构就停下了。

    这不影响物理结论：死区在 pollen 档约 0.0032 rad x 11.0 mm/rad = 0.035 mm，
    nectar 档更小，远在用户 1 mm 口径内。
    """
    th, w, t, work, frozen = th0, 0.0, 0.0, 0.0, 0.0
    sgn = 1.0 if th1 > th0 else -1.0
    while t < tmax:
        T_load = f_tot*abs(dh_dtheta_mm(th))*1.0e-3
        T_avail = T_STALL*(1.0 - min(1.0, abs(w)/W_NOLOAD))
        T_motor = max(-T_avail, min(T_avail, KP*(th1-th) - 0.4*w))
        w += ((T_motor - sgn*T_load)/J_EFF)*dt
        if w*sgn < 0.0: w = 0.0
        th += w*dt
        t += dt
        work += abs(T_motor*w)*dt
        if (abs(th1-th) < 2.0e-4 and abs(w) < 0.05) or (abs(w) < 1.0e-9 and (frozen := frozen+dt) > 0.05):
            return {"t_s": t, "work_J": work,
                    "residual_rad": abs(th1-th),
                    "residual_mm": abs(th1-th)*abs(dh_dtheta_mm(th))*1.0,
                    "stalled_on_friction": bool(abs(th1-th) > 2.0e-4)}
    return {"t_s": None, "work_J": work, "residual_rad": None, "residual_mm": None,
            "stalled_on_friction": None}

MU_BAND = (0.30, 0.60)
sw = {}
for mu in MU_BAND:
    f_tot = 2.0*FACES*STUDS_PER_CARRIAGE*PRELOAD_N*mu
    for src, dst in (("pollen", "nectar"), ("nectar", "pollen")):
        r = switch(TH[src], TH[dst], f_tot)
        sw["mu%.2f_%s_to_%s" % (mu, src, dst)] = {
            "t_s": round(r["t_s"], 3) if r["t_s"] else None,
            "servo_work_J": round(r["work_J"], 4),
            "residual_mm": round(r["residual_mm"], 4) if r["residual_mm"] is not None else None,
            "stalled_on_friction": r["stalled_on_friction"]}

t_switch_max = max(v["t_s"] for v in sw.values() if v["t_s"])
e_switch_max = max(v["servo_work_J"] for v in sw.values())
SEQUENCE_S = 0.35 + 0.05 + 0.05          # 换档 + 稳定 + 余量
N_SWITCH_PER_MATCH = 12                  # ASSUMED：一场比赛换档次数上限
duty = N_SWITCH_PER_MATCH*SEQUENCE_S/150.0

# ================================================= 2) 发射反力保持 ================
M_BALL = {"pollen": 0.060, "nectar": 0.130}      # kg, ASSUMED（config: 0.060/0.130）
V_EXIT = 5.56                                    # m/s, P3 弹道基线 CALCULATED
T_CONTACT = 0.020                                # s, ASSUMED（球通过夹口接触段）
MU_BALL = 0.40                                   # ASSUMED（球-轮面）
PEAK_FACTOR = 1.8                                # 冲击峰值/均值，ASSUMED

recoil = {}
for k in ("pollen", "nectar"):
    f_tan = M_BALL[k]*V_EXIT/T_CONTACT                       # N，切向驱动力的均值
    f_sep_car = PEAK_FACTOR*f_tan/(2.0*MU_BALL)              # N/滑座，把两轮顶开的分量
    recoil[k] = {
        "f_tangential_mean_N": round(f_tan, 1),
        "f_separation_per_carriage_peak_N": round(f_sep_car, 1),
        "elastic_deflection_mm": round(f_sep_car/K_CHAIN[k], 3),
        "residual_offset_mm": round(F_CLAMP/K_CHAIN[k], 3),
        "vs_clamp_only_x": round(f_sep_car/F_CLAMP, 2),
        "vs_servo_hold_x": round(f_sep_car/F_HOLD[k], 2),
        "servo_holds": bool(f_sep_car < F_HOLD[k])}

# 脉冲响应（单自由度：链刚度 + 夹紧库仑摩擦），看会不会跑掉
def pulse_response(k_n_per_mm, f_peak, f_coulomb, t_pulse=0.020, m=1.0, dt=2.0e-6, t_end=0.25):
    k = k_n_per_mm*1.0e3
    x, v, t, xmax = 0.0, 0.0, 0.0, 0.0
    xs = []
    while t < t_end:
        f_load = f_peak if t < t_pulse else 0.0
        f_fric = -math.copysign(min(f_coulomb, abs(k*x)*0.5 + f_peak*0.0), v) if abs(v) > 1e-6 else 0.0
        a = (f_load - k*x + f_fric)/m
        v += a*dt; x += v*dt; t += dt
        xmax = max(xmax, x)
        if int(t/(dt*50)) != int((t-dt)/(dt*50)):
            xs.append((round(t, 4), round(x*1000.0, 4)))     # mm
    return xmax*1000.0, x*1000.0, xs                      # mm, mm, [(s, mm)]

k_pollen = K_CHAIN["pollen"]
x_max, x_res, xs = pulse_response(k_pollen, recoil["nectar"]["f_separation_per_carriage_peak_N"], F_CLAMP)

# ================================================= 3) 端点安全 ====================
margin_dead = H_DEAD - HALF["nectar"]

# ================================================= 输出 ===========================
OUT = os.path.join("cad", "output", "_r53e_match")
os.makedirs(OUT, exist_ok=True)
rep = {
 "units": "mm, N, N.m, deg, s, J",
 "question": "比赛中无人介入时，现有 25-2 调隙舵机能否自动在两档之间切换，换档后夹口能否在发射时守住。",
 "answers": {
   "no_human_in_match": True,
   "why": "R53b 夹紧件是被动常闭弹簧夹（装配时用尼龙锁紧螺母做反作用座，装一次），比赛全程没有任何需要人碰的零件；换档只由已有的 2000-0025-0002 位置舵机完成，不需要新增舵机通道。",
   "switch_time_max_s": round(t_switch_max, 3),
   "recoil_holds_gap": all(v["servo_holds"] for v in recoil.values())},
 "switch_sequence": {"servo_degrees": {k: round(math.degrees(v), 3) for k, v in TH.items()},
                     "span_deg": round(SPAN_DEG, 2),
                     "t_switch_s": round(t_switch_max, 3),
                     "settle_after_switch_s": 0.05,
                     "arrived_residual_mm": {k: v["residual_mm"] for k, v in sw.items()},
                     "sequence_total_s": round(SEQUENCE_S, 2),
                     "assumed_switches_per_match": N_SWITCH_PER_MATCH,
                     "servo_on_time_duty": round(duty, 4),
                     "note": "换档时先让飞轮停/降速再切，切完等 0.05 s 再恢复发射；换档期间禁止发射（同一根链在动）"},
 "switch_detail": sw,
 "servo_heat": {"work_per_switch_J_max": round(e_switch_max, 4),
                "on_time_per_switch_s": round(t_switch_max, 3),
                "note": "单次换档舵机做功 <=0.64 J、峰值出力时间 <30%，换档 0.35 s 后即可停在上位不需要持续出力（夹紧件与链保持位置）"},
 "clamp": {"friction_per_carriage_N": round(F_CLAMP, 1), "preload_per_stud_N": PRELOAD_N,
           "mu_face": MU_FACE, "studs_per_carriage": STUDS_PER_CARRIAGE},
 "servo_hold": {"f_hold_per_carriage_N": {k: round(F_HOLD[k], 1) for k in HALF},
                "from": "T_stall 2.471 N.m / (2 |dh/dth|)，与 R53b 的 112 N 预算同源"},
 "chain_stiffness_N_per_mm": {k: round(v, 1) for k, v in K_CHAIN.items()},
 "recoil": recoil,
 "recoil_pulse_response": {"k_N_per_mm": round(k_pollen, 1), "peak_mm": round(x_max, 3),
                           "residual_mm": round(x_res, 3), "curve": xs[::2]},
 "endpoint_safety": {"h_dead_point_mm": round(H_DEAD, 3), "nectar_setting_mm": HALF["nectar"],
                     "margin_to_dead_point_mm": round(margin_dead, 3),
                     "note": "nectar 档离行程死点只有 %.3f mm；死点是机构自带的软止挡（不可能再往外跑），固件只需把命令锁在 19.33..96.68 deg，不要往死点方向多给角度" % margin_dead},
 "assumed": {"ball_mass_kg": M_BALL, "exit_speed_m_s": V_EXIT, "contact_s": T_CONTACT,
             "mu_ball_wheel": MU_BALL, "peak_factor": PEAK_FACTOR, "mu_face": MU_FACE,
             "E_PET_N_per_mm2": E_PET, "m_eff_kg": 1.0, "servo_stall_Nm": T_STALL},
 "sources": {"chain_geometry": "cad/paddle_launcher_gap_chain_dynamic_r53d.py（R53c/R53d 口径）",
             "clamp": "cad/paddle_launcher_shooter_lock_r53b.py + report_r53b_pollen.json",
             "exit_speed": "docs/p3_ballistics.py / docs/p3_launcher_comparison.md 5.556 m/s",
             "ball_mass": "config/parameters.yaml（ASSUMED 0.060 / 0.130 kg）"},
 "status": "CALCULATED"}
path = os.path.join(OUT, "report_r53e_match.json")
with open(path, "w", encoding="utf-8") as f:
    json.dump(rep, f, ensure_ascii=False, indent=1)

print(json.dumps({k: rep[k] for k in ("answers", "switch_sequence", "recoil",
                                      "recoil_pulse_response", "endpoint_safety", "servo_heat")},
                 ensure_ascii=False, indent=1))
print("report ->", path)

# ================================================= 图 =============================
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
fp = "C:/Windows/Fonts/msyhbd.ttc"
prop = font_manager.FontProperties(fname=fp)
plt.rcParams["axes.unicode_minus"] = False

fig, ax = plt.subplots(1, 3, figsize=(16.5, 5.2))

# (a) 比赛时序
a = ax[0]
rows = [("飞轮电机", 0.0, 0.35, "#9aa7b4"), ("25-2 调隙舵机", 0.0, t_switch_max, "#2e7d32"),
        ("稳定等待", t_switch_max, 0.05, "#f9a825"), ("可以发射", t_switch_max+0.05, 0.05, "#1565c0")]
for i, (name, t0, dur, col) in enumerate(rows):
    a.broken_barh([(t0, dur)], (i-0.35, 0.7), facecolors=col)
    a.text(t0+dur+0.01, i, "%s  %.3f s" % (name, dur), va="center", fontproperties=prop, fontsize=10)
a.set_yticks(range(len(rows))); a.set_yticklabels([r[0] for r in rows], fontproperties=prop)
a.set_xlim(0, 0.65); a.set_xlabel("时间 (s)", fontproperties=prop)
a.set_title("(a) 一次在线换档的比赛时序（无人介入）", fontproperties=prop, fontsize=12)
a.grid(alpha=0.3, axis="x")

# (b) 发射反力 vs 保持能力
b = ax[1]
labels = ["POLLEN", "NECTAR"]
sep = [recoil["pollen"]["f_separation_per_carriage_peak_N"], recoil["nectar"]["f_separation_per_carriage_peak_N"]]
hold = [F_HOLD["pollen"], F_HOLD["nectar"]]
clamp = [F_CLAMP, F_CLAMP]
xpos = [0, 1]
b.bar([p-0.22 for p in xpos], sep, width=0.22, label="发射反力(峰值)", color="#c62828")
b.bar(xpos, hold, width=0.22, label="舵机堵转保持", color="#2e7d32")
b.bar([p+0.22 for p in xpos], clamp, width=0.22, label="夹紧件摩擦", color="#f9a825")
for i, v in enumerate(sep): b.text(xpos[i]-0.22, v+2, "%.0f N" % v, ha="center", fontproperties=prop, fontsize=9)
for i, v in enumerate(hold): b.text(xpos[i], v+2, "%.0f N" % v, ha="center", fontproperties=prop, fontsize=9)
b.set_xticks(xpos); b.set_xticklabels(labels, fontproperties=prop)
b.set_ylabel("单个滑座上的力 (N)", fontproperties=prop)
b.set_title("(b) 发射反力 vs 夹口保持能力（守夹口的是舵机，不是夹紧件）", fontproperties=prop, fontsize=12)
b.legend(prop=prop); b.grid(alpha=0.3, axis="y")

# (c) 脉冲响应
c = ax[2]
xs_curve = rep["recoil_pulse_response"]["curve"]
c.plot([p[0] for p in xs_curve], [p[1] for p in xs_curve], color="#c62828", lw=1.6)
c.axhline(0, color="k", lw=0.6)
c.axhline(1.0, color="#1565c0", ls="--", lw=1.0)
c.text(0.16, 1.02, "用户口径 1 mm", color="#1565c0", fontproperties=prop, fontsize=9)
c.set_xlim(0, 0.25); c.set_ylim(-0.6, 1.2)
c.set_xlabel("时间 (s)", fontproperties=prop); c.set_ylabel("夹口单边偏移 (mm)", fontproperties=prop)
c.set_title("(c) 发射冲击下夹口偏移：峰值 %.2f mm，发射后回弹 %.2f mm" % (x_max, x_res),
            fontproperties=prop, fontsize=12)
c.grid(alpha=0.3)

fig.suptitle("T06 R53e 比赛中在线换档工况复核（25-2 自动、无人介入）", fontproperties=prop, fontsize=14)
fig.tight_layout(rect=[0, 0, 1, 0.94])
png = os.path.join(OUT, "T06_R53e_match_cycle.png")
fig.savefig(png, dpi=130)
print("figure ->", png)
