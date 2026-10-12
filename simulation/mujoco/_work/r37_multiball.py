# -*- coding: utf-8 -*-
"""R37: 多球紧密排队下的索引式送球 + 发射仿真（DEC-0035 方向 B：托板 150 -> 215）。

与 R36 的唯一几何差异 = TRAY_X1 150 -> 215 mm（等待区整体搬出扫掠圆，容量
NECTAR 2 / POLLEN 3）；TPU 尖取 DEC-0034 实测外缘 r 58..60。其余口径与 R36 相同
（R_IN=107.974 / 扇区 142..275 / 5 deg 托板 / 拨杆 330-150 / 夹口 nip/2+48 热态）。
原始 R36:

几何 = R27/R32 口径（外罩内弧 R_IN=107.974，扇区 142..275 deg，5 deg 托盘
x=38.901..150，后挡墙 x=150..156 高 70）。拨杆 = 两叶 330/150 中心距 ~60。

装载方式：把球沿支撑面（球窝底 -> 外罩内弧 275 deg 切点 -> 5 deg 托盘）依次
相切成一条紧密排队，再静置收敛；排不进支撑面的球按"叠在上方"摆放（真实抓
一把球丢进去的堆积形态）。

驱动 = 索引式：停 hold 秒 -> 连续扫掠 SWEEP 度 -> 转回 360 度取下一颗。

输出：每颗球出膛时刻 / 出膛速度 / 轮内耗时，以及平均每颗耗时。
"""
import math, sys, json, random, argparse
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import opt_lib as ol
import r10_cradle as R10
import mujoco
import numpy as np

pv2 = ol.pv2
OUT = Path("simulation/mujoco/out")
R_IN, CUT_X, A_LIP, TRAY_X1, TILT, WHEEL_R = 107.974, 38.901, 275.0, 215.0, 5.0, 48.0
PIVOT = (-0.806, 0.423)
T_STALL, RPM = 0.530, 290.0
MU = 0.40
MM = 0.001
SIN_T, COS_T = math.sin(math.radians(TILT)), math.cos(math.radians(TILT))
D = math.degrees
SP = {"NECTAR": dict(r=45.974, m=0.130, nip=82.0),
      "POLLEN": dict(r=35.56, m=0.060, nip=64.0)}
PH0S = (0.0, 30.0, 60.0, 90.0, 120.0, 150.0)
SWEEP = 248.0
T_ROT = 360.0 / (RPM * 6.0)
XLIM = 40.0
SPILL_X = TRAY_X1 + 25.0     # 托板末端再往外 25 mm 才算逸出（R36 是硬编码 172）
SETTLE = 6.0
pv2.PIVOT_X, pv2.PIVOT_Z = PIVOT
pv2.R_IN = R_IN
pv2.R_OUT = R_IN + pv2.SHELL_WALL
FLOOR = ('    <geom name="catch_floor" type="box" size="2 2 0.01" pos="0.2 0 -0.10" '
         'rgba="0.6 0.6 0.6 0.5"/>\n')


def parts(phases=(330.0, 150.0), hub_r=12.0):
    def f():
        out = [("hub", (0., 0., 0.), (hub_r, 17.), 0.0, "cylY")]
        for i, a in enumerate(phases, 1):
            out += [("arm_%d" % i, (28., 0., 0.), (18., 9., 5.), a, "box"),
                    ("blade_%d" % i, (52., 0., 0.), (6., pv2.PADDLE_W / 2., 15.), a, "box"),
                    ("flex_%d" % i, (59., 0., 0.), (2., pv2.PADDLE_W / 2., 17.), a, "box")]
        return out
    return f


def support_path(r_ball, n_arc=560, n_ramp=500):
    """球心可停留的支撑面母线，从后挡墙端排到出口端：
    5 deg 托盘（x_center = TRAY_X1-r 直到切点）-> 外罩内弧（275 -> 142 deg）。"""
    pts = []
    rc = R_IN - r_ball
    xc0 = TRAY_X1 - r_ball
    xc1 = CUT_X - r_ball * SIN_T
    for i in range(n_ramp + 1):
        xc = xc0 + (xc1 - xc0) * i / n_ramp
        pts.append((xc, pv2.tray_top_z(xc + r_ball * SIN_T) + r_ball * COS_T))
    for i in range(1, n_arc + 1):
        a = math.radians(A_LIP - (A_LIP - pv2.A_EXIT) * i / n_arc)
        pts.append((pv2.PADDLE_CX + rc * math.cos(a), pv2.PADDLE_CZ + rc * math.sin(a)))
    return pts


MIN_ANG = 180.0
GAP = 0.6          # 球-球之间留的间隙 (mm)
ALLOW = 0.3        # 允许的初始浅穿透 (mm)
_PROBE = {}


def _ang(pt):
    return math.degrees(math.atan2(pt[1] - pv2.PADDLE_CZ,
                                   pt[0] - pv2.PADDLE_CX)) % 360.0


def _ball_name(r):
    for k, v in SP.items():
        if abs(v["r"] - r) < 1e-6:
            return k
    raise KeyError(r)


def _probe(r, nip, ph0):
    """单球探针模型：用来问 MuJoCo "球心放这里会不会撞东西"。"""
    key = (round(r, 4), round(ph0, 4))
    if key not in _PROBE:
        nm = _ball_name(r)
        m, d, aid, jid, meta, w, xml = build_multi([nm], ph0, nip)
        d.qpos[jid] = math.radians(ph0)
        g1 = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, "ball_geom_1")
        _PROBE[key] = (m, d, meta[0]["qadr"], g1)
    return _PROBE[key]


def clear_mm(r, nip, ph0, px, pz):
    """球心放 (px, pz) 时，球面到环境任何 geom 的最小净距 (mm，负=穿透)。"""
    m, d, adr, g1 = _probe(r, nip, ph0)
    d.qpos[adr:adr + 3] = [px * MM, 0.0, pz * MM]
    mujoco.mj_forward(m, d)
    best = 1e9
    for g2 in range(m.ngeom):
        if g2 == g1:
            continue
        dd = float(mujoco.mj_geomDistance(m, d, g1, g2, 0.06, None))
        if dd < best:
            best = dd
    return best * 1000.0


def _in_bowl(cx, cz, r):
    """有效装载区 = 外罩弧内（半径 <= R_IN-r）∪ 托板面之上（x 在托板跨度内）。
    托板区不封顶，允许叠放多颗球。"""
    if math.hypot(cx - pv2.PADDLE_CX, cz - pv2.PADDLE_CZ) <= R_IN - r - 0.5:
        return True
    if CUT_X - 4.0 <= cx <= TRAY_X1 - r + 4.0:
        return cz >= pv2.tray_top_z(cx + r * SIN_T) + r * COS_T - 2.0
    return False


def _free(r, nip, ph0, px, pz, others):
    """(px,pz) 处既不吃环境穿透、也不与已放好的球打架。"""
    for (ox, oz, orr) in others:
        if math.hypot(px - ox, pz - oz) < r + orr - ALLOW:
            return False
    if clear_mm(r, nip, ph0, px, pz) < -ALLOW:
        return False
    return True


def place_queue(mix, ph0=0.0):
    """从出口端向后退着排：第一颗取最靠前且不吃穿透的母线点，之后逐颗相切后撤；
    母线仍排不下的球，在"上一颗的外法向"附近网格搜一个不吃穿透的空位叠放。
    返回 (中心点列表, 叠放球数, 通道内球数)。"""
    n = len(mix)
    nip = max(SP[x]["nip"] for x in mix)
    pos = [None] * n
    r0 = SP[mix[0]]["r"]
    pts0 = [p for p in support_path(r0) if _ang(p) >= MIN_ANG]
    j0 = 0
    for j in range(len(pts0) - 1, -1, -1):
        if clear_mm(r0, nip, ph0, pts0[j][0], pts0[j][1]) >= -ALLOW:
            j0 = j
            break
    pos[0] = pts0[j0]
    stacked = 0
    for k in range(1, n):
        rp, r = SP[mix[k - 1]]["r"], SP[mix[k]]["r"]
        need = rp + r + GAP
        pv = pos[k - 1]
        pts = [p for p in support_path(r) if _ang(p) >= MIN_ANG]
        j = min(range(len(pts)), key=lambda i: math.hypot(pts[i][0] - pv[0],
                                                          pts[i][1] - pv[1]))
        found = False
        while j >= 0:
            px, pz = pts[j]
            if math.hypot(px - pv[0], pz - pv[1]) >= need and \
               _free(r, nip, ph0, px, pz, [(q[0], q[1], SP[mix[i]]["r"])
                                           for i, q in enumerate(pos[:k]) if q]):
                pos[k] = (px, pz)
                found = True
                break
            j -= 1
        if not found:
            # 母线排不下 -> 当成"从进料口继续投入"：在托板末端正上方逐层贴着摞，
            # 每层只高出 2r，静置阶段它们自己滚下去重新堆稳。
            xt = TRAY_X1 - r
            zt = pv2.tray_top_z(xt + r * SIN_T) + r * COS_T
            layers = sum(1 for q in pos[:k] if q and abs(q[0] - xt) < 1e-6)
            pos[k] = (xt, zt + (rp + r + GAP) * (layers + 1))
            stacked += 1
    return pos, stacked, n - stacked



def build_multi(mix, ph0, nip, mu=MU):
    rmax = max(SP[n]["r"] for n in mix)
    pv2.HALF_SPACING = nip / 2.0 + WHEEL_R
    pv2.R_CARRY = R_IN - rmax
    pv2.PIVOT_X, pv2.PIVOT_Z = PIVOT
    pv2.R_IN = R_IN
    pv2.R_OUT = R_IN + pv2.SHELL_WALL
    R10.R_MID = R_IN + 3.5
    pv2.BALL_R = SP[mix[0]]["r"]
    pv2.BALL_MASS = SP[mix[0]]["m"]
    pv2.static_geoms = (lambda: R10.stat(CUT_X, A_LIP, tray_x1=TRAY_X1))
    pv2.paddle_parts = parts()
    w = RPM * 2 * math.pi / 60.0
    xml, ctrl = pv2.build_xml(1620.0, -1, 0.0, 0.0, 0.0)
    xml = xml.replace("  <worldbody>\n", "  <worldbody>\n" + FLOOR, 1)
    i0 = xml.index('<body name="ball"')
    i1 = xml.index('</body>', i0) + len('</body>')
    lines = []
    for k, nm in enumerate(mix, 1):
        lines.append('  <body name="ball_%d" pos="0 0 0">' % k)
        lines.append('    <freejoint name="ball_free_%d"/>' % k)
        lines.append('    <geom name="ball_geom_%d" class="ball" type="sphere" '
                     'size="%.6f" mass="%g"/>' % (k, SP[nm]["r"] * MM, SP[nm]["m"]))
        lines.append('  </body>')
    xml = xml[:i0] + "\n".join(lines) + xml[i1:]
    xml = xml.replace('kv="0.08"', 'kv="%.6f"' % (T_STALL / w))
    xml = xml.replace('forcerange="-1.5 1.5"', 'forcerange="-%g %g"' % (T_STALL, T_STALL))
    xml = xml.replace('class="ball"><geom friction="1.0 0.02 0.0001"',
                      'class="ball"><geom friction="%g 0.02 0.0001"' % mu)
    m = mujoco.MjModel.from_xml_string(xml)
    d = mujoco.MjData(m)
    aid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "paddle_vel")
    jid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "paddle_joint")
    meta = []
    for k in range(1, len(mix) + 1):
        bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball_%d" % k)
        fj = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "ball_free_%d" % k)
        meta.append(dict(bid=bid, qadr=m.jnt_qposadr[fj], dadr=m.jnt_dofadr[fj]))
    d.ctrl[:] = [ctrl[0], ctrl[1], 0.0]
    d.qpos[jid] = math.radians(ph0)
    mujoco.mj_forward(m, d)
    return m, d, aid, jid, meta, w, xml


def put(d, mt, x, z):
    a = mt["qadr"]
    d.qpos[a:a + 3] = [x * MM, 0.0, z * MM]
    d.qpos[a + 3:a + 7] = [1.0, 0.0, 0.0, 0.0]
    d.qvel[mt["dadr"]:mt["dadr"] + 6] = 0.0


def run_case(mix, ph0, nip, hold, mu=MU, quiet=False, tq_mult=1.0,
             stiff_tc=0.0, dt=None):
    m, d, aid, jid, meta, w, xml = build_multi(mix, ph0, nip, mu)
    if dt:
        m.opt.timestep = dt
    if stiff_tc:
        m.geom_solref[:, 0] = stiff_tc
        m.geom_solimp[:, 0] = 0.95
        m.geom_solimp[:, 1] = 0.995
    if tq_mult != 1.0:
        m.actuator_forcerange[aid] = [-T_STALL * tq_mult, T_STALL * tq_mult]
        m.actuator_gainprm[aid, 0] = (T_STALL / w) * tq_mult
    nb = len(mix)
    centres, stacked, in_channel = place_queue(mix, ph0)
    dt = m.opt.timestep
    t0 = SETTLE
    n = int((t0 + (nb + 2) * (T_ROT + hold) + 4.0) / dt)   # +2 圈余量：最后一颗球也会被轮到
    kt = max(1, int(round(0.002 / dt)))
    kq = max(1, int(round(0.05 / dt)))
    tq, tr = [], [[] for _ in range(nb)]
    n_drive = 0
    exits = [None] * nb
    spilled = [None] * nb
    cyc_t0 = []
    phase, t_ph, kk = "settle", 0.0, 0
    sweep_end = reindex_end = None
    J0 = None
    for i in range(n):
        t = i * dt
        if phase == "settle":
            d.ctrl[aid] = 0.0
            if i == 0:
                for k, mt in enumerate(meta):
                    put(d, mt, *centres[k])
            if t + 0.5 * dt >= t0:
                phase, t_ph, kk = "settle_tail", t, 0
        J = D(d.qpos[jid])
        if phase == "settle_tail":
            d.ctrl[aid] = 0.0
            if t - t_ph >= hold:
                phase = "sweep"
                if J0 is None:
                    J0 = J
                sweep_end = J0 + 360.0 * kk + SWEEP
                reindex_end = J0 + 360.0 * (kk + 1)
        elif phase in ("sweep", "reindex"):
            d.ctrl[aid] = w
            if phase == "sweep" and J >= sweep_end:
                phase = "reindex"
            if J >= reindex_end:
                phase, t_ph, kk = "settle_tail", t, kk + 1
                if kk < 4:
                    cyc_t0.append(t)
        else:
            d.ctrl[aid] = 0.0
        mujoco.mj_step(m, d)
        if i % kt == 0:
            if phase != "settle" and n_drive == 0:
                n_drive = len(tq)
            tq.append(abs(float(d.actuator_force[aid])))
            for k, mt in enumerate(meta):
                if exits[k] is None:
                    p = d.xpos[mt["bid"]] * 1000.0
                    lx, _ = pv2.to_shooter(p[0], p[2])
                    if lx > XLIM:
                        exits[k] = dict(t=round(t, 3),
                                        v=round(float(np.linalg.norm(d.cvel[mt["bid"]][3:])), 3),
                                        cyc=kk, cyc_t=round(t - t_ph, 3),
                                        x=round(p[0], 1), z=round(p[2], 1))
                if spilled[k] is None and exits[k] is None and t > 1.0:
                    p = d.xpos[mt["bid"]] * 1000.0
                    if p[0] > SPILL_X or p[2] < -20.0:
                        spilled[k] = dict(t=round(t, 2), x=round(p[0], 1), z=round(p[2], 1))
        if i % kq == 0:
            for k, mt in enumerate(meta):
                p = d.xpos[mt["bid"]] * 1000.0
                lx, _ = pv2.to_shooter(p[0], p[2])
                rx, rz = p[0] - pv2.PADDLE_CX, p[2] - pv2.PADDLE_CZ
                tr[k].append(dict(t=round(t, 2), x=round(p[0], 1), z=round(p[2], 1),
                                  v=round(float(np.linalg.norm(d.cvel[mt["bid"]][3:])), 2),
                                  r=round(math.hypot(rx, rz), 1),
                                  ang=round(D(math.atan2(rz, rx)) % 360.0, 1),
                                  lx=round(lx, 1), J=round(D(d.qpos[jid]) % 360.0, 1)))
    tqa = np.array(tq[n_drive:]) if n_drive else np.array(tq)
    res = dict(mix=list(mix), ph0=ph0, nip=nip, hold=hold, mu=mu,
               start=[(round(c[0], 1), round(c[1], 1)) for c in centres], stacked=stacked,
               in_channel=in_channel,
               n_launched=sum(1 for e in exits if e), exit=exits, spill=spilled,
               cyc_t0=[round(x, 3) for x in cyc_t0],
               jam_frac=round(float(np.mean(tqa > 0.40)), 3),
               tq_peak=round(float(np.max(tqa)), 3), trace=tr)
    ok = [e for e in exits if e]
    if ok:
        res["t_total_s"] = round(max(e["t"] for e in ok) - t0, 2)
        res["cyc_mean_s"] = round(float(np.mean([e["cyc_t"] for e in ok])), 2)
        ts = sorted(e["t"] for e in ok)
        res["gaps"] = [round(ts[j + 1] - ts[j], 2) for j in range(len(ts) - 1)]
    settled = []
    for k, tk in enumerate(tr):
        s = [q for q in tk if abs(q["t"] - t0) < 0.03]
        if s:
            settled.append((round(s[0]["x"], 1), round(s[0]["z"], 1), s[0]["ang"]))
    res["settled"] = settled
    return res, xml


def probe(args):
    mix = args.mix.split(",") if args.mix else ["NECTAR"] * args.balls
    nip = max(SP[n]["nip"] for n in mix)
    res, xml = run_case(mix, args.ph0, nip, args.hold, dt=(args.dt or None))
    print("=== R37 装载探针 mix=%s  nip=%.0f  通道内=%d 叠放=%d ===" % ("+".join(mix), nip, res["in_channel"], res["stacked"]), flush=True)
    for k, c in enumerate(res["start"]):
        print("  球%d %-6s 摆放 (%.1f, %.1f)" % (k + 1, mix[k], c[0], c[1]), flush=True)
    print("静置 %.1f s 后落位：" % SETTLE, flush=True)
    for k, (x, z, a) in enumerate(res["settled"]):
        print("  球%d %-6s (%.1f, %.1f)  a=%.0f" % (k + 1, mix[k], x, z, a), flush=True)
    print("逸出:", [(k + 1, s) for k, s in enumerate(res["spill"]) if s], flush=True)
    print("出膛:", [(k + 1, e and e["t"]) for k, e in enumerate(res["exit"])], flush=True)
    print("=== probe done ===", flush=True)


def main_run(args):
    rng = random.Random(args.seed)
    nb = args.balls
    rows = []
    if args.mix:
        cases = [("固定 " + args.mix, ph0, args.mix.split(","))
                 for ph0 in PH0S[:args.cases]]
    else:
        cases = [("全 NECTAR 最坏", 0.0, ["NECTAR"] * nb)]
        for ph0 in PH0S[:args.cases]:
            cases.append(("随机", ph0,
                          [rng.choice(["POLLEN", "NECTAR"]) for _ in range(nb)]))
    print("=== R37 多球：紧密排队，索引式 1 圈/球，扫掠 %.0f deg，停 %.1f s，mu=%.2f ==="
          % (SWEEP, args.hold, MU), flush=True)
    for tag, ph0, mix in cases:
        nip = max(SP[x]["nip"] for x in mix)
        res, xml = run_case(mix, ph0, nip, args.hold, dt=(args.dt or None))
        rows.append(res)
        print("\n[%s  ph0=%3.0f deg  球序 %s  夹口 %.0f mm  叠放 %d 颗]" %
              (tag, ph0, ">".join(mix), nip, res["stacked"]), flush=True)
        for k, e in enumerate(res["exit"]):
            if e:
                print("   球%d %-6s 出膛 t=%6.2f s  轮内 %5.2f s  v=%5.2f m/s" %
                      (k + 1, mix[k], e["t"], e["cyc_t"], e["v"]), flush=True)
            else:
                sp = res["spill"][k]
                print("   球%d %-6s 未出膛%s" % (k + 1, mix[k],
                      ("  (逸出 t=%.2f @ (%.0f,%.0f))" % (sp["t"], sp["x"], sp["z"])) if sp else ""),
                      flush=True)
        print("   -> %d/%d 出膛  清空总耗时 %s s  平均每颗 %s s  扭矩峰值 %.3f Nm  卡滞占比 %.0f%%" %
              (res["n_launched"], len(mix), res.get("t_total_s", "--"),
               (round(res["t_total_s"] / res["n_launched"], 2) if res.get("t_total_s") else "--"),
               res["tq_peak"], 100 * res["jam_frac"]), flush=True)
    n_balls = sum(len(r["mix"]) for r in rows)
    ok = [e for r in rows for e in r["exit"] if e]
    tt = [r["t_total_s"] for r in rows if r.get("t_total_s")]
    print("\n=== 汇总（%d 轮，共 %d 颗）===" % (len(rows), n_balls), flush=True)
    print("  出膛成功率 %d/%d = %.0f%%" % (len(ok), n_balls, 100.0 * len(ok) / n_balls), flush=True)
    if ok:
        print("  平均轮内耗时 %.2f s (n=%d, 标准差 %.2f s)" %
              (float(np.mean([e["cyc_t"] for e in ok])), len(ok),
               float(np.std([e["cyc_t"] for e in ok]))), flush=True)
        vv = [e["v"] for e in ok]
        print("  出膛速度 均值 %.2f m/s  最小 %.2f  最大 %.2f" %
              (float(np.mean(vv)), min(vv), max(vv)), flush=True)
    if tt:
        print("  平均清空总耗时 %.2f s" %
              float(np.mean(tt)), flush=True)
    print("  最大扭矩峰值 %.3f Nm，最大卡滞占比 %.0f%%  逸出球数 %d" %
          (max(r["tq_peak"] for r in rows), 100 * max(r["jam_frac"] for r in rows),
           sum(1 for r in rows for s in r["spill"] if s)), flush=True)
    (OUT / ("_r37_multiball_%s.json" % args.tag)).write_text(
        json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print("  saved", OUT / ("_r37_multiball_%s.json" % args.tag), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--mix", default="")
    ap.add_argument("--ph0", type=float, default=0.0)
    ap.add_argument("--hold", type=float, default=3.0)
    ap.add_argument("--balls", type=int, default=4)
    ap.add_argument("--cases", type=int, default=6)
    ap.add_argument("--seed", type=int, default=20261011)
    ap.add_argument("--dt", type=float, default=0.0)
    ap.add_argument("--tag", default="run")
    args = ap.parse_args()
    if args.probe:
        probe(args)
    else:
        main_run(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
