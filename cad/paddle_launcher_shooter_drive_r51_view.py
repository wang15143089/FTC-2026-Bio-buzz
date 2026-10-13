"""T06 R51 shooter assembly views (top + side + the gap-adjust travel)."""

from __future__ import annotations

import math
import pickle
import sys
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import paddle_launcher_shooter_drive_r51 as R      # noqa: E402
import paddle_launcher_constrained as K             # noqa: E402

W, H = 1240, 820
LIGHT = (0.40, 0.58, 0.71)

COL = {
    "plate": (92, 130, 220, 150),
    "motor": (58, 58, 66, 235),
    "clamp": (208, 122, 58, 235),
    "coupler": (232, 176, 40, 235),
    "carriage": (74, 196, 150, 240),
    "servo": (70, 70, 82, 240),
    "servoframe": (146, 146, 198, 200),
    "link": (236, 84, 168, 235),
    "gap": (150, 70, 190, 235),
    "ctx": (150, 154, 162, 38),
}


def colour_of(n):
    if n.startswith("shooter_side_plate"):
        return COL["plate"]
    if n.startswith("flywheel_motor"):
        return COL["motor"]
    if n.startswith("motor_clamp"):
        return COL["clamp"]
    if "coupler" in n:
        return COL["coupler"]
    if n.startswith(("bearing_carriage", "carriage_guide", "bearing_insert")):
        return COL["carriage"]
    if n.startswith(("main_spacing_link", "carriage_link", "crosshead",
                     "servo_crank", "servo_drag_link")):
        return COL["link"]
    if n.startswith(("gap_servo", "servo_spline_hub")):
        return COL["gap"]
    if n.startswith("paddle_servo_frame"):
        return COL["servoframe"]
    if n.startswith("paddle_servo"):
        return COL["servo"]
    return COL["ctx"]


def raw_tris(shape, tol):
    out = []
    for s in shape.Solids():
        try:
            vs, fs = s.tessellate(tol)
        except Exception:
            continue
        for f in fs:
            a, b, c = vs[f[0]], vs[f[1]], vs[f[2]]
            out.append(((a.x, a.y, a.z), (b.x, b.y, b.z), (c.x, c.y, c.z)))
    return out


def tris(name, shape):
    tol = 2.6 if colour_of(name) is COL["ctx"] else 0.8
    cache = R.OUT / ("v_tris_%s_%.1f.pkl" % (name.replace("/", "_"), tol))
    raw = None
    if cache.exists():
        try:
            raw = pickle.loads(cache.read_bytes())
        except Exception:
            raw = None
    if raw is None:
        raw = raw_tris(shape, tol)
        cache.write_bytes(pickle.dumps(raw, protocol=4))
    return raw


def render(parts, mode, box, title, note, marks=()):
    x0, x1, v0, v1 = box
    groups = []
    for n, shp in parts.items():
        if mode == "xy" and n.startswith("gecko_flywheel"):
            pass
        c = colour_of(n)
        for tri in tris(n, shp):
            key = (0.3333 * sum(v[1] for v in tri) if mode == "xy"
                   else 0.3333 * sum(v[2] for v in tri))
            groups.append((key, c, tri))
    groups.sort(key=lambda g: g[0])

    img = Image.new("RGB", (W, H), (255, 255, 255))
    dr = ImageDraw.Draw(img, "RGBA")
    scale = min(W / (x1 - x0), H / (v1 - v0))
    ox = 0.5 * (W - scale * (x1 - x0))
    oy = 0.5 * (H - scale * (v1 - v0))
    gx = lambda x: ox + scale * (x - x0)
    gy = lambda v: oy + scale * (v1 - v)
    if mode == "xy":
        proj = lambda p: (gx(p[0]), gy(p[1]))
    else:
        proj = lambda p: (gx(p[0]), gy(p[2]))

    for _, col, tri in groups:
        a, b, c = tri
        ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
        vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
        nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
        ln = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
        sh = 0.36 + 0.64 * abs((nx * LIGHT[0] + ny * LIGHT[1]
                                + nz * LIGHT[2]) / ln)
        dr.polygon([proj(a), proj(b), proj(c)],
                   fill=(int(col[0] * sh), int(col[1] * sh), int(col[2] * sh),
                         col[3]))

    f_sm = _font(19, bold=False)
    for m in marks:
        if "circle" in m:
            cx, cv, r = m["circle"]
            dr.ellipse([gx(cx - r), gy(cv + r), gx(cx + r), gy(cv - r)],
                       outline=m["color"], width=3)
        if "dot" in m:
            px, pv = m["dot"]
            px, pv = gx(px), gy(pv)
            dr.line([(px - 14, pv), (px + 14, pv)], fill=m["color"], width=3)
            dr.line([(px, pv - 14), (px, pv + 14)], fill=m["color"], width=3)
        if "label" in m:
            tx, tv = m["label"][:2]
            txt = m.get("text", "")
            dr.text((gx(tx), gy(tv)), txt, fill=m["color"], font=f_sm)
        if "arrow" in m:
            (ax0, av0), (ax1, av1) = m["arrow"]
            dr.line([(gx(ax0), gy(av0)), (gx(ax1), gy(av1))], fill=m["color"],
                    width=3)

    f_big = _font(27)
    dr.rectangle([8, 8, 8 + int(dr.textlength(title, font=f_big)) + 24, 47],
                 fill=(0, 0, 0, 210))
    dr.text((20, 13), title, fill=(255, 255, 255), font=f_big)
    dr.text((12, H - 30), note, fill=(40, 40, 40), font=f_sm)
    _axes(dr, mode, gx, gy)
    return img


def _font(sz, bold=True):
    for p in (("C:/Windows/Fonts/msyhbd.ttc", "C:/Windows/Fonts/msyh.ttc")
              if bold else ("C:/Windows/Fonts/msyh.ttc",)):
        try:
            return ImageFont.truetype(p, sz)
        except Exception:
            pass
    return ImageFont.load_default()


def _axes(dr, mode, gx, gy):
    if mode == "xy":
        dr.line([(gx(-165), gy(0)), (gx(260), gy(0))], fill=(185, 185, 195, 200))
        dr.line([(gx(0), gy(-245)), (gx(0), gy(175))], fill=(185, 185, 195, 200))
        dr.text((gx(245), gy(0) + 4), "+X", fill=(90, 90, 100))
        dr.text((gx(0) + 8, gy(168)), "+Y", fill=(90, 90, 100))
        dr.text((gx(0) + 8, gy(-234)), "-Y", fill=(90, 90, 100))


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "pollen"
    half = R.SETTINGS[name]
    t0 = time.time()
    assy, parts, kin = R.build(name, half)
    print("[view %s] build %.1f s, %d parts" % (name, time.time() - t0, len(parts)),
          flush=True)

    up64 = K.to_world(K.box(1, 1, 1, (0, 0, R.SETTINGS["pollen"])))
    lo64 = K.to_world(K.box(1, 1, 1, (0, 0, -R.SETTINGS["pollen"])))
    up86 = K.to_world(K.box(1, 1, 1, (0, 0, R.SETTINGS["nectar"])))
    lo86 = K.to_world(K.box(1, 1, 1, (0, 0, -R.SETTINGS["nectar"])))
    c = lambda s: (0.5 * (s.BoundingBox().xmin + s.BoundingBox().xmax),
                   0.5 * (s.BoundingBox().zmin + s.BoundingBox().zmax))
    c64u, c64l, c86u, c86l = c(up64), c(lo64), c(up86), c(lo86)

    frames = [
        render(parts, "xy", (-170.0, 265.0, -245.0, 175.0),
               "A  俯视：+Y 舵机 / -Y 两台飞轮马达",
               "两台 5203-2402-0003 直驱（-Y），拨杆 2000-0025-0004 + 支架 + 联轴器（+Y），"
               "外侧两块开窗侧板；两根飞轮轴各自独立"),
        render(parts, "xz", (-175.0, 265.0, -40.0, 405.0),
               "B  侧视（沿 -Y 看）：整机",
               "两侧开窗侧板 + 底盘纵梁 = 支撑；调隙链（2000-0025-0002 曲柄-拉杆-十字滑块-两根 110 连杆）"
               "只驱动滑座，不上锁"),
        render(parts, "xz", (-140.0, 250.0, 140.0, 400.0),
               "C  侧视放大：发射部分 + 调隙行程",
               "红/蓝十字 = 夹口 64 / 86 时的轴心；窗口行程 80.0-91.2 mm（夹口 64.0-86.4）",
               marks=[
                   {"dot": c64u, "color": (232, 60, 60, 255)},
                   {"dot": c64l, "color": (232, 60, 60, 255)},
                   {"dot": c86u, "color": (40, 90, 232, 255)},
                   {"dot": c86l, "color": (40, 90, 232, 255)},
                   {"arrow": (c64u, c86u), "color": (30, 30, 30, 255)},
                   {"label": (c64u[0] - 44, c64u[1] - 30),
                    "color": (30, 30, 30, 255),
                    "text": "夹口 64 -> 86：轴心行 11.2 mm"},
               ]),
    ]

    top = Image.new("RGB", (2 * W + 46, 2 * H + 46), (250, 250, 252))
    for i, (f, pos) in enumerate(zip(frames + [frames[1]], [(0, 0), (W + 46, 0),
                                                            (0, H + 46)])):
        top.paste(f, pos)
    out = R.OUT / ("r51_shooter_view_%s.png" % name)
    top.save(out)
    print("[view] -> %s" % out, flush=True)


if __name__ == "__main__":
    main()
