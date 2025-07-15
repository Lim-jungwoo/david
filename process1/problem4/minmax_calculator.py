import math

def is_number(value):
    try:
        num = float(value)
        return math.isfinite(num)
    except ValueError:
        return False

def getMax(numbers):
    max = float('-inf')
    for number in numbers:
        if number > max:
            max = number
    return max
        

def getMin(numbers):
    min = float('inf')
    for number in numbers:
        if number < min:
            min = number
    return min

def main():
    numbers = input("숫자를 입력하세요(공백 기준): ").split()
    
    if not numbers or not all(is_number(num) for num in numbers):
        print("Invalid input.")
        return
    
    numbers = [float(num) for num in numbers]
    
    max_value = getMax(numbers)
    min_value = getMin(numbers)
    
    print(f"Min: {min_value}, Max: {max_value}")

if __name__ == "__main__":
    main()