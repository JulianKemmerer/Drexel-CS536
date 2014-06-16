#!/usr/bin/env python

import argparse #For cmd line parsing
import sys
import global_vars

def parse(argv):
	#Arg parse object
	parser = argparse.ArgumentParser(description='Do some graphics magic, eh?')
	
	#Add the options
	parser.add_argument('-f', help='the input "Postscript" file', metavar='FILE', default=global_vars.ps_file)
	parser.add_argument('-s', help='float specifying the scaling factor in both dimensions about the world origin', metavar='SCALE', default=global_vars.scale)
	parser.add_argument('-r', help='integer specifying the number of degrees for a counter-clockwise rotation about the world origin', metavar='CC_DEG', default=global_vars.rotation_cc)
	parser.add_argument('-m', help='integer specifying a translation in the x dimension', metavar='TRANS_X', default=global_vars.trans_x)
	parser.add_argument('-n', help='integer specifying a translation in the y dimension', metavar='TRANS_Y', default=global_vars.trans_y)
	parser.add_argument('-a', help='integer lower bound in the x dimension of the world window', metavar='LX', default=global_vars.lower_bound_x)
	parser.add_argument('-b', help='integer lower bound in the y dimension of the world window', metavar='LY', default=global_vars.lower_bound_y)
	parser.add_argument('-c', help='integer upper bound in the x dimension of the world window', metavar='UX', default=global_vars.upper_bound_x)
	parser.add_argument('-d', help='integer upper bound in the y dimension of the world window', metavar='UY', default=global_vars.upper_bound_y)
	parser.add_argument('-j', help='integer lower bound in the x dimension of the viewport window', metavar='VP_LX', default=global_vars.vp_lower_bound_x)
	parser.add_argument('-k', help='integer lower bound in the y dimension of the viewport window', metavar='VP_LY', default=global_vars.vp_lower_bound_y)
	parser.add_argument('-o', help='integer upper bound in the x dimension of the viewport window', metavar='VP_UX', default=global_vars.vp_upper_bound_x)
	parser.add_argument('-p', help='integer upper bound in the y dimension of the viewport window', metavar='VP_UY', default=global_vars.vp_upper_bound_y)

	#Do the parsing, do not pass in prog name
	parsed_args = parser.parse_args(argv[1:])
	
	#Store the values into globals
	global_vars.ps_file = str(parsed_args.f)
	global_vars.scale = float(parsed_args.s)
	global_vars.rotation_cc = int(parsed_args.r)
	global_vars.trans_x = int(parsed_args.m)
	global_vars.trans_y = int(parsed_args.n)
	global_vars.lower_bound_x = int(parsed_args.a)
	global_vars.lower_bound_y = int(parsed_args.b)
	global_vars.upper_bound_x = int(parsed_args.c)
	global_vars.upper_bound_y = int(parsed_args.d)
	global_vars.vp_lower_bound_x = int(parsed_args.j)
	global_vars.vp_lower_bound_y = int(parsed_args.k)
	global_vars.vp_upper_bound_x = int(parsed_args.o)
	global_vars.vp_upper_bound_y = int(parsed_args.p)
	
	
	return None
