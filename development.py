#!/usr/bin/python3
# /file: development.py
# /date: 20200515
# /author: Roch Schanen
# /content: biot-savart numerics

# numpy: https://numpy.org/
from numpy import sqrt, inner, pi, cross, array, sin, cos, linspace

# local module
from postscript import *

# scipy: https://scipy.org/
from scipy.constants import mu_0

from pygnetti import coil

# Compute the field ()
def BiotSavart(I, dl, r):
	n = sqrt(inner(r, r)) # norm of r
	if n == 0: return array([0.0, 0.0, 0.0])
	return I * mu_0/4.0/pi * cross(dl, r) / (n**3)

# Compute the field (bx, by, bz) at point p
# for a loop of current I, of radius r
# in the plan xOy and centered on O
def LoopXY(I, r, p, n = 1000):
	t, dt, B = 0.0, 2.0*pi/n, array([0.0, 0.0, 0.0])
	for i in range(n): # integrate over the loop
		m  =    r*array([ cos(t), sin(t), 0.0])
		dm = dt*r*array([-sin(t), cos(t), 0.0])
		B += BiotSavart(I, dm, p-m) # sum integrale
		t += dt
	return B

def testDirections():

	#compute 

	psOpen()
	psAxis()

	I      = 1.000 # 1A
	radius = 1.000 # 1mm

	# reset lists
	X, Z, BX, BY, BZ = [],[],[],[],[]

	# scan through grid of points 
	for x in linspace(-radius*2.0, radius*2.0, 23):
		for z in linspace(-radius*2.0, radius*2.0, 23):
			# compute field at point (x, z)
			bx, by, bz = LoopXY(I, radius, array([x, 0.0, z]))
			if (x==0.0) & (z==0): print(bx, by, bz)
			# save point coordinates
			X.append(x)
			Z.append(z)
			# save field
			BX.append(bx)
			BY.append(by)
			BZ.append(bz)

	psStyle(width = 2)
	psColor(1.0, 0.5, 0.5)

	B = sqrt(array(BX)*array(BX) + array(BZ)*array(BZ))
	psVectors(array(X), array(Z), 0.1*array(BX)/B, 0.1*array(BZ)/B)

	COIL = coil()
	COIL.setupCoil(0.95, 0.1, 1, 1)
	
	COIL.psCoil()

	# reset lists
	X, Z, BX, BY, BZ = [],[],[],[],[]

	# scan through grid of points 
	for x in linspace(-radius*2.0, radius*2.0, 23):
		for z in linspace(-radius*2.0, radius*2.0, 23):
			# compute field at point (x, z)
			bx, bz = COIL.computeLoop(radius, x, z)
			if (x==0.0) & (z==0): print(bx, bz)
			# save point coordinates
			X.append(x)
			Z.append(z)
			# save field
			BX.append(bx)
			BZ.append(bz)

	psStyle(width = 1.0)
	psColor(0.5, 1.0, 0.5)

	B = sqrt(array(BX)*array(BX) + array(BZ)*array(BZ))
	psVectors(array(X), array(Z), 0.1*array(BX)/B, 0.1*array(BZ)/B)

	COIL.setupGrid(-radius*2.0, radius*2.0, 23, -radius*2.0, radius*2.0, 23)
	COIL.computeCoil()

	X, Z, BX, BY, BZ = [],[],[],[],[]

	X  = COIL.X
	Z  = COIL.Z
	BX = COIL.BX
	BZ = COIL.BZ

	psStyle(width = 0.2)
	psColor(0.5, 0.5, 1.0)

	B = sqrt(array(BX)*array(BX) + array(BZ)*array(BZ))
	psVectors(array(X), array(Z), 0.1*array(BX)/B, 0.1*array(BZ)/B)

	psClose()

def testSingleLoopNumericsVectors():

	#compute 

	psOpen()
	psAxis()

	I      = 1.000 # 1A
	radius = 1.000 # 1mm
	B0     = 2.0   # scaling

	# reset lists
	X, Z, BX, BY, BZ = [],[],[],[],[]

	# scan through grid of points 
	for x in linspace(-radius*2.0, radius*2.0, 23):
		for z in linspace(-radius*2.0, radius*2.0, 23):
			# compute field at point (x, z)
			bx, by, bz = LoopXY(I, radius, array([x, 0.0, z]))
			if (x==0.0) & (z==0): print(bx, by, bz)
			# save point coordinates
			X.append(x)
			Z.append(z)
			# save field
			BX.append(bx)
			BY.append(by)
			BZ.append(bz)

	psStyle(width = 2)
	psColor(1.0, 0.5, 0.5)

	B = B0*1E-7 # B = sqrt(array(BX)*array(BX) + array(BZ)*array(BZ))
	psVectors(array(X), array(Z), 0.1*array(BX)/B, 0.1*array(BZ)/B)

	COIL = coil()
	COIL.setupCoil(0.95, 0.1, 1, 1)
	
	COIL.psCoil()

	# reset lists
	X, Z, BX, BY, BZ = [],[],[],[],[]

	# scan through grid of points 
	for x in linspace(-radius*2.0, radius*2.0, 23):
		for z in linspace(-radius*2.0, radius*2.0, 23):
			# compute field at point (x, z)
			bx, bz = COIL.computeLoop(radius, x, z)
			if (x==0.0) & (z==0): print(bx, bz)
			# save point coordinates
			X.append(x)
			Z.append(z)
			# save field
			BX.append(bx)
			BZ.append(bz)

	psStyle(width = 1.0)
	psColor(0.5, 1.0, 0.5)

	B = B0 *100 # B = sqrt(array(BX)*array(BX) + array(BZ)*array(BZ))
	psVectors(array(X), array(Z), 0.1*array(BX)/B, 0.1*array(BZ)/B)

	COIL.setupGrid(-radius*2.0, radius*2.0, 23, -radius*2.0, radius*2.0, 23)
	COIL.computeCoil()

	X, Z, BX, BY, BZ = [],[],[],[],[]

	X  = COIL.X
	Z  = COIL.Z
	BX = COIL.BX
	BZ = COIL.BZ

	psStyle(width = 0.2)
	psColor(0.5, 0.5, 1.0)

	B = B0*1E2 # B = sqrt(array(BX)*array(BX) + array(BZ)*array(BZ))
	psVectors(array(X), array(Z), 0.1*array(BX)/B, 0.1*array(BZ)/B)

	psClose()

def testCoil():

	#compute 

	psOpen()
	psAxis()

	n = 5

	COIL = coil()
	COIL.setupCoil(0.95, 0.1*n, n, 1)
	COIL.psCoil()

	I      = 1.000 # 1A
	radius = 1.000 # 1mm
	B0     = 5*n   # scaling
	# xs, xe, xn = 0.8, 0.8, 1
	# ys, ye, yn = 0.20, 0.20, 1
	xs, xe, xn = -radius*2.0, +radius*2.0, 23
	ys, ye, yn = -radius*2.0, +radius*2.0, 23

	# reset lists
	X, Z, BX, BY, BZ = [],[],[],[],[]
	# scan through grid of points 
	for x in linspace(xs, xe, xn):
		for z in linspace(ys, ye, yn):
			# compute field at point (x, z)
			bx, bz = COIL._computeCoil(x, z)
			# save point coordinates
			X.append(x)
			Z.append(z)
			# save field
			BX.append(bx)
			BZ.append(bz)

	psStyle(width = 2.0)
	psColor(0.5, 1.0, 0.5)
	B = B0 *100
	psVectors(array(X), array(Z), 0.1*array(BX)/B, 0.1*array(BZ)/B)

	COIL.setupGrid(xs, xe, xn, ys, ye, yn)
	COIL.computeCoil()
	X, Z, BX, BY, BZ = [],[],[],[],[]
	X  = COIL.X
	Z  = COIL.Z
	BX = COIL.BX
	BZ = COIL.BZ

	psStyle(width = 1.0)
	psColor(0.5, 0.5, 1.0)
	B = B0*1E2
	psVectors(array(X), array(Z), 0.1*array(BX)/B, 0.1*array(BZ)/B)

	# reset lists
	i, j = 10, 17
	X, Z = COIL.X[i,j], COIL.Z[i,j]
	BX, BY, BZ = 0.0, 0.0, 0.0
	# scan through loops
	for h, r in zip(COIL.hl, COIL.rl):
			# compute field at point (x, z)
			bx, by, bz = LoopXY(I, radius, array([X, 0.0, Z-h]))
			# save field
			BX += bx
			BY += by
			BZ += bz

	psStyle(width = 0.2)
	psColor(1.0, 0.1, 0.1)

	B = B0*1E-6
	psVector(X, Z, BX/B, BZ/B)

	# reset lists
	i, j = 11, 11
	X, Z = COIL.X[i,j], COIL.Z[i,j]
	BX, BY, BZ = 0.0, 0.0, 0.0
	# scan through loops
	for h, r in zip(COIL.hl, COIL.rl):
			# compute field at point (x, z)
			bx, by, bz = LoopXY(I, radius, array([X, 0.0, Z-h]))
			# save field
			BX += bx
			BY += by
			BZ += bz

	psStyle(width = 0.2)
	psColor(1.0, 0.1, 0.1)

	B = B0*1E-6
	psVector(X, Z, BX/B, BZ/B)

	psClose()

if __name__ == "__main__":

	# testDirections()                  # --> loop1.pdf
	# testSingleLoopNumericsVectors()   # --> loop2.pdf
	testCoil()                          # --> loop3.pdf
