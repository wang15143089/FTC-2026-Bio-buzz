# -*- coding: utf-8 -*-
"""R47 交付附件：直接驱动 R47 MJCF 模型的运行脚本。

XML 只描述模型；挡舌（mocap）与"待机停位"（真实舵机位置保持）是控制逻辑，须外部驱动。
本脚本按 R47 验收口径驱动：
  飞轮 1620 rpm 对向旋转 -> 静置 6 s -> 每颗球: 停 1 s -> 290 rpm 扫 248 deg -> 回位 360 deg/颗
  挡舌: 拨杆停稳后 0.10 s 抬到 z=139.5 mm，被送那颗球尾缘越过闸口面即落回 z=47.5 mm（最长抬 3 s）
  停位: 舵机速度伺服保持 188 deg（真实舵机不自由下垂）
  混装模型对: 每颗球按球径选轮间夹口（POLLEN 64 mm / NECTAR 82 mm），换档时搬运完整状态

用法:
  python run_R47_xml.py                                   # 默认 out/R47_launcher_4xPOLLEN_gap064.xml
  python run_R47_xml.py out/R47_launcher_4xNECTAR_gap082.xml --ph 3
  python run_R47_xml.py --pair                            # 混装模型对（gap064 <-> gap082 自动换档）
"""
import sys, os, math, argparse, importlib.util

import mujoco

ap = argparse.ArgumentParser()
ap.add_argument("xml", nargs="?", default="")
ap.add_argument("--pair", action="store_true", help="跑 out/ 里的混装模型对（按球种自动换档）")
ap.add_argument("--ph", type=int, default=0, help="起始相位 keyframe 索引 0..5 (0/30/60/90/120/150 deg)")
ap.add_argument("--sec", type=float, default=40.0, help="仿真总时长上限 s")
ap.add_argument("--fw-rpm", type=float, default=1620.0)
ap.add_argument("--park", type=float, default=188.0)
a = ap.parse_args()

HERE = os.path.dirname(os.path.abspath(__file__))
OD = lambda n: os.path.join(HERE, "out", n)
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
GX, GT, GMARG, GDELAY, GMAXOPEN, GRAMP = 180.0, 5.0, 3.0, 0.10, 3.00, 0.15
GZ_DN, GZ_UP, PKP = 47.5, 139.5, 40.0
W = RPM * 2.0 * math.pi / 60.0


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
        self.fw = [gid(mujoco.mjtObj.mjOBJ_ACTUATOR, "fw_upper_vel"),
                   gid(mujoco.mjtObj.mjOBJ_ACTUATOR, "fw_lower_vel")]
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
nb = len(rig.balls)
dt = rig.m.opt.timestep
kt = max(1, int(round(0.002 / dt)))

exits, spilled, inside = [None] * nb, [None] * nb, [False] * nb
peak, peak_t = [0.0] * nb, [0.0] * nb
phase, t_ph, kk, J0 = "settle", 0.0, 0, None
sweep_end = reindex_end = 0.0
cmd, g, t_park, started = 0.0, 0.0, None, False
pend, pend_t, nswitch, t_done = cur_nip, None, 0, None

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
    if i % kt:
        continue
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