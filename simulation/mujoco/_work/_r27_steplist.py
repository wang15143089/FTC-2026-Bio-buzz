# -*- coding: utf-8 -*-
import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
pat = re.compile(rb"PRODUCT\('([^']*)'")
for f in ("nectar", "pollen"):
    p = Path("cad/output/paddle_launcher_feeder_a_prime_shared_%s.step" % f)
    data = p.read_bytes()
    names = []
    for m in pat.finditer(data):
        n = m.group(1).decode("utf-8", "replace")
        if n not in names:
            names.append(n)
    tail = data[-60:].decode("utf-8", "replace").strip().replace("\n", " ")
    print("=== %s  %.1f MB  complete=%s" % (f, len(data) / 1048576.0, "END-ISO-10303-21;" in tail))
    print("    unique PRODUCT names = %d" % len(names))
    for n in names:
        print("      -", n)
