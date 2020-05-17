#!/usr/bin/python3
# /content: magnetic field calculator
# /file: pygnetti.py
# /date: 20200515
# /author: Roch Schanen
# /repository: https://github.com/RochSchanen/pygnetti

# /todo: turn loops into array computations

from postscript import *

# numpy: https://numpy.org/
# float type is float64 by default <=> double
from numpy import pi, sqrt, cos, square
# from numpy import linspace
# from numpy import empty_like as empty

# scipy: https://scipy.org/
# from scipy.constants import mu_0
# we assume that mu_0 is 4*pi*1E-7

_LAST = -1

# the loop axis is aligned with oz
# the current is 1A by default
# magnetic units are in mm and µT
# radius is the bore of the coil
# layers are assumed to be compact
# the wire diameter is derived from
# the height and the number of turns
# turns alternates between n and n-1
# remember: no coil is perfectly wound
# experience shows that this model
# can't be too far from real coils
# output some results to eps files
class coil:

    def __init__(self, radius, height, turns, layers):
        self.geometry = radius, height, turns, layers
        return

    # separate I1, I2 integration
    # to allow for speed optimisation
    def getI1I2(self,
            alpha = 0.0,   # alpha
            n = 1000):     # intervals
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
    # no optimisatiom yet
    def getLoop(self,
            x = 0.0,    # position radius [mm]
            h = 0.0):   # position height [mm]
        R, H, T, L  = self.geometry
        m = square(x)+square(h)+square(R)
        b = sqrt(m*m*m) # beta
        a = 2.0*x*R/b   # alpha
        I1, I2 = self.getI1I2(a)
        bx, bz = h*R*I1/b, R/b*(R*I2-x*I1)
        return bx*1E2, bz*1E2

    # Single point calculation
    # not optimisation yet
    def getCoil(self,
            x = 0.0,    # position radius [mm]
            h = 0.0):   # position height [mm]
        # constant
        f = sqrt(3.0)/2.0
        # get geometry
        R, H, T, L  = self.geometry
        # wire diameter
        d = H/T
        # coil width
        l = d+(L-1)*d*f
        psOpen()
        psAxis()
        psSquare(+R + l/2, 0, l, H, 'right')        
        psSquare(-R - l/2, 0, l, H, 'left')        
        # loop over radiuses and positions
        rl, zl, n, Bx, Bz = [], [], 0, 0.0, 0.0
        for j in range(L):
            n = j%2 # oddness
            for i in range(T - n):
                r = +R   + d/2 + j*d*f
                z = -H/2 + d/2 + i*d + n*d/2
                rl.append(r); zl.append(z)
                bx, bz = self.getLoop(x, h-z)
                Bx += bx; Bz += bz
        psCircles(rl, zl, d/2)
        psClose()
        return Bx, Bz

if __name__ == "__main__":

    c = coil(radius = 5.0, height = 10.0, turns =13, layers = 3)
    print(f'{c.getCoil(h = 0.0, x = 0.0)}[µT]')
