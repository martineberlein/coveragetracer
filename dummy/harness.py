import sys
from project.calc import main


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python harness.py <input_data>")
        sys.exit(1)

    input_data = sys.argv[1]
    print(main(input_data))
