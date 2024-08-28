from ship import Ship
# from ship_analyzer import plot_container_network
import pandas as pd
import numpy as np
from tqdm import tqdm

BAYS = 7
ROWS = 25
LAYERS = 25
CONTAINER_TYPE = "standard"
ITERATIONS = 2
TYPE = "plane"

# Define the ranges
jammer_power_ranges = np.arange(18, 24.1, 0.5)
distance_ranges = np.arange(0, 146.1, 0.1)

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

    csv_filename = f"{BAYS}x{ROWS}x{LAYERS}-{CONTAINER_TYPE}-{TYPE}.csv"
    df.to_csv(csv_filename, mode='a', index=False, header=not pd.io.common.file_exists(csv_filename))

for power in tqdm(jammer_power_ranges, desc="Jammer Power"):
    for distance in tqdm(distance_ranges, desc="Distance", leave=False):
        ship = Ship(bays=BAYS, rows=ROWS, layers=LAYERS)
        ship.add_containers(":", ":", ":", container_type=CONTAINER_TYPE)

        if TYPE == "plane":
            ship.set_max_nodes_in_plane('bays', int(BAYS / 2), distance, malicious=True, jammer=True, transmit_power=power)
        else:
            ship.set_max_nodes(distance, malicious=True, jammer=True, transmit_power=power)

        ship.generate_container_graph()
        results = ship.analyse_graph()
        save_to_csv(results, power)
