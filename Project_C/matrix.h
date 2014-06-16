#ifndef MATRIX_H
#define MATRIX_H

//2D Matrix
struct Matrix2D
{
	float ** values;
	int columns;
	int rows;
};

//Allocate a new matrix
struct Matrix2D new_matrix(int columns,int rows);

//Debug, print matrix
void print_matrix(struct Matrix2D m);

//Set matrix to identity values
struct Matrix2D make_identity(struct Matrix2D m);

//Multiple two matricies
struct Matrix2D matrix_multiply(struct Matrix2D A,
									struct Matrix2D B);

#endif
