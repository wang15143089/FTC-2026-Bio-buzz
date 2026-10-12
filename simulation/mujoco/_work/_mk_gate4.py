# -*- coding: utf-8 -*-
"""由 _r45_gate3.py 生成 _r45_gate4.py：加「真实舵机待机保持位」补丁。"""
import io, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "_r45_gate3.py"), encoding="utf-8").read()

assert src.count("GPRIO = 2") == 1
src = src.replace("GPRIO = 2",
                  "GPRIO = 2\nPARK, PKP = 0.0, 40.0          # PARK>0: 待机段用速度伺服保持停位角(真实舵机行为)")

old = '''    if a_ == "--paddle-mu" and i + 1 < len(argv):
        paddle_mu = float(argv[i + 1]); i += 2; continue
'''
new = old + '''    if a_ == "--park" and i + 1 < len(argv):
        PARK = float(argv[i + 1]); i += 2; continue
    if a_ == "--park-kp" and i + 1 < len(argv):
        PKP = float(argv[i + 1]); i += 2; continue
'''
assert src.count(old) == 1
src = src.replace(old, new)

old = '''if GATE_ON:
    print("###   下插'''
new = '''if PARK > 0.0:
    print("###   待机停位保持 J_park=%.1f deg (Kp=%.1f 1/s, 峰值扭矩 %.3f Nm)"
          % (PARK, PKP, 0.08 * PKP * 0.5), flush=True)
if GATE_ON:
    print("###   下插'''
assert src.count(old) == 1
src = src.replace(old, new)

old = '''    if dump and (not ST["rows"] or ST["t"] - ST["rows"][-1][0] >= 0.01):'''
new = '''    # --- 真实舵机待机保持位：相位机写 0 时（settle/settle_tail）改为速度伺服保持 PARK 角 ---
    # 注意必须放在闸门判决之后：闸门逻辑用 ctrl==0 判定"拨杆已停"，此处已读到 0。
    if PARK > 0.0 and ST["aid_p"] >= 0 and abs(float(d.ctrl[ST["aid_p"]])) < 1e-9:
        _er = math.remainder(math.radians(PARK) - float(d.qpos[ST["jid_p"]]), 2.0 * math.pi)
        d.ctrl[ST["aid_p"]] = max(-100.0, min(100.0, PKP * _er))
    if dump and (not ST["rows"] or ST["t"] - ST["rows"][-1][0] >= 0.01):'''
assert src.count(old) == 1
src = src.replace(old, new)

src = src.replace('"""R45 台架 v3：挡舌改「从上方竖直下插」（全宽，只做 z 向平移，绕开竖直轴摆动路线）。',
                  '"""R45 台架 v4 = v3 + 真实舵机待机保持位（修 ph0=60 楔死）。\n\n停位保持必要性：v3 在 settle/settle_tail 段 ctrl=0，拨杆变自由摆，重力下垂到 ~53 deg，\n此时弹性指(外缘 r=61)正落在球道内球心半径(NECTAR 61.7)上 -> 与托板形成径向夹口，\n后到的球在 x~122 被永久楔死。真实舵机待机是位置保持，不会自由下垂。\n停位角安全区间由「挡片极角 = 390-J 不得落入球道/球窝窗口 [235,355]」定为 J in (171,199)。\n\n原 v3 说明：挡舌改「从上方竖直下插」（全宽，只做 z 向平移，绕开竖直轴摆动路线）。', 1)

open(os.path.join(HERE, "_r45_gate4.py"), "w", encoding="utf-8").write(src)
print("written _r45_gate4.py", len(src), "chars")
