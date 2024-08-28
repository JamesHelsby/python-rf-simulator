from ship import Ship
from ship_analyzer import plot_container_network
import json
import pandas as pd
import numpy as np
from tqdm import tqdm

BAYS = 10
ROWS = 10
LAYERS = 10
CONTAINER_TYPE = "standard"
ITERATIONS = 1

jammer_power_ranges = np.arange(0, 5.1, 0.1)
distance_ranges = np.arange(2, 5.1, 0.1)

for power in tqdm(jammer_power_ranges, desc=f"Jammer Power"):
    for dist in tqdm(distance_ranges, desc="Distance    "):
        for iter in range(ITERATIONS):
            ship = Ship(bays=BAYS, rows=ROWS, layers=LAYERS)
            ship.add_containers(":", ":", ":", container_type=CONTAINER_TYPE)
            ship.set_max_nodes(dist, malicious=True, jammer=True, transmit_power=power)
            
            ship.generate_container_graph()
            results = ship.analyse_graph()
                    
            results['power'] = power
            results['distance'] = results.pop('avg_min_distance_jammers', 'N/A')
            status = results.get('status', 'N/A')
        
            df = pd.DataFrame([results])
            df = df[['power', 'distance', 'status'] + [col for col in df.columns if col not in ['power', 'distance', 'status']]]
        
            csv_filename = f"{BAYS}x{ROWS}x{LAYERS}-{CONTAINER_TYPE}.csv"

            df.to_csv(csv_filename, mode='a', index=False, header=not pd.io.common.file_exists(csv_filename))