
def bubblesort(arr):
    n=len(arr)
    for i in range(n):
        swapped=False
        for j in range(n-1):
            if arr[j]>arr[j+1]:
                arr[j], arr[j+1]=arr[j+1], arr[j]
                swapped = True
        if swapped==False:
            return arr
    

arr = [5, 2, 4, 7, 3, 6, 1, 0]
print(bubblesort(arr))