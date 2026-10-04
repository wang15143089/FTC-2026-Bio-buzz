# -*- coding: utf-8 -*-
"""T06 POLLEN V2 R6: bridge the shell and the ball-nest pad with one smooth arc.

R5 floor = tray (5 deg) + a flat 30 x 108 x 12.8 pad at x -17..13 (top z = 24.33)
           + the 225 deg shell lip.
R6 floor = tray + a continuous arc of radius R_IN (93.96) centred on the paddle
           axis, running from the 225 deg lip down to where that circle meets the
           tray plane (260.2 deg, x = 13.5).  No step, tangent to the shell.
"""
import json, math, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path("simulation/mujoco/_work").resolve()))
import opt_lib as ol
import mujoco

pv2 = ol.pv2
OUT = Path("simulation/mujoco/out"); OUT.mkdir(parents=True, exist_ok=True)


def blades(angs, W=pv2.PADDLE_W):
    def f():
        parts = [("hub", (0., 0., 0.), (18., 17., 18.), 0., "cylY")]
        for i, a in enumerate(angs, 1):
            parts += [("arm_%d" % i, (30., 0, 0), (16., 9., 5.), a, "box"),
                      ("blade_%d" % i, (52., 0, 0), (6., W / 2., 15.), a, "box"),
                      ("flex_%d" % i, (58., 0, 0), (2., W / 2., 17.), a, "box")]
        return parts
    return f


def th2(ts):
    return blades([(360. - t) % 360. for t in ts])


def arc_pad(a0, a1, thick=7.0, n=12, r_in=None, tag="sp"):
    r_in = pv2.R_IN if r_in is None else r_in
    r_mid = r_in + thick / 2.0
    out = []
    for i in range(n):
        b0 = a0 + (a1 - a0) * i / n
        b1 = a0 + (a1 - a0) * (i + 1) / n
        bm = 0.5 * (b0 + b1)
        half = 0.5 * r_mid * math.radians(b1 - b0) * 1.35
        cx, cz = pv2.polar(r_mid, bm)
        out.append(("%s_%02d" % (tag, i), "shell", "box", (2.0 * half, pv2.FEEDER_W, thick),
                    (cx, 0.0, cz), pv2.quat_y(-(bm + 90.0))))
    return out


def r6_static(base, a1, r_in=None, tag="r6"):
    def f():
        return [t for t in base() if t[0] != "rest_pad"] + arc_pad(225.0, a1, n=12, r_in=r_in, tag=tag)
    return f


DPB = ol.GEOM["D 球窝抬高6.8"][0]
ol.GEOM["R5"] = (DPB, th2((350., 170.)))
ol.GEOM["R6"] = (r6_static(DPB, 260.2, None, "r6a"), th2((350., 170.)))
ol.GEOM["R6b"] = (r6_static(DPB, 268.0, None, "r6b"), th2((350., 170.)))
ol.GEOM["R6c"] = (r6_static(DPB, 256.0, pv2.R_IN - 2.0, "r6c"), th2((350., 170.)))


def arc_report(name, a0, a1, r_in):
    r_mid = r_in + 3.5
    print("  [%s] arc r_in=%.2f  angles %.1f..%.1f deg" % (name, r_in, a0, a1))
    for a in (a0, 0.25 * a0 + 0.75 * a1, 0.5 * (a0 + a1), 0.75 * a0 + 0.25 * a1, a1):
        x, z = pv2.polar(r_in, a)
        print("     a=%6.1f  inner pt x=%7.2f z=%7.2f   tray_top_z=%7.2f  lift=%6.2f mm"
              % (a, x, z, pv2.tray_top_z(x), z - pv2.tray_top_z(x)))


def rest_contacts(name, bx=145.0, sec=6.0):
    ol.apply_geom(name)
    xml, ctrl = pv2.build_xml(1620.0, -1, 0.0, bx, pv2.tray_top_z(bx) + pv2.BALL_R)
    m = mujoco.MjModel.from_xml_string(xml); d = mujoco.MjData(m)
    d.ctrl[:] = ctrl; mujoco.mj_forward(m, d)
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "ball")
    bg = {g for g in range(m.ngeom) if m.geom_bodyid[g] == bid}
    for _ in range(int(sec / m.opt.timestep)):
        mujoco.mj_step(m, d)
    p = d.xpos[bid] * 1000.0
    rx, rz = p[0] - pv2.PADDLE_CX, p[2] - pv2.PADDLE_CZ
    cnt = {}
    for c in range(d.ncon):
        con = d.contact[c]
        for g in (con.geom1, con.geom2):
            if g in bg:
                o = con.geom2 if g == con.geom1 else con.geom1
                nm = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, o) or ("geom%d" % o)
                cnt[nm] = cnt.get(nm, 0) + 1
    print("  [%s] rest x=%.2f z=%.2f  r=%.2f ang=%.1f  contacts=%s"
          % (name, p[0], p[2], math.hypot(rx, rz),
             math.degrees(math.atan2(rz, rx)) % 360.0, cnt))
    return p


def metrics(name, rpm, bx=145.0, sec=12.0, fr=1.0):
    r = ol.run(name, bx=bx, rpm=rpm, fr=fr, sec=sec, trace=True, fw=1620.0)
    tr = r["_trace"]
    t_set = None
    for s in tr:
        if s["v"] < 0.05 and s["t"] > 0.3:
            t_set = s["t"]; break
    t_grab = None
    base = t_set if t_set is not None else 0.0
    for s in tr:
        if s["t"] > base + 0.05 and s["v"] > 0.10:
            t_grab = s["t"]; break
    ent = next((s for s in tr if s["ang"] < 232.0 and 45.0 <= s["r"] <= 70.0), None)
    ex = next((s for s in tr if s["ang"] <= 143.0 and 45.0 <= s["r"] <= 70.0), None)
    carry = (ex["t"] - ent["t"]) if (ent and ex) else -1.0
    w = rpm * 2.0 * math.pi / 60.0
    vslip = -1.0
    if ent and ex and carry > 0:
        seg = [s for s in tr if ent["t"] <= s["t"] <= ex["t"]]
        vmean = sum(s["v"] for s in seg) / len(seg)
        vslip = 1.0 - vmean / (w * pv2.R_CARRY)
    print("  [%s @%3g rpm bx=%g] settled=%.2f grabbed=%.2f creep=%s carry=%s slip=%s "
          "launched=%s peak=%.3f Nm"
          % (name, rpm, bx, t_set or -1, t_grab or -1,
             ("%.2f" % (t_grab - base)) if (t_grab and t_set) else "-",
             ("%.2f" % carry) if carry > 0 else "-",
             ("%.0f%%" % (100 * vslip)) if vslip >= 0 else "-",
             r["launched"], r["torque_peak_Nm"]))
    return r


def thr(name, rpm, bx, tol=0.03, sec=12.0):
    t0 = ol.threshold(name, lo=0.20, hi=1.60, tol=tol, bx=bx, rpm=rpm, fr=1.0, sec=sec, fw=1620.0)
    print("  [%s @%3g rpm bx=%g] torque threshold = %s Nm" % (name, rpm, bx, t0[0]))
    return t0


def main():
    print("=== R6 smooth shell-pad arc: geometry ===")
    arc_report("R6", 225.0, 260.2, pv2.R_IN)
    arc_report("R6b", 225.0, 268.0, pv2.R_IN)
    arc_report("R6c", 225.0, 256.0, pv2.R_IN - 2.0)
    print("  R_IN=%.2f  R_OUT=%.2f  ball R=%.2f  R_CARRY=%.2f  tray foot x=%.2f"
          % (pv2.R_IN, pv2.R_OUT, pv2.BALL_R, pv2.R_CARRY, 29.49))

    print()
    print("=== rest position / contact (paddle static, ball in at x=145) ===")
    for nm in ("R5", "R6", "R6b", "R6c"):
        rest_contacts(nm)

    print()
    print("=== creep + carry metrics ===")
    for nm in ("R5", "R6", "R6c"):
        for rpm in (40, 70, 90, 105):
            metrics(nm, rpm)

    print()
    print("=== launch torque threshold (12 s, both entry heights) ===")
    res = {}
    for nm in ("R5", "R6", "R6c"):
        for rpm in (90, 105):
            for bx in (145.0, 138.0):
                res["%s_%g_%g" % (nm, rpm, bx)] = thr(nm, rpm, bx)[0]
    (OUT / "_r6_thresholds.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print()
    print("saved", OUT / "_r6_thresholds.json")


if __name__ == "__main__":
    main()
