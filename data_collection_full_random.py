from ship import Ship
from ship_analyzer import plot_container_network
import pandas as pd
import numpy as np
from tqdm import tqdm

BAYS = 15
ROWS = 15
LAYERS = 15
CONTAINER_TYPE = "standard"
ITERATIONS = 1

# Define the ranges
jammer_power_ranges = np.arange(-3, 10.1, 0.5)
distance_ranges = np.arange(0, 60.1, 1.0)

# Shuffle the ranges to make the iterations random
np.random.shuffle(jammer_power_ranges)
np.random.shuffle(distance_ranges)

def save_to_csv(results, power):
    distance = results.get('avg_min_distance_jammers', 'N/A')
    results['power'] = power
    results['distance'] = distance
    status = results.get('status', 'N/A')

    df = pd.DataFrame([results])
    df = df[['power', 'distance', 'status'] + [col for col in df.columns if col not in ['power', 'distance', 'status']]]

    csv_filename = f"{BAYS}x{ROWS}x{LAYERS}-{CONTAINER_TYPE}-domain.csv"
    df.to_csv(csv_filename, mode='a', index=False, header=not pd.io.common.file_exists(csv_filename))

for power in tqdm(jammer_power_ranges, desc="Jammer Power"):
    for distance in tqdm(distance_ranges, desc="Distance", leave=False):
        ship = Ship(bays=BAYS, rows=ROWS, layers=LAYERS)
        ship.add_containers(":", ":", ":", container_type=CONTAINER_TYPE)
        ship.set_max_nodes(distance, malicious=True, jammer=True, transmit_power=power)
        
        ship.generate_container_graph()
        results = ship.analyse_graph()
        save_to_csv(results, power)
