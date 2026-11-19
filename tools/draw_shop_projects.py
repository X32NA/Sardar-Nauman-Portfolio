"""Draw assembly and component sheets for the sensor stand and drill fixture."""
from generate_drawings import (
    prepare, sheet, text, line, rect, circle, holes, dimx, dimy, label, notes, bubble, INK,
)
from generate_shop_projects import (
    OUT, STAND_ANCHORS, POST_FASTENERS, FIXTURE_ANCHORS, FIXTURE_PINS, GUIDE_FASTENERS, DRILL_AXIS,
)


def view(c, x, y, caption):
    text(c, x, y, caption, 3.6, True, "center")


def table(c, x, y, widths, heading, rows):
    for i, row in enumerate([heading, *rows]):
        bottom = y-8*(i+1)
        rect(c, x, bottom, sum(widths), 8, i == 0)
        current = x
        for width, value in zip(widths, row):
            text(c, current+2.6, bottom+2.7, value, 3.2, i == 0)
            current += width
            if current < x+sum(widths):
                line(c,current,bottom,current,bottom+8,True)


def roundslot(c, x, y, width, height):
    c.setStrokeColor(INK)
    c.setLineWidth(.33)
    c.roundRect(x-width/2,y-height/2,width,height,width/2)
    line(c,x,y-height/2-3,x,y+height/2+3,True,[2,1])


def axis(c,x1,y1,x2,y2):
    line(c,x1,y1,x2,y2,True,[4,1,1,1])


def circle_on_plan(c,x,y,positions,diameter,scale=1):
    holes(c, [(x+a*scale,y+b*scale) for a,b in positions], diameter*scale/2)


def paired(c,x,y,positions,outer,inner,scale=1):
    for a,b in positions:
        circle(c,x+a*scale,y+b*scale,outer*scale/2,True)
    circle_on_plan(c,x,y,positions,inner,scale)


def sensor_set():
    c=prepare("SM-100-sensor-stand-drawings.pdf")
    sheet(c,"SM-100","Adjustable sensor stand","General arrangement  /  M12 barrel sensor  /  fastener interfaces", "1:1")
    x,y=36,83
    rect(c,x,y,100,10)
    rect(c,x+38,y+10,24,120)
    roundslot(c,x+50,y+78,6.6,60)
    # Carriage hides the middle part of the slot in this view.
    c.setFillColorRGB(1,1,1)
    c.rect(x+32,y+56,36,44,stroke=0,fill=1)
    rect(c,x+32,y+56,36,44)
    rect(c,x+14,y+72,18,12)
    rect(c,x+68,y+72,10,12)
    axis(c,x+9,y+78,x+83,y+78)
    dimy(c,x,y,y+130,24,"130")
    dimx(c,x,x+100,y,71,"100")
    bubble(c,1,145,83,x+95,y+3)
    bubble(c,2,113,225,x+60,y+120)
    bubble(c,3,148,181,x+66,y+98)
    bubble(c,4,48,180,x+15,y+81)
    view(c,87,60,"FRONT")
    bx,by=166,83
    rect(c,bx,by,70,10)
    rect(c,bx+46,by+10,10,120)
    rect(c,bx+30,by+56,16,44)
    circle(c,bx+38,by+78,6)
    axis(c,bx+25,by+78,bx+62,by+78)
    line(c,bx+46,by+68,bx+59,by+68,True,[2,1])
    line(c,bx+46,by+88,bx+59,by+88,True,[2,1])
    dimx(c,bx,bx+70,by,71,"70")
    view(c,201,60,"RIGHT")
    table(c,251,234,[14,14,119],("ITEM","QTY","PART / HARDWARE"),[
        ("1","1","SM-101 base, 6061-T6"),("2","1","SM-102 upright, 6061-T6"),
        ("3","1","SM-103 carriage, 6061-T6"),("4","1","M12 barrel sensor and two locknuts"),
        ("5","2","M4 × 12 socket screws, underside of base"),
        ("6","2","M6 × 18 screws with flat washers, rear of upright")])
    notes(c,251,160,"ASSEMBLY AND SETUP",[
        "1. Fasten upright from below. Seat the base flush to the machine.",
        "2. Install both carriage screws from the rear of the upright.",
        "3. Set sensor height, then secure the barrel with its locknuts.",
        "Two-screw adjustment range: 61.3 to 94.7 nominal sensor height.",
        "Sensor envelope is represented in CAD. Fasteners are listed in BOM."])
    c.showPage()
    sheet(c,"SM-101","Sensor stand base","6061-T6 aluminium  /  machining drawing", "1:1")
    x,y=55,139
    rect(c,x,y,100,70)
    circle_on_plan(c,x,y,STAND_ANCHORS,6.6)
    paired(c,x,y,POST_FASTENERS,8,4.5)
    dimx(c,x,x+100,y+70,225,"100")
    dimy(c,x,y,y+70,37,"70")
    view(c,105,128,"TOP")
    rect(c,x,86,100,10)
    dimy(c,x,86,96,37,"10")
    view(c,105,76,"FRONT")
    table(c,180,222,[57,33,33,94],("FEATURE","X","Y","DETAIL"),[
        ("Machine mounting","12 / 88","12 / 58","4× Ø6.6 THRU, all combinations"),
        ("Post screws","44 / 56","51","2× Ø4.5 THRU"),
        ("Underside pockets","44 / 56","51","2× Ø8 counterbore × 4.4 deep")])
    notes(c,180,159,"MACHINING NOTES",[
        "Hole coordinates reference the lower-left corner of the top view.",
        "Unless specified, linear dimensions ±0.20 mm.",
        "Break sharp edges. Keep the bottom seating face flat and burr-free.",
        "DXF separates drilled features and underside counterbores."])
    c.showPage()
    sheet(c,"SM-102 / SM-103","Slotted upright and carriage","6061-T6 aluminium  /  machining drawing  /  one of each", "1:1")
    x,y=58,88
    rect(c,x,y,24,120)
    roundslot(c,x+12,y+68,6.6,60)
    dimx(c,x,x+24,y+120,221,"24")
    dimy(c,x,y,y+120,39,"120")
    axis(c,x+12,y+5,x+12,y+114)
    label(c,(x+15,y+68),(93,158),"6.6 × 60 THRU")
    view(c,70,74,"SM-102 FRONT")
    rect(c,98,187,24,10)
    circle_on_plan(c,98,187,[(6,5),(18,5)],3.3)
    label(c,(116,192),(126,211),"2× M4 × 0.7")
    view(c,110,181,"UNDERSIDE")
    q,r=241,133
    rect(c,q,r,36,44)
    circle_on_plan(c,q,r,[(18,12),(18,32)],5)
    axis(c,q-3,r+22,q+40,r+22)
    dimx(c,q,q+36,r+44,189,"36")
    dimy(c,q,r,r+44,229,"44")
    view(c,259,122,"SM-103 REAR")
    rect(c,327,r,16,44)
    circle_on_plan(c,327,r,[(8,22)],12.2)
    dimx(c,327,343,r+44,189,"16")
    label(c,(335,r+22),(350,160),"Ø12.2 THRU")
    view(c,335,122,"END")
    notes(c,41,62,"UPRIGHT FEATURES",[
        "Slot centred on width, centre 68 from lower face.",
        "M4 hole centres at X = 6 and 18, centred on 10 mm thickness.",
        "M4 thread depth 8. Tap-drill depth 10."])
    notes(c,210,91,"CARRIAGE FEATURES",[
        "2× M6 × 1 tapped holes on the width centreline.",
        "Hole centres 12 and 32 from lower face. Thread depth 6.",
        "Tap-drill depth 8. Sensor bore centres 8 and 22 in end view.",
        "Unless noted, ±0.20 mm. Break sharp edges and deburr."])
    c.showPage()
    c.save()


def fixture_set():
    c=prepare("DF-200-drill-fixture-drawings.pdf")
    sheet(c,"DF-200","Drill locating fixture","General arrangement  /  Ø6 guided drilling  /  three-point location", "1:1")
    x,y=42,135
    rect(c,x,y,135,90)
    circle_on_plan(c,x,y,FIXTURE_ANCHORS,6.6)
    for a,b in FIXTURE_PINS:
        circle(c,x+a,y+b,3)
    line(c,x+27,y+23,x+105,y+23,True,[2,1])
    line(c,x+105,y+23,x+105,y+63,True,[2,1])
    line(c,x+105,y+63,x+27,y+63,True,[2,1])
    line(c,x+27,y+63,x+27,y+23,True,[2,1])
    rect(c,x+49,y+33,34,43)
    paired(c,x,y,[DRILL_AXIS],16,6)
    circle_on_plan(c,x,y,GUIDE_FASTENERS,5.5)
    bubble(c,1,184,225,x+130,y+85)
    bubble(c,2,140,223,x+82,y+72)
    bubble(c,3,81,190,x+60,y+49)
    bubble(c,4,74,156,x+27,y+43)
    view(c,110,127,"TOP · DASHED WORKPIECE ENVELOPE")
    dimx(c,x,x+135,y+90,241,"135")
    dimy(c,x,y,y+90,24,"90")
    z=74
    rect(c,x,z,135,12)
    rect(c,x+49,z+12,34,20)
    rect(c,x+58,z+32,16,2)
    dimy(c,x,z,z+34,24,"34")
    view(c,110,62,"FRONT")
    table(c,222,229,[14,14,137],("ITEM","QTY","PART / HARDWARE"),[
        ("1","1","DF-201 fixture base, 6061-T6"),
        ("2","1","DF-202 guide, 6061-T6"),
        ("3","1","DF-203 shouldered Ø6 drill bushing, hardened steel"),
        ("4","3","Ø6 × 18 locator dowels"),
        ("5","2","M5 × 30 screws and washers for guide block")])
    notes(c,222,161,"WORKPIECE SETUP",[
        "Part envelope: 78 × 40 × 6 mm. Seat long edge on two dowels.",
        "Seat the short edge on the third dowel. Clamp clear of guide.",
        "Drill axis is 39 mm and 20 mm from the located workpiece edges.",
        "A Ø10 exit hole under the workpiece provides drill clearance.",
        "Workpiece and clamps are supplied for each setup.",
        "Screws are listed in the BOM and omitted from the CAD export."])
    c.showPage()
    sheet(c,"DF-201","Fixture base","6061-T6 aluminium  /  machining drawing", "1:1")
    x,y=47,127
    rect(c,x,y,135,90)
    circle_on_plan(c,x,y,FIXTURE_ANCHORS,6.6)
    circle_on_plan(c,x,y,FIXTURE_PINS,6)
    circle_on_plan(c,x,y,GUIDE_FASTENERS,4.2)
    circle_on_plan(c,x,y,[DRILL_AXIS],10)
    dimx(c,x,x+135,y+90,233,"135")
    dimy(c,x,y,y+90,27,"90")
    view(c,114,115,"TOP")
    rect(c,x,78,135,12)
    dimy(c,x,78,90,27,"12")
    view(c,114,68,"FRONT")
    table(c,204,231,[49,32,28,81],("FEATURE","X","Y","DETAIL"),[
        ("Bench mounting","10 / 125","10 / 80","4× Ø6.6 THRU"),
        ("Front locators","42 / 90","20","2× Ø6 THRU"),
        ("Side locator","24","43","1× Ø6 THRU"),
        ("Guide screws","56 / 76","70","2× M5 × 0.8 THRU"),
        ("Drill exit","66","43","1× Ø10 THRU")])
    notes(c,204,159,"MACHINING AND INSPECTION",[
        "Hole coordinates reference the lower-left corner of the top view.",
        "Unless noted, linear dimensions ±0.15 mm.",
        "Locator centres ±0.05 mm. Finish bores for the selected dowel fit.",
        "Deburr exit hole and keep the workpiece seating face clear.",
        "DXF includes tap-drill geometry. PDF controls the thread callouts."])
    c.showPage()
    sheet(c,"DF-202 / DF-203","Guide and drill bushing","Guide in 6061-T6 aluminium  /  bushing in hardened tool steel", "2:1")
    x,y=61,123
    rect(c,x,y,68,86)
    circle_on_plan(c,x,y,[(17,10)],12,2)
    circle_on_plan(c,x,y,[(7,37),(27,37)],5.5,2)
    dimx(c,x,x+68,y+86,223,"34")
    dimy(c,x,y,y+86,44,"43")
    label(c,(x+34,y+20),(140,138),"Ø12 BUSHING SEAT")
    label(c,(x+54,y+74),(140,203),"2× Ø5.5 THRU")
    view(c,95,116,"GUIDE TOP")
    a,b=58,60
    line(c,a,b+12,a+62,b+12)
    line(c,a+62,b+12,a+62,b)
    line(c,a+62,b,a+86,b)
    line(c,a+86,b,a+86,b+40)
    line(c,a+86,b+40,a,b+40)
    line(c,a,b+40,a,b+12)
    dimy(c,a+86,b,b+40,155,"20")
    view(c,101,48,"GUIDE SIDE")
    u,v=259,155
    circle(c,u,v,16)
    circle(c,u,v,6.05)
    axis(c,u-20,v,u+20,v)
    axis(c,u,v-20,u,v+20)
    view(c,u,v-25,"BUSHING TOP")
    bx,by=242,191
    rect(c,bx,by+28,32,4)
    rect(c,bx+4,by,24,28)
    for xx in (bx+16-6.05,bx+16+6.05):
        line(c,xx,by,xx,by+32,True,[2,1])
    dimx(c,bx,bx+32,by+32,234,"Ø16")
    dimx(c,bx+4,bx+28,by,183,"Ø12")
    dimy(c,bx+32,by,by+32,286,"16")
    label(c,(bx+22,by+30),(296,225),"Ø6.05 +0.03 / 0 THRU")
    view(c,261,245,"BUSHING SIDE")
    notes(c,186,104,"GUIDE GEOMETRY AND BUSHING FIT",[
        "Guide hole centres from lower-left corner: X17/Y10 and X7,27/Y37.",
        "Rear support extends 12 mm from the back edge; front clearance is 6 mm.",
        "Guide top arm thickness 14 mm. Size the seat to the actual bushing fit.",
        "Bushing shoulder thickness 2 mm; body length below shoulder 14 mm.",
        "Unless noted, linear dimensions ±0.15 mm. Break sharp edges."])
    c.showPage()
    c.save()


if __name__ == "__main__":
    sensor_set()
    fixture_set()
