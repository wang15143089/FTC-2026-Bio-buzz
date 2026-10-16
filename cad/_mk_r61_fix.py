# -*- coding: utf-8 -*-
"""Final touch-ups on the generated R61 generator (see cad/_mk_r61.py)."""
import io
from pathlib import Path

P = Path("cad/paddle_launcher_shooter_assembly_r61.py")
s = io.open(P, encoding="utf-8").read()

def rep(old, new, times=1):
    global s
    assert s.count(old) == times, "count=%d for %r" % (s.count(old), old[:60])
    s = s.replace(old, new)

rep("T06_base_rail_R60_%s", "T06_base_rail_R61_%s", 1)
rep('FRAME_NAME = "shooter_frame_R60_merged"', 'FRAME_NAME = "shooter_frame_R61_merged"')
rep("3. Deliverable T06_print_set_R60_<variant>.step: EVERY body that has to be",
    "3. Deliverable T06_print_set_R61_<variant>.step: EVERY body that has to be")
rep("# --- R60: base_rail_+72 / base_rail_-72 stay, thickened DOWNWARDS ----------",
    "# --- R60 rail section kept, thickened DOWNWARDS; R61 fuses both sides -----")
rep("    pocket under each M3 rail joint.  R60: one printed piece per side, no split.",
    "    pocket under each M3 rail joint.  R60: one printed piece per side, no split;\n"
    "    R61 then fuses the two sides with 4 ribs in join_rails() below.")
io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("patched %s" % P)
left = [(i + 1, ln.strip()) for i, ln in enumerate(s.splitlines())
        if "r60" in ln or "R60" in ln]
print("remaining r60/R60 lines: %d" % len(left))
for i, ln in left:
    print("   %4d | %s" % (i, ln[:105]))

