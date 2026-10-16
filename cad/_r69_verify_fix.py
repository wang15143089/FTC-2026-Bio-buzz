# -*- coding: utf-8 -*-
"""One-shot fixer for cad/_r69_verify.py (3 self-bugs found in the first run)."""
from pathlib import Path

p = Path("cad/_r69_verify.py")
s = p.read_text(encoding="utf-8")
n = 0

# --- 1) load the fastener table (needed for V6 ear y-ranges) --------------------
old = 'orig = imp(OLD / "frameP_1_rear_lower.step")'
new = ('orig = imp(OLD / "frameP_1_rear_lower.step")\n'
       'fas = json.loads((D / "fasteners.json").read_text(encoding="utf-8"))\n'
       'NET_GAIN = 7417.0   # 8 ears +7919.9 mm3 minus 8 x d3.4 drillings -502.9 mm3')
assert s.count(old) == 1
s = s.replace(old, new); n += 1

# --- 2) V1: the retired body is the pre-ear, pre-drill shape --------------------
old = '''chk("R69-V1", "volume (split conservation)", 0.0,
    round(mid.Volume() + pL.Volume() + pR.Volume() - orig.Volume(), 3), 1.0,
    "sum of the three delivered STEP volumes minus the retired frameP_1_rear_lower STEP volume",
    "y = +-68 split plane")'''
new = '''chk("R69-V1", "volume (split + joint net)", NET_GAIN,
    round(mid.Volume() + pL.Volume() + pR.Volume() - orig.Volume(), 3), 1.0,
    "sum of the three delivered STEP volumes minus the retired frameP_1_rear_lower STEP volume",
    "y = +-68 split plane, then +8 bolted ears (+7919.9 mm3) and -8 x d3.4 drillings (-502.9 mm3)")'''
assert s.count(old) == 1
s = s.replace(old, new); n += 1

# --- 3) V6: the sample box must sit inside the ear AND clear of the bolt hole ----
old = '''worst = 1.0
for tag, x, z, plate, nut_y, ln in STA:
    for s in (1, -1):
        ya, yb = sorted((s*nut_y, s*67.8))
        c = box(x-4.0, x+4.0, ya+0.3, yb-0.3, z-4.0, z+4.0)
        worst = min(worst, c.intersect(body).Volume() / c.Volume())
chk("R69-V6", "fill fraction (ears)", 1.0, round(worst, 4), 0.05,
    "8 x 8 x 8 sample cube centred in each ear, intersected with the delivered mid body",
    "8 ears", unit="-")'''
new = '''ear_y = {(e["tag"], e["side"]): e["ear_y"] for e in fas["items"]}
worst = 1.0
for tag, x, z, plate, nut_y, ln in STA:
    for s in (1, -1):
        ya, yb = sorted(ear_y[(tag, "R" if s > 0 else "L")])
        c = box(x + 2.2, x + 5.7, ya + 0.3, yb - 0.3, z - 4.7, z + 4.7)
        worst = min(worst, c.intersect(body).Volume() / c.Volume())
chk("R69-V6", "fill fraction (ears)", 1.0, round(worst, 4), 0.05,
    "9.4 x (ear depth - 0.6) x 3.5 sample box inside each ear, offset in +x so the "
    "d3.4 bolt hole is excluded, intersected with the delivered mid body",
    "8 ears", unit="-")'''
assert s.count(old) == 1
s = s.replace(old, new); n += 1

# --- 4) V8: plates_index.json stores sum_volume_mm3 per plate -------------------
old = 'sum(p["volume_mm3"] for p in plates["plates"])'
new = 'sum(p["sum_volume_mm3"] for p in plates["plates"])'
assert s.count(old) == 1
s = s.replace(old, new); n += 1

p.write_text(s, encoding="utf-8")
print("patched %d sites" % n)
