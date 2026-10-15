import runpy
for f in ("cad/_r59_audit.py", "cad/_r59_h2d_audit.py", "cad/_r59_rail_figure.py"):
    print("=====", f, "=====", flush=True)
    runpy.run_path(f, run_name="__main__")
