# -*- coding: utf-8 -*-
import io, os
HERE = os.path.dirname(os.path.abspath(__file__))
src = io.open(os.path.join(HERE, "_r45_gate2.py"), encoding="utf-8").read()

def rep(a, b, n=1):
    global src
    assert src.count(a) == n, ("MISS", a[:60], src.count(a))
    src = src.replace(a, b)

Q = chr(34) * 3
DOC = Q + u'''R45 台架 v3：挡舌改「从上方竖直下插」（全宽，只做 z 向平移，绕开竖直轴摆动路线）。

为什么放弃侧向摆入：闸位 x≈98 处托盘没有 +y 侧导槽壁（导槽壁只到 x=12.5），球可横向游到 y≈±54，
故挡舌必须横跨 108mm 全宽(L≈106)；而 L≈106 的摆程扫掠半径 106mm > 球窝球到铰心 100.3mm，
关门必扫球窝球。短挡舌(实测 L=40)挡不住：球从舌尖外侧绕过(y漂到+42.9)滚过闸口。两条约束互斥。

本方案：全宽挡舌 x[95.5 100.5] y[-54 54]：
  下插(挡) z[20 75]  -> 全宽横断通道，球无法前后绕行；舌顶 75 > 球心高(NECTAR 63.8)，球不能爬过
  抬起(放) z[112 167] -> 底缘 112 > 通道内球顶(NECTAR 109.7)；顶缘 167 < 下飞轮底 167.5
竖直运动不产生横向扫掠 -> 永不碰球窝里的球；下插落在前球尾部/两球之间，前球被推下坡、后球被挡回。
关窗逻辑：抬起后等"被送那颗球整体越过闸口面(tail < 92.5)"就下插，后球此刻仍远在 40mm 外。
''' + Q
i0 = src.index(Q); i1 = src.index(Q, i0 + 3)
src = src[:i0] + DOC + src[i1 + 3:]

rep("GX, GY, GZ, GL, GH, GT = 98.0, -51.0, 48.0, 40.0, 48.0, 5.0",
    "GX = 98.0\n"
    "GW, GH, GT = 108.0, 55.0, 5.0\n"
    "GZ_DN, GZ_UP = 47.5, 139.5          # 下插/抬起时的舌片中心 z（行程 92mm）\n"
    "GY = 0.0\n"
    "GL = GH")
rep("GOUT = math.pi / 2.0", "GOUT = 0.0")
rep("GMARG, GMAXOPEN = 4.0, 3.00", "GMARG, GMAXOPEN = 3.0, 3.00")
rep("GRAMP = 0.15", "GRAMP = 0.15")

old_print = src[src.index('print("### R45 '):src.index('if GATE_ON:\n    print(')]
new_print = ('''print("### R45 竖向挡舌(全宽, z 向平移): x=%.1f t=%.0f w=%.0f h=%.0f mu=%.2f | 延时%.2fs 最长抬%.2fs 行程%.1fmm 用时%.2fs | 门=%s 夹列=%s"
      % (GX, GT, GW, GH, GMU, GDELAY, GMAXOPEN, GZ_UP - GZ_DN, GRAMP,
         "有" if GATE_ON else "无", CLAMP), flush=True)
''')
src = src.replace(old_print, new_print)

old_body = src[src.index('if GATE_ON:\n    print('):src.index('GBODY = (')]
new_body = ('''if GATE_ON:
    print("###   下插 舌片 x[%.1f %.1f] y[%.1f %.1f] z[%.1f %.1f]"
          % (GX - GT / 2, GX + GT / 2, -GW / 2, GW / 2, GZ_DN - GH / 2, GZ_DN + GH / 2), flush=True)
    print("###   抬起 舌片 x[%.1f %.1f] y[%.1f %.1f] z[%.1f %.1f]"
          % (GX - GT / 2, GX + GT / 2, -GW / 2, GW / 2, GZ_UP - GH / 2, GZ_UP + GH / 2), flush=True)

''')
src = src.replace(old_body, new_body)

rep("""GBODY = ('  <body name="gate_leaf" mocap="true" pos="%.9f %.9f %.9f">\\n'
         '    <geom name="gate_blade" type="box" size="%.9f %.9f %.9f" pos="0 %.9f 0" '
         'friction="%g 0.02 0.0001" rgba="0.90 0.22 0.28 1" mass="%.6f"/>\\n'
         '  </body>\\n') % (GX * MM, GY * MM, GZ * MM, GT / 2 * MM, GL / 2 * MM, GH / 2 * MM,
                          GL / 2 * MM, GMU, GT * GL * GH * 1e-9 * 1180.0)""",
    """GBODY = ('  <body name="gate_leaf" mocap="true" pos="%.9f %.9f %.9f">\\n'
         '    <geom name="gate_blade" type="box" size="%.9f %.9f %.9f" pos="0 0 0" '
         'friction="%g 0.02 0.0001" rgba="0.90 0.22 0.28 1" mass="%.6f"/>\\n'
         '  </body>\\n') % (GX * MM, 0.0, GZ_DN * MM, GT / 2 * MM, GW / 2 * MM, GH / 2 * MM,
                          GMU, GT * GW * GH * 1e-9 * 1180.0)""")

rep('''            ST["log"].append((round(ST["t"], 2), "摆出" if cmd > 0 else "摆入"))''',
    '''            ST["log"].append((round(ST["t"], 2), "抬起" if cmd > 0 else "下插"))''')

rep('''            if ST["phase"] == 1:
                cmd = 1.0
                for (bid, rr) in ST["balls"]:
                    p = d.xpos[bid] * 1000.0
                    if p[0] >= GX - 5.0:
                        continue
                    ddx, ddy = p[0] - GX, p[1] - GY
                    if math.sqrt(ddx * ddx + ddy * ddy) > GL + GMARG + rr:
                        ST["log"].append((round(ST["t"], 2), "到位关门"))
                        cmd = 0.0
                        break''',
    '''            if ST["phase"] == 1:
                cmd = 1.0
                for (bid, rr) in ST["balls"]:
                    p = d.xpos[bid] * 1000.0
                    if p[0] >= GX:
                        continue
                    if p[0] + rr < GX - GT / 2.0 - GMARG:
                        ST["log"].append((round(ST["t"], 2), "球已过闸口"))
                        cmd = 0.0
                        break''')

rep('''        th = GOUT * ST["g"]
        d.mocap_pos[ST["moc"]] = (GX * MM, GY * MM, GZ * MM)
        d.mocap_quat[ST["moc"]] = (math.cos(0.5 * th), 0.0, 0.0, math.sin(0.5 * th))''',
    '''        zc = GZ_DN + (GZ_UP - GZ_DN) * ST["g"]
        d.mocap_pos[ST["moc"]] = (GX * MM, 0.0, zc * MM)
        d.mocap_quat[ST["moc"]] = (1.0, 0.0, 0.0, 0.0)''')


rep('''        row = [round(ST["t"], 3), round(D(GOUT * ST["g"]), 1),''',
    '''        row = [round(ST["t"], 3), round(GZ_DN + (GZ_UP - GZ_DN) * ST["g"], 1),''')

rep('''    d2.mocap_pos[mc] = (GX * MM, GY * MM, GZ * MM)''',
    '''    d2.mocap_pos[mc] = (GX * MM, 0.0, GZ_DN * MM)''')

out = os.path.join(HERE, "_r45_gate3.py")
io.open(out, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", out, len(src))
