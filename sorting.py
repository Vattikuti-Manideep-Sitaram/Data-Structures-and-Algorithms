def partition_index(arr,low,high):
    pivot=arr[low]
    s,e=low,high
    while s<e:
        while s<=high and arr[s]<=pivot: s+=1
        while e>=low and arr[e]>pivot: e-=1

        if s<e:
            arr[s],arr[e] = arr[e],arr[s]
    arr[low],arr[e] = arr[e],arr[low]

    return e



def qs(arr,low,high):
    if low>=high:
        return
    p = partition_index(arr,low,high)
    qs(arr,low,p-1)
    qs(arr,p+1,high)

def quickSort(arr):
    qs(arr,0,len(arr)-1)
    return arr