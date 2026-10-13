# -*- coding: utf-8 -*-
"""R49 check picture: orthographic XZ side view of the gate drive, both poses.

Camera is on +Y looking toward -Y, so we see the blade face-on and the servo
stack behind it.  Background (R47) parts are drawn translucent so the new gate
and linkage stay readable.  Painter's algorithm on triangle mean Y -- good
enough for a "does anything look wrong" check.

Output: cad/output/_r49_gate/r49_gate_drive_view.png
"""
from __future__ import annotations

import json
import math
import pickle
import sys
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import paddle_launcher_gate_drive_r49 as R                    # noqa: E402

X0, X1, Z0, Z1 = -100.0, 262.0, -30.0, 300.0
W, H, GAP = 1000, 940, 52
LIGHT = (0.40, 0.58, 0.71)
CTX_TOL = 2.5
ON_TOP = ("gate_blade", "gate_yoke")

CTX = (150, 154, 162, 42)


class V:
    """Picklable stand-in for an OCC vertex (needs .x/.y/.z)."""

    __slots__ = ("x", "y", "z")

    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z


def _v(p):
    return p if hasattr(p, "x") else V(p[0], p[1], p[2])


COL = {
    "kept": CTX,
    "gate_frame": (112, 124, 205, 150),
    "gate_blade": (232, 88, 58, 255),
    "gate_yoke": (244, 158, 62, 255),
    "gate_bracket": (114, 190, 120, 185),
    "gate_servo": (74, 74, 84, 240),
    "gate_crank": (152, 92, 214, 255),
    "gate_rod": (36, 168, 222, 255),
    "pin": (250, 208, 60, 255),
    "ball": (255, 118, 168, 255),
}


def col_of(name):
    if name.startswith("gate_pin_"):
        return COL["pin"]
    if name.startswith("ball_"):
        return COL["ball"]
    return COL.get(name, CTX)


def tris_of(shape, tol, col, plain=False):
    out = []
    for s in shape.Solids():
        try:
            vs, fs = s.tessellate(tol)
        except Exception:
            continue
        for f in fs:
            a, b, c = vs[f[0]], vs[f[1]], vs[f[2]]
            if plain:
                out.append(((a.x, a.y, a.z), (b.x, b.y, b.z), (c.x, c.y, c.z)))
            else:
                out.append((0.3333 * (a.y + b.y + c.y), col, a, b, c))
    return out


def ctx_tris(name, shape):
    """Background tessellation is slow, so cache the flat triangle list."""
    cache = R.OUT / ("tris_ctx_%s_%.1f.pkl" % (name, CTX_TOL))
    if cache.exists():
        try:
            raw = pickle.loads(cache.read_bytes())
            return [(0.3333 * (a[1] + b[1] + c[1]), CTX, _v(a), _v(b), _v(c))
                    for a, b, c in raw]
        except Exception:
            pass
    raw = tris_of(shape, CTX_TOL, CTX, plain=True)
    cache.write_bytes(pickle.dumps(raw, protocol=4))
    return [(0.3333 * (a[1] + b[1] + c[1]), CTX, a, b, c) for a, b, c in raw]


def render(parts, path):
    scene, top = [], []
    for name, shp in parts.items():
        if name in R.ctx_cache.get("pollen", ()):
            grp = ctx_tris(name, shp)
        else:
            grp = tris_of(shp, 0.55, col_of(name))
        (top if name in ON_TOP else scene).extend(grp)
    scene.sort(key=lambda t: t[0])

    img = Image.new("RGB", (W, H), (255, 255, 255))
    dr = ImageDraw.Draw(img, "RGBA")
    scale = min(W / (X1 - X0), H / (Z1 - Z0))
    ox = 0.5 * (W - scale * (X1 - X0))
    oy = 0.5 * (H - scale * (Z1 - Z0))
    px = lambda x: ox + scale * (x - X0)
    pz = lambda z: oy + scale * (Z1 - z)

    for group in (scene, top):
        for _, col, a, b, c in group:
            ux, uy, uz = b.x - a.x, b.y - a.y, b.z - a.z
            vx, vy, vz = c.x - a.x, c.y - a.y, c.z - a.z
            nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
            ln = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
            sh = 0.34 + 0.66 * abs((nx * LIGHT[0] + ny * LIGHT[1]
                                    + nz * LIGHT[2]) / ln)
            dr.polygon([(px(a.x), pz(a.z)), (px(b.x), pz(b.z)),
                        (px(c.x), pz(c.z))],
                       fill=(int(col[0] * sh), int(col[1] * sh), int(col[2] * sh),
                             col[3]))
    return img, dr, px, pz


def font(sz, bold=True):
    for p in (("C:/Windows/Fonts/msyhbd.ttc", "C:/Windows/Fonts/msyh.ttc")
              if bold else ("C:/Windows/Fonts/msyh.ttc",)):
        try:
            return ImageFont.truetype(p, sz)
        except Exception:
            pass
    return ImageFont.load_default()


def main():
    t0 = time.time()
    kept = dict(R.kept_parts("pollen"))
    kept.pop("gate_blade", None)
    kept.pop("gate_yoke", None)
    kept.pop("gate_frame", None)

    f_big, f_mid, f_sm = font(30), font(24), font(21, bold=False)
    canvas = Image.new("RGB", (W, 2 * H + GAP), (255, 255, 255))
    canvas_dr = ImageDraw.Draw(canvas, "RGBA")
    info = {"panels": []}

    for row, (title, phi) in enumerate(
            (("A  关闭位（挡球）  crank 20°", R.PHI_DN),
             ("B  打开位（放行）  crank 160°", R.PHI_UP))):
        parts = dict(kept)
        parts.update(R.drive_parts(phi))
        img, dr, px, pz = render(parts, None)
        yoff = row * (H + GAP)
        canvas.paste(img, (0, yoff))
        dr = ImageDraw.Draw(canvas, "RGBA")

        zs = R.yoke_pin_z(phi)
        bc = R.blade_centre(phi)
        zb = bc - R.GATE_H / 2.0
        bcz = R.tray_top_z(R.GATE_X + R.GATE_T / 2.0 + R.F.BALL_R) + R.F.BALL_R

        # blade silhouette (side view: x 177.5..182.5, z bc +/- 27.5)
        dr.rectangle([px(R.GATE_X - R.GATE_T / 2.0), yoff + pz(bc + R.GATE_H / 2.0),
                      px(R.GATE_X + R.GATE_T / 2.0), yoff + pz(bc - R.GATE_H / 2.0)],
                     outline=(190, 30, 30), width=3)
        # reference lines
        dr.line([(px(-95), yoff + pz(bcz)), (px(250), yoff + pz(bcz))],
                fill=(0, 165, 0, 220), width=2)
        dr.line([(px(-95), yoff + pz(40.0)), (px(250), yoff + pz(40.0))],
                fill=(0, 120, 200, 200), width=2)
        cx, cz = R.CRANK_CX, R.CRANK_CZ
        dr.ellipse([px(cx) - 5, yoff + pz(cz) - 5, px(cx) + 5, yoff + pz(cz) + 5],
                   fill=(120, 0, 200, 255))
        rpx, rpz = R.crank_pin(phi)
        dr.ellipse([px(rpx) - 5, yoff + pz(rpz) - 5, px(rpx) + 5, yoff + pz(rpz) + 5],
                   fill=(240, 170, 0, 255))
        dr.ellipse([px(R.GATE_X) - 5, yoff + pz(zs) - 5, px(R.GATE_X) + 5,
                    yoff + pz(zs) + 5], fill=(240, 170, 0, 255))

        dr.rectangle([8, yoff + 8, 8 + 640, yoff + 48], fill=(0, 0, 0, 210))
        dr.text((20, yoff + 14), title, fill=(255, 255, 255), font=f_big)
        dr.text((px(260) - 300, yoff + pz(bcz) - 30), "球心 z=%.1f" % bcz,
                fill=(0, 150, 0), font=f_sm)
        dr.text((px(-92), yoff + pz(40.0) - 28), "挡舌下端 z=%.1f" % zb,
                fill=(0, 110, 190), font=f_sm)
        dr.text((px(cx) + 14, yoff + pz(cz) - 34), "曲柄中心 z=%.0f" % cz,
                fill=(110, 0, 190), font=f_sm)
        info["panels"].append({"pose": title, "blade_centre_mm": round(bc, 3),
                               "blade_bottom_mm": round(zb, 3),
                               "yoke_pin_mm": round(zs, 3),
                               "crank_pin_mm": [round(rpx, 3), round(rpz, 3)]})

    legend = [("挡舌", COL["gate_blade"]), ("连杆座", COL["gate_yoke"]),
              ("曲柄", COL["gate_crank"]), ("连杆", COL["gate_rod"]),
              ("销", COL["pin"]), ("舵机", COL["gate_servo"]),
              ("支架", COL["gate_bracket"]), ("球", COL["ball"]),
              ("R47 背景", (150, 154, 162, 255))]
    f_leg = font(20, bold=False)
    base = 2 * H + GAP - 34
    x, yrow = 12, base
    for name, c in legend:
        wid = int(canvas_dr.textlength(name, font=f_leg)) + 46
        if x + wid > W - 8:
            x, yrow = 12, yrow + 30
        canvas_dr.rectangle([x, yrow, x + 20, yrow + 20],
                            fill=(c[0], c[1], c[2], 255), outline=(60, 60, 60, 255))
        canvas_dr.text((x + 26, yrow - 1), name, fill=(30, 30, 30), font=f_leg)
        x += wid

    out = R.OUT / "r49_gate_drive_view.png"
    canvas.save(out)
    (R.OUT / "r49_gate_drive_view.json").write_text(
        json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8")
    print("saved %s  (%.1f s)" % (out, time.time() - t0))
    return str(out)


if __name__ == "__main__":
    main()
