#!/usr/bin/python3
# file: pslib.py
# author: Roch Schanen
# created: Tue, 7 May 2024
# content: homemade postscript package
# repository: https://github.com/RochSchanen/pygnetti
# comment: based on both postscript.py modules in postscript_dev and pygnetti

# set debug verbose flags
DEBUG = [
    # "NONE",
    # "ALL",
    # "SHOW_SIZE",    # document size
    ]

# debug flags check
def debug(*flags):
    if "NONE" in DEBUG: return False
    if "ALL"  in DEBUG: return True
    for f in flags:
        if f in DEBUG:
            # enabled
            return True
    # no valid flags
    if flags:
        return False
    # empty parameter -> always valid
    # except if 'NONE' is explicit
    return True

EOL = "\x0A"    # end-of-line
SPC = "\x20"    # space character

# returns a formatted date string
# which includes the date and the time
def fulldatetime():
    from time import strftime 
    return strftime("%A, %d %b %Y, %H:%M:%S")

# system exit with message
# easy to pass in a return line
def exitProcess(message = ""):
    from sys import exit
    if debug():
        if message:
            print(message)
        print("exiting...")
    return exit()

# A-class paper sizes class
# values are given in millimetres
class AClass():
    # build the size dictionary
    def __init__(self):
        # largest size
        d = {"A0" : (841, 1189)}
        # smaller sizes
        for i in range(10):
            W, H = d[f"A{i}"]
            d[f"A{i+1}"] = (round(H/2), W)
        # register dictionary
        self.sizes = d
        # done
        return
    # return size from name: "A0" to "A9"
    def PaperSize(self, name):
        return self.sizes[name]

# string to float rgb colour conversion
# (give "FFFFFF", returns 1.0, 1.0, 1.0)
def hexcolor(code):
    r = int(code[0:2], 16)
    g = int(code[2:4], 16)
    b = int(code[4:6], 16)
    return r/255, g/255, b/255

# fixed point formatting function
# the finest resolution is set to 0.001 point
# an arbitrary list of arguments can be used
def fix(*X):
    S = ""
    for x in X:
        s = f"{x:+08.3f}"
        S = f"{S} {s}" if S else s
    return S

# default units (points per mm)
_units = 72.0 / 25.4
# note: there is 72 points per inches
# by default in a postscript file.
# the size dimensions are expected
# to be given in points. Therefore,
# you should multiply millimetres by
# '_units' to get a value in points.

# scale and format:
def sca(*X):
    Y = []
    for x in X:
        Y.append(x*_units)
    return fix(*Y)
# note: an arbitrary length list
# of arguments can be given. each
# elements is scaled and formatted
# and returned as a tuple.

# postscript document class
class document():

    # open file, write header, setup font, and fix the origin
    def __init__(self,
            Path    = "p",  # default filename
            Size    = "A4", # default page size
            Type    = "ps", # ps or eps
        ):
        
        # initialise page counter
        self.n = 1
        
        # setup document size
        w, h = None, None
        
        # try AClass document size:
        if Size in AClass().sizes.keys(): 
            w, h = AClass().PaperSize(Size)
        
        # parse user size (for example "200x300")
        if "x" in Size.lower():
            w, h = (float(s) for s in Size.split("x"))
            # test: w, h = (float(s) for s in Size.lower.split("x"))
            
        # check parsing result
        if (w, h) == (None, None):
            exitProcess("Document size parsing failed.")
        
        # convert  and record size in points
        # (the natural units of postscript)
        self.size = w*_units, h*_units
        
        # get file handle
        fh = open(f"{Path}.{Type}", 'w')
        if fh is None:
            exitProcess(f"failed to open '{Path}'.")

        # register file handle
        self.fh = fh
        
        # write file magic (two file types available)
        magic = {
            "eps": f"%!PS-Adobe-3.0 EPSF-3.0{EOL}",
            "ps" : f"%!PS-Adobe-3.0{EOL}",
        }
        fh.write(magic[Type])
        
        # create buffer
        self.text = ""
        
        # get geometry
        w, h = self.size
        if debug("SHOW_SIZE"):
            print(f"{w:.0f} X {h:.0f} Points (as defined in the postscript header)")
            print(f"{w:.3f} X {h:.3f} Points (w, h)")
            print(f"{w/_units:.3f} X {h/_units:.3f} Millimetres (w, h)")    
            print(f"{w/72.0:.3f} X {h/72.0:.3f} Inches (w, h)")    

        # define header block
        BLOCK = f"""
        %%BoundingBox: 0 0 {w:.0f} {h:.0f}
        %%Creator:
        %%Title:
        %%CreationDate: {fulldatetime()}
        %%Pages: 001

        % set defaults font
        /Courier 12 selectfont

        % new command (arrow must be defined before usage)
        /arrowto {{
        2 copy rlineto currentpoint stroke gsave
        translate atan -1 mul rotate arrow grestore
        }} def

        %%Page: 1 1

        % --- SET ORIGIN AT PAGE CENTER ---
        {w/2:.0f} {h/2:.0f} translate
        """
        # some other font(s) available:
        # /Times-Roman 8 selectfont

        # export block
        self.write(BLOCK)

        # constants for the user
        self.LEFT, self.RIGHT  = -w/2.0/_units, +w/2.0/_units 
        self.TOP,  self.BOTTOM = +h/2.0/_units, -h/2.0/_units 
        # note: the origin (point 0 0) is at the centre of the page

        # done        
        return

    # add a new page to the document
    # (origin selection not yet implemented)
    def newpage(self, Origin = "tl"):
        
        # increment page number
        n = self.n + 1
        
        # get document size
        w, h = self.size
        
        # define newpage block
        BLOCK = f"""
        showpage

        %%Page: {n} {n}

        % --- SET ORIGIN AT PAGE CENTER ---
        {w/2:.0f} {h/2:.0f} translate
        """        
        
        # export text
        self.write(BLOCK)
        
        # update page counter
        self.n = n
        
        # done
        return        
    
    # BLOCKs are defined using the
    # following convenient formatting:
    
    # BLOCK = """
    # content line 1
    # content line 2
    # ...
    # content last line
    # """
    
    # write block to buffer
    def write(self, Block):
        for l in Block[len(EOL):].split(EOL):
            self.text += l.lstrip()+EOL
        return

    # the closing of the document
    # is automatically done on
    # deleting the class (exit):
    #
    # adjust number of pages
    # flush the buffer
    # and close the file
    def __del__(self):
        if self.fh:
            # show last page
            self.write(f"""
                showpage""")
            # update page number in header
            self.text = self.text.replace(
                f"%%Pages: 001",
                f"%%Pages: {self.n:03d}")
            # write buffer to file
            self.fh.write(self.text)
            # close file
            self.fh.close()
            # clear fh handle
            self.fh = None
        # done
        return

    def close(self):
        return self.__del__()

    ##################
    ### CROSS HAIR ###
    ##################

    # cross hair element is used for debugging
    # full width and full height should be 5 cm
    # either on the screen or paper

    # use the cross hair to calibrate the scaling
    def displayCrosshair(self, size = 50.0):

        # setup
        l, r = -size/2.0, +size/2.0
        b, t = -size/2.0, +size/2.0

        # define  block
        BLOCK = f'''
        % --- CROSSHAIR ---
        {sca(l, t, r, t, r, b)}
        {sca(l, b)}
        moveto 3 {{lineto}} repeat closepath stroke
        gsave 0.3 setlinewidth [1 3 12 3] 0 setdash
        {sca(l, 0.0)}
        {sca(r, 0.0)}
        moveto lineto stroke
        {sca(0.0, b)}
        {sca(0.0, t)}
        moveto lineto stroke
        grestore
        '''

        # export text
        self.write(BLOCK)

        # done
        return

    ##############
    ### STYLES ###
    ##############

    def thickness(self, Value):
        self.write(f"""
            % --- SET THICKNESS ---
            {sca(Value)} setlinewidth
            """)
        return

    # A value of '0.0' is white.
    # A value of '1.0' is black.
    def graycolor(self, Value):
        self.write(f"""
            % --- SET GRAYSCALE ---
            {1.0-Value:.2f} dup dup setrgbcolor
            """)
        return

    def rgbcolor(self, r, g, b):
        self.write(f"""
            % --- SET COLOR ---
            {r:.2f} {g:.2f} {b:.2f} setrgbcolor
            """)
        return

    # def dash(self, dashes = []):
    #     # default is a solid line
    #     s = f"[{sca(dashes)}]" if dashes else f"[]"
    #     self.write(f"""
    #         % --- SET DASH ---
    #         {s} 0 setdash
    #         """)
    #     return

    #############
    ### LINES ###
    #############

    def hline(self, Position = 0.0, lm = 0, rm = 0):
        # lm, rm margins are null by default
        # get geometry
        w, h = self.size
        # convert position to string
        l = fix(-w/2.0+lm*_units)
        r = fix(+w/2.0-rm*_units)
        p = sca(Position)
        # define  block
        BLOCK = f'''
        % --- SINGLE HORIZONTAL LINE ---
        {l} {p} {r} {p}
        moveto lineto stroke
        '''
        # export text
        self.write(BLOCK)
        # done
        return

    def vline(self, Position = 0.0, tm = 0, bm = 0):
        # tm, bm margins are null by default
        # get geometry
        w, h = self.size
        # convert position to string
        t = fix(+h/2.0-tm*_units)
        b = fix(-h/2.0+bm*_units)
        p = sca(Position)
        # define  block
        BLOCK = f'''
        % --- SINGLE VERTICAL LINE ---
        {p} {t} {p} {b}
        moveto lineto stroke
        '''
        # export text
        self.write(BLOCK)
        # done
        return

    def hlines(self, *Positions, lm = 0, rm = 0):
        # get geometry
        w, h = self.size
        # convert position to string
        l = fix(-w/2.0+lm*_units)
        r = fix(+w/2.0-rm*_units)
        # define  block
        BLOCK = f'''
        % --- MULTIPLE HORIZONTAL LINES ---
        {sca(*Positions)} {len(Positions)}
        {{{r} exch dup {l} exch moveto lineto stroke}} repeat
        '''
        # export text
        self.write(BLOCK)
        # done
        return

    def vlines(self, *Positions, tm = 0, bm = 0):
        # get geometry
        w, h = self.size
        # convert position to string
        t = fix(+h/2.0-tm*_units)
        b = fix(-h/2.0+bm*_units)
        # define  block
        BLOCK = f'''
        % --- MULTIPLE VERTICAL LINES ---
        {sca(*Positions)} {len(Positions)}
        {{dup {b} exch {t} moveto lineto stroke}} repeat
        '''
        # export text
        self.write(BLOCK)
        # done
        return

    def hgrid(self, Start, Stop, nLines, lm = 0, rm = 0):
        # get geometry
        w, h = self.size                # width, height
        l = -w/2.0 + lm*_units          # left
        r = +w/2.0 - rm*_units          # right
        s, e = Start, Stop              # start, stop
        i = (Stop-Start)/(nLines-1)     # interval
        # define  block
        BLOCK = f'''
        % --- MULTIPLE EQUIDISTANT HORIZONTAL LINES ---
        {sca(s-i)}
        {nLines} {{
        {sca(i)} add  dup
        {fix(r)} exch dup {fix(l)} exch
        moveto lineto
        stroke}} repeat
        pop
        '''
        # export text
        self.write(BLOCK)
        # done
        return        

    def vgrid(self, Start, Stop, nLines, tm = 0, bm = 0):
        # get geometry
        w, h = self.size                # width, height
        t, b = +h/2.0-tm, -h/2.0+bm     # top, bottom
        s, e = Start, Stop              # start, stop
        i = (Stop-Start)/(nLines-1)     # interval
        # define  block
        BLOCK = f'''
        % --- MULTIPLE EQUIDISTANT VERTICAL LINES ---
        {sca(s-i)}
        {nLines} {{
        {sca(i)} add  dup
        dup  {fix(b)} exch {fix(t)}
        moveto lineto
        stroke}} repeat
        pop
        '''
        # export text
        self.write(BLOCK)
        # done
        return        

    def line(self, x1, y1, x2, y2):
        # define  block
        BLOCK = f'''
        % --- SINGLE LINE ---
        {sca(x1, y1, x2, y2)} moveto lineto stroke
        '''
        # export text
        self.write(BLOCK)
        # done
        return                

    ###############
    ### CIRCLES ###
    ###############

    def circle(self, x, y, r):
        # define  block
        BLOCK = f'''
        % --- SINGLE CIRCLE ---
        {sca(x, y, r)} 0 360 arc stroke
        '''
        # export text
        self.write(BLOCK)
        # done
        return        

    def circles(self, x, y, r):
        # build data array
        N, n, DATA = len(x), 0, ''
        for x, y in zip(x, y):
            n += 1
            DATA += f"{sca(x, y)}"
            DATA += EOL if n % 4 == 0 else SPC
        # make block
        BLOCK = f'''
        % --- MULTIPLE CIRCLES ---
        newpath
        [] 0 setdash
        /circle {{ {sca(r)} 0 360 arc stroke }} def
        {DATA}
        {N} {{circle}} repeat
        '''
        return self.write(BLOCK)

    ##################
    ### RECTANGLES ###
    ##################

    def rectangle(self, x1, y1, x2, y2):
        # define  block
        BLOCK = f'''
        % --- SINGLE RECTANGLE ---
        {sca(x1, y1)} moveto
        {sca(x2, y1)} lineto
        {sca(x2, y2)} lineto
        {sca(x1, y2)} lineto
        {sca(x1, y1)} lineto
        stroke
        '''
        # export text
        self.write(BLOCK)
        # done
        return                

    def box(self, x1, y1, x2, y2):
        # define  block
        BLOCK = f'''
        % --- SINGLE BOX ---
        {sca(x1, y1)} moveto
        {sca(x2, y1)} lineto
        {sca(x2, y2)} lineto
        {sca(x1, y2)} lineto
        {sca(x1, y1)} lineto
        fill
        '''
        # export text
        self.write(BLOCK)
        # done
        return                

    #############
    ### ARROW ###
    #############

    def define_arrow_style(self, size = 3, ratio = 0.3):
        h, w = size, size*ratio
        BLOCK = f'''
        /arrow {{
        +000.000 +000.000 moveto
        {sca(0,h)} 2 div rmoveto
        {sca(-w)} 2 div {sca(-h)} rlineto
        {sca(w,0)} rlineto
        closepath fill
        }} def
        '''
        # done
        return self.write(BLOCK)

    def arrow(self, x, y, dx, dy):
        # build block    
        BLOCK =f"""
        % --- SINGLE VECTOR ---
        {sca( x,  y)} moveto
        {sca(dx, dy)} arrowto
        """
        # done
        return self.write(BLOCK)

    def arrows(self, x, y, dx, dy):
        # reshape arrays into 1D vectors
        X  =  x.reshape(-1)
        Y  =  y.reshape(-1)
        DX = dx.reshape(-1)
        DY = dy.reshape(-1)
        # build data array
        N, n, DATA = len(X), 0, ''
        for x, y, dx, dy in zip(X, Y, DX, DY):
            n += 1
            DATA += f'{sca(dx)} {sca(dy)} '
            DATA += f'{sca( x)} {sca( y)} '
            DATA += EOL if n % 4 == 0 else SPC
        # build block    
        BLOCK =f'''
        % --- MULTIPLE VECTORS ---
        newpath
        [] 0 setdash
        {DATA}
        {len(X)} {{moveto arrowto}} repeat
        '''
        # done
        return self.write(BLOCK)

    ############
    ### TEXT ###
    ############

    def text(self, x, y, txt):
        # define  block
        BLOCK = f'''
        % --- TEXT ---
        {sca(x, y)} moveto
        ({txt}) show
        stroke % quick fix...
        '''
        # export text
        self.write(BLOCK)
        # done
        return                

    def htext(self, x, y, txt):
        return self.text(x, y, txt)

    def vtext(self, x, y, txt):
        # define  block
        BLOCK = f'''
        % --- TEXT ---
        gsave
        {sca(x, y)} moveto
        90 rotate
        ({txt}) show
        % stroke % quick fix...
        grestore
        '''
        # export text
        self.write(BLOCK)
        # done
        return                
        # should I use 'stroke' or not? (7 lines above)           !!!

    ############
    ### META ###
    ############

    def pagelink(self, l, r, t, b, page, showborder = False):
        # get geometry
        w, h = self.size
        # border style if debug
        border = f"/Border [0 0 1]" if showborder else f"% no border"
        # define  block
        BLOCK = f'''
        % --- PAGE LINK ---
        mark
        /Rect [{sca(l, b)} {sca(r, t)}]
        {border}
        /Page {page}
        /View [/XYZ 0 {fix(h)} null]
        /Subtype /Link /ANN pdfmark
        '''
        # export text
        self.write(BLOCK)
        # done
        return                

    #############
    ### SEYES ###
    #############

    ### DRAW A SEYES PAGE ###
    def seyespage(p, lm, tm, vn, hn):

        # lm is the left margin position (red vertical line)
        # tm is the top margin (space above the first horizontal line)
        # vn is the number of vertical lines (minus the red vertical line)
        # hn is the number of thick horizontal lines

        # color for all grids
        p.rgbcolor(*hexcolor("c8c8de"))

        # thickness for sub grid
        p.thickness(0.199)

        # horizontal sub grid
        y0, n = p.TOP - tm, 4*hn + 2
        p.hgrid(y0, y0 - 2*(n-1), n)

        # thickness for main grids and vertical left margin
        p.thickness(0.398)

        # horizontal main grid
        y0, n = p.TOP - tm - 3*2, hn
        p.hgrid(y0, y0 - 8*(n-1), n)

        # vertical main grid
        x0, n = p.LEFT + lm + 8, vn
        p.vgrid(x0, x0 + 8*(n-1), n)
        
        # vertical left margin color
        p.rgbcolor(*hexcolor("f6bbcf"))
        p.vline(p.LEFT + lm)

        # done
        return

if __name__ == "__main__":

    p = document(Size = "A4")
    p.displayCrosshair()

    # done
