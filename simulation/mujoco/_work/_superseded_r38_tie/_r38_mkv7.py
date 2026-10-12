import pathlib
src = pathlib.Path("simulation/mujoco/_work/r38_v6.py").read_text(encoding="utf-8")
src = src.replace('"""r38 v6: v5 + 夹口值从 config/parameters.yaml 读取, 逐球切到设计夹口, 实测运行夹口"""',
 '"""r38 v7: v6 + 逐球扎带刚度; 记录受力瞬间的运行夹口"""')
src = src.replace('ap.add_argument("--nip-map", default="")     # 逐球目标空载夹口 mm, 默认读参数文件',
'''ap.add_argument("--nip-map", default="")     # 逐球目标空载夹口 mm, 默认读参数文件
ap.add_argument("--k-map", default="")       # 逐球扎带刚度 N/m "POLLEN:30000,NECTAR:8000"''')
src = src.replace("NIP = _pmap(a.nip_map, 0.0) if a.nip_map else dict(NIP_FILE)",
'''KK = _pmap(a.k_map, a.k)
NIP = _pmap(a.nip_map, 0.0) if a.nip_map else dict(NIP_FILE)''')
src = src.replace("        ANCH[_k] = (NIP[_k] - GAP) / 2.0 + a.pre / a.k * 1000.0",
                  "        ANCH[_k] = (NIP[_k] - GAP) / 2.0 + a.pre / KK[_k] * 1000.0")
src = src.replace('''    def set_nip(off_mm):
        for s, b in zip(sids, base_ref):
            m.qpos_spring[s] = b + off_mm * 0.001''',
'''    def set_nip(off_mm, kk=None):
        for s in sids:
            m.jnt_stiffness[s] = kk if kk else a.k
            m.qpos_spring[s] = -a.pre / (kk if kk else a.k) + off_mm * 0.001
        mujoco.mj_setConst(m, d)''')
src = src.replace("                    set_nip(ANCH[mix[kk]] if kk < nb else 0.0)",
                  "                    set_nip(ANCH[mix[kk]] if kk < nb else 0.0, KK[mix[kk]] if kk < nb else a.k)")
src = src.replace("                    set_nip(ANCH[mix[0]])",
                  "                    set_nip(ANCH[mix[0]], KK[mix[0]])")
# 受力瞬间夹口
src = src.replace('''                    cf[k] = fm''', '''                    cf[k] = fm
                    nip_load[k] = round(run_nip(), 2)''')
src = src.replace('''    free_nip = [None] * (nb + 1); nip_min = [999.0] * nb''',
                  '''    free_nip = [None] * (nb + 1); nip_min = [999.0] * nb; nip_load = [None] * nb''')
src = src.replace('''               nip_min=[(round(x, 2) if x < 999 else None) for x in nip_min]''',
                  '''               nip_min=[(round(x, 2) if x < 999 else None) for x in nip_min], nip_load=nip_load''')
src = src.replace('''空载夹口%s 运行夹口最小%s"
          % (res["n_launched"], len(mix), res["n_real"], res.get("t_total_s", "--"),
             res["tq_peak"], 100 * res["jam_frac"], res["free_nip"], res["nip_min"]), flush=True)''',
'''空载夹口%s 受力夹口%s 轮峰%s"
          % (res["n_launched"], len(mix), res["n_real"], res.get("t_total_s", "--"),
             res["tq_peak"], 100 * res["jam_frac"], res["free_nip"], res["nip_load"],
             res["wheel_peak"]), flush=True)''')
src = src.replace('扎带%.0fN/%.0fN每mm 锚点P%+.1f/N%+.1f ==="\n      % (">".join(mix), R.TRAY_X1, a.phases, NIP_FILE["NECTAR"], NIP_FILE["POLLEN"], HOT_R,\n         NIP_REQ["NECTAR"], NIP_REQ["POLLEN"], a.pre, a.k / 1000.0,\n         ANCH["POLLEN"], ANCH["NECTAR"]), flush=True)',
'刚度 P%.0f/N%.0f N每m 锚点P%+.1f/N%+.1f ==="\n      % (">".join(mix), R.TRAY_X1, a.phases, NIP_FILE["NECTAR"], NIP_FILE["POLLEN"], HOT_R,\n         NIP_REQ["NECTAR"], NIP_REQ["POLLEN"], KK["POLLEN"], KK["NECTAR"],\n         ANCH["POLLEN"], ANCH["NECTAR"]), flush=True)')
src = src.replace('print("=== r38v6 mix', 'print("=== r38v7 mix')
src = src.replace("        res = dict(mix=list(mix), ph0=ph0, gap=GAP, nip_req=dict(NIP_REQ), free_nip=free_nip,",
                  "        res = {}")
src = src.replace('res = dict(mix=list(mix), ph0=ph0, gap=GAP, nip_req=dict(NIP_REQ)',
                  'res = dict(mix=list(mix), ph0=ph0, gap=GAP, k_map=dict(KK), nip_req=dict(NIP_REQ)')
pathlib.Path("simulation/mujoco/_work/r38_v7.py").write_text(src, encoding="utf-8")
print("v7:", "k_map" in src, "nip_load" in src, src.count("set_nip"))
