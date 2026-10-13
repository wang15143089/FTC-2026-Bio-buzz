# -*- coding: utf-8 -*-
"""R50 check picture: three orthographic panels of the new drive + frame.

  A  top view    (looking down +Z)  -- shows the Y stacking: both motors and
                 their clamps on -Y, the R37 machine in the middle, the servo
                 stack on +Y, the two frame plates and the cross rails.
  B  side view   (looking along -Y) -- XZ placement of the plates, rails and
                 the three axles.
  C  drive only  -- same side view with the shell / tray / gate hidden, so the
                 motor-and-coupler stack and the servo stack can be read.

Background parts are translucent.  Painter's algorithm on the mean coordinate
of each triangle is good enough for a "does anything look wrong" check.

Output: cad/output/_r50_drive/r50_shooter_drive_view.png
"""
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

import paddle_launcher_shooter_drive_r50 as R                    # noqa: E402

W, H, GAP = 1160, 760, 46
LIGHT = (0.40, 0.58, 0.71)
CTX_TOL, NEW_TOL = 2.4, 0.7

CTX = (148, 152, 160, 46)
COL = {
    "frame": (92, 130, 220, 140),
    "motor": (58, 58, 66, 235),
    "clamp": (208, 122, 58, 235),
    "coupler": (232, 176, 40, 235),
    "bearing": (110, 198, 148, 240),
    "servo": (70, 70, 82, 240),
    "servoframe": (146, 146, 198, 190),
}

DRIVE_WHITELIST = ("shooter_frame", "shooter_rail", "motor_bridge",
                   "servo_bridge", "flywheel_motor", "motor_clamp",
                   "motor_coupler", "flywheel_bearing", "paddle_bearing",
                   "paddle_servo", "paddle_shaft_", "flywheel_shaft_",
                   "gecko_flywheel", "paddle_rotor", "paddle_flex_tip")


def colour_of(n):
    if n.startswith(("shooter_frame", "shooter_rail", "motor_bridge",
                     "servo_bridge")):
        return COL["frame"]
    if n.startswith("flywheel_motor"):
        return COL["motor"]
    if n.startswith("motor_clamp"):
        return COL["clamp"]
    if "coupler" in n:
        return COL["coupler"]
    if "bearing" in n:
        return COL["bearing"]
    if n.startswith("paddle_servo_frame"):
        return COL["servoframe"]
    if n.startswith("paddle_servo"):
        return COL["servo"]
    return CTX


def is_context(n):
    return colour_of(n) is CTX


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
    tol = CTX_TOL if is_context(name) else NEW_TOL
    cache = R.OUT / ("tris_%s_%.1f.pkl" % (name.replace("/", "_"), tol))
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


def render(parts, mode, box, title, note):
    x0, x1, y0, y1 = box
    groups = []
    for n, shp in parts.items():
        c = colour_of(n)
        for tri in tris(n, shp):
            key = (0.3333 * sum(v[1] for v in tri) if mode == "xy"
                   else 0.3333 * sum(v[2] for v in tri))
            groups.append((key, c, tri, n))
    groups.sort(key=lambda g: g[0])

    img = Image.new("RGB", (W, H), (255, 255, 255))
    dr = ImageDraw.Draw(img, "RGBA")
    scale = min(W / (x1 - x0), H / (y1 - y0))
    ox = 0.5 * (W - scale * (x1 - x0))
    oy = 0.5 * (H - scale * (y1 - y0))
    if mode == "xy":
        gx = lambda x: ox + scale * (x - x0)
        gy = lambda v: oy + scale * (y1 - v)
        proj = lambda p: (gx(p[0]), gy(p[1]))
    else:
        gx = lambda x: ox + scale * (x - x0)
        gy = lambda v: oy + scale * (y1 - v)
        proj = lambda p: (gx(p[0]), gy(p[2]))

    for _, col, tri, _n in groups:
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

    f_big = _font(28)
    f_sm = _font(19, bold=False)
    dr.rectangle([8, 8, 8 + int(dr.textlength(title, font=f_big)) + 24, 48],
                 fill=(0, 0, 0, 210))
    dr.text((20, 14), title, fill=(255, 255, 255), font=f_big)
    dr.text((12, H - 30), note, fill=(40, 40, 40), font=f_sm)
    _axes(dr, mode, gx, gy, scale)
    return img


def _font(sz, bold=True):
    for p in (("C:/Windows/Fonts/msyhbd.ttc", "C:/Windows/Fonts/msyh.ttc")
              if bold else ("C:/Windows/Fonts/msyh.ttc",)):
        try:
            return ImageFont.truetype(p, sz)
        except Exception:
            pass
    return ImageFont.load_default()


def _axes(dr, mode, gx, gy, scale):
    if mode == "xy":
        dr.line([(gx(-160), gy(0)), (gx(250), gy(0))], fill=(180, 180, 190, 200))
        dr.line([(gx(0), gy(-235)), (gx(0), gy(165))], fill=(180, 180, 190, 200))
        dr.text((gx(240), gy(0) + 4), "+X", fill=(90, 90, 100))
        dr.text((gx(0) + 6, gy(160)), "+Y (servo)", fill=(90, 90, 100))
        dr.text((gx(0) + 6, gy(-205)), "-Y (motors)", fill=(90, 90, 100))


def render_doc(name, parts, out_dir):
    t0 = time.time()
    frames = []
    frames.append(render(
        parts, "xy", (-175.0, 255.0, -235.0, 175.0),
        "A  俯视（+Z 向下看）",
        "Y 向堆叠：-Y = 两台飞轮马达 + 夹具 + 联轴器；中间 = R37 送料/发射本体；"
        "+Y = 拨杆舵机 (25-4) + 支撑框架"))
    frames.append(render(
        parts, "xz", (-175.0, 255.0, -60.0, 385.0),
        "B  侧视（沿 -Y 看）",
        "两块侧板 / 三根横梁 / 三个轴心；横梁放在无干涉的 XZ 空白区"))
    sub = {k: v for k, v in parts.items()
           if any(k.startswith(p) for p in DRIVE_WHITELIST)}
    frames.append(render(
        sub, "xz", (-110.0, 215.0, -40.0, 370.0),
        "C  仅驱动（外壳/托板/闸门隐藏）",
        "马达 - 夹具 - 联轴器 - 飞轮轴 - 轴承 - 侧板 与 拨杆舵机 - 支架 - 联轴器 的轴向堆叠"))

    canvas = Image.new("RGB", (W, 3 * H + 2 * GAP + 40), (255, 255, 255))
    for i, im in enumerate(frames):
        canvas.paste(im, (0, i * (H + GAP)))
    dr = ImageDraw.Draw(canvas, "RGBA")
    legend = [("支撑框架(打印)", COL["frame"]), ("飞轮马达", COL["motor"]),
              ("马达夹具", COL["clamp"]), ("联轴器", COL["coupler"]),
              ("轴承", COL["bearing"]), ("拨杆舵机", COL["servo"]),
              ("舵机支架", COL["servoframe"]), ("R37/R49 本体", (150, 154, 162, 255))]
    f_leg = _font(20, bold=False)
    base = 3 * H + 2 * GAP + 8
    x = 14
    for nm, c in legend:
        wid = int(dr.textbbox((0, 0), nm, font=f_leg)[2]) + 52
        dr.rectangle([x, base, x + 20, base + 20],
                     fill=(c[0], c[1], c[2], 255), outline=(60, 60, 60, 255))
        dr.text((x + 26, base - 1), nm, fill=(30, 30, 30), font=f_leg)
        x += wid
    out = out_dir / "r50_shooter_drive_view.png"
    canvas.save(out)
    print("[r50] view -> %s (%.1f s)" % (out, time.time() - t0), flush=True)
    return str(out)


if __name__ == "__main__":
    raise SystemExit(R.main(sys.argv[1:]))
