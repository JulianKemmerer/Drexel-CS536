#include <stdlib.h>
#include <stdio.h>
#include "matrix.h"

void do_xpm_write(struct Matrix2D pixel_map)
{
	//Cheat and hard code the header and color for now
	printf("/* XPM */\n");
	printf("static char *sco100[] = {\n");
	printf("/* width height num_colors chars_per_pixel */\n");
	int width = pixel_map.columns;
	int height = pixel_map.rows;
	int num_colors = 2;
	int chars_per_pixel = 1;
	printf("\"%d %d %d %d\",\n",width,height,num_colors,chars_per_pixel);
	printf("/* colors */\n");
	printf("\"X c #000000\",\n"); //X for black
	printf("\"- c #ffffff\",\n"); //- for white
	printf("/* pixels */\n");
	//Write pixels
	//Print row wise, inner loop is across columns
	int row,col;
	for(row=0; row<height; row++)
	{
		//New row, write open quote
		printf("\"");
		for(col=0; col<width; col++)
		{
			//Write chars
			if(pixel_map.values[col][row] > 0)
			{
				//Black
				printf("X");
			}
			else
			{
				//White
				printf("-");
			}
		}
		//End of row, write closing quote and comma, and newline
		printf("\",\n");
	}
	printf("};\n");
}


// \rm tmp.xpm; reset && gcc *.c -o CG_hw1 -lm; \rm tmp.xpm; ./CG_hw1 -f hw1.ps -a 0 -b 0 -c 499 -d 499 -s 1.0 -m 0 -n 0 -r 0  > tmp.xpm && display tmp.xpm && \rm tmp.xpm;
// \rm tmp.xpm; reset && gcc *.c -o CG_hw1 -lm; \rm tmp.xpm; ./CG_hw1 -f hw1.ps -a 0 -b 0 -c 499 -d 499 -s 0.8 -m 85 -n 25 -r 10  > tmp.xpm && display tmp.xpm && \rm tmp.xpm;
// \rm tmp.xpm; reset && gcc *.c -o CG_hw1 -lm; \rm tmp.xpm; ./CG_hw1 -f hw1.ps -s 0.5  > tmp.xpm && display tmp.xpm && \rm tmp.xpm;
// \rm tmp.xpm; reset && gcc *.c -o CG_hw1 -lm; \rm tmp.xpm; ./CG_hw1 -f hw1.ps -r -30  > tmp.xpm && display tmp.xpm && \rm tmp.xpm;
//* \rm tmp.xpm; reset && gcc *.c -o CG_hw1 -lm; \rm tmp.xpm; ./CG_hw1 -f hw1.ps -m 100 -n 100  > tmp.xpm && display tmp.xpm && \rm tmp.xpm;
// \rm tmp.xpm; reset && gcc *.c -o CG_hw1 -lm; \rm tmp.xpm; ./CG_hw1 -f hw1.ps -a 25 -b 50 -c 399 -d 399  > tmp.xpm && display tmp.xpm && \rm tmp.xpm;
//* \rm tmp.xpm; reset && gcc *.c -o CG_hw1 -lm; \rm tmp.xpm;  ./CG_hw1 -f hw1.ps -a 25 -b 50 -c 399 -d 399 -r 30 -m 100 -n 100 -s 0.5  > tmp.xpm && display tmp.xpm && \rm tmp.xpm;
