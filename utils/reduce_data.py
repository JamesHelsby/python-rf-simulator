import pandas as pd
import argparse
import random

def reduce_csv_lines(input_file, proportion):
    """
    Reduces the number of lines in a CSV file by randomly removing a specified proportion of lines.

    Args:
        input_file (str): The path to the input CSV file.
        proportion (float): The proportion of lines to keep (between 0 and 1).

    Returns:
        None
    """
    # Calculate the output filename
    output_file = input_file.replace('.csv', '-reduced.csv')

    # Load the CSV file into a DataFrame
    df = pd.read_csv(input_file)

    # Determine the number of rows to keep
    num_rows_to_keep = int(len(df) * proportion)

    # Randomly sample the rows to keep
    reduced_df = df.sample(n=num_rows_to_keep, random_state=42)  # random_state for reproducibility

    # Save the reduced DataFrame to a new CSV file
    reduced_df.to_csv(output_file, index=False)

    print(f"Reduced CSV file created: {output_file}")
    print(f"Original number of lines: {len(df)}")
    print(f"Number of lines in reduced file: {len(reduced_df)}")

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Reduce the number of lines in a CSV file.')
    parser.add_argument('input_file', type=str, help='The input CSV file')
    parser.add_argument('proportion', type=float, help='The proportion of lines to keep (between 0 and 1)')
    args = parser.parse_args()

    # Validate the proportion argument
    if not (0 < args.proportion <= 1):
        print("Error: The proportion must be between 0 and 1.")
    else:
        reduce_csv_lines(args.input_file, args.proportion)
