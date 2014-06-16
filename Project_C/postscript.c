#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "postscript.h"
#include "geometry.h" //For structs

//Take path to ps file and return list of lines
//Also return how many lines
struct Line * ps_parse_to_lines(char * filename, int * line_count)
{
	//Count how many line structs to alloc
	int num_lines = ps_line_count(filename);
	*line_count = num_lines;
	
	//Allocate array of lines
	struct Line * rv = malloc(num_lines*sizeof(struct Line));
	if(rv==NULL)
	{
		fprintf(stderr,"Cannot allocate %d line structs.\n", num_lines);
		exit(-1);
	}
	
	//Read the file and for each 'Line' create a line struct
	//Open the ps file
	FILE * fp = open_ps_file(filename);
	
	//Read each line
	char * line = NULL;
	size_t line_len = 0;
	size_t read_len = 0;
	
	//Only care about "Line" command
	char * to_find = " Line"; //Need space before
	int line_index = 0; //Keep track of how many lines we've created
	//getline is not portable (GNU only)
	while ((read_len = getline(&line, &line_len, fp)) != -1)
	{
		//strstr Returns a pointer to the first occurrence of str2 
		//in str1, or a null pointer if str2 is not part of str1.
		char * found = strstr(line,to_find);
		if(found != NULL)
		{
			//This line describes a line segment
			int x1,y1,x2,y2;
			sscanf(line,"%d %d %d %d",&x1,&y1,&x2,&y2);
			
			//Build line struct
			struct Point p1,p2;
			p1.x = x1;
			p1.y = y1;
			p2.x = x2;
			p2.y = y2;
			struct Line l;
			l.p1 = p1;
			l.p2 = p2;
			
			//Store line
			rv[line_index] = l;
			line_index++;
		}
    }
    //Close file and return
    fclose(fp);
   
	return rv;
}



//Open a file, exit if error, return file pointer
FILE * open_ps_file(char * filename)
{
	FILE * fp = fopen(filename,"r");
	if(fp==NULL)
	{
		//Error reading file
		fprintf(stderr,"Error reading input PS file '%s'.\n", filename);
		exit(-1);
	}
	else
	{
		return fp;
	}
}

//Count how many line objects are in a ps file
int ps_line_count(char * filename)
{
	//Open the ps file
	FILE * fp = open_ps_file(filename);
	
	//Read each line
	char * line = NULL;
	size_t line_len = 0;
	size_t read_len = 0;
	
	//Count how many 'Line' lines there are
	char * to_count = " Line"; //Need space before
	int line_count = 0;
	//getline is not portable (GNU only)
	while ((read_len = getline(&line, &line_len, fp)) != -1)
	{
		//strstr Returns a pointer to the first occurrence of str2 
		//in str1, or a null pointer if str2 is not part of str1.
		char * found = strstr(line,to_count);
		if(found != NULL)
		{
			line_count++;
		}
    }
    //Close file and return
    fclose(fp);
    return line_count;
}
