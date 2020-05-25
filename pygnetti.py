#!/usr/bin/python3
# /content: magnetic field calculator
# /file: pygnetti.py
# /date: 20200515
# /author: Roch Schanen
# /repository: https://github.com/RochSchanen/pygnetti

# numpy: https://numpy.org/
import numpy as np
# float type is float64 by default 
# is equivalent to double in C
from numpy import pi, sqrt, cos, square, absolute
from numpy import linspace

from postscript import *
import toolbox as tb

# here, we assume that mu_0 is 4*pi*1E-7
# One might need to change to the new
# international definition in the futur:
# scipy: https://scipy.org/
# from scipy.constants import mu_0

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
# the first layer (#0) is defined as even
# no coil is ever perfectly wound
# empirically this model should
# not be too far off real world manufacture

class coil:

    def __init__(self):
        # get data for interpolation
        # this is the optimisation part
        # see "optimise.py" for more informations
        data = tb.Import('./J1J2.txt')
        if data: self.A, self.J1, self.J2 = data
        self.sqrt32 = sqrt(32)
        return

    # defines the loop positions
    # from the coil geometry
    def setupCoil(self,
            radius = 10.0,  # radius [mm]
            height =  1.0,  # height [mm]
            turns  =  1.0,  # number of turns (first layer)
            layers =  1.0): # number of layers
        # save geometry
        self.geometry = radius, height, turns, layers
        d = height/turns    # get wire diameter [mm]
        f = sqrt(3.0)/2.0   # compacting factor
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

    # output coil geometry to the
    # postscript file including
    # the wires positions.
    def psCoil(self):
        # get geometry
        radius, height, turns, layers = self.geometry
        d = height/turns    # get wire diameter
        f = sqrt(3.0)/2.0   # compacting factor
        # get more geometry
        rl, hl = self.rl, self.hl        
        # loop cross sections
        psCircles(rl, hl, d/2)
        # coil former geometry
        l = d+(layers-1)*d*f # layers depth
        psSquare(+radius+l/2, 0, l, height)
        psSquare(-radius-l/2, 0, l, height)
        return        

    # elliptic integrales I1, I2
    # brute numerical intergration
    # no optimisation here
    # used for computing tables
    # integrales diverge at -1.0 and +1.0
    def computeI1I2(self,
            alpha = 0.0, # the integration variable
            n = 100):    # intervals of integration
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
    # no optimisatiom here
    # kept as a debugging tool
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
        return bx*1E2, bz*1E2 # field value [µT]

    # Single point calculation
    # no optimisatiom
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
    # from a single point to matrix
    # of points. Also, the integrale
    # values are now interpolated
    # from tables which reduces
    # the computing time.

    # by symmetry, we only need
    # to calculate one quadrant:
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
        self.shape = xn, zn
        self.X, self.Z = np.meshgrid(x, z)
        # reset the grid fields values
        self.BX = np.zeros_like(self.X)
        self.BZ = np.zeros_like(self.Z)
        return 

    # grid calculation
    # optimised for speed
    # upper case variables are matrices
    def addLoop(self,
            r,  # loop radius [mm]
            h): # loop height [mm]
        ZH = self.Z-h
        D2 = square(self.X)+square(ZH)+square(r)
        A = 2*r*self.X/D2  # alpha
        # interpolate J1, J2
        J1 = np.interp(A, self.A, self.J1)
        J2 = np.interp(A, self.A, self.J2)
        # calculate I1, I2
        T81A = self.sqrt32/(1.0-A)/(1.0+A)
        I1, I2 = T81A*J1, T81A*J2
        # calculate fields
        R1D3 = r/sqrt(D2*D2*D2)
        BX = ZH*R1D3*I1            # BX
        BZ = R1D3*(r*I2-self.X*I1) # BZ
        # add contribution
        self.BX += 1E2*BX
        self.BZ += 1E2*BZ
        # done
        return

    # grid calculation
    # optimised for speed
    def computeCoil(self):
        for h, r in zip(self.hl, self.rl):
            self.addLoop(r, h)
        return

if __name__ == "__main__":
    pass
