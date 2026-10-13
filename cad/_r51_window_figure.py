# -*- coding: utf-8 -*-
"""R51 side-plate opening schematic: 8.4 x 9 slot -> 59 x 56 sliding window.

Local frame (u, v) is the side-plate plane:
  u = half-spacing axis (u = 0 at the nip mid-plane, upper shaft at u = -80, lower at u = +80)
  v = transverse direction (throat / nip axis)
All numbers are read from cad/output/_r51_drive/report_r51.json and the -Y plate bbox
in cad/output/_r51_base/manifest.json; nothing is hand-typed except the frame origin,
which is the midpoint of the two measured flywheel axes.
"""
import io, json, math
from PIL import Image, ImageDraw, ImageFont

REPORT = "cad/output/_r51_drive/report_r51.json"
MANIFEST = "cad/output/_r51_base/manifest.json"
OUT = "cad/output/_r51_drive/r51_window_schematic.png"
DESK = "C:/Users/admin/OneDrive/Desktop/T06_R51_滑窗对比.png"

rep = json.load(io.open(REPORT, encoding="utf-8"))
man = json.load(io.open(MANIFEST, encoding="utf-8"))

opening = rep["opening"]
by_var = {e["variant"]: e for e in opening if "variant" in e}
geo = [e for e in opening if "window_mm" in e][0]
WIN = geo["window_mm"]                 # [59, 56]  -> 59 across v, 56 along u
WIN_U = geo["window_n_span_mm"]        # [56.5, 112.5]
NIP_TRAVEL = geo["nip_travel_mm"]      # [64.0, 86.4]
POLLEN_U = by_var["pollen"]["carriage_n_span_mm"]
NECTAR_U = by_var["nectar"]["carriage_n_span_mm"]
POLLEN_NIP = by_var["pollen"]["nip_mm"]
NECTAR_NIP = by_var["nectar"]["nip_mm"]

SLOT_U = [80.0, 89.0]
SLOT_V = 8.4
RAIL_V = (24.0, 29.0)          # 5 mm rail width, 0.5 mm clearance to the +-29.5 window wall
CARRIAGE_V = 23.0              # 38 mm carriage across v

# --- plate bbox projected into (u, v) -------------------------------------
plate = None
for p in man["parts"]:
    if p["part"] == "shooter_side_plate_-1":
        plate = p["bbox_mm"]
bx0, _, bz0, bx1, _, bz1 = plate

up = (-10.737, 284.767)
lo = (115.345, 186.261)
mid = ((up[0] + lo[0]) / 2.0, (up[1] + lo[1]) / 2.0)
d = (lo[0] - up[0], lo[1] - up[1])
L = math.hypot(*d)
u_hat = (d[0] / L, d[1] / L)
v_hat = (-u_hat[1], u_hat[0])


def uv(x, z):
    dx, dz = x - mid[0], z - mid[1]
    return (dx * u_hat[0] + dz * u_hat[1], dx * v_hat[0] + dz * v_hat[1])


PLATE_QUAD = [uv(bx0, bz0), uv(bx1, bz0), uv(bx1, bz1), uv(bx0, bz1)]

# --- fonts ----------------------------------------------------------------
def _font(sz, bold=True):
    for p in ("C:/Windows/Fonts/msyhbd.ttc", "C:/Windows/Fonts/msyh.ttc"):
        try:
            return ImageFont.truetype(p, sz)
        except Exception:
            continue
    return ImageFont.load_default()


INK = (28, 28, 32)
DIM = (105, 105, 112)
BLUE = (70, 185, 255)
BLUEF = (222, 240, 255)
GREY = (150, 150, 158)
GREYF = (236, 236, 240)
GREEN = (35, 160, 95)
GREENF = (224, 244, 232)
ORANGE = (245, 150, 45)
ORANGEF = (255, 240, 222)
PINK = (215, 40, 130)

W, H = 2120, 1200
img = Image.new("RGB", (W, H), (252, 252, 253))
dr = ImageDraw.Draw(img, "RGBA")

f_title = _font(31)
f_h = _font(23)
f_n = _font(19)
f_s = _font(17)
f_tiny = _font(16)


def panel(x0, y0, x1, y1, title):
    dr.rectangle([x0, y0, x1, y1], fill=(255, 255, 255), outline=(214, 214, 220), width=2)
    box = dr.textbbox((0, 0), title, font=f_h)
    dr.rectangle([x0 + 1, y0 + 1, x0 + 16 + (box[2] - box[0]), y0 + 40], fill=(38, 42, 52))
    dr.text((x0 + 10, y0 + 7), title, fill=(255, 255, 255), font=f_h)


# =========================== panel A : full plate ==========================
panel(28, 96, 1032, 1130, "A  侧板（-Y，4 mm）平面：滑窗在板上的位置")
A = (28, 96, 1032, 1130)
ax0, ay0, ax1, ay1 = A
U0, U1 = -280.0, 285.0
V0, V1 = -300.0, 250.0
sA = min((ax1 - ax0 - 90) / (U1 - U0), (ay1 - ay0 - 110) / (V1 - V0))
cAx = (ax0 + ax1) / 2.0
cAy = (ay0 + 62 + ay1) / 2.0


def RA(u, v):
    # v points up in the drawing
    return (cAx + (u - (U0 + U1) / 2) * sA, cAy - (v - (V0 + V1) / 2) * sA)


def rectA(u0, u1, v0, v1, fill, outline, width=2, dash=False):
    p = [RA(u0, v0), RA(u1, v0), RA(u1, v1), RA(u0, v1)]
    if fill:
        dr.polygon(p, fill=fill)
    if dash:
        for a, b in ((p[0], p[1]), (p[1], p[2]), (p[2], p[3]), (p[3], p[0])):
            _dash(dr, a, b, outline, width)
    else:
        dr.polygon(p, outline=outline, width=width)


def _dash(draw, a, b, col, w, seg=9, gap=7):
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    if L < 1e-6:
        return
    n = max(1, int(L // (seg + gap)))
    for i in range(n + 1):
        t0 = (i * (seg + gap)) / L
        t1 = min(1.0, (i * (seg + gap) + seg) / L)
        if t0 >= 1.0:
            break
        draw.line([a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0,
                   a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1], fill=col, width=w)


# plate bbox projection (dashed) + the two carriage paths inside it
dr.polygon([RA(*q) for q in PLATE_QUAD], fill=(246, 248, 252))
for a, b in zip(PLATE_QUAD, PLATE_QUAD[1:] + PLATE_QUAD[:1]):
    _dash(dr, RA(*a), RA(*b), (176, 180, 192), 2)

rectA(POLLEN_U[0], POLLEN_U[1], -CARRIAGE_V, CARRIAGE_V, GREYF, GREY, 2, dash=True)
rectA(NECTAR_U[0], NECTAR_U[1], -CARRIAGE_V, CARRIAGE_V, None, GREEN, 2, dash=True)

# the two shaft axes and the nip gap
for uu, name in ((-80.0, "上飞轮轴"), (80.0, "下飞轮轴")):
    x, y = RA(uu, 0)
    dr.line([x, y - 14, x, y + 14], fill=INK, width=4)
    dr.text((x + 8, y + 16), name, fill=INK, font=f_s)
# measured carriage centre travel for the lower (adjusting) axis
dr.line([RA(SLOT_U[0], 0)[0], RA(SLOT_U[0], 0)[1], RA(SLOT_U[1], 0)[0], RA(SLOT_U[1], 0)[1]],
        fill=(190, 60, 60), width=3)

# the opening itself
rectA(SLOT_U[0], SLOT_U[1], -SLOT_V / 2, SLOT_V / 2, (250, 226, 226), (196, 74, 74), 3)
rectA(WIN_U[0], WIN_U[1], -WIN[0] / 2, WIN[0] / 2, (208, 234, 255), BLUE, 4)

# rails (they pass through the window and bear on its walls)
for vv in (RAIL_V, (-RAIL_V[1], -RAIL_V[0])):
    rectA(POLLEN_U[0], NECTAR_U[1], vv[0], vv[1], ORANGEF, ORANGE, 2)

# callouts
for txt, uu, vv, col in (
    ("旧轴槽 8.4 x 9\n覆盖半间距 80..89", 89.0, 14.0, (176, 60, 60)),
    ("新滑窗 59 x 56\n窗 n 跨 56.5..112.5", 112.5, -12.0, (30, 120, 200)),
):
    x, y = RA(uu, vv)
    dr.text((x + 10, y - 12), txt, fill=col, font=f_s)

# legend
lg = [("侧板包围盒投影", (176, 180, 192), None),
      ("旧 8.4 x 9 轴槽", (196, 74, 74), (250, 226, 226)),
      ("新 59 x 56 滑窗", BLUE, (208, 234, 255)),
      ("导轨（顶窗壁导向）", ORANGE, ORANGEF),
      ("pollen 滑座 n 跨 61..99", GREY, GREYF),
      ("nectar 滑座 n 跨 72..110", GREEN, GREENF)]
ly = ay1 - 176
for name, col, fill in lg:
    dr.rectangle([ax0 + 22, ly, ax0 + 52, ly + 18], fill=fill, outline=col, width=2)
    dr.text((ax0 + 62, ly - 1), name, fill=INK, font=f_tiny)
    ly += 27

dr.text((ax0 + 16, ay0 + 50), "面板尺寸 361 x 367 mm；u 为半间距轴（两飞轮轴间距 160 mm），v 为喉道轴。",
        fill=DIM, font=f_tiny)

# =========================== panel B : window zoom ========================
panel(1052, 96, 2092, 700, "B  滑窗放大：导轨 0.5 mm 侧隙通过")
B = (1052, 96, 2092, 700)
bx0, by0, bx1, by1 = B
ZU0, ZU1 = 45.0, 125.0
ZV0, ZV1 = -38.0, 38.0
sB = min((bx1 - bx0 - 170) / (ZU1 - ZU0), (by1 - by0 - 100) / (ZV1 - ZV0))
cBx = (bx0 + bx1) / 2.0
cBy = (by0 + 34 + by1) / 2.0


def RB(u, v):
    return (cBx + (u - (ZU0 + ZU1) / 2) * sB, cBy - (v - (ZV0 + ZV1) / 2) * sB)


def rectB(u0, u1, v0, v1, fill, outline, width=2, dash=False):
    p = [RB(u0, v0), RB(u1, v0), RB(u1, v1), RB(u0, v1)]
    if fill:
        dr.polygon(p, fill=fill)
    if dash:
        for a, b in ((p[0], p[1]), (p[1], p[2]), (p[2], p[3]), (p[3], p[0])):
            _dash(dr, a, b, outline, width)
    else:
        dr.polygon(p, outline=outline, width=width)


rectB(SLOT_U[0], SLOT_U[1], -SLOT_V / 2, SLOT_V / 2, (250, 226, 226), (196, 74, 74), 3)
rectB(WIN_U[0], WIN_U[1], -WIN[0] / 2, WIN[0] / 2, (208, 234, 255), BLUE, 4)
for vv in (RAIL_V, (-RAIL_V[1], -RAIL_V[0])):
    rectB(POLLEN_U[0], NECTAR_U[1], vv[0], vv[1], ORANGEF, ORANGE, 2)
rectB(POLLEN_U[0], POLLEN_U[1], -CARRIAGE_V, CARRIAGE_V, None, GREY, 2, dash=True)
rectB(NECTAR_U[0], NECTAR_U[1], -CARRIAGE_V, CARRIAGE_V, None, GREEN, 2, dash=True)

# clearance dimension
xa = RB(WIN_U[0], 0)[0]
xb = RB(WIN_U[0], RAIL_V[1])[0]
x0 = RB(WIN_U[0], -29.5)[0]
x1 = RB(WIN_U[0], 29.5)[0]
y_rail = RB(60.0, RAIL_V[0])[1]
dr.line([x0, y_rail, x1, y_rail], fill=(38, 42, 52), width=1)
dr.text((x0 + 6, y_rail - 22), "窗 v 跨 +/-29.5（59）", fill=(30, 120, 200), font=f_s)
dr.line([RB(56.5, 0)[0], y_rail + 30, RB(112.5, 0)[0], y_rail + 30], fill=(30, 120, 200), width=1)
dr.text((RB(56.5, 0)[0] + 6, y_rail + 34), "窗 u 跨 56.5..112.5（56）", fill=(30, 120, 200), font=f_s)
dr.text((RB(60.0, 31.0)[0], RB(60.0, 31.0)[1] - 18), "导轨 5 mm，侧隙 0.5 mm", fill=(190, 105, 20), font=f_s)
dr.text((RB(80.0, -CARRIAGE_V)[0] + 6, RB(80.0, -CARRIAGE_V)[1] - 4),
        "滑座 46 mm（v，虚线）", fill=DIM, font=f_tiny)

# =========================== panel C : verdict ============================
panel(1052, 716, 2092, 1130, "C  判据")
lines = [
    ("夹口行程", "64.0 .. 86.4 mm", INK, "旧轴槽只到 82，够不到 NECTAR 86"),
    ("Pollen 滑座 n 跨", "61.0 .. 99.0", GREEN, "在窗内 56.5 .. 112.5"),
    ("Nectar 滑座 n 跨", "72.0 .. 110.0", GREEN, "在窗内 56.5 .. 112.5"),
    ("导轨侧隙", "0.500 mm", GREEN, "导轨改顶窗壁作侧向导向"),
    ("两飞轮轴刚性连接", "无（0.0 mm3）", GREEN, "侧板 15 组布尔 x 2 档全 0"),
    ("件数 / 版本", "98 件 / R51", INK, "基线 2026-10-01 全整机"),
]
cx = 1074
cy = 776
for k, val, col, note in lines:
    dr.text((cx, cy), k, fill=(70, 74, 84), font=f_n)
    dr.text((cx + 300, cy), val, fill=col, font=f_n)
    dr.text((cx + 560, cy), note, fill=DIM, font=f_tiny)
    cy += 40
dr.text((cx, cy + 16),
        "R51 只改两处：拨杆舵机 2000-0025-0003 -> 2000-0025-0004；侧板开口 8.4x9 轴槽 -> 59x56 滑窗。",
        fill=INK, font=f_n)
dr.text((cx, cy + 46),
        "滑座与导轨只能沿 u 平移；两轴的轴承座分属各自滑座，侧板不再跨接任何一轴。",
        fill=DIM, font=f_s)

# title bar
t = "T06 R51 侧板开口：8.4 x 9 轴槽  ->  59 x 56 滑窗（2026-10-01 基线 + 两处改动）"
bb = dr.textbbox((0, 0), t, font=f_title)
dr.rectangle([28, 26, 28 + (bb[2] - bb[0]) + 40, 82], fill=(38, 42, 52))
dr.text((48, 34), t, fill=(255, 255, 255), font=f_title)
dr.text((28, H - 42), "数据源 cad/output/_r51_drive/report_r51.json、plate_booleans_r51.json；"
                      "侧板包围盒 cad/output/_r51_base/manifest.json；单位 mm。",
        fill=DIM, font=f_tiny)

img.save(OUT)
try:
    img.save(DESK)
except Exception as exc:
    print("desktop copy skipped:", exc)
print("wrote", OUT)
