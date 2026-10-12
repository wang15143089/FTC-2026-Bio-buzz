import sys, os, math, json
CROSS_PIN_U, MAIN_L, CRANK_R, DRAG_L, SERVO_U = 18.0, 110.0, 12.0, 65.0, -120.0
WHEEL_R, WHEEL_OD = 48.0, 96.0
BALL_D = {"NECTAR": 91.948, "POLLEN": 71.120}
def solve(half_spacing):
    crosshead_u = CROSS_PIN_U - math.sqrt(MAIN_L**2 - half_spacing**2)
    d = crosshead_u - SERVO_U
    c = (d*d + CRANK_R*CRANK_R - DRAG_L*DRAG_L) / (2*d*CRANK_R)
    return crosshead_u, math.degrees(math.acos(max(-1.0, min(1.0, c))))
rows = []
for nm in ("NECTAR", "POLLEN"):
    for nip in (82.0, 84.0, 85.0, 86.0, 87.0, 88.0, 90.0):
        hs = nip/2.0 + WHEEL_R
        cu, th = solve(hs)
        rows.append(dict(ball=nm, nip=nip, half_spacing=hs, crosshead_u=round(cu,3),
                         crank_deg=round(th,2),
                         interference_mm=round((BALL_D[nm]-nip)/2.0,3)))
base_net = solve(82.0/2.0+WHEEL_R)[1]
base_pol = solve(64.0/2.0+WHEEL_R)[1]
for r in rows:
    b = base_net if r["ball"] == "NECTAR" else base_pol
    r["servo_travel_from_current_deg"] = round(r["crank_deg"] - b, 2)
print("%-7s %5s %8s %11s %9s %8s %10s" % ("ball","nip","half_sp","crosshead_u","crank","interf","dTravel"))
for r in rows:
    print("%-7s %5.0f %8.1f %11.2f %9.2f %8.2f %10.2f" % (r["ball"], r["nip"], r["half_spacing"],
          r["crosshead_u"], r["crank_deg"], r["interference_mm"], r["servo_travel_from_current_deg"]))
pathlib = __import__("pathlib")
p = pathlib.Path("simulation/mujoco/out/_r38_gap_recalc.json")
p.write_text(json.dumps(dict(crosshead_pin_u=CROSS_PIN_U, main_link_mm=MAIN_L, crank_r=CRANK_R,
    drag_len=DRAG_L, servo_u=SERVO_U, rows=rows), ensure_ascii=False, indent=1), encoding="utf-8")
print("saved", p)
print("舵机总行程(82档->64档) = %.2f deg" % (base_pol - base_net))
