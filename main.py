from abc import ABC, abstractmethod
import plotly.graph_objects as go
import plotly.offline as pyo
import networkx as nx
from tqdm import tqdm
from ship_visualizer import plot_ship_layout
from ship_analyzer import analyse_graph, plot_container_network


RF_RADIUS = 12
INTERFERENCE_RATIO = 1
JAMMER_RF_RADIUS_MULTIPLE = 1


class Ship:
    def __init__(self):
        self.bays = 3
        self.rows = 24
        self.layers = 25
        self.cells = [[[Cell(x, y, z) for z in range(self.layers)] for y in range(self.rows)] for x in range(self.bays)]
        
        self.G = None

        self.model = 'log-normal'
        self.model_params = {
            'P_t': 0,    # Transmit power in dBm
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

    def set_behaviour(self, x_slice, y_slice, z_slice, malicious=False, jammer=False):
        x_range = eval(f"range(self.bays)[{x_slice}]")
        y_range = eval(f"range(self.rows)[{y_slice}]")
        z_range = eval(f"range(self.layers)[{z_slice}]")

        for x in x_range:
            for y in y_range:
                for z in z_range:
                    cell = self.cells[x][y][z]
                    if cell.container:
                        cell.container.malicious = malicious
                        cell.container.jammer = jammer
                        cell.container.rf_radius = RF_RADIUS * INTERFERENCE_RATIO * JAMMER_RF_RADIUS_MULTIPLE if jammer else RF_RADIUS
                    if cell.front_half:
                        cell.front_half.malicious = malicious
                        cell.front_half.jammer = jammer
                        cell.front_half.rf_radius = RF_RADIUS * INTERFERENCE_RATIO * JAMMER_RF_RADIUS_MULTIPLE if jammer else RF_RADIUS
                    if cell.back_half:
                        cell.back_half.malicious = malicious
                        cell.back_half.jammer = jammer
                        cell.back_half.rf_radius = RF_RADIUS * INTERFERENCE_RATIO * JAMMER_RF_RADIUS_MULTIPLE if jammer else RF_RADIUS

        def generate_container_graph(self):
        G = nx.Graph()

        for x in tqdm(range(self.bays), desc="Building nodes       "):
            for y in range(self.rows):
                for z in range(self.layers):
                    cell = self.cells[x][y][z]
                    if cell.container:
                        node_id = f"C({x},{y},{z})"
                        G.add_node(node_id, pos=(cell.x, cell.y, cell.z), container='standard', rf_radius=cell.container.rf_radius, malicious=cell.container.malicious, jammer=cell.container.jammer)
                    if cell.front_half:
                        node_id = f"F({x},{y},{z})"
                        G.add_node(node_id, pos=(cell.front_half.x, cell.front_half.y, cell.front_half.z), container='small_front', rf_radius=cell.front_half.rf_radius, malicious=cell.front_half.malicious, jammer=cell.front_half.jammer)
                    if cell.back_half:
                        node_id = f"B({x},{y},{z})"
                        G.add_node(node_id, pos=(cell.back_half.x, cell.back_half.y, cell.back_half.z), container='small_back', rf_radius=cell.back_half.rf_radius, malicious=cell.back_half.malicious, jammer=cell.back_half.jammer)
        
        nodes = list(G.nodes(data=True))
        for i, (node1, data1) in tqdm(enumerate(nodes), total=len(nodes), desc="Building edges       "):
            if data1['malicious']:
                continue
            for j, (node2, data2) in enumerate(nodes):
                if i < j and not data2['malicious']:
                    dist = ((data1['pos'][0] - data2['pos'][0]) ** 2 + 
                            ((data1['pos'][1] - data2['pos'][1]) ** 2) +
                            ((data1['pos'][2] - data2['pos'][2]) ** 2)) ** 0.5
                    
                    signal_strength = calculate_signal_strength(dist, self.model, self.model_params)
                    
                    threshold = -80
                    if signal_strength > threshold:
                        G.add_edge(node1, node2)
        
        for node, data in tqdm(G.nodes(data=True), desc="Removing jammed edges"):
            if data['jammer']:
                nodes_to_disconnect = []
                for other_node, other_data in G.nodes(data=True):
                    if other_node != node:
                        dist = ((data['pos'][0] - other_data['pos'][0]) ** 2 + 
                                ((data['pos'][1] - other_data['pos'][1]) ** 2) +
                                ((data['pos'][2] - other_data['pos'][2]) ** 2)) ** 0.5
                        if dist <= data['rf_radius']:
                            nodes_to_disconnect.append(other_node)

                for target_node in nodes_to_disconnect:
                    if G.has_node(target_node):
                        neighbors = list(G.neighbors(target_node))
                        for neighbor in neighbors:
                            G.remove_edge(target_node, neighbor)

        self.G = G


def calculate_signal_strength(distance, model, model_params):
    if model == 'log-normal':
        # Log-Normal Shadowing Model
        P_t = model_params.get('P_t', 0)      # Transmit power in dBm
        beta = model_params.get('beta', 2)    # Path loss exponent
        sigma = model_params.get('sigma', 2)  # Standard deviation of shadowing
        return P_t - 10 * beta * np.log10(distance) + np.random.normal(0, sigma)

    elif model == 'rayleigh':
        # Rayleigh Fading Model
        sigma = model_params.get('sigma', 1)  # Scale parameter for Rayleigh distribution
        return np.random.rayleigh(scale=sigma)

    elif model == 'ricean':
        # Ricean Fading Model
        v = model_params.get('v', 1)          # LOS component
        sigma = model_params.get('sigma', 1)  # Scattered component
        return np.random.rice(v, sigma)

    elif model == 'free-space':
        # Free Space Path Loss (FSPL) Model
        f = model_params.get('frequency', 2.4e9)  # Frequency in Hz (e.g., 2.4 GHz)
        c = 3e8                                   # Speed of light in m/s
        return 20 * np.log10(distance) + 20 * np.log10(f) - 20 * np.log10(c / (4 * np.pi))

    else:
        raise ValueError(f"Unknown model type: {model}")


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


class Container(ABC):
    @abstractmethod
    def __init__(self, length, width, height):
        self.length = length
        self.width = width
        self.height = height
        self.rf_radius = 14
        self.malicious = False
        self.jammer = False
        self.x = None
        self.y = None
        self.z = None


class Standard_Container(Container):
    def __init__(self):
        super().__init__(length=12, width=3, height=5)


class Small_Container(Container):
    def __init__(self):
        super().__init__(length=6, width=3, height=5)


def combine_plots(fig1, fig2):
    fig = go.Figure(data=fig1.data + fig2.data)
    fig.update_layout(scene=fig1.layout.scene)
    pyo.plot(fig, filename='combined_plot.html', auto_open=True)


if __name__ == "__main__":
    ship = Ship()

    ship.add_containers(":", ":", ":", "standard")
    # ship.add_containers(":", ":-1", ":-2", "standard")

    # ship.set_behaviour(":", ":", ":", malicious=True, jammer=False)

    ship.set_behaviour("1:2", "0:1", "0:1", malicious=False, jammer=True)
    ship.set_behaviour("1:2", "0:1", "-1:", malicious=False, jammer=True)
    ship.set_behaviour("1:2", "-1:", "0:1", malicious=False, jammer=True)
    ship.set_behaviour("1:2", "-1:", "-1:", malicious=False, jammer=True)

    # ship.set_behaviour("1:2", "6:7", "-3:-2", malicious=False, jammer=True)
    # ship.set_behaviour(":1", "5:6", "2:3", malicious=False, jammer=True)

    ship.generate_container_graph()
    analyse_graph(ship.G)

    # ship_plot = plot_ship_layout(ship, display=False)
    network_plot = plot_container_network(ship, display=True)    
    # combine_plots(ship_plot, network_plot)
    