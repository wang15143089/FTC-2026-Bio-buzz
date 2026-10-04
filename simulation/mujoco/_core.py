def _fmt(v):
    return f"{v:.6f}"


def build_xml(rpm, paddle_omega, spin_sign, ball_x, ball_z, ball_vx=0.0, ball_vz=0.0):
    m = MM
    lines = []
    w = lines.append
    w('<mujoco model="t06_pollen_launcher">')
    w('  <compiler angle="radian" autolimits="true"/>')
    w('  <option timestep="0.0002" gravity="0 0 -9.81" integrator="implicitfast" cone="elliptic"/>')
    w('  <default>')
    w('    <geom friction="0.5 0.01 0.0001" solref="0.008 1" solimp="0.95 0.99 0.001"/>')
    w('    <default class="guide"><geom friction="0.25 0.005 0.0001" rgba="0.2 0.56 0.84 0.55"/></default>')
    w('    <default class="finger"><geom friction="0.2 0.005 0.0001" rgba="0.76 0.88 0.96 0.7"/></default>')
    w('    <default class="flywheel"><geom friction="1.6 0.02 0.0001" solref="0.006 1" rgba="0.18 0.18 0.20 1"/></default>')
    w('    <default class="paddle"><geom friction="0.7 0.01 0.0001" solref="0.006 1" rgba="0.92 0.54 0.12 1"/></default>')
    w('    <default class="ball"><geom friction="1.0 0.02 0.0001" solref="0.010 1" solimp="0.9 0.95 0.002" rgba="0.95 0.85 0.15 1" priority="1"/></default>')
    w('  </default>')
    w('  <worldbody>')
    w('    <light pos="0.2 -0.6 1.0" dir="-0.2 0.6 -1" diffuse="0.8 0.8 0.8"/>')
    for name, panel, cls in static_geoms():
        pieces = clip_drum(panel) if name.startswith(("guide_floor", "guide_roof")) else [panel]
        for k, (center, size, rot) in enumerate(pieces):
            q = quat_y(rot)
            w(f'    <geom name="{name}_{k}" class="{cls}" type="box" '
              f'size="{_fmt(size[0]/2*m)} {_fmt(size[1]/2*m)} {_fmt(size[2]/2*m)}" '
              f'pos="{_fmt(center[0]*m)} {_fmt(center[1]*m)} {_fmt(center[2]*m)}" '
              f'quat="{q[0]:.6f} {q[1]:.6f} {q[2]:.6f} {q[3]:.6f}"/>')
    qx = quat_x(-90)
    for sign, label in ((1, "upper"), (-1, "lower")):
        cx, cy, cz = flywheel_axle_center(sign)
        w(f'  <body name="flywheel_{label}" pos="{_fmt(cx*m)} {_fmt(cy*m)} {_fmt(cz*m)}">')
        w(f'    <joint name="fw_{label}" type="hinge" axis="0 1 0" damping="0.0002"/>')
        w(f'    <geom name="fw_shaft_{label}" class="flywheel" type="cylinder" '
          f'size="{_fmt(4.0*m)} {_fmt(84.0*m)}" quat="{qx[0]:.6f} {qx[1]:.6f} 0 0" mass="{FLYWHEEL_SHAFT_MASS}"/>')
        for i, y in enumerate(WHEEL_Y, 1):
            w(f'    <geom name="fw_{label}_{i}" class="flywheel" type="cylinder" '
              f'size="{_fmt(WHEEL_R*m)} {_fmt(WHEEL_W/2*m)}" pos="0 {_fmt(y*m)} 0" '
              f'quat="{qx[0]:.6f} {qx[1]:.6f} 0 0" mass="{FLYWHEEL_MASS}"/>')
        w('  </body>')
    px, py, pz = PADDLE_CENTER
    w(f'  <body name="paddle" pos="{_fmt(px*m)} {_fmt(py*m)} {_fmt(pz*m)}">')
    w('    <joint name="paddle_joint" type="hinge" axis="0 1 0" damping="0.0005"/>')
    for name, center, half, ang, kind in paddle_parts():
        c = rot_local(center, ang)
        if kind == "cylY":
            w(f'    <geom name="paddle_{name}" class="paddle" type="cylinder" '
              f'size="{_fmt(half[0]*m)} {_fmt(half[1]*m)}" quat="{qx[0]:.6f} {qx[1]:.6f} 0 0" mass="0.05"/>')
        else:
            mass = 0.010 if name.startswith("arm") else (0.020 if name.startswith("blade") else 0.008)
            q = quat_y(ang)
            w(f'    <geom name="paddle_{name}" class="paddle" type="box" '
              f'size="{_fmt(half[0]*m)} {_fmt(half[1]*m)} {_fmt(half[2]*m)}" '
              f'pos="{_fmt(c[0]*m)} {_fmt(c[1]*m)} {_fmt(c[2]*m)}" '
              f'quat="{q[0]:.6f} {q[1]:.6f} {q[2]:.6f} {q[3]:.6f}" mass="{mass}"/>')
    w('  </body>')
    w(f'  <body name="ball" pos="{_fmt(ball_x*m)} 0 {_fmt(ball_z*m)}">')
    w('    <freejoint name="ball_free"/>')
    w(f'    <geom name="ball_geom" class="ball" type="sphere" size="{_fmt(BALL_R*m)}" mass="{BALL_MASS}"/>')
    w('  </body>')
    w('  </worldbody>')
    fw_target = spin_sign * rpm * 2.0 * math.pi / 60.0
    w('  <actuator>')
    w(f'    <velocity name="fw_upper_vel" joint="fw_upper" kv="0.5" ctrlrange="-400 400" forcerange="-3.0 3.0" ctrl="{fw_target:.4f}"/>')
    w(f'    <velocity name="fw_lower_vel" joint="fw_lower" kv="0.5" ctrlrange="-400 400" forcerange="-3.0 3.0" ctrl="{-fw_target:.4f}"/>')
    w(f'    <velocity name="paddle_vel" joint="paddle_joint" kv="0.08" ctrlrange="-100 100" forcerange="-0.6 0.6" ctrl="{paddle_omega:.4f}"/>')
    w('  </actuator>')
    w('  <sensor>')
    w('    <framepos name="ball_pos" objtype="body" objname="ball"/>')
    w('    <framelinvel name="ball_vel" objtype="body" objname="ball"/>')
    w('  </sensor>')
    w('</mujoco>')
    return "\n".join(lines)


def simulate(xml, seconds, sample_dt=0.004):
    import mujoco
    import numpy as np

    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)
    bid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "ball")
    dt = model.opt.timestep
    n = int(round(seconds / dt))
    every = max(1, int(round(sample_dt / dt)))
    trace = []
    for i in range(n):
        mujoco.mj_step(model, data)
        if i % every == 0:
            p = data.xpos[bid]
            v = data.cvel[bid][3:]
            trace.append((round(i * dt, 4), round(float(p[0]), 4), round(float(p[2]), 4),
                          round(float(np.linalg.norm(v)), 3)))
    return trace, model, data
