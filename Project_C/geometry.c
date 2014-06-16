#include <stdlib.h>
#include <stdio.h>
#include <math.h> //For rotation 
#include "geometry.h"
#include "matrix.h"

//Do transforms on every point of every line
//Objects of your scene are scaled, then rotated and 
//finally translated in the world coordinates.
struct Line * transform_lines(struct Line * lines, int num_lines, 
								float scale,
								int rotation_cc, int trans_x,
								int trans_y)
{
	//First compute one transform matrix
	struct Matrix2D scale_matrix = get_scale_matrix(scale,scale,scale);
	struct Matrix2D rotation_matrix = get_zaxis_rotation_matrix(rotation_cc);
	struct Matrix2D translation_matrix = get_translation_matrix(trans_x,trans_y,0);
	//First to last transfrom is left to right and inner to outer
	struct Matrix2D transform_matrix = matrix_multiply(translation_matrix, matrix_multiply(rotation_matrix,scale_matrix) );
	
	//Loop over each line
	int line = 0;
	for(line = 0; line < num_lines; line++)
	{
		//First convert points to matrices
		struct Matrix2D p1_mat = point_to_transform_matrix(lines[line].p1);
		struct Matrix2D p2_mat = point_to_transform_matrix(lines[line].p2);
		
		//Multiply both points
		struct Matrix2D new_p1_mat = matrix_multiply(transform_matrix,p1_mat);
		struct Matrix2D new_p2_mat = matrix_multiply(transform_matrix,p2_mat);
		
		//Convert pack to point structs
		lines[line].p1 = transform_matrix_to_point(new_p1_mat);
		lines[line].p2 = transform_matrix_to_point(new_p2_mat);
	}
	
	return lines;
}

//Return matricies for transforms
struct Matrix2D get_scale_matrix(float sx, float sy, float sz)
{
	//Transform matricies are always 1 row,col larger than dimensions
	struct Matrix2D rv = new_matrix(DIMENSIONS+1,DIMENSIONS+1);
	rv.values[0][0] = sx;
	rv.values[1][1] = sy;
	rv.values[2][2] = 1;
	if(DIMENSIONS>2)
	{
		rv.values[2][2] = sz;
		rv.values[3][3] = 1;
	}
	return rv;
}
struct Matrix2D get_zaxis_rotation_matrix(int rotation_cc)
{
	//Transform matricies are always 1 row,col larger than dimensions
	struct Matrix2D rv = new_matrix(DIMENSIONS+1,DIMENSIONS+1);
	rv.values[0][0] = cos(rotation_cc * (M_PI / 180.0));
	rv.values[1][0] = -1 * sin(rotation_cc * (M_PI / 180.0));
	rv.values[0][1] = sin(rotation_cc * (M_PI / 180.0));
	rv.values[1][1] = cos(rotation_cc * (M_PI / 180.0));
	rv.values[2][2] = 1;
	if(DIMENSIONS>2)
	{
		rv.values[3][3] = 1;
	}
	return rv;
}
struct Matrix2D get_translation_matrix(int trans_x, int trans_y,
											int trans_z)
{
	//Transform matricies are always 1 row,col larger than dimensions
	struct Matrix2D rv = new_matrix(DIMENSIONS+1,DIMENSIONS+1);
	//Set diagonal as 1
	rv = make_identity(rv);
	//Set translation values
	rv.values[DIMENSIONS][0] = trans_x;
	rv.values[DIMENSIONS][1] = trans_y;
	if(DIMENSIONS>2)
	{
		rv.values[DIMENSIONS][2] = trans_z;
	}
	return rv;
}

//Convert a point to single column matrix of DIMENSION+1 length
struct Matrix2D point_to_transform_matrix(struct Point p)
{
	struct Matrix2D rv = new_matrix(1,DIMENSIONS+1);
	rv.values[0][0] = p.x;
	rv.values[0][1] = p.y;
	rv.values[0][2] = 1;
	if(DIMENSIONS >2)
	{
		rv.values[0][2] = p.z;
		rv.values[0][3] = 1;
	}
	return rv;
}	

//Convert a point transform matrix back to point struct
struct Point transform_matrix_to_point(struct Matrix2D m)
{
	struct Point rv;
	rv.x = m.values[0][0];
	rv.y = m.values[0][1];
	rv.z = 0.0;
	if(DIMENSIONS >2)
	{
		rv.z = m.values[0][2];
	}
	return rv;
}	

//Return the Cohen-Sutherland code for this point
unsigned int cs_code(struct Point p, int lower_bound_x, 
										int lower_bound_y, 
										int upper_bound_x, 
										int upper_bound_y)
{
	unsigned int rv = 0;
	//Bit 1 if point is above window
	if(p.y>upper_bound_y)
	{
		rv |= 1;
	}
	//Bit 2 if point is below window
	if(p.y<lower_bound_y)
	{
		rv |= 2;
	}
	//Bit 3 if point is right of window
	if(p.x>upper_bound_x)
	{
		rv |= 4;
	}
	//Bit 4 if point is left of window
	if(p.x<lower_bound_x)
	{
		rv |= 8;
	}
	return rv;
}


//Clip lines to window
struct Line * clip_lines_to_window(struct Line * lines,
									int * num_lines,
									int lower_bound_x, 
									int lower_bound_y, 
									int upper_bound_x, 
									int upper_bound_y)
{
	//Keep track of if any lines changes are made
	//When no more changes are made, all lines are clip, done
	int made_change = 0;
	
	//We may be dropping some lines if they are outside of the window
	//Allocate a new list
	struct Line * rv_lines = malloc(*num_lines*sizeof(struct Line));
	//Keep track of how many lines in new list
	int rv_lines_count = 0;
	
	//Loop over each line in orginal list
	int line = 0;
	for(line=0; line < *num_lines; line++)
	{			
		//Get CS codes for each point
		unsigned int cs1 = cs_code(lines[line].p1,lower_bound_x,
									lower_bound_y, 
									upper_bound_x, 
									upper_bound_y);
		unsigned int cs2 = cs_code(lines[line].p2,lower_bound_x,
									lower_bound_y, 
									upper_bound_x, 
									upper_bound_y);
		
		//Check if completely visible
		unsigned int OR = cs1 | cs2;
		unsigned int AND = cs1 & cs2;
		unsigned int XOR = cs1 ^ cs2;
		if(OR == 0)
		{
			//Line is completely visible (no change to line)
			//Store in new list
			rv_lines[rv_lines_count] = lines[line];
			rv_lines_count++;
			continue;
		}
		else if(AND != 0)
		{
			//Line is completely outside window, drop it from list
			//Do nothing
			//Change to lines was made
			made_change = 1;
			continue;			
		}
		else
		{				
			//Original line and new line
			struct Line orig_line = lines[line];
			struct Line new_line;			
			
			//Decide which bit flips
			//XOR finds flipped bits
			//AND to check 
			//Store clipped line
			if(XOR & 1 == 1) //Bit 1 flipped
			{
				//Window Top, upper_bound_y
				new_line = clip_line(orig_line, 0, 0, upper_bound_y);
			}
			else if((XOR & 2) == 2) //Bit 2 flipped
			{
				//Window Bottom, lower_bound_y
				new_line = clip_line(orig_line, 1, 0, lower_bound_y);
			}
			else if((XOR & 4) == 4) //Bit 3 flipped
			{
				//Window Right, upper_bound_x
				new_line = clip_line(orig_line, 0, 1, upper_bound_x);
			}
			else if((XOR & 8) == 8) //Bit 4 flipped
			{
				//Window Left, lower_bound_x
				new_line = clip_line(orig_line, 1, 1, lower_bound_x);
			}
			else
			{
				fprintf(stderr,"Line does not have valid bit flips. XOR=%x.\n",XOR);
				exit(-1);
			}
			
			//Check if change was made, recursion was running too long
			//Need to fix this for 3D
			if(orig_line.p1.x != new_line.p1.x)
			{
				made_change = 1;
			}
			else if(orig_line.p1.y != new_line.p1.y)
			{
				made_change = 1;
			}
			else if(orig_line.p2.x != new_line.p2.x)
			{
				made_change = 1;
			}
			else if(orig_line.p2.y != new_line.p2.y)
			{
				made_change = 1;
			}			
			
			//Store this new line
			rv_lines[rv_lines_count] = new_line;
			rv_lines_count++;
		}
	}
	
	//Keep track of how many line segments, update line count
	*num_lines = rv_lines_count;
	
	//Decide if to repeat or not
	if(made_change ==1)
	{
		//Re run with new set of lines
		return clip_lines_to_window(rv_lines,
									num_lines,
									lower_bound_x, 
									lower_bound_y, 
									upper_bound_x, 
									upper_bound_y);
	}
	else
	{
		//No changes made, done clipping
		//Return new lines list
		return rv_lines;
	}
}

//Take line and do clipping
struct Line clip_line(struct Line line, int is_lower, int is_x, 
						int bound_value)
{
	//Find which point on this line is past the boundary(outside window)
	struct Point p1 = line.p1;
	struct Point p2 = line.p2;
	int p1_in_bound = point_in_bound(p1,is_lower,is_x,bound_value);
	int p2_in_bound = point_in_bound(p2,is_lower,is_x,bound_value);
	
	//Check
	if( (p1_in_bound==0) && (p2_in_bound==0) )
	{
		fprintf(stderr,"Neither point is outside boundary.\n");
		exit(-1);
	}
	else if( (p1_in_bound==0) && (p2_in_bound==1) )
	{
		return do_clip_make_line(p1, p2, is_lower, is_x, bound_value);
	}
	else if( (p1_in_bound==1) && (p2_in_bound==0) )
	{
		return do_clip_make_line(p2, p1, is_lower, is_x, bound_value);
	}
	else if( (p1_in_bound==1) && (p2_in_bound==1) )
	{
		fprintf(stderr,"Both points are outside boundary.\n");
		exit(-1);
	}
}

struct Line do_clip_make_line(struct Point point_to_clip,
								struct Point other_point,
								int is_lower, int is_x, 
								int bound_value)
{
	//Point to clip is point 2 for ease
	float x1 = (float)other_point.x;
	float y1 = (float)other_point.y;
	float x2 = (float)point_to_clip.x;
	float y2 = (float)point_to_clip.y;
	
	float dx = x2 - x1;
	float dy = y2 - y1;
	
	//Special case for vertical line
	if(dx == 0)
	{
		struct Line rv_vert;
		rv_vert.p1 = other_point;
		rv_vert.p2 = point_to_clip;
		return rv_vert;
	}
	
	//Calc line equation values
	float m = (y2-y1)/(x2-x1);
	//Solve for intercept
	//y=mx+b , b = y-mx, use point 2
	float b = y2 - (m*x2);
	
	//Decide what we need to solve for, an x or y value
	if(is_x == 1)
	{
		//X Bound, solve for Y value
		// y = mx + b
		float bounded_y = m*bound_value + b;
		point_to_clip.x = bound_value;
		point_to_clip.y = bounded_y;
	}
	else
	{
		//Y Bound, solve for X value
		// x = (y-b)/m
		float bounded_x = (bound_value - b)/m;
		point_to_clip.x = bounded_x;
		point_to_clip.y = bound_value;
	}
	
	struct Line rv;
	rv.p1 = other_point;
	rv.p2 = point_to_clip;
	return rv;	
}

//Given a bound, say if this point is within the bound
int point_in_bound(struct Point p, int is_lower, int is_x, 
						int bound_value)
{
	float x = p.x;
	float y = p.y;
	
	if( (is_lower==0) && (is_x==0) )
	{
		//Upper bound in y check
		if( y <= bound_value) return 1;
	}
	else if( (is_lower==0) && (is_x==1) )
	{
		//Upper bound in x check
		if( x <= bound_value) return 1;
	}
	else if( (is_lower==1) && (is_x==0) )
	{
		//Lower bound in y check
		if( y >= bound_value) return 1;
	}
	else if( (is_lower==1) && (is_x==1) )
	{
		//Lower bound in x check
		if( x >= bound_value) return 1;
	}
	return 0;
}



//Convert lines into list of points
struct Point * lines_to_points(struct Line * lines, int num_lines,
								int * num_points)
{
	//Loop over lines, add points from each line into total list
	struct Point * all_points = NULL;
	int point_count = 0;
	//Could do some more intelligent allocations but this
	//will work fine. (linked list is probably best)
	int line = 0;
	for(line=0; line < num_lines; line++)
	{
		int new_points_count = 0;
		struct Point * new_points = line_to_points(lines[line], &new_points_count);
		
		//Combine the old points and new points
		struct Point * new_all_points = malloc((new_points_count+point_count)*sizeof(struct Point));
		int i;
		//First add in old points
		for(i=0; i<point_count; i++)
		{
			new_all_points[i] = all_points[i];
		}
		//Then new points
		for(i=0; i<new_points_count; i++)
		{
			new_all_points[i+point_count] = new_points[i];
		}
		//Do swap for next iteration
		all_points = new_all_points;
		point_count += new_points_count;
	}
	
	//Finally return the whole list of points
	*num_points = point_count;
	return all_points;
}

//Function that evaluates =m*var + b
float line_func(float m, int var, float b)
{
	float rv = m*var + b;
	return rv;
}

//Convert single line to list of points
struct Point * line_to_points(struct Line line, int * num_points)
{
	//DDA (does use floating point rounding to ints)
	//Some variables for ease
	struct Point p1 = line.p1;
	struct Point p2 = line.p2;
	float x1 = p1.x;
	float y1 = p1.y;
	float x2 = p2.x;
	float y2 = p2.y;
	
	//Slope
	//Check special cases
	float dy = (y2-y1);
	float dx = (x2-x1);
	float ady = fabs(dy);
	float adx = fabs(dx);
	
	//Calculate equation values and deciding which eq form to take
	float m = 0;
	float b = 0;
	//Also keep track of starting and end loop bounds for later
	int start = 0;
	int end = 0;	
	//Decide on which equation form to use
	int is_y_mx_b = 0;
	
	
	//If dx dy  = 0?
	if( (dx==0) && (dy==0))
	{
		//No change in y or x between points?
		*num_points = 0;
		return NULL;
	}
	//If dy/dx is >1 then line is close to vertical than horozontal
	else if( (adx==0) || (ady/adx) > 1)
	{
		//More vertical, use x=my+b form
		is_y_mx_b = 0;
		m = dx/dy;
		b = x2 - (m*y2);
		//Will loop over Y
		start = (int)y1;
		end = (int)y2;
	}
	else
	{
		//More horozontal, use y=mx+b form
		is_y_mx_b = 1;
		m = dy/dx;
		b = y2 - (m*x2);
		//Will loop over X
		start = (int)x1;
		end = (int)x2;
	}
	
	
	
	//Start looping over either x or y
	//Check bounds first, swap
	if(start > end)
	{
		int tmp = start;
		start = end;
		end = tmp;
	}
	
	//There will be a point for each loop iteration
	int point_count = end - start + 1;
	struct Point * rv = malloc(point_count*sizeof(struct Point));
	
	
	//Begin looping
	int var,i;i=0;
	for(var=start; var<=end; var++)
	{
		//Some generic names for ease
		float func_val_f = line_func(m,var,b);
		int func_val_i = (int)func_val_f;
		int x,y;	
		
		if(is_y_mx_b==1)
		{
			//Loop variable is x
			x = var;
			y = func_val_i;
		}
		else
		{
			//Loop variable is y
			x = func_val_i;
			y = var;
		}
		
				
		//Save this point
		struct Point tmp;
		tmp.x = x;
		tmp.y = y;
		//printf("%d\n",i);
		rv[i]=tmp;
		i++;
	}
		
	*num_points = point_count;
	return rv;
}

//Write points in world coordinates into pixel map coords
struct Matrix2D write_points_to_pixel_map(struct Point * points,
											int num_points,
											struct Matrix2D pixel_map,
											int lower_bound_x,
											int upper_bound_y)
{
	//Loop over each point
	int i;
	for(i=0; i<num_points;i++)
	{
		//World
		int world_x = points[i].x;
		int world_y = points[i].y;
		//Pixel map
		int pixel_x = world_x - lower_bound_x;
		int pixel_y = upper_bound_y - world_y;
		
		//Cheap check...bleh
		if(pixel_x < 0)
		{
			pixel_x = 0;
		}
		if(pixel_y < 0)
		{
			pixel_y = 0;
		}
		
		//Write something... a 1?
		pixel_map.values[pixel_x][pixel_y] = 1.0;
	}
	return pixel_map;
}
