import math
CROSS_PIN_U, MAIN_L, CRANK_R, DRAG_L, SERVO_U, WHEEL_R = 18.0, 110.0, 12.0, 65.0, -120.0, 48.0
d_max = CRANK_R + DRAG_L            # 曲柄与拉杆共线 = 死点
cu_min = SERVO_U + d_max
hs_max = math.sqrt(MAIN_L**2 - (CROSS_PIN_U - cu_min)**2)
nip_max = 2.0*(hs_max - WHEEL_R)
print("十字滑块最外行程 u = %.3f (死点)" % cu_min)
print("机构可达最大半间距 = %.3f  ->  最大夹口 = %.2f mm" % (hs_max, nip_max))
def ratio(hs):
    u = CROSS_PIN_U - math.sqrt(MAIN_L**2 - hs*hs) - SERVO_U
    c = (u*u + CRANK_R**2 - DRAG_L**2)/(2*u*CRANK_R)
    th = math.acos(max(-1.0, min(1.0, c)))
    du = abs(-u*CRANK_R*math.sin(th)/(u - CRANK_R*math.cos(th)))
    return math.degrees(th), du
print("%6s %8s %10s %14s" % ("nip","half_sp","crank_deg","dT/dF mm/rad"))
for nip in (64.0, 82.0, 85.0, 86.0, 87.0, 87.07):
    th, du = ratio(nip/2.0 + WHEEL_R)
    print("%6.2f %8.2f %10.2f %14.3f" % (nip, nip/2.0+WHEEL_R, th, du))
