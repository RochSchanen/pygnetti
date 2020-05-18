#!/usr/bin/python3
# /content: simple postscript output toolbox
# /file: postscript.py
# /date: 20200517
# /author: Roch Schanen
# /repository: https://github.com/RochSchanen/pygnetti

# from numpy import array

# TAB FILTER
_TAB = '    '

# ACTIVE FILE HANDLE
_FH = None

# close file
# showpage
# %%EOF
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
        return 1
    return 0

# PAGE WIDTH AND HEIGHT
# A4: 595 x 842
_W  = 595
_H  = 842

# FILE NAME
_FN = './garbage/p.ps'

# open file and write header
# %%BeginProlog
# %%EndProlog
def psOpen(w = None, h = None):
    global _FH, _W, _H
    if _FH: return 0 # already open
    if w is None: w = _W
    if h is None: h = _H
    _W, _H, _FH = w, h, open(_FN, 'w')
    BLOCK = f'''
    %!PS-Adobe-3.0 EPSF-3.0
    %%BoundingBox: 0 0 {_W} {_H}
    %%Creator: 
    %%Title:
    %%CreationDate:
    % Defaults
    /Times-Roman 10 selectfont
    {_W/2:.0f} {_H/2:.0f} translate
    0 0 moveto
    '''
    return psWrite(BLOCK)

def psColor(r, g, b):
    BLOCK =f'{b:.3f} {g:.3f} {b:.3f} setrgbcolor\n'
    return psWrite(BLOCK)

def psStyle(width = None, dash = None):
    BLOCK = ''
    if width is not None:
        BLOCK += f'{width:.1f} setlinewidth\n'
    if dash is not None:
        BLOCK += f'{dash} 0 setdash\n'
    if BLOCK:
        BLOCK = f'\n% Style\n{BLOCK}'
        return psWrite(BLOCK)
    return 0

# draw axis
def psAxis():
    BLOCK = f'''
    % Axis
    newpath
    -{_W/2-15:.0f} 0 moveto
    +{_W/2-15:.0f} 0 lineto
    0 -{_H/2-15:.0f} moveto
    0 +{_H/2-15:.0f} lineto
    0.3 setlinewidth
    [1 3 12 3] 0 setdash
    stroke
    '''
    return psWrite(BLOCK)

# Scale Of the drawing (from millimeters)
# _SCALE = 10 # means 10:1
_SCALE = 5  # means  5:1
# _SCALE = 2  # means  2:1
# _SCALE = 1  # means  1:1

# USER UNITS (millimeters)
_U = 25.4/72/_SCALE

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
    1.0 0.5 0.5 setrgbcolor
    closepath stroke
    '''
    return psWrite(BLOCK)

# draw circles
def psCircles(x, y, r, name = ''):
    # x, y = array(x)/_U, array(y)/_U
    r = r/_U
    N, n = len(x), 0
    POSITIONS = ''
    for x, y in zip(x, y):
        n += 1
        POSITIONS += f'{x/_U:+08.3f} '
        POSITIONS += f'{y/_U:+08.3f} '
        if n < N:
            if n % 4 == 0:
                POSITIONS += '\n'

    BLOCK = f'''
    % Circles: {name}
    newpath
    [] 0 setdash
    1.0 0.5 0.5 setrgbcolor
    /circle {{ {r:.2f} 0 360 arc stroke }} def
    {POSITIONS}
    {N} {{circle}} repeat
    '''
    return psWrite(BLOCK)

# draw vector
def psVector(x, y, dx, dy):
    x, y, dx, dy = x/_U, y/_U, dx/_U, dy/_U
    BLOCK = f'{dx:.2f} {dy:.2f} {x:.2f} {y:.2f}'
    BLOCK += ' moveto rlineto stroke\n'
    return psWrite(BLOCK)

if __name__ == "__main__":

    psOpen()
    psAxis()
    psStyle(width = 0.5, dash = [])
    psVector(0,0,1,1)
    psClose()
