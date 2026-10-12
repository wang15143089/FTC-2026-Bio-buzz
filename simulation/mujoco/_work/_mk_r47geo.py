# -*- coding: utf-8 -*-
import io
p = r"simulation/mujoco/_work/_r46_relief.py"
out = r"simulation/mujoco/_work/_r47_geo.py"
src = io.open(p, encoding="utf-8").read()

src = src.replace("RELIEF = 0.0                    # >0:",
                  "FLEX_IN, BLADE_IN, EXIT_OPEN = 0.0, 0.0, 0.0\nRELIEF = 0.0                    # >0:", 1)
assert "FLEX_IN, BLADE_IN" in src

anchor = '    if a_ == "--relief" and i + 1 < len(argv):\n        RELIEF = float(argv[i + 1]); i += 2; continue\n'
assert anchor in src, "anchor A missing"
add = anchor + (
    '    if a_ == "--flex-in" and i + 1 < len(argv):\n'
    '        FLEX_IN = float(argv[i + 1]); i += 2; continue\n'
    '    if a_ == "--blade-in" and i + 1 < len(argv):\n'
    '        BLADE_IN = float(argv[i + 1]); i += 2; continue\n'
    '    if a_ == "--exit-open" and i + 1 < len(argv):\n'
    '        EXIT_OPEN = float(argv[i + 1]); i += 2; continue\n')
src = src.replace(anchor, add, 1)

i0 = src.index("    if RELIEF > 0.0:")
i1 = src.index("    R._PROBE.clear()\n    return out\n", i0)
new_blk = (
    "    if RELIEF or FLEX_IN or BLADE_IN or EXIT_OPEN:\n"
    "        for g in range(mm.ngeom):\n"
    "            nmx = mujoco.mj_id2name(mm, mujoco.mjtObj.mjOBJ_GEOM, g) or \"\"\n"
    "            if nmx.startswith(\"paddle_\"):\n"
    "                vx, vz = mm.geom_pos[g][0] * 1000.0, mm.geom_pos[g][2] * 1000.0\n"
    "            elif nmx.startswith(\"r10_\") or nmx.startswith(\"shell_\"):\n"
    "                vx = mm.geom_pos[g][0] * 1000.0 - pv2.PADDLE_CX\n"
    "                vz = mm.geom_pos[g][2] * 1000.0 - pv2.PADDLE_CZ\n"
    "            else:\n"
    "                continue\n"
    "            L_ = math.hypot(vx, vz) or 1.0\n"
    "            dd = 0.0\n"
    "            if nmx.startswith(\"r10_\") or nmx.startswith(\"shell_\"):\n"
    "                dd += RELIEF\n"
    "            if nmx == \"shell_exit_face\":\n"
    "                dd += EXIT_OPEN\n"
    "            if nmx.startswith(\"paddle_flex_\"):\n"
    "                dd -= FLEX_IN\n"
    "            if nmx.startswith(\"paddle_blade_\"):\n"
    "                dd -= BLADE_IN\n"
    "            if dd:\n"
    "                mm.geom_pos[g][0] += (vx / L_) * dd * MM\n"
    "                mm.geom_pos[g][2] += (vz / L_) * dd * MM\n"
    "        print(\"### geo flex_in=%.2f blade_in=%.2f exit_open=%.2f relief=%.2f\"\n"
    "              % (FLEX_IN, BLADE_IN, EXIT_OPEN, RELIEF), flush=True)\n")
src = src[:i0] + new_blk + src[i1:]
io.open(out, "w", encoding="utf-8", newline="\n").write(src)
print("OK", len(src))
