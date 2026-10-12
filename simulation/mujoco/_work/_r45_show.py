# -*- coding: utf-8 -*-
import csv, sys, math
p = sys.argv[1]
rows = list(csv.reader(open(p, encoding="utf-8")))
hdr = rows[0]; print(p, len(rows)-1, "rows"); print(hdr)
data = [[float(x) for x in r] for r in rows[1:]]
iJ = hdr.index("J"); ig = hdr.index("gate"); it = hdr.index("t")
# ball cols
bcols = [(j, hdr[j]) for j in range(len(hdr)) if hdr[j].endswith("_x")]
t0 = float(sys.argv[2]); t1 = float(sys.argv[3]); st = float(sys.argv[4])
last = -9
for r in data:
    if r[it] < t0 or r[it] > t1: continue
    if r[it] - last < st: continue
    last = r[it]
    s = "t=%6.2f J=%7.1f gate=%5.1f" % (r[it], r[iJ], r[ig])
    for j, nm in bcols:
        bx = r[j]
        if abs(bx) > 5000: continue
        s += "  %s(%.0f,%.0f)" % (nm[:2], bx, r[j+2])
    print(s)
