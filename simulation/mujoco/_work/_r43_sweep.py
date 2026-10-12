import sys, os, math
sys.path.insert(0, "simulation/mujoco/_work")
import mujoco, r37_multiball as R
pv2 = R.pv2; MM = R.MM
mix4 = ["POLLEN","NECTAR","POLLEN","NECTAR"]
pv2.HALF_SPACING = 86/2.0 + R.WHEEL_R
pv2.R_CARRY = R.R_IN - R.SP["NECTAR"]["r"]
pv2.PIVOT_X, pv2.PIVOT_Z = R.PIVOT
pv2.R_IN = R.R_IN; pv2.R_OUT = R.R_IN + pv2.SHELL_WALL
R.TRAY_X1 = 350.0
pv2.static_geoms = (lambda: R.R10.stat(R.CUT_X, R.A_LIP, tray_x1=R.TRAY_X1))
T = R.TILT; ct, st = math.cos(math.radians(T)), math.sin(math.radians(T))
S = 42.0
GPX = R.CUT_X + S*ct; GPZ = pv2.tray_top_z(R.CUT_X) + S*st
ux, uz = -st, ct
QS = "%.9f %.9f %.9f %.9f" % tuple(pv2.quat_y(-T))

def gate_xml(kind, h=50.0, t=5.0, w=90.0, k=0.20, mass=0.02, clear=3.0):
    t2, w2, h2 = t/2.0, w/2.0, h/2.0
    if kind == "flex":
        bx, bz = GPX + ux*clear, GPZ + uz*clear
        return ('  <body name="gate" pos="%.9f 0 %.9f" quat="%s">\n'
                '    <joint name="gate_joint" type="hinge" axis="0 1 0" pos="0 0 0" stiffness="%g" damping="0.002"/>\n'
                '    <geom name="gate_geom" type="box" size="%.9f %.9f %.9f" pos="0 0 %.9f" friction="0.30 0.02 0.0001" mass="%g"/>\n'
                '  </body>\n') % (bx*MM, bz*MM, QS, k, t2*MM, w2*MM, h2*MM, h2*MM, mass)
    if kind == "pawl":
        hx, hz = GPX + ux*(clear+h), GPZ + uz*(clear+h)
        return ('  <body name="gate" pos="%.9f 0 %.9f" quat="%s">\n'
                '    <joint name="gate_joint" type="hinge" axis="0 1 0" pos="0 0 0" stiffness="0" damping="0.002"/>\n'
                '    <geom name="gate_geom" type="box" size="%.9f %.9f %.9f" pos="0 0 -%.9f" friction="0.30 0.02 0.0001" mass="%g"/>\n'
                '  </body>\n') % (hx*MM, hz*MM, QS, t2*MM, w2*MM, h2*MM, h2*MM, mass)
    return ""

_m0, _d0, _a0, _j0, _me0, _w0, _xml0 = R.build_multi(mix4, 0.0, 86.0, 0.60)
_pos0, _st0, _ic0 = R.place_queue(mix4, 0.0)

def shift_out(pos):
    out = list(pos)
    for k in range(1, len(out)):
        r = R.SP[mix4[k]]["r"]
        px, pz = out[k]
        proj = (px - GPX)*ct + (pz - GPZ)*st
        if proj < r + 1.0:
            dd = r + 1.0 - proj
            out[k] = (px + dd*ct, pz + dd*st)
    for k in range(1, len(out)):
        rp, r = R.SP[mix4[k-1]]["r"], R.SP[mix4[k]]["r"]
        need = rp + r + R.GAP
        dd = math.hypot(out[k][0]-out[k-1][0], out[k][1]-out[k-1][1])
        if dd < need:
            out[k] = (out[k][0] + (need-dd)*ct, out[k][1] + (need-dd)*st)
    return out

def run(label, kind, **kw):
    gx = gate_xml(kind, **kw) if kind else ""
    pos = shift_out(_pos0) if gx else list(_pos0)
    src = pos[1:]
    xml = _xml0.replace("  <worldbody>", "  <worldbody>\n" + gx, 1)
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    jid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "paddle_joint")
    m.dof_damping[m.jnt_dofadr[jid]] = 1e6
    gj = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "gate_joint")
    ga = m.jnt_qposadr[gj] if gj >= 0 else -1
    for k in range(len(src)):
        fj = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "ball_free_%d" % (k+1))
        a = m.jnt_qposadr[fj]
        d.qpos[a:a+3] = [src[k][0]*MM, 0.0, src[k][1]*MM]
        d.qpos[a+3:a+7] = [1,0,0,0]
    for k in range(len(src), len(mix4)):
        fj = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "ball_free_%d" % (k+1))
        a = m.jnt_qposadr[fj]
        d.qpos[a:a+3] = [700.0*MM, 0.0, 300.0*MM]
    d.ctrl[:] = 0.0
    mujoco.mj_forward(m, d)
    dt = m.opt.timestep
    x0 = [p[0] for p in src]
    gmax = 0.0; xpass = None
    prev = x0[0]
    for i in range(int(6.0/dt) + 1):
        fj = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "ball_free_1")
        xb = d.qpos[m.jnt_qposadr[fj]]/MM
        vmax = abs(xb - prev)/dt; prev = xb
        if ga >= 0:
            ang = abs(d.qpos[ga])
            if ang > gmax: gmax = ang
        if xpass is None and xb < 15.0:
            xpass = i*dt
        mujoco.mj_step(m, d)
    xs = []
    for k in range(len(mix4)):
        fj = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "ball_free_%d" % (k+1))
        xs.append(d.qpos[m.jnt_qposadr[fj]]/MM)
    print("%-24s x0=%6.1f -> x1=%7.1f 到发射位%6s  挡件峰角%6.1fdeg  x=(%s)"
          % (label, x0[0], xs[0], ("%.2fs" % xpass) if xpass is not None else " 未达",
             math.degrees(gmax), " ".join("%6.1f" % v for v in xs)), flush=True)

print("### B1(flex/弹性片) vs B2(pawl/自重挡爪) 排队筛选  s=42 h=50 mu球-挡0.30")
run("none 无挡件", None)
for kk, mm in ((0.002,0.002),(0.008,0.003),(0.02,0.005),(0.05,0.008),(0.20,0.02),(0.50,0.05)):
    run("B1 flex k=%.3f m=%.3f" % (kk, mm), "flex", k=kk, mass=mm)
for mm in (0.002, 0.005, 0.02, 0.05):
    run("B2 pawl m=%.3f" % mm, "pawl", mass=mm)
for kk, mm in ((0.008,0.003),(0.02,0.005)):
    run("B1 flex h=22 k=%.3f" % kk, "flex", k=kk, mass=mm, h=22.0)
for mm in (0.005, 0.02):
    run("B2 pawl h=22 m=%.3f" % mm, "pawl", mass=mm, h=22.0)
