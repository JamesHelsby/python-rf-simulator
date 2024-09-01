import csv

csv_filename = "20x20x20-standard-domain-number-cumulative.csv"
clean_csv_filename = csv_filename.replace('.csv', '-clean.csv')  # Create a new filename with "-clean" suffix
expected_fields = 13  # The expected number of fields per line

def remove_null_bytes(filename):
    """
    Remove null bytes from the file and create a clean temporary version.
    """
    with open(filename, 'rb') as file:
        content = file.read()

    # Replace null bytes with an empty string
    clean_content = content.replace(b'\x00', b'')

    with open(filename, 'wb') as file:
        file.write(clean_content)

def clean_and_copy_csv(csv_filename, clean_csv_filename, expected_fields):
    total_lines = 0
    removed_lines_count = 0

    with open(csv_filename, 'r', encoding='utf-8', errors='replace') as infile, \
         open(clean_csv_filename, 'w', encoding='utf-8') as outfile:
        
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        for line_number, row in enumerate(reader, start=1):
            total_lines += 1
            if len(row) == expected_fields:
                writer.writerow(row)
            else:
                print(f"Garbled line detected at line {line_number}")
                removed_lines_count += 1

    return total_lines, removed_lines_count

def main():
    # Remove any null bytes in the file
    remove_null_bytes(csv_filename)

    total_lines, removed_lines_count = clean_and_copy_csv(csv_filename, clean_csv_filename, expected_fields)

    print(f"\nTotal lines processed: {total_lines}")
    print(f"Number of lines removed: {removed_lines_count}")
    print(f"Clean file created: {clean_csv_filename}")

if __name__ == "__main__":
    main()
