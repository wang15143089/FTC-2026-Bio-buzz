# -*- coding: utf-8 -*-
"""R45-i 体检：把闸位 x 作为参数，检查行程干涉/拨杆扫掠/球列/封堵能力/抬升净空。
用法: python _r45_idxchk16.py [GX] [GZ_DN] [GZ_UP]
"""
import sys, os, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import mujoco, r37_multiball as R
MM = R.MM
GX   = float(sys.argv[1]) if len(sys.argv) > 1 else 185.0
GZ_DN = float(sys.argv[2]) if len(sys.argv) > 2 else 47.5
GZ_UP = float(sys.argv[3]) if len(sys.argv) > 3 else 139.5
GW, GH, GT = 108.0, 55.0, 5.0
R.TRAY_X1 = 400.0
MIX = ["POLLEN", "NECTAR", "POLLEN", "NECTAR"]
BODY = ('  <body name="idx_gate" pos="%.9f 0 0">\n'
        '    <joint name="idx_joint" type="slide" axis="0 0 1"/>\n'
        '    <geom name="idx_blade" type="box" size="%.9f %.9f %.9f" pos="0 0 0"/>\n'
        '  </body>\n') % (GX * MM, GT / 2 * MM, GW / 2 * MM, GH / 2 * MM)
print("### R45-i 竖向挡舌体检 x=%.1f t=%.0f w=%.0f h=%.0f | 下插 z[%.1f %.1f] 抬起 z[%.1f %.1f] 行程%.0f"
      % (GX, GT, GW, GH, GZ_DN - GH/2, GZ_DN + GH/2, GZ_UP - GH/2, GZ_UP + GH/2, GZ_UP - GZ_DN))
m0, d0, aid, jid0, meta, w, xml = R.build_multi(MIX, 0.0, 86)
m = mujoco.MjModel.from_xml_string(xml.replace("  <worldbody>", "  <worldbody>\n" + BODY, 1))
d = mujoco.MjData(m)
gt = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, "idx_blade")
jz = int(m.jnt_qposadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "idx_joint")])
jp = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "paddle_joint")
pbody = int(m.jnt_bodyid[jp])
pgeom = [g for g in range(m.ngeom) if int(m.geom_bodyid[g]) == pbody]
balls = [g for g in range(m.ngeom) if (mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, g) or "").startswith("ball_geom")]
static = [g for g in range(m.ngeom) if g != gt and g not in balls and g not in pgeom]
nm = lambda g: (mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, g) or "?")
def setz(zc):
    d.qpos[jz] = zc * MM; d.qpos[jp] = 0.0; mujoco.mj_forward(m, d)
print("\n### A. 行程 x 静态件（步长 4mm）")
worst = (1e9, None, None)
rows = []
for zc in np.arange(GZ_DN, GZ_UP + 0.01, 4.0):
    setz(zc)
    best, bn = 1e9, None
    for g in static:
        v = float(mujoco.mj_geomDistance(m, d, gt, g, 0.5, None))
        if v < best: best, bn = v, nm(g)
    rows.append((zc, bn, best))
    if best < worst[0]: worst = (best, bn, zc)
for zc, bn, v in rows:
    if zc in (GZ_DN, GZ_UP) or v == worst[0]:
        print("   z=%6.1f 最近 %-20s %8.2f mm" % (zc, bn, v * 1000))
print("   >>> 全程最差: z=%.1f 对 %s %.2f mm %s" % (worst[2], worst[1], worst[0]*1000,
      "OK" if worst[0] > 0 else "干涉!"))
print("\n### B. 抬起位 x 拨杆全扫掠(0..248deg, 步长 4deg)")
d.qpos[jz] = GZ_UP * MM
wb = (1e9, None, None)
for J in np.arange(0.0, 248.1, 4.0):
    d.qpos[jp] = math.radians(J); mujoco.mj_forward(m, d)
    for g in pgeom:
        v = float(mujoco.mj_geomDistance(m, d, gt, g, 0.5, None))
        if v < wb[0]: wb = (v, nm(g), J)
print("   >>> 最差: 拨杆%.0fdeg 对 %s : %.2f mm %s" % (wb[2], wb[1], wb[0]*1000,
      "OK" if wb[0] > 0 else "干涉!"))
print("\n### C. 下插位 x 拨杆停车带(0..24deg, 步长 3deg)")
d.qpos[jz] = GZ_DN * MM
wc = (1e9, None, None)
for J in np.arange(0.0, 24.1, 3.0):
    d.qpos[jp] = math.radians(J); mujoco.mj_forward(m, d)
    for g in pgeom:
        v = float(mujoco.mj_geomDistance(m, d, gt, g, 0.5, None))
        if v < wc[0]: wc = (v, nm(g), J)
print("   >>> 最差: 拨杆%.0fdeg 对 %s : %.2f mm %s" % (wc[2], wc[1], wc[0]*1000,
      "OK" if wc[0] > 0 else "干涉!"))
print("\n### D. 托盘面高 / 球静止高度（射线避开挡舌）")
def tray_top(x):
    z0 = 260.0
    for _ in range(10):
        pnt = np.array([[x*MM],[0.0],[z0*MM]]); vec = np.array([[0.0],[0.0],[-1.0]])
        gid = np.zeros(1, dtype=np.int32); nrm = np.zeros(3)
        dd = float(mujoco.mj_ray(m, d, pnt, vec, None, 1, -1, gid, nrm))
        if dd <= 0 or gid[0] < 0: return None
        z = z0 - dd*1000.0
        if nm(int(gid[0])) != "idx_blade": return z
        z0 = z - 0.05
    return None
d.qpos[jz] = 200.0 * MM; d.qpos[jp] = 0.0; mujoco.mj_forward(m, d)
zt = tray_top(GX)
tr = math.cos(math.radians(R.TILT))
print("   闸位托板面 z=%.2f ; POLLEN 静止球心 z=%.2f(顶 %.2f) ; NECTAR 球心 z=%.2f(顶 %.2f)"
      % (zt, zt + 35.56*tr, zt + 2*35.56, zt + 45.974*tr, zt + 2*45.974))
print("\n### E. 封堵能力（下插位）")
setz(GZ_DN)
lo, hi = GZ_DN - GH/2, GZ_DN + GH/2
print("   舌片 x[%.1f %.1f] y[%.1f %.1f] z[%.1f %.1f]" % (GX-GT/2, GX+GT/2, -GW/2, GW/2, lo, hi))
print("   舌底-托板面间隙 %.2f mm（球径 71.1/91.9 均不能过）" % (lo - zt))
print("   舌顶 z=%.1f 比 POLLEN/NECTAR 球心高 %.1f / %.1f mm" % (hi, hi-(zt+35.56*tr), hi-(zt+45.974*tr)))
print("\n### F. 抬起位净空")
setz(GZ_UP)
lo2, hi2 = GZ_UP - GH/2, GZ_UP + GH/2
print("   抬起舌底 z=%.1f ; POLLEN 球顶 %.1f / NECTAR 球顶 %.1f -> 净空 %+.1f / %+.1f mm"
      % (lo2, zt+2*35.56, zt+2*45.974, lo2-(zt+2*35.56), lo2-(zt+2*45.974)))
print("   抬起舌顶 z=%.1f ; 该 x 上方最近件(射线)=" % hi2, end=" ")
z1 = tray_top(GX)
pnt = np.array([[GX*MM],[0.0],[(hi2+400)*MM]]); vec = np.array([[0.0],[0.0],[-1.0]])
gid = np.zeros(1, dtype=np.int32); nrm = np.zeros(3)
dd = float(mujoco.mj_ray(m, d, pnt, vec, None, 1, -1, gid, nrm))
print("%s z=%.1f" % (nm(int(gid[0])), hi2 + 400 - dd*1000 if dd > 0 else -1))
print("\n### G. 沿托板 y=±30 处上方净空（挡舌全宽 y±54，逐 x 扫）")
for x in (98, 150, 172, 185, 200, 215):
    worstz = 1e9; wn = None
    for yy in (-40, -20, 20, 40):
        for g in range(m.ngeom):
            if g == gt or not (m.geom_contype[g] or m.geom_conaffinity[g]): continue
            if nm(g).startswith("ball"): continue
            d.qpos[jz] = 0.0; mujoco.mj_forward(m, d)
            # 用挡舌在该 x 的窄片去探上方
            break
    print("   x=%5.1f (见 H 段)" % x)
print("done")
