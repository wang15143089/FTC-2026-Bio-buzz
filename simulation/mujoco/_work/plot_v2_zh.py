# -*- coding: utf-8 -*-
"""V2 全流程仿真结果图（中文，v2）"""
import json, math, sys, importlib.util
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")
spec = importlib.util.spec_from_file_location("pv2", r"simulation/mujoco/pollen_v2_sim.py")
pv2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(pv2)
plt.rcParams["font.sans-serif"]=["Microsoft YaHei","SimHei","DejaVu Sans"]
plt.rcParams["axes.unicode_minus"]=False
OUT="simulation/mujoco/out/"
tr=json.load(open(OUT+"trace_v2_tray_p200.json",encoding="utf-8"))

fig=plt.figure(figsize=(20,11.6))
gs=fig.add_gridspec(2,3,width_ratios=[1,1,1],height_ratios=[1.02,1.0],hspace=0.20,wspace=0.22)

# ============ 面板1：全流程总览 ============
ax=fig.add_subplot(gs[0,0:2])
CX,CZ=pv2.PADDLE_CX,pv2.PADDLE_CZ
th=np.linspace(math.radians(pv2.A_EXIT),math.radians(pv2.A_LIP),200)
ax.fill(np.concatenate([CX+pv2.R_OUT*np.cos(th),(CX+pv2.R_IN*np.cos(th))[::-1]]),
        np.concatenate([CZ+pv2.R_OUT*np.sin(th),(CZ+pv2.R_IN*np.sin(th))[::-1]]),
        color="#9ec9e2",alpha=.8,zorder=1,label="外罩（一体式，内壁 R94）")
ax.plot(CX+pv2.R_CARRY*np.cos(th),CZ+pv2.R_CARRY*np.sin(th),"--",color="#2b6c93",lw=1.2,zorder=2,label="球心轨道 R58.4")
xs=np.array([pv2.TRAY_X0,pv2.TRAY_X1]); ax.plot(xs,pv2.tray_top_z(xs),color="#0e7a3c",lw=6,alpha=.9,zorder=1,label="托板（5° 倾斜，右高左低）")
ax.plot([pv2.STRUT_X0,pv2.STRUT_X1],[45,45],color="#0e7a3c",lw=4,zorder=1)
ax.annotate("唇口 225°",xy=pv2.polar(97,-135),xytext=(-72,84),fontsize=10,color="#1f4e79",
            arrowprops=dict(arrowstyle="->",color="#1f4e79"))
ax.annotate("出口 142°",xy=pv2.polar(97,152),xytext=(-38,178),fontsize=10,color="#1f4e79",
            arrowprops=dict(arrowstyle="->",color="#1f4e79"))
for a in (18,138,258):
    ax.plot([CX,CX+60*math.cos(math.radians(a))],[CZ,CZ+60*math.sin(math.radians(a))],lw=7,color="#e08a1e",solid_capstyle="round",zorder=3)
ax.plot(CX,CZ,"o",color="#b06a00",ms=7,zorder=4); ax.text(CX+3,CZ+6,"拨杆轴",fontsize=10,color="#b06a00")
t52=pv2.direction(52); n52=pv2.normal(52); o=pv2.SHOOTER_ORIGIN
L=np.array([-190,215])
ax.plot(o[0]+L*t52[0],o[2]+L*t52[1],"--",color="#666",lw=1.2,zorder=1)
for s in (+1,-1):
    ax.plot(o[0]+L*t52[0]+s*55*n52[0],o[2]+L*t52[1]+s*55*n52[1],"-",color="#555",lw=2.2,zorder=1)
ax.text(o[0]+118*t52[0]+30,o[2]+118*t52[1]+30,"52° 发射通道\n宽 108",fontsize=10,color="#333",rotation=52,clip_on=True)
for sgn,lab in ((1,"上飞轮"),(-1,"下飞轮")):
    c=pv2.flywheel_axle_center(sgn); ax.plot(c[0],c[2],"s",color="#333",ms=9,zorder=4,clip_on=True); ax.text(c[0]+6,c[2]-18,lab,fontsize=10,clip_on=True)
ax.plot([],[],"s",color="#333",label="对置双飞轮 Ø96（夹口 lx=0）")
seg=[s for s in tr if -70<=s["x"]<=235 and -25<=s["z"]<=205]
sc=ax.scatter([s["x"] for s in seg],[s["z"] for s in seg],c=[s["v"] for s in seg],cmap="turbo",s=10,zorder=5)
cb=fig.colorbar(sc,ax=ax,pad=.012,fraction=.042); cb.set_label("球速 / (m/s)",fontsize=10)
ax.plot([-2.3],[53.06],"*",color="red",ms=17,zorder=6,label="唇口停位 (-2.3, 53.1)")
ax.annotate("① 球从托板右端滚入",xy=(140,66),xytext=(24,10),fontsize=12,color="#0e7a3c",fontweight="bold",
            arrowprops=dict(arrowstyle="->",color="#0e7a3c"))
ax.annotate("② 叶片在 x≈113 接球",xy=(112,63),xytext=(110,104),fontsize=12,color="#b06a00",fontweight="bold",
            arrowprops=dict(arrowstyle="->",color="#b06a00"))
ax.annotate("③ 沿内壁输送 ≈99°",xy=pv2.polar(58.4,183),xytext=(-118,118),fontsize=12,color="#1f4e79",fontweight="bold",
            arrowprops=dict(arrowstyle="->",color="#1f4e79"))
ax.annotate("④ 142° 切线出罩",xy=(-18,150),xytext=(-96,190),fontsize=12,color="#1f4e79",fontweight="bold",
            arrowprops=dict(arrowstyle="->",color="#1f4e79"))
ax.annotate("⑤ 飞轮夹口发射\n6.53 m/s @ 50.2°",xy=(14,6),xytext=(58,120),fontsize=13,color="red",fontweight="bold",
            arrowprops=dict(arrowstyle="->",color="red"))
ax.set_xlim(-150,250); ax.set_ylim(-45,190); ax.set_aspect("equal")
ax.set_xlabel("X / mm"); ax.set_ylabel("Z / mm")
ax.set_title("C06B-POLLEN-FEEDER-V2 全流程 MuJoCo 仿真（拨杆 200 rpm，飞轮 1620 rpm）",fontsize=15)
ax.legend(loc="lower left",fontsize=9,framealpha=.92); ax.grid(alpha=.25)

# ============ 面板2：飞轮转速阶梯 ============
ax4=fig.add_subplot(gs[0,2])
rpm=[810,1620,2430]; sp=[3.60,6.53,8.67]; rg=[1.29,4.28,7.49]
ax4.bar([str(r) for r in rpm],sp,color="#2b6c93",alpha=.9,width=.55)
for i,(s,g) in enumerate(zip(sp,rg)):
    ax4.text(i,s+.18,"%.2f m/s\n射程 %.2f m"%(s,g),ha="center",fontsize=10)
ax4.set_ylim(0,11.2); ax4.set_xlabel("飞轮转速 / rpm"); ax4.set_ylabel("出射速度 / (m/s)")
ax4.set_title("发射性能：出口速度\n≈0.80×轮缘线速度，出射角 50–53°",fontsize=12)
ax4.grid(alpha=.25,axis="y")

# ============ 面板3：通道放大 ============
ax2=fig.add_subplot(gs[1,0:2])
seg2=[s for s in tr if s["t"]>=4.88 and -185<=s["lx"]<=70]
lx=np.array([s["lx"] for s in seg2]); lz=np.array([s["lz"] for s in seg2]); vv=np.array([s["v"] for s in seg2])
ax2.plot([-185,70],[0,0],"--",color="#666",lw=1.2)
for s in (+1,-1): ax2.plot([-185,70],[s*55,s*55],"-",color="#555",lw=2.4)
for xx in (-55,55): ax2.plot([xx,xx],[-48,48],color="#333",lw=1.6)
for yy in (-43,43): ax2.add_patch(plt.Circle((0,yy),48,fill=False,color="#333",lw=1.6))
ax2.text(-50,40,"上飞轮 Ø96",fontsize=10); ax2.text(60,-46,"下飞轮",fontsize=10)
sc2=ax2.scatter(lx,lz,c=vv,cmap="turbo",s=16,zorder=5)
fig.colorbar(sc2,ax=ax2,pad=.012,fraction=.045).set_label("球速 / (m/s)",fontsize=10)
ax2.annotate("142° 出口切线，球心距中线仅 ≈4 mm\n（旧几何 52° 顶板卡点未复现）",xy=(-168,4),xytext=(-182,38),fontsize=10,color="#1f4e79",
             arrowprops=dict(arrowstyle="->",color="#1f4e79"))
ax2.annotate("夹口 lx=0\n0.15 → 6.55 m/s",xy=(1,0),xytext=(16,34),fontsize=11,color="red",fontweight="bold",
             arrowprops=dict(arrowstyle="->",color="red"))
ax2.set_xlim(-185,70); ax2.set_ylim(-60,60); ax2.set_aspect("equal")
ax2.set_xlabel("沿 52° 通道坐标 lx / mm"); ax2.set_ylabel("法向 lz / mm")
ax2.set_title("通道段放大：球沿中线进入夹口，全程无卡点",fontsize=13); ax2.grid(alpha=.25)

# ============ 面板4：拨杆转速门槛 ============
ax3=fig.add_subplot(gs[1,2])
labs=["100","105","110","115","200","140","200"]
res=[1,1,1,1,1,.25,1]
txt=["成功","成功","成功","成功","成功","2/8 成功","8/8 成功"]
ax3.bar(range(len(res)),[r*100 for r in res],color=["#1e8449" if r==1 else "#c0392b" for r in res],alpha=.9)
for i,(r,t) in enumerate(zip(res,txt)): ax3.text(i,r*100+4,t,ha="center",fontsize=9)
ax3.set_xticks(range(len(res))); ax3.set_xticklabels(labs,fontsize=10)
ax3.set_ylim(0,132)
ax3.set_xlabel("拨杆转速 / rpm"); ax3.set_ylabel("全流程成功率 / %")
ax3.text(.5,120,"球已在唇口停位",fontsize=11,color="#1e8449",fontweight="bold")
ax3.text(5.0,120,"从托板进料",fontsize=11,color="#b06a00",fontweight="bold")
ax3.axvspan(-.5,4.5,color="#1e8449",alpha=.06); ax3.axvspan(4.5,6.5,color="#b06a00",alpha=.07)
ax3.set_title("拨杆转速门槛",fontsize=13); ax3.grid(alpha=.25,axis="y")

fig.savefig(OUT+"v2_fullflow_zh.png",dpi=112,bbox_inches="tight")
print("saved",OUT+"v2_fullflow_zh.png")
