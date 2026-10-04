# -*- coding: utf-8 -*-
"""T06 POLLEN V2 接触几何方案 A/B/C/D 逐个仿真 + 摩擦敏感性（求发射门槛扭矩）。"""
import json, math, sys, time, importlib.util
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
import mujoco, numpy as np

spec = importlib.util.spec_from_file_location("pv2", r"simulation/mujoco/pollen_v2_sim.py")
pv2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(pv2)
OUT = Path("simulation/mujoco/out"); OUT.mkdir(parents=True, exist_ok=True)
ORIG_STATIC, ORIG_PARTS = pv2.static_geoms, pv2.paddle_parts

# ---------------------------------------------------------------- 几何补丁
def seg(am, r_in, thick=7.0, da=4.0):
    r_mid = r_in + thick / 2.0
    half = 0.5 * r_mid * math.radians(da) * 1.35
    cx, cz = pv2.polar(r_mid, am)
    return ("flare_%d" % int(round(am * 10)), "shell", "box", (2 * half, pv2.FEEDER_W, thick),
            (cx, 0.0, cz), pv2.quat_y(-(am + 90.0)))

def flare(base):
    def f():
        g = [t for t in base() if t[0] != "shell_lip_face"]
        g += [seg(227.5 + 4.0 * k, 95.5 + 4.0 * k) for k in range(3)]
        return g
    return f

def tray_recess(x0=-12.0):
    def f(base):
        def g():
            out = []
            for t in base():
                if t[0] == "tray":
                    x1 = pv2.TRAY_X1
                    nmx, nmz = pv2.normal(-pv2.TILT)
                    xm = 0.5 * (x0 + x1); zt = pv2.tray_top_z(xm)
                    L = (x1 - x0) / math.cos(math.radians(pv2.TILT))
                    t = ("tray", "shell", "box", (L, pv2.FEEDER_W, pv2.TRAY_T),
                         (xm - nmx * pv2.TRAY_T / 2.0, 0.0, zt - nmz * pv2.TRAY_T / 2.0),
                         pv2.quat_y(-pv2.TILT))
                out.append(t)
            return out
        return g
    return f

def pad(step):
    def f(base):
        def g():
            out = list(base())
            ztop = pv2.tray_top_z(-2.0) + step
            out.append(("rest_pad", "shell", "box", (30.0, pv2.FEEDER_W, step + 6.0),
                        (-2.0, 0.0, ztop - (step + 6.0) / 2.0), pv2.quat_y(0.0)))
            return out
        return g
    return f

def blade_low(base, tip=56.0):
    def f():
        parts = [("hub", (0.0, 0.0, 0.0), (18.0, 17.0, 18.0), 0.0, "cylY")]
        for i, a in enumerate((pv2.PADDLE_PHASE, pv2.PADDLE_PHASE + 120.0, pv2.PADDLE_PHASE + 240.0), 1):
            parts.append(("arm_%d" % i, (30.0, 0.0, 0.0), (16.0, 9.0, 5.0), a, "box"))
            parts.append(("blade_%d" % i, (tip - 8.0, 0.0, 0.0), (6.0, pv2.PADDLE_W / 2.0, 15.0), a, "box"))
            parts.append(("flex_%d" % i, (tip - 2.0, 0.0, 0.0), (2.0, pv2.PADDLE_W / 2.0, 17.0), a, "box"))
        return parts
    return f

BASE = ORIG_STATIC
GEOM = {
    "V0 现状":          (BASE,                    ORIG_PARTS),
    "A 唇口喇叭":        (flare(BASE),             ORIG_PARTS),
    "B 托板缩进":        (tray_recess()(BASE),     ORIG_PARTS),
    "C 叶尖卸载":        (BASE,                    blade_low(ORIG_PARTS, 56.0)),
    "D 球窝抬高6.8":     (pad(6.8)(BASE),          ORIG_PARTS),
    "A+B":             (flare(tray_recess()(BASE)), ORIG_PARTS),
    "A+D":             (flare(pad(6.8)(BASE)),     ORIG_PARTS),
}

def apply_geom(name):
    s, p = GEOM[name]
    pv2.static_geoms, pv2.paddle_parts = s, p

# ---------------------------------------------------------------- 仿真
def run(name, bx=145.0, rpm=200.0, fr=1.0, sec=7.0, mu_ball=None, mu_shell=None,
        fw=1620.0, trace=False, rest=False):
    apply_geom(name)
    prpm = 1.0 if rest else rpm
    xml, ctrl = pv2.build_xml(fw, -1, prpm * 2 * math.pi / 60.0, bx,
                              pv2.tray_top_z(bx) + pv2.BALL_R)
    xml = xml.replace('forcerange="-1.5 1.5"', 'forcerange="-%g %g"' % (fr, fr))
    if mu_ball is not None:
        xml = xml.replace('class="ball"><geom friction="1.0 0.02 0.0001"',
                          'class="ball"><geom friction="%g 0.02 0.0001"' % mu_ball)
    if mu_shell is not None:
        xml = xml.replace('class="shell"><geom friction="0.25 0.005 0.0001"',
                          'class="shell"><geom friction="%g 0.005 0.0001"' % mu_shell)
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
    aid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "paddle_vel")
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    dt = m.opt.timestep; n = int(round(sec / dt))
    k = max(1, int(round(0.002 / dt)))
    tr = []; tq = np.zeros(n); sv = np.zeros(n)
    for i in range(n):
        mujoco.mj_step(m, d)
        tq[i] = abs(float(d.actuator_force[aid]))
        sv[i] = float(np.linalg.norm(d.cvel[bid][3:]))
        if i % k == 0:
            p = d.xpos[bid]
            px, pz = float(p[0]) * 1000.0, float(p[2]) * 1000.0
            rx, rz = px - pv2.PADDLE_CX, pz - pv2.PADDLE_CZ
            lx, lz = pv2.to_shooter(px, pz)
            tr.append({"t": round(i * dt, 4), "x": round(px, 3), "z": round(pz, 3),
                       "v": round(float(np.linalg.norm(d.cvel[bid][3:])), 4),
                       "vx": round(float(d.cvel[bid][3]), 4), "vz": round(float(d.cvel[bid][5]), 4),
                       "r": round(math.hypot(rx, rz), 3),
                       "ang": round(math.degrees(math.atan2(rz, rx)) % 360.0, 2),
                       "lx": round(lx, 3), "lz": round(lz, 3)})
    res = pv2.analyse(tr)
    res["torque_peak_Nm"] = round(float(tq.max()), 3)
    res["torque_load_mean_Nm"] = round(float(tq[sv > 0.05].mean()) if (sv > 0.05).any() else 0.0, 3)
    pix = sv > 0.05
    res["torque_load_p95_Nm"] = round(float(np.percentile(tq[pix], 95)) if pix.any() else 0.0, 3)
    if trace:
        res["_trace"] = tr
    return res

def settles(name, bx=145.0, sec=4.0):
    r = run(name, bx=bx, fr=1.0, sec=sec, rest=True)
    # 静止位置：用最后 20 个采样点的平均
    f = r["_trace"][-20:] if "_trace" in r else None
    return r

def ok(name, bx, fr, **kw):
    r = run(name, bx=bx, fr=fr, **kw)
    return bool(r["launched"]), r

def threshold(name, lo=0.20, hi=1.60, tol=0.05, bx=145.0, **kw):
    """二分法找最小可通过力矩限幅"""
    ok_hi, r_hi = ok(name, bx, hi, **kw)
    if not ok_hi:
        return None, hi, r_hi
    ok_lo, _ = ok(name, bx, lo, **kw)
    if ok_lo:
        return lo, lo, None
    while hi - lo > tol:
        mid = round(0.5 * (lo + hi), 3)
        good, _ = ok(name, bx, mid, **kw)
        if good: hi = mid
        else:    lo = mid
    return hi, hi, r_hi
