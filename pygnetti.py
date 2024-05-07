#!/usr/bin/python3
# file: pygnetti.py
# author: Roch Schanen
# date: 2020 05 15
# content: magnetic field calculator
# repository: https://github.com/RochSchanen/pygnetti

# from "https://numpy.org/"
from numpy import pi, sqrt, cos, square, absolute, linspace
from numpy import meshgrid, zeros_like, interp
# the float type is float64 by default which is equivalent to double in C

# from local modules
from ielib import file_import

# here, we assume that mu_0 is 4*pi*1E-7. This simplifies the expressions used
# for computation. One might need to change to the international definition,
# by using the scipy library: "https://scipy.org/" where the constant mu_0 can
# be found. Use then instead: "from scipy.constants import mu_0"

# The coil axis is aligned along Oz. The current is 1A by default. The units of
# length are the mm, and the magnetic units are the mT. The "radius" parameter
# represents the bore of the coil, the coil being centred on the origin. The
# layer filling is assumed to be compact (a triangular stacking from a cross
# section view). The wire diameter is derived from the height and the number of
# turns. The number of turns alternates, with n turns on even layers, and n-1
# turns on odd layers. The first layer (number 0) is always defined as even.
# No coil is ever perfectly wound, however, the compact model with alternating
# even and odd number of turns cannot be not too far from how a real coil looks
# like, especially when a small diameter wire is used. Other models should be
# easy to program.

class coil:

    def __init__(self):
        # get interpolation data 
        # see "optimise.py" for more information
        # A is alpha, J1 and J2 the normalised integrals
        data = file_import('./J1J2.txt', 2)
        if data is not None:
            self.A, self.J1, self.J2 = data 
        # compute the square root of 32 only once
        self.sqrt32 = sqrt(32)
        return

    # defines the loop positions
    # from the coil geometry
    def setupCoil(self,
            radius = 10.0,  # radius [mm]
            height =  1.0,  # height [mm]
            turns  =  1.0,  # number of turns (first layer #0, n turns)
            layers =  1.0): # number of layers (odd layers, n-1 turns)
        # record geometry
        self.geometry = radius, height, turns, layers
        d = height/turns    # get wire diameter [mm]
        f = sqrt(3.0)/2.0   # compacting factor (compute only once)
        # place loops:
        # rl is the radius list
        # hl is the height list
        rl, hl, n = [], [], 0
        for j in range(layers):
            n = j%2 # determine oddness
            for i in range(turns-n):
                r = +radius  +d/2+j*d*f
                h = -height/2+d/2+i*d+n*d/2
                hl.append(h)
                rl.append(r)
        # record lists
        self.rl, self.hl = rl, hl
        return

    # draw the coil wire positions
    def draw_wires(self, psdoc):
        # get geometry
        radius, height, turns, layers = self.geometry
        d = height/turns    # get wire diameter
        f = sqrt(3.0)/2.0   # compacting factor
        # get more geometry
        from numpy import array
        rl, hl = array(self.rl), array(self.hl)        
        # loop cross sections
        psdoc.circles(+rl, hl, d/2)
        psdoc.circles(-rl, hl, d/2)
        return        

    # draw the coil area
    def draw_area(self, psdoc):
        # get geometry
        radius, height, turns, layers = self.geometry
        d = height/turns        # get wire diameter
        f = sqrt(3.0)/2.0       # compacting factor
        l = d+(layers-1)*d*f    # layers depth
        psdoc.rectangle(+radius, -height/2, +radius+l, +height/2)
        psdoc.rectangle(-radius, -height/2, -radius-l, +height/2)
        return        

    # elliptic integrals I1, I2
    # raw numerical integration
    # there is no optimisation here
    # it is used for computing optimisation tables
    # note that these integrals diverge at -1.0 and +1.0
    def computeI1I2(self,
            alpha = 0.0,    # integration variable
            n = 100):       # number of intervals
        i1, i2 = 0.0, 0.0
        t, dt  = 0.0, 2*pi/n
        for i in range(n):
            c = cos(t)
            m = 1.0-alpha*c
            d = sqrt(m*m*m)
            i1 += c/d
            i2 += 1.0/d
            t  += dt
        return i1*dt, i2*dt

    # Single point calculation
    # no optimisation here
    # kept for debugging
    def _computeLoop(self,
            r,  # loop radius [mm]
            h,  # loop height [mm]
            x,  # point position x [mm]
            z): # point position z [mm]
        zh = z-h
        d2 = square(x)+square(r)+square(zh)
        a = 2.0*r*x/d2   # alpha
        I1, I2 = self.computeI1I2(a)
        r1d3 = r/sqrt(d2*d2*d2)
        bx, bz = zh*r1d3*I1, r1d3*(r*I2-x*I1)
        return bx/10.0, bz/10.0 # field value [mT]

    # Single point calculation
    # no optimisation
    # kept for debugging
    def _computeCoil(self,
            x = 0.0,  # point position x [mm]
            z = 0.0): # point position z [mm]
        Bx, Bz = 0, 0
        for h, r in zip(self.hl, self.rl):
            bx, bz = self._computeLoop(r, h, x, z)
            Bx += bx
            Bz += bz
        return Bx, Bz

    # here we switch the computation
    # from single points to matrices
    # of points. Also, the integrals
    # are now interpolated from tables
    # to accelerate the computing time.
    # note: by symmetry, we only need
    # to calculate one quadrant.
    # the grid is in the plan xOz.
    def setupGrid(self,
            xs,  # start x [mm]
            xe,  # stop  x [mm]
            xn,  # number of points
            zs,  # start y [mm]
            ze,  # stop  y [mm]
            zn): # number of points
        x = linspace(xs, xe, xn)
        z = linspace(zs, ze, zn)
        # build grid
        self.X, self.Z = meshgrid(x, z)
        # reset the grid fields values
        self.BX = zeros_like(self.X)
        self.BZ = zeros_like(self.Z)
        return 

    # single loop grid calculation
    # (optimised using matrix computation)
    # All upper case variables are matrices
    def addLoop(self,
            r,  # loop radius [mm]
            h): # loop height [mm]
        ZH = self.Z-h
        D2 = square(self.X)+square(ZH)+square(r)
        A = 2*r*self.X/D2  # alpha
        # interpolate J1, J2
        J1 = interp(A, self.A, self.J1)
        J2 = interp(A, self.A, self.J2)
        # calculate I1, I2
        T81A = self.sqrt32/(1.0-A)/(1.0+A)
        I1, I2 = T81A*J1, T81A*J2
        # calculate fields
        R1D3 = r/sqrt(D2*D2*D2)
        BX = ZH*R1D3*I1
        BZ = R1D3*(r*I2-self.X*I1)
        # add contribution
        self.BX += BX/10.0 # [mT]
        self.BZ += BZ/10.0 # [mT]
        # done
        return

    # full coil grid calculation
    # (optimised using matrix computation)
    def computeCoil(self):
        for h, r in zip(self.hl, self.rl):
            self.addLoop(r, h)
        return

if __name__ == "__main__":

    from pslib import document

    d = document(Size = "A6")

    # show axes
    d.graycolor(0.3)
    d.thickness(0.1)
    d.hline()
    d.vline()

    # instantiate coil
    c = coil()

    # setup coil geometry
    c.setupCoil(
        radius = 10, 
        height = 10,
        turns  = 20,
        layers = 3)

    d.graycolor(0.3)
    d.thickness(0.01)
    c.draw_wires(d)

    # d.rgbcolor(0.7, 0.0, 0.7)
    # d.thickness(0.25)
    # c.draw_area(d)

    # setup grid geometry
    c.setupGrid(
        -20.0, +20.0, 13, # min, max, points (x)
        -20.0, +20.0, 13) # min, max, points (y)
    
    # compute
    c.computeCoil()

    # setup arrow size and style
    d.define_arrow_style(1.5, 0.3)

    d.graycolor(0.8)
    d.thickness(0.1)
    d.arrows(c.X, c.Z, c.BX, c.BZ)

    # center field
    bx, bz = c.BX[6, 6], c.BZ[6, 6]
    print(f"center field = {sqrt(bx*bx+bz*bz):.3f}mT")
