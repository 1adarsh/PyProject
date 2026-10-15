class Calculator:
    def __init__(self, name):
        self.oprator = input("Enter the operator you want to use (+, -, *, /): ")
        self.number1 = float(input("Enter the first number: "))
        self.number2 = float(input("Enter the second number: "))
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b

    def multiply(self, a, b):
        return a * b

    def divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero.")
        return a / b

calc = Calculator()
print("Addition of 5 & 6: ", calc.add(5, 6))
print("Subtraction of 7 & 8: ", calc.subtract(7, 8))
print("Multiplication of 9 & 3: ", calc.multiply(9, 3))
print("Division of 12 & 9: ", calc.divide(12, 9))