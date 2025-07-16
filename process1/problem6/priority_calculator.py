from problem3.david.calculator import add, subtract, multiply, divide, is_number
from collections import deque

def is_operator(token):
    return token in ['+', '-', '*', '/']

def is_bracket(token):
    return token in ['(', ')']

def infix_to_postfix(parts):
    precedence = {'+': 1, '-': 1, '*': 2, '/': 2}
    output = []
    stack = deque()
    
    for part in parts:
        if is_number(part):
            output.append(part)
        elif is_operator(part):
            while (stack and stack[-1] != '(' and
                   precedence[part] <= precedence[stack[-1]]):
                output.append(stack.pop())
            stack.append(part)
        elif part == '(':
            stack.append(part)
        elif part == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()
    
    while stack:
        output.append(stack.pop())
    
    return output

def evaluate_postfix(parts):
    stack = deque()
    
    for part in parts:
        if is_number(part):
            stack.append(float(part))
        elif is_operator(part):
            b = stack.pop()
            a = stack.pop()
            if part == '+':
                stack.append(add(a, b))
            elif part == '-':
                stack.append(subtract(a, b))
            elif part == '*':
                stack.append(multiply(a, b))
            elif part == '/':
                stack.append(divide(a, b))
    
    return stack.pop()

def valid_expression(parts):
    bracketStack = deque()
    prev = None
    for part in parts:
        if is_bracket(part):
            if part == '(': 
                if prev and (is_number(prev) or prev == ')'):
                    return False
                bracketStack.append(part)
            elif part == ')':
                if not bracketStack or (prev is None or is_operator(prev) or prev == '('):
                    return False
                bracketStack.pop()
        elif is_operator(part):
            if prev is None or is_operator(prev) or prev == '(': 
                return False
        else:
            if not is_number(part) or (prev and (is_number(prev) or prev == ')')):
                return False
        prev = part
    if prev is None or is_operator(prev) or bracketStack:
        return False
    return True

def main():
    parts = input("Enter expression: ").split()
    if not valid_expression(parts):
        print("Invalid input.")
        return
    
    postfix = infix_to_postfix(parts)
    result = evaluate_postfix(postfix)
    if isinstance(result, str):
        print(result)
        return
    print(f"Result: {result}")
    
if __name__ == '__main__':
    main()