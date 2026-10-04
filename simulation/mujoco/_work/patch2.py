p=r"simulation/mujoco/_work/plot_v2_zh.py"
s=open(p,encoding="utf-8").read()
s=s.replace('ax.text(o[0]+118*t52[0]+30,o[2]+118*t52[1]+30,clip_on=True,"52\u00b0 \u53d1\u5c04\u901a\u9053\\n\u5bbd 108",fontsize=10,color="#333",rotation=52)',
            'ax.text(o[0]+118*t52[0]+30,o[2]+118*t52[1]+30,"52\u00b0 \u53d1\u5c04\u901a\u9053\\n\u5bbd 108",fontsize=10,color="#333",rotation=52,clip_on=True)')
open(p,"w",encoding="utf-8").write(s)
print("ok")
