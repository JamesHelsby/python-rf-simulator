import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import ast
import csv
from matplotlib.widgets import Slider

# Global variables for initial thresholds
RATIO = 0.7  # Threshold for partition failure
COMPONENT_THRESHOLD = 0.1  # Threshold for adding small components to the unconnected count
csv_filename = "10x20x20-small-domain-number.csv"
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

def read_data(ratio, component_threshold):
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
    df['num_unconnected'] = pd.to_numeric(df['num_unconnected'], errors='coerce')

    # Parse connected components to list
    def parse_connected_components(component_str):
        try:
            component_dict = ast.literal_eval(component_str)
            return [int(nodes) for nodes in component_dict.values()]
        except (ValueError, SyntaxError):
            return []

    df['connected_components_list'] = df['connected_components'].apply(parse_connected_components)

    # Calculate additional nodes to add to B from subcomponents smaller than COMPONENT_THRESHOLD
    def calculate_additional_unconnected_nodes(row):
        small_components = [nodes for nodes in row['connected_components_list'] if nodes < component_threshold * row['total_nodes']]
        return sum(small_components)

    # Calculate B
    df['additional_unconnected_nodes'] = df.apply(calculate_additional_unconnected_nodes, axis=1)
    df['B'] = df['num_unconnected'] - df['num_jamming'] + df['additional_unconnected_nodes']

    # Classification based on failure modes
    def classify(row):
        # Fail due to overwhelming if num_jamming exceeds the threshold
        fail_overwhelming = row['num_jamming'] > int((row['total_nodes'] - 1 - row['B']) / 3)
        
        # Fail due to partitioning if there is no single large component or all components are too small
        fail_partition = not (row['num_connected_components'] == 1 or
                              any(nodes >= ratio * row['total_nodes'] for nodes in row['connected_components_list']))

        if fail_overwhelming and fail_partition:
            return 'orange'  # Fail by both overwhelming and partition
        elif fail_overwhelming:
            return 'red'  # Fail by overwhelming
        elif fail_partition:
            return 'purple'  # Fail by partition
        else:
            return 'green'  # Pass

    df['classification'] = df.apply(classify, axis=1)

    return df

def plot_data(ratio, component_threshold):
    """
    Plot the data in a 3D scatter plot, updating it periodically.
    """
    df = read_data(ratio, component_threshold)
    df = df.dropna(subset=['power', 'num_jamming', 'B'])
    power = df['power']
    num_jamming = df['num_jamming'] / df['total_nodes']
    B = df['B'] / df['total_nodes']
    classification = df['classification']
    colors = classification.map({'green': 'green', 'red': 'red', 'purple': 'purple', 'orange': 'orange'})
    ax.cla()
    surf = ax.scatter(num_jamming, B, power, c=colors)
    ax.set_xlabel('Number of Jamming Nodes')
    ax.set_ylabel('B (num_unconnected - num_jamming + small components)')
    ax.set_zlabel('Power')
    ax.set_title('Jamming Nodes vs B vs Power with Classification Color-Coded')
    plt.draw()

def update_plot(val):
    """
    Update the plot by calling the plot_data function.
    """
    ratio = ratio_slider.val
    component_threshold = component_threshold_slider.val
    plot_data(ratio, component_threshold)

# Set up the plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Create sliders for RATIO and COMPONENT_THRESHOLD
ax_ratio = plt.axes([0.25, 0.02, 0.65, 0.03], facecolor='lightgoldenrodyellow')
ax_component_threshold = plt.axes([0.25, 0.06, 0.65, 0.03], facecolor='lightgoldenrodyellow')

ratio_slider = Slider(ax_ratio, 'Ratio', 0.0, 1.0, valinit=RATIO, valstep=0.01)
component_threshold_slider = Slider(ax_component_threshold, 'Component Threshold', 0.0, 0.5, valinit=COMPONENT_THRESHOLD, valstep=0.001)

# Attach the slider to the update function
ratio_slider.on_changed(update_plot)
component_threshold_slider.on_changed(update_plot)

# Initial plot
plot_data(RATIO, COMPONENT_THRESHOLD)

# Show the plot
plt.show()
