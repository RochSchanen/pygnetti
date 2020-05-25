#!/usr/bin/python3
# /content: magnetic field calculator
# /file: optimise.py
# /date: 20200519
# /author: Roch Schanen
# /repository: https://github.com/RochSchanen/pygnetti

from numpy import sin, pi, sqrt, linspace
from numpy import polyfit as polynomeFit
from numpy import poly1d as polynome

import numpy as np
import toolbox as tb
import pygnetti as pg
import matplotlib as mpl
import matplotlib.pyplot as pp
# pp.rcParams['toolbar'] = 'None'
scrw, scrh = 3840, 1200

# instanciate class
# to access methods
C = pg.coil()

# load table if exists
data = tb.Import('./I1I2.txt')
# data = None
if data:
	A, I1, I2 = data
else:
	dA = 0.0001 # resolution
	# if none compute and save table
	A  = np.linspace(-1.000+dA, 1.000-dA, 2.0/dA-1)
	I1, I2 = np.empty_like(A), np.empty_like(A)
	for i in range(len(A)):
		# n = 1000 is the number of subdivision
		# for evaluating the integrale (empirically
		# 1000 is a good enougth number)
		I1[i], I2[i] = C.computeI1I2(A[i], n = 1000)
		# export result data to file
	tb.Export(A, I1, I2, format = '+.6e', filePath = './I1I2.txt')

fig0, ax0 = pp.subplots()
fig0.set_size_inches(9, 9)
position = f"+{int(scrw*0.50+10)}+{int(scrh*0.0+10)}"
fig0.canvas.manager.window.wm_geometry(position)

# ax0.semilogy(A, I1, label = r'$I_1$')
# ax0.semilogy(A, I2, label = r'$I_2$')
ax0.plot(A, I1, label = r'$I_1$')
ax0.plot(A, I2, label = r'$I_2$')
ax0.set_xlabel('alpha')
ax0.set_ylabel(r'$I_1, I_2$')
ax0.set_title('Integrales')
ax0.legend()
ax0.grid()

# pp.show()
# exit()

# load table if exists
data = tb.Import('./J1J2.txt')
# data = None
if data:
	A, J1, J2 = data
else:
	# if none compute and save table
	# normalisation of I1 and I2
	# the sqrt(32) arises from
	# computing the asymtotic
	# behaviour of J1 and J2
	# at the point -1.0 and +1.0
	J1 = I1*(1.0-A)*(1.0+A)/sqrt(32)
	J2 = I2*(1.0-A)*(1.0+A)/sqrt(32)

	# The normalised functions have
	# computable theoretical limits
	# at +1.0: (J1, J2) = (+1.0, +1.0)
	# at -1.0: (J1, J2) = (-1.0, +1.0)
	# These limit points are added by hand

	# at +1.0
	A  = np.append(A,  +1.0)
	J1 = np.append(J1, +1.0)
	J2 = np.append(J2, +1.0)

	# at -1.0
	A  = np.insert(A,  0, -1.0)
	J1 = np.insert(J1, 0, -1.0)
	J2 = np.insert(J2, 0, +1.0)
	
	# export result data to file
	tb.Export(A, J1, J2, format = '+.6e', filePath = './J1J2.txt')

fig1, ax1 = pp.subplots()
fig1.set_size_inches(9, 9)
position = f"+{int(scrw*0.75+10)}+{int(scrh*0.0+10)}"
fig1.canvas.manager.window.wm_geometry(position)

J1_label = r'$J_1 = I_1(1-\alpha)(1+\alpha)/\sqrt{32}$'
J2_label = r'$J_2 = I_2(1-\alpha)(1-\alpha)/\sqrt{32}$'
ax1.plot(A, J1, label = J1_label)
ax1.plot(A, J2, label = J2_label)
ax1.set_xlabel(r'$\alpha$')
ax1.set_ylabel(r'$J_1, J_2$')
ax1.set_title('Normalised Integrales')
ax1.legend()
ax1.grid()

# there are several options from here:
# - fit the data with polynomials or
# - interpolate the existing data


# Empirically, a polynomial interpolation
# requires a fairly large degree to remain
# accurate which sensibly increases the
# time of computation. In contrast, on the
# finite interval (-1.0 to +1.0) with a
# fairly large number of points (20000),
# the interpolation method works well.
# The memory consumption is no more an
# issue in these modern days.

pp.show()
