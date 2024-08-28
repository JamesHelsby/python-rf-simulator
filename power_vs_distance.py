import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

csv_filename = "10x10x10-standard-domain.csv"

def plot_data():
    df = pd.read_csv(csv_filename)
    
    power = df['power']
    distance = df['distance']
    status = df['status']
    
    colors = status.map({'Pass': 'green', 'Fail': 'red'})
    
    plt.clf()
    plt.scatter(power, distance, c=colors)

    plt.xlabel('Power')
    plt.ylabel('Distance')
    plt.title('Power vs Distance with Status Color-Coded')

    plt.draw()

def update_plot(frame):
    plot_data()

fig = plt.figure()
ani = FuncAnimation(fig, update_plot, interval=5000)

plt.show()
