# -*- coding: utf-8 -*-
import io, sys
src = open("cad/paddle_launcher_shooter_assembly_r55.py", encoding="utf-8").read()
def rep(old, new, n=1):
    global src
    assert src.count(old) == n, (old[:60], src.count(old))
    src = src.replace(old, new)

rep('"""T06 R55 -- assembly-friendly frame (prototype), DEC-0055 fix A.',
    '"""T06 R56 -- R55 assembly-friendly frame with the intake tray lengthened.')
rep('OUT = HERE / "output" / "_r55_frame"', 'OUT = HERE / "output" / "_r56_frame"')
rep('HALF = {"pollen": 80.0, "nectar": 91.0}',
    'HALF = {"pollen": 80.0, "nectar": 91.0}\n\n'
    '# --- R56: lengthen the intake tray (single-parameter change) ---------------\n'
    '# Per the 2026-10-14 brief the tray is made longer so more balls queue behind\n'
    '# the paddle; everything else is R55.  Capacity (cad/_r56_tray_pick.py):\n'
    '#   TRAY_X1 = 215 -> pollen 3 / nectar 2      (R55)\n'
    '#   TRAY_X1 = 285 -> pollen 4 / nectar 3      (R56, chosen)\n'
    'STAGE_X1_R56 = 285.0\n'
    'import paddle_launcher_feeder_a_prime_shared as SH             # noqa: E402\n'
    'import paddle_launcher_feeder_a_prime_shared_staging as ST     # noqa: E402\n'
    'ST.STAGE_X1 = STAGE_X1_R56\n'
    'SH.F.TRAY_X1 = STAGE_X1_R56\n')
rep('FRAME_NAME = "shooter_frame_R55_merged"', 'FRAME_NAME = "shooter_frame_R56_merged"')
rep('    parts = build_parts(name)', '    parts = build_parts(name, fresh=True)')
rep('"T06_shooter_frame_R55_%s" % name', '"T06_shooter_frame_R56_%s" % name')
rep('"T06_shooter_assembly_R55_%s" % name', '"T06_shooter_assembly_R56_%s" % name')
rep('("report_r55_%s.json" % name)', '("report_r56_%s.json" % name)')
src = src.replace('"R55 %s section', '"R56 %s section').replace('"R55 %s full kept', '"R56 %s full kept')
src = src.replace('r55_%s_section_y', 'r56_%s_section_y').replace('r55_%s_assembly_y', 'r56_%s_assembly_y')
open("cad/paddle_launcher_shooter_assembly_r56.py", "w", encoding="utf-8").write(src)
print("written", len(src))
