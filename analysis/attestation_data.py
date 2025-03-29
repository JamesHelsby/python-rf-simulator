import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from cooja_clean import clean_data

CSV_FILE_PATH = "cooja_results.csv"

def load_data(csv_file_path):
    try:
        data = pd.read_csv(csv_file_path)
        return data
    except FileNotFoundError:
        print(f"File not found: {csv_file_path}")
        return None

def convert_time_to_seconds(time_str):
    if time_str == "No Attestations":
        return None
    
    time_str = time_str.replace(',', '.')
    try:
        minutes, rest = time_str.split(':')
        seconds, millis, micros = rest.split('.')
        total_seconds = int(minutes) * 60 + int(seconds) + int(millis) * 0.001 + int(micros) * 0.000001
        return total_seconds
    except ValueError:
        print(f"Error converting time: {time_str}")
        return None

def update_plot(frame, fig, ax1, ax2):
    clean_data()
    data = load_data(CSV_FILE_PATH)
    if data is not None:
        ax1.clear()
        ax2.clear()

        data['Last Attestation Time (seconds)'] = data['Last Attestation Time'].apply(convert_time_to_seconds)
        data = data.dropna(subset=['Last Attestation Time (seconds)'])
        data['Proportion of Attestations'] = data['Number of Attestations'] / data['Total Motes']

        grouped_data = data.groupby('Mote Type')

        for mote_type, group in grouped_data:
            if mote_type == 'cache':
                label = 'Cache'
            elif mote_type == 'ttl':
                label = 'TTL'
            elif mote_type == 'bls':
                label = 'Batch'
            else:
                label = mote_type

            ax1.scatter(group['Total Motes'], group['Proportion of Attestations'], label=label, s=5)
            ax2.scatter(group['Total Motes'], group['Last Attestation Time (seconds)'], label=label, s=5)

        ax1.set_xlabel('Total Parties')
        ax1.set_ylabel('Proportion of Attestations')
        ax1.set_title('Attestations as a Proportion of Total Parties vs. Total Parties')
        ax1.grid(True)
        ax1.legend(title='Mote Type')
        ax1.axhline(y=0.5, color='red', linestyle='--', linewidth=1)

        ax2.set_xlabel('Total Parties')
        ax2.set_ylabel('Attestation Collection Time (seconds)')
        ax2.set_title('Attestation Collection Time vs. Total Parties')
        ax2.grid(True)
        ax2.legend(title='Mote Type')

        fig.canvas.draw()

def main():
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    plt.subplots_adjust(hspace=0.4)
    ani = FuncAnimation(fig, update_plot, fargs=(fig, ax1, ax2), interval=10000)
    plt.show()

if __name__ == "__main__":
    main()
