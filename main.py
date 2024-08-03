from abc import ABC, abstractmethod
import plotly.graph_objects as go
import plotly.offline as pyo
from ship_visualizer import plot_ship_layout
from ship_analyzer import plot_container_network


class Ship:
    def __init__(self):
        self.bays = 5
        self.rows = 5
        self.layers = 5
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

    def add_small_container(self, container, position):
        if self.front_half and self.back_half:
            print("Cell is fully occupied.")
        elif position == "front" and not self.front_half:
            self.front_half = container
            container.x = self.x - self.length / 4
            container.y = self.y
            container.z = self.z
            print("Small container added to the front.")
        elif position == "back" and not self.back_half:
            self.back_half = container
            container.x = self.x + self.length / 4
            container.y = self.y
            container.z = self.z
            print("Small container added to the back.")
        else:
            print(f"Cell's {position} is already occupied.")

    def add_standard_container(self, container):
        if self.front_half or self.back_half:
            print("Cell cannot hold a standard container as it is partially occupied.")
        else:
            self.container = container
            container.x = self.x
            container.y = self.y
            container.z = self.z
            print("Standard container added.")


class Container(ABC):
    @abstractmethod
    def __init__(self, length, width, height):
        self.length = length
        self.width = width
        self.height = height
        self.rf_radius = 14
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

    ship.add_container(Standard_Container(), 0, 0, 0)
    ship.add_container(Small_Container(), 1, 0, 0, "front")
    ship.add_container(Small_Container(), 1, 0, 0, "back")
    ship.add_container(Standard_Container(), 1, 0, 1)

    ship_plot = plot_ship_layout(ship, display=True)
    network_plot = plot_container_network(ship, display=True)
    combine_plots(ship_plot, network_plot)
    