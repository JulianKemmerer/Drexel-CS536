#include <stdlib.h>
#include <stdio.h>
#include "matrix.h"

//Allocate a new matrix, zeros
struct Matrix2D new_matrix(int columns,int rows)
{
	//Values accessed as [x][y], x selects column,
	//y select location in coluumn (row)
	struct Matrix2D rv;
	rv.values = malloc(sizeof(float*)*columns);
	int col = 0;
	for(col=0; col<columns; col++)
	{
		rv.values[col] = malloc(sizeof(float)*rows);
	}
	rv.columns = columns;
	rv.rows = rows;
	
	//Zero out
	int row;
	for(col=0; col<columns; col++)
	{
		for(row=0;row<rows;row++)
		{
			rv.values[col][row] = 0.0;
		}
	}
	return rv;
}

//Set matrix to identity values
struct Matrix2D make_identity(struct Matrix2D m)
{
	int row = 0;
	int col = 0;
	for(row = 0; row<m.rows; row++)
	{
		for(col=0; col<m.columns; col++)
		{
			if(col==row)
			{
				m.values[col][row] = 1.0;
			}
			else
			{
				m.values[col][row] = 0.0;
			}
		}
	}
	return m;
}

//Multiple two matricies
struct Matrix2D matrix_multiply(struct Matrix2D A,
									struct Matrix2D B)
{
	//Product AB is defined only if the number of columns in A
	//is equal to the number of rows in B
	if( A.columns != B.rows)
	{
		fprintf(stderr,"Product AB is defined only if the number of columns in A is equal to the number of rows in B. %d,%d\n",A.columns, B.rows);
		exit(-1);
	}
	else
	{
		//Allocate matrix for result
		struct Matrix2D rv = new_matrix(B.columns,A.rows);
		
		//Do the math, eh
		int arow = 0;
		int bcol = 0;
		for (arow = 0; arow < A.rows; arow++)
		{
			for (bcol = 0; bcol < B.columns; bcol++) 
			{
				//Init to 0
				rv.values[bcol][arow] = 0.0;
				//Sum over A columns or B rows (which are equal)
				int i = 0;
				for (i = 0; i < A.columns; i++)
				{
					rv.values[bcol][arow] += A.values[i][arow] * B.values[bcol][i];
				}
			}
		}
		return rv;
	}
}

//Debug, print matrix
void print_matrix(struct Matrix2D m)
{
	int row = 0;
	int col = 0;
	for(row = 0; row<m.rows; row++)
	{
		for(col=0; col<m.columns; col++)
		{
			printf("%f ", m.values[col][row]);
		}
		printf("\n");
	}
}
