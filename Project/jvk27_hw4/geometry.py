#!/usr/bin/env python

import matrix
import math
import sys
import copy #For object copying
import global_vars
import gen_utils
import numpy #For matrix operations

#Enter exit text consts for polygon clipping
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
	
	#Convert points to matrix (for transforms, uses 4D coords)
	def to_matrix(self):
		point_matrix = matrix.zeros_matrix(1,4)
		point_matrix[0,0] = self.x
		point_matrix[1,0] = self.y
		point_matrix[2,0] = self.z
		point_matrix[3,0] = 1.0
		return point_matrix
		
	#Convert points to 3D vector (for projections, uses 3D coords)
	def to_vector3d(self):
		v = numpy.array([self.x,self.y,self.z])
		return v
		
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
	def __ne__(self, obj):
		return not( self.__eq__(obj) )
		
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
		#This function experiences a weird floating point issue
		#To see the issue set global variable this flag to True
		
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
			#This is where floating point issue occurs
			#Get line value as FP
			func_val_f = line_func(m,var,b)
			#Broken conversion to int
			func_val_i = int(func_val_f)
			#Spent ~6 hours to find that for some reason this occurs
			# func_val_f = 172.0
			# func_val_i = 171
			#WHHAAAATTT!?
			#Happens multiple times too, must be weird FP issue
			#This is working FP to int conversion, 
			#shouldnt be different from above though
			#Round FP first, then convert to int
			func_val_f_rounded = round(func_val_f)
			func_val_f_rounded_i = int(func_val_f_rounded)
			#^That works correctly...
			if global_vars.use_broken_fp:
				func_val_to_use_i = func_val_i
			else:
				func_val_to_use_i = func_val_f_rounded_i
		
			x=0
			y=0	
			if(is_y_mx_b==True):
				#Loop variable is x
				x = var
				y = func_val_to_use_i
			else:
				#Loop variable is y
				x = func_val_to_use_i
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
		
	#Find intersection point of two lines
	#Returns point or None (None is same line or parallel)
	def get_intersection_point(self,other_line):
		#Avoid thinking. Copying algorithm from parametric line intersection:
		#http://www.ahinson.com/algorithms_general/Sections/Geometry/ParametricLineIntersection.pdf
		#s, t are time/percents vars
		#Self line is points 1 and 2
		x1 = self.p1.x
		y1 = self.p1.y
		x2 = self.p2.x
		y2 = self.p2.y
		#Other line is points 3 and 4
		x3 = other_line.p1.x
		y3 = other_line.p1.y
		x4 = other_line.p2.x
		y4 = other_line.p2.y
		
		#s is percent for first line
		x21 = x2 - x1
		y21 = y2 - y1
		x31 = x3 - x1
		y31 = y3 - y1
		x43 = x4 - x3
		y43 = y4 - y3
		
		s_numerator = x43*y31 - x31*y43
		s_denom = x43*y21 - x21*y43
		
		#Check for parallel
		if s_denom == 0:
			return None
		
		#Calc s percent
		s = float(s_numerator)/float(s_denom)
		#Check if in bounds of line
		if (0 <= s) and (s <= 1):
			#Return intersection point
			x = x1 + (x2 - x1)*s
			y = y1 + (y2 - y1)*s
			rv = Point()
			rv.x = x
			rv.y = y
			return rv
		else:
			#Lines intersect elsewhere
			return None
	
	#Equality operator	
	def __eq__(self, obj):
		return (self.p1==obj.p1) and (self.p2==obj.p2)
	def __ne__(self, obj):
		return not( self.__eq__(obj) )
		
	#To string operator
	def __str__(self):
		return self.p1.__str__() + "->" + self.p2.__str__()
	
	
#Polygon object, polygon is list of vertices
#polygon with no holes and with vertices given in counter-clockwise order
#Does NOT INCLUDE closing point, assume last point connects to first
class Polygon(GeometricObject):
	vertices = [] #List of points
	def __init__(self):
		self.vertices = [] #List of points
	
	#Loop over all points and apply transform
	def apply_transform(self, transform_matrix):
		for p in self.vertices:
			p.apply_transform(transform_matrix)
		return None
			
	#All geometric objects can be clipped to window, return the clipped object
	def clip_to_window(self,lower_bound_x, lower_bound_y,upper_bound_x, upper_bound_y):
		#Sutherland-Hodgman does not account for polygons that 'leave' the window on one bound
		#and return into the window through another bound (ex. leave through top, enter through bottom)
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
		rv = None
		if len(boundary_points) <= 0:
			#No, return now
			self.vertices = new_vertices
			rv = self
		else:
			#Do boundary processing and return vertices
			verts = self.process_boundaries(new_vertices, boundary_points, lower_bound_x, lower_bound_y, upper_bound_x, upper_bound_y)
			self.vertices = verts
			rv = self
			
		#Remove duplicate vertices
		self.vertices = gen_utils.remove_ordered_duplicates(self.vertices)
			
		#Before returning, final check of if the whole polygon was clipped away
		if len(self.vertices) <= 0:
			return None
		elif len(self.vertices) <= 2:
			#Clipped down to a line?
			#print "Polygon clipped to line?"
			return None
		else:
			return rv
	
	#Do boundary processing and return vertices
	def process_boundaries(self, new_vertices, boundary_points, lower_bound_x, lower_bound_y, upper_bound_x, upper_bound_y):
		#First task is to remove duplicate points in new vertices
		#Start with first point in list
		#Then loop, if this point is identical to the one before it, dont add
		no_dups = gen_utils.remove_ordered_duplicates(new_vertices)
			
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
				points_to_insert = exit_enter_window_points_lookup(exit_point,enter_point, lower_bound_x, lower_bound_y, upper_bound_x, upper_bound_y)
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
	#Also need to do filling here too
	def render_points(self,do_filling = False):
		#First get points from poly outline
		outline_points = []
		#Get list of lines
		lines = self.to_lines()
		for line in lines:
			outline_points = outline_points + line.render_points()
		
		#Then get fill points
		if do_filling:
			fill_points = self.get_fill_points()
			rv = outline_points + fill_points
		else:
			rv = outline_points	
		
		#Return list of points
		return rv
		
	#Return bounding box for this poly
	#Return upper,lower points
	def get_bounding_box_points(self):
		#Find min and max x and y values
		minx = 99999
		miny = 99999
		maxx = -99999
		maxy = -99999
		for v in self.vertices:
			if v.x < minx:
				minx = v.x
			if v.y < miny:
				miny = v.y
			if v.x > maxx:
				maxx = v.x
			if v.y > maxy:
				maxy = v.y
				
		bottom_left = Point()
		bottom_left.x = minx
		bottom_left.y = miny
		top_right = Point()
		top_right.x = maxx
		top_right.y = maxy
		
		return top_right,bottom_left
		
	#Get list of points that fill the interior of the polygon
	def get_fill_points(self):
		#Fill points to return
		rv = []
		#First determine scan line ranges
		top_right,bottom_left = self.get_bounding_box_points()
		
		#Scan lines are horizontal, loop over Y range
		for y in range(int(bottom_left.y),int(top_right.y+1)):
			#Fill points just for this scan line
			scan_line_fill_points = []
			
			#Scan line goes from xmin to x max
			scan_line_p1 = Point()
			scan_line_p1.x = bottom_left.x
			scan_line_p1.y = y
			scan_line_p2 = Point()
			scan_line_p2.x = top_right.x
			scan_line_p2.y = y
			scan_line = Line()
			#The whole line
			scan_line.p1 = scan_line_p1
			scan_line.p2 = scan_line_p2
			
			#For this scan line collect intsection points
			intersection_points = []
			#of all lines from poly
			poly_lines = self.to_lines()
			for poly_line in poly_lines:
				intersection = poly_line.get_intersection_point(scan_line)
				if not(intersection is None):
					#Add intersection point to list
					intersection_points = intersection_points + [intersection]
					
			#Sort the interesection points by x values (for scanning left to right)
			intersection_points.sort(key = lambda p: p.x) #Pythonic indeed
			
			#Remove duplicate intersection points
			intersection_points = gen_utils.remove_ordered_duplicates(intersection_points)
		
			#Process points in groups of 2
			#    p0      p1       p2        p3
			#    enter   exit      enter     exit
			# line p0->p1   and line p2->p3
			i = 0
			p0_is_enter = True
			while i < (len(intersection_points) - 1):
				#Look at two points
				p0 = intersection_points[i]
				p1 = intersection_points[i+1]
				#Get points on this line, dont store yet
				fill_line = Line()
				fill_line.p1 = p0
				fill_line.p2 = p1
				#Get points on this fill line
				scan_line_fill_points = fill_line.render_points()
				
				#If this is an entering point, draw line
				if p0_is_enter:
					rv = rv + scan_line_fill_points
					
				#Now detemine what to do with next point	
				#Determine if next intersection point is entering or exiting
				#If the next intsection point is not a vertex it must be exiting
				if not(p1 in self.vertices):
					#print "p1 NOT in self.vertices"
					#Since p1 is exiting, incrementt i by 2 so next iteration p0 enters
					p0_is_enter = True
					#Inrement i by 2
					i = i + 2
				else:
					#print "p1 in self.vertices"
					#p1 is a vertex
					#Need to decide if it is an entering vertex or exiting
					#Find the index of this vertex in the poly vertex list
					index = -1
					for j in range(0, len(self.vertices)):
						if self.vertices[j] == p1:
							#Found at index i
							index = j
							break
					if index == -1:
						print "Could not find vertex?"
					else:
						#Knowing vertices are in CC order
						#And knowing scan lines are horozontal
						#The vertex to the right of p1 determines if p1 is entering or exiting
						vertex_right_of_p1 = None
						vertex_before_p1 = None #before after in CC order
						vertex_after_p1 = None
						
						#print "len(self.vertices)",len(self.vertices)
						#print "vertex index",index
						
						#Check if this vertex is at beginning or end of list
						#Beginning
						if index == 0:
							#First vertex in list, so 'before' that is last vertex
							vertex_before_p1 = self.vertices[len(self.vertices)-1]
							vertex_after_p1 = self.vertices[1]
						#End of list
						elif index == len(self.vertices) - 1:
							vertex_before_p1 = self.vertices[len(self.vertices)-2]
							vertex_after_p1 = self.vertices[0]
						#Middle of list
						else:
							vertex_before_p1 = self.vertices[index - 1]
							vertex_after_p1 = self.vertices[index + 1]
							
						#Select vertex to right of p1
						if vertex_before_p1.x >= p1.x:
							vertex_right_of_p1 = vertex_before_p1
						elif vertex_after_p1.x >= p1.x:
							vertex_right_of_p1 = vertex_after_p1
						else:
							#No vertex to right? Points saved by now
							#Just exit
							break;
							
						#Need to know if this vertex was before or after and above or below p1
						vertex_right_of_p1_is_above = (vertex_right_of_p1.y >= p1.y)
						vertex_right_of_p1_is_before = (vertex_right_of_p1 == vertex_before_p1)
						
						if vertex_right_of_p1_is_above and vertex_right_of_p1_is_before:
							#Above and before, entering
							#Increment i by 1, next p0 is entering
							p0_is_enter = True
							i = i+1
						elif vertex_right_of_p1_is_above and not(vertex_right_of_p1_is_before):
							#Above and after, exiting
							#Since p1 is exiting, increment i by 2 so next iteration p0 enters
							p0_is_enter = True
							#Inrement i by 2
							i = i + 2
						elif not(vertex_right_of_p1_is_above) and vertex_right_of_p1_is_before:
							#Below and before, exiting
							#Since p1 is exiting, increment i by 2 so next iteration p0 enters
							p0_is_enter = True
							#Inrement i by 2
							i = i + 2
						elif not(vertex_right_of_p1_is_above) and not(vertex_right_of_p1_is_before):
							#Below and and after, entering
							#Increment i by 1, next p0 is entering
							p0_is_enter = True
							i = i+1
						else:
							print "Whoops! Issue with vertex above and below section?"
							
		#Return the fill points
		return rv	
	
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
	def __ne__(self, obj):
		return not( self.__eq__(obj) )
		
	#To string operator
	def __str__(self):
		#Print vertices
		rv = "["
		for i in range(0,len(self.vertices)):
			v = self.vertices[i]
			rv = rv + str(v)
			if i != len(self.vertices)-1:
				rv = rv + ","
			else:
				rv = rv + "]"
		return rv

#Determine if this point is on the x/y boundary and if on upper or lower
#Returns (is_x,is_lower)
def point_is_x_is_lower(p, lower_bound_x, lower_bound_y, upper_bound_x, upper_bound_y):
	#Determine if lower
	is_lower = None
	is_x = None
	if (p.x ==  lower_bound_x) or (p.y ==  lower_bound_y):
		is_lower = True
		if p.x ==  lower_bound_x:
			is_x = True
		elif p.y ==  lower_bound_y:
			is_x = False
		else:
			print "Point is lower but cannot determine X or Y",p
			print lower_bound_x,lower_bound_y
	elif (p.x ==  upper_bound_x) or (p.y ==  upper_bound_y):
		is_lower = False
		if p.x ==  upper_bound_x:
			is_x = True
		elif p.y ==  upper_bound_y:
			is_x = False
		else:
			print "Point is upper but cannot determine X or Y",p
			print upper_bound_x,upper_bound_y
	else:
		print "Point is neither an upper or lower boundary",p
		print lower_bound_x,lower_bound_y,upper_bound_x,upper_bound_y
	
	return is_x,is_lower	


#Sutherland-Hodgman does not account for polygons that 'leave' the window on one bound
def exit_enter_window_points_lookup(exit_point,enter_point, lower_bound_x, lower_bound_y, upper_bound_x, upper_bound_y):
	#Get boundary info
	#Use that information to get points to insert
	exit_is_x, exit_is_lower = point_is_x_is_lower(exit_point, lower_bound_x, lower_bound_y, upper_bound_x, upper_bound_y)
	enter_is_x, enter_is_lower = point_is_x_is_lower(enter_point, lower_bound_x, lower_bound_y, upper_bound_x, upper_bound_y)
		
	#Knowing that vertices are given in counter-clockwise order
	#Knowing where the exit and enter points will let us know which
	#Window corners will become part of clipped polygon
	TOP_LEFT = Point()
	TOP_RIGHT = Point()
	BOT_LEFT = Point()
	BOT_RIGHT = Point()
	
	TOP_LEFT.x = lower_bound_x
	TOP_LEFT.y = upper_bound_y
	
	TOP_RIGHT.x = upper_bound_x
	TOP_RIGHT.y = upper_bound_y
	
	BOT_LEFT.x = lower_bound_x
	BOT_LEFT.y = lower_bound_y
	
	BOT_RIGHT.x = upper_bound_x
	BOT_RIGHT.y = lower_bound_y
	
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
		print "Missed a case apparently..."
		print exit_is_x, exit_is_lower,enter_is_x,enter_is_lower
		return None
	
#Return scale tranform matrix 
def get_scale_matrix(scale_x,scale_y,scale_z=1):
	scale_matrix = matrix.identity_matrix(4,4)
	scale_matrix[0,0] = scale_x
	scale_matrix[1,1] = scale_y
	scale_matrix[2,2] = scale_z
	return scale_matrix
	
#Return rotation around Z axis tranform matrix
def get_rotation_zaxis_matrix(rotation_cc):
	rads = rotation_cc * (math.pi/180.0)
	rotation_matrix = matrix.identity_matrix(4,4)
	rotation_matrix[0,0] = math.cos(rads)
	rotation_matrix[1,0] = math.sin(rads) 
	rotation_matrix[0,1] = -1 * math.sin(rads)
	rotation_matrix[1,1] = math.cos(rads)
	return rotation_matrix

#Return translation matrix
def get_translation_matrix(trans_x, trans_y, trans_z=0):
	translation_matrix = matrix.identity_matrix(4,4)
	translation_matrix[0,3] = trans_x
	translation_matrix[1,3] = trans_y
	translation_matrix[2,3] = trans_z
	return translation_matrix
	
#Do transformation for each line, return list of transformed objects
def transform_objects(objects, scale,rotation_cc, trans_x, trans_y, trans_z=0):
	#Construct transform matrices
	#Scale (same in xyz)
	scale_matrix = get_scale_matrix(scale,scale,scale)
	#Rotation (around Z axis)
	rotation_matrix = get_rotation_zaxis_matrix(rotation_cc)
	#Translation
	translation_matrix = get_translation_matrix(trans_x, trans_y, trans_z)
	
	#Multiply for one transform matrix
	transform_matrix = translation_matrix * (rotation_matrix * scale_matrix)
	
	#Loop over each geometric object
	for obj in objects:
		#Apply transform to each object
		obj.apply_transform(transform_matrix)
	
	#Return modified objects
	return objects
	
#Do viewport transformation, return list of transformed objects
def viewport_transform(objects,lower_bound_x, lower_bound_y,upper_bound_x, upper_bound_y, vp_lower_bound_x, vp_lower_bound_y, vp_upper_bound_x, vp_upper_bound_y):
	#Rename vars for ease
	xmin = float(lower_bound_x)
	ymin = float(lower_bound_y)
	xmax = float(upper_bound_x)
	ymax = float(upper_bound_y)
	umin = float(vp_lower_bound_x)
	vmin = float(vp_lower_bound_y)
	umax = float(vp_upper_bound_x)
	vmax = float(vp_upper_bound_y)
	
	#3 steps 
	#1. Translate to world origin
	first_translate_matrix = get_translation_matrix(-1*xmin, -1*ymin, 0)
	#2. Scale
	scale_matrix = get_scale_matrix((umax-umin)/(xmax-xmin), (vmax-vmin)/(ymax-ymin),1)
	#3. Translate to viewport
	second_translate_matrix = get_translation_matrix(umin,vmin,0)
	
	#Form single tranform matrix
	transform_matrix = second_translate_matrix * (scale_matrix * first_translate_matrix)
	
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
		if not(new_obj is None):
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
	
#Return pixel map from list of points given points and output image size
def points_to_pixel_map(points, xdim, ydim):
	#Allocate a blank 2d matrix to serve as the pixel map
	#Pixel map is sized according to given image size
	#Columns = X size, Rows = Y size
	pixel_map = matrix.zeros_matrix(xdim,ydim)

	#Loop over each point
	for point in points:
		#World
		world_x = point.x
		world_y = point.y
		#Pixel map
		lower_bound_x = 0 #Always zero?
		upper_bound_y = ydim-1
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
	
def points_to_pixel_map_old(points, lower_bound_x, lower_bound_y, upper_bound_x, upper_bound_y):
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

#Get rotation transform matrix
def get_rotation_3d_matrix(vpn_x, vpn_y, vpn_z, vup_x, vup_y, vup_z):
	#Get vpn and vup into vector/matrices
	vpn_point = Point()
	vpn_point.x = vpn_x
	vpn_point.y = vpn_y
	vpn_point.z = vpn_z
	vpn_vec3d = vpn_point.to_vector3d()
	vup_point = Point()
	vup_point.x = vup_x
	vup_point.y = vup_y
	vup_point.z = vup_z
	vup_vec3d  = vup_point.to_vector3d()
	
	#Calc R X,Y,Z vectors
	#|v| = sqrt(v dot v)
	Rz = numpy.divide(vpn_vec3d , matrix.magnitude(vpn_vec3d))
	Rx = numpy.divide( numpy.cross(vup_vec3d,Rz), matrix.magnitude(numpy.cross(vup_vec3d,Rz)) )
	Ry = numpy.cross(Rz,Rx)
	
	#Populate 4D transform matrix
	m = matrix.identity_matrix(4,4)
	r1x = Rx[0]
	r2x = Rx[1]
	r3x = Rx[2]
	r1y = Ry[0]
	r2y = Ry[1]
	r3y = Ry[2]
	r1z = Rz[0]
	r2z = Rz[1]
	r3z = Rz[2]
	m[0,0] = r1x
	m[0,1] = r2x
	m[0,2] = r3x
	m[1,0] = r1y
	m[1,1] = r2y
	m[1,2] = r3y
	m[2,0] = r1z
	m[2,1] = r2z
	m[2,2] = r3z
	return m
	
#Return shear transform matrix (same for parallel and perspective)
def get_shear_3d_matrix(umin, umax, vmin, vmax, prpu, prpv, prpn):
	#Calc shx and y values to fill in matrix
	shx = (0.5*(umax+umin) - prpu) / prpn
	shy = (0.5*(vmax+vmin) - prpv) / prpn
	
	#Populate 4D transform matrix
	m = matrix.identity_matrix(4,4)
	m[0,2] = shx
	m[1,2] = shy
	return m

#Return parallel normalizing tranformation matrix
def get_parallel_normalizing_tranformation_matrix(vrp_x, vrp_y, vrp_z, vpn_x, vpn_y, vpn_z, vup_x, vup_y, vup_z, vrc_u_min, vrc_u_max, vrc_v_min, vrc_v_max, prp_x, prp_y, prp_z, F, B):
	#Get individual matrices for transform, use variable names from slides
	#Translate VRP to the origin
	T = get_translation_matrix(-1.0 * vrp_x, -1.0 * vrp_y, -1.0 * vrp_z)
	#Rotate VPN rotated to z, VUP rotated to y
	R = get_rotation_3d_matrix(vpn_x, vpn_y, vpn_z, vup_x, vup_y, vup_z)
	#Parallel shear
	SHpar = get_shear_3d_matrix(vrc_u_min, vrc_u_max, vrc_v_min, vrc_v_max, prp_x, prp_y, prp_z)
	#Translate the center of the volume to the origin 
	Tpar = get_translation_matrix(-1.0*(vrc_u_max+vrc_u_min)/2.0,-1.0*(vrc_v_max+vrc_v_min)/2.0, -1.0*F)		
	#Scaling to 2x2x1
	Spar = get_scale_matrix(2.0/(vrc_u_max-vrc_u_min), 2.0/(vrc_v_max-vrc_v_min), 1.0/(F-B) )
	
	#Debug steps of multiplying
	#~ step0 = T
	#~ step1 = R*step0
	#~ step2 = SHpar*step1
	#~ step3 = Tpar*step2
	#~ step4 = Spar*step3
	#~ print "step0",step0
	#~ print "step1",step1
	#~ print "step2",step2
	#~ print "step3",step3
	#~ print "step4",step4	
	
	#Multiply all together and return
	Npar = (Spar * (Tpar * (SHpar * (R*T))))
	return Npar
	
#Return Sper perspective scale matrix
def get_perspective_scale_transform_matrix(prp_z, vrc_u_min, vrc_u_max, vrc_v_min, vrc_v_max, B):
	vrp_prime_z = -1.0 * prp_z
	sx = (2*vrp_prime_z) / ( (vrc_u_max-vrc_u_min)*(vrp_prime_z+B) )
	sy = (2*vrp_prime_z) / ( (vrc_v_max-vrc_v_min)*(vrp_prime_z+B) )
	sz = -1.0 / (vrp_prime_z+B)	
	return get_scale_matrix(sx,sy,sz)
	
#Return perspective normalizing tranformation matrix
def get_perspective_normalizing_tranformation_matrix(vrp_x, vrp_y, vrp_z, vpn_x, vpn_y, vpn_z, vup_x, vup_y, vup_z, vrc_u_min, vrc_u_max, vrc_v_min, vrc_v_max, prp_x, prp_y, prp_z, F, B):
	#Get individual matrices for transform, use variable names from slides
	#Translate VRP to the origin
	T_VRP = get_translation_matrix(-1.0 * vrp_x, -1.0 * vrp_y, -1.0 * vrp_z)
	#Rotate VPN rotated to z, VUP rotated to y
	R = get_rotation_3d_matrix(vpn_x, vpn_y, vpn_z, vup_x, vup_y, vup_z)
	#Translate COP to origin T(-PRP)
	T_PRP = get_translation_matrix(-1.0 * prp_x, -1.0 * prp_y, -1.0 * prp_z)
	#Perspective shear is same as parallel shear
	SHpar = get_shear_3d_matrix(vrc_u_min, vrc_u_max, vrc_v_min, vrc_v_max, prp_x, prp_y, prp_z)
	#Scale into a canonical view volume for clipping
	Sper = get_perspective_scale_transform_matrix(prp_z, vrc_u_min, vrc_u_max, vrc_v_min, vrc_v_max, B)

	#Multiply all together and return
	Nper = (Sper * (SHpar * (T_PRP * (R * T_VRP))))
	return Nper

#Return normalizing transformation matricies
def get_npar_nper(vrp_x, vrp_y, vrp_z, vpn_x, vpn_y, vpn_z, vup_x, vup_y, vup_z, vrc_u_min, vrc_u_max, vrc_v_min, vrc_v_max, prp_x, prp_y, prp_z, F, B):
	npar = get_parallel_normalizing_tranformation_matrix(vrp_x, vrp_y, vrp_z, vpn_x, vpn_y, vpn_z, vup_x, vup_y, vup_z, vrc_u_min, vrc_u_max, vrc_v_min, vrc_v_max, prp_x, prp_y, prp_z, F, B)
	nper = get_perspective_normalizing_tranformation_matrix(vrp_x, vrp_y, vrp_z, vpn_x, vpn_y, vpn_z, vup_x, vup_y, vup_z, vrc_u_min, vrc_u_max, vrc_v_min, vrc_v_max, prp_x, prp_y, prp_z, F, B)
	return npar,nper
	
#Apply transformation matricies, applied matrix depends on parallel v.s. perspective switch
#Return modified models
def apply_par_per_transforms(smf_models,npar,nper,use_parallel_projection):
	#Select which transform to use
	transform_matrix = None
	if use_parallel_projection:
		transform_matrix = npar
	else:
		transform_matrix = nper
	
	#Apply the appropriate transform to the smf models
	for smf_model in smf_models:
		smf_model.apply_transform(transform_matrix)
		
	return smf_models
	
#Perform trivial reject test with view volume 
#Return modified models
def trivial_test_reject(smf_models):
	return None
	
#Perform parallel projection or perform perspective projection 
#Return modified models
def perform_projection(smf_models,use_parallel_projection, prp_z, B):
	#Select which projection to use
	if use_parallel_projection:
		#Parallel just drops the Z value, nothing to do here
		#since further steps dont look at Z value
		pass
	else:
		#Perspective divides x and y by z/d, z is just d
		d = prp_z / (B - prp_z)
		#Loop over all models
		for smf_model in smf_models:
			#Loop over all vertices
			for vertex in smf_model.vertices:
				#Do z/d division
				z = vertex.z
				vertex.x = vertex.x / (z/d)
				vertex.y = vertex.y / (z/d)
				vertex.z = d
			#Updates faces after changes vertices
			smf_model.rebuild_faces_list()
	
	return smf_models
	
#Render the model into polygons (geometric objects)
#Return list of polys
def render_smf_to_polys(smf_models):
	#Loop over models and return list of all polys
	all_polys = []
	for smf_model in smf_models:
		#Rebuild faces before rendering polys
		smf_model.rebuild_faces_list()
		polys = smf_model.faces
		all_polys = all_polys + polys
	return all_polys

#Transform from normalized view volume to viewport
#Return modified smf models
def do_normalized_window_to_viewport_transform(smf_models, prp_z, B, vp_lower_bound_x, vp_lower_bound_y, vp_upper_bound_x, vp_upper_bound_y, use_parallel_projection):
	#Undo normalizing tranformations from earlier
	#Select which d value to use
	if use_parallel_projection:
		d = 1.0
	else:
		#Perspective divides x and y by z/d, z is just d
		d = float(prp_z / (B - prp_z))
		#Apparently missed a negative when copying from slides?
		d = -1.0*d
	
	#First translate
	T_d = get_translation_matrix(d,d,0)
	#Scale
	S = get_scale_matrix( (vp_upper_bound_x-vp_lower_bound_x)/(2*d), (vp_upper_bound_y-vp_lower_bound_y)/(2*d), 1.0 )
	#Translate again (viewport)
	T_vp = get_translation_matrix(vp_lower_bound_x,vp_lower_bound_y,0)
	#Combine
	transform_matrix = T_vp * (S * T_d)
	
	#Apply to all vertices of the smf_models
	#Loop over all models
	for smf_model in smf_models:
		#Loop over all vertices
		for vertex in smf_model.vertices:
			vertex.apply_transform(transform_matrix)
		#Rebuild faces list after vertex modification
		smf_model.rebuild_faces_list()
	
	return smf_models
	
	
	
	
	
	
	
	
	
	
	
