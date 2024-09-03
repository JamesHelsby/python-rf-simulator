import os
import random
import subprocess
import re
import xml.etree.ElementTree as ET
import csv
import fcntl
from gen_sim import create_simulation_xml

CSV_FILE_PATH = "cooja_results.csv"

def parse_simulation_file(file_path):
    tree = ET.parse(os.path.expanduser(f"~/bitbucket/Attack-the-BLOCC/simulations/java_{file_path}_sim.csc"))
    root = tree.getroot()
    mote_count = 0
    for node_type in root.findall(".//motetype"):
        mote_count += len(node_type.findall(".//mote"))
    return mote_count

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

def save_results_to_csv(total_motes, progress_bars, mote_type):    
    if progress_bars:
        num_attestations = sum(pb['progress'] for pb in progress_bars.values())
        last_attestation_time = max(
            (pb['last_attestation_time'] for pb in progress_bars.values() if pb['last_attestation_time']),
            default="No Attestations"
        )
    else:
        num_attestations = 0
        last_attestation_time = "No Attestations"

    file_exists = os.path.isfile(CSV_FILE_PATH)

    with open(CSV_FILE_PATH, 'a', newline='') as csvfile:
        # Acquire an exclusive lock
        fcntl.flock(csvfile, fcntl.LOCK_EX)
        try:
            writer = csv.writer(csvfile)
            if not file_exists:
                writer.writerow(['Total Motes', 'Number of Attestations', 'Last Attestation Time', 'Mote Type'])
            writer.writerow([total_motes, num_attestations, last_attestation_time, mote_type])
        finally:
            # Always release the lock
            fcntl.flock(csvfile, fcntl.LOCK_UN)

def run_cooja_simulation(config):
    rows = config['rows']
    cols = config['cols']
    layers = config['layers']
    spacing_x = config['spacing_x']
    spacing_y = config['spacing_y']
    spacing_z = config['spacing_z']
    tx_range = config['tx_range']
    interference_range = config['interference_range']
    success_ratio = config['success_ratio']
    mote_type = config['mote_type']
    disturber = config['disturber']
    
    create_simulation_xml(
        rows=rows,
        cols=cols,
        layers=layers,
        spacing_x=spacing_x,
        spacing_y=spacing_y,
        spacing_z=spacing_z,
        tx_range=tx_range,
        interference_range=interference_range,
        success_ratio=success_ratio,
        language="java",
        mote_type=mote_type
    )

    simulation = f"{rows}x{cols}x{layers}_{success_ratio}_{mote_type}{'_disturber' if disturber else ''}"
    total_motes = parse_simulation_file(simulation)
    command = ['./gradlew_parallel', 'run', f"--args='--no-gui ../../simulations/java_{simulation}_sim.csc'"]
    working_directory = os.path.expanduser(f"~/bitbucket/Attack-the-BLOCC/tools/cooja")

    process = subprocess.Popen(
        f"{' '.join(command)} 2>&1 | tee /dev/tty",
        cwd=working_directory,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        text=True
    )

    return process, total_motes

def run_simulation_and_save(config):
    process, total_motes = run_cooja_simulation(config)
    progress_bars = {}

    try:
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                entry = parse_log_entry(output.strip())
                if entry:
                    update_progress_bars(progress_bars, entry, total_motes)

        if process.returncode != 0:
            print(f"Simulation failed with return code {process.returncode}")

    except BrokenPipeError:
        print("Broken pipe error: The reader process has closed the FIFO.")

    save_results_to_csv(total_motes, progress_bars, config['mote_type'])
    print("Results saved to CSV.")

def clean_up_temp_files():
    subprocess.run("rm -rf /tmp/gradle-project*", shell=True)
    subprocess.run("rm -rf /tmp/gradle-user*", shell=True)
    print("Temporary files cleaned up.")

def main():    
    iterations = 1

    spacing_x = 3
    spacing_y = 12
    spacing_z = 5
    tx_range = 14
    interference_range = 20
    success_ratio = 1
    disturber = False

    range_min = 1
    range_max = 20

    mote_types = ["cache", "bls"]

    row_col_layer_options = [
        (rows, cols, layers)
        for rows in range(range_min, range_max + 1)
        for cols in range(range_min, range_max + 1)
        for layers in range(range_min, range_max + 1)
    ]

    for iteration in range(iterations):
        random.shuffle(row_col_layer_options)

        for rows, cols, layers in row_col_layer_options:
            for mote_type in mote_types:
                config = {
                    "rows": rows,
                    "cols": cols,
                    "layers": layers,
                    "spacing_x": spacing_x,
                    "spacing_y": spacing_y,
                    "spacing_z": spacing_z,
                    "tx_range": tx_range,
                    "interference_range": interference_range,
                    "success_ratio": success_ratio,
                    "mote_type": mote_type,
                    "disturber": disturber
                }

                print("=" * 80)
                print(f"Running simulation with config: {config}")
                clean_up_temp_files()
                run_simulation_and_save(config)
                clean_up_temp_files()

if __name__ == "__main__":
    main()
