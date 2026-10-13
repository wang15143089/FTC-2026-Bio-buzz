# -*- coding: utf-8 -*-
"""T06 R49 -- gate stroke 92 -> 72 mm, driven by a real servo crank.

User instructions (2026-10-12):
  * "the blade does not need that much travel; its lowest edge only has to sit
     below the POLLEN ball centre"  ->  blade centre 47.5 -> 67.5 (bottom 20 -> 40)
  * "give the gate a structure that really starts it as intended, and pick a
     suitable servo"
  * "send me a picture after every change"

R47 is re-used read-only (never edited): this file only replaces the gate parts
and adds the drive train, so the delivered R47 output stays untouched.

Slider-crank kinematics (all in the XZ plane)
---------------------------------------------
  crank centre    C = (190.0, 240.0)   +10 mm in X of the blade: the rod then
                                       clears the servo case instead of crossing it
  crank radius    r = 38.35
  connecting rod  L = 90.0             rod/vertical <= 25 deg, good transmission
  crank sweep     20 deg .. 160 deg    = 140 deg of servo travel

  phi = 0 puts the crank pin straight below C.  The yoke pin height is

      z_s(phi) = Cz - r*cos(phi) - sqrt(L^2 - (dx + r*sin(phi))^2)

  and the blade centre is z_s - 22 - 55/2 = z_s - 49.5, so

      closed (blocking)  phi =  20 deg -> yoke pin 117.0, blade centre  67.5
      open   (feeding)   phi = 160 deg -> yoke pin 189.1, blade centre 139.6
      stroke 72.08 mm  (target 72)

  Both sweep ends sit 20 deg away from the toggle positions (0 / 180 deg), so
  the servo never has to push through a dead point.

Y stacking -- every linkage part stays inside |y| <= 27; the frame rails move
out to y = 34..72 because a full-width top beam would sit in the rod path:

  servo case   -22.05 .. 17.95     spline 17.95 .. 22.05 (O6.1)
  crank plate   17.95 .. 22.95     hub boss r = 15, 17.95 .. 26.0
  rod           22.95 .. 26.95
  rails         34 .. 72 (both sides)

Units: millimetres.
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path

import cadquery as cq

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import paddle_launcher_feeder_a_prime_shared as SH          # noqa: E402
import paddle_launcher_feeder_a_prime_shared_staging as ST  # noqa: E402
import t06_vendor_cad as TC                                 # noqa: E402

F, pl = SH.F, SH.pl

# ---------------------------------------------------------------- geometry --
GATE_X, GATE_T, GATE_W, GATE_H = 180.0, 5.0, 108.0, 55.0
GATE_Z_DN, GATE_Z_UP = 67.5, 139.5                  # blade centre, stroke 72
CHISEL_H, CHISEL_FLAT = 12.0, 1.5                   # anti-jam wedge on the tip

PIN_DZ = 22.0                                       # yoke pin above blade top
PIN_Z_DN = GATE_Z_DN + GATE_H / 2.0 + PIN_DZ        # 117.0

CRANK_CX, CRANK_CZ = 190.0, 240.0
CRANK_R, ROD_L = 38.35, 90.0
DX = CRANK_CX - GATE_X                              # 10.0
PHI_DN, PHI_UP = 20.0, 160.0

YOKE_X0, YOKE_X1 = GATE_X - 6.0, GATE_X + 6.0
YOKE_HW, YOKE_DZ0, YOKE_DZ1 = 10.0, -22.0, 4.0      # yoke 20 wide, 26 tall
CRANK_W, ARM_W = 5.0, 14.0
CRANK_Y0, CRANK_Y1 = 17.95, 22.95                   # arm plate
HUB_R, HUB_Y1 = 15.0, 26.0                          # hub boss over the spline
ROD_W, ROD_Y0, ROD_Y1 = 9.0, 22.95, 26.95
PIN_R = 2.0
PIN_CRANK_Y0, PIN_CRANK_Y1 = 17.0, 28.0
PIN_YOKE_Y0, PIN_YOKE_Y1 = -12.0, 27.0
SPLINE_BORE_R = 3.2

SERVO_SKU = "2000-0025-0003"                        # goBILDA 25-3 (user pick)
SERVO_TIP_Y = 22.05

RAIL_X0, RAIL_X1 = 176.0, 204.0                     # flush with the bracket legs
RAIL_Z0, RAIL_Z1 = 190.0, 198.0
RAIL_Y_IN, RAIL_Y_OUT = 34.0, 62.0                  # flush with the post outer face

SHELF_X0, SHELF_X1 = 166.0, 232.0
SHELF_Y, SHELF_Z0, SHELF_Z1 = 34.0, 225.0, 229.5
LEG_X0, LEG_X1 = 176.0, 204.0
LEG_Y0, LEG_Y1 = 34.0, 42.0
EARS = ((166.0, 174.0), (223.0, 231.0))
EAR_Y0, EAR_Y1 = 24.0, 32.0
EAR_Z1 = 258.0
STRAP_X0, STRAP_X1 = 166.0, 232.0
STRAP_Y, STRAP_Z0, STRAP_Z1 = 32.0, 250.15, 252.65   # zip-tie over the case

DESKTOP = Path(os.path.expanduser("~")) / "OneDrive" / "Desktop"
OUT = HERE / "output" / "_r49_gate"
OUT.mkdir(parents=True, exist_ok=True)


def _box(dx, dy, dz, c):
    return cq.Solid.makeBox(dx, dy, dz,
                            cq.Vector(-dx / 2.0, -dy / 2.0, -dz / 2.0)).translate(
        cq.Vector(*c))


def _cyl_y(r, y0, y1, x, z):
    return cq.Solid.makeCylinder(r, y1 - y0, cq.Vector(x, y0, z),
                                 cq.Vector(0.0, 1.0, 0.0))


def _bar(p0, p1, w, y0, y1, grow=0.0):
    """Flat bar in the XZ plane, centre line p0 -> p1, w wide, y0..y1 thick."""
    dx, dz = p1[0] - p0[0], p1[1] - p0[1]
    length = math.hypot(dx, dz) + grow
    ang = math.degrees(math.atan2(dz, dx))
    bar = cq.Solid.makeBox(length, y1 - y0, w,
                           cq.Vector(-0.5 * length, -0.5 * (y1 - y0), -0.5 * w))
    bar = bar.rotate(cq.Vector(0.0, 0.0, 0.0), cq.Vector(0.0, 1.0, 0.0), -ang)
    return bar.translate(cq.Vector(0.5 * (p0[0] + p1[0]), 0.5 * (y0 + y1),
                                   0.5 * (p0[1] + p1[1])))


def tray_top_z(x):
    return F.PIVOT_Z + (x - F.PIVOT_X) * math.tan(math.radians(F.TILT_DEG))


def yoke_pin_z(phi_deg):
    phi = math.radians(phi_deg)
    return (CRANK_CZ - CRANK_R * math.cos(phi)
            - math.sqrt(ROD_L ** 2 - (DX + CRANK_R * math.sin(phi)) ** 2))


def crank_pin(phi_deg):
    phi = math.radians(phi_deg)
    return (CRANK_CX + CRANK_R * math.sin(phi), CRANK_CZ - CRANK_R * math.cos(phi))


def blade_centre(phi_deg):
    return yoke_pin_z(phi_deg) - PIN_DZ - GATE_H / 2.0


# ------------------------------------------------------------------- parts --
def gate_blade(z_centre=None):
    """5 x 108 x 55 blade, both bottom edges chamfered to a 1.5 mm flat."""
    z_centre = GATE_Z_DN if z_centre is None else z_centre
    zb, zt = -GATE_H / 2.0, GATE_H / 2.0
    hx = GATE_T / 2.0
    prof = [(hx, zt), (hx, zb + CHISEL_H), (CHISEL_FLAT / 2.0, zb),
            (-CHISEL_FLAT / 2.0, zb), (-hx, zb + CHISEL_H), (-hx, zt)]
    blade = cq.Workplane("XZ").polyline(prof).close().extrude(
        GATE_W / 2.0, both=True).val()
    return blade.translate(cq.Vector(GATE_X, 0.0, z_centre))


def gate_yoke(pin_z=None):
    """Yoke on the blade top, O4 bore for the yoke/rod pin."""
    pin_z = PIN_Z_DN if pin_z is None else pin_z
    zc = pin_z + 0.5 * (YOKE_DZ0 + YOKE_DZ1)
    y = _box(YOKE_X1 - YOKE_X0, 2.0 * YOKE_HW, YOKE_DZ1 - YOKE_DZ0,
             (0.5 * (YOKE_X0 + YOKE_X1), 0.0, zc))
    return y.cut(_cyl_y(PIN_R + 0.1, -60.0, 60.0, GATE_X, pin_z)).clean()


def gate_frame():
    """Posts + tray lugs + the two outboard side rails (no full-width beam)."""
    parts = []
    for sy in (-1.0, 1.0):
        parts.append(_box(11.0, 8.0, 184.0, (GATE_X + 0.5, sy * 58.0, 106.0)))
        parts.append(_box(11.0, 8.0, 6.0,
                          (GATE_X + 0.5, sy * 50.0, tray_top_z(GATE_X + 0.5))))
        parts.append(_box(RAIL_X1 - RAIL_X0, RAIL_Y_OUT - RAIL_Y_IN,
                          RAIL_Z1 - RAIL_Z0,
                          (0.5 * (RAIL_X0 + RAIL_X1),
                           sy * 0.5 * (RAIL_Y_IN + RAIL_Y_OUT),
                           0.5 * (RAIL_Z0 + RAIL_Z1))))
    fr = parts[0]
    for p in parts[1:]:
        fr = fr.fuse(p)
    return fr.clean()


def gate_bracket():
    """Printed shelf under the servo, two legs on the rails, zip-tie ears."""
    parts = [_box(SHELF_X1 - SHELF_X0, 2.0 * SHELF_Y, SHELF_Z1 - SHELF_Z0,
                  (0.5 * (SHELF_X0 + SHELF_X1), 0.0,
                   0.5 * (SHELF_Z0 + SHELF_Z1)))]
    for sy in (-1.0, 1.0):
        parts.append(_box(LEG_X1 - LEG_X0, LEG_Y1 - LEG_Y0, SHELF_Z0 - RAIL_Z1,
                          (0.5 * (LEG_X0 + LEG_X1), sy * 0.5 * (LEG_Y0 + LEG_Y1),
                           0.5 * (RAIL_Z1 + SHELF_Z0))))
        for x0, x1 in EARS:
            parts.append(_box(x1 - x0, EAR_Y1 - EAR_Y0, EAR_Z1 - SHELF_Z1,
                              (0.5 * (x0 + x1), sy * 0.5 * (EAR_Y0 + EAR_Y1),
                               0.5 * (SHELF_Z1 + EAR_Z1))))
    parts.append(_box(STRAP_X1 - STRAP_X0, 2.0 * STRAP_Y, STRAP_Z1 - STRAP_Z0,
                      (0.5 * (STRAP_X0 + STRAP_X1), 0.0,
                       0.5 * (STRAP_Z0 + STRAP_Z1))))
    brk = parts[0]
    for p in parts[1:]:
        brk = brk.fuse(p)
    return brk.clean()


def servo():
    """goBILDA 25 series, spline tip on +Y at SERVO_TIP_Y."""
    return TC.servo_with_output_face(SERVO_SKU, (CRANK_CX, CRANK_CZ),
                                     SERVO_TIP_Y, 1)


def crank(phi_deg=None):
    """Hub boss over the spline + arm out to the O4 crank pin."""
    phi_deg = PHI_DN if phi_deg is None else phi_deg
    px, pz = crank_pin(phi_deg)
    ux, uz = (px - CRANK_CX) / CRANK_R, (pz - CRANK_CZ) / CRANK_R
    hub = _cyl_y(HUB_R, CRANK_Y0, HUB_Y1, CRANK_CX, CRANK_CZ)
    arm = _bar((CRANK_CX, CRANK_CZ), (px + 6.0 * ux, pz + 6.0 * uz), ARM_W,
               CRANK_Y0, CRANK_Y1)
    c = hub.fuse(arm)
    c = c.cut(_cyl_y(SPLINE_BORE_R, -20.0, 60.0, CRANK_CX, CRANK_CZ))
    c = c.cut(_cyl_y(PIN_R + 0.05, -20.0, 60.0, px, pz))
    return c.clean()


def connecting_rod(phi_deg=None):
    """Flat rod, O4 eyes on the crank pin and on the yoke pin."""
    phi_deg = PHI_DN if phi_deg is None else phi_deg
    zs = yoke_pin_z(phi_deg)
    px, pz = crank_pin(phi_deg)
    bar = _bar((GATE_X, zs), (px, pz), ROD_W, ROD_Y0, ROD_Y1)
    bar = bar.cut(_cyl_y(PIN_R + 0.05, -60.0, 60.0, GATE_X, zs))
    bar = bar.cut(_cyl_y(PIN_R + 0.05, -60.0, 60.0, px, pz))
    return bar.clean()


def dowels(phi_deg=None):
    phi_deg = PHI_DN if phi_deg is None else phi_deg
    zs = yoke_pin_z(phi_deg)
    px, pz = crank_pin(phi_deg)
    return {
        "gate_pin_crank": _cyl_y(PIN_R, PIN_CRANK_Y0, PIN_CRANK_Y1, px, pz),
        "gate_pin_yoke": _cyl_y(PIN_R, PIN_YOKE_Y0, PIN_YOKE_Y1, GATE_X, zs),
    }


def balls(n=4):
    r = F.BALL_R
    xc = GATE_X + GATE_T / 2.0 + r
    return [cq.Solid.makeSphere(r, cq.Vector(xc + i * 2.0 * r, 0.0,
                                             tray_top_z(xc + i * 2.0 * r) + r))
            for i in range(n)]


# ---------------------------------------------------------------- assembly --
def drive_parts(phi_deg, n_balls=4):
    parts = {
        "gate_frame": gate_frame(),
        "gate_blade": gate_blade(blade_centre(phi_deg)),
        "gate_yoke": gate_yoke(yoke_pin_z(phi_deg)),
        "gate_bracket": gate_bracket(),
        "gate_servo": servo(),
        "gate_crank": crank(phi_deg),
        "gate_rod": connecting_rod(phi_deg),
    }
    parts.update(dowels(phi_deg))
    for i, b in enumerate(balls(n_balls)):
        parts["ball_%d" % (i + 1)] = b
    return parts


def kept_parts(name):
    if name not in ctx_cache:
        t0 = time.time()
        kept, *_ = ST.build_variant_stage(name)
        ctx_cache[name] = kept
        print("[r49 %s] parent build %.1f s, %d parts" % (name, time.time() - t0,
                                                          len(kept)), flush=True)
    return ctx_cache[name]


ctx_cache = {}


def dump(parts):
    rows = []
    for n, s in parts.items():
        bb = s.BoundingBox()
        c = s.Center()
        rows.append({
            "part": n,
            "n_solids": len(s.Solids()),
            "volume_mm3": round(s.Volume(), 2),
            "bbox_mm": [round(v, 3) for v in (bb.xmin, bb.ymin, bb.zmin,
                                              bb.xmax, bb.ymax, bb.zmax)],
            "centre_mm": [round(v, 3) for v in (c.x, c.y, c.z)],
        })
    return rows


def run(name="pollen", export=True):
    t0 = time.time()
    parts = dict(kept_parts(name))
    parts.pop("gate_blade", None)
    parts.pop("gate_yoke", None)
    parts.pop("gate_frame", None)
    parts.update(drive_parts(PHI_DN))
    declared = dump(parts)
    stem = "T06_gate_drive_R49_%s" % name
    assy = cq.Assembly(name=stem)
    for n, s in parts.items():
        assy.add(s, name=n, color=cq.Color(0.7, 0.72, 0.76, 1.0))
    dst = DESKTOP / (stem + ".step")
    if export:
        assy.export(str(dst), exportType="STEP")
        assy.export(str(OUT / (stem + ".step")), exportType="STEP")
        print("[r49 %s] export -> %s (%.1f s)" % (name, dst, time.time() - t0),
              flush=True)
    data = {
        "variant": name,
        "units": "mm",
        "caliber": "T06 R49 gate drive",
        "gate_x_mm": GATE_X,
        "gate_blade_size_mm": [GATE_T, GATE_W, GATE_H],
        "gate_z_closed_mm": round(blade_centre(PHI_DN), 3),
        "gate_z_open_mm": round(blade_centre(PHI_UP), 3),
        "gate_stroke_mm": round(blade_centre(PHI_UP) - blade_centre(PHI_DN), 3),
        "crank_centre_mm": [CRANK_CX, 0.0, CRANK_CZ],
        "crank_radius_mm": CRANK_R,
        "rod_length_mm": ROD_L,
        "sweep_deg": [PHI_DN, PHI_UP],
        "servo_sku": SERVO_SKU,
        "delivered_step": str(dst) if export else None,
        "parts": declared,
    }
    (OUT / ("parts_%s.json" % name)).write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    for r in declared:
        print("  %-32s solids=%d vol=%10.1f z %.1f..%.1f"
              % (r["part"], r["n_solids"], r["volume_mm3"], r["bbox_mm"][2],
                 r["bbox_mm"][5]), flush=True)
    return data


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    names = [a for a in argv if not a.startswith("-")] or ["pollen"]
    for n in names:
        run(n, export="--no-export" not in argv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
