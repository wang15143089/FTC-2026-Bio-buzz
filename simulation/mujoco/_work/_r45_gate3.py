# -*- coding: utf-8 -*-
"""R45 台架 v3：挡舌改「从上方竖直下插」（全宽，只做 z 向平移，绕开竖直轴摆动路线）。

为什么放弃侧向摆入：闸位 x≈98 处托盘没有 +y 侧导槽壁（导槽壁只到 x=12.5），球可横向游到 y≈±54，
故挡舌必须横跨 108mm 全宽(L≈106)；而 L≈106 的摆程扫掠半径 106mm > 球窝球到铰心 100.3mm，
关门必扫球窝球。短挡舌(实测 L=40)挡不住：球从舌尖外侧绕过(y漂到+42.9)滚过闸口。两条约束互斥。

本方案：全宽挡舌 x[95.5 100.5] y[-54 54]：
  下插(挡) z[20 75]  -> 全宽横断通道，球无法前后绕行；舌顶 75 > 球心高(NECTAR 63.8)，球不能爬过
  抬起(放) z[112 167] -> 底缘 112 > 通道内球顶(NECTAR 109.7)；顶缘 167 < 下飞轮底 167.5
竖直运动不产生横向扫掠 -> 永不碰球窝里的球；下插落在前球尾部/两球之间，前球被推下坡、后球被挡回。
关窗逻辑：抬起后等"被送那颗球整体越过闸口面(tail < 92.5)"就下插，后球此刻仍远在 40mm 外。
"""
import sys, os, math, csv

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mujoco
import r37_multiball as R

pv2 = R.pv2
MM = R.MM
D = math.degrees

argv = sys.argv[1:]
GATE_ON = True
CLAMP_ON = None
GX = 98.0
GW, GH, GT = 108.0, 55.0, 5.0
GZ_DN, GZ_UP = 47.5, 139.5          # 下插/抬起时的舌片中心 z（行程 92mm）
GY = 0.0
GL = GH
GOUT = 0.0
GRAMP = 0.15
GDELAY, GWIN = 0.10, 0.00
GMARG, GMAXOPEN = 3.0, 3.00
GMU = 0.40
GPRIO = 2
liner_shell, paddle_mu = -1.0, -1.0
dump = False
keep = []
i = 0
while i < len(argv):
    a_ = argv[i]
    if a_ == "--gate-off":
        GATE_ON = False; i += 1; continue
    if a_ == "--clamp-on":
        CLAMP_ON = True; i += 1; continue
    if a_ == "--clamp-off":
        CLAMP_ON = False; i += 1; continue
    if a_ == "--gate-dump":
        dump = True; i += 1; continue
    if a_ == "--liner-shell" and i + 1 < len(argv):
        liner_shell = float(argv[i + 1]); i += 2; continue
    if a_ == "--paddle-mu" and i + 1 < len(argv):
        paddle_mu = float(argv[i + 1]); i += 2; continue
    if a_.startswith("--gate-") and i + 1 < len(argv):
        v = float(argv[i + 1])
        if   a_ == "--gate-x":     GX = v
        elif a_ == "--gate-y":     GY = v
        elif a_ == "--gate-z":     GZ = v
        elif a_ == "--gate-l":     GL = v
        elif a_ == "--gate-h":     GH = v
        elif a_ == "--gate-t":     GT = v
        elif a_ == "--gate-ramp":  GRAMP = v
        elif a_ == "--gate-delay": GDELAY = v
        elif a_ == "--gate-win":   GWIN = v
        elif a_ == "--gate-mu":    GMU = v
        elif a_ == "--gate-margin":  GMARG = v
        elif a_ == "--gate-maxopen": GMAXOPEN = v
        elif a_ == "--gate-prio":  GPRIO = int(v)
        elif a_ == "--gate-out":   GOUT = math.radians(v)
        else:
            keep.append(a_); keep.append(argv[i + 1])
        i += 2; continue
    keep.append(a_); i += 1

FACE = GX + GT / 2.0
CLAMP = GATE_ON if CLAMP_ON is None else CLAMP_ON
print("### R45 竖向挡舌(全宽, z 向平移): x=%.1f t=%.0f w=%.0f h=%.0f mu=%.2f | 延时%.2fs 最长抬%.2fs 行程%.1fmm 用时%.2fs | 门=%s 夹列=%s"
      % (GX, GT, GW, GH, GMU, GDELAY, GMAXOPEN, GZ_UP - GZ_DN, GRAMP,
         "有" if GATE_ON else "无", CLAMP), flush=True)
if GATE_ON:
    print("###   下插 舌片 x[%.1f %.1f] y[%.1f %.1f] z[%.1f %.1f]"
          % (GX - GT / 2, GX + GT / 2, -GW / 2, GW / 2, GZ_DN - GH / 2, GZ_DN + GH / 2), flush=True)
    print("###   抬起 舌片 x[%.1f %.1f] y[%.1f %.1f] z[%.1f %.1f]"
          % (GX - GT / 2, GX + GT / 2, -GW / 2, GW / 2, GZ_UP - GH / 2, GZ_UP + GH / 2), flush=True)

GBODY = ('  <body name="gate_leaf" mocap="true" pos="%.9f %.9f %.9f">\n'
         '    <geom name="gate_blade" type="box" size="%.9f %.9f %.9f" pos="0 0 0" '
         'friction="%g 0.02 0.0001" rgba="0.90 0.22 0.28 1" mass="%.6f"/>\n'
         '  </body>\n') % (GX * MM, 0.0, GZ_DN * MM, GT / 2 * MM, GW / 2 * MM, GH / 2 * MM,
                          GMU, GT * GW * GH * 1e-9 * 1180.0)

NO_GATE = [False]
ST = dict(t=0.0, model=None, moc=-1, aid_p=-1, jid_p=-1, started=False,
          t_park=None, cmd=0.0, g=0.0, gt=0.0, log=[], rows=[], nopen=0, topen=0.0,
          phase=None, t_open=None, balls=[])

_orig_step = mujoco.mj_step


def _hook(m, d):
    if ST["model"] is not m:
        ST["model"] = m
        ST["aid_p"] = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "paddle_vel")
        ST["jid_p"] = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "paddle_joint")
        gb = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "gate_leaf")
        ST["moc"] = int(m.body_mocapid[gb]) if gb >= 0 else -1
        ST["balls"] = []
        for k in range(1, 9):
            b = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball_%d" % k)
            if b < 0:
                break
            gid = int(m.body_geomadr[b])
            ST["balls"].append((b, float(m.geom_size[gid][0]) * 1000.0))
    ST["t"] += float(m.opt.timestep)
    if ST["moc"] >= 0:
        if abs(float(d.ctrl[ST["aid_p"]])) > 1e-9:
            ST["started"] = True
            ST["t_park"] = None
            ST["phase"] = None
            cmd = 0.0
        elif ST["started"]:
            if ST["t_park"] is None:
                ST["t_park"] = ST["t"]
            dtp = ST["t"] - ST["t_park"]
            if ST["phase"] is None and dtp >= GDELAY:
                ST["phase"] = 1
                ST["t_open"] = ST["t"]
            if ST["phase"] == 1:
                cmd = 1.0
                for (bid, rr) in ST["balls"]:
                    p = d.xpos[bid] * 1000.0
                    if p[0] >= GX:
                        continue
                    if p[0] + rr < GX - GT / 2.0 - GMARG:
                        ST["log"].append((round(ST["t"], 2), "球已过闸口"))
                        cmd = 0.0
                        break
                if cmd < 0.5 or (ST["t"] - ST["t_open"] > GMAXOPEN):
                    ST["phase"] = 2
                    cmd = 0.0
            else:
                cmd = 0.0
        else:
            cmd = 0.0
        if cmd != ST["cmd"]:
            ST["log"].append((round(ST["t"], 2), "抬起" if cmd > 0 else "下插"))
            ST["cmd"] = cmd
            if cmd > 0:
                ST["nopen"] += 1
        ST["gt"] = cmd
        dlt = ST["gt"] - ST["g"]
        rate = float(m.opt.timestep) / GRAMP
        ST["g"] = ST["gt"] if abs(dlt) <= rate else ST["g"] + math.copysign(rate, dlt)
        zc = GZ_DN + (GZ_UP - GZ_DN) * ST["g"]
        d.mocap_pos[ST["moc"]] = (GX * MM, 0.0, zc * MM)
        d.mocap_quat[ST["moc"]] = (1.0, 0.0, 0.0, 0.0)
    if dump and (not ST["rows"] or ST["t"] - ST["rows"][-1][0] >= 0.01):
        row = [round(ST["t"], 3), round(GZ_DN + (GZ_UP - GZ_DN) * ST["g"], 1),
               round(D(d.qpos[ST["jid_p"]]) % 360.0, 1),
               round(float(d.ctrl[ST["aid_p"]]), 2), round(ST["g"], 2)]
        for k in range(1, 7):
            b = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball_%d" % k)
            if b < 0:
                break
            p = d.xpos[b] * 1000.0
            row += [round(p[0], 1), round(p[1], 1), round(p[2], 1)]
        ST["rows"].append(row)
    _orig_step(m, d)


mujoco.mj_step = _hook

_orig_build = R.build_multi


def build_patch(mix, ph0, nip, mu=R.MU):
    out = _orig_build(mix, ph0, nip, mu)
    if not GATE_ON or NO_GATE[0]:
        return out
    m, d, aid, jid, meta, w, xml = out
    xml2 = xml.replace("  <worldbody>", "  <worldbody>\n" + GBODY, 1)
    m2 = mujoco.MjModel.from_xml_string(xml2)
    d2 = mujoco.MjData(m2)
    d2.ctrl[:] = d.ctrl[:]
    aid2 = mujoco.mj_name2id(m2, mujoco.mjtObj.mjOBJ_ACTUATOR, "paddle_vel")
    jid2 = mujoco.mj_name2id(m2, mujoco.mjtObj.mjOBJ_JOINT, "paddle_joint")
    meta2 = []
    for k in range(1, len(mix) + 1):
        bid = mujoco.mj_name2id(m2, mujoco.mjtObj.mjOBJ_BODY, "ball_%d" % k)
        fj = mujoco.mj_name2id(m2, mujoco.mjtObj.mjOBJ_JOINT, "ball_free_%d" % k)
        meta2.append(dict(bid=bid, qadr=m2.jnt_qposadr[fj], dadr=m2.jnt_dofadr[fj]))
    d2.qpos[jid2] = math.radians(ph0)
    gb = mujoco.mj_name2id(m2, mujoco.mjtObj.mjOBJ_BODY, "gate_leaf")
    mc = int(m2.body_mocapid[gb])
    d2.mocap_pos[mc] = (GX * MM, 0.0, GZ_DN * MM)
    d2.mocap_quat[mc] = (1.0, 0.0, 0.0, 0.0)
    mujoco.mj_forward(m2, d2)
    out = (m2, d2, aid2, jid2, meta2, w, xml2)
    mm = out[0]
    for g in range(mm.ngeom):
        nm = mujoco.mj_id2name(mm, mujoco.mjtObj.mjOBJ_GEOM, g) or ""
        if nm.startswith("shell_") or nm.startswith("r10_"):
            if liner_shell >= 0.0:
                mm.geom_friction[g][0] = liner_shell
                mm.geom_priority[g] = 2
        elif nm.startswith("tray") or nm.startswith("ramp"):
            if liner_shell >= 0:
                mm.geom_friction[g][0] = liner_shell
                mm.geom_priority[g] = 2
        elif nm.startswith("paddle"):
            mm.geom_friction[g][0] = (paddle_mu if paddle_mu >= 0 else 0.70)
            mm.geom_priority[g] = 2
        elif nm.startswith("gate"):
            mm.geom_friction[g][0] = GMU
            mm.geom_priority[g] = GPRIO
    R._PROBE.clear()
    return out


R.build_multi = build_patch

_orig_pq = R.place_queue


def place_queue_patch(mix, ph0=0.0):
    """第 1 颗照旧停在球窝（无挡舌模型里量），第 2 颗起沿坡相切排到挡舌后方 x>=闭合面。"""
    NO_GATE[0] = True
    try:
        base, stacked, nch = _orig_pq(mix, ph0)
    finally:
        NO_GATE[0] = False
    if not CLAMP:
        print("   [初始球列] 不夹列: " + " | ".join("b%d x=%.1f z=%.1f" % (k + 1, p[0], p[1])
                                                   for k, p in enumerate(base)), flush=True)
        return base, stacked, nch
    n = len(mix)
    ct = math.cos(math.radians(R.TILT))
    st_ = math.sin(math.radians(R.TILT))
    pos = [base[0]]
    for k in range(1, n):
        rp, r = R.SP[mix[k - 1]]["r"], R.SP[mix[k]]["r"]
        x = pos[k - 1][0] + (rp + r + R.GAP) * ct
        if x < FACE + r + R.ALLOW:
            x = FACE + r + R.ALLOW
        z = pv2.tray_top_z(x + r * st_) + r * ct
        if x + r > R.TRAY_X1:
            print("   [警告] 球%d 尾缘 x=%.1f 超出托板 %.1f" % (k + 1, x + r, R.TRAY_X1), flush=True)
        pos.append((x, z))
    print("   [初始球列] " + " | ".join("b%d x=%.1f z=%.1f" % (k + 1, p[0], p[1])
                                        for k, p in enumerate(pos)), flush=True)
    return pos, 0, n


if CLAMP:
    R.place_queue = place_queue_patch

sys.argv = [os.path.join(HERE, "r38_v8.py")] + keep
_src = open(os.path.join(HERE, "r38_v8.py"), encoding="utf-8").read()
try:
    exec(compile(_src, os.path.join(HERE, "r38_v8.py"), "exec"),
         {"__name__": "__main__", "__file__": os.path.join(HERE, "r38_v8.py")})
finally:
    print("### 挡舌动作序列（%d 次摆出）: %s" % (ST["nopen"], ST["log"][:26]), flush=True)
    if dump and ST["rows"]:
        p = os.path.join(HERE, "..", "out", "_r45_gate_diag.csv")
        ncol = len(ST["rows"][0])
        hdr = ["t", "gate", "J", "pctrl", "gon"]
        for k in range((ncol - 5) // 3):
            hdr += ["b%d_x" % (k + 1), "b%d_y" % (k + 1), "b%d_z" % (k + 1)]
        with open(p, "w", newline="", encoding="utf-8") as f:
            cw = csv.writer(f); cw.writerow(hdr); cw.writerows(ST["rows"])
        print("### diag -> %s (%d 行)" % (p, len(ST["rows"])), flush=True)
