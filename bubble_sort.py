# Bubble sort
## 1. compare adjacent element
## 2. After each pass, the largest unsorted element
#### moves at the end.
## 3.Repeat untile sorted

# Complexity :
## Best case O(n)
## Average O(n*n)
## Worst O(n*n)
## Extra space O(1)


a = [5,2,8,1,3]

for i in range(len(a)-1):
    for j in range(len(a) -1 - i):
        print(a[j], a[j+1])
        if a[j] > a[j+1]:
            a[j], a[j+1] = a[j+1] ,a[j]
            
print(a)