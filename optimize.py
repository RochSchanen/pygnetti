#!/usr/bin/python3
# file: optimize.py
# author: Roch Schanen
# created: 20200519
# content: make optimisation tables for pygnetti
# repository: https://github.com/RochSchanen/pygnetti

import numpy as np
import pygnetti as pg
import matplotlib as mpl
import matplotlib.pyplot as pp

from numpy import sin, pi, sqrt, linspace
from ielib import file_export, file_import

# instantiate a coil to access computation functions
C = pg.coil()

# load table from file if available
data = file_import('./I1I2.txt')
if data is not None:
	A, I1, I2 = data
else:
	# Setup the alpha resolution. A 1000 subdivisions for evaluating the
	# integral seams empirically to be a good enough number. we use 10000.
	dA = 0.0001
	# discretise the range of integration
	A  = np.linspace(-1.000+dA, 1.000-dA, int(2.0/dA-1))
	# declare the result tables
	I1, I2 = np.empty_like(A), np.empty_like(A)
	# compute the integrals
	for i in range(len(A)):
		I1[i], I2[i] = C.computeI1I2(A[i], n = 1000)
		# export result data to file
	file_export('./I1I2.txt', A, I1, I2)

fig0, ax0 = pp.subplots()
fig0.set_size_inches(7, 7)
ax0.plot(A, I1, label = r'$I_1$')
ax0.plot(A, I2, label = r'$I_2$')
ax0.set_xlabel('alpha')
ax0.set_ylabel(r'$I_1, I_2$')
ax0.set_title('Integrals')
ax0.legend()
ax0.grid()

# load table from file if available
data = file_import('./J1J2.txt')
if data is not None:
	A, J1, J2 = data
else:

	# Normalisation of I1 and I2. The sqrt(32) can be found when computing
	# the asymptotic behaviour of J1 and J2 at the end points -1.0 and +1.0:
	
	J1 = I1*(1.0-A)*(1.0+A)/sqrt(32)
	J2 = I2*(1.0-A)*(1.0+A)/sqrt(32)

	# The normalised functions have computable theoretical limits:
	# at +1.0, (J1, J2) = (+1.0, +1.0)
	# at -1.0, (J1, J2) = (-1.0, +1.0)
	# These limit points are added by hand in the tables

	# at +1.0
	A  = np.append(A,  +1.0)
	J1 = np.append(J1, +1.0)
	J2 = np.append(J2, +1.0)

	# at -1.0
	A  = np.insert(A,  0, -1.0)
	J1 = np.insert(J1, 0, -1.0)
	J2 = np.insert(J2, 0, +1.0)
	
	# export result data to file
	file_export('./J1J2.txt', A, J1, J2)

fig1, ax1 = pp.subplots()
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

# there are several options from here: 1) fit the data with polynomials or
# 2) interpolate the existing data. Empirically, a polynomial interpolation
# requires a fairly large degree to remain accurate, which sensibly increases
# the time of computation. In contrast, on a finite interval (-1.0 to +1.0)
# with a fairly large number of points (20000), the interpolation method works
# well. Since large amounts of memory allocation is not any more an issue in
# this day and age, the second solution has been selected.

pp.show()
