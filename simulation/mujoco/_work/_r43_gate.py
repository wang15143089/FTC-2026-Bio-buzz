# -*- coding: utf-8 -*-
"""R43 台架：托板加长 + 分球挡球件（fixed / flex / pawl）。"""
import sys, os, math

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mujoco
import r37_multiball as R

pv2 = R.pv2
MM = R.MM

argv = sys.argv[1:]
GATE = "none"
GATE_S = 42.0
GATE_H = 50.0
GATE_T = 5.0
GATE_W = 90.0
GATE_K = 0.20
GATE_M = 0.02
GATE_CLEAR = 3.0
liner_shell = -1.0
liner_tray = -1.0
paddle_mu = -1.0
tray_hdr = None
no_pq_fix = False
keep = []
i = 0
while i < len(argv):
    a_ = argv[i]
    if a_ == "--gate" and i + 1 < len(argv):        GATE = argv[i + 1].lower();  i += 2; continue
    if a_ == "--gate-s" and i + 1 < len(argv):      GATE_S = float(argv[i + 1]); i += 2; continue
    if a_ == "--gate-h" and i + 1 < len(argv):      GATE_H = float(argv[i + 1]); i += 2; continue
    if a_ == "--gate-t" and i + 1 < len(argv):      GATE_T = float(argv[i + 1]); i += 2; continue
    if a_ == "--gate-w" and i + 1 < len(argv):      GATE_W = float(argv[i + 1]); i += 2; continue
    if a_ == "--gate-k" and i + 1 < len(argv):      GATE_K = float(argv[i + 1]); i += 2; continue
    if a_ == "--gate-m" and i + 1 < len(argv):      GATE_M = float(argv[i + 1]); i += 2; continue
    if a_ == "--gate-clear" and i + 1 < len(argv):  GATE_CLEAR = float(argv[i + 1]); i += 2; continue
    if a_ == "--liner-shell" and i + 1 < len(argv): liner_shell = float(argv[i + 1]); i += 2; continue
    if a_ == "--liner-tray" and i + 1 < len(argv):  liner_tray = float(argv[i + 1]); i += 2; continue
    if a_ == "--paddle-mu" and i + 1 < len(argv):   paddle_mu = float(argv[i + 1]); i += 2; continue
    if a_ == "--tray" and i + 1 < len(argv):         tray_hdr = float(argv[i + 1]); keep.append(a_); keep.append(argv[i + 1]); i += 2; continue
    if a_ == "--no-pq-fix":                         no_pq_fix = True; i += 1; continue
    keep.append(a_); i += 1

GATE_PLANE = [0.0, 0.0]
GATE_QADR = -1
GATE_MAXANG = [0.0]
GATE_SUM = [0.0]
GATE_N = [0]

_orig_mjstep = mujoco.mj_step


def _mjstep_hook(m, d):
    _orig_mjstep(m, d)
    if GATE_QADR >= 0:
        v = float(d.qpos[GATE_QADR])
        av = abs(v)
        if av > GATE_MAXANG[0]:
            GATE_MAXANG[0] = av
        GATE_SUM[0] += v
        GATE_N[0] += 1


mujoco.mj_step = _mjstep_hook


def _gate_xml():
    """在托板面沿坡 s=GATE_S 处生成挡球件，底面离托板 GATE_CLEAR。"""
    T = R.TILT
    ct, st = math.cos(math.radians(T)), math.sin(math.radians(T))
    x_cut = R.CUT_X
    z_cut = pv2.tray_top_z(x_cut)
    px = x_cut + GATE_S * ct
    pz = z_cut + GATE_S * st
    ux, uz = -st, ct
    q = pv2.quat_y(-T)
    qs = "%.9f %.9f %.9f %.9f" % tuple(q)
    GATE_PLANE[0], GATE_PLANE[1] = px, pz
    t2, w2, h2 = GATE_T / 2.0, GATE_W / 2.0, GATE_H / 2.0
    c0 = GATE_CLEAR
    if GATE == "fixed":
        cx, cz = px + ux * (c0 + h2), pz + uz * (c0 + h2)
        body = """  <geom name="gate_fixed" type="box" size="{a} {b} {c}" pos="{x} 0 {z}" quat="{q}" friction="0.40 0.02 0.0001" rgba="0.55 0.25 0.75 1"/>
""".format(a=t2 * MM, b=w2 * MM, c=h2 * MM, x=cx * MM, z=cz * MM, q=qs)
        return body, "fixed s=%.1f h=%.1f" % (GATE_S, GATE_H)
    if GATE == "flex":
        bx, bz = px + ux * c0, pz + uz * c0
        body = """  <body name="gate" pos="{x} 0 {z}" quat="{q}">
    <joint name="gate_joint" type="hinge" axis="0 1 0" pos="0 0 0" stiffness="{k}" damping="0.002" armature="0.00001"/>
    <geom name="gate_geom" type="box" size="{a} {b} {c}" pos="0 0 {c}" friction="0.30 0.02 0.0001" rgba="0.30 0.75 0.45 1" mass="{m}"/>
  </body>
""".format(x=bx * MM, z=bz * MM, q=qs, k=GATE_K, a=t2 * MM, b=w2 * MM, c=h2 * MM, m=GATE_M * 0.25)
        return body, "flex s=%.1f h=%.1f k=%.3f clear=%.1f" % (GATE_S, GATE_H, GATE_K, c0)
    if GATE == "pawl":
        hx, hz = px + ux * (c0 + GATE_H), pz + uz * (c0 + GATE_H)
        body = """  <body name="gate" pos="{x} 0 {z}" quat="{q}">
    <joint name="gate_joint" type="hinge" axis="0 1 0" pos="0 0 0" stiffness="0" damping="0.002" armature="0.00001"/>
    <geom name="gate_geom" type="box" size="{a} {b} {c}" pos="0 0 -{c}" friction="0.30 0.02 0.0001" rgba="0.90 0.50 0.15 1" mass="{m}"/>
  </body>
""".format(x=hx * MM, z=hz * MM, q=qs, a=t2 * MM, b=w2 * MM, c=h2 * MM, m=GATE_M)
        return body, "pawl s=%.1f h=%.1f m=%.3f clear=%.1f" % (GATE_S, GATE_H, GATE_M, c0)
    return "", "none"


GATE_XML, GATE_DESC = _gate_xml()
print("### R43 分球台架: gate=%s | 外罩mu=%s 托板mu=%s 拨杆mu=%.2f | tray=%.0f"
      % (GATE_DESC,
         "%.2f" % liner_shell if liner_shell >= 0 else "off",
         "%.2f" % liner_tray if liner_tray >= 0 else "off",
         paddle_mu if paddle_mu >= 0 else 0.70, tray_hdr if tray_hdr is not None else R.TRAY_X1), flush=True)


def _shift_out_of_gate(pos, mix, i0):
    """把与挡球件重叠的球沿坡向后（+s）挪开。"""
    ct, st = math.cos(math.radians(R.TILT)), math.sin(math.radians(R.TILT))
    gx, gz = GATE_PLANE
    for k in range(i0, len(pos)):
        r = R.SP[mix[k]]["r"]
        px, pz = pos[k]
        proj = (px - gx) * ct + (pz - gz) * st
        if proj < r + 1.0:
            dd = r + 1.0 - proj
            px += dd * ct; pz += dd * st
        pos[k] = (px, pz)
    return pos


_orig_pq = R.place_queue


def place_queue_patch(mix, ph0=0.0):
    pos, stacked, in_ch = _orig_pq(mix, ph0)
    if not GATE_XML or no_pq_fix:
        return pos, stacked, in_ch
    pos = list(pos)
    pos = _shift_out_of_gate(pos, mix, 1)
    for k in range(1, len(pos)):
        rp, r = R.SP[mix[k - 1]]["r"], R.SP[mix[k]]["r"]
        need = rp + r + R.GAP
        ct, st = math.cos(math.radians(R.TILT)), math.sin(math.radians(R.TILT))
        qx, qz = pos[k - 1]
        dd = math.hypot(pos[k][0] - qx, pos[k][1] - qz)
        if dd < need:
            pos[k] = (pos[k][0] + (need - dd) * ct, pos[k][1] + (need - dd) * st)
        xt = pos[k][0] + r
        if xt > R.TRAY_X1:
            print("   [警告] 球%d 尾缘 x=%.1f 超出托板 TRAY_X1=%.1f" % (k + 1, xt, R.TRAY_X1), flush=True)
    return pos, stacked, in_ch


R.place_queue = place_queue_patch

_orig = R.build_multi


def build_patch(mix, ph0, nip, mu=0.40):
    m, d, aid, jid, meta, w, xml = _orig(mix, ph0, nip, mu)
    if not GATE_XML:
        out = (m, d, aid, jid, meta, w, xml)
    else:
        xml2 = xml.replace("  <worldbody>", "  <worldbody>\n" + GATE_XML, 1)
        m2 = mujoco.MjModel.from_xml_string(xml2)
        d2 = mujoco.MjData(m2)
        d2.ctrl[:] = d.ctrl
        aid2 = mujoco.mj_name2id(m2, mujoco.mjtObj.mjOBJ_ACTUATOR, "paddle_vel")
        jid2 = mujoco.mj_name2id(m2, mujoco.mjtObj.mjOBJ_JOINT, "paddle_joint")
        meta2 = []
        for k in range(1, len(mix) + 1):
            bid = mujoco.mj_name2id(m2, mujoco.mjtObj.mjOBJ_BODY, "ball_%d" % k)
            fj = mujoco.mj_name2id(m2, mujoco.mjtObj.mjOBJ_JOINT, "ball_free_%d" % k)
            meta2.append(dict(bid=bid, qadr=m2.jnt_qposadr[fj], dadr=m2.jnt_dofadr[fj]))
        d2.qpos[jid2] = math.radians(ph0)
        mujoco.mj_forward(m2, d2)
        gj = mujoco.mj_name2id(m2, mujoco.mjtObj.mjOBJ_JOINT, "gate_joint")
        global GATE_QADR
        GATE_QADR = int(m2.jnt_qposadr[gj]) if gj >= 0 else -1
        out = (m2, d2, aid2, jid2, meta2, w, xml2)
    mm = out[0]
    for g in range(mm.ngeom):
        nm = mujoco.mj_id2name(mm, mujoco.mjtObj.mjOBJ_GEOM, g) or ""
        if nm.startswith("shell_") or nm.startswith("r10_"):
            if liner_shell >= 0.0:
                mm.geom_friction[g][0] = liner_shell
                mm.geom_priority[g] = 2
        elif nm.startswith("tray") or nm.startswith("ramp"):
            if liner_tray >= 0.0:
                mm.geom_friction[g][0] = liner_tray
                mm.geom_priority[g] = 2
        elif nm.startswith("paddle") or nm.startswith("gate"):
            mm.geom_friction[g][0] = (paddle_mu if paddle_mu >= 0 else 0.70)
            mm.geom_priority[g] = 2
    R._PROBE.clear()
    return out


R.build_multi = build_patch

sys.argv = [os.path.join(HERE, "r38_v8.py")] + keep
_src = open(os.path.join(HERE, "r38_v8.py"), encoding="utf-8").read()
try:
    exec(compile(_src, os.path.join(HERE, "r38_v8.py"), "exec"),
         {"__name__": "__main__", "__file__": os.path.join(HERE, "r38_v8.py")})
finally:
    if GATE_QADR >= 0:
        print("### 挡爪摆角: 最大 %.3f rad (%.1f deg), 平均 %.3f rad, 采样 %d"
              % (GATE_MAXANG[0], math.degrees(GATE_MAXANG[0]),
                 (GATE_SUM[0] / GATE_N[0]) if GATE_N[0] else 0.0, GATE_N[0]), flush=True)
