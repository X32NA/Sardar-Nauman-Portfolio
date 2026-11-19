"""Create the dimensioned vector PDF sheets from the drafting sample dimensions."""
from math import atan2, cos, sin, pi, hypot
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
pdfmetrics.registerFont(TTFont("DrawingText", f"{FONT_DIR}/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DrawingBold", f"{FONT_DIR}/DejaVuSans-Bold.ttf"))
from generate_cad import OUT, TRAY_BA, BRACKET_BA, TRAY_FLAT, BRACKET_FLAT

INK = HexColor("#172638")
DIM = HexColor("#31567a")
LIGHT = HexColor("#eaf0f5")


def prepare(filename):
    c = canvas.Canvas(str(OUT / filename), pagesize=(420*mm, 297*mm), invariant=1)
    c.setTitle(filename.removesuffix(".pdf"))
    c.setAuthor("Sardar Nauman Ahmed Maan | Portfolio demonstration")
    return c


def text(c, x, y, value, size=3.4, bold=False, align="left"):
    c.setFillColor(INK)
    c.setFont("DrawingBold" if bold else "DrawingText", size)
    {"left": c.drawString, "center": c.drawCentredString, "right": c.drawRightString}[align](x, y, value)


def line(c, x, y, a, b, fine=False, dash=None):
    c.setStrokeColor(DIM if fine else INK)
    c.setLineWidth(.21 if fine else .38)
    c.setDash(dash or [])
    c.line(x, y, a, b)
    c.setDash([])


def rect(c, x, y, w, h, fill=False):
    c.setLineWidth(.33)
    c.setStrokeColor(INK)
    c.setFillColor(LIGHT if fill else white)
    c.rect(x, y, w, h, fill=int(fill))


def circle(c, x, y, r, fine=False):
    c.setLineWidth(.22 if fine else .33)
    c.setStrokeColor(DIM if fine else INK)
    c.circle(x, y, r)


def arrow(c, x, y, direction):
    for angle in (direction + .42, direction - .42):
        line(c, x, y, x+2.6*cos(angle), y+2.6*sin(angle), fine=True)


def dimx(c, start, end, origin, offset, label):
    line(c, start, origin, start, offset+2, True)
    line(c, end, origin, end, offset+2, True)
    line(c, start, offset, end, offset, True)
    arrow(c, start, offset, 0)
    arrow(c, end, offset, pi)
    text(c, (start+end)/2, offset+1.6, label, 3.25, align="center")


def dimy(c, x, y1, y2, offset, label):
    line(c, x, y1, offset-2, y1, True)
    line(c, x, y2, offset-2, y2, True)
    line(c, offset, y1, offset, y2, True)
    arrow(c, offset, y1, pi/2)
    arrow(c, offset, y2, -pi/2)
    c.saveState()
    c.translate(offset-1.8, (y1+y2)/2)
    c.rotate(90)
    text(c, 0, 0, label, 3.25, align="center")
    c.restoreState()


def label(c, point, elbow, name, run=40):
    x,y = point
    a,b = elbow
    line(c, x, y, a, b, True)
    arrow(c, x, y, atan2(b-y, a-x))
    line(c, a, b, a+run, b, True)
    text(c, a+1, b+1.5, name, 3.3)


def bubble(c, i, x, y, px, py):
    length = hypot(px-x, py-y)
    line(c, x+4*(px-x)/length, y+4*(py-y)/length, px, py, True)
    circle(c, x,y,4)
    text(c, x,y-1.15,str(i),3.4,True,"center")


def holes(c, positions, r=1.375):
    for x, y in positions:
        circle(c, x, y, r)
        line(c, x-r-1, y, x+r+1, y, True)
        line(c, x, y-r-1, x, y+r+1, True)


def slot(c,x,y,scale):
    r=3.5*scale
    c.setStrokeColor(INK)
    c.setLineWidth(.33)
    c.roundRect(x-r,y-2*r,2*r,4*r,r)
    line(c,x-1.5*r,y,x+1.5*r,y,True,[1,.7])


def sheet(c, number, title, note, scale):
    c.scale(mm, mm)
    rect(c, 9, 9, 402, 279)
    rect(c, 9, 9, 402, 20, True)
    for x in (244, 303, 342, 370, 391):
        line(c,x,9,x,29)
    for x,top,base in [(14,"SARDAR NAUMAN AHMED MAAN",title),(249,"DRAWING",number),
                       (308,"STATUS","DEMO"),(347,"SCALE",scale),(374,"REV","A"),(395,"SIZE","A3")]:
        text(c,x,22,top,2.8,True)
        text(c,x,14,base,3.9,True)
    text(c,18,273,title,7,True)
    text(c,18,264,note,3.7)
    line(c,18,258,402,258,True)


def notes(c,x,y,title,items):
    text(c,x,y,title,4.1,True)
    for i,item in enumerate(items,1):
        text(c,x,y-i*6.4,item,3.25)


def bom(c,x,y):
    w=131
    rect(c,x,y-7,w,7,True)
    for dx,name in [(4,"ITEM"),(22,"QTY"),(40,"PART / HARDWARE")]:
        text(c,x+dx,y-4.7,name,3.2,True)
    for index,qty,name in [(1,1,"VT-101 formed tray"),(2,2,"VT-102 wall bracket"),(3,4,"M5 x 10 hex screw"),(4,4,"M5 hex nut")]:
        py=y-(index+1)*7
        rect(c,x,py,w,7)
        for dx,value in [(6,str(index)),(24,str(qty)),(40,name)]:
            text(c,x+dx,py+2.2,value,3.25)


def quarter(c,x,y,r,angle):
    c.setStrokeColor(INK)
    c.setLineWidth(.33)
    c.arc(x-r,y-r,x+r,y+r,angle,90)


def tray_section(c,x,y,s):
    for cy,thick in [(y,0),(y+2*s,2)]:
        line(c,x+5*s,cy,x+155*s,cy)
        quarter(c,x+5*s,y+5*s,(5-thick)*s,180)
        quarter(c,x+155*s,y+5*s,(5-thick)*s,270)
        line(c,x+thick*s,y+5*s,x+thick*s,y+24*s)
        line(c,x+(160-thick)*s,y+5*s,x+(160-thick)*s,y+36*s)
    line(c,x,y+24*s,x+2*s,y+24*s)
    line(c,x+158*s,y+36*s,x+160*s,y+36*s)


def assembly(c):
    sheet(c, "VT-100", "Van shelving tray assembly", "General arrangement  /  independent sheet-metal design sample  /  millimetres", "1:2")
    x,y=44,151
    rect(c,x,y,180,80)
    for yy in (y+2.5,y+77.5):
        line(c,x,yy,x+180,yy,True)
    for xx in (x+27.5,x+152.5):
        for yy in (y+13.5,y+63.5):
            circle(c,xx,yy,2.25)
    dimx(c,x,x+180,y+80,y+16+80,"360")
    dimx(c,x+27.5,x+152.5,y+81,y+87,"250 nominal bracket pitch")
    dimy(c,x,y,y+80,x-11,"160 tray depth")
    text(c,x+90,y-6,"TOP",3.6,True,"center")
    yy=87
    rect(c,x,yy,180,12)
    for cx in (x+15,x+140):
        rect(c,cx,yy-1.5,25,1.5)
        line(c,cx,yy+12,cx,yy+18,True,[2,1])
        line(c,cx+25,yy+12,cx+25,yy+18,True,[2,1])
        rect(c,cx,yy+18,25,14)
        slot(c,cx+12.5,yy+24,.5)
    line(c,x,yy+18,x+180,yy+18)
    text(c,x+90,yy-9,"FRONT",3.6,True,"center")
    bubble(c,1,199,71,184,92)
    bubble(c,2,238,74,193,86)
    bx,by=279,190
    tray_section(c,bx,by,.5)
    line(c,bx+3,by,bx+81.5,by)
    line(c,bx+3,by-1.5,bx+81.5,by-1.5)
    line(c,bx+3,by,bx+3,by-1.5)
    for a,r in [(bx+81.5,1.5),(bx+81.5,3)]:
        quarter(c,a,by+1.5,r,270)
        line(c,a+r,by+1.5,a+r,by+32)
    line(c,bx+83,by+32,bx+84.5,by+32)
    for cx in (bx+13.5,bx+63.5):
        rect(c,cx-2.2,by+1,4.4,1.5)
        rect(c,cx-2.2,by-3.5,4.4,2)
    bubble(c,3,306,224,bx+13.5,by+2.5)
    bubble(c,4,319,177,bx+63.5,by-3.5)
    dimy(c,bx+84.5,by-1.5,by+32,bx+97,"67 overall")
    text(c,bx+41,by-23,"RIGHT SIDE",3.6,True,"center")
    bom(c,263,148)
    notes(c,262,98,"ASSEMBLY / INSTALLATION SEQUENCE",[
        "1. Deburr formed parts and place tray on both brackets.",
        "2. Align the four clearance holes. Fit screws from above.",
        "3. Fit nuts below. Use the assembled unit to transfer wall locations.",
        "4. Select anchors for the substrate and verify loads before use.",
        "Wall anchors excluded. Load, vibration and crash retention untested."
    ])
    text(c,18,39,"ORTHOGRAPHIC VIEWS   /   SIDE VIEW OFFSET   /   DIMENSIONS GOVERN",3.3,True)
    c.showPage()


def tray_detail(c):
    sheet(c,"VT-101","Formed tray","5052-H32 aluminium  /  2 mm sheet  /  millimetres  /  quantity 1", "1:2")
    x,y=44,144
    rect(c,x,y,180,80)
    for yy in (y+2.5,y+77.5):
        line(c,x,yy,x+180,yy,True)
    holes(c,[(x+i*.5,y+j*.5) for i in (55,305) for j in (27,127)])
    dimx(c,x,x+180,y+80,242,"360")
    dimx(c,x,x+27.5,y+80,231,"55")
    dimx(c,x+27.5,x+152.5,y+80,231,"250")
    dimy(c,x,y,y+80,20,"160")
    dimy(c,x,y,y+13.5,33,"27")
    dimy(c,x,y+13.5,y+63.5,33,"100")
    label(c,(x+152.5,y+13.5),(186,122),"4X Ø5.5 ±0.10")
    text(c,134,136,"TOP",3.6,True,"center")
    sx,sy=52,76
    tray_section(c,sx,sy,.5)
    dimy(c,sx,sy,sy+12,43,"24")
    dimy(c,sx+80,sy,sy+18,144,"36")
    label(c,(sx+2,sy+1),(70,103),"2X R3 INSIDE")
    text(c,92,65,"END PROFILE",3.6,True,"center")
    fx,fy=245,138
    fw,fl=360*.38,TRAY_FLAT*.38
    rect(c,fx,fy,fw,fl)
    for bend in (19+TRAY_BA/2,169+3*TRAY_BA/2):
        line(c,fx,fy+bend*.38,fx+fw,fy+bend*.38,True,[2,1])
    holes(c,[(fx+i*.38,fy+(19+TRAY_BA+j-5)*.38) for i in (55,305) for j in (27,127)],1.05)
    dimy(c,fx,fy,fy+fl,236,f"{TRAY_FLAT:.2f} REF")
    text(c,fx+fw/2,129,"FLAT PATTERN (NTS)",3.6,True,"center")
    notes(c,232,106,"FORMING / CUT FILE",[
        "2X 90° bends, same direction. R3 inside. K = 0.40 assumed.",
        "Bend allowance 5.97 mm per bend. Confirm with a test coupon.",
        "Use CUT layer for profile and holes. BEND_CENTER is reference.",
        "Deburr all cut edges. Unless noted: ±0.30 mm and ±1°.",
        "Verify formed dimensions before using any supplier flat pattern."
    ])
    c.showPage()


def bracket_detail(c):
    sheet(c,"VT-102","Formed mounting bracket","5052-H32 aluminium  /  3 mm sheet  /  millimetres  /  quantity 2", "1:1")
    x,y=66,82
    rect(c,x,y,50,163)
    line(c,x,y+157,x+50,y+157,True,[2,1])
    holes(c,[(x+25,y+k) for k in (21,121)],2.75)
    dimy(c,x,y,y+163,24,"163 formed depth")
    dimy(c,x,y,y+21,42,"21")
    dimy(c,x,y+21,y+121,42,"100")
    dimx(c,x,x+50,y+162,y+169,"50")
    dimx(c,x,x+25,y,y-8,"25")
    label(c,(x+25,y+121),(123,219),"2X Ø5.5 ±0.10")
    text(c,x+25,65,"TOP",3.6,True,"center")
    bx,by=147,115
    rect(c,bx,by,50,67)
    for yy in (by+27,by+51):
        slot(c,bx+25,yy,1)
    dimy(c,bx,by,by+27,135,"27")
    dimy(c,bx,by+27,by+51,135,"24")
    dimy(c,bx,by,by+67,126,"67")
    dimx(c,bx,bx+25,by,by-9,"25")
    label(c,(bx+25,by+51),(177,188),"2X SLOT 7 × 14")
    text(c,bx+25,94,"REAR",3.6,True,"center")
    sx,sy=16,45
    line(c,sx,sy,sx+78.5,sy)
    line(c,sx,sy-1.5,sx+78.5,sy-1.5)
    line(c,sx,sy,sx,sy-1.5)
    for rr in (1.5,3):
        quarter(c,sx+78.5,sy+1.5,rr,270)
        line(c,sx+78.5+rr,sy+1.5,sx+78.5+rr,sy+32)
    line(c,sx+80,sy+32,sx+81.5,sy+32)
    label(c,(sx+80,sy+.5),(106,47),"R3 INSIDE")
    text(c,sx+42,34,"SIDE (1:2)",3.6,True,"center")
    # Flatness frame on the horizontal mating face.
    end_x,end_y=176,64
    line(c,66,sy,124,end_y+3,True)
    arrow(c,66,sy,atan2(end_y+3-sy,58))
    line(c,124,end_y+3,end_x,end_y+3,True)
    rect(c,end_x,end_y,17,6)
    line(c,end_x+6,end_y,end_x+6,end_y+6)
    symbol=[(177,66),(180,66),(181,68),(178,68),(177,66)]
    for (x0,y0),(x1,y1) in zip(symbol,symbol[1:]):
        line(c,x0,y0,x1,y1)
    text(c,end_x+7.4,end_y+1.7,"0.5",3.2)
    fx,fy=254,145
    w,h=BRACKET_FLAT*.55,50*.55
    rect(c,fx,fy,w,h)
    line(c,fx+(157+BRACKET_BA/2)*.55,fy,fx+(157+BRACKET_BA/2)*.55,fy+h,True,[2,1])
    holes(c,[(fx+k*.55,fy+h/2) for k in (21,121)],1.5)
    for z in (24,48):
        xslot=fx+(157+BRACKET_BA+z-3)*.55
        c.setStrokeColor(INK)
        c.roundRect(xslot-7*.55,fy+h/2-3.5*.55,14*.55,7*.55,3.5*.55)
    dimx(c,fx,fx+w,fy+h,fy+h+12,f"{BRACKET_FLAT:.2f} REF")
    text(c,fx+w/2,fy-9,"FLAT PATTERN (NTS)",3.6,True,"center")
    notes(c,234,116,"FORMING / INSPECTION",[
        "1X 90° bend. R3 inside. K = 0.40 assumed.",
        "Bend allowance 6.60 mm. Confirm with a test coupon.",
        "Laser cut flat; deburr both faces before forming.",
        "Unless noted: ±0.30 mm and ±1°.",
        "Check formed flange angle, slot location, and tray fit."
    ])
    c.showPage()


def route(c, points):
    for (x,y),(a,b) in zip(points,points[1:]):
        line(c,x,y,a,b)
    x,y=points[-2]
    a,b=points[-1]
    arrow(c,a,b,atan2(y-b,x-a))


def process_sample():
    c=prepare("HX-200-cooling-loop.pdf")
    sheet(c,"HX-200","Equipment cooling loop","Flow diagram and exchanger detail  /  conceptual drafting sample  /  water loop", "NTS")
    text(c,23,244,"PROCESS FLOW DIAGRAM",4.7,True)
    for x,w,tag,name in [(33,62,"TK-201","Vented reservoir"),(119,60,"P-201","Circulation pump"),
                         (205,63,"HX-201","Air-cooled exchanger"),(297,73,"LD-201","Equipment cold plate")]:
        rect(c,x,193,w,28,True)
        text(c,x+w/2,210,tag,4.1,True,"center")
        text(c,x+w/2,200.5,name,3.4,False,"center")
    for a,b,tag in [(95,119,"L-201"),(179,205,"L-202"),(268,297,"L-203")]:
        route(c,[(a,206),(b,206)])
        text(c,(a+b)/2,211,tag,2.9,False,"center")
    route(c,[(333,193),(333,174),(64,174),(64,193)])
    arrow(c,188,174,0)
    text(c,188,167,"L-204  /  warmed return",3.6,False,"center")
    text(c,23,148,"HX-201  /  LONGITUDINAL DETAIL",4.7,True)
    rect(c,60,70,190,60)
    for x in range(80,241,8):
        line(c,x,80,x,120,True)
    for y in (86,99,112):
        line(c,73,y,238,y)
    rect(c,61,79,11,42,True)
    rect(c,238,79,11,42,True)
    route(c,[(257,112),(249,112)])
    route(c,[(61,86),(45,86)])
    for x in (105,155,205):
        route(c,[(x,61),(x,76)])
    text(c,152,53,"AIRFLOW ACROSS FIN BANK",3.3,True,"center")
    label(c,(150,113),(166,138),"FINS / TUBES")
    label(c,(242,118),(258,128),"INLET HEADER")
    text(c,26,90,"OUT",3.0,True)
    text(c,258,110,"IN",3.0,True)
    notes(c,275,98,"DRAWING NOTES",[
        "Arrows indicate normal flow direction.",
        "Exchanger detail is a symbolic cutaway.",
        "Equipment and line tags are illustrative.",
        "Design pressure, duty, and nozzle schedule",
        "are outside this concept drawing."
    ])
    c.showPage()
    c.save()


if __name__ == "__main__":
    doc=prepare("VT-100-drawing-package.pdf")
    assembly(doc)
    tray_detail(doc)
    bracket_detail(doc)
    doc.save()
    process_sample()
