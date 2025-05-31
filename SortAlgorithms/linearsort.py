
def linsort(arr):
    for i in range(len(arr)):
        k=arr[i]
        t=i
        for j in range(i,len(arr)):
            if arr[j]<k:
                k=arr[j]
                t=j
        temp=k
        arr[t]=arr[i]
        arr[i]=temp
    return arr


arr=[4, 0, 0, 4, 5, 3, 2, 1]
print(linsort(arr))