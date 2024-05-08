#!/usr/bin/python3
# file: optimize.py
# author: Roch Schanen
# created: 20200519
# modified: 20240508
# content: build optimisation tables for pygnetti
# repository: https://github.com/RochSchanen/pygnetti


# from "https://matplotlib.org/"
from matplotlib.pyplot import subplots
from matplotlib.pyplot import show

# from "https://numpy.org/"
from numpy import cos
from numpy import pi
from numpy import sqrt
from numpy import linspace
from numpy import empty_like
from numpy import append
from numpy import insert

# from local module "ielib.py"
from ielib import file_export, file_import

################################################## INTEGRATION

# elliptic integrals I1 and I2
# brute numerical integration
# there is no optimisation
# it is used for computing optimisation tables
# note that these integrals diverge at -1.0 and +1.0
def computeI1I2(
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

################################################## I1 and I2

# load table from file if available
data = file_import('./I1I2.txt')
if data is not None:
	A, I1, I2 = data
else:
	dA = 0.0001
	# discretise the range of integration
	A  = linspace(-1.000+dA, 1.000-dA, int(2.0/dA-1))
	# prepare the result tables
	I1, I2 = empty_like(A), empty_like(A)
	# compute the integrals: a thousand subdivisions for
	# evaluating the integral seams empirically to be a
	# good number.
	for i in range(len(A)):
		I1[i], I2[i] = computeI1I2(A[i], n = 1000)
	# export the results
	file_export('./I1I2.txt', A, I1, I2)

# make a plot for illustrations
fig0, ax0 = subplots()
fig0.set_size_inches(7, 7)
ax0.plot(A, I1, label = r'$I_1$')
ax0.plot(A, I2, label = r'$I_2$')
ax0.set_xlabel('alpha')
ax0.set_ylabel(r'$I_1, I_2$')
ax0.set_title('Integrals')
ax0.legend()
ax0.grid()

################################################## J1 and J2

# normalised elliptic integrals J1 and J2
# load table from file if available
data = file_import('./J1J2.txt')
if data is not None:
	A, J1, J2 = data
else:

	# Normalisation of I1 and I2
	# The sqrt(32) can be found when computing
	# the asymptotic behaviour of J1 and J2 at
	# the end points (alpha = -1.0 or +1.0)
	
	J1 = I1*(1.0-A)*(1.0+A)/sqrt(32)
	J2 = I2*(1.0-A)*(1.0+A)/sqrt(32)

	# The normalised functions have computable
	# theoretical limits:
	# at +1.0, (J1, J2) = (+1.0, +1.0)
	# at -1.0, (J1, J2) = (-1.0, +1.0)
	# These limit points are added by hand in
	# the tables.

	# at +1.0
	A  = append(A,  +1.0)
	J1 = append(J1, +1.0)
	J2 = append(J2, +1.0)

	# at -1.0
	A  = insert(A,  0, -1.0)
	J1 = insert(J1, 0, -1.0)
	J2 = insert(J2, 0, +1.0)
	
	# export the results
	file_export('./J1J2.txt', A, J1, J2)

# make a plot for illustrations
fig1, ax1 = subplots()
fig1.set_size_inches(7, 7)
J1_label = r'$J_1 = I_1(1-\alpha)(1+\alpha)/\sqrt{32}$'
J2_label = r'$J_2 = I_2(1-\alpha)(1-\alpha)/\sqrt{32}$'
ax1.plot(A, J1, label = J1_label)
ax1.plot(A, J2, label = J2_label)
ax1.set_xlabel(r'$\alpha$')
ax1.set_ylabel(r'$J_1, J_2$')
ax1.set_title('Normalised Integrals')
ax1.legend()
ax1.grid()

##################################################

# there are several options from here: 1) fit the data with polynomials
# 2) interpolate the existing data. Empirically, a polynomial interpolation
# requires a fairly large degree to remain accurate. this sensibly increases
# the time of computation. In contrast, on a finite interval (-1.0 to +1.0)
# with a fairly large number of points (20000), the interpolation method works
# very fast and remains accurate. Since a large amounts of memory allocation
# is not any more an issue in this day and age, the second solution has been
# selected in pygnetti.py

##################################################

show()

# The full computation takes less than one minute on an HP EliteOne 800
