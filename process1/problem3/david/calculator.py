import math

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        return "Error: Division by zero"
    return a / b

def is_number(value):
    try:
        num = float(value)
        return math.isfinite(num)
    except ValueError:
        return False

def main():
    num1, operation, num2 = None, None, None
    isBonus = input("Enter 'y' if bonus, otherwise anything: ")

    if isBonus.lower() == 'y':
        line = input("Enter expression: ")
        parts = line.split()
        if len(parts) != 3:
            print("Invalid input format. Use: num1 operator num2")
            return
        num1, operation, num2 = parts
    else:
        num1 = input("Enter first number: ")
        num2 = input("Enter second number: ")
        operation = input("Enter operator (+, -, *, /): ")

    if not (is_number(num1) or is_number(num2)):
        print("Invalid numbers")
        return
    
    num1 = int(float(num1))
    num2 = int(float(num2))
    
    if operation == '+':
        result = add(num1, num2)
    elif operation == '-':
        result = subtract(num1, num2)
    elif operation == '*':
        result = multiply(num1, num2)
    elif operation == '/':
        result = divide(num1, num2)
    else:
        result = "Invalid operator"

    if result == "Error: Division by zero" or result == "Invalid operator":
        print(result)
        return
    
    print(f"Result: {float(result)}")

if __name__ == "__main__":
    main()