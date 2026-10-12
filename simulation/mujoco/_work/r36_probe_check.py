# -*- coding: utf-8 -*-
r"""R36 几何探针复核（可复算证据，对应 DEC-0033 / DEC-0034）。

只用 MuJoCo 自己的碰撞/几何接口当量具，不用任何自写解析几何。输出四张表：
 1) 模型单位：证明本模型是"米"制 -> mj_geomDistance 必须 *1000 才是 mm
 2) 相位标定：parts(phases=(330,150)) 在 ph0=0 时叶片其实在 30/210 deg
 3) 托板 vs 叶片扫掠：球停在托板面上时，随相位的最坏净距（负=穿透）
 4) 托板长度上限：后挡墙 + 球径决定球心最远能到哪 -> 容量

用法： .\.venv-cad\Scripts\python.exe -X utf8 simulation\mujoco\_work\r36_probe_check.py
"""
import sys, math
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import mujoco
import r36_multiball as M

pv2 = M.pv2


def _nearest(m, d, g1):
    best, bn = 1e9, None
    for g2 in range(m.ngeom):
        if g2 == g1:
            continue
        dd = float(mujoco.mj_geomDistance(m, d, g1, g2, 0.06, None))
        if dd < best:
            best, bn = dd, mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, g2)
    return best * 1000.0, bn


def clear_mm(r, nip, ph0, x, z):
    m, d, adr, g1 = M._probe(r, nip, ph0)
    d.qpos[adr:adr + 3] = [x * M.MM, 0.0, z * M.MM]
    mujoco.mj_forward(m, d)
    return _nearest(m, d, g1)


def tray_z(r, x):
    """球停在托板面上时球心高度 (mm)。"""
    return pv2.tray_top_z(x + r * M.SIN_T) + r * M.COS_T


def main():
    m, d, aid, jid, meta, w, xml = M.build_multi(["NECTAR"], 60.0, 82.0)
    g1 = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, "ball_geom_1")
    print("mujoco %s / gravity=%s / timestep=%g / ball_r(model)=%g"
          % (mujoco.__version__, list(m.opt.gravity), m.opt.timestep, m.geom_size[g1][0]))
    print("=> 模型长度单位 = m，mj_geomDistance 返回 m；读成 mm 必须 *1000\n")

    print("== 2) 相位标定（paddle_blade 几何角度, deg）==")
    for ph0 in (0.0, 60.0):
        mm, dd, _, jj, _, _, _ = M.build_multi(["NECTAR"], ph0, 82.0)
        dd.qpos[jj] = math.radians(ph0)
        mujoco.mj_forward(mm, dd)
        got = {}
        for g in range(mm.ngeom):
            nm = mujoco.mj_id2name(mm, mujoco.mjtObj.mjOBJ_GEOM, g) or ""
            if nm.startswith("paddle_blade"):
                p = dd.geom_xpos[g] * 1000
                got[nm] = round(math.degrees(math.atan2(p[2] - pv2.PADDLE_CZ,
                                                        p[0] - pv2.PADDLE_CX)) % 360, 1)
        print("   ph0=%5.1f -> %s" % (ph0, got))
    print("   => ph0=60 才等于 CAD 标称零位 330/150\n")

    print("== 3) NECTAR 停在托板面（球心 x,z）随相位的最坏净距 mm（负=穿透）==")
    print("   ph0 |      x=30       |      x=60       |      x=90       |     x=104")
    for ph0 in range(0, 360, 30):
        row = []
        for x in (30.0, 60.0, 90.0, 104.0):
            c, bn = clear_mm(45.974, 82.0, float(ph0), x, tray_z(45.974, x))
            row.append("%7.1f %-9s" % (c, (bn or "")[:9]))
        print("   %4d | %s" % (ph0, " | ".join(row)))
    print("   => 每个 180 deg 周期里，x>=30 的等待球都会被 paddle_flex/blade 打出穿透；")
    print("      托板（球心到轴心 62~93 mm）永远不可能让球'停着等'（叶片扫掠 46~60 mm）\n")

    print("== 4) 托板球心可达范围与容量 ==")
    for nm in ("NECTAR", "POLLEN"):
        r = M.SP[nm]["r"]
        xmax = None
        for x in range(40, 200):
            c, bn = clear_mm(r, M.SP[nm]["nip"], 0.0, float(x), tray_z(r, x))
            if bn == "rear_wall" or (bn and bn.startswith("rear")):
                xmax = x - 1
                break
        print("   %-7s r=%5.2f mm  球心 x<=%s mm（后挡墙 x=150） 相切排放需间距 %.1f mm -> 托板上最多 %d 颗"
              % (nm, r, xmax, 2 * r, 1 if xmax is None else max(1, int((xmax - 30.0) / (2 * r)) + 1)))


if __name__ == "__main__":
    raise SystemExit(main())
