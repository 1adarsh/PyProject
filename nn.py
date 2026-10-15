numbers= [8,5,12,3,7]

numbers.sort(reverse=True)
print("list is sorted",numbers)

total = 0
selected = []
for n in numbers:
    if total < 20:
        selected.append(n)
        print("current status of selected",selected)
        total = total + n
        print("current total",total)

print("Selected numbers", selected)
print("Total", total)