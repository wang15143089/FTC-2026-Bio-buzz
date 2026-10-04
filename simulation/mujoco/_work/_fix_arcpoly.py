import io, re, pathlib
p = pathlib.Path("simulation/mujoco/_work/r6_fig_zh.py")
s = p.read_text(encoding="utf-8")
old = '''def arc_poly(a0, a1, r0=R_IN, r1=R_OUT, n=60):
    inn = [fp(a0 + (a1 - a0) * i / n, r0) for i in range(n + 1)]
    out = [fp(a0 + (a1 - a0) * i / n, r1) for i in range(n + 1)]
    return Polygon(inn + out[::-1], closed=True)
'''
new = '''def arc_poly(a0, a1, r0=R_IN, r1=R_OUT, n=60, **kw):
    inn = [fp(a0 + (a1 - a0) * i / n, r0) for i in range(n + 1)]
    out = [fp(a0 + (a1 - a0) * i / n, r1) for i in range(n + 1)]
    poly = Polygon(inn + out[::-1], closed=True)
    if kw:
        poly.set(**kw)
    return poly
'''
assert old in s, "pattern not found"
s = s.replace(old, new)
p.write_text(s, encoding="utf-8")
print("patched arc_poly")
