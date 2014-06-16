#!/usr/bin/env python
import numpy

#MATRICIES ARE ADDRESSED AS [Y,X]

def zeros_matrix(xdim,ydim):
	xarr=[0.0]*xdim
	arr=[xarr]*ydim
	mat = numpy.matrix(arr)
	return mat

def identity_matrix(xdim,ydim):
	mat=zeros_matrix(xdim,ydim)
	min_dim = min(xdim,ydim)
	for i in range(0,min_dim):
		mat[i,i] = 1.0
	return mat
	
def magnitude(np_array):
	dot = np_array.dot(np_array)
	mag = numpy.sqrt(dot)
	return mag
