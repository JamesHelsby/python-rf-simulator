import os
import re
import sys
import csv

CSV_FILE_PATH = "cooja_results.csv"

def parse_log_entry(entry):
    log_pattern = re.compile(
        r"(?P<timestamp>\d+:\d{2}\.\d{3},\d{3})\s+"
        r"ID:\s*(?P<id>\d+)\s+"
        r"(?P<direction>Tx|Rx):\s*"
        r"'(?P<message_num>\d+)\|(?P<origin_node>\d+)\|(?P<attesting_node>\d+)'(?:\sfrom node:\s'(?P<from_node>\d+)')?\s*->\s*"
        r"(?P<action>REQUEST|ATTESTATION RECEIVED)"
    )
    match = log_pattern.search(entry)
    if match:
        return match.groupdict()
    return None

def update_progress_bars(progress_bars, entry, total_motes):
    key = f"{entry['message_num']}|{entry['origin_node']}"
    if entry['action'] == "REQUEST":
        progress_bars[key] = {'progress': 0, 'total': total_motes, 'last_attestation_time': None}
    if entry['action'] == "ATTESTATION RECEIVED":
        progress_bars[key]['progress'] += 1
        progress_bars[key]['last_attestation_time'] = entry['timestamp']

def display_progress_bars(progress_bars, total_motes):
    bar_length = 50
    notch = -(-total_motes // 3) * 2
    for key, pb in progress_bars.items():
        progress = pb['progress']
        total = pb['total']
        filled_length = min(int(bar_length * progress // total), bar_length)
        notch_position = min(int(bar_length * notch // total), bar_length - 1)

        bar = ['-'] * bar_length
        for i in range(filled_length):
            if i < notch_position:
                bar[i] = '█'
            else:
                bar[i] = '█' if progress >= notch else '-'

        bar[notch_position] = '|'

        bar_str = ''.join(bar)
        if progress >= notch:
            bar_str = f'\033[92m{bar_str}\033[0m'

        print(f'\033[K{key}: |{bar_str}| {progress}/{total}', end='\r\n')

def save_results_to_csv(total_motes, progress_bars, mote_type):
    num_attestations = sum(pb['progress'] for pb in progress_bars.values())
    last_attestation_time = max(pb['last_attestation_time'] for pb in progress_bars.values() if pb['last_attestation_time'])

    file_exists = os.path.isfile(CSV_FILE_PATH)

    with open(CSV_FILE_PATH, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['Total Motes', 'Number of Attestations', 'Last Attestation Time', 'Mote Type'])
        writer.writerow([total_motes, num_attestations, last_attestation_time, mote_type])

def main():
    if len(sys.argv) != 4:
        print("Usage: python fifo_display_script.py <total_motes> <fifo_path> <mote_type>")
        sys.exit(1)

    total_motes = int(sys.argv[1])
    fifo_path = sys.argv[2]
    mote_type = sys.argv[3]

    if not os.path.exists(fifo_path):
        print(f"FIFO {fifo_path} does not exist.")
        return

    progress_bars = {}

    with open(fifo_path, 'r') as fifo:
        while True:
            line = fifo.readline()
            if line:
                entry = parse_log_entry(line.strip())
                if entry:
                    try:
                        update_progress_bars(progress_bars, entry, total_motes)
                        print('\033[H', end='')
                        display_progress_bars(progress_bars, total_motes)
                    except Exception as e:
                        print(e)
                elif "TERMINATE" in line:
                    save_results_to_csv(total_motes, progress_bars, mote_type)
                    print("Simulation ended")
                    # input("Press any key to close...")
            else:
                if os.path.getsize(fifo_path) == 0:
                    continue

if __name__ == "__main__":
    main()
