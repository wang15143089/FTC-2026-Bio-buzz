import cadquery as cq
for tag, p in (("NECTAR", r"C:\Users\admin\Downloads\am-5852_blue Blue Alliance Nectar.STEP"),
               ("POLLEN", r"C:\Users\admin\Downloads\am-5851_yellow Pollen.STEP")):
    try:
        s = cq.importers.importStep(p)
        v = s.val()
        bb = v.BoundingBox()
        print(tag, "solids=", len(s.solids().vals()),
              "bbox=", [round(x,3) for x in (bb.xlen, bb.ylen, bb.zlen)],
              "vol=", round(v.Volume(),1))
    except Exception as e:
        print(tag, "ERR", e)
