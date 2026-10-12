import pathlib
src = pathlib.Path("simulation/mujoco/_work/r38_v4.py").read_text(encoding="utf-8")
src = src.replace('"""r38 v4: v3 + 逐球舵机曲线(每球独立拾取保持/转速)"""',
                  '"""r38 v5: v4 + 逐球在线可调夹口(扎带锚点按球种切换)"""')
src = src.replace('ap.add_argument("--tag", default="v4")',
'''ap.add_argument("--anchor-map", default="")  # 逐球夹口锚点偏移 mm "POLLEN:-3,NECTAR:5"
ap.add_argument("--tag", default="v5")''')
src = src.replace("SPD = _pmap(a.spd_map, 1.0)",
'''SPD = _pmap(a.spd_map, 1.0)
ANCH = _pmap(a.anchor_map, 0.0)''')

# 应用锚点：在 settle 结束时写入 springref
src = src.replace('''def run_case(mix, ph0, hold):
    m, d, aid, jid, meta, w, xml = _build(mix, ph0, GAP)''',
'''def run_case(mix, ph0, hold):
    m, d, aid, jid, meta, w, xml = _build(mix, ph0, GAP)
    sids = []
    for lab in ("upper", "lower"):
        s = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "fw_%s_slide" % lab)
        if s >= 0:
            sids.append(s)
    base_ref = [-a.pre / a.k] * len(sids)


    def set_nip(off_mm):
        for s, b in zip(sids, base_ref):
            m.joint_springref[s] = b + off_mm * 0.001''')
src = src.replace('''                phase = "sweep"
                if J0 is None:
                    J0 = J''',
'''                phase = "sweep"
                if sids:
                    set_nip(ANCH[mix[kk]] if kk < nb else 0.0)
                if J0 is None:
                    J0 = J''')
src = src.replace('''            if i == 0:
                for k, mt in enumerate(meta):
                    R.put(d, mt, *centres[k])''',
'''            if i == 0:
                if sids:
                    set_nip(ANCH[mix[0]])
                for k, mt in enumerate(meta):
                    R.put(d, mt, *centres[k])''')
src = src.replace('res = dict(mix=list(mix), ph0=ph0, gap=GAP, hold_map=dict(HOLD)',
                  'res = dict(mix=list(mix), ph0=ph0, gap=GAP, anchor_map=dict(ANCH), hold_map=dict(HOLD)')
src = src.replace('print("=== r38v4 mix=%s tray=%.0f ph0=%s 夹口=%s 保持P%.2f/N%.2f 转速P%.2f/N%.2f ==="\n      % (">".join(mix), R.TRAY_X1, a.phases, MODE, HOLD["POLLEN"], HOLD["NECTAR"],\n         SPD["POLLEN"], SPD["NECTAR"]), flush=True)',
'''print("=== r38v5 mix=%s tray=%.0f ph0=%s | 扎带%.0fN/%.0fN每mm 锚点P%+.1f/N%+.1f | 保持P%.2f/N%.2f 转速P%.2f/N%.2f ==="
      % (">".join(mix), R.TRAY_X1, a.phases, a.pre, a.k / 1000.0,
         ANCH["POLLEN"], ANCH["NECTAR"], HOLD["POLLEN"], HOLD["NECTAR"],
         SPD["POLLEN"], SPD["NECTAR"]), flush=True)''')
pathlib.Path("simulation/mujoco/_work/r38_v5.py").write_text(src, encoding="utf-8")
import re
print("v5 anchors:", len(re.findall("set_nip", src)), "sids uses:", len(re.findall("sids", src)))
