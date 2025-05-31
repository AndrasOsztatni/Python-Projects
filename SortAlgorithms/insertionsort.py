def insertionSort(arr):
    n = len(arr)
    for i in range(1, n):
        if arr[i]<arr[i-1]:
            j=i
            temp=arr[i]
            arr[j]=0
            while(arr[j-1]>temp):
                arr[j], arr[j-1]=arr[j-1], 0
                j-=1
                if j==0:
                    break
            arr[j]=temp
    return arr
            
arr= [5, 2, 4, 7, 3, 1, 6, 0]
print(insertionSort(arr))