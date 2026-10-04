# -*- coding: utf-8 -*-
"""Is the paddle really turning at the commanded rpm, and how fast is the ball carried?"""
import math, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import r6_smooth as r6
import opt_lib as ol
import mujoco

pv2 = ol.pv2


def probe(name, rpm, fr=1.0, bx=145.0, sec=8.0):
    ol.apply_geom(name)
    xml, ctrl = pv2.build_xml(1620.0, -1, rpm * 2 * math.pi / 60.0, bx,
                              pv2.tray_top_z(bx) + pv2.BALL_R)
    xml = xml.replace('forcerange="-1.5 1.5"', 'forcerange="-%g %g"' % (fr, fr))
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
    pid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "paddle_joint")
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    aid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "paddle_vel")
    dt = m.opt.timestep
    print("[%s @%g rpm fr=%g] commanded omega = %.2f rad/s (%.1f rpm)" % (name, rpm, fr, ctrl[2], ctrl[2] * 60 / 2 / math.pi))
    print("   t     qvel_deg_s  rpm_eff  ball_ang  ball_angrate_deg_s  ball_v  act_Nm")
    prev = None
    for i in range(int(sec / dt)):
        mujoco.mj_step(m, d)
        if i % int(0.1 / dt) == 0:
            qv = d.qvel[pid] if pid >= 0 else 0.0
            p = d.xpos[bid] * 1000.0
            ang = math.degrees(math.atan2(p[2] - pv2.PADDLE_CZ, p[0] - pv2.PADDLE_CX)) % 360.0
            ra = ""
            if prev is not None:
                da = (ang - prev) % 360.0
                if da > 180.0:
                    da -= 360.0
                ra = "%8.1f" % (da / 0.1)
            prev = ang
            print("  %5.2f  %10.1f  %7.1f  %8.1f  %s   %5.2f  %6.3f"
                  % (i * dt, math.degrees(qv), qv * 60 / 2 / math.pi, ang, ra,
                     float((d.cvel[bid][3:] ** 2).sum() ** 0.5), abs(float(d.actuator_force[aid]))))
            if i * dt > 4.2:
                break


for nm in ("R5", "R6"):
    for rpm in (90.0, 105.0, 40.0):
        probe(nm, rpm)
        print()
