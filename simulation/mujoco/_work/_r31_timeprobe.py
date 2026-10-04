"""Timing probe for the R26 shared export (does not modify any generator)."""
import sys, time, pathlib
sys.path.insert(0, "cad")
import paddle_launcher_feeder_redesign as F
import paddle_launcher_feeder_a_prime_shared as S  # applies the DEC-0030 overrides

print("probe start", flush=True)
t = time.time()
F.pl.build("nectar", 89.0)
print("pl.build(nectar, 89)  -> %.1f s" % (time.time() - t), flush=True)

t = time.time()
F.pl.build("pollen", 80.0)
print("pl.build(pollen, 80)  -> %.1f s" % (time.time() - t), flush=True)

F.BALL_D = 91.948
F.BALL_R = 45.974
F.R_CARRY = S.R_IN - 45.974
t = time.time()
F.build("nectar", 89.0)
print("F.build(nectar, 89)   -> %.1f s" % (time.time() - t), flush=True)
print("probe done", flush=True)
