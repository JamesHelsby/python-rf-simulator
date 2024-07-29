import os
import re
import sys
from tqdm import tqdm

def parse_log_entry(entry):
    log_pattern = re.compile(r"(?P<message_num>\d+)\|(?P<origin_node>\d+)\|(?P<attesting_node>\d+)")
    match = log_pattern.search(entry)
    if match:
        return match.groupdict()
    return None

def update_progress_bars(progress_bars, entry, total_motes):
    key = f"{entry['message_num']}|{entry['origin_node']}"
    if key not in progress_bars:
        progress_bars[key] = {'progress': 0, 'total': -(-total_motes // 3), 'completed': False}
    if not progress_bars[key]['completed']:
        if int(entry['attesting_node']) != 0:
            progress_bars[key]['progress'] += 1
        if progress_bars[key]['progress'] >= progress_bars[key]['total']:
            progress_bars[key]['progress'] = progress_bars[key]['total']
            progress_bars[key]['completed'] = True

def display_progress_bars(progress_bars):
    os.system('clear')
    for key, pb in progress_bars.items():
        pbar = tqdm(total=pb['total'], position=0, desc=key, leave=True)
        pbar.update(pb['progress'])
        pbar.set_postfix_str(f"{pb['progress']}/{pb['total']}")
        pbar.refresh()

def main():
    if len(sys.argv) != 3:
        print("Usage: python fifo_display_script.py <total_motes> <fifo_path>")
        sys.exit(1)

    total_motes = int(sys.argv[1])
    fifo_path = sys.argv[2]

    if not os.path.exists(fifo_path):
        print(f"FIFO {fifo_path} does not exist.")
        input("Here")
        return

    progress_bars = {}

    with open(fifo_path, 'r') as fifo:
        while True:
            line = fifo.readline()
            if line:
                entry = parse_log_entry(line.strip())
                if entry:
                    update_progress_bars(progress_bars, entry, total_motes)
                    display_progress_bars(progress_bars)
            else:
                break

if __name__ == "__main__":
    main()
