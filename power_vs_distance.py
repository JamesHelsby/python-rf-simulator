import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

csv_filename = "7x25x25-standard-plane-number.csv"

def plot_data():
    df = pd.read_csv(csv_filename)

    df = df.dropna(subset=['status'])
    df = df[df['status'].isin(['Pass', 'Fail'])]

    df['power'] = pd.to_numeric(df['power'], errors='coerce')
    df['distance'] = pd.to_numeric(df['distance'], errors='coerce')
    df['num_jamming'] = pd.to_numeric(df['num_jamming'], errors='coerce')
    df = df.dropna(subset=['distance', 'power'])

    power = df['power']
    distance = df['distance'] / (np.sqrt((3*25)**2 + (5*25)**2) * 0.95)
    status = df['status']
    num_jammers = df['num_jamming'] / (25*25)

    colors = status.map({'Pass': 'green', 'Fail': 'none'})

    plt.clf()
    #plt.scatter(power, distance, c=colors)
    plt.scatter(power, num_jammers, c=colors)

    plt.xlabel('Power')
    plt.ylabel('Number of Jammers')
    plt.title('Power vs Distance with Status Color-Coded')

    plt.xlim(-10, 21)

    plt.ylim(0, 1)
    #plt.ylim(0, 140)

    plt.draw()

def update_plot(frame):
    plot_data()

fig = plt.figure()
ani = FuncAnimation(fig, update_plot, interval=5000)

plt.show()
