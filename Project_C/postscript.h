#ifndef POSTSCRIPT_H
#define POSTSCRIPT_H

//Take path to ps file and return list of lines
//Also return how many lines
struct Line * ps_parse_to_lines(char * filename, int * line_count);

//Count how many line objects are in a ps file
int ps_line_count(char * filename);

//Open a file, exit if error, return file pointer
FILE * open_ps_file(char * filename);


#endif
