#include <stdio.h>
#include <stdlib.h>
#include <unistd.h> //For getopt
#include "cmd_line.h"

//Command line option defaults
char * ps_file = "hw1.ps";
float scale = 1.0;
int rotation_cc = 0; //Counter clockwise
int trans_x = 0;
int trans_y = 0;
int lower_bound_x = 0;
int lower_bound_y = 0;
int upper_bound_x = 499;
int upper_bound_y = 499;

//Do commandline parsing directly into global variables
void do_cmd_line_parse(int argc, char** argv)
{
	//String of acceptable cmd line options, : after char means has argument
	char * options = "a:b:c:d:f:m:n:r:s:";
	
	//getopt function gets the next option argument from the argument list specified
	//getopt function returns the option character for the next command line option
	char optchar = 0;
	while ( (optchar = getopt (argc, argv, options)) != -1 )
	{
		//Have a option char, which one?
		if(optchar == 'a')
		{
			lower_bound_x = atoi(optarg);
		}
		else if(optchar == 'b')
		{
			lower_bound_y = atoi(optarg);
		}
		else if(optchar == 'c')
		{
			upper_bound_x = atoi(optarg);
		}
		else if(optchar == 'd')
		{
			upper_bound_y = atoi(optarg);
		}
		else if(optchar == 'f')
		{
			ps_file = optarg;
		}
		else if(optchar == 'm')
		{
			trans_x = atoi(optarg);
		}
		else if(optchar == 'n')
		{
			trans_y = atoi(optarg);
		}
		else if(optchar == 'r')
		{
			rotation_cc = atoi(optarg);
		}
		else if(optchar == 's')
		{
			scale = atof(optarg);
		}
		else
		{
			fprintf(stderr,"Unknown arg '%s'",optarg);
		}
	}
}
