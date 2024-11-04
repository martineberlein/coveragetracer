def find_even(numbers):
    for num in numbers:
        if num % 2 == 0:
            print(f"Found an even number: {num}")
            break
    else:
        print("No even number found.")


if __name__ == "__main__":
    # Test cases
    find_even([1, 3, 5])  # No even number found.
    find_even([1, 3, 5, 6])  # Found an even number: 6
