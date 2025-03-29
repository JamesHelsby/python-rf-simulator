import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import numpy as np
import ast
import csv
from matplotlib.colors import ListedColormap
from matplotlib.lines import Line2D

RATIO = 1 / 3
COMPONENT_THRESHOLD = 0
csv_filename = "./backup/10x20x20-small-domain-number-cumulative-old-reduced.csv"
# csv_filename = "20x20x20-standard-domain-number-cumulative.csv"
# csv_filename = "10x20x20-small-domain-number-cumulative.csv"
expected_fields = 13

ELEVATION = -128
AZIMUTH = -126
ROLL = 120

# ELEVATION = -128
# AZIMUTH = -124
# ROLL = 120

# ELEVATION = -120
# AZIMUTH = -100
# ROLL = 100

def find_garbled_lines(csv_filename, expected_fields):
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
    with open(csv_filename, 'r') as file:
        lines = file.readlines()

    with open(csv_filename, 'w') as file:
        for line_number, line in enumerate(lines, start=1):
            if line_number not in garbled_lines:
                file.write(line)
            else:
                print(f"Removing garbled line {line_number}")

def read_data():
    total_lines, garbled_lines = find_garbled_lines(csv_filename, expected_fields)

    print(f"\nTotal lines: {total_lines}")
    print(f"Garbled lines: {len(garbled_lines)}")

    if len(garbled_lines) > 0:
        remove_garbled_lines(csv_filename, garbled_lines)
        print(f"{len(garbled_lines)} garbled lines removed.")
    else:
        print("No garbled lines found.")

    df = pd.read_csv(csv_filename)

    numeric_columns = ['power', 'total_nodes', 'num_jamming', 'num_unconnected']
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')
    df['distance'] = pd.to_numeric(df['distance'], errors='coerce')

    df = df.dropna(subset=numeric_columns)

    def parse_connected_components(component_str):
        try:
            component_dict = ast.literal_eval(component_str)
            return [int(nodes) for nodes in component_dict.values()]
        except (ValueError, SyntaxError):
            return []

    df['connected_components_list'] = df['connected_components'].apply(parse_connected_components)

    def calculate_additional_unconnected_nodes(row):
        small_components = [nodes for nodes in row['connected_components_list'] if nodes < COMPONENT_THRESHOLD * row['total_nodes']]
        return sum(small_components)

    df['additional_unconnected_nodes'] = df.apply(calculate_additional_unconnected_nodes, axis=1)
    df['B'] = df['num_unconnected'] - df['num_jamming'] + df['additional_unconnected_nodes']

    def classify(row):
        fail_overwhelming = row['num_jamming'] > int((row['total_nodes'] - 1 - row['B']) / 3)
        fail_partition = not (row['num_connected_components'] == 1 or any(nodes >= RATIO * row['total_nodes'] for nodes in row['connected_components_list']))

        if fail_overwhelming and fail_partition:
            return 'orange'
        elif fail_overwhelming:
            return 'red'
        elif fail_partition:
            return 'purple'
        else:
            return 'green'

    df['classification'] = df.apply(classify, axis=1)

    return df

def plot_data():
    df = read_data()
    df = df.dropna(subset=['power', 'num_jamming', 'B'])
    
    power = df['power']
    num_jamming = df['num_jamming'] / df['total_nodes']
    B = df['B'] / df['total_nodes']
    classification = df['classification']

    classification_numeric = classification.map({'green': 0, 'red': 1, 'purple': 2, 'orange': 3}).astype(float)

    grid_x, grid_y = np.meshgrid(
        np.linspace(num_jamming.min(), num_jamming.max(), 100),
        np.linspace(B.min(), B.max(), 100)
    )

    grid_z = griddata((num_jamming, B), power, (grid_x, grid_y), method='linear')
    grid_class = griddata((num_jamming, B), classification_numeric, (grid_x, grid_y), method='nearest')

    colormap = ListedColormap(['green', 'red', 'purple', 'orange'])

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(grid_x, grid_y, grid_z, facecolors=colormap(grid_class.astype(int)), alpha=0.8)#, edgecolor='none')

    colors = classification.map({'green': 'green', 'red': 'red', 'purple': 'purple', 'orange': 'orange'})
    ax.scatter(num_jamming, B, power, s=10, c=colors, edgecolor='k', linewidths=0.1)

    for axis in ax.xaxis, ax.yaxis:
        axis.set_label_position('lower')  # Can be 'lower', 'upper', 'default', 'both', 'none'
        axis.set_ticks_position('lower')  # Can be 'lower', 'upper', 'default', 'both', 'none'
    
    ax.zaxis.set_label_position('upper')
    ax.zaxis.set_ticks_position('upper')

    ax.view_init(elev=ELEVATION, azim=AZIMUTH, roll=ROLL)

    x_label = r'$\mathcal{M}$'
    y_label = r'$B$'
    z_label = 'Power\n(dBm)'

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_zlabel(z_label)

    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_zlabel('')

    ax.text2D(0.15, 0.09, x_label, transform=ax.transAxes, horizontalalignment='center', fontsize=10, rotation=0)
    ax.text2D(0.85, 0.09, y_label, transform=ax.transAxes, horizontalalignment='center', fontsize=10, rotation=0)
    ax.text2D(1.15, 0.45, z_label, transform=ax.transAxes, horizontalalignment='center', fontsize=10, rotation=0)

    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Valid', markerfacecolor='green', markersize=10),
        Line2D([0], [0], marker='o', color='w', label='Invalid - Overwhelming', markerfacecolor='red', markersize=10),
        Line2D([0], [0], marker='o', color='w', label='Invalid - Partitioning', markerfacecolor='purple', markersize=10),
        Line2D([0], [0], marker='o', color='w', label='Invalid - Both', markerfacecolor='orange', markersize=10)
    ]

    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.3, 1))

    # plt.savefig('plot.png', bbox_inches='tight', dpi=1000)
    # plt.savefig('plot.png', dpi=1000)

    plt.show()

plot_data()
