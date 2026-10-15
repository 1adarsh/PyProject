def postfix(s):
    stack, out = [], []
    prec = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3}

    for c in s.replace(" ", ""):
        if c.isalnum():
            out.append(c)
        elif c == '(':
            stack.append(c)
        elif c == ')':
            while stack and stack[-1] != '(':
                out.append(stack.pop())
            if not stack:
                raise ValueError("Mismatched parentheses")
            stack.pop()
        elif c in prec:
            while (stack and stack[-1] in prec and
                   (prec[stack[-1]] > prec[c] or
                    (prec[stack[-1]] == prec[c] and c != '^'))):
                out.append(stack.pop())
            stack.append(c)

    if '(' in stack:
        raise ValueError("Mismatched parentheses")
    while stack:
        out.append(stack.pop())
    return ''.join(out)

print("Postfix:", postfix(input("Infix: ")))