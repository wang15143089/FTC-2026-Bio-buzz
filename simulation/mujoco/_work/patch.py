import re,sys
p=r"simulation/mujoco/_work/plot_v2_zh.py"
s=open(p,encoding="utf-8").read()
s=s.replace('height_ratios=[1.18,1.0]','height_ratios=[1.02,1.0]')
s=s.replace('ax.set_xlim(-150,245); ax.set_ylim(-45,215)','ax.set_xlim(-150,250); ax.set_ylim(-45,190)')
s=s.replace('ax.text(o[0]+118*t52[0]+30,o[2]+118*t52[1]+30,','ax.text(o[0]+118*t52[0]+30,o[2]+118*t52[1]+30,clip_on=True,')
s=s.replace('ax.plot(c[0],c[2],"s",color="#333",ms=9,zorder=4); ax.text(c[0]+6,c[2]-18,lab,fontsize=10)',
            'ax.plot(c[0],c[2],"s",color="#333",ms=9,zorder=4,clip_on=True); ax.text(c[0]+6,c[2]-18,lab,fontsize=10,clip_on=True)')
open(p,"w",encoding="utf-8").write(s)
print("patched")
