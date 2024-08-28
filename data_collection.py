from ship import Ship
from ship_analyzer import plot_container_network
import pandas as pd
import numpy as np
from tqdm import tqdm

BAYS = 10
ROWS = 10
LAYERS = 10
CONTAINER_TYPE = "standard"
ITERATIONS = 1

jammer_power_ranges = np.arange(0, 10.1, 1)
distance_range = np.arange(2, 10.1, 0.1)

def save_to_csv(results, power):
    distance = results.get('avg_min_distance_jammers', 'N/A')
    results['power'] = power
    results['distance'] = distance
    status = results.get('status', 'N/A')

    df = pd.DataFrame([results])
    df = df[['power', 'distance', 'status'] + [col for col in df.columns if col not in ['power', 'distance', 'status']]]

    csv_filename = f"{BAYS}x{ROWS}x{LAYERS}-{CONTAINER_TYPE}-domain.csv"
    df.to_csv(csv_filename, mode='a', index=False, header=not pd.io.common.file_exists(csv_filename))

def analyse_and_save(ship, power):
    ship.generate_container_graph()
    results = ship.analyse_graph()
    save_to_csv(results, power)
    return results.get('status', 'N/A'), results.get('avg_min_distance_jammers', 'N/A')

for power in tqdm(jammer_power_ranges, desc="Jammer Power"):
    ship = Ship(bays=BAYS, rows=ROWS, layers=LAYERS)
    ship.add_containers(":", ":", ":", container_type=CONTAINER_TYPE)

    best_dist, last_status = None, None

    low, high = 0, len(distance_range) - 1
    while low <= high:
        mid = (low + high) // 2
        dist = distance_range[mid]

        ship.set_max_nodes(dist, malicious=True, jammer=True, transmit_power=power)
        status, actual_distance = analyse_and_save(ship, power)

        if status == "Pass":
            high = mid - 1
            best_dist = actual_distance
            last_status = status
        else:
            low = mid + 1

    if best_dist is not None:
        for iter in range(ITERATIONS):
            ship = Ship(bays=BAYS, rows=ROWS, layers=LAYERS)
            ship.add_containers(":", ":", ":", container_type=CONTAINER_TYPE)
            ship.set_max_nodes(dist, malicious=True, jammer=True, transmit_power=power)
            
            analyse_and_save(ship, power)
