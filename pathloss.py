import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

class SignalStrengthModel:
    def __init__(self, left, right, resolution):
        self.frequency = 2.4e9
        self.speed_of_light = 3e8
        self.distances = np.linspace(left, right, resolution)
        self.noise_radios = []
        self.network_radios = []

    def free_space_path_loss(self, distance):
        return 20 * np.log10(distance) + 20 * np.log10(self.frequency) - 20 * np.log10(self.speed_of_light)

    def calculate_path_loss(self, radio_position, power_dBm):
        relative_distances = np.abs(self.distances - radio_position)
        relative_distances = np.clip(relative_distances, 0.1, None)
        path_loss = power_dBm - self.free_space_path_loss(relative_distances)
        return path_loss

    def add_noise_radio(self, position, power_dBm):
        self.noise_radios.append({"position": position, "power": power_dBm})

    def add_network_radio(self, position, power_dBm):
        self.network_radios.append({"position": position, "power": power_dBm})

    def sort_radios_by_position(self):
        self.network_radios.sort(key=lambda x: x["position"])

    def plot(self, truncate=False, fill=False, show_noise_radios=False):
        self.sort_radios_by_position()
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.margins(x=0)

        # Calculate noise floor across the entire distance array
        noise_power_linear = np.zeros_like(self.distances)
        for radio in self.noise_radios:
            individual_noise_power_dBm = self.calculate_path_loss(radio["position"], radio["power"])
            noise_power_linear += 10 ** (individual_noise_power_dBm / 10)

            # Show individual noise radio contributions if show_noise_radios is True
            if show_noise_radios:
                ax.plot(self.distances, individual_noise_power_dBm, color='gray', linestyle='--', alpha=0.5)

        # Avoid log10 of zero
        noise_power_linear = np.clip(noise_power_linear, 1e-10, None)
        total_noise_power_dBm = 10 * np.log10(noise_power_linear)

        for radio in self.noise_radios:
            ax.plot([radio["position"], radio["position"]], [-80, radio["power"]], color='gray', linestyle='--')

        for radio in self.network_radios:
            ax.plot([radio["position"], radio["position"]], [-80, radio["power"]], color='gray', linestyle=':')

        ax.plot(self.distances, total_noise_power_dBm, color='black', linewidth=2)

        # Fill under the noise floor if fill is True
        if fill:
            ax.fill_between(self.distances, -80, total_noise_power_dBm, color='red', alpha=0.3)

        for i, radio in enumerate(self.network_radios):
            path_loss_network_radio = self.calculate_path_loss(radio["position"], radio["power"])

            if truncate:
                left_boundary = 0 if i == 0 else self.network_radios[i - 1]["position"]
                right_boundary = np.inf if i == len(self.network_radios) - 1 else self.network_radios[i + 1]["position"]
            else:
                left_boundary, right_boundary = 0, np.inf

            valid_indices = (self.distances >= left_boundary) & (self.distances <= right_boundary)

            for j in range(len(self.distances[valid_indices]) - 1):
                if path_loss_network_radio[valid_indices][j] > total_noise_power_dBm[valid_indices][j]:
                    ax.plot(self.distances[valid_indices][j:j+2], path_loss_network_radio[valid_indices][j:j+2], color='green')
                else:
                    ax.plot(self.distances[valid_indices][j:j+2], path_loss_network_radio[valid_indices][j:j+2], color='red')

            # Fill under the network radio signals if fill is True
            if fill:
                ax.fill_between(self.distances[valid_indices], total_noise_power_dBm[valid_indices], 
                                path_loss_network_radio[valid_indices], where=(path_loss_network_radio[valid_indices] > total_noise_power_dBm[valid_indices]),
                                color='green', alpha=0.3)

        ax.set_ylim(-80, 15)
        ax.set_xlabel('Distance (meters)')
        ax.set_ylabel('Power (dBm)')
        ax.set_title('Signal Strength vs. Noise Floor')
        plt.show()

    def update_plot(self, val):
        for i, radio in enumerate(self.noise_radios):
            radio["position"] = self.noise_radio_sliders[i].val

        for i, radio in enumerate(self.network_radios):
            radio["position"] = self.network_radio_sliders[i].val

        self.ax.clear()
        self.plot_in_ax(truncate=self.truncate, fill=self.fill, show_noise_radios=self.show_noise_radios)

    def plot_in_ax(self, truncate=False, fill=False, show_noise_radios=False):
        self.sort_radios_by_position()
        self.ax.margins(x=0)

        # Calculate noise floor across the entire distance array
        noise_power_linear = np.zeros_like(self.distances)
        for radio in self.noise_radios:
            individual_noise_power_dBm = self.calculate_path_loss(radio["position"], radio["power"])
            noise_power_linear += 10 ** (individual_noise_power_dBm / 10)

            # Show individual noise radio contributions if show_noise_radios is True
            if show_noise_radios:
                self.ax.plot(self.distances, individual_noise_power_dBm, color='gray', linestyle='--', alpha=0.5)

        # Avoid log10 of zero
        noise_power_linear = np.clip(noise_power_linear, 1e-10, None)
        total_noise_power_dBm = 10 * np.log10(noise_power_linear)

        for radio in self.noise_radios:
            self.ax.plot([radio["position"], radio["position"]], [-80, radio["power"]], color='gray', linestyle='--')

        for radio in self.network_radios:
            self.ax.plot([radio["position"], radio["position"]], [-80, radio["power"]], color='gray', linestyle=':')

        self.ax.plot(self.distances, total_noise_power_dBm, color='black', linewidth=2)

        # Fill under the noise floor if fill is True
        if fill:
            self.ax.fill_between(self.distances, -80, total_noise_power_dBm, color='red', alpha=0.3)

        for i, radio in enumerate(self.network_radios):
            path_loss_network_radio = self.calculate_path_loss(radio["position"], radio["power"])

            if truncate:
                left_boundary = 0 if i == 0 else self.network_radios[i - 1]["position"]
                right_boundary = np.inf if i == len(self.network_radios) - 1 else self.network_radios[i + 1]["position"]
            else:
                left_boundary, right_boundary = 0, np.inf

            valid_indices = (self.distances >= left_boundary) & (self.distances <= right_boundary)

            for j in range(len(self.distances[valid_indices]) - 1):
                if path_loss_network_radio[valid_indices][j] > total_noise_power_dBm[valid_indices][j]:
                    self.ax.plot(self.distances[valid_indices][j:j+2], path_loss_network_radio[valid_indices][j:j+2], color='green')
                else:
                    self.ax.plot(self.distances[valid_indices][j:j+2], path_loss_network_radio[valid_indices][j:j+2], color='red')

            # Fill under the network radio signals if fill is True
            if fill:
                self.ax.fill_between(self.distances[valid_indices], total_noise_power_dBm[valid_indices], 
                                     path_loss_network_radio[valid_indices], where=(path_loss_network_radio[valid_indices] > total_noise_power_dBm[valid_indices]),
                                     color='green', alpha=0.3)

        self.ax.set_ylim(-80, 15)
        self.ax.set_xlabel('Distance (meters)')
        self.ax.set_ylabel('Power (dBm)')
        self.ax.set_title('Signal Strength vs. Noise Floor')

    def plot_interactive(self, truncate=False, fill=False, show_noise_radios=False):
        self.truncate = truncate
        self.fill = fill
        self.show_noise_radios = show_noise_radios
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        plt.subplots_adjust(left=0.1, bottom=0.35)

        self.noise_radio_sliders = [
            Slider(plt.axes([0.1, 0.25 - 0.05 * i, 0.8, 0.03]), f'Noise Radio {i+1}', 0, 100, valinit=radio["position"])
            for i, radio in enumerate(self.noise_radios)
        ]

        self.network_radio_sliders = [
            Slider(plt.axes([0.1, 0.1 - 0.05 * i, 0.8, 0.03]), f'Network Radio {i+1}', 0, 100, valinit=radio["position"])
            for i, radio in enumerate(self.network_radios)
        ]

        for slider in self.noise_radio_sliders + self.network_radio_sliders:
            slider.on_changed(self.update_plot)

        self.plot_in_ax(truncate=self.truncate, fill=self.fill)
        plt.show()

# Example usage
model = SignalStrengthModel(0, 3*15, 1000)

noise_power = 0
network_power = 0

noise_positions = {3*5, 3*13}

# model.add_network_radio(6, network_power)
# model.add_noise_radio(15, noise_power + 6)
# model.add_noise_radio(24, noise_power - 6)

model.add_network_radio(0, network_power)
for dist in range(3, 3*15, 3):
    if dist in noise_positions:
        model.add_noise_radio(dist, noise_power)
        continue
    model.add_network_radio(dist, network_power)
model.add_network_radio(3*15, network_power)
    
model.plot(truncate=False, fill=True, show_noise_radios=True)
# model.plot_interactive(truncate=True)  # Plot interactively with truncation
