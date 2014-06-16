#ifndef GEOMETRY_H
#define GEOMETRY_H

//Point as two ints
static const unsigned int DIMENSIONS = 2;
struct Point
{
	float x,y,z;
};

//Convert a point to single column matrix of DIMENSION+1 length
struct Matrix2D point_to_transform_matrix(struct Point p);

//Convert a point transform matrix back to point struct
struct Point transform_matrix_to_point(struct Matrix2D m);

//Line as two points
struct Line
{
	struct Point p1,p2;
};

//Do transforms on every point of every line
struct Line * transform_lines(struct Line * lines, int num_lines, 
								float scale,
								int rotation_cc, int trans_x,
								int trans_y);
								
//Clip lines to window
struct Line * clip_lines_to_window(struct Line * lines,
									int * num_lines,
									int lower_bound_x, 
									int lower_bound_y, 
									int upper_bound_x, 
									int upper_bound_y);
									
//Given a bound, say if this point is within the bound
int point_in_bound(struct Point p, int is_lower, int is_x, 
						int bound_value);
						
//Take line and do clipping
struct Line clip_line(struct Line line, int is_lower, int is_x, 
						int bound_value);
						
//Clip point and return line
struct Line do_clip_make_line(struct Point point_to_clip,
								struct Point other_point,
								int is_lower, int is_x, 
								int bound_value);
									
//Return the Cohen-Sutherland code for this point
unsigned int cs_code(struct Point p, int lower_bound_x, 
										int lower_bound_y, 
										int upper_bound_x, 
										int upper_bound_y);
									
//Convert lines into list of points
struct Point * lines_to_points(struct Line * lines, int num_lines,
								int * num_points);

//Convert single line to list of points
struct Point * line_to_points(struct Line line, int * num_points);

//Function that evaluates =m*var + b
float line_func(float m, int var, float b);

//Write points in world coordinates into pixel map coords
struct Matrix2D write_points_to_pixel_map(struct Point * points,
											int num_points,
											struct Matrix2D pixel_map,
											int lower_bound_x,
											int upper_bound_y);						

//Return matricies for transforms
struct Matrix2D get_scale_matrix(float sx, float sy, float sz);
struct Matrix2D get_zaxis_rotation_matrix(int rotation_cc);
struct Matrix2D get_translation_matrix(int trans_x, int trans_y,
											int trans_z);				
								

#endif
