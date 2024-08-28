from abc import ABC, abstractmethod
from container import Container, Standard_Container, Small_Container
# import plotly.graph_objects as go
# import plotly.offline as pyo
import networkx as nx
import numpy as np
import random
from math import inf
from tqdm import tqdm
# from ship_visualizer import plot_ship_layout
# from ship_analyzer import analyse_graph, plot_container_network


TRANSMIT_POWER = 0
COMMUNICATION_THRESHOLD = -inf
JAMMER_POWER = 3


class Ship:
    TRANSMIT_POWER = 0
    COMMUNICATION_THRESHOLD = -inf

    class Cell:
        def __init__(self, x, y, z):
            self.length = 12
            self.width = 3
            self.height = 5
            self.x = x * self.length + self.length / 2
            self.y = y * self.width + self.width / 2
            self.z = z * self.height + self.height / 2
            self.container = None
            self.front_half = None
            self.back_half = None

        def add_small_container(self, container, position, verbose=False):
            if self.front_half and self.back_half:
                if verbose:
                    print("Cell is fully occupied.")
            elif position == "front" and not self.front_half:
                self.front_half = container
                container.x = self.x - self.length / 4
                container.y = self.y
                container.z = self.z
                if verbose:
                    print("Small container added to the front.")
            elif position == "back" and not self.back_half:
                self.back_half = container
                container.x = self.x + self.length / 4
                container.y = self.y
                container.z = self.z
                if verbose:
                    print("Small container added to the back.")
            else:
                if verbose:
                    print(f"Cell's {position} is already occupied.")

        def add_standard_container(self, container, verbose=False):
            if self.front_half or self.back_half:
                if verbose:
                    print("Cell cannot hold a standard container as it is partially occupied.")
            else:
                self.container = container
                container.x = self.x
                container.y = self.y
                container.z = self.z
                if verbose:
                    print("Standard container added.")

    def __init__(self, bays=1, rows=25, layers=25):
        self.bays = bays
        self.rows = rows
        self.layers = layers
        self.cells = [[[self.Cell(x, y, z) for z in range(self.layers)] for y in range(self.rows)] for x in range(self.bays)]
        
        self.G = None

        self.model = 'free-space'
        self.model_params = {
            'beta': 2,   # Path loss exponent (for log-normal)
            'sigma': 2,  # Shadowing variance (for log-normal) or Rayleigh/Ricean scale
            'v': 1,      # Ricean LOS component
            'frequency': 2.4e9  # Frequency in Hz for free-space model
        }

    def set_model(self, model, model_params=None):        
        self.model = model
        if model_params:
            self.model_params.update(model_params)
    
    def add_container(self, container, x, y, z, position="front"):
        cell = self.cells[x][y][z]
        if not cell.container:
            if isinstance(container, Small_Container):
                if position not in ["front", "back"]:
                    raise ValueError("Position must be 'front' or 'back' for small containers.")
                cell.add_small_container(container, position)
            elif isinstance(container, Standard_Container):
                cell.add_standard_container(container)
            else:
                raise ValueError("Unknown container type.")
        else:
            print(f"Cell ({x}, {y}, {z}) is already occupied.")

    def add_containers(self, x_slice, y_slice, z_slice, container_type):
        x_range = eval(f"range(self.bays)[{x_slice}]")
        y_range = eval(f"range(self.rows)[{y_slice}]")
        z_range = eval(f"range(self.layers)[{z_slice}]")

        for x in x_range:
            for y in y_range:
                for z in z_range:
                    if container_type == 'small':
                        self.add_container(Small_Container(), x, y, z, 'front')
                        self.add_container(Small_Container(), x, y, z, 'back')
                    elif container_type == 'standard':
                        self.add_container(Standard_Container(), x, y, z)
                    else:
                        raise ValueError("Unknown container type.")

    def set_behaviour(self, x_range, y_range, z_range, malicious=False, jammer=False, transmit_power=TRANSMIT_POWER):
        if jammer:
            malicious = True

        for x in x_range:
            for y in y_range:
                for z in z_range:
                    cell = self.cells[x][y][z]
                    if cell.container:
                        cell.container.malicious = malicious
                        cell.container.jammer = jammer
                        cell.container.transmit_power = transmit_power
                    if cell.front_half:
                        cell.front_half.malicious = malicious
                        cell.front_half.jammer = jammer
                        cell.front_half.transmit_power = transmit_power
#                    if cell.back_half:
#                        cell.back_half.malicious = malicious
#                        cell.back_half.jammer = jammer
#                        cell.back_half.transmit_power = transmit_power

    def set_max_nodes_in_plane(self, plane, index, min_distance, malicious=True, jammer=False, transmit_power=TRANSMIT_POWER):
        if plane not in ["bays", "rows", "layers"]:
            raise ValueError("Plane must be 'bays', 'rows', or 'layers'.")

        if plane == "bays":
            nodes_in_plane = [(index, y, z) for y in range(self.rows) for z in range(self.layers)]
        elif plane == "rows":
            nodes_in_plane = [(x, index, z) for x in range(self.bays) for z in range(self.layers)]
        elif plane == "layers":
            nodes_in_plane = [(x, y, index) for x in range(self.bays) for y in range(self.rows)]

        selected_nodes = []

        while nodes_in_plane:
            node = random.choice(nodes_in_plane)
            nodes_in_plane.remove(node)

            if all(self._distance(node, selected_node) >= min_distance for selected_node in selected_nodes):
                selected_nodes.append(node)
                x, y, z = node
                self.set_behaviour([x], [y], [z], malicious=malicious, jammer=jammer, transmit_power=transmit_power)        

    def set_max_nodes(self, min_distance, malicious=True, jammer=False, transmit_power=TRANSMIT_POWER):
            nodes = [(x, y, z) for x in range(self.bays) for y in range(self.rows) for z in range(self.layers)]
            selected_nodes = []

            while nodes:
                node = random.choice(nodes)
                nodes.remove(node)

                if all(self._distance(node, selected_node) >= min_distance for selected_node in selected_nodes):
                    selected_nodes.append(node)
                    x, y, z = node
                    self.set_behaviour([x], [y], [z], malicious=malicious, jammer=jammer, transmit_power=transmit_power)

    def set_n_nodes(self, n, malicious=True, jammer=False, transmit_power=TRANSMIT_POWER):
        all_nodes = [(x, y, z) for x in range(self.bays) for y in range(self.rows) for z in range(self.layers)]
        selected_nodes = random.sample(all_nodes, min(n, len(all_nodes)))
        for x, y, z in selected_nodes:
            self.set_behaviour([x], [y], [z], malicious=malicious, jammer=jammer, transmit_power=transmit_power)

    def set_n_nodes_in_plane(self, plane, index, n, malicious=True, jammer=False, transmit_power=TRANSMIT_POWER):
        if plane not in ["bays", "rows", "layers"]:
            raise ValueError("Plane must be 'bays', 'rows', or 'layers'.")

        if plane == "bays":
            nodes_in_plane = [(index, y, z) for y in range(self.rows) for z in range(self.layers)]
        elif plane == "rows":
            nodes_in_plane = [(x, index, z) for x in range(self.bays) for z in range(self.layers)]
        elif plane == "layers":
            nodes_in_plane = [(x, y, index) for x in range(self.bays) for y in range(self.rows)]

        selected_nodes = random.sample(nodes_in_plane, min(n, len(nodes_in_plane)))

        for x, y, z in selected_nodes:
            self.set_behaviour([x], [y], [z], malicious=malicious, jammer=jammer, transmit_power=transmit_power)

    def generate_container_graph(self):        
        G = nx.Graph()
        
        # Step 1: Build nodes
        for x in tqdm(range(self.bays), desc="Building nodes       ", leave=False):
            for y in range(self.rows):
                for z in range(self.layers):
                    cell = self.cells[x][y][z]
                    if cell.container:
                        node_id = f"C({x},{y},{z})"
                        G.add_node(node_id, pos=(cell.x, cell.y, cell.z), container='standard', transmit_power=cell.container.transmit_power, malicious=cell.container.malicious, jammer=cell.container.jammer)
                    if cell.front_half:
                        node_id = f"F({x},{y},{z})"
                        G.add_node(node_id, pos=(cell.front_half.x, cell.front_half.y, cell.front_half.z), container='small_front', transmit_power=cell.front_half.transmit_power, malicious=cell.front_half.malicious, jammer=cell.front_half.jammer)
                    if cell.back_half:
                        node_id = f"B({x},{y},{z})"
                        G.add_node(node_id, pos=(cell.back_half.x, cell.back_half.y, cell.back_half.z), container='small_back', transmit_power=cell.back_half.transmit_power, malicious=cell.back_half.malicious, jammer=cell.back_half.jammer)
        
        # Step 2: Build edges based on signal strength
        nodes = list(G.nodes(data=True))
        for i, (node1, data1) in tqdm(enumerate(nodes), total=len(nodes), desc="Building edges       ", leave=False):
            if data1['malicious']:
                continue
            for j, (node2, data2) in enumerate(nodes):
                if i < j and not data2['malicious']:
                    dist = self._distance(data1['pos'], data2['pos'])
                    signal_strength = self.calculate_signal_strength(dist, data1['transmit_power'], self.model, self.model_params)

                    if signal_strength > COMMUNICATION_THRESHOLD:
                        G.add_edge(node1, node2, signal_strength=signal_strength)

        # Step 3: Process jammers and remove weaker edges
        for jammer_node, jammer_data in tqdm(G.nodes(data=True), desc="Processing jammers   ", leave=False):
            if jammer_data['jammer']:
                for target_node, target_data in G.nodes(data=True):
                    if jammer_node != target_node:
                        dist = self._distance(jammer_data['pos'], target_data['pos'])
                        jamming_strength = self.calculate_signal_strength(dist, jammer_data['transmit_power'], self.model, self.model_params)

                        neighbors = list(G.neighbors(target_node))
                        for neighbor in neighbors:
                            edge_data = G.get_edge_data(target_node, neighbor)
                            if edge_data:
                                neighbor_signal_strength = edge_data['signal_strength']
                                if jamming_strength > neighbor_signal_strength:
                                    G.remove_edge(target_node, neighbor)

        self.G = G

    def analyse_graph(self, verbose=False):
        total_nodes = len(self.G.nodes())
        unconnected = [node for node in self.G.nodes() if len(list(self.G.neighbors(node))) == 0]
        num_unconnected = len(unconnected)
        num_connected = total_nodes - num_unconnected
        
        connected_subgraph = self.G.subgraph([n for n in self.G.nodes() if len(list(self.G.neighbors(n))) > 0])
        connected_components = list(nx.connected_components(connected_subgraph))
        num_connected_components = len(connected_components)

        honest_nodes = [node for node, data in self.G.nodes(data=True) if not data['malicious']]
        malicious_nodes = [node for node, data in self.G.nodes(data=True) if data['malicious']]
        jamming_nodes = [node for node in malicious_nodes if self.G.nodes[node]['jammer']]
        non_jamming_malicious_nodes = [node for node in malicious_nodes if not self.G.nodes[node]['jammer']]

        num_honest = len(honest_nodes)
        num_malicious = len(malicious_nodes)
        num_jamming = len(jamming_nodes)
        num_non_jammings = len(non_jamming_malicious_nodes)

        B = total_nodes - 1 - 3 * num_malicious
        trustset_configuration = B >= (num_unconnected - num_jamming)

        status = "Pass" if trustset_configuration and num_connected_components == 1 else "Fail"

        avg_min_distance = 'N/A'
        if num_jamming > 1:
            min_distances = []
            for i, jammer_node in enumerate(jamming_nodes):
                jammer_pos = self.G.nodes[jammer_node]['pos']
                min_distance = min(
                    self._distance(jammer_pos, self.G.nodes[other_jammer]['pos'])
                    for other_jammer in jamming_nodes if other_jammer != jammer_node
                )
                min_distances.append(min_distance)
            avg_min_distance = sum(min_distances) / len(min_distances)

        analysis_results = {
            'total_nodes': total_nodes,
            'num_honest': num_honest,
            'num_jamming': num_jamming,
            'num_unconnected': num_unconnected,
            'num_connected': num_connected,
            'buffer_margin': B,
            'trustset_configuration': trustset_configuration,
            'num_connected_components': num_connected_components,
            'connected_components': {f'Component_{i+1}': len(comp) for i, comp in enumerate(connected_components)},
            'avg_min_distance_jammers': avg_min_distance,
            'status': status
        }

        if verbose:
            print(f"\nTotal nodes             : {total_nodes}")
            print(f"  Honest Nodes          : {num_honest}")
            print(f"  Jamming Nodes         : {num_jamming}\n")
            print(f"Total disconnected      : {num_unconnected}")
            print(f"  Potential Honest      : {num_unconnected - num_jamming}")
            print(f"  Buffer Margin         : {B}\n")
            print(f"Trustset Configuration  : {trustset_configuration}\n")
            print(f"Components              : {num_connected_components}")
            if num_connected_components > 1:
                for i, component in enumerate(connected_components):
                    print(f"  Component {i + 1:<12}: {len(component)} nodes")
                print()
            else:
                print()

            if avg_min_distance != 'N/A':
                print(f"Average Distance        : {avg_min_distance:.2f}\n")
            else:
                print(f"Average Distance        : N/A\n")

            print(f"Status                  : {status}\n")

        return analysis_results

    def _distance(self, pos1, pos2):
        x1, y1, z1 = pos1
        x2, y2, z2 = pos2
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2) ** 0.5

    def calculate_signal_strength(self, distance, P_t, model, model_params):
        if model == 'log-normal':                     # Log-Normal Shadowing Model
            beta = model_params.get('beta', 2)        # Path loss exponent
            sigma = model_params.get('sigma', 2)      # Standard deviation of shadowing
            return P_t - 10 * beta * np.log10(distance) + np.random.normal(0, sigma)

        elif model == 'rayleigh':                     # Rayleigh Fading Model
            sigma = model_params.get('sigma', 1)      # Scale parameter for Rayleigh distribution
            return np.random.rayleigh(scale=sigma)

        elif model == 'ricean':                       # Ricean Fading Model
            v = model_params.get('v', 1)              # LOS component
            sigma = model_params.get('sigma', 1)      # Scattered component
            return np.random.rice(v, sigma)

        elif model == 'free-space':                   # Free Space Path Loss (FSPL) Model
            f = model_params.get('frequency', 2.4e9)  # Frequency in Hz (e.g., 2.4 GHz)
            c = 3e8                                   # Speed of light in m/s
            fspl = 20 * np.log10(distance) + 20 * np.log10(f) - 20 * np.log10(c / (4 * np.pi))
            return P_t - fspl

        else:
            raise ValueError(f"Unknown model type: {model}")


def combine_plots(fig1, fig2):
    fig = go.Figure(data=fig1.data + fig2.data)
    fig.update_layout(scene=fig1.layout.scene)
    pyo.plot(fig, filename='combined_plot.html', auto_open=True)


if __name__ == "__main__":
    ship = Ship(5, 5, 5)

    ship.add_containers(":", ":", ":", "standard")

    # ship.set_max_nodes_in_plane('bays', 5, 3.3, malicious=True, jammer=True, transmit_power=TRANSMIT_POWER)  # x1 Power
    # ship.set_max_nodes_in_plane('bays', 0, 4.5, malicious=True, jammer=True, transmit_power=JAMMER_POWER)  # x2 Power

    ship.set_max_nodes(3, malicious=True, jammer=True, transmit_power=0)  # x2 Power

    # ship.set_model('free-space')
    ship.generate_container_graph()
    results = ship.analyse_graph(verbose=True)

    # ship_plot = plot_ship_layout(ship, display=False)
    # network_plot = plot_container_network(ship, display=True)    
    # combine_plots(ship_plot, network_plot)
