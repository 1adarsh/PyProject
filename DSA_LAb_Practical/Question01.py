class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

def create(values):
    head = None
    for x in values:
        n = Node(x)
        if head is None:
            head = n
            tail = n
        else:
            tail.next = n
            tail = n
    return head
def delete(head, key):
    if head and head.data == key:
        return head.next
    p = head
    while p and p.next:
        if p.next.data == key:
            p.naxt = p.next.next
            return head
        p = p.next
    print("Value not found")
    return head

def display(head):
    while head:
        print(head.data, end =" -> ")
        head = head.next
    print("None")

a = list(map(int, input("Enter integers: ").split()))
head = create(a)
print("Original list:")
display(head)
key = int(input("Enter value to delete: "))
head = delete(head, key)
print("Updated List:")
display(head)