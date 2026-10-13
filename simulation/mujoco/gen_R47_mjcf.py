# -*- coding: utf-8 -*-
"""R47 交付：把验收口径的 MuJoCo 台架落盘为 MJCF/XML（含 6 相位 keyframe）。

每个相位在独立子进程里跑真实代码路径（_r47_geo.py 头部补丁 + r38_v8.py 参数解析），
在 build_multi 返回时捕获编译好的模型与 XML 文本，随后：
  1) 按 geom 名字把编译期数组改动（摩擦 / priority / 径向让位）注入 XML 文本；
  2) 把初始球列写进 <body pos> 与 6 个 <keyframe>；
  3) 回读最终 XML，与捕获模型逐项比对（geom 名字/摩擦/priority/位置/尺寸）。
"""
import sys, os, math, re, json, subprocess

WORK = os.path.abspath(os.path.join("simulation", "mujoco", "_work"))
GEO = os.path.join(WORK, "_r47_geo.py")
R38 = os.path.join(WORK, "r38_v8.py")
OUTD = os.path.abspath(os.path.join("simulation", "mujoco", "out"))
TMP = os.path.join(OUTD, "_r47xml_tmp")
PH0S = (0.0, 30.0, 60.0, 90.0, 120.0, 150.0)
MIXES = {"mixed": ["POLLEN", "NECTAR", "POLLEN", "NECTAR"],
         "pol": ["POLLEN"] * 4,
         "net": ["NECTAR"] * 4}
FILETAG = {"mixed": "mixed4", "pol": "4xPOLLEN", "net": "4xNECTAR"}
BASE_CLI = ["--tray", "460", "--hold", "1", "--mu", "0.6", "--park", "188",
            "--liner-shell", "0.30", "--relief", "-0.20", "--gate-x", "180"]
F_SHELL, F_PADDLE, F_GATE = 0.30, 0.70, 0.40


def nips_of(key):
    return (64.0, 82.0) if key == "mixed" else (R_NIP[key],)


R_NIP = {"pol": 64.0, "net": 82.0}


def classify(nm):
    if nm.startswith("r10_") or nm.startswith("shell_"):
        return F_SHELL, 2, True            # 摩擦 0.30 + priority 2 + 径向让位
    if nm.startswith("tray") or nm.startswith("ramp"):
        return F_SHELL, 2, False           # 只改摩擦/priority
    if nm.startswith("paddle"):
        return F_PADDLE, 2, False
    if nm.startswith("gate"):
        return F_GATE, 2, False
    return None, 0, False


def inject(xml, relief, pcx, pcz):
    out = []
    for ln in xml.splitlines():
        st = ln.strip()
        if st.startswith("<geom ") and 'name="' in st and "<default" not in st:
            nm = re.search(r'name="([^"]*)"', st).group(1)
            f, prio, rad = classify(nm)
            if f is not None:
                mf = re.search(r'friction="([^"]*)"', ln)
                if mf:
                    q = mf.group(1).split()
                    q[0] = "%.4f" % f
                    ln = ln[:mf.start(1)] + " ".join(q) + ln[mf.end(1):]
                else:
                    ln = ln.replace(' type=', ' friction="%.4f 0.005 0.0001" type=' % f, 1)
            if prio:
                if 'priority="' in ln:
                    ln = re.sub(r'priority="[^"]*"', 'priority="%d"' % prio, ln)
                else:
                    ln = ln.replace("/>", ' priority="%d"/>' % prio, 1)
            if rad and relief:
                mp = re.search(r'pos="([^"]*)"', ln)
                if mp:
                    x, y, z = [float(v) for v in mp.group(1).split()]
                    vx, vz = x * 1000.0 - pcx, z * 1000.0 - pcz
                    L = math.hypot(vx, vz) or 1.0
                    x += vx / L * relief * 0.001
                    z += vz / L * relief * 0.001
                    ln = ln[:mp.start(1)] + "%.9f %.9f %.9f" % (x, y, z) + ln[mp.end(1):]
        out.append(ln)
    return "\n".join(out)


def keyframes_block(qpos_list, rad_list):
    L = ["  <keyframe>"]
    for q, ang in zip(qpos_list, rad_list):
        L.append('    <key name="ph%03d" qpos="%s"/>'
                 % (int(ang), " ".join("%.9g" % v for v in q)))
    L.append("  </keyframe>")
    return "\n".join(L)


def worker(ph0, key):
    import mujoco
    mix = MIXES[key]
    sys.argv = [GEO] + BASE_CLI + ["--mix", ",".join(mix), "--phases", "%g" % ph0]
    src = open(GEO, encoding="utf-8").read()
    cut = 'sys.argv = [os.path.join(HERE, "r38_v8.py")] + keep'
    ci = src.index(cut)
    ci = src.index("\n", ci) + 1
    g = {"__name__": "__main__", "__file__": GEO}
    exec(compile(src[:ci], GEO, "exec"), g)
    R = g["R"]
    pv2 = R.pv2
    patched = R.build_multi
    want = nips_of(key)
    CAP = {}

    def wrap(mx, ph0_, nip, *a, **k):          # 只收整机模型，忽略 place_queue 的单球探针
        out = patched(mx, ph0_, nip, *a, **k)
        if len(mx) > 1:
            CAP[float(nip)] = out
            if len(CAP) >= len(want):
                raise SystemExit(0)
        return out

    R.build_multi = wrap
    try:
        exec(compile(open(R38, encoding="utf-8").read(), R38, "exec"),
             {"__name__": "__main__", "__file__": R38})
    except SystemExit:
        pass
    R.build_multi = patched
    os.makedirs(TMP, exist_ok=True)
    pcx, pcz = pv2.PADDLE_CX, pv2.PADDLE_CZ
    centres, stacked, in_ch = R.place_queue(list(mix), ph0)
    for nip, out in sorted(CAP.items()):
        m2, d2, aid2, jid2, meta2, w, xml2 = out
        for k, mt in enumerate(meta2):
            R.put(d2, mt, *centres[k])
        d2.qpos[jid2] = math.radians(ph0)
        mujoco.mj_forward(m2, d2)
        qpos = [float(v) for v in d2.qpos[:m2.nq]]
        xml3 = inject(xml2, -0.20, pcx, pcz)
        for k, (x, z) in enumerate(centres, 1):
            xml3 = re.sub(r'(<body name="ball_%d" pos=")[^"]*(")' % k,
                          lambda mm: mm.group(1) + "%.9f 0 %.9f" % (x * .001, z * .001)
                          + mm.group(2), xml3)
        xml3 = xml3.replace("</mujoco>", keyframes_block([qpos], [ph0]) + "\n</mujoco>")
        tag = "%s_ph%03d_nip%03d" % (key, int(ph0), int(nip))
        open(os.path.join(TMP, tag + ".xml"), "w", encoding="utf-8", newline="\n").write(xml3)
        ref = dict(nip=nip, ph0=ph0, nq=int(m2.nq), nv=int(m2.nv), ngeom=int(m2.ngeom),
                   nbody=int(m2.nbody), nu=int(m2.nu), qpos=qpos,
                   geom=[(mujoco.mj_id2name(m2, mujoco.mjtObj.mjOBJ_GEOM, i) or "",
                          float(m2.geom_friction[i][0]), int(m2.geom_priority[i]),
                          [round(float(v) * 1000.0, 6) for v in m2.geom_pos[i]],
                          [round(float(v) * 1000.0, 6) for v in m2.geom_size[i]])
                         for i in range(m2.ngeom)])
        open(os.path.join(TMP, tag + ".json"), "w", encoding="utf-8").write(
            json.dumps(ref, ensure_ascii=False, indent=1))
        print("### dumped %s (nq=%d ngeom=%d nbody=%d)" % (tag, m2.nq, m2.ngeom, m2.nbody),
              flush=True)


def header(key, nip):
    return ("<!--\n  T06 送球+发射台架 R47 验收模型（MuJoCo 3.14，SI 单位 m / kg）\n"
            "  球种排布: %s\n"
            "  口径: 托板末端 x=460mm  挡舌 x=180mm  球-环境 mu=0.6\n"
            "        外罩/托板/球窝摩擦 0.30 + priority 2（托板顶面单侧低摩擦胶带）\n"
            "        外罩内弧/唇口径向让位 -0.20mm  拨杆 0.70 + priority 2  挡舌 0.40 + priority 2\n"
            "  轮间半间距: nip=%g mm -> HALF_SPACING=%.1f mm（WHEEL_R=48 夹口）\n"
            "  飞轮 1620 rpm 对向旋转；拨杆两叉(330/150)，索引式 360 deg/颗、停 1 s、扫 248 deg\n"
            "  <keyframe ph000..ph150> = 6 个拨杆起始相位，配 run_R47_xml.py --ph 0..5\n"
            "  挡舌 = mocap body \"gate_leaf\"，需外部驱动 z 47.5mm(挡) <-> 139.5mm(放)\n"
            "  挡位角 188 deg 需速度伺服保持（真实舵机行为，脚本里实现）\n"
            "-->\n") % (",".join(MIXES[key]), nip, nip / 2.0 + 48.0)


def main():
    import mujoco
    os.makedirs(OUTD, exist_ok=True)
    ok_all = True
    for key in ("mixed", "pol", "net"):
        for ph0 in PH0S:
            r = subprocess.run([sys.executable, "-X", "utf8", os.path.abspath(__file__),
                                "--worker", "%g" % ph0, key], capture_output=True, text=True,
                               encoding="utf-8", errors="replace")
            if r.returncode != 0:
                print("!! %s ph0=%g 子进程失败 rc=%d" % (key, ph0, r.returncode))
                print((r.stdout or "")[-2500:])
                print((r.stderr or "")[-2500:])
                return 1
        for nip in nips_of(key):
            tags = ["%s_ph%03d_nip%03d" % (key, int(p), int(nip)) for p in PH0S]
            xml = open(os.path.join(TMP, tags[0] + ".xml"), encoding="utf-8").read()
            refs = [json.load(open(os.path.join(TMP, t + ".json"), encoding="utf-8")) for t in tags]
            qps = [ref["qpos"] for ref in refs]
            xml = re.sub(r"  <keyframe>.*?</keyframe>\n", "", xml, flags=re.S)
            xml = xml.replace("</mujoco>", keyframes_block(qps, list(PH0S)) + "\n</mujoco>")
            xml = xml.replace("<mujoco ", header(key, nip) + "<mujoco ", 1)
            name = "R47_launcher_%s_gap%03d.xml" % (FILETAG[key], int(nip))
            dst_repo = os.path.join(OUTD, name)
            dst_desk = os.path.abspath(os.path.join(os.path.expanduser("~"), "OneDrive",
                                                    "Desktop", name))
            open(dst_repo, "w", encoding="utf-8", newline="\n").write(xml)
            open(dst_desk, "w", encoding="utf-8", newline="\n").write(xml)
            m = mujoco.MjModel.from_xml_string(xml)
            ref0 = refs[0]
            bad = []
            if (m.nq, m.nv, m.ngeom, m.nbody, m.nu) != (ref0["nq"], ref0["nv"],
                                                        ref0["ngeom"], ref0["nbody"], ref0["nu"]):
                bad.append("维度不符")
            for i, (nm, fr, pr, ps, sz) in enumerate(ref0["geom"]):
                gg = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, nm)
                if gg < 0:
                    bad.append("缺 " + nm)
                    continue
                if abs(float(m.geom_friction[gg][0]) - fr) > 1e-9:
                    bad.append("%s 摩擦" % nm)
                if int(m.geom_priority[gg]) != pr:
                    bad.append("%s priority" % nm)
                if max(abs(float(m.geom_pos[gg][j]) * 1000.0 - ps[j]) for j in range(3)) > 2e-3:
                    bad.append("%s 位置" % nm)
                if max(abs(float(m.geom_size[gg][j]) * 1000.0 - sz[j]) for j in range(3)) > 2e-3:
                    bad.append("%s 尺寸" % nm)
            d = mujoco.MjData(m)
            mujoco.mj_resetDataKeyframe(m, d, 0)
            if max(abs(float(d.qpos[i]) - qps[0][i]) for i in range(m.nq)) > 1e-9:
                bad.append("keyframe0")
            ok_all = ok_all and not bad
            print("  %-38s ngeom=%d nkey=%d  %s" % (name, m.ngeom, m.nkey,
                                                    "PASS" if not bad else "FAIL:" + ",".join(bad[:6])))
    print("桌面输出目录: " + os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop"))
    return 0 if ok_all else 2


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--worker":
        worker(float(sys.argv[2]), sys.argv[3])
    else:
        raise SystemExit(main())