import math

def is_number(value):
    try:
        num = float(value)
        return math.isfinite(num)
    except ValueError:
        return False
    
def merge_sort(numbers):
    if len(numbers) <= 1:
        return numbers
    
    mid = len(numbers) // 2
    left_half = merge_sort(numbers[:mid])
    right_half = merge_sort(numbers[mid:])
    
    return merge(left_half, right_half)

def merge(left, right):
    sorted_list = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            sorted_list.append(left[i])
            i += 1
        else:
            sorted_list.append(right[j])
            j += 1
            
    sorted_list.extend(left[i:])
    sorted_list.extend(right[j:])
    
    return sorted_list
    

def main():
    numbers = input("숫자를 입력하세요(공백 기준): ").split()
    if not numbers or not all(is_number(num) for num in numbers):
        print("Invalid Input.")
        return
    
    numbers = [float(num) for num in numbers]
    sorted_numbers = merge_sort(numbers)
    print("Sorted: ", end="")
    for num in sorted_numbers:
        print(f"<{num}>", end=" ")


if __name__ == "__main__":
    main()
    