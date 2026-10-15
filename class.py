a = [4,8,12,17,21,26,31,40]
target = 31
low = 0
high = len(a) - 1
while low <= high:
    mid = (low + high)//2
    if a[mid] < target :
        low = mid +1

    elif a[mid] > target: 
        high = mid -1

    else:
        print("found index :",mid)
        break
else:
    print("not found")


## dry run
'''
low = 0
high = 7
mid = (0+7)//2=3
so it check a[3]= 17
then 17 < 31
then low = 4
then (4+7)//2=5
then a[5]=26
so it check 26< 31
then low = 5+1=6
then mid = (6+7)//2 =6
so it check a[6]= 31 == 31
the it break the loop
and print the mid

'''
## Complexity
'''
we have to inspect every element
time:-O(n)
Space:-O(1)

'''