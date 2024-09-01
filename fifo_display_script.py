import os
import re
import sys

def parse_log_entry(entry):
    log_pattern = re.compile(
        r"(?P<timestamp>\d+:\d{2}\.\d{3},\d{3})\s+"  # Timestamp
        r"ID:\s*(?P<id>\d+)\s+"                      # ID
        r"(?P<direction>Tx|Rx):\s*"                  # Direction
        r"'(?P<message_num>\d+)\|(?P<origin_node>\d+)\|(?P<attesting_node>\d+)'(?:\sfrom node:\s'(?P<from_node>\d+)')?\s*->\s*"  # Message details
        r"(?P<action>REQUEST|ATTESTATION RECEIVED)"  # Action
    )
    match = log_pattern.search(entry)
    if match:
        return match.groupdict()
    return None

def update_progress_bars(progress_bars, entry, total_motes):
    key = f"{entry['message_num']}|{entry['origin_node']}"
    if entry['action'] == "REQUEST":
        progress_bars[key] = {'progress': 0, 'total': total_motes}
    if entry['action'] == "ATTESTATION RECEIVED":
        progress_bars[key]['progress'] += 1

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

def main():
    if len(sys.argv) != 3:
        print("Usage: python fifo_display_script.py <total_motes> <fifo_path>")
        sys.exit(1)

    total_motes = int(sys.argv[1])
    fifo_path = sys.argv[2]

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

if __name__ == "__main__":
    main()
