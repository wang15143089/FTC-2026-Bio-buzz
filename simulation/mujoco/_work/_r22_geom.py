# -*- coding: utf-8 -*-
"""Analytic check of the a' hand-off geometry for the NECTAR ball."""
import math

PAD_CX, PAD_CZ = 29.49, 111.46
PIV_X, PIV_Z = -2.30, 17.50
TILT = math.radians(5.0)
BR = 45.974
A_EXIT = 142.0


def tray_top_z(x):
    return PIV_Z + (x - PIV_X) * math.tan(TILT)


def solve(r_carry, r_hub, label):
    R_IN = r_carry + BR
    # intersection of the tray top line with the shell inner circle
    # (x-cx)^2 + (z-cz)^2 = R_IN^2 ; z = tray_top_z(x)
    t = math.tan(TILT)
    # z - cz = PIV_Z + (x - PIV_X)*t - cz  =  t*x + (PIV_Z - t*PIV_X - cz)
    b = PIV_Z - t * PIV_X - PAD_CZ
    # (x-cx)^2 + (t x + b)^2 = R_IN^2
    A = 1 + t * t
    B = -2 * PAD_CX + 2 * t * b
    C = PAD_CX ** 2 + b * b - R_IN ** 2
    disc = B * B - 4 * A * C
    x1 = (-B - math.sqrt(disc)) / (2 * A)
    x2 = (-B + math.sqrt(disc)) / (2 * A)
    cut = x2
    zt = tray_top_z(cut)
    ang = math.degrees(math.atan2(zt - PAD_CZ, cut - PAD_CX)) % 360.0
    # ball resting on the tray at the cut -> centre radius / hub clearance
    cz = zt + BR
    r_c = math.hypot(cut - PAD_CX, cz - PAD_CZ)
    hub_clr = r_c - BR - r_hub
    # nest rest position
    nest_z = PAD_CZ - r_carry
    print("--- %s ---" % label)
    print("  R_CARRY=%.3f  R_IN=%.3f  hub r=%.1f" % (r_carry, R_IN, r_hub))
    print("  tray/shell intersections: x=%.2f (left) and x=%.2f (right)" % (x1, x2))
    print("  -> cut_x=%.2f  a_lip=%.2f deg" % (cut, ang))
    print("  ball on tray at cut: centre=(%.2f, %.2f) r=%.2f ang=%.2f" % (cut, cz, r_c, ang))
    print("  hub clearance there: %.2f mm" % hub_clr)
    print("  nest rest centre: (%.2f, %.2f)  bottom z=%.2f" % (PAD_CX, nest_z, nest_z - BR))
    print("  hub clearance at nest: %.2f mm" % (r_carry - BR - r_hub))
    # where ball-on-tray centre radius equals R_CARRY (pure tangency)
    # (x-cx)^2 + (t x + b + BR)^2 = r_carry^2
    b2 = b + BR
    A2 = 1 + t * t
    B2 = -2 * PAD_CX + 2 * t * b2
    C2 = PAD_CX ** 2 + b2 * b2 - r_carry ** 2
    d2 = B2 * B2 - 4 * A2 * C2
    if d2 < 0:
        print("  carry-circle tangency: NONE (ball centre never reaches r=R_CARRY on the tray)")
    else:
        xa = (-B2 + math.sqrt(d2)) / (2 * A2)
        print("  ball centre reaches r=R_CARRY on the tray at x=%.2f" % xa)
    print()
    return cut, ang


solve(64.000, 18.0, "hub r=18 (print hub unchanged)")
solve(58.400, 12.0, "hub r=12 (shrunk hub)")
solve(58.400, 12.0, "h24 check")
print("R20-B used cut=84 lip=300 R_CARRY=64 ; R21-F used cut=56 lip=292 R_CARRY=58.4")
