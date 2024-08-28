import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import ast

RATIO = 0.7

csv_filename = "7x25x25-standard-plane-number.csv"

def read_data():
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
    df = read_data()
    df = df.dropna(subset=['distance', 'power'])
    power = df['power']
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
    plot_data()

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ani = FuncAnimation(fig, update_plot, interval=5000)
plt.show()

