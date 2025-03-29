import os
import re
import fcntl

CSV_FILE_PATH = "cooja_results.csv"

def is_valid_line(line):
    """Check if the line is a valid entry."""
    pattern = re.compile(r'^\d+,\d+,"[0-9:.,]+",(cache|bls|ttl)$')
    return bool(pattern.match(line.strip()))

def clean_data():
    """Clean the CSV file and remove garbled lines."""
    cleaned_lines = []

    with open(CSV_FILE_PATH, 'r+') as file:
        # Acquire an exclusive lock
        fcntl.flock(file, fcntl.LOCK_EX)
        try:
            header = file.readline()  # Keep the header line
            cleaned_lines.append(header.strip())

            for line in file:
                if is_valid_line(line):
                    cleaned_lines.append(line.strip())
                # else:
                #     print(f"Garbled line removed: {line.strip()}")

            # Write the cleaned lines to a temporary file
            temp_file_path = CSV_FILE_PATH + ".tmp"
            with open(temp_file_path, 'w') as temp_file:
                temp_file.write('\n'.join(cleaned_lines) + '\n')

            # Replace the original file with the cleaned file
            os.replace(temp_file_path, CSV_FILE_PATH)
            print("Data cleaned successfully.")
        finally:
            # Always release the lock
            fcntl.flock(file, fcntl.LOCK_UN)

def main():
    print(f"Attempting to clean data with file lock on {CSV_FILE_PATH}...")
    clean_data()

if __name__ == "__main__":
    main()
