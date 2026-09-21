from pathlib import Path
from math import cos, sin, pi
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import portrait
from reportlab.lib.units import inch

OUT = Path(__file__).parent / 'tiny-inventors-lab-interior.pdf'
PAGE_W, PAGE_H = 8.625 * inch, 11.25 * inch
SAFE = 0.625 * inch
NAVY = HexColor('#163A6B')
BLUE = HexColor('#2687E8')
SKY = HexColor('#54C7E8')
GREEN = HexColor('#57B957')
YELLOW = HexColor('#FFD84A')
ORANGE = HexColor('#FF9B45')
PINK = HexColor('#F47EAE')
PURPLE = HexColor('#9179E8')
CREAM = HexColor('#FFF9E8')
INK = HexColor('#233A56')
PALETTE = [SKY, GREEN, YELLOW, ORANGE, PINK, PURPLE, BLUE]

pdfmetrics.registerFont(TTFont('Comic', r'C:\Windows\Fonts\comic.ttf'))
pdfmetrics.registerFont(TTFont('Comic-Bold', r'C:\Windows\Fonts\comicbd.ttf'))


def rounded(c, x, y, w, h, fill=white, stroke=None, r=12, sw=1.2):
    c.setFillColor(fill)
    c.setStrokeColor(stroke or fill)
    c.setLineWidth(sw)
    c.roundRect(x, y, w, h, r, fill=1, stroke=1 if stroke else 0)


def text(c, value, x, y, size=14, color=INK, font='Comic', align='left'):
    c.setFillColor(color)
    c.setFont(font, size)
    if align == 'center':
        c.drawCentredString(x, y, value)
    elif align == 'right':
        c.drawRightString(x, y, value)
    else:
        c.drawString(x, y, value)


def wrap(c, value, x, y, width, size=14, leading=19, color=INK, font='Comic'):
    words, line, lines = value.split(), '', []
    for word in words:
        trial = f'{line} {word}'.strip()
        if c.stringWidth(trial, font, size) <= width:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    for index, line in enumerate(lines):
        text(c, line, x, y - index * leading, size, color, font)
    return y - len(lines) * leading


def star(c, x, y, radius, fill=YELLOW):
    points = []
    for i in range(10):
        angle = pi / 2 + i * pi / 5
        r = radius if i % 2 == 0 else radius * 0.42
        points.append((x + cos(angle) * r, y + sin(angle) * r))
    path = c.beginPath(); path.moveTo(*points[0])
    for point in points[1:]: path.lineTo(*point)
    path.close(); c.setFillColor(fill); c.setStrokeColor(NAVY); c.setLineWidth(1); c.drawPath(path, fill=1, stroke=1)


def gear(c, x, y, radius, fill=ORANGE):
    c.setFillColor(fill); c.setStrokeColor(NAVY); c.setLineWidth(1.5)
    c.circle(x, y, radius, fill=1, stroke=1)
    for i in range(8):
        angle = i * pi / 4
        c.saveState(); c.translate(x + cos(angle) * radius * 1.12, y + sin(angle) * radius * 1.12); c.rotate(i * 45)
        c.roundRect(-radius * .17, -radius * .22, radius * .34, radius * .44, 2, fill=1, stroke=1); c.restoreState()
    c.setFillColor(CREAM); c.circle(x, y, radius * .3, fill=1, stroke=1)


def robot(c, x, y, scale=1, fill=SKY):
    c.setLineWidth(2); c.setStrokeColor(NAVY); c.setFillColor(white)
    c.roundRect(x - 34*scale, y - 35*scale, 68*scale, 58*scale, 12*scale, fill=1, stroke=1)
    c.setFillColor(HexColor('#0A6FC4')); c.roundRect(x - 25*scale, y - 16*scale, 50*scale, 30*scale, 8*scale, fill=1, stroke=0)
    c.setFillColor(PINK); c.circle(x - 15*scale, y - 1*scale, 3*scale, fill=1, stroke=0); c.circle(x + 15*scale, y - 1*scale, 3*scale, fill=1, stroke=0)
    c.setStrokeColor(SKY); c.setLineWidth(2*scale); c.arc(x-10*scale, y-10*scale, x+10*scale, y+7*scale, 200, 140)
    c.setStrokeColor(NAVY); c.setFillColor(fill); c.line(x, y+23*scale, x, y+39*scale); c.circle(x, y+43*scale, 5*scale, fill=1, stroke=1)
    c.setFillColor(fill); c.circle(x-38*scale, y-5*scale, 10*scale, fill=1, stroke=1); c.circle(x+38*scale, y-5*scale, 10*scale, fill=1, stroke=1)
    c.setStrokeColor(HexColor('#8B9CB3')); c.line(x-34*scale, y-10*scale, x-48*scale, y-24*scale); c.line(x+34*scale, y-10*scale, x+48*scale, y-24*scale)
    c.line(x-20*scale, y-35*scale, x-26*scale, y-55*scale); c.line(x+20*scale, y-35*scale, x+26*scale, y-55*scale)


def child(c, x, y, scale=1, shirt=PINK):
    c.setStrokeColor(NAVY); c.setLineWidth(2); c.setFillColor(HexColor('#FFD3B6'))
    c.circle(x, y+45*scale, 24*scale, fill=1, stroke=1)
    c.setFillColor(HexColor('#6A3218')); c.arc(x-27*scale, y+38*scale, x+27*scale, y+83*scale, 0, 180); c.circle(x-20*scale, y+67*scale, 10*scale, fill=1, stroke=0); c.circle(x+20*scale, y+67*scale, 10*scale, fill=1, stroke=0)
    c.setFillColor(HexColor('#258CE1')); c.roundRect(x-29*scale, y+54*scale, 58*scale, 15*scale, 5*scale, fill=1, stroke=1)
    c.setFillColor(SKY); c.circle(x-12*scale, y+61*scale, 7*scale, fill=1, stroke=1); c.circle(x+12*scale, y+61*scale, 7*scale, fill=1, stroke=1); c.setStrokeColor(NAVY); c.line(x, y+54*scale, x, y+68*scale)
    c.setFillColor(shirt); c.roundRect(x-31*scale, y-30*scale, 62*scale, 62*scale, 12*scale, fill=1, stroke=1)
    c.setFillColor(CREAM); c.circle(x-9*scale, y+48*scale, 6*scale, fill=1, stroke=1); c.circle(x+9*scale, y+48*scale, 6*scale, fill=1, stroke=1)
    c.setStrokeColor(NAVY); c.arc(x-10*scale, y+31*scale, x+10*scale, y+43*scale, 200, 140)
    c.line(x-18*scale, y-30*scale, x-24*scale, y-62*scale); c.line(x+18*scale, y-30*scale, x+24*scale, y-62*scale)


def bulb(c, x, y, scale=1, fill=YELLOW):
    c.setFillColor(fill); c.setStrokeColor(NAVY); c.setLineWidth(1.8)
    c.circle(x, y+12*scale, 22*scale, fill=1, stroke=1); c.roundRect(x-10*scale, y-16*scale, 20*scale, 15*scale, 3*scale, fill=1, stroke=1)
    c.setStrokeColor(NAVY); c.line(x-8*scale, y-21*scale, x+8*scale, y-21*scale); c.line(x-6*scale, y-26*scale, x+6*scale, y-26*scale)


def rocket(c, x, y, scale=1, fill=PINK):
    c.saveState(); c.translate(x, y); c.setStrokeColor(NAVY); c.setLineWidth(2); c.setFillColor(fill)
    c.ellipse(-20*scale, -45*scale, 20*scale, 45*scale, fill=1, stroke=1); c.setFillColor(SKY); c.circle(0, 16*scale, 9*scale, fill=1, stroke=1)
    c.setFillColor(ORANGE); c.wedge(-16*scale, -60*scale, 16*scale, -28*scale, 200, 140, fill=1, stroke=1)
    c.setFillColor(YELLOW); c.wedge(-11*scale, -54*scale, 11*scale, -33*scale, 200, 140, fill=1, stroke=1)
    c.setFillColor(fill); c.wedge(-36*scale, -20*scale, -8*scale, 18*scale, 270, 180, fill=1, stroke=1); c.wedge(8*scale, -20*scale, 36*scale, 18*scale, 90, 180, fill=1, stroke=1); c.restoreState()


def background(c, accent, page_no, title, subtitle=None, cover=False):
    c.setFillColor(HexColor('#EFFAFF')); c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setStrokeColor(BLUE); c.setLineWidth(1.5); c.roundRect(22, 22, PAGE_W-44, PAGE_H-44, 24, fill=0, stroke=1)
    c.setFillColor(accent); c.roundRect(38, PAGE_H-105, PAGE_W-76, 70, 28, fill=1, stroke=0)
    for x, y, r, col in [(52, PAGE_H-124, 8, YELLOW), (PAGE_W-52, PAGE_H-125, 8, PINK), (PAGE_W-47, 118, 6, SKY), (48, 170, 6, ORANGE)]:
        c.setFillColor(col); c.circle(x, y, r, fill=1, stroke=0)
    if cover:
        c.setFillColor(SKY); c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        for x, y, r, col in [(70, 100, 42, YELLOW), (PAGE_W-70, 150, 34, PINK), (PAGE_W-60, PAGE_H-130, 42, PURPLE), (65, PAGE_H-160, 28, GREEN)]:
            c.setFillColor(col); c.circle(x, y, r, fill=1, stroke=0)
        return
    text(c, title, SAFE, PAGE_H-76, 27, NAVY, 'Comic-Bold')
    if subtitle: text(c, subtitle, SAFE, PAGE_H-94, 11, NAVY)
    c.setFillColor(white); c.setStrokeColor(BLUE); c.setLineWidth(1.2); c.circle(PAGE_W-SAFE-16, 44, 18, fill=1, stroke=1)
    text(c, f'{page_no}', PAGE_W-SAFE-16, 38, 13, NAVY, 'Comic-Bold', 'center')
    for x, y, r, col in [(SAFE-12, PAGE_H-105, 5, YELLOW), (PAGE_W-SAFE+8, PAGE_H-105, 5, PINK)]:
        c.setFillColor(col); c.circle(x, y, r, fill=1, stroke=0)


def instruction(c, value, y):
    return wrap(c, value, SAFE, y, PAGE_W-2*SAFE, 15, 19, NAVY, 'Comic-Bold')


def cloud_panel(c, x, y, w, h, fill=white, stroke=SKY):
    c.setFillColor(fill); c.setStrokeColor(stroke); c.setLineWidth(1.8)
    c.roundRect(x, y, w, h, 24, fill=1, stroke=1)
    for cx, cy, r in [(x+28, y+h-5, 20), (x+w-32, y+h-5, 24), (x+18, y+8, 18), (x+w-18, y+8, 18)]:
        c.circle(cx, cy, r, fill=1, stroke=1)
    c.setStrokeColor(HexColor('#55BDF2')); c.setDash(4, 4); c.roundRect(x+8, y+8, w-16, h-16, 18, fill=0, stroke=1); c.setDash()


def pencil(c, x, y, scale=1, color=YELLOW):
    c.saveState(); c.translate(x, y); c.rotate(18); c.setStrokeColor(NAVY); c.setLineWidth(1); c.setFillColor(color); c.rect(-6*scale, -34*scale, 12*scale, 62*scale, fill=1, stroke=1); c.setFillColor(HexColor('#FFD3B6')); c.wedge(-6*scale, 28*scale, 6*scale, 40*scale, 0, 180, fill=1, stroke=1); c.setFillColor(NAVY); c.wedge(-3*scale, 37*scale, 3*scale, 43*scale, 0, 180, fill=1, stroke=1); c.restoreState()


def line(c, x1, y1, x2, y2, width=1.5, color=NAVY):
    c.setStrokeColor(color); c.setLineWidth(width); c.line(x1, y1, x2, y2)


def answer_line(c, label, x, y, width=170):
    text(c, label, x, y, 13, NAVY, 'Comic-Bold'); line(c, x+c.stringWidth(label, 'Comic-Bold', 13)+8, y-2, x+width, y-2, 1, NAVY)


def draw_grid(c, x, y, w, h, step=28, color=HexColor('#B8DFF2')):
    c.setStrokeColor(color); c.setLineWidth(.45)
    for ix in range(int(w/step)+1): c.line(x+ix*step, y, x+ix*step, y+h)
    for iy in range(int(h/step)+1): c.line(x, y+iy*step, x+w, y+iy*step)


def page_1(c):
    background(c, SKY, 1, '', cover=True)
    c.setStrokeColor(BLUE); c.setLineWidth(1.5); c.roundRect(22, 22, PAGE_W-44, PAGE_H-44, 24, fill=0, stroke=1)
    for x, y in [(80, 690), (PAGE_W-80, 680), (100, 120), (PAGE_W-90, 130)]: star(c, x, y, 18, YELLOW)
    bulb(c, 105, 530, 1.25); rocket(c, PAGE_W-112, 610, .75); gear(c, 92, 405, 24, ORANGE); gear(c, PAGE_W-92, 390, 30, PURPLE); pencil(c, 122, 280, .8, PINK); pencil(c, 146, 280, .8, YELLOW)
    c.setFillColor(HexColor('#FFF3A6')); c.ellipse(75, 440, PAGE_W-75, 700, fill=1, stroke=0)
    text(c, 'Tiny', PAGE_W/2, 618, 56, BLUE, 'Comic-Bold', 'center'); text(c, 'Inventors', PAGE_W/2, 550, 54, ORANGE, 'Comic-Bold', 'center'); text(c, 'Lab', PAGE_W/2, 485, 60, PURPLE, 'Comic-Bold', 'center')
    rounded(c, 130, 425, PAGE_W-260, 48, YELLOW, ORANGE, 22, 1.5); text(c, 'Build, Think & Solve', PAGE_W/2, 441, 21, NAVY, 'Comic-Bold', 'center')
    c.setFillColor(HexColor('#C98B4A')); c.rect(45, 218, PAGE_W-90, 32, fill=1, stroke=1); c.setFillColor(HexColor('#65C66C')); c.rect(330, 250, 190, 85, fill=1, stroke=1); draw_grid(c, 340, 260, 170, 65, 20, HexColor('#8CE0B4'))
    child(c, 245, 280, 1.15, ORANGE); robot(c, 430, 277, 1.0, SKY); gear(c, 335, 252, 16, BLUE); gear(c, 512, 252, 18, YELLOW)
    rounded(c, 115, 72, PAGE_W-230, 104, white, BLUE, 28, 1.5); text(c, 'Welcome, Little Inventor!', PAGE_W/2, 132, 24, NAVY, 'Comic-Bold', 'center'); text(c, 'A Fun Activity Book for Curious Kids', PAGE_W/2, 101, 15, NAVY, 'Comic-Bold', 'center'); text(c, '1', PAGE_W-SAFE-16, 38, 13, NAVY, 'Comic-Bold', 'center')


def page_2(c):
    background(c, SKY, 2, 'Welcome, Little Inventor!')
    wrap(c, 'You have a big imagination and amazing ideas! This book is filled with fun activities to help you think, imagine, solve and create.', SAFE, 650, 460, 16, 22, INK)
    cloud_panel(c, SAFE, 195, PAGE_W-2*SAFE, 385, white, SKY); child(c, 170, 455, .72, ORANGE); child(c, 245, 455, .72, PINK); robot(c, PAGE_W-160, 455, .72, SKY); bulb(c, PAGE_W/2, 355, 1.1); pencil(c, PAGE_W/2-90, 275, .7, YELLOW); gear(c, PAGE_W/2+95, 280, 22, ORANGE)
    text(c, 'What will you invent today?', PAGE_W/2, 235, 22, NAVY, 'Comic-Bold', 'center')
    for i in range(4): line(c, 145, 205-i*32, PAGE_W-145, 205-i*32, 1, HexColor('#9AB7D0'))


def page_3(c):
    background(c, PINK, 3, 'All About Me')
    instruction(c, 'Draw yourself as an inventor!', 655)
    rounded(c, SAFE, 245, PAGE_W-2*SAFE, 355, white, PINK, 18, 2); child(c, PAGE_W-125, 170, .55, SKY)
    answer_line(c, 'My Inventor Name:', SAFE, 195, 285); answer_line(c, 'My Age:', 345, 195, 450); answer_line(c, 'I want to invent:', SAFE, 145, PAGE_W-80)


def object_row(c, y, label, kind, count=5):
    text(c, label, SAFE, y+18, 15, NAVY, 'Comic-Bold')
    start = SAFE + 145
    for i in range(count):
        if kind == 'bulb': bulb(c, start+i*50, y, .42)
        elif kind == 'gear': gear(c, start+i*50, y+5, 13, PALETTE[i%len(PALETTE)])
        elif kind == 'robot': robot(c, start+i*50, y+14, .22, PALETTE[i%len(PALETTE)])
        else: rocket(c, start+i*50, y+8, .3, PALETTE[i%len(PALETTE)])
    rounded(c, PAGE_W-SAFE-54, y-11, 54, 38, white, NAVY, 8, 1.5)


def page_4(c):
    background(c, YELLOW, 4, "Let's Count!"); instruction(c, 'Count the objects and write the number.', 655)
    for y, label, kind, count in [(570,'Lightbulbs','bulb',4),(465,'Gears','gear',6),(360,'Robots','robot',3),(255,'Rockets','rocket',5)]: object_row(c,y,label,kind,count)


def page_5(c):
    background(c, PURPLE, 5, 'Shape Shifters'); instruction(c, 'Identify the shapes and draw one invention using them.', 655)
    shapes = [('Circle', 'circle'), ('Square', 'square'), ('Triangle', 'triangle'), ('Rectangle', 'rect'), ('Star', 'star'), ('Heart', 'heart')]
    for i, (label, shape) in enumerate(shapes):
        x = SAFE + (i%3)*150; y = 565 - (i//3)*95; rounded(c,x,y,112,66,white,PURPLE,12,1.3); text(c,label,x+56,y+12,12,NAVY,'Comic-Bold','center')
        c.setFillColor(PALETTE[i]); c.setStrokeColor(NAVY); c.setLineWidth(1.3)
        if shape == 'circle': c.circle(x+56,y+41,14,fill=1,stroke=1)
        elif shape == 'square': c.rect(x+42,y+27,28,28,fill=1,stroke=1)
        elif shape == 'rect': c.rect(x+35,y+31,42,21,fill=1,stroke=1)
        elif shape == 'triangle': c.wedge(x+38,y+24,x+74,y+57,0,180,fill=1,stroke=1)
        elif shape == 'star': star(c,x+56,y+42,17,PALETTE[i])
        else: c.circle(x+56,y+40,15,fill=1,stroke=1)
    rounded(c, SAFE, 105, PAGE_W-2*SAFE, 220, white, PURPLE, 18, 2); text(c, 'My invention:', SAFE+18, 295, 15, NAVY, 'Comic-Bold'); gear(c, PAGE_W-130, 160, 24, ORANGE); robot(c, PAGE_W-185, 175, .45, SKY)


def page_6(c):
    background(c, ORANGE, 6, 'Find the Differences'); instruction(c, 'Look carefully at the two pictures. Find and circle 5 differences.', 655)
    for x in [SAFE, PAGE_W/2+12]:
        rounded(c,x,300,230,285,white,ORANGE,16,1.5); text(c,'WORKSHOP',x+115,560,13,NAVY,'Comic-Bold','center'); gear(c,x+55,500,22,ORANGE); bulb(c,x+160,500,.75); robot(c,x+112,390,.62,SKY); line(c,x+35,345,x+195,345,2,NAVY); rocket(c,x+190,365,.3,PINK)
    # Five controlled differences: right panel omits gear, changes bulb fill, adds star, removes rocket, changes workshop line.
    c.setFillColor(CREAM); c.circle(PAGE_W/2+12+55,500,22,fill=1,stroke=0); bulb(c,PAGE_W/2+12+160,500,.75,PINK); star(c,PAGE_W/2+12+180,455,10,YELLOW); line(c,PAGE_W/2+12+35,345,PAGE_W/2+12+195,345,4,NAVY)
    rounded(c, SAFE, 195, PAGE_W-2*SAFE, 62, white, ORANGE, 12, 1.2); text(c, 'I found ______ differences!', PAGE_W/2, 220, 17, NAVY, 'Comic-Bold', 'center')


def page_7(c):
    background(c, GREEN, 7, 'Maze Time'); instruction(c, 'Help the invention reach its goal!', 655)
    x,y,w,h=SAFE,145,PAGE_W-2*SAFE,420; rounded(c,x,y,w,h,white,GREEN,16,1.5)
    # solvable serpentine maze
    c.setStrokeColor(NAVY); c.setLineWidth(3)
    walls=[(x+60,y+40,x+60,y+h-40),(x+140,y+40,x+140,y+h-100),(x+220,y+100,x+220,y+h-40),(x+300,y+40,x+300,y+h-100),(x+380,y+100,x+380,y+h-40)]
    for line_data in walls: c.line(*line_data)
    for xx in [x+60,x+140,x+220,x+300,x+380]:
        gap_y = y+80 if xx in [x+60,x+220,x+380] else y+h-80
        c.setFillColor(white); c.rect(xx-3,gap_y-24,6,48,fill=1,stroke=0)
    text(c,'START',x+14,y+20,11,NAVY,'Comic-Bold'); robot(c,x+30,y+42,.3,SKY); text(c,'GOAL',x+w-62,y+h-25,11,NAVY,'Comic-Bold'); star(c,x+w-32,y+h-55,15,YELLOW); text(c,'Trace the path!',PAGE_W/2,105,16,NAVY,'Comic-Bold','center')


def page_8(c):
    background(c, BLUE, 8, 'Color by Number'); instruction(c, 'Color the rocket using the key.', 655)
    key=[('1 = Red', HexColor('#EF5350')),('2 = Blue', BLUE),('3 = Yellow',YELLOW),('4 = Green',GREEN),('5 = Orange',ORANGE)]
    for i,(label,col) in enumerate(key): rounded(c,SAFE+i*85,590,76,30,white,col,8,1.2); text(c,label,SAFE+i*85+38,600,10,NAVY,'Comic-Bold','center')
    rocket(c,PAGE_W/2,350,2.0,PINK); text(c,'1',PAGE_W/2,405,18,NAVY,'Comic-Bold','center'); text(c,'2',PAGE_W/2-20,348,18,NAVY,'Comic-Bold','center'); text(c,'3',PAGE_W/2+22,348,18,NAVY,'Comic-Bold','center'); text(c,'4',PAGE_W/2-42,265,18,NAVY,'Comic-Bold','center'); text(c,'5',PAGE_W/2+42,265,18,NAVY,'Comic-Bold','center');
    for x in [110, PAGE_W-110]: star(c,x,200,15,YELLOW)


def page_9(c):
    background(c, PINK, 9, 'Draw & Create'); instruction(c, 'Finish the invention drawing and color it.', 655)
    rounded(c,SAFE,175,PAGE_W-2*SAFE,385,white,PINK,18,1.5); bulb(c,SAFE+130,420,1.2); robot(c,SAFE+205,350,.75,SKY); text(c,'•  •  •  •  •',SAFE+275,420,22,PINK,'Comic-Bold'); text(c,'Continue the dotted guide!',PAGE_W/2,210,15,NAVY,'Comic-Bold','center'); star(c,PAGE_W-120,315,15,YELLOW)


def page_10(c):
    background(c, SKY, 10, 'Match the Pairs'); instruction(c, 'Draw a line to match each object to its partner.', 655)
    left=[('lightbulb',bulb),('gear',gear),('wrench',None),('battery',None),('magnet',None)]; right=['gear','magnet','lightbulb','battery','wrench'];
    for i,(label,fn) in enumerate(left):
        y=555-i*78; rounded(c,SAFE,y-18,160,48,white,SKY,10,1.2); text(c,label.title(),SAFE+78,y-2,13,NAVY,'Comic-Bold','center')
        if fn: fn(c,SAFE+24,y+5,.32 if label=='lightbulb' else .45,PALETTE[i]) if label=='lightbulb' else fn(c,SAFE+24,y+5,12,PALETTE[i])
    for i,label in enumerate(right):
        y=555-i*78; rounded(c,PAGE_W-SAFE-160,y-18,160,48,white,SKY,10,1.2); text(c,label.title(),PAGE_W-SAFE-82,y-2,13,NAVY,'Comic-Bold','center')
    text(c,'Connect matching pairs without crossing lines.',PAGE_W/2,110,14,NAVY,'Comic-Bold','center')


def word_search(c):
    grid=[list('ROCKET'),list('SCIENCE'),list('BUILDX'),list('SOLARG'),list('GEARID'),list('TOOLSZ'),list('IDEAXY')]
    x0,y0=SAFE+18,270; cell=40
    for r,row in enumerate(grid):
        for col,ch in enumerate(row): rounded(c,x0+col*cell,y0+(6-r)*cell,cell,cell,white,SKY,3,.8); text(c,ch,x0+col*cell+20,y0+(6-r)*cell+12,16,NAVY,'Comic-Bold','center')
    words=['ROBOT','ROCKET','SCIENCE','IDEA','TOOLS','BUILD','SOLAR','GEAR']
    for i,word in enumerate(words): text(c,word,SAFE+(i%4)*95,220-(i//4)*25,13,NAVY,'Comic-Bold')


def page_11(c):
    background(c, SKY, 11, 'Inventor Word Search'); instruction(c, 'Find the hidden words. Words may go across or down.', 655); word_search(c); robot(c,PAGE_W-115,500,.5,ORANGE)


def page_12(c):
    background(c, YELLOW, 12, 'How Many?'); instruction(c, 'Count and write the number.', 655)
    for i,(label,kind,count) in enumerate([('Rockets','rocket',4),('Planets','planet',3),('Stars','star',7),('Gears','gear',5),('Lightbulbs','bulb',6)]):
        y=570-i*85; text(c,label,SAFE,y,14,NAVY,'Comic-Bold');
        for j in range(count):
            xx=SAFE+115+j*36
            if kind=='rocket': rocket(c,xx,y+7,.22,PALETTE[j%7])
            elif kind=='star': star(c,xx,y+5,11,PALETTE[j%7])
            elif kind=='gear': gear(c,xx,y+5,10,PALETTE[j%7])
            elif kind=='bulb': bulb(c,xx,y+3,.25,PALETTE[j%7])
            else: c.setFillColor(PALETTE[j%7]); c.circle(xx,y+5,12,fill=1,stroke=1)
        rounded(c,PAGE_W-SAFE-45,y-9,45,28,white,NAVY,7,1.2)


def page_13(c):
    background(c, PURPLE, 13, 'Finish the Pattern'); instruction(c, 'Look at the pattern and draw the next shape.', 655)
    rows=[(['star','circle','star','circle'],'?'),(['gear','rocket','gear','rocket'],'?'),(['triangle','square','triangle','square'],'?')]
    for r,(items,ans) in enumerate(rows):
        y=520-r*120; rounded(c,SAFE,y-25,PAGE_W-2*SAFE,65,white,PURPLE,10,1.2)
        for i,item in enumerate(items):
            xx=SAFE+52+i*62
            if item=='star': star(c,xx,y+8,18,YELLOW)
            elif item=='circle': c.setFillColor(SKY); c.circle(xx,y+8,18,fill=1,stroke=1)
            elif item=='gear': gear(c,xx,y+8,17,ORANGE)
            elif item=='rocket': rocket(c,xx,y+12,.32,PINK)
            elif item=='triangle': c.setFillColor(GREEN); c.wedge(xx-20,y-12,xx+20,y+28,0,180,fill=1,stroke=1)
            else: c.setFillColor(BLUE); c.rect(xx-18,y-10,36,36,fill=1,stroke=1)
        text(c,'?',SAFE+52+4*62,y-2,28,NAVY,'Comic-Bold','center')
    text(c,'Draw the next shape in each row!',PAGE_W/2,130,16,NAVY,'Comic-Bold','center')


def page_14(c):
    background(c, GREEN, 14, 'Build a Robot'); instruction(c, 'Design your own robot.', 655); rounded(c,SAFE,190,PAGE_W-2*SAFE,395,white,GREEN,18,1.5); robot(c,PAGE_W/2,420,.9,HexColor('#D8F3FF')); gear(c,SAFE+45,220,18,ORANGE); gear(c,PAGE_W-SAFE-45,220,18,PURPLE); answer_line(c,"My Robot's Name:",SAFE,145,300); answer_line(c,'My robot can:',345,145,470)


def page_15(c):
    background(c, BLUE, 15, 'Design a Rocket'); instruction(c, 'Create a rocket and give it a name!', 655); rounded(c,SAFE,185,PAGE_W-2*SAFE,405,white,BLUE,18,1.5); rocket(c,PAGE_W/2,420,.9,PINK); star(c,130,500,12,YELLOW); star(c,PAGE_W-130,530,14,YELLOW); answer_line(c,"My Rocket's Name:",SAFE,145,300); answer_line(c,'My Rocket Can:',345,145,470)


def drawing_page(c, page_no, title, instr, accent, prompts, decor='house'):
    background(c,accent,page_no,title); instruction(c,instr,655); rounded(c,SAFE,250,PAGE_W-2*SAFE,320,white,accent,18,1.5)
    if decor=='house':
        c.setFillColor(PINK); c.setStrokeColor(NAVY); c.setLineWidth(2); c.rect(PAGE_W/2-90,355,180,125,fill=1,stroke=1); p=c.beginPath(); p.moveTo(PAGE_W/2-115,480); p.lineTo(PAGE_W/2,555); p.lineTo(PAGE_W/2+115,480); p.close(); c.setFillColor(ORANGE); c.drawPath(p,fill=1,stroke=1); robot(c,PAGE_W-130,295,.35,SKY)
    elif decor=='nature':
        c.setFillColor(GREEN); c.circle(160,420,65,fill=1,stroke=1); c.setFillColor(ORANGE); c.rect(150,300,20,100,fill=1,stroke=1); star(c,PAGE_W-150,480,18,YELLOW); c.setFillColor(SKY); c.circle(PAGE_W-130,350,45,fill=1,stroke=0)
    elif decor=='water': bulb(c,PAGE_W/2,430,1.3,SKY); c.setFillColor(BLUE); c.ellipse(PAGE_W/2-70,330,PAGE_W/2+70,370,fill=1,stroke=1)
    elif decor=='solar': c.setFillColor(YELLOW); c.circle(PAGE_W/2,470,45,fill=1,stroke=1); c.setFillColor(BLUE); c.rect(PAGE_W/2-75,320,PAGE_W/2+75-(PAGE_W/2-75),70,fill=1,stroke=1); robot(c,PAGE_W/2,275,.35,ORANGE)
    elif decor=='alien': c.setFillColor(GREEN); c.circle(PAGE_W/2,430,40,fill=1,stroke=1); c.setFillColor(white); c.circle(PAGE_W/2-15,440,10,fill=1,stroke=1); c.circle(PAGE_W/2+15,440,10,fill=1,stroke=1); rocket(c,PAGE_W-130,330,.5,PINK)
    for i,prompt in enumerate(prompts): answer_line(c,prompt,SAFE,195-i*30,PAGE_W-SAFE)


def page_16(c): drawing_page(c,16,'Build a Dream House','Draw your dream invention house.',PINK,['Special Feature:','My house can:'])
def page_21(c): drawing_page(c,21,'Invent for Nature','Design something that helps nature.',GREEN,['My invention helps:'], 'nature')
def page_22(c): drawing_page(c,22,'Water Saver','Create a water-saving invention.',SKY,['My Idea:','How it works:'],'water')
def page_23(c): drawing_page(c,23,'Solar Power Idea','Design a sun-powered invention.',YELLOW,['My Idea:','It uses sunlight to:'],'solar')
def page_24(c): drawing_page(c,24,'Alien Invention','Imagine an invention for space!',PURPLE,['My Invention:'],'alien')


def page_17(c):
    background(c, ORANGE, 17, 'Gear Match'); instruction(c, 'Match the gears that fit together.', 655)
    for i in range(4):
        gear(c,SAFE+70+i*115,500,22,[ORANGE,PINK,SKY,GREEN][i])
        gear(c,PAGE_W-SAFE-70-i*115,300, [14,22,18,26][i], [GREEN,ORANGE,PINK,SKY][i])
    text(c,'Draw lines between matching sizes and shapes.',PAGE_W/2,150,15,NAVY,'Comic-Bold','center')


def page_18(c):
    background(c, SKY, 18, 'Which Tool?'); instruction(c, 'Choose the right tool for each job.', 655)
    jobs=['Tighten a screw','Cut paper','Measure length','Paint a wall','Fix a nut']; tools=['screwdriver','scissors','ruler','paintbrush','wrench']
    for i,(job,tool) in enumerate(zip(jobs,tools)):
        y=565-i*75; rounded(c,SAFE,y-20,260,46,white,SKY,9,1.2); text(c,job,SAFE+12,y-3,13,NAVY,'Comic-Bold'); rounded(c,PAGE_W-SAFE-170,y-20,170,46,white,BLUE,9,1.2); text(c,tool.title(),PAGE_W-SAFE-85,y-3,12,NAVY,'Comic-Bold','center')


def page_19(c):
    background(c, PURPLE, 19, 'Mystery Machine'); instruction(c, "What's missing? Choose the missing part.", 655)
    rounded(c,SAFE,355,PAGE_W-2*SAFE,225,white,PURPLE,18,1.5); gear(c,PAGE_W/2-60,450,35,ORANGE); bulb(c,PAGE_W/2+70,450,1.0,SKY); text(c,'?',PAGE_W/2,380,48,PINK,'Comic-Bold','center')
    for i,label in enumerate(['A  Gear','B  Rocket','C  Battery','D  Star']): rounded(c,SAFE+i*112,235,98,60,white,PURPLE,10,1.2); text(c,label,SAFE+i*112+49,260,12,NAVY,'Comic-Bold','center')


def page_20(c):
    background(c, BLUE, 20, 'Mini Science Lab'); instruction(c, 'Try this simple experiment! What happens when you put a small object in water?', 655)
    rounded(c,SAFE,350,PAGE_W-2*SAFE,220,white,BLUE,18,1.5); c.setFillColor(SKY); c.ellipse(PAGE_W/2-105,365,PAGE_W/2+105,450,fill=1,stroke=1); c.setFillColor(ORANGE); c.circle(PAGE_W/2,470,15,fill=1,stroke=1); text(c,'Observe carefully!',PAGE_W/2,315,17,NAVY,'Comic-Bold','center')
    answer_line(c,'It:',SAFE,250,260); text(c,'floats / sinks',SAFE+105,250,13,NAVY); answer_line(c,'What did you observe?',SAFE,205,360); answer_line(c,'What do you think happened?',SAFE,160,450)


def page_25(c):
    background(c, ORANGE, 25, 'Tiny Problem, Big Idea'); instruction(c,'Choose an everyday problem and solve it with an invention.',655); child(c,PAGE_W-135,465,.65,PINK); bulb(c,SAFE+90,500,1.1,YELLOW)
    answer_line(c,'The Problem:',SAFE,440,470); answer_line(c,'My Solution:',SAFE,375,470); answer_line(c,'It helps by:',SAFE,310,470); rounded(c,SAFE,105,PAGE_W-2*SAFE,160,white,ORANGE,18,1.5)


def page_26(c):
    background(c, GREEN, 26, 'Inventor Logic Challenge'); instruction(c,'Solve each puzzle. Think like an inventor!',655)
    qs=['1. Circle, Triangle, Circle, Triangle, ___','2. Which does not belong? Apple / Banana / Carrot / Gear','3. 2, 4, 6, 8, ___','4. Which is heavier? A paperclip or a toolbox?']
    for i,q in enumerate(qs): rounded(c,SAFE,535-i*90,PAGE_W-2*SAFE,55,white,GREEN,10,1.2); text(c,q,SAFE+16,555-i*90,13,NAVY,'Comic-Bold'); line(c,PAGE_W-SAFE-90,545-i*90,PAGE_W-SAFE-18,545-i*90,1,NAVY)


def page_27(c):
    background(c, PINK, 27, 'Crack the Code'); instruction(c,'Use the code to find the secret message.',655)
    codes=[('star','A'),('heart','B'),('triangle','C'),('circle','D'),('square','E')]
    for i,(shape,letter) in enumerate(codes):
        x=SAFE+i*85; y=570; rounded(c,x,y,70,48,white,PINK,8,1.2); text(c,shape.title(),x+35,y+25,10,NAVY,'Comic-Bold','center'); text(c,letter,x+35,y+8,12,PINK,'Comic-Bold','center')
    text(c,'Secret message:',SAFE,475,15,NAVY,'Comic-Bold');
    for i in range(9): rounded(c,SAFE+i*50,420,38,38,white,PINK,7,1.1)
    text(c,'Your Turn!',PAGE_W/2,350,19,NAVY,'Comic-Bold','center'); rounded(c,SAFE,160,PAGE_W-2*SAFE,150,white,PINK,18,1.5); text(c,'Create your own coded message.',PAGE_W/2,280,15,NAVY,'Comic-Bold','center')


def page_28(c):
    background(c, BLUE, 28, "Inventor's Blueprint"); instruction(c,'Draw a complete invention with labels.',655); rounded(c,SAFE,165,PAGE_W-2*SAFE,410,HexColor('#E8F7FF'),BLUE,18,1.5); draw_grid(c,SAFE+10,175,PAGE_W-2*SAFE-20,390,24); text(c,'Invention Name:',SAFE,130,13,NAVY,'Comic-Bold'); line(c,SAFE+100,128,PAGE_W-SAFE,128); text(c,'What does it do?',SAFE,95,13,NAVY,'Comic-Bold'); line(c,SAFE+105,93,PAGE_W-SAFE,93)


def page_29(c):
    background(c, YELLOW, 29, 'My Big Idea'); instruction(c,'Describe your invention.',655); bulb(c,PAGE_W-125,535,1.0,YELLOW)
    fields=['My invention is called:','It solves:','How it works:','Who can use it:','Why it is useful:']
    for i,field in enumerate(fields): answer_line(c,field,SAFE,550-i*75,PAGE_W-SAFE)


def page_30(c):
    background(c, PURPLE, 30, 'Inventor Challenge'); instruction(c,'Complete all 5 steps!',655); child(c,PAGE_W-125,445,.65,SKY); star(c,SAFE+65,530,20,YELLOW)
    checks=['Choose a problem','Think of an idea','Draw your invention','Give it a name','Explain how it works']
    for i,item in enumerate(checks):
        y=510-i*62; rounded(c,SAFE,y-18,25,25,white,PURPLE,5,1.2); text(c,item,SAFE+45,y-1,17,NAVY,'Comic-Bold')
    rounded(c,SAFE,100,PAGE_W-2*SAFE,70,white,PURPLE,18,1.5); text(c,'YOU CAN DO IT!',PAGE_W/2,125,25,PURPLE,'Comic-Bold','center'); star(c,PAGE_W-100,205,20,YELLOW)


def page_31(c):
    background(c, YELLOW, 31, 'Inventor Certificate')
    cloud_panel(c, SAFE, 175, PAGE_W-2*SAFE, 390, white, ORANGE)
    text(c, 'CONGRATULATIONS!', PAGE_W/2, 500, 29, ORANGE, 'Comic-Bold', 'center'); text(c, 'This certificate is proudly awarded to', PAGE_W/2, 455, 15, NAVY, 'Comic-Bold', 'center')
    line(c, 150, 405, PAGE_W-150, 405, 1.5, NAVY); text(c, 'Junior Inventor', PAGE_W/2, 350, 24, BLUE, 'Comic-Bold', 'center'); wrap(c, 'For creativity, curiosity and amazing ideas!', PAGE_W/2-150, 305, 300, 15, 18, NAVY, 'Comic-Bold')
    star(c, 120, 465, 20, YELLOW); star(c, PAGE_W-120, 465, 20, PINK); gear(c, 130, 250, 22, ORANGE); gear(c, PAGE_W-130, 250, 22, PURPLE); child(c, 245, 205, .55, ORANGE); robot(c, 405, 215, .52, SKY)
    answer_line(c, 'Date:', SAFE+20, 215, 205); answer_line(c, 'Signature:', 365, 215, PAGE_W-SAFE)


def page_32(c):
    background(c, PINK, 32, 'Great Job, Inventor!')
    text(c, 'Great Job, Inventor!', PAGE_W/2, 610, 32, NAVY, 'Comic-Bold', 'center'); text(c, 'You did it!', PAGE_W/2, 570, 24, ORANGE, 'Comic-Bold', 'center')
    rocket(c, 112, 535, .55, PINK); gear(c, PAGE_W-105, 535, 24, YELLOW); star(c, 105, 410, 18, YELLOW); star(c, PAGE_W-110, 405, 18, SKY)
    child(c, 245, 300, .9, ORANGE); robot(c, 410, 300, .82, SKY); bulb(c, PAGE_W/2, 450, .8, YELLOW); gear(c, 325, 235, 17, GREEN)
    cloud_panel(c, SAFE, 75, PAGE_W-2*SAFE, 170, white, PINK); text(c, 'You explored.  You created.', PAGE_W/2, 205, 17, NAVY, 'Comic-Bold', 'center'); text(c, 'You solved.  You imagined.  You invented.', PAGE_W/2, 178, 15, NAVY, 'Comic-Bold', 'center'); text(c, 'Keep dreaming. Keep creating. Keep exploring.', PAGE_W/2, 135, 16, PURPLE, 'Comic-Bold', 'center'); answer_line(c, 'My favorite activity was:', SAFE+55, 102, PAGE_W-SAFE-55)


PAGES = [page_1,page_2,page_3,page_4,page_5,page_6,page_7,page_8,page_9,page_10,page_11,page_12,page_13,page_14,page_15,page_16,page_17,page_18,page_19,page_20,page_21,page_22,page_23,page_24,page_25,page_26,page_27,page_28,page_29,page_30,page_31,page_32]


def build():
    c = Canvas(str(OUT), pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    c.setTitle('Tiny Inventors Lab - 32 Page Interior')
    for page in PAGES:
        page(c)
        c.showPage()
    c.save()
    print(f'Created {OUT}')
    print(f'Pages: {len(PAGES)} | Size: {PAGE_W/72:.3f} x {PAGE_H/72:.3f} inches')


if __name__ == '__main__':
    build()
