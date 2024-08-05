from abc import ABC, abstractmethod
import plotly.graph_objects as go
import plotly.offline as pyo
from ship_visualizer import plot_ship_layout
from ship_analyzer import generate_container_network, analyse_graph, plot_container_network


RF_RADIUS = 12
INTERFERENCE_RATIO = 1
JAMMER_RF_RADIUS_MULTIPLE = 1


class Ship:
    def __init__(self):
        self.bays = 10
        self.rows = 10
        self.layers = 6
        self.cells = [[[Cell(x, y, z) for z in range(self.layers)] for y in range(self.rows)] for x in range(self.bays)]
    
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

    ship.add_containers(":-2", ":", ":", "standard")
    # ship.add_containers(":", ":-1", ":-2", "standard")

    # ship.set_behaviour("3:4", "4:5", "2:3", malicious=False, jammer=True)
    ship.set_behaviour("0:5", ":", ":", malicious=True)
    ship.set_behaviour("5:6", ":", ":2", malicious=True)
    ship.set_behaviour("5:6", ":1", "1:2", malicious=False)

    G = generate_container_network(ship)
    analyse_graph(G)

    # ship_plot = plot_ship_layout(ship, display=False)
    network_plot = plot_container_network(ship, G, display=True)    
    # combine_plots(ship_plot, network_plot)
    