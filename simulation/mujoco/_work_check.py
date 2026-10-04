import math, sys
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass

ANGLE=52.0
def direction(a):
    r=math.radians(a); return math.cos(r), math.sin(r)
def normal(a):
    r=math.radians(a); return -math.sin(r), math.cos(r)
T52,N52=direction(52.0),normal(52.0)
R=BALL_R=35.56
GUIDE=[((-150.,16.),70.,0.),(None,55.,26.),(None,70.,52.)]
segs=[];start=GUIDE[0][0]
for _,L,a in GUIDE:
    tx,tz=direction(a); end=(start[0]+L*tx,start[1]+L*tz); segs.append((start,end,a)); start=end
GE=segs[-1][1]
THROAT=(GE[0]+55*N52[0],GE[1]+55*N52[1])
NIP=(THROAT[0]+135*T52[0],THROAT[1]+135*T52[1])
FLOOR_TOP=17.5; BALL_Z=FLOOR_TOP+R
C_OLD=(-47.,73.)
R_CARRY=58.4; R_SHELL=R_CARRY+R; CZ=FLOOR_TOP+R_SHELL
CX=NIP[0]+(-R_CARRY-(CZ-NIP[1])*N52[1])/N52[0]
C=(CX,CZ)
print("THROAT",tuple(round(v,2) for v in THROAT),"NIP",tuple(round(v,2) for v in NIP))
print("C_NEW",(round(CX,2),round(CZ,2)),"R_SHELL",round(R_SHELL,2))
TAN=(CX+R_CARRY*N52[0],CZ+R_CARRY*N52[1])
print("tangent pt",tuple(round(v,2) for v in TAN),"angle",round(math.degrees(math.atan2(TAN[1]-CZ,TAN[0]-CX)),2))
print("|C-nip|",round(math.dist(C,NIP),2),"|C_OLD-nip|",round(math.dist(C_OLD,NIP),2))
print("throat centre angle about C:",round(math.degrees(math.atan2(THROAT[1]-CZ,THROAT[0]-CX)),2),
      " dist",round(math.dist(C,THROAT),2))

def d(x):  # distance from C to ball centre while ball sits on tray floor
    return math.hypot(x-CX, BALL_Z-CZ)
# ball disc (radius 35.56 about (x,BALL_Z)) vs shell circle (radius R_SHELL about C)
lo,hi=R_SHELL-R, R_SHELL+R
print("ball disc hits shell circle when dist in [%.2f, %.2f]"%(lo,hi))
xs=[ -150,-130,-110,-90,-85.7,-80,-70,-60,-46.1,-20,0,20,29.49]
for x in xs:
    dd=d(x)
    hit = lo<=dd<=hi
    # angle of contact point (radially outward from C toward ball)
    ang=math.degrees(math.atan2(BALL_Z-CZ, x-CX))
    print(f"  ball centre x={x:8.2f}  dist_from_C={dd:7.2f}  hits_shell={hit}  contact_angle={ang%360:7.2f}")
print()
print("shell inner surface: x-range [%.2f, %.2f], lowest z=%.2f"%(CX-R_SHELL,CX+R_SHELL,CZ-R_SHELL))
print("hub needs ball centre >= %.2f from axis -> on tray floor x<=%.2f or x>=%.2f"%(18+R, CX-math.sqrt((18+R)**2-(BALL_Z-CZ)**2), CX+math.sqrt((18+R)**2-(BALL_Z-CZ)**2)))
print()
# blade reach
for rt in (58,60):
    # ball on floor: nearest surface to axis = d-35.56 ; blade tip reaches rt
    xmin=CX-math.sqrt((rt+R)**2-(BALL_Z-CZ)**2)
    print(f"  blade tip r={rt}: can touch a ball sitting on the tray floor only for x>={xmin:.1f}")
print()
# exit direction
th=142.0
r=math.radians(th)
tang_dec=(math.sin(r),-math.cos(r))   # travel dir if theta decreasing
tang_inc=(-math.sin(r),math.cos(r))
print("at exit theta=142deg: T52=",tuple(round(v,3) for v in T52))
print("  travel dir (theta decreasing)=",tuple(round(v,3) for v in tang_dec))
print("  travel dir (theta increasing)=",tuple(round(v,3) for v in tang_inc))
print("  -> need DECREASING theta (CAD view X-right/Z-up = clockwise; w_y>0)")
print()
# tray angular extent seen from C
for x in (-150.,-80.):
    print(f"  tray ball centre x={x}: angle about C = {math.degrees(math.atan2(BALL_Z-CZ,x-CX))%360:.1f} deg")
