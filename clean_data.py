import csv

csv_filename = "7x25x25-small-plane-number.csv"
expected_fields = 13  # The expected number of fields per line

def find_garbled_lines(csv_filename, expected_fields):
    garbled_lines = []
    total_lines = 0

    with open(csv_filename, 'r') as file:
        reader = csv.reader(file)
        for line_number, row in enumerate(reader, start=1):
            total_lines += 1
            if len(row) != expected_fields:
                print(f"Garbled line detected at line {line_number}: {row}")
                garbled_lines.append(line_number)

    return total_lines, garbled_lines

def remove_garbled_lines(csv_filename, garbled_lines):
    with open(csv_filename, 'r') as file:
        lines = file.readlines()

    # Write back all lines except the garbled ones
    with open(csv_filename, 'w') as file:
        for line_number, line in enumerate(lines, start=1):
            if line_number not in garbled_lines:
                file.write(line)

def main():
    total_lines, garbled_lines = find_garbled_lines(csv_filename, expected_fields)

    print(f"\nTotal lines: {total_lines}")
    print(f"Garbled lines: {len(garbled_lines)}")

    if len(garbled_lines) > 0:
        choice = input("Do you want to remove the garbled lines? (Y/N): ").strip().upper()
        if choice == 'Y':
            remove_garbled_lines(csv_filename, garbled_lines)
            print(f"{len(garbled_lines)} garbled lines removed.")
        else:
            print("No lines were removed.")
    else:
        print("No garbled lines found.")

if __name__ == "__main__":
    main()
