import csv
rows=list(csv.DictReader(open(r'simulation/mujoco/out/_r45_idx_diag.csv',encoding='utf-8')))
print('cols',list(rows[0].keys()))
last=-1
for r in rows:
    t=float(r['t'])
    if t>6.2: break
    if t-last<0.25: continue
    last=t
    print('t=%5.2f J=%6.1f idx=%6.1f | '%(t,float(r['J']),float(r['idx']))+
          ' | '.join('b%d(%7.1f,%6.1f)'%(k,float(r['b%d_x'%k]),float(r['b%d_z'%k])) for k in (1,2,3,4)))