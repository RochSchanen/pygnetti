#!/usr/bin/python3
# /content: magnetic field calculator
# /file: pygnetti.py
# /date: 20200515
# /author: Roch Schanen
# /repository: https://github.com/RochSchanen/pygnetti

# /todo: turn loops into array computations

# numpy: https://numpy.org/
# float type is float64 by default <=> double
from numpy import pi, sqrt, cos, linspace, square
from numpy import empty_like as empty

# scipy: https://scipy.org/
from scipy.constants import mu_0

# loop axis is set along oz
# r, h: radius [m], position along z [m]
# current is set at 1A
# magnetic units are S.I.
class loop:

    def __init__(self, R):
        self.R = R
        return

    # Single point calculation
    # for checking future
    # optimisations
    def getpoint(
            self,      # loop instance
            X = 0.0,     # position radius [m]
            H = 0.0,     # position height [m]
            n = 1000): # intervals for integrals
        # get geometry
        R = self.R
        # compute constants
        c = square(X)+square(H)+square(R)
        # beta
        b = sqrt(c*c*c)
        # alpha
        a = 2.0*X*R/b
        # angle interval
        dt = 2*pi/n
        # accumulators  
        i1, i2 = 0.0, 0.0
        # angle theta
        t = 0.0
        for i in range(n):
            print(f'{i:03d}',end=' - ')
            print(f'{t:+18f}',end=' - ')
            c = cos(t)      ;print(f'c : {c :+.18f}',end=' ')
            m = 1.0-a*c     ;print(f'm : {m :+.18f}',end=' ')
            d = sqrt(m*m*m) ;print(f'd : {d :+.18f}',end=' ')
            i1 += c/d       ;print(f'i1: {i1:+.18f}',end=' ')
            i2 += 1.0/d     ;print(f'i2: {i2:+.18f}',end=' ')
            t  += dt
            print()
        # integrals value
        I1, I2 = dt*i1, dt*i2
        bx, bz = H*R*I1/b, R/b*(R*I2-X*I1)
        # scale to S.I. units
        Bx, Bz = bx*mu_0/4.0/pi, bz*mu_0/4.0/pi
        # return Bx, Bz
        return Bx, Bz

if __name__ == "__main__":

    l = loop(1.0) # 1 meter radius

    # # check point 1 : centre (1A)
    # Bx, Bz = l.getpoint()           # centre of the loop
    # print(f'{Bx:.6e}, {Bz:.6e}')      # result in Tesla
    # # compare
    # print(f'{0.0:.6e}, {mu_0/2:.6e}')

    # # check point 2 : along the axis
    # Z  = linspace(0.0, 2.0, 21)
    # Bx, Bz = empty(Z), empty(Z)
    # for i in range(len(Z)): Bx[i], Bz[i] = l.getpoint(H = Z[i], n = 10000)
    # # compare
    # bx, bz = empty(Z), empty(Z)
    # for i in range(len(Z)): bx[i], bz[i] = 0.0, mu_0/2/(1+Z[i]**2)**1.5
    # f = '+.9f'
    # for i in range(len(Z)):
    #     print(f'Z = {Z[i]:.3f}', end=' ')
    #     print(f'BX = {bx[i]*1E6:{f}}µT, {Bx[i]*1E6:{f}}µT', end=' ')
    #     print(f'BZ = {bz[i]*1E6:{f}}µT, {Bz[i]*1E6:{f}}µT', end=' ')
    #     print()

    # check point 3: value of Bx should be strictly zero
    Bx, Bz = l.getpoint(H = 0.0, n = 12) 
    print(f'{Bx*1E6:+.9f}µT, {Bz*1E6:+.9f}µT')
    # the non zero result due to numerical precision limits
    # and not to the algorithm. Passed check point 3
    