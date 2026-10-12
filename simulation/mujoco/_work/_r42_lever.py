# -*- coding: utf-8 -*-
"""R42 新杠杆台架：完全复用 r38_v8.py（R40 真口径，含舵机两档换档）。

在 R39/R40 的内衬机制之上，新增两个此前从未动过的杠杆：
  --paddle-mu MU   拨杆接触面(paddle*)摩擦上限。默认 0.70（=原值，用于自检透传）
  --grav G         重力加速度（默认 9.81）。减小压力假设的判决性对照。
  原内衬参数 --liner / --liner-shell / --liner-tray 原样保留。

用法：
  _r42_lever.py --liner-shell 0.05 --liner-tray 0.15 --paddle-mu 0.70 ...
  _r42_lever.py --liner-shell 0.05 --liner-tray 0.15 --paddle-mu 0.10 ...
  _r42_lever.py --liner-shell 0.05 --liner-tray 0.15 --grav 2.0 ...
"""
import sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mujoco
import r37_multiball as R

argv = sys.argv[1:]
liner = -1.0
liner_shell = -1.0
liner_tray = -1.0
paddle_mu = -1.0
grav = 0.0
keep = []
i = 0
while i < len(argv):
    if argv[i] == "--liner" and i + 1 < len(argv):
        liner = float(argv[i + 1]); i += 2; continue
    if argv[i] == "--liner-shell" and i + 1 < len(argv):
        liner_shell = float(argv[i + 1]); i += 2; continue
    if argv[i] == "--liner-tray" and i + 1 < len(argv):
        liner_tray = float(argv[i + 1]); i += 2; continue
    if argv[i] == "--paddle-mu" and i + 1 < len(argv):
        paddle_mu = float(argv[i + 1]); i += 2; continue
    if argv[i] == "--grav" and i + 1 < len(argv):
        grav = float(argv[i + 1]); i += 2; continue
    keep.append(argv[i]); i += 1

if liner >= 0.0:
    if liner_shell < 0.0: liner_shell = liner
    if liner_tray < 0.0: liner_tray = liner

_orig = R.build_multi
print("### R42 杠杆: 外罩=%s 托板=%s 拨杆mu=%s grav=%s"
      % ("%.2f" % liner_shell if liner_shell >= 0 else "off",
         "%.2f" % liner_tray if liner_tray >= 0 else "off",
         "%.2f" % paddle_mu if paddle_mu >= 0 else "off(原值)",
         "%.2f" % grav if grav > 0 else "off(9.81)"), flush=True)


def build_patch(mix, ph0, nip, mu=0.40):
    m, d, aid, jid, meta, w, xml = _orig(mix, ph0, nip, mu)
    for g in range(m.ngeom):
        nm = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, g) or ""
        if nm.startswith("r10_") or nm.startswith("shell_"):
            if liner_shell >= 0.0:
                m.geom_friction[g][0] = liner_shell
                m.geom_priority[g] = 2
        elif nm.startswith("tray"):
            if liner_tray >= 0.0:
                m.geom_friction[g][0] = liner_tray
                m.geom_priority[g] = 2
        elif nm.startswith("paddle"):
            if paddle_mu >= 0.0:
                m.geom_friction[g][0] = paddle_mu
                m.geom_priority[g] = 2
    if grav > 0:
        m.opt.gravity[:] = [0.0, 0.0, -grav]
    return m, d, aid, jid, meta, w, xml


R.build_multi = build_patch

sys.argv = [os.path.join(HERE, "r38_v8.py")] + keep
src = open(os.path.join(HERE, "r38_v8.py"), encoding="utf-8").read()
exec(compile(src, os.path.join(HERE, "r38_v8.py"), "exec"),
     {"__name__": "__main__", "__file__": os.path.join(HERE, "r38_v8.py")})
