# -*- coding: utf-8 -*-
"""R47 交付附件：直接驱动 R47 MJCF 模型的运行脚本。

XML 只描述模型；挡舌（mocap）与"待机停位"（真实舵机位置保持）是控制逻辑，须外部驱动。
本脚本按 R47 验收口径驱动：
  飞轮 1620 rpm 对向旋转 -> 静置 6 s -> 每颗球: 停 1 s -> 290 rpm 扫 248 deg -> 回位 360 deg/颗
  挡舌: 拨杆停稳后 0.10 s 抬到 z=139.5 mm（下端 112.0），被送那颗球尾缘越过闸口面即落回
        z=72.5 mm（下端 45.0，低于 POLLEN 球心 55.1 mm 约 10 mm）（最长抬 3 s）
        行程 67 mm（--gate-dn / --gate-up 可改；92 mm 旧口径见 R47/DEC-0043）
  停位: 舵机速度伺服保持 188 deg（真实舵机不自由下垂）
  混装模型对: 每颗球按球径选轮间夹口（POLLEN 64 mm / NECTAR 82 mm），换档时搬运完整状态

用法:
  python run_R47_xml.py                                   # 默认 out/R47_launcher_4xPOLLEN_gap064.xml
  python run_R47_xml.py out/R47_launcher_4xNECTAR_gap082.xml --ph 3
  python run_R47_xml.py out/R47_launcher_mixed4_gap064.xml  # 混装（随机排布），会自动启用换档
  python run_R47_xml.py --pair --ph 3                      # 手动指定混装 + 起始相位 ph3 (90 deg)

  # 3) 开窗口边跑边看（推荐；鼠标可转视角）
  python run_R47_xml.py --view
  python run_R47_xml.py out/R47_launcher_4xPOLLEN_gap064.xml --view
  python run_R47_xml.py --pair --view --slow 2.0
窗口操作：左键拖=旋转，右键拖=平移，滚轮=缩放，空格=暂停/继续，Esc=关闭。
"""
import sys, os, re, math, time, argparse, importlib.util

import mujoco

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ap = argparse.ArgumentParser()
ap.add_argument("xml", nargs="?", default="")
ap.add_argument("--pair", action="store_true", help="跑 out/ 里的混装模型对（按球种自动换档）")
ap.add_argument("--ph", type=int, default=0, help="起始相位 keyframe 索引 0..5 (0/30/60/90/120/150 deg)")
ap.add_argument("--sec", type=float, default=40.0, help="仿真总时长上限 s")
ap.add_argument("--fw-rpm", type=float, default=1620.0)
ap.add_argument("--park", type=float, default=188.0)
ap.add_argument("--view", action="store_true", help="开 MuJoCo 交互窗口边跑边看")
ap.add_argument("--slow", type=float, default=1.0, help="慢放倍数（1.0=实时，2.0=两倍慢）")
ap.add_argument("--gate-ramp", type=float, default=0.15, help="挡舌全行程用时 s（真实舵机速度）")
ap.add_argument("--gate-dn", type=float, default=67.5, help="挡舌关闭位中心 z mm（下端 = z-27.5；67.5 -> 40.0）")
ap.add_argument("--gate-up", type=float, default=139.5, help="挡舌开启位中心 z mm（下端 z-27.5）")
ap.add_argument("--gatelog", default="", help="把挡舌行程 + 挡舌接触载荷写成 CSV")
a = ap.parse_args()

HERE = os.path.dirname(os.path.abspath(__file__))
OD = lambda n: os.path.join(HERE, "out", n)
if a.xml and not os.path.exists(a.xml):        # 允许从仓库根目录用相对路径
    _alt = os.path.join(HERE, a.xml)
    if os.path.exists(_alt):
        a.xml = _alt
if not a.pair:                      # 混装（随机排布）自动换档
    _p = a.xml or OD("R47_launcher_4xPOLLEN_gap064.xml")
    try:
        _t = open(_p, encoding="utf-8").read()
        _n = set(82 if float(v) > 0.040 else 64
                 for v in re.findall(r'name="ball_geom_\d"[^>]*size="([0-9.]+)"', _t))
    except Exception:
        _n = set()
    if len(_n) > 1 and os.path.exists(OD("R47_launcher_mixed4_gap064.xml")) \
       and os.path.exists(OD("R47_launcher_mixed4_gap082.xml")):
        a.pair = True
        print("检测到混装（随机排布）模型 %s，自动启用换档" % os.path.basename(_p))

if a.pair:
    SINGLE = ""
    PAIR_PATHS = {64: OD("R47_launcher_mixed4_gap064.xml"),
                  82: OD("R47_launcher_mixed4_gap082.xml")}
else:
    SINGLE, PAIR_PATHS = (a.xml or OD("R47_launcher_4xPOLLEN_gap064.xml")), {}

spec = importlib.util.spec_from_file_location("pv2", os.path.join(HERE, "pollen_v2_sim.py"))
pv2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pv2)

MM = 0.001
RPM, SWEEP, HOLD, SETTLE, XLIM, SW_DELAY = 290.0, 248.0, 1.0, 6.0, 40.0, 0.25
GX, GT, GMARG, GDELAY, GMAXOPEN = 180.0, 5.0, 3.0, 0.10, 3.00
GRAMP = max(0.01, float(a.gate_ramp))
GZ_DN, GZ_UP, PKP = float(a.gate_dn), float(a.gate_up), 40.0
W = RPM * 2.0 * math.pi / 60.0


def gate_load(m, d, ggeom):
    """挡舌受到的接触合力（世界系：Fx 沿球道，Fz 沿行程）；用于给闸门驱动选型。

    MuJoCo 约定 ``mj_contactForce`` 给出的是 geom1 作用在 geom2 上的力，故
    geom1=挡舌时取负号。``frame`` 是行主序 3x3 接触系，v_world = R @ v_local。

    只把「球」的载荷算作设计载荷；与托板/外罩等静态件的接触单独统计 —— 仿真里
    托板是整块平板（真实件要在 x=180 开槽让挡舌穿过），那部分接触是建模假象。
    """
    import numpy as _np
    fx = fz = fnorm = 0.0
    fxo = fzo = fno = 0.0
    res = _np.zeros(6)
    for ci in range(d.ncon):
        c = d.contact[ci]
        if c.geom1 != ggeom and c.geom2 != ggeom:
            continue
        other = c.geom2 if c.geom1 == ggeom else c.geom1
        oname = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, int(other)) or ""
        mujoco.mj_contactForce(m, d, ci, res)
        R = c.frame
        wx = R[0] * res[0] + R[1] * res[1] + R[2] * res[2]
        wz = R[6] * res[0] + R[7] * res[1] + R[8] * res[2]
        s = 1.0 if c.geom2 == ggeom else -1.0
        mag = math.sqrt(wx * wx + wz * wz)
        if oname.startswith("ball_geom"):
            fx += s * wx
            fz += s * wz
            fnorm += mag
        else:
            fxo += s * wx
            fzo += s * wz
            fno += mag
    return fx, fz, fnorm, fxo, fzo, fno


class Rig(object):
    """一份 XML = 一个轮间夹口档位的台架。"""

    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path)
        self.m = mujoco.MjModel.from_xml_string(open(path, encoding="utf-8").read())
        self.d = mujoco.MjData(self.m)
        m = self.m
        gid = lambda o, n: mujoco.mj_name2id(m, o, n)
        self.aid = gid(mujoco.mjtObj.mjOBJ_ACTUATOR, "paddle_vel")
        self.jid = gid(mujoco.mjtObj.mjOBJ_JOINT, "paddle_joint")
        gb = gid(mujoco.mjtObj.mjOBJ_BODY, "gate_leaf")
        self.mc = int(m.body_mocapid[gb]) if gb >= 0 else -1
        self.gg = gid(mujoco.mjtObj.mjOBJ_GEOM, "gate_blade")
        self.fw = [gid(mujoco.mjtObj.mjOBJ_ACTUATOR, "fw_upper_vel"),
                   gid(mujoco.mjtObj.mjOBJ_ACTUATOR, "fw_lower_vel")]
        self.wj = [gid(mujoco.mjtObj.mjOBJ_JOINT, "fw_upper"),
                   gid(mujoco.mjtObj.mjOBJ_JOINT, "fw_lower")]
        self.balls, self.need = [], []
        for k in range(1, 9):
            b = gid(mujoco.mjtObj.mjOBJ_BODY, "ball_%d" % k)
            if b < 0:
                break
            gg = gid(mujoco.mjtObj.mjOBJ_GEOM, "ball_geom_%d" % k)
            self.balls.append(b)
            self.need.append(82 if float(m.geom_size[gg][0]) > 0.040 else 64)

    def reset(self, ph):
        mujoco.mj_resetDataKeyframe(self.m, self.d, min(ph, max(self.m.nkey - 1, 0)))
        w = a.fw_rpm * 2.0 * math.pi / 60.0
        self.d.ctrl[self.fw[0]], self.d.ctrl[self.fw[1]], self.d.ctrl[self.aid] = -w, w, 0.0
        if self.mc >= 0:
            self.d.mocap_pos[self.mc] = (GX * MM, 0.0, GZ_DN * MM)
            self.d.mocap_quat[self.mc] = (1.0, 0.0, 0.0, 0.0)
        mujoco.mj_forward(self.m, self.d)

    def xfer(self, dst):
        """把一个档位的完整状态搬到另一个档位模型（结构必须一致）。"""
        if (dst.m.nq, dst.m.nv, dst.m.na) != (self.m.nq, self.m.nv, self.m.na):
            raise SystemExit("两个模型结构不一致，不能换档")
        dst.d.qpos[:] = self.d.qpos[:]
        dst.d.qvel[:] = self.d.qvel[:]
        dst.d.ctrl[:] = self.d.ctrl[:]
        if dst.m.na:
            dst.d.act[:] = self.d.act[:]
        mujoco.mj_forward(dst.m, dst.d)


MAIN_PATH = SINGLE if SINGLE else PAIR_PATHS[64]
PAIR = dict((k, Rig(v)) for k, v in PAIR_PATHS.items())
if PAIR:
    _n0, _n1 = PAIR[64].need, PAIR[82].need
    if _n0 != _n1:
        raise SystemExit("两个档位模型的球径序列不一致: %s vs %s" % (_n0, _n1))
rig = PAIR[64] if PAIR else Rig(SINGLE)
cur_nip = rig.need[0]
rig.reset(a.ph)
PH0 = [0.0, 30.0, 60.0, 90.0, 120.0, 150.0][min(a.ph, 5)]
print("### 挡舌口径(实跑): x=%.1f 厚%.0f 宽%.0f 高%.0f  中心 %.1f -> %.1f mm"
      "  下端 %.1f -> %.1f mm  行程 %.0f mm"
      "  全行程用时 %.2f s = %.0f mm/s  (--gate-ramp)  闸门逻辑: 停稳+%.2f s 抬起"
      % (GX, GT, 108.0, 55.0, GZ_DN, GZ_UP, GZ_DN - 27.5, GZ_UP - 27.5, GZ_UP - GZ_DN, GRAMP,
         (GZ_UP - GZ_DN) / GRAMP, GDELAY), flush=True)

VIEW, SLOW, VW, T0 = bool(a.view), max(0.05, float(a.slow)), None, 0.0
TPRINT = 0.0
if VIEW:
    import mujoco.viewer
    T0 = time.time()


def open_view(r):
    """开（或换）一个交互窗口，并把机位定到一眼能看到全部机构的侧视。"""
    global VW
    if VW is not None:
        try:
            VW.close()
        except Exception:
            pass
    VW = mujoco.viewer.launch_passive(r.m, r.d)
    VW.cam.azimuth = 90.0
    VW.cam.elevation = -8.0
    VW.cam.distance = 0.60
    VW.cam.lookat[:] = (0.140, 0.0, 0.120)
    return VW


if VIEW:
    open_view(rig)
nb = len(rig.balls)
dt = rig.m.opt.timestep
kt = max(1, int(round(0.002 / dt)))

exits, spilled, inside = [None] * nb, [None] * nb, [False] * nb
peak, peak_t = [0.0] * nb, [0.0] * nb
phase, t_ph, kk, J0 = "settle", 0.0, 0, None
sweep_end = reindex_end = 0.0
cmd, g, t_park, started = 0.0, 0.0, None, False
pend, pend_t, nswitch, t_done = cur_nip, None, 0, None
glog, glast, glup = [], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]

for i in range(int(a.sec / dt)):
    t = i * dt
    m, d = rig.m, rig.d
    if phase == "settle":
        d.ctrl[rig.aid] = 0.0
        if t + 0.5 * dt >= SETTLE:
            phase, t_ph = "settle_tail", t
    J = math.degrees(d.qpos[rig.jid])
    if phase == "settle_tail":
        d.ctrl[rig.aid] = 0.0
        if t - t_ph >= HOLD:
            phase = "sweep"
            if J0 is None:
                J0 = J
            sweep_end = J0 + 360.0 * kk + SWEEP
            reindex_end = J0 + 360.0 * (kk + 1)
    elif phase in ("sweep", "reindex"):
        d.ctrl[rig.aid] = W
        if phase == "sweep" and J >= sweep_end:
            phase = "reindex"
        if J >= reindex_end:
            phase, t_ph, kk = "settle_tail", t, kk + 1
    else:
        d.ctrl[rig.aid] = 0.0
    if abs(float(d.ctrl[rig.aid])) > 1e-9:
        started = True
    # ---------------- 挡舌 ----------------
    if rig.mc >= 0:
        if not started:
            cmd = 0.0
        elif float(d.ctrl[rig.aid]) == 0.0:
            if t_park is None:
                t_park = t
            dtp = t - t_park
            if GDELAY <= dtp <= GDELAY + GMAXOPEN:
                cmd = 1.0
                for k, bid in enumerate(rig.balls):
                    p = d.xpos[bid] * 1000.0
                    if p[0] >= GX:
                        continue
                    if p[0] + float(m.geom_size[m.body_geomadr[bid]][0]) * 1000.0 \
                       < GX - GT / 2.0 - GMARG:
                        cmd = 0.0
                        break
            else:
                cmd = 0.0
        else:
            cmd = 0.0
            t_park = None
        rate = dt / GRAMP
        dl = cmd - g
        g = cmd if abs(dl) <= rate else g + math.copysign(rate, dl)
        d.mocap_pos[rig.mc] = (GX * MM, 0.0, (GZ_DN + (GZ_UP - GZ_DN) * g) * MM)
        d.mocap_quat[rig.mc] = (1.0, 0.0, 0.0, 0.0)
    # ---------------- 待机停位保持（真实舵机不自由下垂）----------------
    if abs(float(d.ctrl[rig.aid])) < 1e-9:
        er = math.remainder(math.radians(a.park) - float(d.qpos[rig.jid]), 2.0 * math.pi)
        d.ctrl[rig.aid] = max(-100.0, min(100.0, PKP * er))
    mujoco.mj_step(m, d)
    if VIEW and t >= TPRINT:
        TPRINT = t + 1.0
        _pd = math.degrees(float(d.qpos[int(m.jnt_qposadr[rig.jid])]))
        _rp = [float(d.qvel[int(m.jnt_dofadr[j])]) * 60.0 / (2.0 * math.pi) for j in rig.wj]
        _gz = float(d.mocap_pos[rig.mc][2]) * 1000.0 if rig.mc >= 0 else float("nan")
        _no = sum(1 for k in range(nb) if exits[k] is not None)
        print("  t=%6.2fs  paddle=%7.1fdeg  fw=%+7.0f/%+7.0f rpm  gate=%6.1fmm  out=%d/%d"
              % (t, _pd, _rp[0], _rp[1], _gz, _no, nb), flush=True)
    if VIEW:
        if not VW.is_running():
            break
        VW.sync()
        lag = t / SLOW - (time.time() - T0)
        if lag > 0.0:
            time.sleep(min(0.05, lag))
    if i % kt:
        continue
    if a.gatelog:
        _fx, _fz, _fn, _ox, _oz, _on = gate_load(m, d, rig.gg)
        _gz = float(d.mocap_pos[rig.mc][2]) * 1000.0 if rig.mc >= 0 else float("nan")
        glog.append((round(t, 3), round(cmd, 4), round(g, 4), round(_gz, 2),
                     round(_fx, 4), round(_fz, 4), round(_fn, 4), round(_on, 4)))
        if abs(_fz) > glast[0]:
            glast[0], glast[1] = abs(_fz), t
        if abs(_fx) > glast[2]:
            glast[2], glast[3] = abs(_fx), t
        if 1e-6 < g < 1.0 - 1e-6:
            if abs(_fz) > glup[0]:
                glup[0], glup[1] = abs(_fz), t
            if abs(_fx) > glup[2]:
                glup[2], glup[3] = abs(_fx), t
        if _on > 1.0:
            print("  [挡舌撞静态件] t=%.3f s 合 %.1f N（建模假象，真实件此处开槽）" % (t, _on), flush=True)
        elif _fn > 20.0:
            _bs = "  ".join("b%d x=%6.1f z=%5.1f" % (k + 1, d.xpos[b][0] * 1000.0,
                                                    d.xpos[b][2] * 1000.0)
                            for k, b in enumerate(rig.balls))
            print("  [挡舌受载] t=%.3f s 舌面 z=%6.1f mm  Fx=%8.1f N  Fz=%8.1f N | %s"
                  % (t, _gz, _fx, _fz, _bs), flush=True)
    for k, bid in enumerate(rig.balls):
        p = d.xpos[bid] * 1000.0
        v = math.sqrt(float((d.cvel[bid][3:6] ** 2).sum()))
        if exits[k] is None and v > peak[k]:      # 峰值只统计出膛前（出膛后是自由落体）
            peak[k], peak_t[k] = v, t
        lx, ln = pv2.to_shooter(p[0], p[2])
        if abs(lx) < 15.0 and abs(ln) < 70.0:
            inside[k] = True
        if exits[k] is None and inside[k] and lx > XLIM and abs(ln) < 80.0:
            exits[k] = (round(t, 3), round(v, 2))
        if spilled[k] is None and exits[k] is None and t > 1.0:
            if p[0] > 485.0 or p[2] < -20.0:
                spilled[k] = (round(t, 2), round(p[0], 1), round(p[2], 1))
    if PAIR and phase != "settle":
        nxt = None
        for k in range(nb):
            if exits[k] is None and spilled[k] is None:
                nxt = rig.need[k]
                break
        if nxt is not None and nxt != pend:
            pend, pend_t = nxt, t
        if nxt is not None and nxt != cur_nip and pend_t is not None and t - pend_t >= SW_DELAY:
            rig.xfer(PAIR[nxt])
            rig, cur_nip, nswitch = PAIR[nxt], nxt, nswitch + 1
            if VIEW:
                open_view(rig)
            print("  [换档] t=%6.2f s  轮间夹口 -> %d mm（%s，状态已搬运）" % (t, nxt, rig.name))
    if all((exits[k] is not None) or (spilled[k] is not None) for k in range(nb)):
        if t_done is None:
            t_done = t
        if t - t_done >= 1.0:          # 末颗出膛后再空跑 1 s，让球飞离机构
            break

print("模型 %s  初始相位 ph%s (%g deg)  球数 %d  t_end=%.2f s%s"
      % (os.path.basename(MAIN_PATH), ["000", "030", "060", "090", "120", "150"][min(a.ph, 5)],
         PH0, nb, t, "  换档 %d 次" % nswitch if PAIR else ""))
nok = 0
for k in range(nb):
    if exits[k]:
        nok += 1
        print("  球%d  出膛 t=%6.3f s   速度 %5.2f m/s   （全程峰值 %6.2f m/s @ t=%.3f s）"
              % (k + 1, exits[k][0], exits[k][1], peak[k], peak_t[k]))
    else:
        print("  球%d  未出膛   %s" % (k + 1, ("逸出 %s" % (spilled[k],)) if spilled[k] else "仍在机构内"))
ts = [exits[k][0] for k in range(nb) if exits[k]]
print("真出膛 %d/%d" % (nok, nb))
if ts:
    print("全清 %.2f s（含静置 %.0f s）；从静置结束算每颗平均 %.2f s" % (max(ts), SETTLE, (max(ts) - SETTLE) / max(nok, 1)))
if a.gatelog:
    with open(a.gatelog, "w", encoding="utf-8", newline="") as f:
        f.write("t_s,cmd,g_frac,gate_z_mm,Fx_ball_N,Fz_ball_N,Fabs_ball_N,Fabs_static_N\n")
        for row in glog:
            f.write("%.3f,%.4f,%.4f,%.2f,%.4f,%.4f,%.4f,%.4f\n" % row)
    print("挡舌载荷（接触合力，作用在挡舌上；Fz<0 = 球把挡舌往下拖，抬升要克服）")
    print("  全程峰 |Fz| = %.2f N @ t=%.2f s ；峰 |Fx| = %.2f N @ t=%.2f s"
          % (glast[0], glast[1], glast[2], glast[3]))
    print("  行程段峰 |Fz| = %.2f N @ t=%.2f s ；峰 |Fx| = %.2f N @ t=%.2f s"
          % (glup[0], glup[1], glup[2], glup[3]))
    print("  CSV -> %s（%d 行，采样 2 ms）" % (a.gatelog, len(glog)))
if VIEW:
    print("窗口保持打开，看完按 Esc 或关窗口结束。")
    while VW.is_running():
        VW.sync()
        time.sleep(0.02)
