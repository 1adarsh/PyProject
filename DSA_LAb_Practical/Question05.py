from collections import deque

dq = deque()

while True:
    print("1.Front+  2.Rear+  3.Front-  4.Rear-  5.Show  0.Exit")
    ch = int(input("Choice: "))

    if ch == 1:
        dq.appendleft(int(input("Value: ")))
    elif ch == 2:
        dq.append(int(input("Value: ")))
    elif ch == 3:
        print(dq.popleft() if dq else "Deque empty")
    elif ch == 4:
        print(dq.pop() if dq else "Deque empty")
    elif ch == 5:
        print(list(dq))
    elif ch == 0:
        break
    else:
        print("Invalid choice")