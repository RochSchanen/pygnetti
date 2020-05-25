#!/usr/bin/python3
# /content: simple postscript output toolbox
# /file: postscript.py
# /date: 20200517
# /author: Roch Schanen
# /repository: https://github.com/RochSchanen/pygnetti

# todo: ?
# close file
# showpage
# %%EOF

###########

# TAB FILTER
_TAB = '    '

# ACTIVE FILE HANDLE
_FH = None

def psClose():
    global _FH
    if _FH:
        _FH.close()
    _FH = None
    return

# write block to file
def psWrite(block):
    if _FH:
        _FH.write(block.replace(_TAB,''))
        return 0
    return -1

# fast fixed formating function for floats
def f(*args):
    DATA = ''
    for x in args:
        DATA += f'{x:+08.3f} '
    return DATA.strip()

# setup colors
def psColor(r, g, b):
    BLOCK =f'{r:.3f} {g:.3f} {b:.3f} setrgbcolor\n'
    return psWrite(BLOCK)

# setup line style
def psStyle(width = None, dash = None):
    BLOCK = ''
    if width is not None: BLOCK += f'{width:.1f} setlinewidth\n'
    if dash  is not None: BLOCK += f'{dash} 0 setdash\n'
    if BLOCK:
        BLOCK = f'\n% Style\n{BLOCK}'
        return psWrite(BLOCK)
    return 0

def psArrowStyle(height = 3, ratio = 0.3):
    h, w = height/_U, height/_U*ratio
    BLOCK = f'''
    /arrow {{
    +000.000 +000.000 moveto
    {f(0,h)} 2 div rmoveto
    {f(-w)} 2 div {f(-h)} rlineto
    {f(w,0)} rlineto
    closepath fill
    }} def
    '''
    return psWrite(BLOCK)

# only work for A4 dimensions
def psCool():
    # set pastel background and light blue pen
    BLOCK = f'''
    0.85 0.95 1.0 setrgbcolor
    -292 +416 +292 +416 +292 -416 -292 -416
    moveto 3 {{lineto}} repeat closepath fill
    0.6 0.7 0.9 setrgbcolor
    '''
    return psWrite(BLOCK)

# PAGE WIDTH AND HEIGHT
# A4: 595 x 842
_W  = 595
_H  = 842

# FILE NAME
_FN = './garbage/p.ps'

# open file and write header
# todo: ? %%BeginProlog %%EndProlog
def psOpen(w = None, h = None):
    global _FH, _W, _H
    if _FH: return 0       # already open
    if w is None: w = _W   # select default width
    if h is None: h = _H   # select default height
    # open file and set global variables
    _W, _H, _FH = w, h, open(_FN, 'w')
    # build block:
    # define standard header
    # define commands
    # set default font
    # move axis to the center of the page
    BLOCK = f'''%!PS-Adobe-3.0 EPSF-3.0
    %%BoundingBox: 0 0 {_W} {_H}
    %%Creator: 
    %%Title:
    %%CreationDate:
    
    % new command
    /arrowto {{
    2 copy rlineto currentpoint stroke gsave
    translate atan -1 mul rotate arrow grestore
    }} def

    % set defaults font
    /Times-Roman 10 selectfont

    % set origin
    {_W/2:.0f} {_H/2:.0f} translate

    '''
    if psWrite(BLOCK): return -1 # error
    # default color
    if psColor(0,0,0): return -1 # error
    # default line style
    if psStyle(1, []): return -1 # error
    # default arrow style
    if psArrowStyle(): return -1 # error
    # some cool style: you may comment out
    # if you don't like it...
    if psCool(): return -1 # error
    # done
    return 0

# draw axis
def psAxis():
    BLOCK = f'''
    % Axis
    gsave 0.3 setlinewidth [1 3 12 3] 0 setdash
    newpath
    {f(-_W/2-15, 0)} moveto
    +{_W/2-15:.0f} 0 lineto
    0 -{_H/2-15:.0f} moveto
    0 +{_H/2-15:.0f} lineto
    stroke
    grestore
    '''
    return psWrite(BLOCK)

# DEFAULT SCALE (all dimensions are multiplied by SCALE)
_SCALE = 1.0

# DEFAULT UNITS (base unit is millimeter)
_U = 25.4/72/_SCALE

# dynamic change of scale
def psScale(scale):
    global _SCALE
    global _U
    _SCALE = scale
    _U = 25.4/72/_SCALE
    return        

# draw square
def psSquare(x, y, w, h, name = ''):
    x, y = x/_U, y/_U
    w, h = w/_U, h/_U
    BLOCK = f'''
    % Square: {name}
    newpath
    {x-w/2:.2f} {y+h/2:.2f} moveto
    {w:.2f} {0:.2f} rlineto
    {0:.2f} {-h:.2f} rlineto
    {-w:.2f} {0:.2f} rlineto
    closepath stroke
    '''
    return psWrite(BLOCK)

# draw circles
def psCircles(x, y, r, name = ''):
    # x, y = array(x)/_U, array(y)/_U
    r = r/_U
    N, n = len(x), 0
    DATA = ''
    for x, y in zip(x, y):
        n += 1
        DATA += f'{x/_U:+08.3f} '
        DATA += f'{y/_U:+08.3f} '
        if n < N:
            if n % 4 == 0:
                DATA += '\n'
    BLOCK = f'''
    % Circles: {name}
    newpath
    [] 0 setdash
    /circle {{ {r:.2f} 0 360 arc stroke }} def
    {DATA}
    {N} {{circle}} repeat
    '''
    return psWrite(BLOCK)

# draw vectors
def psVectors(x, y, dx, dy):
    # reshape arrays into vectors
    X  =  x.reshape(-1)
    Y  =  y.reshape(-1)
    DX = dx.reshape(-1)
    DY = dy.reshape(-1)
    # build table
    N, n, DATA = len(X), 0, ''
    for x, y, dx, dy in zip(X, Y, DX, DY):
        n += 1
        DATA += f'{dx/_U:+09.3f} {dy/_U:+09.3f} '
        DATA += f'{ x/_U:+09.3f} { y/_U:+09.3f} '
        if n < N:
            if n % 5 == 0:
                DATA += '\n'
    # build block    
    BLOCK =f'''
    % Vectors
    newpath
    [] 0 setdash
    {DATA}
    {len(X)} {{moveto arrowto}} repeat
    '''
    # done
    return psWrite(BLOCK)

    # {len(X)} {{moveto rlineto stroke}} repeat


# draw single vector
def psVector(x, y, dx, dy):
    x, y, dx, dy = x/_U, y/_U, dx/_U, dy/_U
    BLOCK = f'{dx:.2f} {dy:.2f} {x:.2f} {y:.2f}'
    BLOCK += ' moveto rlineto stroke\n'
    return psWrite(BLOCK)

# demo
if __name__ == "__main__":

    psOpen()

    # draw axis
    psAxis()

    psArrowStyle(5, 0.4)

    # draw vector
    psWrite(f'''
    100  20 moveto
    -70 -50 arrowto
    ''')

    psClose()
