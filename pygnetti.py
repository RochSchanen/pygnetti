#!/usr/bin/python3
# /content: magnetic field calculator
# /file: pygnetti.py
# /date: 20200515
# /author: Roch Schanen
# /repository: https://github.com/RochSchanen/pygnetti

# /todo: check type casting for arithmetic

# numpy: https://numpy.org/
from numpy import pi, sqrt, double, cos

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
			self,	   # loop instance
			X = 0,     # position radius [m]
			H = 0,     # position height [m]
			n = 1000): # intervals for integrals
		# get geometry
		R = self.R
		# compute constants
		c = X**2+H**2+R**2
		# beta
		b = sqrt(c*c*c)
		# alpha
		a = 2.0*X*R/b
		# angle interval
		dt = pi/n
		# accumulators
		i1, i2 = 0.0, 0.0
		# angle theta
		t = dt/2.0
		for i in range(n):
			c = cos(t)
			m = 1.0-a*c
			d = sqrt(m*m*m)
			i1 += c/d
			i2 += 1.0/d
		# integrals value
		I1, I2 = dt+i1, dt*i2
		bx, bz = 2*H*R*I1/b, 2*R/b*(R*I2-X*I1)
		# scale to S.I. units 
		Bx, Bz = bx*mu_0/4.0/pi, bz*mu_0/4.0/pi
		return Bx, Bz

if __name__ == "__main__":

	l = loop(1.0)			# 1 meter radius
	Bx, Bz = l.getpoint()	# centre of the loop
	print(Bx, Bz)           # result in Tesla
