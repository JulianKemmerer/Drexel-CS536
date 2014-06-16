#!/usr/bin/env python
import sys

def do_xpm_write(pixel_map):
	#Cheat and hard code the header and color for now
	print "/* XPM */"
	print "static char *sco100[] = {"
	print "/* width height num_colors chars_per_pixel */"
	#Numpy matrix property
	rows,columns = pixel_map.shape	
	width = columns;
	height = rows;
	num_colors = 2;
	chars_per_pixel = 1;
	print '"{0} {1} {2} {3}"'.format(width,height,num_colors,chars_per_pixel)
	print "/* colors */"
	print "\"X c #000000\"," #X for black
	print "\"- c #ffffff\"," #- for white
	print "/* pixels */"
	#Write pixels
	#Print row wise, inner loop is across columns
	#Pixel map is a matrix addressed as pixel_map[y,x] 
	
	for row in range(0,height): #Y
		#New row, write open quote
		sys.stdout.write('"')
		for col in range(0,width): #X
			#Write chars
			if pixel_map[row,col] > 0:
				#Black
				sys.stdout.write('X')
			else:
				sys.stdout.write('-')
		
		#Do end of row
		#If last row
		#Write closing quote and comma, and newline for all but last line
		if row==height-1:
			#Last line
			sys.stdout.write("\"\n")
		else:
			sys.stdout.write("\",\n")
		
	#EOF
	sys.stdout.write("};\n")
