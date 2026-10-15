dq = []

while True:
    print("1.Insert Front  2.Insert Rear")
    print("3.Delete Front  4.Delete Rear  5.Display  0.Exit")
    ch = int(input("Choice: "))

    if ch == 1:
        dq.insert(0, int(input("Value: ")))
    elif ch == 2:
        dq.append(int(input("Value: ")))
    elif ch == 3:
        print(dq.pop(0) if dq else "Deque empty")
    elif ch == 4:
        print(dq.pop() if dq else "Deque empty")
    elif ch == 5:
        print(dq)
    elif ch == 0:
        break
    else:
        print("Invalid choice")