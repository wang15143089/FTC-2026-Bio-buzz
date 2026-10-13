# -*- coding: utf-8 -*-
"""T06 R52 view -- the accepted R51 renderer with an R52 colour map.

paddle_launcher_shooter_drive_r51_view.render() already draws any {name: shape}
mapping; R52 only needs its own colours and its own triangle-cache directory,
so the renderer itself is imported, not copied.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import paddle_launcher_shooter_drive_r51_view as V
import paddle_launcher_shooter_drive_r52 as R

V.R = R                      # triangle cache -> cad/output/_r52_drive/
_BASE = V.colour_of

COL = dict(V.COL)
COL["feeder"] = (110, 190, 120, 215)
COL["paddle"] = (36, 128, 92, 240)
COL["gate"] = (238, 150, 40, 235)
COL["new"] = (124, 122, 214, 215)


def colour_of(n):
    if n.startswith("gate_"):
        return COL["gate"]
    if n.startswith(("paddle_rotor", "paddle_flex", "paddle_shaft",
                     "paddle_bearing")):
        return COL["paddle"]
    if n.startswith(("feeder_shell", "guide_", "shooter_throat")):
        return COL["feeder"]
    if n.startswith(("servo_bridge", "feeder_mount")):
        return COL["new"]
    return _BASE(n)


V.colour_of = colour_of      # render() and tris() resolve this at call time
W, H = V.W, V.H
render = V.render
