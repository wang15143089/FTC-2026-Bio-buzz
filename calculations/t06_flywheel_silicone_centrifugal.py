# -*- coding: utf-8 -*-
"""T06: 30A silicone Gecko flywheel (goBILDA 3613-0014-0096) centrifugal growth.

官方图纸（用户提供）确定的真实结构：
  * OD 96 mm  -> b = 48 mm
  * 金属轮毂 Ø32 灌/粘在硅胶体内 -> 硅胶内边界 a = 16 mm（刚性内约束）
  * 总宽 24 mm；轮毂处轴向 8 mm，外缘处轴向 12 mm（图纸 8/12/24 标注）
  * 6 x Ø4 螺栓孔 + 12 条波形减重槽（正视图），实体体积 95767.311 mm3
    = 同尺寸实心环 π(48²-16²)·24 = 154409 mm3 的 62 %。

三种模型（同一转速下给出上下界）：
  M1 自由薄环  delta = rho*w^2*b^3/E                —— 绝对上界
  M2 厚环自由   内外表面均自由（Timoshenko 平面应力）
  M3 厚环固支   内表面被 Ø32 轮毂锁住 u(a)=0      —— 结构上的下界
真实零件介于 M2/M3 与 M1 之间：减重槽降低等效刚度，轮毂点胶只是部分约束。
"""
import math, sys
sys.stdout.reconfigure(encoding="utf-8")

RHO = 1150.0                      # kg/m^3  ASSUMED  硅胶 1.10-1.30 g/cm3
E_LIST = (0.7e6, 1.0e6, 1.5e6)    # Pa      ASSUMED  Shore 30A ~ 0.7-1.5 MPa
NU = 0.48                         # ASSUMED  硅胶近似不可压
A, B = 0.016, 0.048               # m  硅胶内/外半径
RPM_LIST = (1150.0, 1620.0, 2430.0)
M_WHEEL = 0.105                   # kg  goBILDA 供应商值
J_MEAS = 1.2844e-4                # kg m^2  由官方 STEP 网格积分实测（本仓库）


def w_of(n):
    return n * 2.0 * math.pi / 60.0


def thin_ring(n, E):
    return RHO * w_of(n) ** 2 * B ** 3 / E


def thick_annulus(n, E, rigid_inner):
    """平面应力厚环。返回 (u(b), sigma_theta(b))。"""
    wr2 = RHO * w_of(n) ** 2
    if rigid_inner:
        # A - B/b^2 = (3+nu)*rho*w^2*b^2/8
        # (1-nu)A + (1+nu)B/a^2 = (1+6nu+nu^2)*rho*w^2*a^2/8
        c1 = (3.0 + NU) * wr2 * B * B / 8.0
        c2 = (1.0 + 6.0 * NU + NU * NU) * wr2 * A * A / 8.0
        # A = c1 + B/b^2 ;  (1-nu)c1 + (1-nu)B/b^2 + (1+nu)B/a^2 = c2
        k = (1.0 - NU) / (B * B) + (1.0 + NU) / (A * A)
        Bc = (c2 - (1.0 - NU) * c1) / k
        Ac = c1 + Bc / (B * B)
    else:
        # 内外均自由: sigma_r(a)=sigma_r(b)=0
        c3 = (3.0 + NU) * wr2 / 8.0
        # A - B/a^2 = c3 a^2 ; A - B/b^2 = c3 b^2
        Bc = c3 * (A * A - B * B) / (1.0 / (B * B) - 1.0 / (A * A))
        Ac = c3 * B * B + Bc / (B * B)
    sr = lambda r: (Ac - Bc / (r * r)) - (3.0 + NU) * wr2 * r * r / 8.0
    st = lambda r: (Ac + Bc / (r * r)) - (1.0 + 3.0 * NU) * wr2 * r * r / 8.0
    u = lambda r: r * (st(r) - NU * sr(r)) / E
    return u(B), st(B)


def report(fh):
    p = lambda *a: (print(*a), print(*a, file=fh))
    p("T06 飞轮硅胶离心膨胀  RHO=%.0f kg/m3  nu=%.2f  a=%.0f mm  b=%.0f mm"
      % (RHO, NU, A * 1000, B * 1000))
    p("实体体积比：95767.3 / 154409 mm3 = 62 %（波形减重槽）")
    p("")
    hdr = "%8s %9s %32s %28s" % ("rpm", "rim m/s", "M1 自由薄环 dr (mm)", "M2 厚环自由 / M3 厚环固支 dr (mm)")
    p(hdr)
    for n in RPM_LIST:
        cells1 = " ".join("%.2f" % (thin_ring(n, E) * 1000) for E in E_LIST)
        c2 = " ".join("%.2f" % (thick_annulus(n, E, False)[0] * 1000) for E in E_LIST)
        c3 = " ".join("%.2f" % (thick_annulus(n, E, True)[0] * 1000) for E in E_LIST)
        p("%8.0f %9.2f  E0.7/1.0/1.5 -> %-22s  M2 %-22s M3 %s"
          % (n, w_of(n) * B, cells1, c2, c3))
    p("")
    n = 1620.0
    for E in E_LIST:
        u2, st2 = thick_annulus(n, E, False)
        u3, st3 = thick_annulus(n, E, True)
        p("  E=%.1f MPa @1620 rpm:  周向应力 M3=%.3f MPa   M2=%.3f MPa" % (E / 1e6, st3 / 1e6, st2 / 1e6))
    p("")
    p("--- 存能（用实测 J = %.4e kg m^2，不是实心盘近似）---" % J_MEAS)
    for n in RPM_LIST:
        ke = 0.5 * J_MEAS * w_of(n) ** 2
        p("  %6.0f rpm  单轮 %.2f J   两轮 %.2f J" % (n, ke, 2 * ke))
    p("")
    p("--- 球的需求能量（0.5 m v^2）---")
    for name, m, v in (("NECTAR D91.948", 0.130, 4.80), ("NECTAR D91.948", 0.130, 6.00),
                       ("POLLEN D71.120", 0.060, 6.20)):
        ke = 0.5 * m * v * v
        p("  %-16s v=%.2f m/s  KE=%.2f J  = 两轮(1620rpm, %.2f J)的 %.0f %%"
          % (name, v, ke, 2 * 0.5 * J_MEAS * w_of(1620) ** 2,
             100 * ke / (2 * 0.5 * J_MEAS * w_of(1620) ** 2)))


if __name__ == "__main__":
    from pathlib import Path
    fh = open(Path(__file__).with_name("t06_flywheel_silicone_centrifugal.txt"), "w", encoding="utf-8")
    try:
        report(fh)
    finally:
        fh.close()
