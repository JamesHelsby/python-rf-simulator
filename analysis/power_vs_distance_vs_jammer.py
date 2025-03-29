import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import ast
import csv

RATIO = 0.7
csv_filename = "7x25x25-standard-plane-number-cumulative.csv"
csv_filename = "./backup/10x20x20-small-domain-number-cumulative-old-reduced.csv"
expected_fields = 13  # The expected number of fields per line

def find_garbled_lines(csv_filename, expected_fields):
    """
    Identify lines in the CSV file that do not have the expected number of fields.
    """
    garbled_lines = []
    total_lines = 0

    print("Checking for garbled lines in the CSV file...")

    with open(csv_filename, 'r') as file:
        reader = csv.reader(file)
        for line_number, row in enumerate(reader, start=1):
            total_lines += 1
            if len(row) != expected_fields:
                print(f"Garbled line detected at line {line_number}: {row}")
                garbled_lines.append(line_number)

    return total_lines, garbled_lines

def remove_garbled_lines(csv_filename, garbled_lines):
    """
    Remove lines from the CSV file that have been identified as garbled.
    """
    with open(csv_filename, 'r') as file:
        lines = file.readlines()

    # Write back all lines except the garbled ones
    with open(csv_filename, 'w') as file:
        for line_number, line in enumerate(lines, start=1):
            if line_number not in garbled_lines:
                file.write(line)
            else:
                print(f"Removing garbled line {line_number}")

def read_data():
    """
    Read the CSV data and process it for plotting, removing garbled lines if necessary.
    """
    # Detect and handle garbled lines
    total_lines, garbled_lines = find_garbled_lines(csv_filename, expected_fields)

    print(f"\nTotal lines: {total_lines}")
    print(f"Garbled lines: {len(garbled_lines)}")

    if len(garbled_lines) > 0:
        remove_garbled_lines(csv_filename, garbled_lines)
        print(f"{len(garbled_lines)} garbled lines removed.")
    else:
        print("No garbled lines found.")

    # Load the cleaned data
    df = pd.read_csv(csv_filename)
    df['power'] = pd.to_numeric(df['power'], errors='coerce')
    df['distance'] = pd.to_numeric(df['distance'], errors='coerce')
    df['total_nodes'] = pd.to_numeric(df['total_nodes'], errors='coerce')
    df['num_jamming'] = pd.to_numeric(df['num_jamming'], errors='coerce')
    df['num_connected_components'] = pd.to_numeric(df['num_connected_components'], errors='coerce')

    def parse_connected_components(component_str):
        try:
            component_dict = ast.literal_eval(component_str)
            return [int(nodes) for nodes in component_dict.values()]
        except (ValueError, SyntaxError):
            return []

    df['connected_components_list'] = df['connected_components'].apply(parse_connected_components)

    df['classification'] = df.apply(lambda row: True if row['num_connected_components'] == 1 or
                                    any(nodes >= RATIO * row['total_nodes'] for nodes in row['connected_components_list'])
                                    else False, axis=1)

    return df

def plot_data():
    """
    Plot the data in a 3D scatter plot, updating it periodically.
    """
    df = read_data()
    df = df.dropna(subset=['distance', 'power'])
    power = df['power']
    status = df['status']
    distance = df['distance'] / (np.sqrt((3*25)**2 + (5*25)**2) * 0.95)
    num_jammers = df['num_jamming'] / (25*25)
    classification = df['classification']
    colors = classification.map({True: 'green', False: 'red'})
    ax.cla()
    surf = ax.scatter(power, distance, num_jammers, c=colors)
    ax.set_xlabel('Power')
    ax.set_ylabel('Distance')
    ax.set_zlabel('Number of Jamming Nodes')
    ax.set_title('Power vs Distance vs Number of Jamming Nodes with Classification Color-Coded')
    plt.draw()

def update_plot(frame):
    """
    Update the plot by calling the plot_data function.
    """
    plot_data()

# Set up the plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Create the animation
ani = FuncAnimation(fig, update_plot, interval=5000, cache_frame_data=False)

# Show the plot
plt.show()

