#!/usr/bin/python3
# /content: tools
# /file: toolbox.py
# /date: 20200519
# /author: Roch Schanen
# /repository: https://github.com/RochSchanen/pygnetti

import pathlib as pl
import numpy as np
import time as tm

#######################
# super simple 

# output data to garbage file for  
def Export(*argv, format = '.2f', filePath = None):
	# get filepath
	fp = './garbage/out.txt' # default
	if filePath: fp = filePath
	# create file
	fh = open(fp, 'w')
	tf = "%a, %d %b %Y %H:%M:%S"
	fh.write(tm.strftime(tf, tm.gmtime())+'\n\n')
	n = len(argv[0])
	m = len(argv)
	for j in range(n):
		for i in range(m):
			fh.write(f'{argv[i][j]:{format}} ')
		fh.write('\n')
	fh.close()
	return

def Import(filePath = None):
	# get filepath
	fp = './garbage/out.txt' # default
	if filePath: fp = filePath
    # check path
	if pl.Path(fp).exists():
		# open
		_FH = open(fp, 'r')
		if not _FH: return None
		# skip two lines
		_FH.readline()
		_FH.readline()
		# read first line with data
		S = _FH.readline()
		# detect width
		n = len(S.split(' '))-1
		# built data list
		dl = [] 
		while S:
			L = S.split(' ')[:n] # fixed columns
			# L = S.split(' ')[:-1] # variable columns
			l = []
			for N in L: l.append(float(N))
			dl.append(l)
			S = _FH.readline()
		_FH.close()
		da = np.array(dl)
		# make list of arrays
		dl = []
		for i in range(n):
			dl.append(da[:,i])
		return dl
	return None

if __name__ == "__main__":
	pass