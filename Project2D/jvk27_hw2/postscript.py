#!/usr/bin/env python

import geometry
import sys

PS_BEGIN_TEXT="%%%BEGIN"
PS_END_TEXT="%%%END"
PS_LINE_CMD_TEXT="Line"
PS_MOVETO_CMD_TEXT = "moveto"
PS_LINETO_CMD_TEXT = "lineto"
PS_STROKE_CMD_TEXT = "stroke"


#Parse the ps 'Line' command and return a line object
def ps_line_cmd(ps_line):
	#Parse this line, space seperator
	toks = ps_line.split(" ")
	l = None
	l = geometry.Line()
	l.p1 = geometry.Point()
	l.p2 = geometry.Point()
	l.p1.x = float(toks[0])
	l.p1.y = float(toks[1])
	l.p2.x = float(toks[2])
	l.p2.y = float(toks[3])
	return l
	
#Parse a set of lines from ps file and return polygon object
#Does NOT INCLUDE closing point, assume last point connects to first
def ps_polygon(ps_polygon_lines):
	points = []
	#Do not include last point
	for i in range(0,len(ps_polygon_lines)-1):
		line = ps_polygon_lines[i]
		toks = line.split(" ")
		x = toks[0]
		y = toks[1]
		tmp_p = None
		tmp_p = geometry.Point()
		tmp_p.x = x
		tmp_p.y = y
		points = points + [tmp_p]
	
	poly = geometry.Polygon()
	poly.vertices = points
	return poly

#Return list of line objects from ps file
def get_geometric_objects(ps_file):
	#List to return
	rv = []
	
	#Open the file
	f=open(ps_file,'r')
	
	#Get all lines
	lines=f.readlines()
	#Keep flags
	reached_begin = False
	#Temp list of text lines (for polygons)
	temp_lines = []	
	#Loop over all lines
	for line in lines:
		#Check for begin flag
		if PS_BEGIN_TEXT in line:
			reached_begin = True
			continue
		
		#IF we've past begin and arent at end start parsing commands
		if reached_begin and not(PS_END_TEXT in line):		
			if PS_LINE_CMD_TEXT in line:
				#Get line add to list
				l = ps_line_cmd(line)
				rv = rv + [l]
			elif PS_MOVETO_CMD_TEXT in line:
				#Start of a polygon, collect line for parsing
				temp_lines = [line]
			elif PS_LINETO_CMD_TEXT in line:
				#Collect this line for parsing
				temp_lines = temp_lines + [line]
			elif PS_STROKE_CMD_TEXT in line:
				#Stroke line ends polygon, add obj to rv list
				poly = ps_polygon(temp_lines)
				rv = rv + [poly]
			else:
				print "Unknown postscript command in line '",line,"'"
		
	return rv
