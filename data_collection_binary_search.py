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

jammer_power_ranges = np.arange(0, 10.1, 0.5)
max_distance = 50.0

def save_to_csv(results, power):
    distance = results.get('avg_min_distance_jammers', 'N/A')
    results['power'] = power
    results['distance'] = distance
    status = results.get('status', 'N/A')

    df = pd.DataFrame([results])
    df = df[['power', 'distance', 'status'] + [col for col in df.columns if col not in ['power', 'distance', 'status']]]

    csv_filename = f"{BAYS}x{ROWS}x{LAYERS}-{CONTAINER_TYPE}-domain.csv"
    df.to_csv(csv_filename, mode='a', index=False, header=not pd.io.common.file_exists(csv_filename))

def analyse_and_save(ship, power, distance):
    ship.generate_container_graph()
    results = ship.analyse_graph()
    save_to_csv(results, power)
    return results.get('status', 'N/A')

for power in tqdm(reversed(jammer_power_ranges), desc="Jammer Power"):
    low, high = 3.0, max_distance
    best_dist = None

    while low <= high:
        mid = (low + high) / 2.0

        ship = Ship(bays=BAYS, rows=ROWS, layers=LAYERS)
        ship.add_containers(":", ":", ":", container_type=CONTAINER_TYPE)
        ship.set_max_nodes(mid, malicious=True, jammer=True, transmit_power=power)
        
        status = analyse_and_save(ship, power, mid)

        if status == "Pass":
            best_dist = mid
            high = mid - 0.1  # Narrow the search to lower distances
        else:
            low = mid + 0.1  # Narrow the search to higher distances

    # After finding the boundary, save the result for the final best distance
    if best_dist is not None:
        for iter in range(ITERATIONS):
            ship = Ship(bays=BAYS, rows=ROWS, layers=LAYERS)
            ship.add_containers(":", ":", ":", container_type=CONTAINER_TYPE)
            ship.set_max_nodes(best_dist, malicious=True, jammer=True, transmit_power=power)
            
            analyse_and_save(ship, power, best_dist)
