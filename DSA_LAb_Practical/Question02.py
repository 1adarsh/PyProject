# Question02.py
class Node:
    def __init__(self, data):
        self.data = data
        self.prev = self.next = None

def create(a):
    head = tail = None
    for x in a:
        n = Node(x)
        if not head:
            head = n
        else:
            tail.next = n
            n.prev = tail
        tail = n
    return head

def delete(head, key):
    p = head
    while p and p.data != key:
        p = p.next
    if not p:
        print("Value not found")
        return head
    if p.prev:
        p.prev.next = p.next
    else:
        head = p.next
    if p.next:
        p.next.prev = p.prev
    return head

def display(p):
    while p:
        print(p.data, end=" <-> ")
        p = p.next
    print("None")

a = list(map(int, input("Enter integers: ").split()))
head = create(a)
display(head)
head = delete(head, int(input("Delete value: ")))
display(head)