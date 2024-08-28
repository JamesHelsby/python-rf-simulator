import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

csv_filename = "7x25x25-standard-plane.csv"

def plot_data():
    df = pd.read_csv(csv_filename)
    
    power = df['power']
    distance = df['distance'] / np.sqrt((3*25)**2 + (5*25)**2)
    num_jamming = df['num_jamming']
    status = df['status']
    
    colors = status.map({'Pass': 'green', 'Fail': 'red'})
    
    ax.cla()

    surf = ax.scatter(power, distance, num_jamming, c=colors)

    ax.set_xlabel('Power')
    ax.set_ylabel('Distance')
    ax.set_zlabel('Number of Jamming Nodes')
    ax.set_title('Power vs Distance vs Number of Jamming Nodes with Status Color-Coded')

    plt.draw()

def update_plot(frame):
    plot_data()

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ani = FuncAnimation(fig, update_plot, interval=5000)

plt.show()
