"""Timing probe #2: where do the post-build minutes go for the SHARED variant?"""
import sys, time
sys.path.insert(0, "cad")
import cadquery as cq
import paddle_launcher_feeder_redesign as F
import paddle_launcher_feeder_a_prime_shared as S

name = sys.argv[1] if len(sys.argv) > 1 else "nectar"
pl = S.pl


def tic(label):
    t = time.time()
    print("START %s" % label, flush=True)
    return t


def toc(label, t):
    print("  END %s -> %.1f s" % (label, time.time() - t), flush=True)


t = tic("build_variant(%s)" % name)
kept, dropped, relieved, consumed, kinematics, half = S.build_variant(name)
toc("build_variant", t)

v = S.VARIANTS[name]
ball_r = v["ball_r"]
r_carry = S.R_IN - ball_r
shell = kept["feeder_shell_tray"]

t = tic("nest ball volume"); print("   shell vol %.0f" % shell.Volume(), flush=True)
nest = cq.Vector(F.PADDLE_CX, 0.0, F.PADDLE_CZ - r_carry)
toc("shell.Volume", t)

t = tic("nest ball makeSphere")
ball_nest = cq.Solid.makeSphere(ball_r, nest)
toc("makeSphere", t)

t = tic("nest_ball ^ shell")
print("   ->", round(max(0.0, ball_nest.intersect(shell).Volume()), 4), flush=True)
toc("nest_ball ^ shell", t)

t = tic("nest_ball ^ hub")
hub = pl.cyl_y(S.HUB_R, 34.0, pl.PADDLE_CENTER)
print("   ->", round(max(0.0, ball_nest.intersect(hub).Volume()), 4), flush=True)
toc("nest_ball ^ hub", t)

others = {n: s for n, s in kept.items() if n != "feeder_shell_tray"}
t = tic("_clash(shell, %d kept parts)" % len(others))
hits = S._clash(shell, others)
toc("_clash", t)
print("   hits:", hits, flush=True)

wu = sorted(n for n in kept if n.startswith("gecko_flywheel_upper_"))
wl = sorted(n for n in kept if n.startswith("gecko_flywheel_lower_"))
t = tic("flywheel nip distance (%dx%d)" % (len(wu), len(wl)))
nipm = min((kept[u].distance(kept[l]), u, l) for u in wu for l in wl)
print("   nip %.4f" % nipm[0], flush=True)
toc("flywheel distance", t)

t = tic("hub.distance(shell)")
print("   ->", round(kept["paddle_hub"].distance(shell), 4), flush=True)
toc("hub.distance(shell)", t)

t = tic("report()")
data = F.report(kept, dropped, relieved, consumed, kinematics)
toc("report", t)
print("PROBE2 DONE", flush=True)
