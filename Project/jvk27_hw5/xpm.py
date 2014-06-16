#!/usr/bin/env python
import sys

#Colors
COLOR_RED = "Red"
COLOR_GREEN = "Green"
COLOR_BLUE = "Blue"
ALL_COLORS = [COLOR_RED,COLOR_GREEN,COLOR_BLUE]
#Dict of char to hex color string
XPM_CHAR_TO_COLOR = dict()
#ANd reverse
XPM_COLOR_TO_CHAR = dict()
#Color hex pairs
XPM_CHAR_HEX_PAIRS = []
#Generate RGB ranges
RGB_MAX_VAL = 255
NUM_RGB_SHADES = 20
SHADE_STEP = float(RGB_MAX_VAL+1)/float(NUM_RGB_SHADES)
#Also store all hex values used for later
HEX_STRS_LIST = []
rgbval = 255.0
count = 0
#Printing ascii chars start at 33 
#but startign at 48 gets rids of some bad chars for C code xpm format
ascii_int = 48
while count < NUM_RGB_SHADES:
	#int(rgbval) is int color
	#Do r g b
	hex_str = str(hex(int(rgbval))).replace("0x","")
	#Pad if needed
	while len(hex_str) < 2:
		hex_str = "0" + hex_str
	HEX_STRS_LIST = HEX_STRS_LIST + [hex_str]	
	r_str = hex_str + "00" + "00"
	g_str = "00" + hex_str + "00"
	b_str = "00" + "00" + hex_str
	
	#Store this value using ascii count value
	r_char = str(unichr(ascii_int)); ascii_int = ascii_int + 1;
	g_char = str(unichr(ascii_int)); ascii_int = ascii_int + 1;
	b_char = str(unichr(ascii_int)); ascii_int = ascii_int + 1;
	XPM_CHAR_HEX_PAIRS.append( (r_char,r_str) )
	XPM_CHAR_HEX_PAIRS.append( (g_char,g_str) )
	XPM_CHAR_HEX_PAIRS.append( (b_char,b_str) )
	
	#~ print "r_str",r_str,"r_char",r_char
	#~ print "g_str",g_str,"g_char",g_char
	#~ print "b_str",b_str,"b_char",b_char
	
	#Increment
	rgbval = rgbval - SHADE_STEP
	count = count + 1
	
#Finally add black and white
white_char = str(unichr(ascii_int)); ascii_int = ascii_int + 1;
black_char = str(unichr(ascii_int)); ascii_int = ascii_int + 1;
XPM_CHAR_HEX_PAIRS.append( (black_char,"000000") )
XPM_CHAR_HEX_PAIRS.append( (white_char,"ffffff") )
	
#Now store in dicts
for char_str_pair in XPM_CHAR_HEX_PAIRS:
	c,s = char_str_pair
	XPM_CHAR_TO_COLOR[c] = s
	XPM_COLOR_TO_CHAR[s] = c
	
#RGB values range 0 to 255
#Use thousands place as selection for RGB
R_OFFSET = 0
G_OFFSET = 1000
B_OFFSET = 2000
W_OFFSET = 3000
BLK_OFFSET = 4000
BACKGROUND_FP_VAL = BLK_OFFSET
#0000 - 0255 for R only value
#1000 - 1255 for G only value
#2000 - 2255 for B only value
#3000 - 3999 for W
#4000 - 4999 for B
def pixel_map_float_to_xpm_char(float_val):
	#Get the floating point R G or B value
	color = ""
	color_float_val = -1.0
	if float_val <= 255:
		#R
		color_float_val = float_val - R_OFFSET
		color = COLOR_RED
	elif float_val <= 1255:
		#G
		color_float_val = float_val - G_OFFSET
		color = COLOR_GREEN
	elif float_val <= 2255:
		#B
		color_float_val = float_val - B_OFFSET
		color = COLOR_BLUE
	elif float_val <= 3999:
		#W
		return XPM_COLOR_TO_CHAR["ffffff"]
	else:
		#B
		return XPM_COLOR_TO_CHAR["000000"]
		
	#Loop over list of colors and find which of the 20 shades values is closest
	#Which of these two digit hex strs is closest to the floating point value
	closest_hex_str = ""
	minimum_diff = 9999.0
	for hex_str in HEX_STRS_LIST:
		float_hex_str = float(int(hex_str,16))
		diff = abs(color_float_val - float_hex_str)
		if diff < minimum_diff:
			closest_hex_str = hex_str
			minimum_diff = diff
			
	#Now we have the closest hex str, now produce a string
	full_hex_str = ""
	if color == COLOR_RED:
		full_hex_str = closest_hex_str + "00" + "00"
	elif color == COLOR_GREEN:
		full_hex_str = "00" + closest_hex_str + "00"
	else:#b
		full_hex_str = "00" + "00" + closest_hex_str
		
	#Now look up the char for this full hex number
	c = XPM_COLOR_TO_CHAR[full_hex_str]
	
	return c

def do_xpm_write(pixel_map):
	#Hard code the header and color for now
	print "/* XPM */"
	print "static char *sco100[] = {"
	print "/* width height num_colors chars_per_pixel */"
	#Numpy matrix property
	rows,columns = pixel_map.shape	
	width = columns;
	height = rows;
	num_colors = len(XPM_CHAR_TO_COLOR);
	chars_per_pixel = 1;
	print '"{0} {1} {2} {3}"'.format(width,height,num_colors,chars_per_pixel)
	print "/* colors */"
	#Print each color pair
	for c in XPM_CHAR_TO_COLOR:
		print "\"" + c + " c #" + XPM_CHAR_TO_COLOR[c] + "\","
	
	print "/* pixels */"
	#Write pixels
	#Print row wise, inner loop is across columns
	#Pixel map is a matrix addressed as pixel_map[y,x] 
	for row in range(0,height): #Y
		#New row, write open quote
		sys.stdout.write('"')
		for col in range(0,width): #X
			#Get char based for this pixel map fp value
				fp_val = pixel_map[row,col]
				c = pixel_map_float_to_xpm_char(fp_val)
				sys.stdout.write(c)
		
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
