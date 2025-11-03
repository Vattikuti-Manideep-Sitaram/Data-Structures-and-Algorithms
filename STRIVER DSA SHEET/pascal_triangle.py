
def print_pascal_triangle(n):
    ans = []
    
    for i in range(n):
        temp = []
        for j in range(i+1):
            if j == 0 or j == i:
                 temp.append(1)
            else:
                temp.append(ans[i-1][j-1] + ans[i-1][j])
        ans.append(temp)
    for row in ans:
        print(row)


def print_nth_row(n):
    for i in range(n+1):
        nCr(n,i)

def nCr(n,r):
    ans = 1
    if r:
        ans = 1
        for i in range(1,r+1):
            res = (n-i+1)/i
            ans *=res
    print(int(ans),end=" ")
    
def print_nth_row_optimized(n):
    ans = [1]
    
    for i in range(1,n+1):
        res *= (n-i+1) /i
        ans.append(res)
    
    return ans
    
            




if __name__ == "__main__":
    print_pascal_triangle(8)
    print_nth_row(5)
    # nCr(5,4)