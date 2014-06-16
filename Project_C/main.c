#include <stdio.h>
#include <stdlib.h>
#include "cmd_line.h"
#include "geometry.h"
#include "postscript.h"
#include "matrix.h"
#include "xpm.h"

//Compile and run with:
//gcc *.c -o CG_hw1 -lm && ./CG_hw1

//PS file cmd line arg
extern char * ps_file;
extern float scale;
extern int rotation_cc;
extern int trans_x;
extern int trans_y;
extern int lower_bound_x;
extern int lower_bound_y;
extern int upper_bound_x;
extern int upper_bound_y;

int main(int argc, char** argv)
{
	//Parse commandline into globals
	do_cmd_line_parse(argc,argv);
	
	//Parse the PS file into line structs
	int num_lines = 0;
	struct Line * lines = ps_parse_to_lines(ps_file,&num_lines);
	
	//Do transforms on these line structs
	//Objects of your scene are scaled, then rotated 
	//and finally translated in the world coordinates.
	lines = transform_lines(lines, num_lines, scale, rotation_cc, 
							trans_x, trans_y);

	//Clip lines to window
	lines = clip_lines_to_window(lines, &num_lines, lower_bound_x,
						lower_bound_y,upper_bound_x,upper_bound_y);
		
	//Convert lines into list of points
	int num_points = 0;
	struct Point * points = lines_to_points(lines, num_lines, 
												&num_points);
	
	
	//Allocate a blank 2d matrix to serve as the pixel map
	//Pixel map is sizes according to view window
	//Columns = X size, Rows = Y size 
	struct Matrix2D pixel_map = new_matrix(
										upper_bound_x-lower_bound_x+1,
										upper_bound_y-lower_bound_y+1);									
	
	//Write list of pixels in world coords into this pixel map
	//Deals with origin location							
	pixel_map = write_points_to_pixel_map(points, num_points, pixel_map,
										lower_bound_x, upper_bound_y);
		
	//Pass pixel map in xpm write
	do_xpm_write(pixel_map);
	
	//Done
	return 0;
}
