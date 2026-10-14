import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
OUT=r"C:\FTC design\FTC 2026 biobuzz\cad\output\_r55_frame\sections\r55_pollen_joint_schematic.png"
cases=[("x = 60  (tab z 16..44, grip 42 mm)",44.0,38.0),("x = 76  (tab z 16..48, grip 46 mm)",48.0,42.0)]
fig,axes=plt.subplots(1,2,figsize=(13,7))
for ax,(ttl,ztop,zplate) in zip(axes,cases):
    ax.add_patch(Rectangle((63,2),18,14,fc="#c9d6e8",ec="k",lw=1.2))
    ax.text(64.5,9,"base_rail\n(y 63..81, z 2..16)",fontsize=8,va="center")
    ax.add_patch(Rectangle((68,ztop),4,60-ztop,fc="#e8c9c9",ec="k",lw=1.2,hatch="//"))
    ax.text(66.0,min(ztop+7,52),"side plate y 68..72 (lower edge z=%.0f)"%zplate,fontsize=8,rotation=90,va="center",ha="right")
    ax.add_patch(Rectangle((68,16),16,ztop-16,fc="#d8e8c9",ec="k",lw=1.2))
    ax.text(76.5,16+(ztop-16)/2,"tab\n(y 68..84)",fontsize=8,ha="left",va="center")
    ax.add_patch(Rectangle((73.25,ztop),5.5,2.2,fc="#888",ec="k",lw=1.0))
    ax.text(79.3,ztop+1.1,"M3 head (O5.5)",fontsize=8,va="center")
    ax.add_patch(Rectangle((75.9,2.0-1.0),0.2*(76-75.9)*0+0.2*0+0.2,0))
    ax.add_patch(Rectangle((75.9,0.0),0.2*(76-75.9)*0+0.2*0+0.2,0))
    ax.add_patch(Rectangle((74.75,1.0),2.5,1.0,fc="#bbb",ec="k",lw=0.8))
    ax.add_patch(Rectangle((74.1,-1.4),4.0,2.4,fc="#999",ec="k",lw=0.8))
    ax.text(79.3,-0.2,"washer + M3 nut",fontsize=8,va="center")
    ax.plot([76,76],[ztop,-1.4],color="#b03030",lw=2.4)
    ax.text(51.2,34,"bolt shank:\nfrom leg top,\nnut under rail",fontsize=8,ha="left",va="center",color="#b03030")
    ax.annotate("",xy=(76,ztop),xytext=(76,-1.4),arrowprops=dict(arrowstyle="<->",color="#b03030",lw=1.0))
    ax.text(76.6,20,"grip %.0f mm"%(ztop-2),fontsize=9,color="#b03030")
    ax.set_xlim(50,104); ax.set_ylim(-10,64)
    ax.set_xlabel("y (mm)"); ax.set_ylabel("z (mm)")
    ax.set_title(ttl+"   -- R55 DEC-0055 fix A",fontsize=10)
    ax.grid(alpha=.3)
fig.suptitle("R55 rail-leg to base_rail joint, schematic section through the bolt axis (known dims, not a measurement)",fontsize=10)
fig.tight_layout()
fig.savefig(OUT,dpi=110)
print("wrote",OUT)
