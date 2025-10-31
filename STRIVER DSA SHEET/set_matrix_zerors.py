class Solution:
    def setZeroes(self, matrix: List[List[int]]) -> None:
        """
        Do not return anything, modify matrix in-place instead.
        """
        rows = len(matrix)
        cols = len(matrix[0])

        row0=0
        col0=0

        for i in range(rows):
            for j in range(cols):
                if matrix[i][j] == 0:
                    if i ==0:
                        row0=1
                    if j == 0:
                        col0=1
                    matrix[i][0] = 0
                    matrix[0][j] = 0
        
        
        for i in range(1,rows):
            for j in range(1,cols):
                if  matrix[i][0] == 0 or matrix[0][j] == 0:
                    matrix[i][j] = 0
                
        if row0 :
            for j in range(0,cols):
                matrix[0][j] = 0
        if col0 :
            for i in range(0,rows):
                matrix[i][0] = 0
            
        return matrix
        