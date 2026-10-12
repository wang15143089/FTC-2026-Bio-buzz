# -*- coding: utf-8 -*-
"""R39 送球优化迭代台架：完全复用 r38_v8.py（R38 基线口径），只多一个 --liner 参数。

--liner MU      外罩内弧(r10_*/shell_*) + 托板(tray) 的接触摩擦上限（贴 0.5mm PTFE 带）
                机制：把这些 geom 的 priority 设 2（高于球的 1）并写 friction=MU，
                MuJoCo 取高优先级 geom 的摩擦 => 球-外罩/球-托板 有效 mu = MU。
--liner-shell MU / --liner-tray MU   只改一处
用法：
  _r39_v9.py --liner 0.20 --nip-net 86 --phases 150,145,140,130,120,160 --tag L20
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
keep = []
i = 0
while i < len(argv):
    if argv[i] == "--liner" and i + 1 < len(argv):
        liner = float(argv[i + 1]); i += 2; continue
    if argv[i] == "--liner-shell" and i + 1 < len(argv):
        liner_shell = float(argv[i + 1]); i += 2; continue
    if argv[i] == "--liner-tray" and i + 1 < len(argv):
        liner_tray = float(argv[i + 1]); i += 2; continue
    keep.append(argv[i]); i += 1

if liner >= 0.0:
    if liner_shell < 0.0: liner_shell = liner
    if liner_tray < 0.0: liner_tray = liner

if liner_shell >= 0.0 or liner_tray >= 0.0:
    _orig = R.build_multi

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
        return m, d, aid, jid, meta, w, xml

    R.build_multi = build_patch
    print("### R39 内衬: 外罩=%s  托板=%s" %
          ("%.2f" % liner_shell if liner_shell >= 0 else "off",
           "%.2f" % liner_tray if liner_tray >= 0 else "off"), flush=True)

sys.argv = [os.path.join(HERE, "r38_v8.py")] + keep
src = open(os.path.join(HERE, "r38_v8.py"), encoding="utf-8").read()
exec(compile(src, os.path.join(HERE, "r38_v8.py"), "exec"),
     {"__name__": "__main__", "__file__": os.path.join(HERE, "r38_v8.py")})
