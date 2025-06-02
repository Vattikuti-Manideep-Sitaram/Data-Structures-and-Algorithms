def mergeSort(nums,n):
    ms(nums,0,n-1)
    return nums


def ms(nums,low,high):
    if low>=high:
        return
    mid = (low + high)//2
    ms(nums,low,mid)
    ms(nums,mid+1,high)

    merge(nums,low,mid,high)


def merge(nums,low,mid,high):
    i,j=low,mid+1
    n=high-low+1
    temp=[]

    while i<=mid and j<=high:
        if nums[i] <=nums[j]:
            temp.append(nums[i])
            i+=1
        else:
            temp.append(nums[j])
            j+=1
    while i<=mid:
        temp.append(nums[i])
        i+=1
    while j<=high:
        temp.append(nums[j])
        j+=1

    i=low

    for k in range(n):
        nums[i] = temp[k]
        i+=1
        
