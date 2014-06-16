#!/usr/bin/env python

import argparse #For cmd line parsing
import sys
import global_vars

def parse(argv):
	#Arg parse object
	parser = argparse.ArgumentParser(description='Do some graphics magic, eh?')
	
	#Add the options
	parser.add_argument('-f', help='input SMF file', metavar='FILE', default=global_vars.smf_file)
	parser.add_argument('-j', help='integer lower bound in the x dimension of the viewport window', metavar='VP_LX', default=global_vars.vp_lower_bound_x)
	parser.add_argument('-k', help='integer lower bound in the y dimension of the viewport window', metavar='VP_LY', default=global_vars.vp_lower_bound_y)
	parser.add_argument('-o', help='integer upper bound in the x dimension of the viewport window', metavar='VP_UX', default=global_vars.vp_upper_bound_x)
	parser.add_argument('-p', help='integer upper bound in the y dimension of the viewport window', metavar='VP_UY', default=global_vars.vp_upper_bound_y)
	parser.add_argument('-x', help='floating point x of Projection Reference Point (PRP) in VRC coordinates', metavar='PRP_X', default=global_vars.prp_x)
	parser.add_argument('-y', help='floating point y of Projection Reference Point (PRP) in VRC coordinates', metavar='PRP_Y', default=global_vars.prp_y)
	parser.add_argument('-z', help='floating point z of Projection Reference Point (PRP) in VRC coordinates', metavar='PRP_Z', default=global_vars.prp_z)
	parser.add_argument('-X', help='floating point x of View Reference Point (VRP) in world coordinates', metavar='VRP_X', default=global_vars.vrp_x)
	parser.add_argument('-Y', help='floating point y of View Reference Point (VRP) in world coordinates', metavar='VRP_Y', default=global_vars.vrp_y)
	parser.add_argument('-Z', help='floating point z of View Reference Point (VRP) in world coordinates', metavar='VRP_Z', default=global_vars.vrp_z)
	parser.add_argument('-q', help='floating point x of View Plane Normal vector (VPN) in world coordinates', metavar='VPN_X', default=global_vars.vpn_x)
	parser.add_argument('-r', help='floating point y of View Plane Normal vector (VPN) in world coordinates', metavar='VPN_Y', default=global_vars.vpn_y)
	parser.add_argument('-w', help='floating point z of View Plane Normal vector (VPN) in world coordinates', metavar='VPN_Z', default=global_vars.vpn_z)
	parser.add_argument('-Q', help='floating point x of View Up Vector (VUP) in world coordinates', metavar='VUP_X', default=global_vars.vup_x)
	parser.add_argument('-R', help='floating point y of View Up Vector (VUP) in world coordinates', metavar='VUP_Y', default=global_vars.vup_y)
	parser.add_argument('-W', help='floating point z of View Up Vector (VUP) in world coordinates', metavar='VUP_Z', default=global_vars.vup_z)
	parser.add_argument('-u', help='floating point u min of the VRC window in VRC coordinates', metavar='VRC_U_MIN', default=global_vars.vrc_u_min)
	parser.add_argument('-v', help='floating point v min of the VRC window in VRC coordinates', metavar='VRC_V_MIN', default=global_vars.vrc_v_min)
	parser.add_argument('-U', help='floating point u max of the VRC window in VRC coordinates', metavar='VRC_U_MAX', default=global_vars.vrc_u_max)
	parser.add_argument('-V', help='floating point v max of the VRC window in VRC coordinates', metavar='VRC_V_MAX', default=global_vars.vrc_v_max)
	#On off flag for projection method
	parser.add_argument('-P', help='use parallel projection',action="store_true")
	#Values for the near and far plane
	parser.add_argument('-F', help='floating point value for front plane', metavar='F_PLANE', default=global_vars.front_clip_value)
	parser.add_argument('-B', help='floating point value for back plane', metavar='B_PLANE', default=global_vars.back_clip_value)
	
	
	#Do the parsing, do not pass in prog name
	parsed_args = parser.parse_args(argv[1:])
	
	#Store the values into globals
	global_vars.smf_file = str(parsed_args.f)
	#Viewport
	global_vars.vp_lower_bound_x = int(parsed_args.j)
	global_vars.vp_lower_bound_y = int(parsed_args.k)
	global_vars.vp_upper_bound_x = int(parsed_args.o)
	global_vars.vp_upper_bound_y = int(parsed_args.p)
	#3D view volume
	global_vars.prp_x = float(parsed_args.x)
	global_vars.prp_y = float(parsed_args.y)
	global_vars.prp_z = float(parsed_args.z)
	global_vars.vrp_x = float(parsed_args.X)
	global_vars.vrp_y = float(parsed_args.Y)
	global_vars.vrp_z = float(parsed_args.Z)
	global_vars.vpn_x = float(parsed_args.q)
	global_vars.vpn_y = float(parsed_args.r)
	global_vars.vpn_z = float(parsed_args.w)
	global_vars.vup_x = float(parsed_args.Q)
	global_vars.vup_y = float(parsed_args.R)
	global_vars.vup_z = float(parsed_args.W)
	global_vars.vrc_u_min = float(parsed_args.u)
	global_vars.vrc_v_min = float(parsed_args.v)
	global_vars.vrc_u_max = float(parsed_args.U)
	global_vars.vrc_v_max = float(parsed_args.V)
	global_vars.use_parallel_projection = parsed_args.P
	global_vars.front_clip_value = float(parsed_args.F)
	global_vars.back_clip_value = float(parsed_args.B)
	
	
	return None
