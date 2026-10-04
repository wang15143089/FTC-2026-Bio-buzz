# -*- coding: utf-8 -*-
import pathlib
p = pathlib.Path("simulation/mujoco/_work/r7_loadprobe.py")
s = p.read_text(encoding="utf-8")
old = '''            p = d.xpos[bid] * 1000.0
            ang = math.degrees(math.atan2(p[2] - pv2.PADDLE_CZ, p[0] - pv2.PADDLE_CX)) % 360.0
            tr.append({"t": round(i * dt, 4), "ang": round(ang, 2),
                       "pv": round(float(math.degrees(d.qvel[pid])), 2),
                       "pa": round(float(d.actuator_force[aid])), 4)})'''
old = old.replace('2), 4)})', '2), "pa": round(float(d.actuator_force[aid]), 4)})')
new = '''            p = d.xpos[bid] * 1000.0
            px, pz = float(p[0]) * 1000.0, float(p[2]) * 1000.0
            rx, rz = px - pv2.PADDLE_CX, pz - pv2.PADDLE_CZ
            lx, lz = pv2.to_shooter(px, pz)
            ang = math.degrees(math.atan2(rz, rx)) % 360.0
            tr.append({"t": round(i * dt, 4), "ang": round(ang, 2),
                       "x": round(px, 3), "z": round(pz, 3),
                       "v": round(float(np.linalg.norm(d.cvel[bid][3:])), 4),
                       "vx": round(float(d.cvel[bid][3]), 4), "vz": round(float(d.cvel[bid][5]), 4),
                       "r": round(math.hypot(rx, rz), 3),
                       "lx": round(lx, 3), "lz": round(lz, 3),
                       "pv": round(float(math.degrees(d.qvel[pid])), 2),
                       "pa": round(float(d.actuator_force[aid]), 4)})'''
assert old in s
s = s.replace(old, new)
p.write_text(s, encoding="utf-8")
print("ok")
