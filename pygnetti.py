#!/usr/bin/python3
# /content: magnetic field calculator
# /file: pygnetti.py
# /date: 20200515
# /author: Roch Schanen
# /repository: https://github.com/RochSchanen/pygnetti

# /todo: turn loops into array computations
# /todo: split postscript output from computation
# /todo: improve activity display

from postscript import *

# numpy: https://numpy.org/
# float type is float64 by default <=> double
from numpy import pi, sqrt, cos, square
from numpy import linspace
# from numpy import empty_like as empty

from os import system

# scipy: https://scipy.org/
# from scipy.constants import mu_0
# we assume that mu_0 is 4*pi*1E-7

# the coil axis is aligned with oz
# the current is 1A by default
# magnetic units are in mm and µT
# radius is the bore of the coil
# the coil is centered on the origin
# layers are assumed to be compact
# the wire diameter is derived from
# the height and the number of turns
# the number of turns alternates
# n on even layer and n-1 on odd layers
# no coil is perfectly wound but
# empirically this model should
# not be too far off real ones
# some of the results are also
# written into eps files for display

class coil:

    def __init__(self,
            radius,  # radius [mm]
            height,  # height [mm]
            turns,   # number of turns (first layer)
            layers): # number of layers
        # record geometry
        self.geometry = radius, height, turns, layers
        d = height/turns   # get wire diameter
        f = sqrt(3.0)/2.0  # compacting factor
        # place loops:
        # rl is the radius list
        # hl is the height list
        rl, hl, n = [], [], 0
        for j in range(layers):
            n = j % 2 # determine oddness
            for i in range(turns - n):
                r = + radius   + d/2 + j*d*f
                h = - height/2 + d/2 + i*d + n*d/2
                rl.append(r)
                hl.append(h)
        # record lists
        self.r, self.h = rl, hl
        # display loop cross sections
        psCircles(rl, hl, d/2)
        # display coil former geometry
        l = d+(layers-1)*d*f # layers depth
        psSquare(+ radius + l/2, 0, l, height)
        psSquare(- radius - l/2, 0, l, height)
        return

    # elliptic integrales I1, I2
    def getI1I2(self,
            alpha = 0.0,   # alpha
            n = 100):      # intervals
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
    def getLoopField(self,
            x = 0.0,    # position radius [mm]
            z = 0.0):   # position height [mm]
        R, H, T, L  = self.geometry
        b = square(x)+square(R)+square(z)
        d = sqrt(b*b*b)
        a = 2.0*x*R/b   # alpha
        I1, I2 = self.getI1I2(a)
        bx, bz = z*R*I1/d, R/d*(R*I2-x*I1)
        return bx*1E2, bz*1E2

    # Single point calculation
    # not optimisation yet
    def getCoilField(self,
            x = 0.0,    # position radius [mm]
            z = 0.0):   # position height [mm]
        Bx, Bz = 0, 0
        for h in self.h:
            for r in self.r:
                bx, bz = self.getLoopField(x, z-h)
                Bx += bx; Bz += bz
        return Bx, Bz

if __name__ == "__main__":

    system('clear')
    fh = open('./garbage/t.txt', 'w')
    # output to postscript file
    psOpen(); 
    # draw symetry axis
    psAxis()
    # create coil
    c = coil(radius = 10.0, height = 10.0, turns =11, layers = 3)
    # plot field inside the coil    
    psStyle(width = 1.0, dash = [])
    n, m = 0, ['|','/','-','\\']
    Bx, Bz = c.getCoilField(0, 0)
    d0 = sqrt(square(Bx) + square(Bz))
    for x in linspace(0,9,3):
        for z in linspace(0, 10, 5):
            Bx, Bz = c.getCoilField(x, z)
            d = sqrt(square(Bx)+square(Bz))
            fh.write(f'z={z:+7.2f}, Bx={Bx:+.3f}µT, Bz={Bz:+.3f}µT\n')
            psVector(x, z, Bx/d0, Bz/d0)
            print(m[n%4]+'\b', end='', flush = True)
            n += 1
    # output done
    psClose(); fh.close()
