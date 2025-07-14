import math

def power(number, exponent):
    value = number
    if exponent < 0:
        for i in range(-exponent - 1):
            value *= number
        return 1 / value
    else:
        for i in range(exponent - 1):
            value *= number
        return value
    
def is_number(value):
    try:
        num = float(value)
        return math.isfinite(num)
    except ValueError:
        return False
    
def is_int(value):
    try:
        int(value)
        return float(value).is_integer()
    except ValueError:
        return False
    
def main():
    number = input("Enter number: ")
    exponent = input("Enter exponent: ")

    if not is_number(number):
        print("Invalid number input.")
        return
    else:
        number = float(number)
        
    if not is_int(exponent):
        print("Invalid exponent input.")
        return
    else:
        exponent = int(exponent)

    result = power(number, exponent)
    if is_int(result):
        print(f"Result: {int(result)}")
    else:
        print(f"Result: {result}")

if __name__ == "__main__":
    main()