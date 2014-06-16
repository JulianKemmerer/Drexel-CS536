#!/usr/bin/env python

import matrix
import math
import sys
import copy #For object copying
import global_vars

#Enter exit text consts
ENTER="Enter"
EXIT = "Exit"

class GeometricObject:
	#Most of these will be overloaded
	#All geometric objects can be transformed
	def apply_transform(self, transform_matrix):
		print "apply_transform not implemented for GeometricObject"
		return None
		
	#All geometric objects can be clipped to window, return the clipped object
	def clip_to_window(self,lower_bound_x, lower_bound_y,upper_bound_x, upper_bound_y):
		print "clip_to_window not implemented for GeometricObject"
		return None
		
	#All geometric objects can be rendered to points
	def render_points(self):
		print "render_points not implemented for GeometricObject"
		return None

#Point object with helpful methods
class Point(GeometricObject):
	x=0.0
	y=0.0
	z=0.0
	
	def __init__(self):
		x=0.0
		y=0.0
		z=0.0
	
	#Apply transform to this point
	def apply_transform(self,transform_matrix):
		#Convert points to matrix
		point_matrix = self.to_matrix()
		
		#Do multiplication
		result = transform_matrix * point_matrix
		
		#Change values for this point
		self.save_matrix_as_points(result)
		
	#Clip this point to window
	def clip_to_window(self,lower_bound_x, lower_bound_y,upper_bound_x, upper_bound_y):
		#Doesn't actually do anything for a single point
		return self
		
	#Render this point to a point, return list of points with one point
	def render_points(self):
		return [self]
	
	#Save a point matrix into xyz
	def save_matrix_as_points(self,point_matrix):
		self.x = point_matrix[0,0]
		self.y = point_matrix[1,0]
		self.z = point_matrix[2,0]
	
	#Convert points to matrix
	def to_matrix(self):
		point_matrix = matrix.zeros_matrix(1,4)		
		point_matrix[0,0] = self.x
		point_matrix[1,0] = self.y
		point_matrix[2,0] = self.z
		point_matrix[3,0] = 1.0
		return point_matrix
		
	#Return the Cohen-Sutherland code for this point
	def cs_code(self, lower_bound_x, lower_bound_y, upper_bound_x, upper_bound_y):
		#Return value code
		rv = 0
		
		#Bit 1 if point is above window
		if(self.y>upper_bound_y):
			rv = rv | 1;
		#Bit 2 if point is below window
		if(self.y<lower_bound_y):
			rv = rv | 2;
		#Bit 3 if point is right of window
		if(self.x>upper_bound_x):
			rv = rv | 4;
		#Bit 4 if point is left of window
		if(self.x<lower_bound_x):
			rv = rv | 8;
		return rv;
		
	#Given a bound, say if this point is within the bound
	def is_in_bound(self, is_lower, is_x, bound_value):
		x = self.x
		y = self.y
		
		if( (is_lower==False) and (is_x==False) ):
			#Upper bound in y check
			return ( y <= bound_value)
		elif( (is_lower==False) and (is_x==True) ):
			#Upper bound in x check
			return ( x <= bound_value)
		elif( (is_lower==True) and (is_x==False) ):
			#Lower bound in y check
			return ( y >= bound_value)
		else:
			#Lower bound in x check
			return ( x >= bound_value)
	
	#Equality operator	
	def __eq__(self, obj):
		return (self.x==obj.x) and (self.y==obj.y) and (self.z==obj.z)
		
	#To string operator
	def __str__(self):
		return "("+str(self.x)+","+str(self.y)+","+str(self.z)+")"
			

#Line object
class Line(GeometricObject):
	def __init__(self):
		p1 = Point()
		p2 = Point()
	
	#Apply transform to this line
	def apply_transform(self, transform_matrix):
		#Apply transform to both points
		self.p1.apply_transform(transform_matrix)
		self.p2.apply_transform(transform_matrix)
		return None
		
	#All geometric objects can be clipped to window
	def clip_to_window(self,lower_bound_x, lower_bound_y,upper_bound_x, upper_bound_y,run_count=1):
		#Run this function 4 times (for all 4 window bounds)
		#Cheap, but it works for now.
		if run_count > 4:
			return copy.deepcopy(self)
		
		#Get cs code for each point
		cs1 = self.p1.cs_code(lower_bound_x, lower_bound_y, upper_bound_x, upper_bound_y)
		cs2 = self.p2.cs_code(lower_bound_x, lower_bound_y, upper_bound_x, upper_bound_y)
		
		#Check if completely visible
		OR = cs1 | cs2
		AND = cs1 & cs2
		XOR = cs1 ^ cs2
		if(OR == 0):
			#Line is completely visible (no change to line)
			return self
		elif(AND != 0):
			#Line is completely outside window
			#Drop it by returning none
			return None
		else:		
			#Decide which bit flips
			#XOR finds flipped bits
			#AND to check 
			if(XOR & 1 == 1): #Bit 1 flipped
				#Window Top, upper_bound_y
				new_line = self.clip_line(False, False, upper_bound_y)
			elif((XOR & 2) == 2): #Bit 2 flipped
				#Window Bottom, lower_bound_y
				new_line = self.clip_line(True, False, lower_bound_y);
			elif((XOR & 4) == 4): #Bit 3 flipped
				#Window Right, upper_bound_x
				new_line = self.clip_line(False, True, upper_bound_x);
			elif((XOR & 8) == 8): #Bit 4 flipped
				#Window Left, lower_bound_x
				new_line = self.clip_line(True, True, lower_bound_x);
			else:
				print "Line does not have valid bit flips."
				sys.exit(-1)
			
			#return self.clip_to_window(lower_bound_x, lower_bound_y,upper_bound_x, upper_bound_y,run_count+1)
			return new_line.clip_to_window(lower_bound_x, lower_bound_y,upper_bound_x, upper_bound_y,run_count+1)	
		
	#All geometric objects can be rendered to points
	def render_points(self):
		#DDA (does use floating point rounding to ints)
		#Some variables for ease
		p1 = self.p1
		p2 = self.p2
		x1 = p1.x
		y1 = p1.y
		x2 = p2.x
		y2 = p2.y
		
		#Slope
		#Check special cases
		dy = (y2-y1)
		dx = (x2-x1)
		ady = abs(dy)
		adx = abs(dx)
		
		#Calculate equation values and deciding which eq form to take
		m = 0
		b = 0
		#Also keep track of starting and end loop bounds for later
		start = 0
		end = 0
		#Decide on which equation form to use
		is_y_mx_b = False;
		
		
		#If dx dy  = 0?
		if( (dx==0) and (dy==0)):
			#No change in y or x between points?
			#Return list void of points
			return []
		#If dy/dx is >1 then line is closer to vertical than horozontal
		elif( (adx==0) or (ady/adx) > 1):
			#More vertical, use x=my+b form
			is_y_mx_b = False
			m = dx/dy
			b = x2 - (m*y2)
			#Will loop over Y
			start = int(y1)
			end = int(y2)
		else:
			#More horozontal, use y=mx+b form
			is_y_mx_b = True;
			m = dy/dx
			b = y2 - (m*x2)
			#Will loop over X
			start = int(x1)
			end = int(x2)
		
		#Start looping over either x or y
		#Check bounds first, swap
		if(start > end):
			tmp = start
			start = end
			end = tmp
		
		#There will be a point for each loop iteration
		point_count = end - start + 1
		#Points return value
		rv = []	
		
		#Begin looping
		var = 0
		i = 0
		for var in range(start,end+1):
			#Some generic names for ease
			func_val_f = line_func(m,var,b)
			func_val_i = int(func_val_f)
			x=0
			y=0	
			
			if(is_y_mx_b==True):
				#Loop variable is x
				x = var
				y = func_val_i
			else:
				#Loop variable is y
				x = func_val_i
				y = var
			
			#Save this point
			tmp = Point()
			tmp.x = x
			tmp.y = y
			rv = rv + [tmp]
		
		#Return list of points
		return rv
		
	#Take line and do clipping
	def clip_line(self, is_lower, is_x, bound_value):
		#Find which point on this line is past the boundary(outside window)
		p1 = self.p1
		p2 = self.p2
		p1_in_bound = p1.is_in_bound(is_lower,is_x,bound_value)
		p2_in_bound = p2.is_in_bound(is_lower,is_x,bound_value)
		
		#Check
		#The do_clip_make_line defaults to p1=other_point,p2=point_to_clip, pass flag to swap if otherwise
		#No flag can be false if looks like do_clip_make_line(self,p2, p1 ...)
		if( (p1_in_bound==False) and (p2_in_bound==False) ):
			print "Neither point is outside boundary."
			sys.exit(-1)
		elif( (p1_in_bound==False) and (p2_in_bound==True) ):
			#Create line p2->p1 w/o swap flag
			return self.do_clip_make_line(p1, p2, is_lower, is_x, bound_value, True)
		elif( (p1_in_bound==True) and (p2_in_bound==False) ):
			#Create line p2->p1 w/o swap flag
			return self.do_clip_make_line(p2, p1, is_lower, is_x, bound_value, False)
		else:
			print "Both points are outside boundary."
			sys.exit(-1)
	
	#This function defaults to p1=other_point,p2=point_to_clip, pass flag to swap if otherwise
	def do_clip_make_line(self,point_to_clip, other_point, is_lower, is_x, bound_value, swap_points=False):
		#Return line
		rv = Line()
		
		#Let point 2 be the point to clip
		x1 = float(other_point.x)
		y1 = float(other_point.y)
		x2 = float(point_to_clip.x)
		y2 = float(point_to_clip.y)
		
		dx = x2 - x1
		dy = y2 - y1
		
		#Special case for vertical line
		if(dx == 0):
			#Check that we are clipping in Y
			if is_x==False:
				if is_lower:
					#Lower bound
					if point_to_clip.y < bound_value:
						point_to_clip.y = bound_value
				else:
					#Upper bound
					if point_to_clip.y > bound_value:
						point_to_clip.y = bound_value
			
			#Check if swap needed
			if swap_points:
				rv.p1 = point_to_clip
				rv.p2 = other_point
			else:
				rv.p1 = other_point
				rv.p2 = point_to_clip
			return rv
				
		#Calc line equation values
		m = dy/dx
		#Solve for intercept
		#y=mx+b , b = y-mx, use point 2
		b = y2 - (m*x2);
		
		#Decide what we need to solve for, an x or y value
		if(is_x == True):
			#X Bound, solve for Y value
			# y = mx + b
			bounded_y = m*bound_value + b
			point_to_clip.x = bound_value
			point_to_clip.y = bounded_y
		else:
			#Y Bound, solve for X value
			# x = (y-b)/m
			bounded_x = (bound_value - b)/m
			point_to_clip.x = bounded_x
			point_to_clip.y = bound_value
		
		#Check if swap needed
		if swap_points:
			rv.p1 = point_to_clip
			rv.p2 = other_point
		else:
			rv.p1 = other_point
			rv.p2 = point_to_clip
		return rv
	
	#Equality operator	
	def __eq__(self, obj):
		return (self.p1==obj.p1) and (self.p2==obj.p2)
		
	#To string operator
	def __str__(self):
		return self.p1.__str__() + "->" + self.p2.__str__()
	
	
#Polygon object, polygon is list of vertices
#polygon with no holes and with vertices given in counter-clockwise order
#Does NOT INCLUDE closing point, assume last point connects to first
class Polygon(GeometricObject):
	def __init__(self):
		vertices = [] #List of points
	
	#Loop over all points and apply transform
	def apply_transform(self, transform_matrix):
		for p in self.vertices:
			p.apply_transform(transform_matrix)
		return None
			
	#All geometric objects can be clipped to window, return the clipped object
	def clip_to_window(self,lower_bound_x, lower_bound_y,upper_bound_x, upper_bound_y):		
		#Sutherland-Hodgman does not account for polygons that 'leave' the window on one bound
		#and return into the window through another bound
		#Keep track of points of enter and exit
		#Then use those points to look up 
		#which points need to be inserted to complete polygon
		#Will be list of tuples ([ENTER|EXIT],<Point>)
		boundary_points = []
		
		#Make new list of vertices for this clipped polygon
		new_vertices = []
		#Loop over vertices
		#Easiest to loop through if has duplicate end vertex
		wduplicate = self.vertices + [self.vertices[0]]	
		for i in range(0,len(wduplicate)-1):
			current_v = wduplicate[i]
			next_v = wduplicate[i+1]
			#Make line using these
			line = Line()
			#Do not reference points, copy
			line.p1 = copy.deepcopy(current_v)
			line.p2 = copy.deepcopy(next_v)
			
			#Make copy that will not be modified
			orig_line = copy.deepcopy(line)
			
			#print "Clipping line p1->p2:"
			#print orig_line
						
			#Clip this line
			clipped_line = line.clip_to_window(lower_bound_x, lower_bound_y,upper_bound_x, upper_bound_y)
			if clipped_line is None:
				#No part of line this is in window
				#Do not add either vertex to new polygon
				#print "Line not in window"
				#print
				continue
			elif clipped_line == orig_line:
				#Line did not change
				#print "Line unchanged"
				#print orig_line,"=",clipped_line
				#print
				#Save these vertices
				new_vertices = new_vertices + [clipped_line.p1,clipped_line.p2]
			else:
				#Line was clipped		
				#print "Line clipped p1->p2:"
				#print clipped_line
				#Need to figure out if p1,p2 or both were clipped
				p1_clipped = not(clipped_line.p1 == orig_line.p1)
				p2_clipped = not(clipped_line.p2 == orig_line.p2)
				#print "P1 Clipped?:",p1_clipped
				#print "P2 Clipped?:",p2_clipped
				#Knowing points are in cc order
				#print
				#p1 clipped only means p1 entering
				#p2 clipped only means p2 exiting
				#If both points were clipped
				if p1_clipped:
					#Just p1 clipped
					enter_point = copy.deepcopy(clipped_line.p1)
					boundary_points = boundary_points + [(ENTER,enter_point)]
				if p2_clipped:
					#Just p2 clipped
					exit_point = copy.deepcopy(clipped_line.p2)
					boundary_points = boundary_points + [(EXIT,exit_point)]
				
				#Still save both points of clipped line
				new_vertices = new_vertices + [clipped_line.p1,clipped_line.p2]
				
		
		#Do we have boundary points to process?
		if len(boundary_points) <= 0:
			#No, return now
			self.vertices = new_vertices
			return self
		else:
			#Do boundary processing and return vertices
			verts = self.process_boundaries(new_vertices, boundary_points)
			self.vertices = verts
			return self
	
	#Do boundary processing and return vertices
	def process_boundaries(self, new_vertices, boundary_points):
		#First task is to remove duplicate points in new vertices
		#Start with first point in list
		#Then loop, if this point is identical to the one before it, dont add
		no_dups = [new_vertices[0]]
		for i in range(1,len(new_vertices)):
			if new_vertices[i] != new_vertices[i-1]:
				#NEw point, add to list
				no_dups = no_dups + [new_vertices[i]]
			
		#Now do second round of processing to insert boundary points
		#Need to find Exit->enter pairs
		#Re shape boudnary list for easier processing
		#If first element is enter, push to back 
		#want Exit then Enter in list
		if boundary_points[0][0] == ENTER:
			boundary_points = boundary_points[1:] + [boundary_points[0]]
			
		#Loop to process exit,enter pairs
		for i in range(0,len(boundary_points)-1):
			#Only look at element i if i is exit, i+1 is enter
			if boundary_points[i][0] == EXIT and boundary_points[i+1][0] == ENTER:
				#Look up points to insert, i
				#Insert them after the exit point int the vertices list
				exit_point = boundary_points[i][1]
				enter_point = boundary_points[i+1][1]
				points_to_insert = exit_enter_window_points_lookup(exit_point,enter_point)
				#Now loop through list of vertices and insert after exit
				for i in range(0,len(no_dups)):
					if no_dups[i] == exit_point:
						#Insert points after index i
						no_dups = no_dups[:i+1] + points_to_insert + no_dups[i+1:]
						#End now
						break
			else:
				#Go to next i, currently looking at backwards Enter,Exit pair
				continue
				
		return no_dups
				
		
	#Make lines from points, render points of lines
	def render_points(self):
		#Get list of lines
		lines = self.to_lines()
		
		#Convert each line to points
		points = []
		for line in lines:
			points = points + line.render_points()
			
		#Return list of points
		return points
	
	#Make lines from vertices
	#Lines list includes closing line and is in order of vertices
	def to_lines(self):
		lines = []
		#0-1,1-2, 2-3
		#Then 3-0
		for i in range(0,len(self.vertices)-1):
			tmp_line = None
			tmp_line = Line()
			tmp_line.p1 = Point()
			tmp_line.p2 = Point()
			tmp_line.p1.x = self.vertices[i].x
			tmp_line.p1.y = self.vertices[i].y
			tmp_line.p2.x = self.vertices[i+1].x
			tmp_line.p2.y = self.vertices[i+1].y
			lines = lines + [tmp_line]
			
		#Do final line from end to start
		tmp_line = None
		tmp_line = Line()
		tmp_line.p1 = Point()
		tmp_line.p2 = Point()
		tmp_line.p1.x = self.vertices[len(self.vertices)-1].x
		tmp_line.p1.y = self.vertices[len(self.vertices)-1].y
		tmp_line.p2.x = self.vertices[0].x
		tmp_line.p2.y = self.vertices[0].y
		lines = lines + [tmp_line]
		
		return lines
		
	#Equality operator	
	def __eq__(self, obj):
		self_vertices = self.vertices
		obj_vertices = obj.vertices
		if len(self_vertices) != len(obj_vertices):
			return False
		else:
			for i in range(0,len(self_vertices)):
				if self_vertices[i] != obj_vertices[i]:
					return False
		
		return True


#Determine if this point is on the x/y boundary and if on upper or lower
#Returns (is_x,is_lower)
def point_is_x_is_lower(p):
	#Determine if lower
	is_lower = None
	is_x = None
	if (p.x ==  global_vars.lower_bound_x) or (p.y ==  global_vars.lower_bound_y):
		is_lower = True
		if p.x ==  global_vars.lower_bound_x:
			is_x = True
		elif p.y ==  global_vars.lower_bound_y:
			is_x = False
		else:
			print "Point is lower but cannot determine X or Y",p
			print global_vars.lower_bound_x,global_vars.lower_bound_y
	elif (p.x ==  global_vars.upper_bound_x) or (p.y ==  global_vars.upper_bound_y):
		is_lower = False
		if p.x ==  global_vars.upper_bound_x:
			is_x = True
		elif p.y ==  global_vars.upper_bound_y:
			is_x = False
		else:
			print "Point is upper but cannot determine X or Y",p
			print global_vars.upper_bound_x,global_vars.upper_bound_y
	else:
		print "Point is neither an upper or lower boundary",p
		print global_vars.lower_bound_x,global_vars.lower_bound_y,global_vars.upper_bound_x,global_vars.upper_bound_y
	
	return is_x,is_lower	


#Sutherland-Hodgman does not account for polygons that 'leave' the window on one bound
def exit_enter_window_points_lookup(exit_point,enter_point):
	#Get boundary info
	#Use that information to get points to insert
	exit_is_x, exit_is_lower = point_is_x_is_lower(exit_point)
	enter_is_x, enter_is_lower = point_is_x_is_lower(enter_point)
		
	#Knowing that vertices are given in counter-clockwise order
	#Knowing where the exit and enter points will let us know which
	#Window corners will become part of clipped polygon
	TOP_LEFT = Point()
	TOP_RIGHT = Point()
	BOT_LEFT = Point()
	BOT_RIGHT = Point()
	
	TOP_LEFT.x = global_vars.lower_bound_x
	TOP_LEFT.y = global_vars.upper_bound_y
	
	TOP_RIGHT.x = global_vars.upper_bound_x
	TOP_RIGHT.y = global_vars.upper_bound_y
	
	BOT_LEFT.x = global_vars.lower_bound_x
	BOT_LEFT.y = global_vars.lower_bound_y
	
	BOT_RIGHT.x = global_vars.upper_bound_x
	BOT_RIGHT.y = global_vars.lower_bound_y
	
	#This is annoying. I think Weiler-Atherton Algorithm might
	#fix this but we are supposed to do Sutherland-Hodgman
	#Instead of lookup as if's, could do index list but would require 'circular list'
	#Also may be smarter to set point x and y individually?
	#Also, I'm screwed if we every clip to non rectangular windows
	if (exit_is_x==False) and (exit_is_lower==False) and (enter_is_x==False) and (enter_is_lower==False):
		#Leaving upper y
		#Entering upper y
		#No additional points needed
		return []
	elif(exit_is_x==False) and (exit_is_lower==False) and (enter_is_x==False) and (enter_is_lower==True):
		#Leaving upper y
		#Entering lower y
		return [TOP_LEFT,BOT_LEFT]
	elif(exit_is_x==False) and (exit_is_lower==False) and (enter_is_x==True) and (enter_is_lower==False):
		#Leaving upper y
		#Entering upper x
		return [TOP_LEFT,BOT_LEFT,BOT_RIGHT]
	elif(exit_is_x==False) and (exit_is_lower==False) and (enter_is_x==True) and (enter_is_lower==True):
		#Leaving upper y
		#Entering lower x
		return [TOP_LEFT]
	elif(exit_is_x==False) and (exit_is_lower==True) and (enter_is_x==False) and (enter_is_lower==False):
		#Leaving lower y
		#Entering upper y
		return [BOT_RIGHT,TOP_RIGHT]
	elif(exit_is_x==False) and (exit_is_lower==True) and (enter_is_x==False) and (enter_is_lower==True):
		#Leaving lower y
		#Entering lower y
		#No additional points needed
		return []
	elif(exit_is_x==False) and (exit_is_lower==True) and (enter_is_x==True) and (enter_is_lower==False):
		#Leaving lower y
		#Entering upper x
		return [BOT_RIGHT]
	elif(exit_is_x==False) and (exit_is_lower==True) and (enter_is_x==True) and (enter_is_lower==True):	
		#Leaving lower y
		#Entering lower x
		return [BOT_RIGHT,TOP_RIGHT,TOP_LEFT]
	elif(exit_is_x==True) and (exit_is_lower==False) and (enter_is_x==False) and (enter_is_lower==False):
		#Leaving upper x
		#Entering upper y
		return [TOP_RIGHT]
	elif(exit_is_x==True) and (exit_is_lower==False) and (enter_is_x==False) and (enter_is_lower==True):
		#Leaving upper x
		#Entering lower y
		return [TOP_RIGHT,TOP_LEFT,BOT_LEFT]
	elif(exit_is_x==True) and (exit_is_lower==False) and (enter_is_x==True) and (enter_is_lower==False):
		#Leaving upper x
		#Entering upper x
		#No additional points needed
		return []
	elif(exit_is_x==True) and (exit_is_lower==False) and (enter_is_x==True) and (enter_is_lower==True):
		#Leaving upper x
		#Entering lower x
		return [TOP_RIGHT,TOP_LEFT]
	elif(exit_is_x==True) and (exit_is_lower==True) and (enter_is_x==False) and (enter_is_lower==False):
		#Leaving lower x
		#Entering upper y
		return [BOT_LEFT,BOT_RIGHT,TOP_RIGHT]
	elif(exit_is_x==True) and (exit_is_lower==True) and (enter_is_x==False) and (enter_is_lower==True):
		#Leaving lower x
		#Entering lower y
		return [BOT_LEFT]
	elif(exit_is_x==True) and (exit_is_lower==True) and (enter_is_x==True) and (enter_is_lower==False):
		#Leaving lower x
		#Entering upper x
		return [BOT_LEFT,BOT_RIGHT]
	elif(exit_is_x==True) and (exit_is_lower==True) and (enter_is_x==True) and (enter_is_lower==True):
		#Leaving lower x
		#Entering lower x
		#No additional points needed
		return []
	else:
		print "Binary black magic. Missed a case apparently..."
		print exit_is_x, exit_is_lower,enter_is_x,enter_is_lower
		return None

#Do transformation for each line, return list of changed lines
def transform_objects(objects, scale,rotation_cc, trans_x, trans_y, trans_z=0):
	#Construct transform matrices
	#Scale
	scale_matrix = matrix.identity_matrix(4,4)
	scale_matrix[0,0] = scale
	scale_matrix[1,1] = scale
	scale_matrix[2,2] = scale
	#Rotation (around Z axis)
	rads = rotation_cc * (math.pi/180.0)
	rotation_matrix = matrix.identity_matrix(4,4)
	rotation_matrix[0,0] = math.cos(rads)
	rotation_matrix[1,0] = math.sin(rads) 
	rotation_matrix[0,1] = -1 * math.sin(rads)
	rotation_matrix[1,1] = math.cos(rads)
	#Translation
	translation_matrix = matrix.identity_matrix(4,4)
	translation_matrix[0,3] = trans_x
	translation_matrix[1,3] = trans_y
	translation_matrix[2,3] = trans_x
	
	#Multiply for one transform matrix
	transform_matrix = translation_matrix * (rotation_matrix * scale_matrix)
	
	#Loop over each geometric object
	for obj in objects:
		#Apply transform to each object
		obj.apply_transform(transform_matrix)
	
	#Return modified objects
	return objects

#Clip lines to windows
def	clip_geometric_objects_to_window(objects, lower_bound_x, lower_bound_y,upper_bound_x, upper_bound_y,recursion_count=0):
	#Keep list of objects
	rv_objs = []
	#Loop over original objects and clip
	for obj in objects:
		new_obj = obj.clip_to_window(lower_bound_x, lower_bound_y,upper_bound_x, upper_bound_y)
		if new_obj != None:
			rv_objs = rv_objs + [new_obj]
	return rv_objs

#Function that evaluates =m*var + b
def line_func(m, var, b):
	rv = m*var + b
	return rv
	
#Convert lines into list of points
def geometric_objects_to_points(objects):
	#Loop over all geometric objects and collect list of points
	rv = []
	for obj in objects:
		new_points = obj.render_points()
		rv = rv + new_points
	return rv
	
def points_to_pixel_map(points, lower_bound_x, lower_bound_y, upper_bound_x, upper_bound_y):
	#Allocate a blank 2d matrix to serve as the pixel map
	#Pixel map is sized according to view window
	#Columns = X size, Rows = Y size
	xdim = upper_bound_x-lower_bound_x+1
	ydim = upper_bound_y-lower_bound_y+1
	pixel_map = matrix.zeros_matrix(xdim,ydim)

	#Loop over each point
	for point in points:
		#World
		world_x = point.x
		world_y = point.y
		#Pixel map
		pixel_x = int( world_x - lower_bound_x ) - 1
		pixel_y = int( upper_bound_y - world_y ) - 1
				
		#Cheap check...bleh
		if(pixel_x < 0):
			pixel_x = 0
		if(pixel_y < 0):
			pixel_y = 0
		
		#Write something... a 1?
		pixel_map[pixel_y,pixel_x] = 1.0

	return pixel_map
